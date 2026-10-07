#!/usr/bin/env python3
"""Dựng app PWA "Xử lý tại nhà" từ noi-dung.md.

Sửa nội dung ở noi-dung.md rồi chạy:  python3 build.py
Kết quả nằm trong docs/ (đưa lên GitHub Pages hoặc host tĩnh bất kỳ).
"""
import hashlib, json, pathlib, re

HERE = pathlib.Path(__file__).parent
OUT = HERE / "docs"

TITLE = "Xử lý tại nhà"
SHORT = "Xử lý tại nhà"
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

    version = hashlib.sha1(page.encode("utf-8")).hexdigest()[:10]
    OUT.mkdir(exist_ok=True)
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

    make_icons()
    n_steps = sum(len(s["items"]) for it in situations for s in it["sections"]
                  if s["kind"] == "steps")
    print("Đã dựng docs/  |  %d tình huống, %d kỹ năng, %d bước, %d từ ngữ, phiên bản %s"
          % (len(situations), len(skills), n_steps, len(glossary), version))


# ---------------------------------------------------------------- icon
def make_icons():
    from PIL import Image, ImageDraw
    d = OUT / "icons"
    d.mkdir(exist_ok=True)

    def draw(size, pad_ratio, rounded):
        scale = 4
        S = size * scale
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        g = ImageDraw.Draw(img)
        if rounded:
            g.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=THEME)
        else:
            g.rectangle([0, 0, S, S], fill=THEME)
        # chữ thập bo tròn màu kem, giữa có trái tim nhỏ màu san hô
        inner = S * (1 - 2 * pad_ratio)
        cx = cy = S / 2
        arm = inner * 0.30
        length = inner * 0.86
        r = arm * 0.32
        cream = BG
        g.rounded_rectangle([cx - arm / 2, cy - length / 2, cx + arm / 2, cy + length / 2],
                            radius=r, fill=cream)
        g.rounded_rectangle([cx - length / 2, cy - arm / 2, cx + length / 2, cy + arm / 2],
                            radius=r, fill=cream)
        h = arm * 0.62
        coral = "#E0674F"
        g.ellipse([cx - h * 0.5, cy - h * 0.42, cx, cy + h * 0.08], fill=coral)
        g.ellipse([cx, cy - h * 0.42, cx + h * 0.5, cy + h * 0.08], fill=coral)
        g.polygon([(cx - h * 0.47, cy - h * 0.08), (cx + h * 0.47, cy - h * 0.08),
                   (cx, cy + h * 0.46)], fill=coral)
        return img.resize((size, size), Image.LANCZOS)

    draw(192, 0.16, True).save(d / "icon-192.png")
    draw(512, 0.16, True).save(d / "icon-512.png")
    draw(512, 0.24, False).save(d / "icon-maskable-512.png")
    draw(180, 0.16, False).save(d / "apple-touch-icon.png")
    draw(64, 0.10, True).save(d / "favicon.png")


if __name__ == "__main__":
    build()
