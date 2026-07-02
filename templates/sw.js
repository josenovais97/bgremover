{% load static %}/* BG Remover service worker — app-shell offline cache. */
const CACHE = 'bgr-v1';
const SHELL = [
  '/',
  '/convert/',
  '{% static "css/tailwind.css" %}',
  '{% static "js/app.js" %}',
  '{% static "js/converter.js" %}',
  '{% static "js/theme.js" %}',
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

  // Same-origin assets: cache-first, then network (and cache it).
  event.respondWith(
    caches.match(req).then((cached) =>
      cached || fetch(req).then((res) => { cachePut(req, res.clone()); return res; }),
    ),
  );
});
