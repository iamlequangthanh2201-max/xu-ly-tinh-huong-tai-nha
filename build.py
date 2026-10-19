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
         items=["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A27"]),
    dict(id="da", icon="🧴", title="Da, rốn, cơ thể",
         items=["A9", "A10", "A11", "A12", "A13", "A14", "A15", "A23"]),
    dict(id="ho-hap", icon="🫁", title="Hô hấp",
         items=["A16", "A3"]),
    dict(id="sot", icon="🌡️", title="Sốt, thân nhiệt",
         items=["A17", "A28", "A18"]),
    dict(id="ngu", icon="😴", title="Ngủ, khóc",
         items=["A6", "A26", "A19", "A20"]),
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
    "A27": "mọc răng, răng, nhú răng, lợi sưng, sưng lợi, chảy dãi, nước dãi, gặm, ngứa lợi",
    "A28": "co giật, giật, lên cơn, sốt cao co giật, động kinh, trợn mắt, sùi bọt mép, giật kinh",
    "A26": "khóc lặng, nín thở, khóc tím tái, ngất khi khóc, lên cơn khóc, ăn vạ",
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
    "K8": "rốn, vệ sinh rốn, lau rốn, chăm sóc rốn, cuống rốn, rụng rốn",
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
    "K8": "Cách vệ sinh rốn",
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


# ---------------------------------------------------------------- lịch trình
RE_STAGE = re.compile(r"^## (\w+) \| (.+?) \| (.+)$")
RE_SLOT = re.compile(r"^- (\d{2}:\d{2}) \| (\w+) \| (.+)$")
RE_WHO = re.compile(r"^(Mẹ|Bố|Bà|Ông bà|Cả nhà): (.+)$")
SLOT_TYPES = {"thuc", "bu", "binh", "dem", "an", "choi", "ngoai", "ngu", "tam", "vesinh", "hut"}
STAGE_KEYS = ["0a", "0b"] + [str(i) for i in range(1, 13)]
GLOBAL_SECTIONS = {"Nguyên tắc chung": "principles", "Cữ đêm là gì": "night",
                   "Cho bé bú bình sữa mẹ": "bottle", "Bảo quản sữa mẹ": "storage",
                   "Khi nào dùng sữa công thức": "formula"}
STAGE_SECTIONS = [("tóm tắt", "summary"), ("lịch của bé", "baby"), ("ban đêm", "night"),
                  ("mẹo ban đêm", "nightTips"), ("bú và hút sữa", "milk"), ("lưu ý", "notes")]


def parse_slot(line):
    s = RE_SLOT.match(line)
    if not s:
        return None
    assert s.group(2) in SLOT_TYPES, "Loại không có: " + line
    parts = []
    for part in s.group(3).split(" / "):
        w = RE_WHO.match(part.strip())
        parts.append(dict(who=w.group(1), text=w.group(2).strip()) if w else dict(who=None, text=part.strip()))
    return dict(t=s.group(1), k=s.group(2), text=s.group(3).strip(), parts=parts)


def parse_schedule(md):
    out = dict(stages=[])
    for v in GLOBAL_SECTIONS.values():
        out[v] = []
    cur, key = None, None
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip() == "---":
            continue
        if line.startswith("## ") and line[3:] in GLOBAL_SECTIONS:
            cur, key = out, GLOBAL_SECTIONS[line[3:]]
            continue
        m = RE_STAGE.match(line)
        if m:
            big, _, small = m.group(2).partition(" ")
            cur = dict(key=m.group(1), big=big, small=small, sub=m.group(3).strip(),
                       summary=[], baby=[], night=[], nightTips=[], milk=[], milkNotes=[], notes=[])
            out["stages"].append(cur)
            key = None
            continue
        if cur is None:
            continue
        if cur is not out and line.startswith("**") and line.endswith(":**"):
            label = line.strip("*").rstrip(":").lower()
            key = next((k for pre, k in STAGE_SECTIONS if label.startswith(pre)), None)
            assert key, "Không hiểu nhãn: " + line
            continue
        if key is None or not line.startswith("- "):
            continue
        if cur is out:
            out[key].append(line[2:].strip())
        elif key in ("baby", "night"):
            slot = parse_slot(line)
            assert slot, "Dòng lịch sai dạng: " + line
            cur[key].append(slot)
        elif key == "milk":
            slot = parse_slot(line)
            if slot:
                cur["milk"].append(slot)
            else:
                cur["milkNotes"].append(line[2:].strip())
        elif key == "summary":
            lab, _, val = line[2:].partition(":")
            cur["summary"].append(dict(label=lab.strip(), value=val.strip()))
        else:
            cur[key].append(line[2:].strip())
    keys = [x["key"] for x in out["stages"]]
    assert keys == STAGE_KEYS, "Lịch phải đủ các giai đoạn %s, đang có %s" % (STAGE_KEYS, keys)
    return out

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

    schedule = parse_schedule((HERE / "lich-trinh.md").read_text(encoding="utf-8"))
    data = dict(skills=skills, situations=situations, emergency=emergency,
                glossary=glossary, categories=CATEGORIES, schedule=schedule)
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
    print("Đã dựng docs/  |  %d tình huống, %d kỹ năng, %d bước, %d từ ngữ, %d giai đoạn lịch trình, phiên bản %s"
          % (len(situations), len(skills), n_steps, len(glossary), len(schedule["stages"]), version))


# ---------------------------------------------------------------- icon
# Ảnh gốc: icon hoa hướng dương nền xanh, đặt trên nền sáng. Build tự tìm khung icon,
# tách nền theo đúng đường bo góc kiểu iOS, rồi xuất các cỡ cần cho PWA.
ICON_SRC = HERE / "assets" / "app-icon-source.png"
SQUIRCLE_N = 5.5   # độ cong góc, khớp với góc bo của ảnh gốc


def icon_layers():
    """Trả về (icon bo góc nền trong suốt, icon vuông tràn viền) ở độ phân giải gốc."""
    from PIL import Image
    src = Image.open(ICON_SRC).convert("RGB")
    W, H = src.size
    px = src.load()

    def is_icon(c):
        return max(c) - min(c) > 100
    xs = [x for x in range(W) if any(is_icon(px[x, y]) for y in range(0, H, 4))]
    ys = [y for y in range(H) if any(is_icon(px[x, y]) for x in range(0, W, 4))]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    S = min(x1 - x0, y1 - y0) + 1
    box = src.crop((x0, y0, x0 + S, y0 + S))

    # mặt nạ squircle, khử răng cưa bằng cách vẽ ở độ phân giải gấp 4.
    # inset: thu mép vào vài px để bỏ viền sáng sót lại từ nền của ảnh gốc
    def squircle(inset):
        k = 4
        a = S * k / 2.0 - k * inset
        m = Image.new("L", (S * k, S * k), 0)
        mp = m.load()
        c = S * k / 2.0 - 0.5
        for yy in range(S * k):
            dy = abs(yy - c) / a
            if dy >= 1:
                continue
            half = a * (1 - dy ** SQUIRCLE_N) ** (1 / SQUIRCLE_N)
            for xx in range(max(0, int(c - half)), min(S * k, int(c + half) + 1)):
                mp[xx, yy] = 255
        return m.resize((S, S), Image.LANCZOS)
    mask = squircle(2.2)

    rounded = box.convert("RGBA")
    rounded.putalpha(mask)

    # màu nền theo từng hàng: lấy ở cạnh thẳng bên trái (giữa) và cạnh thẳng trên, dưới (giữa)
    bp = box.load()
    samples = {}
    for y in range(int(S * 0.3), int(S * 0.7)):
        samples[y] = bp[int(S * 0.03), y]
    for y in list(range(int(S * 0.02), int(S * 0.06))) + list(range(int(S * 0.94), int(S * 0.975))):
        samples[y] = bp[S // 2, y]
    keys = sorted(samples)

    def row_color(y):
        if y <= keys[0]:
            return samples[keys[0]]
        if y >= keys[-1]:
            return samples[keys[-1]]
        lo = max(k_ for k_ in keys if k_ <= y)
        hi = min(k_ for k_ in keys if k_ >= y)
        if lo == hi:
            return samples[lo]
        f = (y - lo) / float(hi - lo)
        return tuple(int(round(samples[lo][i] * (1 - f) + samples[hi][i] * f)) for i in range(3))

    bg = Image.new("RGB", (S, S))
    gp = bg.load()
    for y in range(S):
        col = row_color(y)
        for x in range(S):
            gp[x, y] = col
    full = bg.copy()
    # nối icon vào nền bằng mép mềm, để không lộ đường bo góc ở bản vuông
    from PIL import ImageFilter
    full.paste(box, (0, 0), squircle(22).filter(ImageFilter.GaussianBlur(S / 45.0)))
    return rounded, full, row_color, S


def make_icons():
    from PIL import Image
    d = OUT / "icons"
    d.mkdir(exist_ok=True)
    rounded, full, row_color, S = icon_layers()

    def save(img, size, name):
        img.resize((size, size), Image.LANCZOS).save(d / name)

    # "any": bo góc sẵn, nền trong suốt
    save(rounded, 512, "icon-512.png")
    save(rounded, 192, "icon-192.png")
    save(rounded, 96, "mark.png")
    save(rounded, 64, "favicon.png")
    # iPhone tự bo góc, nên dùng bản vuông tràn viền
    save(full.convert("RGB"), 180, "apple-touch-icon.png")
    # maskable cho Android: thu nhỏ vào vùng an toàn, phần viền nối tiếp màu nền
    scale = 0.84
    inner = int(S * scale)
    off = (S - inner) // 2
    canvas = Image.new("RGB", (S, S))
    cp = canvas.load()
    for y in range(S):
        col = row_color(int((y - off) / scale))
        for x in range(S):
            cp[x, y] = col
    canvas.paste(full.resize((inner, inner), Image.LANCZOS), (off, off))
    save(canvas, 512, "icon-maskable-512.png")
    # bản gốc đã tách nền, để dùng ở nơi khác
    rounded.save(d / "app-icon.png")


if __name__ == "__main__":
    build()
