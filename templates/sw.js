{% load static %}/* BG Remover service worker — app-shell offline cache. */
// Bump this whenever shipped JS/CSS changes: static filenames aren't hashed in
// production, so a new cache name is what forces every client to drop the old
// cached assets and pull the fresh ones (see the `activate` handler).
const CACHE = 'bgr-v7';
const SHELL = [
  '/',
  '/convert/',
  '/instagram/',
  '/crop/',
  '{% static "css/tailwind.css" %}',
  '{% static "js/app.js" %}',
  '{% static "js/converter.js" %}',
  '{% static "js/instagram.js" %}',
  '{% static "js/crop.js" %}',
  '{% static "js/theme.js" %}',
  '{% static "js/colorpicker.js" %}',
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
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
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
  if (url.origin !== self.location.origin) return; // let the browser handle CDNs

  // Navigations: network-first so updates show, fall back to cache when offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => { cachePut(req, res.clone()); return res; })
        .catch(() => caches.match(req).then((r) => r || caches.match('/'))),
    );
    return;
  }

  // Same-origin assets: stale-while-revalidate. Serve the cached copy instantly
  // (fast, offline-friendly) but always refetch in the background and update the
  // cache, so a redeploy is picked up on the next load — no cache-name bump
  // needed for the change to eventually reach users.
  event.respondWith(
    caches.match(req).then((cached) => {
      const fresh = fetch(req)
        .then((res) => { cachePut(req, res.clone()); return res; })
        .catch(() => cached);
      return cached || fresh;
    }),
  );
});
