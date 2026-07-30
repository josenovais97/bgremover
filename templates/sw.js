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
// unlike the previous unhashed urls, which each deploy simply overwrote.
const HASHED_ASSET = /\/static\/.+\.[0-9a-f]{12}\.\w+$/;

/** Drop superseded builds: hashed assets that this SHELL no longer references.
 *  Runtime-cached pages and unhashed assets are left alone — they are still
 *  current, and they are what serves the site offline. */
function pruneStaleAssets() {
  const current = new Set(SHELL.map((p) => new URL(p, self.location.origin).href));
  return caches.open(CACHE).then((cache) =>
    cache.keys().then((reqs) =>
      Promise.all(
        reqs
          .filter((r) => HASHED_ASSET.test(new URL(r.url).pathname) && !current.has(r.url))
          .map((r) => cache.delete(r)),
      ),
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
  if (res && res.ok) caches.open(CACHE).then((c) => c.put(req, res));
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
