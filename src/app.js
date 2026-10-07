(function () {
  "use strict";

  /* ============================================================
     Dữ liệu
     ============================================================ */
  var DATA = JSON.parse(document.getElementById("data").textContent);
  var SIT = {}, SKILL = {}, CAT = {};
  DATA.situations.forEach(function (s) { SIT[s.id] = s; });
  DATA.skills.forEach(function (k) { SKILL[k.id] = k; });
  DATA.categories.forEach(function (c) { CAT[c.id] = c; });

  var SEV_LABEL = { green: "Thường gặp", yellow: "Cần lưu ý", red: "Nguy hiểm" };
  var CHECK_TTL = 12 * 3600 * 1000;   // checklist tự xoá sau 12 giờ

  /* ============================================================
     Lưu trữ an toàn (trình duyệt riêng tư có thể chặn)
     ============================================================ */
  var store = {
    get: function (k, d) {
      try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); }
      catch (e) { return d; }
    },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };

  /* ============================================================
     Tiện ích
     ============================================================ */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function plain(s) { return String(s).replace(/\*\*/g, ""); }

  function refChip(id) {
    if (SKILL[id]) return '<button class="ref" data-skill="' + id + '">' + esc(SKILL[id].short) + "</button>";
    if (SIT[id]) return '<a class="ref" href="#/t/' + id + '">' + esc(SIT[id].title) + "</a>";
    return id;
  }
  // **đậm**, "(xem K1)", "(K5)", "theo K2" thành chip bấm được
  function fmt(s) {
    var h = esc(s);
    h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    h = h.replace(/\s?\((?:xem )?([AKB]\d{1,2})\)/g, function (_, id) { return " " + refChip(id); });
    h = h.replace(/\b(theo|xem) ([AKB]\d{1,2})\b/g, function (_, w, id) { return w + " " + refChip(id); });
    return h;
  }

  // Bỏ dấu tiếng Việt, giữ nguyên độ dài từng ký tự để còn tô sáng được
  function normChar(c) {
    if (c === "đ" || c === "Đ") return "d";
    var n = c.normalize("NFD").replace(/[̀-ͯ]/g, "");
    return (n.length === 1 ? n : c).toLowerCase();
  }
  function norm(s) {
    var out = "";
    for (var i = 0; i < s.length; i++) out += normChar(s[i]);
    return out;
  }

  var ICON = {
    chev: '<svg class="chev" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    tw: '<svg class="tw" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    check: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    phone: '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M6.6 3.5l2.6-.3 1.6 4.3-2 1.5a12 12 0 0 0 6.2 6.2l1.5-2 4.3 1.6-.3 2.6a2.5 2.5 0 0 1-2.6 2.1C10.4 21 3 13.6 4.5 6.1a2.5 2.5 0 0 1 2.1-2.6z" fill="currentColor"/></svg>',
    alert: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M12 3.5l9 16H3z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M12 10v4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17" r="1.3" fill="currentColor"/></svg>',
    search: '<svg class="s-icon" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    x: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
    prevent: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z" fill="currentColor"/></svg>',
    avoid: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M6 6l12 12" stroke="currentColor" stroke-width="2.6"/></svg>',
    doctor: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5z" fill="currentColor"/></svg>',
    info: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 11v6" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><circle cx="12" cy="7.5" r="1.5" fill="currentColor"/></svg>'
  };

  function dots(sev) {
    return '<span class="dots" aria-hidden="true">' +
      sev.map(function (c) { return '<span class="dot ' + c + '"></span>'; }).join("") + "</span>";
  }
  function sevNote(sev) {
    var g = sev.indexOf("green") > -1, y = sev.indexOf("yellow") > -1, r = sev.indexOf("red") > -1;
    if (r && !g && !y) return "Cần đi khám ngay.";
    if (r && g) return "Thường không nguy hiểm, nhưng có trường hợp phải đi cấp cứu.";
    if (r) return "Có thể nguy hiểm. Đọc kỹ các dấu hiệu phải đi khám.";
    if (y && g) return "Thường xử lý được tại nhà, đôi khi cần hỏi bác sĩ.";
    if (y) return "Nên hỏi bác sĩ nếu không đỡ sau 24-48 giờ.";
    return "Thường gặp, chăm sóc được tại nhà.";
  }
  function sevA11y(sev) { return sev.map(function (c) { return SEV_LABEL[c]; }).join(" đến "); }

  /* ============================================================
     Checklist: đánh dấu từng bước đã làm
     ============================================================ */
  function checkKey(id) { return "xltn-check-" + id; }
  function loadCheck(id) {
    var c = store.get(checkKey(id), null);
    if (!c || Date.now() - c.ts > CHECK_TTL) return { ts: 0, done: {} };
    return c;
  }
  function saveCheck(id, c) {
    if (Object.keys(c.done).length) store.set(checkKey(id), c);
    else store.del(checkKey(id));
  }
  function timeStr(ts) {
    var d = new Date(ts);
    return d.getHours() + ":" + String(d.getMinutes()).padStart(2, "0");
  }

  function renderSteps(ownerId, sec, si, check) {
    var total = sec.items.length;
    var n = 0;
    var lis = sec.items.map(function (it, i) {
      var key = si + "-" + i;
      var done = !!check.done[key];
      if (done) n++;
      var sub = "";
      if (it.children.length) {
        var ol = /^\d/.test(it.children[0]) ? "" : "";
        sub = '<ul class="sub' + ol + '">' + it.children.map(function (c) {
          return "<li>" + fmt(c) + "</li>";
        }).join("") + "</ul>";
      }
      return '<li class="step' + (done ? " done" : "") + '" data-owner="' + ownerId + '" data-key="' + key +
        '" role="checkbox" aria-checked="' + done + '" tabindex="0">' +
        '<span class="step-n"><span>' + (i + 1) + "</span>" + ICON.check + "</span>" +
        '<div class="step-body"><div class="step-text">' + fmt(it.text) + "</div>" + sub + "</div></li>";
    }).join("");
    var label = sec.label || "Các bước";
    return '<section class="block k-steps" data-sec="' + si + '">' +
      '<div class="block-head"><h2>' + esc(label) + "</h2>" +
      '<span class="progress' + (n === total ? " done" : "") + '" data-progress="' + si + '">' + n + "/" + total + "</span></div>" +
      '<ol class="steps">' + lis + "</ol></section>";
  }

  function renderOther(sec, opts) {
    var kind = sec.kind;
    var open = kind !== "prevent" || opts.openAll;
    var label = sec.label || "Ghi chú";
    var body = "";
    if (sec.text) body += '<p class="ptext">' + fmt(sec.text) + "</p>";
    if (sec.items.length) {
      body += '<ul class="blist">' + sec.items.map(function (it) {
        var sub = it.children.length ? '<ul class="sub">' + it.children.map(function (c) {
          return "<li>" + fmt(c) + "</li>"; }).join("") + "</ul>" : "";
        return "<li>" + fmt(it.text) + sub + "</li>";
      }).join("") + "</ul>";
    }
    if (kind === "doctor" && opts.call) {
      body += '<a class="btn danger big call" href="tel:115">' + ICON.phone + "Gọi cấp cứu 115</a>";
    }
    return '<details class="block k-' + kind + '"' + (open ? " open" : "") +
      (kind === "doctor" ? ' id="kham"' : "") + "><summary>" +
      '<span class="k-ico">' + (ICON[kind] || ICON.info) + "</span><h2>" + esc(label) + "</h2>" + ICON.tw +
      "</summary>" + body + "</details>";
  }

  function renderItemBody(item, opts) {
    opts = opts || {};
    var check = loadCheck(item.id);
    var hasRed = (item.severity || []).indexOf("red") > -1;
    var html = "";
    var stepSecs = 0;
    item.sections.forEach(function (sec, si) {
      if (sec.kind === "steps") {
        stepSecs++;
        html += renderSteps(item.id, sec, si, check);
      } else {
        html += renderOther(sec, { call: hasRed || /cấp cứu/i.test(sec.label || ""), openAll: opts.openAll });
      }
    });
    (item.notes || []).forEach(function (n) {
      html += '<div class="note">' + ICON.info.replace("<svg ", '<svg width="20" height="20" style="flex:none;margin-top:2px" ') +
        "<div>" + fmt(n) + "</div></div>";
    });
    var bar = "";
    if (stepSecs) {
      bar = '<div class="since" data-since="' + item.id + '">' + sinceText(check) + "</div>";
    }
    return bar + html;
  }
  function sinceText(check) {
    if (!check.ts || !Object.keys(check.done).length) return "Chạm vào từng bước để đánh dấu đã làm.";
    return 'Đánh dấu từ lúc ' + timeStr(check.ts) + ' · <button class="reset" data-reset>Làm lại từ đầu</button>';
  }

  function toggleStep(el) {
    var owner = el.getAttribute("data-owner"), key = el.getAttribute("data-key");
    var c = loadCheck(owner);
    var on = !c.done[key];
    if (on) { c.done[key] = 1; if (!c.ts) c.ts = Date.now(); }
    else delete c.done[key];
    if (!Object.keys(c.done).length) c.ts = 0;
    saveCheck(owner, c);
    el.classList.toggle("done", on);
    el.setAttribute("aria-checked", on);
    if (on && navigator.vibrate) { try { navigator.vibrate(12); } catch (e) {} }
    refreshProgress(el.closest(".block"), owner);
  }
  function refreshProgress(block, owner) {
    if (!block) return;
    var all = block.querySelectorAll(".step").length;
    var n = block.querySelectorAll(".step.done").length;
    var p = block.querySelector(".progress");
    if (p) { p.textContent = n + "/" + all; p.classList.toggle("done", n === all); }
    var root = block.parentNode;
    var since = root.querySelector('[data-since="' + owner + '"]');
    if (since) since.innerHTML = sinceText(loadCheck(owner));
  }

  /* ============================================================
     Tìm kiếm
     ============================================================ */
  var INDEX = [];
  function bodyText(item) {
    var parts = [];
    item.sections.forEach(function (s) {
      if (s.label) parts.push(s.label);
      if (s.text) parts.push(s.text);
      s.items.forEach(function (it) { parts.push(it.text); parts = parts.concat(it.children); });
    });
    return plain(parts.join(" · ")).replace(/\(xem [AKB]\d+\)|\([AKB]\d+\)/g, "");
  }
  function buildIndex() {
    DATA.situations.concat(DATA.skills).forEach(function (it) {
      var body = bodyText(it);
      INDEX.push({ item: it, t: norm(it.title), k: norm(it.keywords || ""), b: norm(body), body: body });
    });
  }
  // vị trí đầu tiên mà t khớp ở đầu một từ ("ho" khớp "ho khan", không khớp "hơi")
  // từ ngắn 1-2 chữ phải khớp trọn từ, nếu không "ho" sẽ khớp cả "hơi"
  function wordAt(text, t) {
    var whole = t.length <= 2;
    var i = text.indexOf(t);
    while (i > -1) {
      var startOk = i === 0 || !/[a-z0-9]/.test(text[i - 1]);
      var endOk = !whole || !/[a-z0-9]/.test(text[i + t.length] || "");
      if (startOk && endOk) return i;
      i = text.indexOf(t, i + 1);
    }
    return -1;
  }
  function search(q) {
    var nq = norm(q.trim()).replace(/\s+/g, " ");
    if (!nq) return [];
    var toks = nq.split(" ").filter(Boolean);
    var res = [];
    INDEX.forEach(function (d) {
      var score = 0, ok = true;
      toks.forEach(function (t) {
        var s = 0;
        if (wordAt(d.t, t) > -1) s += 12;
        if (wordAt(d.k, t) > -1) s += 7;
        if (wordAt(d.b, t) > -1) s += 1;
        if (!s) ok = false;
        score += s;
      });
      if (!ok) return;
      if (toks.length > 1) {
        if (wordAt(d.t, nq) > -1) score += 20;
        if (wordAt(d.k, nq) > -1) score += 12;
        if (wordAt(d.b, nq) > -1) score += 3;
      }
      if (d.item.id[0] === "K") score -= 2;
      res.push({ d: d, score: score, toks: toks, nq: nq });
    });
    res.sort(function (a, b) { return b.score - a.score; });
    return res.slice(0, 30);
  }
  function snippet(r) {
    var d = r.d;
    var needle = wordAt(d.b, r.nq) > -1 ? r.nq : null;
    if (!needle) {
      for (var i = 0; i < r.toks.length; i++) if (wordAt(d.b, r.toks[i]) > -1) { needle = r.toks[i]; break; }
    }
    var at = needle ? wordAt(d.b, needle) : -1;
    if (at < 0) return d.item.severity && d.item.severity.length ? esc(sevNote(d.item.severity)) : "Kỹ năng cơ bản";
    var start = Math.max(0, at - 36);
    var end = Math.min(d.body.length, at + needle.length + 70);
    // cắt ở ranh giới từ cho gọn
    if (start > 0) { var sp = d.body.indexOf(" ", start); if (sp > -1 && sp < at) start = sp + 1; }
    return (start > 0 ? "…" : "") + esc(d.body.slice(start, at)) + "<mark>" + esc(d.body.slice(at, at + needle.length)) +
      "</mark>" + esc(d.body.slice(at + needle.length, end)) + (end < d.body.length ? "…" : "");
  }

  /* ============================================================
     Các trang
     ============================================================ */
  var view = $("#view");
  var top = $(".top");
  var lastQuery = "";

  function rowFor(it, sub) {
    var isSkill = it.id[0] === "K";
    var href = isSkill ? "#/ky-nang/" + it.id : "#/t/" + it.id;
    var lead = isSkill ? '<span class="k-badge">' + it.id + "</span>" : dots(it.severity);
    return '<a class="row" href="' + href + '"' + (isSkill ? "" : ' aria-label="' + esc(it.title + ", " + sevA11y(it.severity)) + '"') + ">" +
      lead + '<span class="row-main"><span class="row-title">' + esc(it.title) + "</span>" +
      (sub ? '<span class="row-sub">' + sub + "</span>" : "") + "</span>" + ICON.chev + "</a>";
  }

  function pageHome() {
    var cats = DATA.categories.map(function (c) {
      return '<a class="cat' + (c.id === "me" ? " me" : "") + '" href="#/nhom/' + c.id + '">' +
        '<span class="cat-icon" aria-hidden="true">' + c.icon + "</span>" +
        '<span class="cat-title">' + esc(c.title) + "</span>" +
        '<span class="cat-count">' + c.items.length + " tình huống</span></a>";
    }).join("");
    var chips = DATA.skills.map(function (k) {
      return '<a class="chip" href="#/ky-nang/' + k.id + '">' + esc(k.short) + "</a>";
    }).join("");
    view.innerHTML =
      "<h1>Bé hoặc mẹ đang gặp chuyện gì?</h1>" +
      '<div class="search">' + ICON.search +
      '<input id="q" type="search" inputmode="search" autocomplete="off" enterkeyhint="search" ' +
      'placeholder="Gõ: trớ sữa, sốt, tắc sữa…" aria-label="Tìm tình huống" value="' + esc(lastQuery) + '">' +
      '<button class="s-clear" id="qClear" aria-label="Xoá tìm kiếm"' + (lastQuery ? "" : " hidden") + ">" + ICON.x + "</button></div>" +
      '<div id="results"></div>' +
      '<div id="browse">' +
      '<div class="cats">' + cats + "</div>" +
      '<div class="legend"><span><i class="dot green"></i>Thường gặp</span><span><i class="dot yellow"></i>Cần lưu ý</span><span><i class="dot red"></i>Có thể nguy hiểm</span></div>' +
      '<div class="eyebrow">Kỹ năng cơ bản</div><div class="chips">' + chips + "</div>" +
      installCard() +
      '<p class="disclaimer">Thông tin tham khảo theo khuyến nghị phổ biến của WHO, AAP và Bộ Y tế. Không thay thế bác sĩ. Khi thấy dấu hiệu nguy hiểm hoặc khi bố mẹ thấy bất an, hãy đưa bé đi khám.</p>' +
      "</div>";
    var q = $("#q");
    q.addEventListener("input", function () { lastQuery = q.value; showResults(); });
    $("#qClear").addEventListener("click", function () { lastQuery = ""; q.value = ""; showResults(); q.focus(); });
    showResults();
  }
  function showResults() {
    var box = $("#results"), browse = $("#browse"), clear = $("#qClear");
    if (!box) return;
    clear.hidden = !lastQuery;
    if (!lastQuery.trim()) { box.innerHTML = ""; browse.hidden = false; return; }
    browse.hidden = true;
    var res = search(lastQuery);
    if (!res.length) {
      box.innerHTML = '<div class="search-empty">Chưa tìm thấy <strong>“' + esc(lastQuery) + '”</strong>.<br>Thử từ khác, ví dụ “nôn”, “ho”, “đau ti”.</div>' +
        '<a class="btn big" href="#/" data-clear>Xem tất cả các nhóm</a>';
      return;
    }
    box.innerHTML = '<div class="list">' + res.map(function (r) { return rowFor(r.d.item, snippet(r)); }).join("") + "</div>";
  }

  function pageCategory(id) {
    var c = CAT[id];
    if (!c) return notFound();
    setTitle(c.title);
    view.innerHTML = "<h1>" + c.icon + " " + esc(c.title) + "</h1>" +
      '<p class="lede">' + (id === "me" ? "Các vấn đề mẹ hay gặp trong 6 tuần đầu sau sinh." : "Chọn tình huống đang gặp.") + "</p>" +
      '<div class="list">' + c.items.map(function (sid) {
        var s = SIT[sid];
        return rowFor(s, esc(sevNote(s.severity)));
      }).join("") + "</div>" +
      '<div class="legend"><span><i class="dot green"></i>Thường gặp</span><span><i class="dot yellow"></i>Cần lưu ý</span><span><i class="dot red"></i>Có thể nguy hiểm</span></div>';
  }

  function pageSituation(id) {
    var s = SIT[id];
    if (!s) return notFound();
    setTitle(s.title);
    var hasRed = s.severity.indexOf("red") > -1;
    var redOnly = hasRed && s.severity.length === 1;
    var pills = s.severity.map(function (c) { return '<span class="pill ' + c + '">' + SEV_LABEL[c] + "</span>"; }).join("");
    var alert = "";
    if (redOnly) {
      alert = '<a class="alert" href="tel:115">' + ICON.phone + "<span>Tình huống này cần đi khám ngay. Bấm để gọi 115.</span></a>";
    } else if (hasRed && s.sections.some(function (x) { return x.kind === "doctor"; })) {
      alert = '<a class="alert" href="#kham" data-jump="kham">' + ICON.alert + "<span>Có trường hợp phải đi cấp cứu. Xem các dấu hiệu.</span></a>";
    }
    var cats = DATA.categories.filter(function (c) { return c.items.indexOf(id) > -1; });
    view.innerHTML =
      '<div class="sit-head"><h1 id="pageH1">' + esc(s.title) + "</h1>" +
      '<div class="sev">' + pills + "</div>" +
      '<p class="sev-note">' + esc(sevNote(s.severity)) + "</p></div>" +
      alert + renderItemBody(s) +
      '<p class="disclaimer">Nhóm: ' + cats.map(function (c) {
        return '<a href="#/nhom/' + c.id + '">' + esc(c.title) + "</a>"; }).join(", ") +
      ". Thông tin tham khảo, không thay thế bác sĩ.</p>";
  }

  function pageSkills() {
    setTitle("Kỹ năng cơ bản");
    view.innerHTML = '<h1>Kỹ năng cơ bản</h1><p class="lede">Những thao tác dùng lại ở nhiều tình huống. Nên đọc trước một lần khi bé còn khoẻ.</p>' +
      '<div class="list">' + DATA.skills.map(function (k) {
        var n = k.sections.reduce(function (a, s) { return a + s.items.length; }, 0);
        return rowFor(k, n + " bước");
      }).join("") + "</div>";
  }

  function pageSkill(id) {
    var k = SKILL[id];
    if (!k) return notFound();
    setTitle(k.title);
    var used = DATA.situations.filter(function (s) {
      return JSON.stringify(s.sections).indexOf(id) > -1;
    });
    view.innerHTML = '<div class="sit-head"><h1 id="pageH1">' + esc(k.title) + "</h1></div>" + renderItemBody(k) +
      (used.length ? '<div class="eyebrow">Dùng trong các tình huống</div><div class="list">' +
        used.map(function (s) { return rowFor(s, ""); }).join("") + "</div>" : "");
  }

  function pageEmergency() {
    setTitle("Cấp cứu");
    var groups = DATA.emergency.map(function (g) {
      var items = [];
      g.sections.forEach(function (s) { items = items.concat(s.items); });
      return '<section class="block k-doctor"><div class="block-head"><span class="k-ico">' + ICON.doctor +
        "</span><h2>" + (g.title === "Bé" ? "Bé" : "Mẹ") + "</h2></div>" +
        '<ul class="blist">' + items.map(function (it) { return "<li>" + fmt(it.text) + "</li>"; }).join("") + "</ul></section>";
    }).join("");
    view.innerHTML =
      '<div class="sos-hero"><h1>Cấp cứu</h1><p>Thấy bất kỳ dấu hiệu nào bên dưới: gọi 115 hoặc đến bệnh viện gần nhất ngay.</p>' +
      '<a class="sos-call" href="tel:115">' + ICON.phone + "Gọi 115</a></div>" +
      '<div class="sos-quick">' +
      '<a href="#/ky-nang/K6">Sơ cứu hóc dị vật<small>Bé dưới 1 tuổi</small></a>' +
      '<a href="#/cong-cu">Đếm nhịp thở<small>Đồng hồ 60 giây</small></a>' +
      '<a href="#/t/A17">Sốt<small>Bé dưới 3 tháng là cấp cứu</small></a>' +
      '<a href="#/t/A24">Bé bị ngã<small>Dấu hiệu cần đi viện</small></a>' +
      "</div>" +
      '<div class="eyebrow">Đi cấp cứu ngay khi</div>' + groups +
      '<div class="note">' + ICON.info.replace("<svg ", '<svg width="20" height="20" style="flex:none;margin-top:2px" ') +
      "<div>Khi gọi 115, nói <strong>địa chỉ</strong> trước, sau đó nói tuổi của bé, bé đang bị gì, bé còn thở và còn tỉnh không. Mang theo sổ khám và giấy ra viện.</div></div>";
  }

  function notFound() {
    setTitle("");
    view.innerHTML = '<h1>Không tìm thấy trang</h1><p class="lede">Đường dẫn này không còn tồn tại.</p><a class="btn primary" href="#/">Về trang chủ</a>';
  }

  /* ============================================================
     Công cụ: đếm nhịp thở, hẹn giờ đo lại nhiệt độ
     ============================================================ */
  var breath = { age: store.get("xltn-breath-age", "u2"), state: "idle", count: 0, start: 0, raf: 0, timer: 0 };
  var LIMIT = { u2: 60, o2: 50 };

  function pageTools() {
    setTitle("Công cụ");
    view.innerHTML =
      '<h1>Công cụ</h1><p class="lede">Dùng khi đang theo dõi bé.</p>' +
      '<section class="tool" id="breathTool"><h2>Đếm nhịp thở</h2>' +
      "<p>Đếm khi bé nằm yên hoặc đang ngủ. Mỗi lần bụng bé phồng lên, chạm vào ô bên dưới một lần.</p>" +
      '<div class="seg" role="group" aria-label="Tuổi của bé">' +
      '<button data-age="u2">Dưới 2 tháng</button><button data-age="o2">2-12 tháng</button></div>' +
      '<button class="tap idle" id="tap"></button>' +
      '<div class="timer-bar"><i id="bar"></i></div><div class="timer-meta"><span id="tLeft"></span><span id="tHint"></span></div>' +
      '<div id="verdict"></div></section>' +
      '<section class="tool" id="tempTool"><h2>Hẹn giờ đo lại nhiệt độ</h2>' +
      "<p>Sau khi hạ sốt hoặc ủ ấm, đo lại theo giờ hẹn. Chuông chỉ kêu khi app đang mở, nên để điện thoại gần bên.</p>" +
      '<div id="tempBox"></div><p style="margin:12px 0 0">' + refChip("K3") + "</p></section>";
    view.querySelectorAll("[data-age]").forEach(function (b) {
      b.addEventListener("click", function () {
        if (breath.state === "run") return;
        breath.age = b.getAttribute("data-age");
        store.set("xltn-breath-age", breath.age);
        drawBreath();
      });
    });
    $("#tap").addEventListener("pointerdown", onTap);
    $("#tap").addEventListener("keydown", function (e) { if (e.key === " " || e.key === "Enter") { e.preventDefault(); onTap(e); } });
    drawBreath();
    drawTemp();
  }

  function onTap(e) {
    if (e && e.type === "pointerdown") e.preventDefault();
    if (breath.state === "idle" || breath.state === "done") {
      breath.state = "run"; breath.count = 0; breath.start = Date.now();
      wakeLock(true);
      tickBreath();
    } else if (breath.state === "run") {
      breath.count++;
      if (navigator.vibrate) { try { navigator.vibrate(8); } catch (x) {} }
    }
    drawBreath();
  }
  function tickBreath() {
    cancelAnimationFrame(breath.raf);
    var loop = function () {
      if (breath.state !== "run") return;
      var el = Date.now() - breath.start;
      if (el >= 60000) {
        breath.state = "done"; wakeLock(false); beep(1); drawBreath(); return;
      }
      var bar = $("#bar"), left = $("#tLeft");
      if (!bar) { breath.state = "idle"; wakeLock(false); return; }
      bar.style.width = (el / 600) + "%";
      left.textContent = "Còn " + Math.ceil((60000 - el) / 1000) + " giây";
      breath.raf = requestAnimationFrame(loop);
    };
    loop();
  }
  function drawBreath() {
    var tap = $("#tap");
    if (!tap) return;
    view.querySelectorAll("[data-age]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-age") === breath.age);
    });
    var lim = LIMIT[breath.age];
    $("#tHint").textContent = "Bình thường dưới " + lim + " lần/phút";
    var v = $("#verdict");
    if (breath.state === "run") {
      tap.className = "tap";
      tap.innerHTML = '<span class="big">' + breath.count + '</span><span class="small">Chạm mỗi lần bé hít vào</span>';
      v.innerHTML = "";
    } else if (breath.state === "done") {
      tap.className = "tap idle";
      tap.innerHTML = '<span class="big">' + breath.count + '</span><span class="small">lần/phút · Chạm để đếm lại</span>';
      $("#bar").style.width = "100%";
      $("#tLeft").textContent = "Đã đủ 60 giây";
      var n = breath.count;
      if (n >= lim) {
        v.innerHTML = '<div class="verdict bad"><strong>Thở nhanh: ' + n + " lần/phút</strong>" +
          "Đếm lại một lần nữa khi bé nằm thật yên. Nếu vẫn từ " + lim + " lần trở lên, hoặc bé rút lõm ngực, phập phồng cánh mũi, tím môi: đi khám ngay.</div>" +
          '<a class="btn danger big" style="margin-top:10px" href="tel:115">' + ICON.phone + "Gọi 115</a>";
      } else if (n < 20) {
        v.innerHTML = '<div class="verdict bad"><strong>Chỉ đếm được ' + n + " lần</strong>" +
          "Có thể đã đếm sót, hãy đếm lại. Nếu bé có lúc ngừng thở trên 20 giây, tím tái hoặc khó đánh thức: gọi 115 ngay.</div>";
      } else {
        v.innerHTML = '<div class="verdict ok"><strong>' + n + " lần/phút: trong giới hạn bình thường</strong>" +
          "Vẫn theo dõi thêm các dấu hiệu rút lõm ngực, phập phồng cánh mũi, tím môi.</div>";
      }
    } else {
      tap.className = "tap idle";
      tap.innerHTML = '<span class="big" style="font-size:40px">Bắt đầu</span><span class="small">Chạm để bắt đầu đếm 60 giây</span>';
      $("#bar").style.width = "0";
      $("#tLeft").textContent = "60 giây";
      v.innerHTML = "";
    }
  }

  // ---- hẹn giờ nhiệt độ ----
  var tempTick = 0;
  function tempEnd() { return store.get("xltn-temp-end", 0); }
  function drawTemp() {
    var box = $("#tempBox");
    if (!box) return;
    var end = tempEnd();
    if (!end) {
      box.innerHTML = '<div class="row-btns"><button class="btn primary" data-temp="30">Sau 30 phút</button>' +
        '<button class="btn primary" data-temp="60">Sau 60 phút</button></div>';
    } else {
      var left = end - Date.now();
      box.innerHTML = '<div class="countdown' + (left <= 0 ? " ring" : "") + '" id="tempLeft">' + fmtLeft(left) + "</div>" +
        '<div class="row-btns"><button class="btn" data-temp="stop">' + (left <= 0 ? "Tắt chuông" : "Huỷ hẹn giờ") + "</button></div>" +
        '<p style="margin:10px 0 0;font-size:14px">Hẹn lúc ' + timeStr(end) + ".</p>";
    }
    box.querySelectorAll("[data-temp]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-temp");
        if (v === "stop") { store.del("xltn-temp-end"); stopAlarm(); }
        else { unlockAudio(); store.set("xltn-temp-end", Date.now() + (+v) * 60000); toast("Đã hẹn giờ " + v + " phút"); }
        drawTemp(); checkTemp();
      });
    });
  }
  function fmtLeft(ms) {
    if (ms <= 0) return "Đến giờ!";
    var s = Math.ceil(ms / 1000), m = Math.floor(s / 60);
    return String(m).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  }
  var alarming = false, alarmLoop = 0;
  function checkTemp() {
    clearInterval(tempTick);
    var end = tempEnd();
    if (!end) { stopAlarm(); return; }
    var step = function () {
      var left = tempEnd() - Date.now();
      var el = $("#tempLeft");
      if (el) el.textContent = fmtLeft(left);
      if (left <= 0 && !alarming) startAlarm();
    };
    step();
    tempTick = setInterval(step, 1000);
  }
  function startAlarm() {
    alarming = true;
    drawTemp();
    showAlarmBar();
    var ring = function () {
      beep(3);
      if (navigator.vibrate) { try { navigator.vibrate([300, 150, 300]); } catch (e) {} }
    };
    ring();
    alarmLoop = setInterval(ring, 4000);
  }
  function stopAlarm() {
    alarming = false;
    clearInterval(alarmLoop);
    var bar = $(".alarm-bar");
    if (bar) bar.remove();
  }
  function showAlarmBar() {
    if (!alarming || $(".alarm-bar")) return;
    var bar = document.createElement("div");
    bar.className = "alarm-bar";
    bar.innerHTML = "<span>🌡️ Đến giờ đo lại nhiệt độ cho bé</span>" +
      '<button class="btn" data-alarm-off>Đã biết</button>';
    view.insertBefore(bar, view.firstChild);
  }

  // ---- âm thanh ----
  var actx = null;
  function unlockAudio() {
    try {
      if (!actx) actx = new (window.AudioContext || window.webkitAudioContext)();
      if (actx.state === "suspended") actx.resume();
    } catch (e) {}
  }
  function beep(times) {
    if (!actx) return;
    try {
      for (var i = 0; i < times; i++) {
        var t = actx.currentTime + i * 0.35;
        var o = actx.createOscillator(), g = actx.createGain();
        o.type = "sine"; o.frequency.value = 880;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.35, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
        o.connect(g); g.connect(actx.destination);
        o.start(t); o.stop(t + 0.27);
      }
    } catch (e) {}
  }

  // ---- giữ màn hình sáng khi đang đếm ----
  var lock = null;
  function wakeLock(on) {
    try {
      if (on && "wakeLock" in navigator && !lock) {
        navigator.wakeLock.request("screen").then(function (l) { lock = l; }).catch(function () {});
      } else if (!on && lock) { lock.release(); lock = null; }
    } catch (e) {}
  }

  /* ============================================================
     Cài app lên màn hình chính
     ============================================================ */
  var deferredPrompt = null;
  var isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault(); deferredPrompt = e;
    var slot = $("#installSlot");
    if (slot) slot.outerHTML = installCard();
  });
  function installCard() {
    if (isStandalone || store.get("xltn-install-hide", false)) return "";
    var how;
    if (deferredPrompt) how = '<button class="btn primary" data-install>Cài app</button>';
    else if (isIOS) how = "";
    else how = "";
    var text = isIOS
      ? "Trong Safari, bấm nút <strong>Chia sẻ</strong> (ô vuông có mũi tên), rồi chọn <strong>Thêm vào MH chính</strong>."
      : deferredPrompt
        ? "Mở nhanh từ màn hình chính, dùng được cả khi mất mạng."
        : "Trong Chrome, mở menu <strong>⋮</strong> rồi chọn <strong>Thêm vào màn hình chính</strong>.";
    return '<div class="install" id="installSlot"><span class="install-icon" aria-hidden="true"></span><div>' +
      "<strong>Cài lên màn hình điện thoại</strong><p>" + text + " Sau khi cài, app chạy được cả khi không có mạng.</p>" +
      '<div class="btns">' + how + '<button class="btn ghost" data-install-hide>Ẩn gợi ý này</button></div></div></div>';
  }

  /* ============================================================
     Bảng trượt xem nhanh kỹ năng
     ============================================================ */
  var sheet = $("#sheet"), lastFocus = null;
  function openSheet(id) {
    var k = SKILL[id];
    if (!k) return;
    lastFocus = document.activeElement;
    $("#sheetTitle").textContent = k.title;
    $("#sheetBody").innerHTML = renderItemBody(k) +
      '<a class="btn" style="width:100%" href="#/ky-nang/' + id + '" data-close-sheet>Mở trang riêng</a>';
    sheet.hidden = false;
    document.body.style.overflow = "hidden";
    $(".sheet-x").focus();
  }
  function closeSheet() {
    if (sheet.hidden) return;
    sheet.hidden = true;
    document.body.style.overflow = "";
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* ============================================================
     Điều hướng
     ============================================================ */
  var scrollMem = {};
  var curHash = null;
  var depth = 0;

  function setTitle(t) { $("#topTitle").textContent = t || ""; }

  function route() {
    var h = location.hash || "#/";
    if (curHash !== null) scrollMem[curHash] = window.scrollY;
    var parts = h.replace(/^#\/?/, "").split("/");
    var tab = "home";
    closeSheet();
    setTitle("");
    if (h === "#kham") return;
    if (!parts[0]) { pageHome(); }
    else if (parts[0] === "nhom") { pageCategory(parts[1]); }
    else if (parts[0] === "t") { pageSituation(parts[1]); }
    else if (parts[0] === "ky-nang") { tab = "skills"; parts[1] ? pageSkill(parts[1]) : pageSkills(); }
    else if (parts[0] === "cong-cu") { tab = "tools"; pageTools(); }
    else if (parts[0] === "cap-cuu") { tab = "sos"; pageEmergency(); }
    else notFound();

    var inner = !!parts[0] && ["ky-nang", "cong-cu", "cap-cuu"].indexOf(parts[0]) === -1 || (parts[0] === "ky-nang" && parts[1]);
    top.classList.toggle("inner", !!inner);
    $("#back").hidden = !inner;
    top.classList.remove("show-title");
    document.querySelectorAll(".tabs a").forEach(function (a) {
      a.classList.toggle("on", a.getAttribute("data-tab") === tab);
      if (a.getAttribute("data-tab") === tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    document.title = ($("#topTitle").textContent ? $("#topTitle").textContent + " · " : "") + "Xử lý tại nhà";

    view.classList.remove("page-enter"); void view.offsetWidth; view.classList.add("page-enter");
    showAlarmBar();
    var y = scrollMem[h] || 0;
    window.scrollTo(0, y);
    curHash = h;
    onScroll();
  }

  function onScroll() {
    var y = window.scrollY;
    top.classList.toggle("scrolled", y > 4);
    var h1 = $("#pageH1") || view.querySelector("h1");
    if (h1 && top.classList.contains("inner")) {
      top.classList.toggle("show-title", h1.getBoundingClientRect().bottom < 60);
    }
  }

  /* ============================================================
     Sự kiện chung
     ============================================================ */
  document.addEventListener("click", function (e) {
    var t = e.target;
    var step = t.closest(".step");
    if (step && !t.closest(".ref")) { toggleStep(step); return; }
    var ref = t.closest("[data-skill]");
    if (ref) { e.preventDefault(); openSheet(ref.getAttribute("data-skill")); return; }
    if (t.closest("[data-close-sheet]")) {
      var a = t.closest("a[data-close-sheet]");
      closeSheet();
      if (!a) e.preventDefault();
      return;
    }
    if (t.closest("[data-reset]")) {
      var root = t.closest("[data-since]");
      var id = root.getAttribute("data-since");
      store.del(checkKey(id));
      var container = root.parentNode;
      container.querySelectorAll('.step[data-owner="' + id + '"]').forEach(function (s) {
        s.classList.remove("done"); s.setAttribute("aria-checked", "false");
      });
      container.querySelectorAll(".k-steps").forEach(function (b) { refreshProgress(b, id); });
      toast("Đã xoá các dấu đã làm");
      return;
    }
    var jump = t.closest("[data-jump]");
    if (jump) {
      e.preventDefault();
      var el = document.getElementById(jump.getAttribute("data-jump"));
      if (el) { el.open = true; el.scrollIntoView({ behavior: "smooth", block: "start" }); }
      return;
    }
    if (t.closest("[data-clear]")) { lastQuery = ""; }
    if (t.closest("[data-install-hide]")) { store.set("xltn-install-hide", true); var c = $("#installSlot"); if (c) c.remove(); return; }
    if (t.closest("[data-install]") && deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.finally(function () { deferredPrompt = null; var c = $("#installSlot"); if (c) c.remove(); });
      return;
    }
    if (t.closest("[data-alarm-off]")) { store.del("xltn-temp-end"); stopAlarm(); clearInterval(tempTick); drawTemp(); return; }
    if (t.closest("a[href^='#/']")) depth++;
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSheet();
    if ((e.key === " " || e.key === "Enter") && e.target.classList && e.target.classList.contains("step")) {
      e.preventDefault(); toggleStep(e.target);
    }
  });
  $("#back").addEventListener("click", function () {
    if (depth > 0) { depth--; history.back(); }
    else location.hash = "#/";
  });
  window.addEventListener("hashchange", route);
  window.addEventListener("scroll", onScroll, { passive: true });

  // đổi sáng tối
  $("#themeBtn").addEventListener("click", function () {
    var root = document.documentElement;
    var cur = root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    var next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("xltn-theme", next); } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", next === "dark" ? "#11161D" : "#F7F4EE");
  });

  var toastT = 0;
  function toast(msg) {
    var el = $("#toast");
    el.textContent = msg; el.hidden = false;
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.hidden = true; }, 1800);
  }

  // vuốt xuống để đóng bảng trượt
  (function () {
    var y0 = null, panel = $(".sheet");
    panel.addEventListener("touchstart", function (e) {
      if ($("#sheetBody").scrollTop > 0) { y0 = null; return; }
      y0 = e.touches[0].clientY;
    }, { passive: true });
    panel.addEventListener("touchmove", function (e) {
      if (y0 == null) return;
      var dy = e.touches[0].clientY - y0;
      if (dy > 0) panel.style.transform = "translateY(" + dy + "px)";
    }, { passive: true });
    panel.addEventListener("touchend", function (e) {
      if (y0 == null) return;
      var dy = e.changedTouches[0].clientY - y0;
      panel.style.transform = "";
      y0 = null;
      if (dy > 90) closeSheet();
    });
  })();

  /* ============================================================
     Khởi động
     ============================================================ */
  buildIndex();
  route();
  checkTemp();
  document.addEventListener("visibilitychange", function () { if (!document.hidden) checkTemp(); });

  if ("serviceWorker" in navigator && location.protocol !== "file:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").then(function (reg) {
        reg.addEventListener("updatefound", function () {
          var w = reg.installing;
          if (!w) return;
          w.addEventListener("statechange", function () {
            if (w.state === "installed" && navigator.serviceWorker.controller) {
              toast("Đã có nội dung mới, mở lại app để cập nhật");
            }
          });
        });
      }).catch(function () {});
    });
  }
})();
