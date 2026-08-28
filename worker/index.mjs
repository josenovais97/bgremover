/**
 * /api/stats/ — the usage counter, rebuilt for Cloudflare.
 *
 * This endpoint was a Django view backed by Upstash Redis. Neither survived the
 * move off Vercel: the site is prerendered to static files and served by a
 * Worker with no script at all, so there was nothing left to run the view and
 * nothing left to hold the numbers. The twenty `window.__clearbgReport?.(…)`
 * call sites in static/js were still there, silently no-oping.
 *
 * The shape of the JSON is unchanged, so a bookmark on /api/stats/ reads the
 * same as it did before:
 *
 *   GET  /api/stats/              → {"enabled": true, "count": N, "week": M}
 *   GET  /api/stats/?breakdown=1  → {"enabled": true, "breakdown": {"processed:home": N, …}}
 *   POST /api/stats/  {"n": 1, "tool": "home", "event": "processed"}
 *                                 → the same counts, after incrementing
 *
 * What changed underneath:
 *
 * * The store is a single SQLite-backed Durable Object instead of Upstash. It
 *   needs no provisioning (`wrangler deploy` creates it), no secrets, and no
 *   third-party account, and it is on the Workers Free plan. Because one
 *   instance serialises every write, `count` is exact rather than best-effort.
 * * `enabled` is now always true — it existed to say "no store is configured,
 *   so the badge must not invent a number", and there is no unconfigured state
 *   left. It is kept so existing callers do not have to change.
 * * Weekly buckets are no longer expired after 45 days. Redis charged rent for
 *   them; 52 rows a year in SQLite does not, and keeping them means the history
 *   is there if it is ever worth showing.
 * * The rate limiter counts in the Durable Object's memory rather than in the
 *   store. It is a speed bump on a vanity counter, and the old one spent a
 *   round trip and a write on every single POST to enforce it.
 * * The client IP comes from CF-Connecting-IP, which Cloudflare sets and a
 *   client cannot forge, rather than from the first hop of X-Forwarded-For,
 *   which it can.
 */
import { DurableObject } from 'cloudflare:workers';

import {
  POST_LIMIT, POST_WINDOW_MS,
  breakdownNames, clampCount, eventKey, weekKey,
} from './lib.mjs';

/** The one instance that holds every counter. */
const SINGLETON = 'global';

/**
 * The counter store: one row per key in a SQLite-backed Durable Object.
 *
 * Keys are `total`, `w:<ISO week>` and `evt:<event>:<tool>` — see lib.js, which
 * builds all three from whitelists.
 */
export class Stats extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    // Synchronous, and cheap when the table already exists, so there is no need
    // to gate it behind blockConcurrencyWhile.
    ctx.storage.sql.exec(
      'CREATE TABLE IF NOT EXISTS counters (key TEXT PRIMARY KEY, n INTEGER NOT NULL)',
    );
    // Rate-limit state, deliberately in memory: it is worth nothing once it is
    // a minute old, and persisting it would put a write on the hot path of the
    // one endpoint that gets hammered.
    this.recent = new Map();
  }

  /** All-time and current-week totals. */
  read() {
    return { count: this.#get('total'), week: this.#get(weekKey()) };
  }

  /** Every per-tool/per-event counter, zero-filled so the shape is stable. */
  breakdown() {
    const stored = new Map(
      this.ctx.storage.sql
        .exec("SELECT key, n FROM counters WHERE key LIKE 'evt:%'")
        .toArray()
        .map((row) => [row.key.slice('evt:'.length), Number(row.n)]),
    );
    return Object.fromEntries(breakdownNames().map((name) => [name, stored.get(name) ?? 0]));
  }

  /**
   * Record one report and return the resulting totals.
   *
   * `{limited: true}` instead means the caller is over its budget — the counts
   * are deliberately not returned with it, so a client cannot use a flood of
   * rejected POSTs to poll the numbers for free.
   */
  record({ n, tool, event, ip }) {
    if (this.#rateLimited(ip)) return { limited: true };
    // The all-time and weekly totals are the "images processed" figure, so only
    // real cut-outs count towards them; an export ('downloaded') moves its own
    // per-tool counter and nothing else.
    if (event === 'processed') {
      this.#add('total', n);
      this.#add(weekKey(), n);
    }
    const key = eventKey(event, tool);
    if (key) this.#add(key, n);
    return { limited: false, ...this.read() };
  }

  #get(key) {
    const row = this.ctx.storage.sql
      .exec('SELECT n FROM counters WHERE key = ?', key)
      .toArray()[0];
    return row ? Number(row.n) : 0;
  }

  #add(key, n) {
    this.ctx.storage.sql.exec(
      'INSERT INTO counters (key, n) VALUES (?, ?) '
      + 'ON CONFLICT(key) DO UPDATE SET n = n + excluded.n',
      key, n,
    );
  }

  /** Fixed window per client IP. Cheap, approximate, and that is the point. */
  #rateLimited(ip) {
    const window = Math.floor(Date.now() / POST_WINDOW_MS);
    const seen = this.recent.get(ip);
    if (seen && seen.window === window) {
      seen.hits += 1;
      return seen.hits > POST_LIMIT;
    }
    // Entries from windows that have passed are dead weight but not worth a
    // sweep on every request; drop the lot once the map is implausibly large.
    if (this.recent.size > 10000) this.recent.clear();
    this.recent.set(ip, { window, hits: 1 });
    return false;
  }
}

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      // The numbers change constantly and are read to be current; nothing about
      // them should sit in a CDN or a browser cache.
      'cache-control': 'no-store',
      ...headers,
    },
  });
}

/** The POST body, or {} for anything that is not a JSON object. */
async function readPayload(request) {
  try {
    const body = await request.json();
    return body && typeof body === 'object' && !Array.isArray(body) ? body : {};
  } catch {
    return {};
  }
}

export default {
  async fetch(request, env) {
    const { pathname, searchParams } = new URL(request.url);

    // assets.run_worker_first routes `/api/stats*` here, which is a prefix: a
    // near miss like /api/statistics lands on the Worker too. Hand anything that
    // is not the endpoint back to the asset router, which answers it with
    // _site/404.html exactly as it does for every other unknown path.
    if (pathname !== '/api/stats' && pathname !== '/api/stats/') {
      return env.ASSETS.fetch(request);
    }

    const stats = env.STATS.get(
      env.STATS.idFromName(SINGLETON),
      // Placement is decided when the instance is first created, and otherwise
      // falls wherever the first request in the world happened to land. Western
      // Europe is where the reads come from; the writes are fire-and-forget.
      { locationHint: 'weur' },
    );

    if (request.method === 'GET' || request.method === 'HEAD') {
      if (searchParams.has('breakdown')) {
        return json({ enabled: true, breakdown: await stats.breakdown() });
      }
      return json({ enabled: true, ...(await stats.read()) });
    }

    if (request.method === 'POST') {
      const payload = await readPayload(request);
      const result = await stats.record({
        n: clampCount(payload.n),
        tool: payload.tool,
        // Legacy payloads sent no event at all and meant a cut-out.
        event: payload.event ?? 'processed',
        ip: request.headers.get('CF-Connecting-IP') || 'unknown',
      });
      if (result.limited) {
        return json({ enabled: true, count: null, error: 'rate_limited' }, 429);
      }
      return json({ enabled: true, count: result.count, week: result.week });
    }

    return json({ error: 'method_not_allowed' }, 405, { allow: 'GET, HEAD, POST' });
  },
};
