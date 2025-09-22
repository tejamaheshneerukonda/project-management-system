// Service Worker for ProjectManager Pro
// Version: 1.0.0

const CACHE_NAME = 'projectmanager-pro-cache-v1';
const ASSET_CACHE = 'projectmanager-pro-assets-v1';
const RUNTIME_CACHE = 'projectmanager-pro-runtime-v1';

// Core assets to cache for offline functionality
const CORE_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
  // Add other critical assets here as needed
];

// Resources that shouldn't be cached
const NO_CACHE = [
  '/admin/',
  '/media/',
  '/api/',
  '*.sqlite3',
  '*.py',
  '*.pyc',
  '*.json'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching core assets');
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => {
        // Force activation after installation
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== ASSET_CACHE && cacheName !== RUNTIME_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all clients immediately
  return self.clients.claim();
});

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
  // Skip requests that shouldn't be cached
  if (shouldNotCache(event.request.url)) {
    return;
  }

  // Handle navigation requests
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return caches.open(CACHE_NAME)
            .then(cache => cache.match('/'));
        })
    );
  } else if (isStaticAsset(event.request.url)) {
    // Cache static assets for faster loading
    event.respondWith(
      caches.open(ASSET_CACHE)
        .then(cache => {
          return cache.match(event.request)
            .then(response => {
              // Return cached response if available, otherwise fetch from network
              const fetchPromise = fetch(event.request)
                .then(networkResponse => {
                  cache.put(event.request, networkResponse.clone());
                  return networkResponse;
                });
              return response || fetchPromise;
            });
        })
    );
  } else {
    // Handle API requests and dynamic content
    event.respondWith(
      caches.open(RUNTIME_CACHE)
        .then(cache => {
          return fetch(event.request)
            .then(networkResponse => {
              // Cache successful responses
              if (networkResponse.status === 200) {
                cache.put(event.request, networkResponse.clone());
              }
              return networkResponse;
            })
            .catch(() => {
              // Return cached response if network fails
              return cache.match(event.request);
            });
        })
    );
  }
});

// Helper function to check if a URL should not be cached
function shouldNotCache(url) {
  const parsedUrl = new URL(url, self.location.origin);
  return NO_CACHE.some(pattern => {
    if (pattern.startsWith('*.')) {
      const extension = pattern.substring(2);
      return parsedUrl.pathname.endsWith('.' + extension);
    }
    return parsedUrl.pathname.startsWith(pattern);
  });
}

// Helper function to check if a URL is a static asset
function isStaticAsset(url) {
  const parsedUrl = new URL(url, self.location.origin);
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff2', '.woff', '.ttf'];
  return staticExtensions.some(ext => parsedUrl.pathname.endsWith(ext));
}

// Push notification event handler
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};
  const title = data.title || 'ProjectManager Pro';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-192x192.png',
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clients => {
        if (clients.length > 0) {
          clients[0].focus();
        } else {
          self.clients.openWindow(event.notification.data.url);
        }
      })
  );
});