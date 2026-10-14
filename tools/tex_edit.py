"""Relabel UI textures: replace Japanese labels baked into GFXT pages with English.

A spec (work/ui/tex/<name>.json) names one texture page and the label boxes on it:
    {"tpc": "Graph/Base/UI/Base.tpc", "page": "UI_psp_EQUIP_status_4444.tga",
     "boxes": [{"x": 26, "y": 7, "w": 22, "h": 10, "text": "ATK"}, ...]}
Spec-level "defaults" (merged into every box) and "clear" ([[x,y,w,h], ...]
wiped before drawing). Optional per box: "color" [r,g,b] (default: brightest colour found in the box),
"align" (left/center/right, default left), "stroke" [r,g,b] + "stroke_width" n (outlined text), "bg" [r,g,b] (opaque fill instead of transparent; for opaque pages), "size" (px, default: largest that fits),
"bold" (true/false), "weight" (extra stroke in px, default 0.4), "glow" [r,g,b] +
"glow_radius" n (soft halo), "condense" (narrowest horizontal squeeze, default 0.75), "overlay": true (draw over the
existing pixels instead of clearing the box). "{version}" in a text is the VERSION file. Spec-level "gtx" + "composites" build labels the game assembles from several
sprites (see draw_composites). Spec-level "grow": [w, h] enlarges the page (more room for moved pieces; the GE texture
follows the header size). "exact": true limits the spec to the copy whose
path equals "tpc" (for same-named textures with different content).

Each box is cleared to transparent and the English is drawn with GenEi LateGo,
shrunk (and horizontally condensed if needed) to fit. The page is re-encoded in
its own pixel format (paletted pages map to the nearest palette entry) and
swizzled again. apply_en.py injects every copy of the texture via `changes()`.

Usage:
    python tools/tex_edit.py roundtrip <ALLRES.PCK> <tpc path>       (encoder self-test)
    python tools/tex_edit.py preview <ALLRES.PCK> <spec.json> <out.png>
"""
import glob
import json
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

import pck_extract
import tex_render
import walk_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "incoming/genei-latin/GenEiLatin-Separate_v2.1/GenEiLateGoP_v2.ttf")
SPEC_DIR = os.path.join(ROOT, "work/ui/tex")


def swizzle(lin, width_bytes, height):
    out = bytearray(((height + 7) // 8) * 8 * width_bytes)
    i = 0
    for by in range((height + 7) // 8):
        for bx in range(width_bytes // 16):
            for row in range(8):
                y = by * 8 + row
                if y < height:
                    src = y * width_bytes + bx * 16
                    out[i:i + 16] = lin[src:src + 16]
                i += 16
    return bytes(out[:width_bytes * height])


def pack_color(rgba, kind):
    r, g, b, a = rgba
    if kind == "5551":
        return (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10 | (1 << 15 if a >= 128 else 0)
    if kind == "4444":
        return (r // 17) | (g // 17) << 4 | (b // 17) << 8 | (a // 17) << 12
    return r | g << 8 | b << 16 | a << 24


def page_layout(name, page):
    fmt, _u, w, h = struct.unpack_from("<HHHH", page, 0x10)
    kind = "8888" if "8888" in name else "4444" if "4444" in name else "5551"
    pos, pal = 0x50, []
    if fmt in (7, 9, 10):
        n = 256 if fmt == 10 else 16
        esz = 4 if kind == "8888" else 2
        pal = [tex_render.color(int.from_bytes(page[pos + i * esz:pos + (i + 1) * esz], "little"), kind)
               for i in range(n)]
        pos += n * esz
    return fmt, w, h, kind, pos, pal


def encode_page(name, page, img):
    """Return a new page blob with img (RGBA, same size) encoded into it."""
    fmt, w, h, kind, pos, pal = page_layout(name, page)
    px = img.load()
    bpp = tex_render.BPP[fmt]
    wb = w * bpp // 8
    lin = bytearray(wb * h)
    cache = {}

    def nearest(c):
        if c not in cache:
            cache[c] = min(range(len(pal)), key=lambda i: sum((a - b) ** 2 for a, b in zip(c, pal[i])))
        return cache[c]

    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if fmt in (7, 9):
                v = nearest(c)
                lin[y * wb + x // 2] |= (v << 4) if x & 1 else v
            elif fmt == 10:
                lin[y * wb + x] = nearest(c)
            elif fmt == 4:
                struct.pack_into("<I", lin, y * wb + x * 4, pack_color(c, "8888"))
            else:
                struct.pack_into("<H", lin, y * wb + x * 2, pack_color(c, kind))
    out = bytearray(page)
    out[pos:pos + wb * h] = swizzle(bytes(lin), wb, h)
    return bytes(out)


def read_tpc(allres, tpc_path):
    """All copies of a .tpc in the archive: {vpath: blob}."""
    f = open(allres, "rb")
    found = {}
    base = tpc_path.rsplit("/", 1)[-1]
    for name, off, size in pck_extract.read_table(f):
        # top-level Graph/ files plus every pack: battles load their own copies
        # from Battle/Btl_*_pk.cmp (missed before 0.1.10)
        if not (name.startswith("Graph/") or name.endswith(".cmp")):
            continue
        if name.endswith(".tpc") and name.rsplit("/", 1)[-1] != base:
            continue
        f.seek(off)
        for vpath, blob in walk_assets.walk(name, f.read(size)):
            leaf = vpath.split("::")[-1].rsplit("/", 1)[-1]
            if leaf == base and blob[:4] == b"GFPT":
                found[vpath] = blob
    return found


def tpc_pages(blob):
    return list(walk_assets.nbf_entries(blob[0x80:]))


def grow_page(name, page, w, h):
    """A GFXT page re-dimensioned to w x h (same format/palette, pixels cleared)."""
    fmt, _w, _h, kind, pos, _pal = page_layout(name, page)
    bpp = tex_render.BPP[fmt]
    out = bytearray(page[:pos]) + bytes(w * h * bpp // 8)
    struct.pack_into("<I", out, 4, len(out))
    struct.pack_into("<HH", out, 0x14, w, h)
    return bytes(out)


def rebuild_tpc(blob, page_name, new_page):
    """Rebuild a .tpc with one page replaced by a page of a different size."""
    import font4x
    pages = [(n + "", (new_page if n == page_name else p)) for n, p in font4x.read_pages(blob)]
    return font4x.write_tpc(blob, pages)


def replace_page(blob, page_name, new_page):
    """Rebuild a .tpc with one page replaced (same size, so offsets are unchanged)."""
    out = bytearray(blob)
    data = blob[0x80:]
    for name, page in walk_assets.nbf_entries(data):
        if name == page_name:
            i = data.find(page)
            if len(new_page) != len(page):
                return rebuild_tpc(blob, page_name, new_page)
            out[0x80 + i:0x80 + i + len(page)] = new_page
            return bytes(out)
    raise KeyError(page_name)


def fit_font(text, w, h, size=None, bold=False):
    if size:
        font = ImageFont.truetype(FONT, size)
        l, t, r, b = font.getbbox(text)
        return font, min(1.0, w / max(1, r - l + (2 if bold else 0)))
    sz = h + 2
    while sz >= 5:
        font = ImageFont.truetype(FONT, sz)
        l, t, r, b = font.getbbox(text)
        if b - t <= h and r - l <= w:
            return font, 1.0
        if b - t <= h and size is None and (r - l) * 0.75 <= w:
            return font, w / (r - l)          # condense horizontally (>= 0.75)
        sz -= 1
    font = ImageFont.truetype(FONT, 5)
    l, t, r, b = font.getbbox(text)
    return font, min(1.0, w / max(1, r - l))


SS = 4                 # supersampling factor for weighted text
WEIGHT = 0.4           # default extra stroke (1x px) so labels match the original pixel font's 2 px strokes


def render_weighted(text, w, h, size, weight, color, condense=0.75):
    """Text drawn at SS x with a same-colour stroke of weight*SS, then downsampled:
    a heavier face than GenEi LateGo's single weight. Shrinks to fit (box h), and
    returns (canvas, condense factor) like fit_font."""
    sw = int(round(weight * SS))

    def measure(sz):
        font = ImageFont.truetype(FONT, sz * SS)
        l, t, r, b = font.getbbox(text, stroke_width=sw)
        return font, (l, t, r, b), (r - l) / SS, (b - t) / SS

    sx, sz = 1.0, size
    if size:
        font, bb, tw, th = measure(size)
        sx = min(1.0, w / max(1, tw + 1))
    else:
        sz = h + 3
        while True:
            font, bb, tw, th = measure(sz)
            if th <= h + 0.5 and (tw <= w or (tw * condense <= w and sz <= h)) or sz <= 5:
                sx = min(1.0, w / max(1, tw + 1))
                break
            sz -= 1
    l, t, r, b = bb
    canvas = Image.new("RGBA", (r - l + 2 * SS, b - t + 2 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).text((SS - l, SS - t), text, font=font, fill=tuple(color) + (255,),
                                stroke_width=sw, stroke_fill=tuple(color) + (255,))
    out_w = max(1, round(canvas.width / SS * sx))
    out_h = max(1, round(canvas.height / SS))
    small = canvas.resize((out_w, out_h), Image.LANCZOS)
    bb = small.getbbox()          # trim side padding so split words (Data|base) join up
    out = small.crop((bb[0], 0, bb[2], small.height)) if bb else small
    out.info.update(size=sz if not size else size, sx=sx, lead=(bb[0] if bb else 0))
    return out


def add_glow(canvas, color, radius):
    """Soft coloured halo behind the text (title-card style)."""
    from PIL import ImageFilter
    pad = radius * 2
    big = Image.new("RGBA", (canvas.width + 2 * pad, canvas.height + 2 * pad), (0, 0, 0, 0))
    big.alpha_composite(canvas, (pad, pad))
    alpha = big.getchannel("A").filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    halo = Image.new("RGBA", big.size, tuple(color) + (0,))
    halo.putalpha(alpha)
    halo.alpha_composite(big)
    return halo


def build_version():
    """The build version shown on the title screen (VERSION at the project root)."""
    p = os.path.join(ROOT, "VERSION")
    return open(p, encoding="utf-8").read().strip() if os.path.exists(p) else "dev"


def draw_box(img, box):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    region = img.crop((x, y, x + w, y + h))
    color = box.get("color")
    if not color:
        bright = max(region.getdata(), key=lambda c: (c[3] > 128) * (c[0] + c[1] + c[2]))
        color = bright[:3] if bright[3] > 0 else (255, 255, 255)
    bg = box.get("bg")
    if not box.get("overlay"):             # overlay: draw over the existing pixels (opaque art)
        img.paste(tuple(bg) + (255,) if bg else (0, 0, 0, 0), (x, y, x + w, y + h))
    text = box["text"].replace("{version}", build_version())
    if not text:
        return
    if not box.get("stroke_width"):
        weight = box.get("weight", 0.8 if box.get("bold") else WEIGHT)
        m = 2 * box.get("glow_radius", 2) if box.get("glow") else 0      # room for the halo
        canvas = render_weighted(text, w - 2 * m, h - 2 * m, box.get("size"), weight, color,
                                 box.get("condense", 0.75))
        if box.get("glow"):
            canvas = add_glow(canvas, box["glow"], box.get("glow_radius", 2))
        align = box.get("align", "left")
        dx = x if align == "left" else x + w - canvas.width if align == "right" else x + (w - canvas.width) // 2
        dy = y + (h - canvas.height + 1) // 2
        # keep the glyphs inside the box (the game samples exactly this rectangle)
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.alpha_composite(canvas, (max(0, dx), max(0, dy)))
        img.alpha_composite(layer.crop((x, y, x + w, y + h)), (x, y))
        return
    font, sx = fit_font(text, w, h, box.get("size"), box.get("bold", False))
    l, t, r, b = font.getbbox(text)
    tw, th = r - l, b - t
    canvas = Image.new("RGBA", (tw + 2, th + 2), (0, 0, 0, 0))
    sw = box.get("stroke_width", 0)
    if sw:   # coloured outline around the fill (logo style)
        canvas = Image.new("RGBA", (tw + 2 + 2 * sw, th + 2 + 2 * sw), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).text((1 + sw - l, 1 + sw - t), text, font=font, fill=tuple(color) + (255,),
                                    stroke_width=sw, stroke_fill=tuple(box["stroke"]) + (255,))
    else:
        ImageDraw.Draw(canvas).text((1 - l, 1 - t), text, font=font, fill=tuple(color) + (255,),
                                    stroke_width=1 if box.get("bold") else 0, stroke_fill=tuple(color) + (255,))
    if sx < 1.0:
        canvas = canvas.resize((max(1, int(canvas.width * sx)), canvas.height), Image.LANCZOS)
    align = box.get("align", "left")
    dx = x if align == "left" else x + w - canvas.width if align == "right" else x + (w - canvas.width) // 2
    dy = y + (h - canvas.height) // 2
    img.alpha_composite(canvas, (max(0, dx), max(0, dy)))


def read_files(allres, path):
    """All copies of a Graph file by leaf name (top level and inside packs): {vpath: blob}."""
    f = open(allres, "rb")
    found = {}
    base = path.rsplit("/", 1)[-1]
    for name, off, size in pck_extract.read_table(f):
        if not name.endswith(".cmp") and not (name.startswith("Graph/") and name.rsplit("/", 1)[-1] == base):
            continue
        f.seek(off)
        for vpath, blob in walk_assets.walk(name, f.read(size)):
            if vpath.split("::")[-1].rsplit("/", 1)[-1] == base:
                found[vpath] = blob
    return found


def gtx_table(gtx, page):
    """(offset of the GFUV rect array, [(x, y, w, h)]) for a page in a .gtx, or None."""
    i = gtx.find(page.rsplit(".", 1)[0].encode("ascii") + b"\0")
    if i < 16 or gtx[i - 16:i - 12] != b"GFUV":
        return None
    j = i - 16
    n = struct.unpack_from("<I", gtx, j + 12)[0]
    return j + 52, [struct.unpack_from("<4H", gtx, j + 52 + 8 * k) for k in range(n)]


def free_spot(free, w, h):
    H, W = free.shape
    for y in range(H - h + 1):
        for x in range(W - w + 1):
            if free[y:y + h, x:x + w].all():
                return x, y
    raise ValueError(f"no free {w}x{h} area on the page")


def layout_words(text, x0, x1, line_h, style, color, avoid, fixed=None):
    """Place the words of a composite part: size from the whole phrase, natural word
    positions, then each word is nudged (first word right only, later words -2..+3 px, carried on)
    until no seam column in `avoid` cuts a glyph. `fixed` forces one shift for all."""
    import numpy as np
    weight, condense = style.get("weight", WEIGHT), style.get("condense", 0.75)
    whole = render_weighted(text, x1 - x0, line_h, style.get("size"), weight, color, condense)
    sz, sx = whole.info["size"], whole.info["sx"]
    font = ImageFont.truetype(FONT, sz * SS)
    out, carry, pos = [], fixed or 0, 0
    words = text.split(" ")
    for i, word in enumerate(words):
        prefix = " ".join(words[:i]) + (" " if i else "")
        nat = x0 + round(font.getlength(prefix) / SS * sx)
        img = render_weighted(word, 4096, line_h, sz, weight, color, condense)
        if sx < 1.0:
            img = img.resize((max(1, round(img.width * sx)), img.height), Image.LANCZOS)
        ink = np.array(img)[:, :, 3].max(axis=0)
        def hits(sft):
            return sum(int(ink[c - nat - sft]) for c in avoid if 0 <= c - nat - sft < len(ink))
        if fixed is None:
            lo = carry if i == 0 else carry - 2       # later words may also tuck in a little
            carry = min(range(lo, carry + 4), key=lambda sft: (hits(sft), abs(sft - carry), sft))
        out.append((img, nat + carry))
    return out


def draw_composites(img, original, spec, rects):
    """Multi-sprite labels. The game builds some menu rows from several sprites drawn
    side by side (e.g. Camp "Skill"+"Use"). A composite renders the whole phrase once
    (parts: [text, x0, x1] in row coordinates), cuts it into the pieces' rectangles
    (sprite index, dx, dy = the piece's offset in the row) and writes each slice back.
    A piece with "move": true gets a free transparent spot on the page (its pixels are
    shared with other sprites) and its GFUV rect is repointed there. Free spots are
    judged on the original page, so every copy gets the same layout.
    Returns {sprite: new rect} for moved pieces."""
    import numpy as np
    alpha = np.array(original)[:, :, 3]
    occ = np.zeros(alpha.shape, dtype=bool)
    for x, y, w, h in rects:
        occ[y:y + h, x:x + w] = True
    free = (alpha == 0) & ~occ
    moved = {}
    defaults = spec.get("defaults", {})
    for comp in spec.get("composites", []):
        style = dict(defaults, **comp.get("style", {}))
        pieces = comp["pieces"]
        cw = max(p["dx"] + rects[p["sprite"]][2] for p in pieces)
        ch = max(p.get("dy", 0) + rects[p["sprite"]][3] for p in pieces)
        line_h = comp.get("line_h") or min(rects[p["sprite"]][3] for p in pieces)
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        color = style.get("color", [255, 255, 255])
        # columns that must stay empty: screen gaps between pieces, plus "avoid"
        # (e.g. a page column another sprite sees as a seam)
        avoid = set(comp.get("avoid", []))
        order = sorted(pieces, key=lambda p: p["dx"])
        for a, b in zip(order, order[1:]):
            avoid.update(range(a["dx"] + rects[a["sprite"]][2], b["dx"]))
        for part in comp["parts"]:
            text, x0, x1 = part[:3]
            for word, wx in layout_words(text, x0, x1, line_h, style, color, avoid,
                                         part[3] if len(part) > 3 else None):
                wy = line_h - word.height if style.get("valign") == "bottom" else (line_h - word.height + 1) // 2
                canvas.alpha_composite(word, (wx, max(0, wy)))
        for p in pieces:
            x, y, w, h = rects[p["sprite"]]
            dx, dy = p["dx"], p.get("dy", 0)
            piece = canvas.crop((dx, dy, dx + w, dy + h))
            if p.get("move"):
                x, y = free_spot(free, w, h)
                free[y:y + h, x:x + w] = False
                moved[p["sprite"]] = (x, y, w, h)
            img.paste((0, 0, 0, 0), (x, y, x + w, y + h))
            img.alpha_composite(piece, (x, y))
    return moved


def apply_spec(spec, blob, rects=None):
    pages = dict(tpc_pages(blob))
    page = pages[spec["page"]]
    img = tex_render.page_image(spec["page"], page)
    if spec.get("grow"):
        # taller page = free room for moved composite pieces (rects keep their coordinates)
        gw, gh = spec["grow"]
        if img.size != (gw, gh):
            big = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
            big.paste(img, (0, 0))
            img = big
            page = grow_page(spec["page"], page, gw, gh)
    original = img.copy()
    bg = spec.get("defaults", {}).get("bg")
    for x, y, w, h in spec.get("clear", []):          # extra areas to wipe first
        img.paste(tuple(bg) + (255,) if bg else (0, 0, 0, 0), (x, y, x + w, y + h))
    for box in spec["boxes"]:
        draw_box(img, dict(spec.get("defaults", {}), **box))
    moved = draw_composites(img, original, spec, rects) if spec.get("composites") else {}
    blob = replace_page(blob, spec["page"], encode_page(spec["page"], page, img))
    return (blob, img, moved) if rects is not None else (blob, img)


def changes(allres):
    """{vpath: new tpc blob} for every spec in work/ui/tex (all copies of each texture)."""
    specs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(SPEC_DIR, "*.json")))]
    by_tpc = {}
    for s in specs:
        by_tpc.setdefault(s["tpc"], []).append(s)
    out, gtx_moves = {}, {}
    for tpc, group in by_tpc.items():
        for vpath, blob in read_tpc(allres, tpc).items():
            names = {n for n, _ in tpc_pages(blob)}
            leaf = vpath.split("::")[-1]
            # same file name, other content: skip; "exact" specs only touch their own path
            # (Graph/Adv/eff/5xx/ADV_EFF.tpc share page names but hold different pictures)
            hit = [s for s in group if s["page"] in names and (not s.get("exact") or leaf == s["tpc"])]
            for s in hit:
                if s.get("composites"):
                    blob, _, moved = apply_spec(s, blob, composite_rects(allres, s))
                    gtx_moves.setdefault(s["gtx"], {}).setdefault(s["page"], {}).update(moved)
                else:
                    blob, _ = apply_spec(s, blob)
            if hit:
                out[vpath] = blob
    # repoint moved sprites in every copy of their .gtx
    for gtx_path, by_page in gtx_moves.items():
        for vpath, gtx in read_files(allres, gtx_path).items():
            data = bytearray(gtx)
            for page, moved in by_page.items():
                t = gtx_table(gtx, page)
                if not t:
                    continue
                base, _ = t
                for k, rect in moved.items():
                    struct.pack_into("<4H", data, base + 8 * k, *rect)
            if bytes(data) != gtx:
                out[vpath] = bytes(data)
    return out


_RECTS = {}


def composite_rects(allres, spec):
    """Original GFUV rects of the spec's page (from the first .gtx copy that has it)."""
    key = (spec["gtx"], spec["page"])
    if key not in _RECTS:
        for gtx in read_files(allres, spec["gtx"]).values():
            t = gtx_table(gtx, spec["page"])
            if t:
                _RECTS[key] = t[1]
                break
    return _RECTS[key]


def main():
    cmd = sys.argv[1]
    if cmd == "roundtrip":
        allres, tpc = sys.argv[2], sys.argv[3]
        for vpath, blob in read_tpc(allres, tpc).items():
            for name, page in tpc_pages(blob):
                img = tex_render.page_image(name, page)
                if img is None:
                    continue
                same = encode_page(name, page, img) == page
                print(f"{vpath} {name}: {'identical' if same else 'DIFFERS'}")
    elif cmd == "preview":
        allres, spec_path, out = sys.argv[2], sys.argv[3], sys.argv[4]
        spec = json.load(open(spec_path, encoding="utf-8"))
        blob = next(b for v, b in read_tpc(allres, spec["tpc"]).items()
                    if spec["page"] in {n for n, _ in tpc_pages(b)}
                    and (not spec.get("exact") or v.split("::")[-1] == spec["tpc"]))
        if spec.get("composites"):
            _, img, moved = apply_spec(spec, blob, composite_rects(allres, spec))
            print("moved sprites:", moved)
        else:
            _, img = apply_spec(spec, blob)
        bg = Image.new("RGBA", img.size, (40, 40, 60, 255))
        bg.alpha_composite(img)
        bg = bg.resize((img.width * 4, img.height * 4), Image.NEAREST)
        bg.convert("RGB").save(out)


if __name__ == "__main__":
    main()
