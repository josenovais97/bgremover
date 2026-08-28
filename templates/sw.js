{% load static %}/* ClearBG service worker — app-shell offline cache. */
// Assets are served network-first (see the `fetch` handler), so a redeploy is
// picked up on the next online load WITHOUT bumping this name — the manual bump
// is no longer required for freshness. The name is just the offline snapshot's
// store; only bump it if you ever need to force-evict every client's cache.
const CACHE = 'bgr-v23';
// The AI model weights + WASM runtime (~190MB for the full-precision model,
// ~56MB for the quantized one) live on a separate, long-lived cache so a normal
// shell redeploy (which changes CACHE) never evicts them — the model is
// downloaded once, then served instantly and offline on every repeat use.
const MODEL_CACHE = 'bgr-model-v1';
// Cross-origin hosts served cache-first into the long-lived model cache: the
// AI model weights/WASM (staticimgly.com) AND the version-pinned library
// ESM (@imgly, JSZip on cdn.jsdelivr.net). Both are immutable per version, so a
// CDN outage can't break repeat visitors — everything is served from cache.
const MODEL_HOSTS = ['staticimgly.com', 'cdn.jsdelivr.net'];
// The shell is GENERATED from the tool list and the contents of static/js (see
// SHELL_PAGES / SHELL_ASSETS in remover/views.py), not hand-listed here: the
// hand-written version silently fell nine tool pages behind while the offline
// landing page advertised those tools as working without a connection.
const SHELL = [
{% for path in shell_pages %}  '{{ path }}',
{% endfor %}{% for asset in shell_assets %}  '{% static asset %}',
{% endfor %}{% comment %}
  The worker scripts are requested under their unhashed name because the module
  that spawns them resolves them itself, from import.meta.url (see
  SHELL_RUNTIME_ASSETS in remover/views.py) — so precache the name that is
  actually fetched, using the static prefix WITHOUT the manifest hash.
{% endcomment %}{% for asset in shell_runtime_assets %}  '{% get_static_prefix %}{{ asset }}',
{% endfor %}  '/manifest.webmanifest',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()),
  );
});

// Static assets are content-hashed (see config/storage.py), e.g.
// /static/js/app.9d4b502996a1.js. A redeploy therefore mints NEW urls rather
// than replacing existing ones, so nothing would ever evict the old entries —
// unlike the previous unhashed urls, which each deploy simply overwrote. Both
// eviction paths below are keyed on the name WITHOUT the hash, because that is
// what identifies "the same file, rebuilt".
const HASHED_ASSET = /^(\/static\/.+)\.[0-9a-f]{12}(\.\w+)$/;

/** '/static/js/app.9d4b5.js' -> '/static/js/app.js'; null if not hashed. */
function baseName(pathname) {
  const m = HASHED_ASSET.exec(pathname);
  return m ? m[1] + m[2] : null;
}

/** Drop the previous build's SHELL assets: a cached hash of a file this shell
 *  now references under a different hash. Deleting everything the shell does not
 *  list would take the ~50 runtime-cached grid thumbnails with it — those are
 *  current, and evicting them is exactly what breaks the offline homepage. Their
 *  supersession is handled in cachePut instead, where the replacement arrives. */
function pruneStaleAssets() {
  const currentByBase = new Map();
  SHELL.forEach((p) => {
    const url = new URL(p, self.location.origin);
    const base = baseName(url.pathname);
    if (base) currentByBase.set(base, url.href);
  });
  return caches.open(CACHE).then((cache) =>
    cache.keys().then((reqs) =>
      Promise.all(reqs.map((r) => {
        const current = currentByBase.get(baseName(new URL(r.url).pathname));
        return current && current !== r.url ? cache.delete(r) : null;
      })),
    ),
  );
}

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      // Keep the current shell cache AND the model cache; drop stale shell caches.
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE && k !== MODEL_CACHE).map((k) => caches.delete(k))))
      .then(pruneStaleAssets)
      .then(() => self.clients.claim()),
  );
});

function cachePut(req, res) {
  if (!res || !res.ok) return;
  caches.open(CACHE).then((cache) => {
    cache.put(req, res);
    // Hashed assets the shell does not list (grid thumbnails, demo art, social
    // cards) land here and nowhere else, so this is where an older hash of the
    // same file gets dropped — one entry per file, however many deploys pass.
    const base = baseName(new URL(req.url).pathname);
    if (!base) return;
    cache.keys().then((reqs) => reqs.forEach((r) => {
      if (r.url !== req.url && baseName(new URL(r.url).pathname) === base) cache.delete(r);
    }));
  });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // AI model weights/WASM + version-pinned library ESM (cross-origin): cache-first
  // into the long-lived model cache so the heavy download happens once, then
  // repeats are instant + offline and survive a CDN outage.
  if (MODEL_HOSTS.includes(url.hostname)) {
    event.respondWith(
      caches.open(MODEL_CACHE).then((cache) =>
        cache.match(req).then((hit) =>
          hit || fetch(req).then((res) => {
            // Cache full 200s and opaque responses; skip 206 range replies (the
            // Cache API can't store partial content).
            if (res && (res.status === 200 || res.type === 'opaque')) cache.put(req, res.clone());
            return res;
          }),
        ),
      ),
    );
    return;
  }

  if (url.origin !== self.location.origin) return; // let the browser handle other CDNs

  // /api/stats/ answers `Cache-Control: no-store` and its whole value is being
  // current. Without this it would land in the offline snapshot below like any
  // other same-origin GET, and an offline visit would be served a stale count
  // with no hint that it is stale.
  if (url.pathname.indexOf('/api/') === 0) return;

  // Same-origin navigations AND assets: network-first. Always fetch fresh when
  // online (so a redeploy is picked up on the very next load — no cache-name bump
  // needed), and fall back to the cache when offline. The cache is refreshed on
  // every successful fetch, so it stays a current offline snapshot.
  event.respondWith(
    fetch(req)
      .then((res) => { cachePut(req, res.clone()); return res; })
      .catch(() => caches.match(req).then((r) => r || (req.mode === 'navigate' ? caches.match('/') : undefined))),
  );
});
