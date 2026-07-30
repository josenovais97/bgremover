/**
 * Unit tests for the service worker's cache eviction (templates/sw.js).
 *
 * Static assets are content-hashed, so a redeploy mints new URLs instead of
 * overwriting old ones — the cache only stays bounded because sw.js evicts by
 * the name WITHOUT the hash. Getting that wrong is invisible in a browser (both
 * "kept everything forever" and "evicted the current thumbnails" look fine
 * online), which is exactly why it is worth a test.
 *
 * sw.js is a Django template, so it can't be imported. Following
 * crop-geometry.test.mjs, the three pure/injectable helpers are extracted from
 * the source text and evaluated with a fake Cache API, so the test exercises
 * exactly the code that ships.
 *
 * Run: node tests/sw-cache.test.mjs   (exit code 0 = pass)
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, '..', 'templates', 'sw.js'), 'utf8');

function extract(re, label) {
  const m = src.match(re);
  if (!m) throw new Error(`Could not find ${label} in sw.js — did it get renamed?`);
  return m[0];
}

// Each helper's inner braces are indented, so the first line-start `}` closes it.
const parts = [
  extract(/const HASHED_ASSET = [^\n]+;/, 'HASHED_ASSET'),
  extract(/function baseName\([\s\S]*?\n}/, 'baseName'),
  extract(/function pruneStaleAssets\([\s\S]*?\n}/, 'pruneStaleAssets'),
  extract(/function cachePut\([\s\S]*?\n}/, 'cachePut'),
].join('\n');

const load = (SHELL, caches) =>
  new Function(
    'SHELL', 'CACHE', 'caches', 'self',
    `${parts}\nreturn { baseName, pruneStaleAssets, cachePut };`,
  )(SHELL, 'test-cache', caches, { location: { origin: 'https://x.test' } });

/** Minimal Cache API over a Map, enough for keys/put/delete. Cache keys are
 *  absolute, as a real Request.url always is. */
function fakeCaches(urls) {
  const store = new Map(urls.map((u) => [abs(u), 'response']));
  const cache = {
    keys: () => Promise.resolve([...store.keys()].map((url) => ({ url }))),
    put: (req, res) => { store.set(req.url, res); return Promise.resolve(); },
    delete: (req) => Promise.resolve(store.delete(req.url)),
  };
  return { api: { open: () => Promise.resolve(cache) }, store };
}

const flush = () => new Promise((r) => setTimeout(r, 0));
const abs = (p) => `https://x.test${p}`;

let failures = 0;
function check(name, cond) {
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`);
  if (!cond) failures++;
}

/* ------------------------------------------------------------- baseName */
{
  const { baseName } = load([], fakeCaches([]).api);
  check('baseName strips the hash', baseName('/static/js/app.9d4b502996a1.js') === '/static/js/app.js');
  check('baseName handles nested dirs', baseName('/static/img/thumbs/a-b.0123456789ab.webp') === '/static/img/thumbs/a-b.webp');
  check('baseName ignores unhashed names', baseName('/static/js/compose-worker.js') === null);
  check('baseName ignores a too-short hash', baseName('/static/js/app.9d4b50.js') === null);
  check('baseName ignores non-static paths', baseName('/remove-background/') === null);
}

/* ----------------------------------------------------- pruneStaleAssets */
{
  const CURRENT = '/static/js/app.dd4ed6b3ab6d.js';
  const PREVIOUS = '/static/js/app.9d4b502996a1.js';
  const THUMB = '/static/img/thumbs/demo-crop-after.aaaabbbbcccc.webp';
  const WORKER = '/static/js/compose-worker.js';
  const { api, store } = fakeCaches([CURRENT, PREVIOUS, THUMB, WORKER, '/', '/manifest.webmanifest']);
  const { pruneStaleAssets } = load([CURRENT, WORKER, '/'], api);

  await pruneStaleAssets();
  check('prune drops the previous build of a shell asset', !store.has(abs(PREVIOUS)));
  check('prune keeps the current shell asset', store.has(abs(CURRENT)));
  // The regression this shape exists to prevent: pruning everything the shell
  // does not list took the grid thumbnails with it, so the offline homepage lost
  // its images on every deploy.
  check('prune keeps a runtime-cached thumbnail', store.has(abs(THUMB)));
  check('prune keeps unhashed assets', store.has(abs(WORKER)));
  check('prune keeps cached pages', store.has(abs('/')) && store.has(abs('/manifest.webmanifest')));
}

/* ------------------------------------------------------------- cachePut */
{
  const OLD = '/static/img/thumbs/demo-crop-after.aaaabbbbcccc.webp';
  const NEW = '/static/img/thumbs/demo-crop-after.111122223333.webp';
  const OTHER = '/static/img/thumbs/demo-blur-after.444455556666.webp';
  const { api, store } = fakeCaches([OLD, OTHER]);
  const { cachePut } = load([], api);

  cachePut({ url: abs(NEW) }, { ok: true });
  await flush();
  check('cachePut stores the new hash', store.has(abs(NEW)));
  check('cachePut evicts the superseded hash', !store.has(abs(OLD)));
  check('cachePut leaves other files alone', store.has(abs(OTHER)));
}
{
  const { api, store } = fakeCaches([]);
  const { cachePut } = load([], api);
  cachePut({ url: abs('/some/page/') }, { ok: false });
  await flush();
  check('cachePut ignores failed responses', store.size === 0);
  cachePut({ url: abs('/some/page/') }, { ok: true });
  await flush();
  check('cachePut still caches unhashed urls', store.has(abs('/some/page/')));
}

console.log(failures ? `\n${failures} check(s) failed` : '\nAll service-worker cache tests passed');
process.exit(failures ? 1 : 0);
