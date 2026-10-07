// Service worker: lưu sẵn app để mở được khi mất mạng.
var VERSION = "xltn-__VERSION__";
var CORE = ["./", "index.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "icons/favicon.png",
  "icons/mark.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(CORE); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION && k.indexOf("xltn-") === 0; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);

  // Trang chính: lấy bản mới khi có mạng, mất mạng thì dùng bản đã lưu
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(function (res) {
      var copy = res.clone();
      caches.open(VERSION).then(function (c) { c.put("index.html", copy); });
      return res;
    }).catch(function () {
      return caches.match("index.html");
    }));
    return;
  }

  // Phông chữ Google: dùng bản đã lưu, có mạng thì cập nhật ngầm
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(caches.open("xltn-fonts").then(function (c) {
      return c.match(req).then(function (hit) {
        var net = fetch(req).then(function (res) { c.put(req, res.clone()); return res; }).catch(function () { return hit; });
        return hit || net;
      });
    }));
    return;
  }

  if (url.origin === self.location.origin) {
    e.respondWith(caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        var copy = res.clone();
        caches.open(VERSION).then(function (c) { c.put(req, copy); });
        return res;
      });
    }));
  }
});
