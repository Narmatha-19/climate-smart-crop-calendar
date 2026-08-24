/*
 * Service worker for the Climate-Smart Crop Calendar PWA.
 *
 * Static assets (CSS/JS/icons) are cache-first, since they rarely change
 * and aren't personalized. Pages and API calls are network-first: always
 * prefer the live, session-specific response, and only fall back to a
 * cached copy if the network is unreachable (offline) - avoids ever
 * showing one farmer's cached dashboard to a different session on a
 * shared device while online.
 */
const CACHE_NAME = 'crop-calendar-v1';
const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return; // never intercept POST (logins, form submits, writes)

  const url = new URL(req.url);

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          return res;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(req)
      .then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        return res;
      })
      .catch(() => caches.match(req))
  );
});
