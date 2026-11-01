/**
 * LoomisAI — Service Worker for PWA Offline Shell & Asset Caching
 * Ensures fast load times and reliable offline access for the studio interface.
 */

const CACHE_NAME = 'loomisai-studio-v1';
const STATIC_ASSETS = [
  '/',
  '/web/index.html',
  '/web/style.css',
  '/web/app.js',
  '/web/manifest.json',
  '/web/icons/icon-192.svg',
  '/web/icons/icon-512.svg'
];

// Install event: Pre-cache static shell assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(STATIC_ASSETS).catch((err) => {
          console.warn('[LoomisAI SW] Pre-cache partial warning:', err);
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event: Clean up previous cache versions
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event: Network-first for dynamic API; Cache-first with network fallback for static assets
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests (e.g. POST /api/upload)
  if (request.method !== 'GET') {
    return;
  }

  // Bypass cache for dynamic API endpoints to ensure fresh drawing pipeline status
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            status: 'offline',
            message: 'Network offline. Connect to internet to run portrait analysis.'
          }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })
    );
    return;
  }

  // For app assets & static shell: Stale-while-revalidate strategy
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const fetchPromise = fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});
