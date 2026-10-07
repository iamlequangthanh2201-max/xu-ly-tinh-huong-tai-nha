#!/usr/bin/env python3
"""Dựng app PWA "Sunny time" (xử lý tình huống tại nhà) từ noi-dung.md.

Sửa nội dung ở noi-dung.md rồi chạy:  python3 build.py
Kết quả nằm trong docs/ (đưa lên GitHub Pages hoặc host tĩnh bất kỳ).
"""
import hashlib, json, pathlib, re

HERE = pathlib.Path(__file__).parent
OUT = HERE / "docs"

TITLE = "Sunny time"
SHORT = "Sunny time"
THEME = "#1F3A5F"
BG = "#F7F4EE"

# ---------------------------------------------------------------- nhóm
CATEGORIES = [
    dict(id="an-uong", icon="🍼", title="Ăn uống, tiêu hóa",
         items=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]),
    dict(id="da", icon="🧴", title="Da, rốn, cơ thể",
         items=["A9", "A10", "A11", "A12", "A13", "A14", "A15", "A23"]),
    dict(id="ho-hap", icon="🫁", title="Hô hấp",
         items=["A16", "A3"]),
    dict(id="sot", icon="🌡️", title="Sốt, thân nhiệt",
         items=["A17", "A18"]),
    dict(id="ngu", icon="😴", title="Ngủ, khóc",
         items=["A6", "A19", "A20"]),
    dict(id="mat-mieng", icon="👁️", title="Mắt, miệng",
         items=["A21", "A22"]),
    dict(id="tai-nan", icon="⚠️", title="Tai nạn",
         items=["A24", "A25", "A3"]),
    dict(id="me", icon="👩", title="Mẹ sau sinh",
         items=["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]),
]

# Từ người dùng hay gõ khi tìm, ngoài tên tình huống
KEYWORDS = {
    "A1": "ọc sữa, ói, nôn, trào sữa, trớ",
    "A2": "nôn, ói, ói vọt, nôn mật, dịch xanh, hẹp môn vị",
    "A3": "sặc, sặc sữa, ho khi bú, tím tái, nghẹn",
    "A4": "nấc, nấc cụt",
    "A5": "đầy hơi, xì hơi, chướng bụng, đau bụng, ợ",
    "A6": "khóc, khóc đêm, quấy, dạ đề, colic, không nín",
    "A7": "táo bón, không đi ị, phân cứng, rặn",
    "A8": "tiêu chảy, đi ngoài nhiều, phân lỏng, ị nhiều, mất nước",
    "A9": "vàng da, da vàng, mắt vàng, phân trắng",
    "A10": "hăm, hăm tã, đỏ mông, nấm",
    "A11": "mụn, mụn sữa, ban đỏ, nổi mẩn",
    "A12": "chàm, chàm sữa, viêm da, ngứa, khô da",
    "A13": "cứt trâu, vảy đầu, gàu",
    "A14": "rôm, rôm sảy, nóng",
    "A15": "rốn, cuống rốn, rụng rốn, rốn chảy máu, rốn có mủ",
    "A16": "nghẹt mũi, sổ mũi, khò khè, hút mũi, ngạt mũi, ho, hắt hơi",
    "A17": "sốt, nóng, nhiệt độ, hạ sốt, paracetamol",
    "A18": "lạnh, hạ thân nhiệt, người lạnh, nhiệt độ thấp",
    "A19": "ngủ ngày, thức đêm, lệch giờ, không ngủ đêm",
    "A20": "giật mình, vặn mình, ngủ không yên, quấn, ngủ an toàn",
    "A21": "ghèn, gỉ mắt, chảy nước mắt, tắc lệ",
    "A22": "tưa, tưa lưỡi, nấm miệng, lưỡi trắng",
    "A23": "sưng vú, vú bé, tiết sữa",
    "A24": "ngã, té, rơi, đập đầu, u đầu",
    "A25": "bỏng, phỏng, nước nóng",
    "B1": "sản dịch, ra máu, băng huyết",
    "B2": "cương sữa, căng sữa, vú căng",
    "B3": "tắc sữa, tắc tia sữa, cục cứng, viêm vú",
    "B4": "nứt đầu ti, đau đầu ti, đau ti, khớp ngậm",
    "B5": "ít sữa, mất sữa, không đủ sữa, gọi sữa",
    "B6": "vết khâu, tầng sinh môn, cắt tầng sinh môn",
    "B7": "vết mổ, mổ đẻ, sinh mổ",
    "B8": "trầm cảm, buồn, baby blues, khóc, stress",
    "B9": "táo bón, trĩ",
    "K1": "ợ hơi, vỗ ợ",
    "K2": "nước muối, hút mũi",
    "K3": "đo nhiệt độ, nhiệt kế, cặp nhiệt",
    "K4": "nhịp thở, thở nhanh, đếm thở",
    "K5": "mất nước, tã ướt, thóp lõm",
    "K6": "hóc, dị vật, sơ cứu, nghẹt thở, vỗ lưng ấn ngực",
    "K7": "quấn, quấn chũn, quấn khăn",
}

# Tên ngắn cho các chip "xem kỹ năng"
SKILL_SHORT = {
    "K1": "Cách cho ợ hơi",
    "K2": "Cách hút mũi",
    "K3": "Cách đo nhiệt độ",
    "K4": "Cách đếm nhịp thở",
    "K5": "Kiểm tra mất nước",
    "K6": "Sơ cứu hóc dị vật",
    "K7": "Cách quấn bé",
}

# ---------------------------------------------------------------- đọc md
RE_PART = re.compile(r"^## PHẦN ([0ABCD])")
RE_ITEM = re.compile(r"^### ([ABK]\d+)\. (.+)$")
RE_GROUP = re.compile(r"^### (.+)$")
RE_LABEL = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")
RE_OL = re.compile(r"^( *)(\d+)\. (.+)$")
RE_UL = re.compile(r"^( *)- (.+)$")
SEV = {"🟢": "green", "🟡": "yellow", "🔴": "red"}


def section_kind(label, ordered):
    if label is None:
        return "steps" if ordered else "info"
    l = label.lower()
    if l.startswith("đây là gì"):
        return "about"
    if l.startswith("không nên"):
        return "avoid"
    if l.startswith(("đi khám", "đi cấp cứu", "🔴", "cấp cứu")):
        return "doctor"
    if l.startswith("phòng ngừa") or l.startswith("an toàn"):
        return "prevent"
    return "steps" if ordered else "info"


def parse(md):
    skills, situations, emergency, glossary = [], [], [], []
    part = None
    cur = None      # mục hiện tại (kỹ năng / tình huống / nhóm cấp cứu)
    sec = None      # phần đang đọc trong mục

    def new_sec(label, text=""):
        nonlocal sec
        sec = dict(label=label, text=text, items=[], ordered=False)
        cur["sections"].append(sec)
        return sec

    for raw in md.splitlines():
        line = raw.rstrip()
        m = RE_PART.match(line)
        if m:
            part, cur, sec = m.group(1), None, None
            continue
        if part is None:
            continue
        if not line.strip() or line.strip() == "---":
            continue
        if part == "D":
            m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line)
            if m:
                names = [n.strip() for n in m.group(1).split("/")]
                glossary.append(dict(term=names[0], aliases=names, text=m.group(2).strip()))
            continue

        m = RE_ITEM.match(line)
        if m:
            iid, rest = m.group(1), m.group(2)
            sev = [SEV[e] for e in re.findall("[🟢🟡🔴]", rest)]
            title = re.sub(r"\s*[🟢🟡🔴/]+\s*$", "", rest).strip()
            cur = dict(id=iid, title=title, severity=sev, sections=[])
            sec = None
            (skills if iid.startswith("K") else situations).append(cur)
            continue
        m = RE_GROUP.match(line)
        if m and part == "C":
            cur = dict(title=m.group(1).strip(), sections=[])
            emergency.append(cur)
            sec = None
            continue
        if cur is None:
            continue

        m = RE_LABEL.match(line)
        if m:
            new_sec(m.group(1).strip(), m.group(2).strip())
            continue
        if line.startswith(">"):
            cur.setdefault("notes", []).append(line.lstrip("> ").strip())
            continue

        m = RE_OL.match(line) or RE_UL.match(line)
        if m:
            ordered = m.re is RE_OL
            indent = len(m.group(1))
            text = m.group(3) if ordered else m.group(2)
            if sec is None:
                new_sec(None)
            if indent == 0:
                sec["items"].append(dict(text=text, children=[]))
                if ordered:
                    sec["ordered"] = True
            elif sec["items"]:
                # danh sách con nằm trong bước gần nhất
                sec["items"][-1]["children"].append(text)
            continue

        # đoạn văn thường
        if sec is None:
            new_sec(None)
        sec["text"] = (sec["text"] + " " + line.strip()).strip()

    for item in skills + situations + emergency:
        for s in item["sections"]:
            s["kind"] = section_kind(s["label"], s.pop("ordered"))
    return skills, situations, emergency, glossary


def build():
    md = (HERE / "noi-dung.md").read_text(encoding="utf-8")
    skills, situations, emergency, glossary = parse(md)

    ids = {s["id"] for s in situations}
    for c in CATEGORIES:
        missing = [i for i in c["items"] if i not in ids]
        assert not missing, "Nhóm %s có mã không tồn tại: %s" % (c["id"], missing)
    grouped = {i for c in CATEGORIES for i in c["items"]}
    lost = sorted(ids - grouped)
    assert not lost, "Tình huống chưa được xếp nhóm: %s" % lost

    for item in skills + situations:
        item["keywords"] = KEYWORDS.get(item["id"], "")
        item["audience"] = "me" if item["id"].startswith("B") else "be"
    for k in skills:
        k["short"] = SKILL_SHORT.get(k["id"], k["title"])

    data = dict(skills=skills, situations=situations, emergency=emergency,
                glossary=glossary, categories=CATEGORIES)
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    css = (HERE / "src" / "styles.css").read_text(encoding="utf-8")
    js = (HERE / "src" / "app.js").read_text(encoding="utf-8")
    shell = (HERE / "src" / "index.html").read_text(encoding="utf-8")

    page = (shell
            .replace("/*__CSS__*/", css)
            .replace("/*__JS__*/", js)
            .replace("__DATA__", data_json.replace("</", "<\\/"))
            .replace("__TITLE__", TITLE)
            .replace("__THEME__", THEME))

    OUT.mkdir(exist_ok=True)
    make_icons()
    # phiên bản tính cả icon, để đổi icon thì máy đã cài cũng nhận bản mới
    h = hashlib.sha1(page.encode("utf-8"))
    for f in sorted((OUT / "icons").glob("*.png")):
        h.update(f.read_bytes())
    version = h.hexdigest()[:10]
    (OUT / "index.html").write_text(page.replace("__VERSION__", version), encoding="utf-8")

    sw = (HERE / "src" / "sw.js").read_text(encoding="utf-8").replace("__VERSION__", version)
    (OUT / "sw.js").write_text(sw, encoding="utf-8")

    manifest = dict(
        name=TITLE, short_name=SHORT, lang="vi",
        description="Các bước xử lý tại nhà khi bé hoặc mẹ gặp vấn đề sau sinh.",
        start_url="./", scope="./", display="standalone",
        background_color=BG, theme_color=THEME,
        icons=[
            dict(src="icons/icon-192.png", sizes="192x192", type="image/png"),
            dict(src="icons/icon-512.png", sizes="512x512", type="image/png"),
            dict(src="icons/icon-maskable-512.png", sizes="512x512",
                 type="image/png", purpose="maskable"),
        ],
    )
    (OUT / "manifest.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    n_steps = sum(len(s["items"]) for it in situations for s in it["sections"]
                  if s["kind"] == "steps")
    print("Đã dựng docs/  |  %d tình huống, %d kỹ năng, %d bước, %d từ ngữ, phiên bản %s"
          % (len(situations), len(skills), n_steps, len(glossary), version))


# ---------------------------------------------------------------- icon
def sunflower(size, frame=True, rounded=True, pad=0.0):
    """Hoa hướng dương kiểu huy hiệu trung cổ: nền xanh lapis, viền vàng,
    cánh hoa viền nét đậm, nhụy nâu đan ô trám như tranh khắc gỗ."""
    import math
    from PIL import Image, ImageDraw
    k = 4
    S = size * k
    LAPIS, GOLD, GOLD_D, RED = "#1C2E6E", "#D4A72C", "#9C7416", "#A8322A"
    PETAL, PETAL_IN, INK, DISC = "#F4C430", "#DE9A1E", "#2A1606", "#5B3214"

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    if rounded:
        g.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=LAPIS)
    else:
        g.rectangle([0, 0, S, S], fill=LAPIS)

    # chấm sao nhỏ trên nền, như nền trang sách cổ
    if frame:
        step = S / 9.0
        lo, hi = S * 0.14, S * 0.86
        for i in range(10):
            for j in range(10):
                x, y = (i + 0.5) * step, (j + 0.5) * step
                if (i + j) % 2 or not (lo < x < hi and lo < y < hi):
                    continue
                r = S * 0.006
                g.ellipse([x - r, y - r, x + r, y + r], fill=GOLD_D)

    if frame:
        ins = S * 0.055
        g.rounded_rectangle([ins, ins, S - ins, S - ins], radius=int(S * 0.17),
                            outline=GOLD, width=max(2, int(S * 0.02)))
        ins2 = S * 0.088
        g.rounded_rectangle([ins2, ins2, S - ins2, S - ins2], radius=int(S * 0.14),
                            outline=RED, width=max(1, int(S * 0.007)))

    cx = cy = S / 2
    R = S * (0.5 - pad) * (0.78 if frame else 0.86)
    rd = R * 0.40
    lw = max(2, int(S * 0.009))

    def petal(angle, r0, r1, w, fill):
        pts_l, pts_r = [], []
        n = 18
        for i in range(n + 1):
            tt = i / float(n)
            rr = r0 + (r1 - r0) * tt
            hw = w * (math.sin(math.pi * min(tt * 1.1, 1.0)) ** 0.75) * (1 - tt * 0.15)
            pts_l.append((rr, -hw))
            pts_r.append((rr, hw))
        shape = pts_l + [(r1 + (r1 - r0) * 0.04, 0)] + pts_r[::-1]
        ca, sa = math.cos(angle), math.sin(angle)
        poly = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in shape]
        g.polygon(poly, fill=fill, outline=INK, width=lw)
        v0, v1 = r0 + (r1 - r0) * 0.12, r0 + (r1 - r0) * 0.72
        g.line([(cx + v0 * ca, cy + v0 * sa), (cx + v1 * ca, cy + v1 * sa)],
               fill=INK, width=max(1, lw // 2))

    N = 14
    for i in range(N):
        a = 2 * math.pi * i / N - math.pi / 2
        petal(a, rd * 0.8, R, R * 0.15, PETAL)
    for i in range(N):
        a = 2 * math.pi * (i + 0.5) / N - math.pi / 2
        petal(a, rd * 0.8, R * 0.80, R * 0.13, PETAL_IN)

    # nhụy: đĩa nâu, đan ô trám vàng, chấm vàng ở giữa mỗi ô
    g.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill=DISC, outline=INK, width=lw)
    lat = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    lg = ImageDraw.Draw(lat)
    sp = rd / 2.6
    lwl = max(1, int(S * 0.005))
    m = int(rd * 2 / sp) + 4
    for i in range(-m, m + 1):
        o = i * sp
        lg.line([(cx + o - rd * 2, cy - rd * 2), (cx + o + rd * 2, cy + rd * 2)], fill=GOLD_D, width=lwl)
        lg.line([(cx + o + rd * 2, cy - rd * 2), (cx + o - rd * 2, cy + rd * 2)], fill=GOLD_D, width=lwl)
    for i in range(-m, m + 1):
        for j in range(-m, m + 1):
            x = cx + (i + j) * sp / 2.0
            y = cy + (j - i) * sp / 2.0 + sp / 2.0
            r = sp * 0.13
            lg.ellipse([x - r, y - r, x + r, y + r], fill=GOLD)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([cx - rd * 0.86, cy - rd * 0.86, cx + rd * 0.86, cy + rd * 0.86], fill=255)
    img.paste(lat, (0, 0), Image.composite(lat, Image.new("RGBA", (S, S)), mask).split()[3])
    g = ImageDraw.Draw(img)
    g.ellipse([cx - rd * 0.86, cy - rd * 0.86, cx + rd * 0.86, cy + rd * 0.86], outline=INK, width=max(1, lw // 2))

    return img.resize((size, size), Image.LANCZOS)


def make_icons():
    d = OUT / "icons"
    d.mkdir(exist_ok=True)
    sunflower(192).save(d / "icon-192.png")
    sunflower(512).save(d / "icon-512.png")
    sunflower(512, frame=False, rounded=False, pad=0.12).save(d / "icon-maskable-512.png")
    sunflower(180, rounded=False).save(d / "apple-touch-icon.png")
    sunflower(64, frame=False).save(d / "favicon.png")
    sunflower(96, frame=False).save(d / "mark.png")


if __name__ == "__main__":
    build()
