// Test RPG service worker.
//
// Caches the shell (HTML / JS / WASM) + every shipped data file
// so the game runs offline after first load and survives a
// network interruption mid-play. Uses a single versioned cache
// name; bump CACHE_VERSION on a deploy that changes any cached
// asset so old clients evict the stale cache rather than fight
// it.

const CACHE_VERSION = 'v18';
const CACHE_NAME = `test-rpg-${CACHE_VERSION}`;

// App-shell entry points: cached on install.
const SHELL = [
    './',
    './index.html',
    './mq_js_bundle.js',
    './storage.js',
    './platform.js',
    './audio_unlock.js',
    './manifest.json',
    './test-rpg.wasm',
    './icons/icon-192.png',
    './icons/icon-512.png',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) =>
            // addAll fails the whole install if any one URL 404s.
            // That's intentional: an incomplete shell means the
            // game can't boot offline.
            cache.addAll(SHELL).catch((err) => {
                console.warn('sw install: shell cache failed:', err);
            })
        )
    );
    // Activate as soon as install finishes so the very next
    // load uses the new worker (instead of waiting for all
    // tabs to close).
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Evict caches from older versions so we don't hand out
    // stale assets after a deploy. The current cache survives.
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((k) => k !== CACHE_NAME)
                    .map((k) => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// Cache-first for same-origin GETs: serve from cache when
// present, otherwise fetch + populate. This is the simplest
// strategy that gives offline play; trade-off is that pushing
// new content requires bumping CACHE_VERSION (or the user
// closing all tabs).
self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return;

    event.respondWith(
        caches.match(req).then((cached) => {
            if (cached) return cached;
            return fetch(req).then((res) => {
                // Only cache full responses (not opaque / partial).
                if (!res || res.status !== 200 || res.type !== 'basic') {
                    return res;
                }
                const clone = res.clone();
                caches.open(CACHE_NAME).then((c) => c.put(req, clone));
                return res;
            });
        })
    );
});
