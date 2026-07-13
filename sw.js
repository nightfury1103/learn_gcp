const CACHE_NAME = "gcp-cert-study-v12";
const ASSETS = [
  "./full-real-study-data.json",
  "./full-real-study-reference.md",
  "./pde.html",
  "./pde-study-data.json",
  "./pde-study-reference.md",
  "./pca_exact_keyword_mindmap_2024_now_360.html",
  "./pca_exact_keyword_mindmap_2024_now_360.svg",
  "./pca_exact_keyword_mindmap_2024_now_360_full.png",
  "./exact-question-keywords.md",
  "./manifest.webmanifest"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
        return response;
      }).catch(() => caches.match("./index.html"))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) =>
      cached || fetch(event.request).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
    )
  );
});
