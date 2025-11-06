/**
 * HubPDF Service Worker
 * Handles caching, offline functionality, and PWA features
 */

const CACHE_NAME = 'hubpdf-v3.3.0';
const STATIC_CACHE = 'hubpdf-static-v3.3';
const DYNAMIC_CACHE = 'hubpdf-dynamic-v3.3';
const API_CACHE = 'hubpdf-api-v3.3';

// Files to cache for offline functionality - UPDATED TO LUCIDE ICONS
const STATIC_ASSETS = [
  '/',
  '/static/css/custom.css',
  '/static/js/app.js',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://unpkg.com/htmx.org@2.0.3',
  'https://unpkg.com/lucide@latest/dist/umd/lucide.js',
  'https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js'
];

// API endpoints to cache with network-first strategy
const API_ENDPOINTS = [
  '/auth/refresh',
  '/set-language'
];

// Pages to cache with stale-while-revalidate strategy
const CACHEABLE_PAGES = [
  '/home',
  '/about',
  '/contact',
  '/privacy',
  '/terms',
  '/billing/pricing'
];

/**
 * Service Worker Installation
 */
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS.map(url => new Request(url, { cache: 'reload' })));
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

/**
 * Service Worker Activation
 */
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Delete old caches
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

/**
 * Fetch Event Handler
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle different types of requests
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
  } else if (isAPIRequest(request)) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
  } else if (isCacheablePage(request)) {
    event.respondWith(staleWhileRevalidateStrategy(request, DYNAMIC_CACHE));
  } else if (isNavigationRequest(request)) {
    event.respondWith(networkWithFallbackStrategy(request));
  }
});

/**
 * Caching Strategies
 */

// Cache First - Good for static assets that rarely change
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Cache First Strategy failed:', error);
    return caches.match('/offline.html') || new Response('Offline', { status: 503 });
  }
}

// Network First - Good for API requests and dynamic content
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Stale While Revalidate - Good for pages that can be stale
async function staleWhileRevalidateStrategy(request, cacheName) {
  const cachedResponse = await caches.match(request);
  
  const networkResponsePromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      const cache = caches.open(cacheName);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(() => {
    // Network failed, but we might have cache
    return null;
  });
  
  return cachedResponse || networkResponsePromise || 
    new Response('Offline', { status: 503 });
}

// Network with Offline Fallback - Good for navigation requests
async function networkWithFallbackStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Try to get from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/') || new Response(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>HubPDF - Offline</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .offline-icon { font-size: 64px; color: #dc2626; margin-bottom: 20px; }
            h1 { color: #374151; }
            p { color: #6b7280; }
          </style>
        </head>
        <body>
          <div class="offline-icon">📄</div>
          <h1>HubPDF - Modo Offline</h1>
          <p>Você está offline. Algumas funcionalidades podem não estar disponíveis.</p>
          <p>Verifique sua conexão com a internet e tente novamente.</p>
          <button onclick="window.location.reload()">Tentar Novamente</button>
        </body>
        </html>
      `, {
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Helper Functions
 */

function isStaticAsset(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/static/') ||
         url.hostname === 'cdn.tailwindcss.com' ||
         url.hostname === 'unpkg.com';
}

function isAPIRequest(request) {
  const url = new URL(request.url);
  return API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint)) ||
         url.pathname.startsWith('/api/');
}

function isCacheablePage(request) {
  const url = new URL(request.url);
  return CACHEABLE_PAGES.includes(url.pathname);
}

function isNavigationRequest(request) {
  return request.mode === 'navigate';
}

/**
 * Background Sync for offline actions
 */
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  // Handle offline actions when back online
  console.log('Service Worker: Handling background sync');
  // Implementation would depend on specific offline functionality needed
}

/**
 * Push Notifications (for future use)
 */
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Nova notificação do HubPDF',
    icon: '/static/icon-192.png',
    badge: '/static/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Abrir HubPDF',
        icon: '/static/checkmark.png'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/static/xmark.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('HubPDF', options)
  );
});

/**
 * Notification click handler
 */
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked', event);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      self.clients.openWindow('/')
    );
  }
});

/**
 * Message handler for communication with main thread
 */
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received', event.data);
  
  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'SKIP_WAITING':
        self.skipWaiting();
        break;
      case 'GET_VERSION':
        event.ports[0].postMessage({ version: CACHE_NAME });
        break;
      case 'CACHE_NEW_ROUTE':
        cacheNewRoute(event.data.url);
        break;
      default:
        console.log('Service Worker: Unknown message type', event.data.type);
    }
  }
});

/**
 * Cache a new route dynamically
 */
async function cacheNewRoute(url) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    await cache.add(url);
    console.log('Service Worker: New route cached', url);
  } catch (error) {
    console.error('Service Worker: Failed to cache new route', url, error);
  }
}

/**
 * Periodic cleanup of old cache entries
 */
async function cleanupCaches() {
  const cacheNames = await caches.keys();
  const cachesToDelete = cacheNames.filter(name => 
    !name.includes(STATIC_CACHE) && 
    !name.includes(DYNAMIC_CACHE) && 
    !name.includes(API_CACHE)
  );
  
  await Promise.all(
    cachesToDelete.map(cache => caches.delete(cache))
  );
  
  console.log('Service Worker: Cache cleanup completed');
}

// Cleanup caches periodically
setInterval(cleanupCaches, 24 * 60 * 60 * 1000); // Daily cleanup
