{% load static %}/* ClearBG service worker — app-shell offline cache. */
// Assets are served network-first (see the `fetch` handler), so a redeploy is
// picked up on the next online load WITHOUT bumping this name — the manual bump
// is no longer required for freshness. The name is just the offline snapshot's
// store; only bump it if you ever need to force-evict every client's cache.
const CACHE = 'bgr-v16';
// The ~40MB AI model weights + WASM runtime live on a separate, long-lived cache
// so a normal shell redeploy (which changes CACHE) never evicts them — the model
// is downloaded once, then served instantly and offline on every repeat use.
const MODEL_CACHE = 'bgr-model-v1';
// Cross-origin hosts served cache-first into the long-lived model cache: the
// ~40MB AI model weights/WASM (staticimgly.com) AND the version-pinned library
// ESM (@imgly, JSZip on cdn.jsdelivr.net). Both are immutable per version, so a
// CDN outage can't break repeat visitors — everything is served from cache.
const MODEL_HOSTS = ['staticimgly.com', 'cdn.jsdelivr.net'];
const SHELL = [
  '/',
  '/convert/',
  '/instagram/',
  '/crop/',
  '/favicon-generator/',
  '/sticker-maker/',
  '/passport-photo/',
  '/ecommerce/',
  '/blur-background/',
  '{% static "css/tailwind.css" %}',
  '{% static "css/fontawesome.css" %}',
  '{% static "webfonts/fa-solid-900.woff2" %}',
  '{% static "webfonts/fa-regular-400.woff2" %}',
  '{% static "webfonts/fa-brands-400.woff2" %}',
  '{% static "js/app.js" %}',
  '{% static "js/handoff.js" %}',
  '{% static "js/compose-worker.js" %}',
  '{% static "js/converter.js" %}',
  '{% static "js/instagram.js" %}',
  '{% static "js/crop.js" %}',
  '{% static "js/favicon.js" %}',
  '{% static "js/sticker.js" %}',
  '{% static "js/textbehind.js" %}',
  '{% static "js/passport.js" %}',
  '{% static "js/ecommerce.js" %}',
  '{% static "js/blur.js" %}',
  '{% static "js/stats.js" %}',
  '{% static "js/demo.js" %}',
  '{% static "js/theme.js" %}',
  '{% static "js/colorpicker.js" %}',
  '{% static "js/nav.js" %}',
  '/manifest.webmanifest',
  '{% static "img/favicon.svg" %}',
  '{% static "img/icon-192.png" %}',
  '{% static "img/icon-512.png" %}',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      // Keep the current shell cache AND the model cache; drop stale shell caches.
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE && k !== MODEL_CACHE).map((k) => caches.delete(k))))
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
