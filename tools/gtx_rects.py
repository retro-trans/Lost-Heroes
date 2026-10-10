"""List the sprite rectangles (GFUV) the game samples from a texture page.

A .gtx next to a .tpc holds one GFUV block per page:
    "GFUV", u32 size, "3.00", u32 count, 32-byte page name, u32, count x (u16 x, y, w, h)
Every copy of the .gtx is searched (top level and inside .cmp packs); pass a
path substring to pick one, e.g. "Adv/eff/999".

Usage:
    python tools/gtx_rects.py <ALLRES.PCK> <path substring> [page name substring]
"""
import struct
import sys

import pck_extract
import walk_assets


def blocks(blob):
    pos = 0
    while True:
        i = blob.find(b"GFUV", pos)
        if i < 0:
            return
        n = struct.unpack_from("<I", blob, i + 12)[0]
        name = blob[i + 16:i + 48].split(b"\0")[0].decode("ascii", "replace")
        rects = [struct.unpack_from("<4H", blob, i + 52 + 8 * k) for k in range(n)]
        yield name, rects
        pos = i + 4


def find(allres, path_sub, page_sub=""):
    f = open(allres, "rb")
    out = []
    for name, off, size in pck_extract.read_table(f):
        if not name.startswith("Graph/"):
            continue
        if path_sub not in name and not name.endswith(".cmp"):
            continue
        f.seek(off)
        for vp, blob in walk_assets.walk(name, f.read(size)):
            if vp.endswith(".gtx") and path_sub in vp:
                for page, rects in blocks(blob):
                    if page_sub in page:
                        out.append((vp, page, rects))
    return out


def main():
    allres, path_sub = sys.argv[1], sys.argv[2]
    page_sub = sys.argv[3] if len(sys.argv) > 3 else ""
    seen = set()
    for vp, page, rects in find(allres, path_sub, page_sub):
        key = (page, tuple(rects))
        if key in seen:
            continue
        seen.add(key)
        print(f"{vp} :: {page} ({len(rects)} rects)")
        for k, r in enumerate(rects):
            print(f"  {k:3d} x={r[0]} y={r[1]} w={r[2]} h={r[3]}")


if __name__ == "__main__":
    main()
