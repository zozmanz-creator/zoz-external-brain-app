const CACHE='zoz-brain-v1';
const CORE=['./','./index.html','./manifest.json','./assets/icon.svg'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)));self.skipWaiting();});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',event=>{event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));});
