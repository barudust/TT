// Estrategia "network first": siempre se pide a la red (versión más reciente de
// la interfaz); la caché solo se usa sin conexión. Antes era "cache first" con
// un nombre de caché fijo, y quien ya tenía la PWA se quedaba con una versión
// vieja de la interfaz aunque se desplegara otra. Cambiar CACHE_NAME borra la
// caché anterior al activarse el nuevo service worker.
const CACHE_NAME = 'trading-signals-v2';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Instalar el service worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// Activar el service worker y borrar cachés de versiones anteriores
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Interceptar requests
self.addEventListener('fetch', (event) => {
  // Solo GET del propio origen (la API vive en otro origen y nunca se cachea:
  // sus datos cambian cada día y deben venir siempre del modelo)
  if (event.request.method !== 'GET') {
    return;
  }
  if (new URL(event.request.url).origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() =>
        // Sin conexión: servir lo último guardado (o la página principal)
        caches.match(event.request).then((cached) => cached || caches.match('/index.html'))
      )
  );
});
