"""Zoomed view of a texture PNG with a pixel grid and coordinates (for writing tex_edit specs).

Usage: python tools/tex_grid.py <in.png> <out.png> [zoom] [x0 y0 x1 y1]
"""
import sys
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
z = int(sys.argv[3]) if len(sys.argv) > 3 else 8
im = Image.open(src).convert("RGB")
if len(sys.argv) > 7:
    x0, y0, x1, y1 = map(int, sys.argv[4:8]); im = im.crop((x0, y0, x1, y1))
else:
    x0 = y0 = 0
big = im.resize((im.width * z, im.height * z), Image.NEAREST)
canvas = Image.new("RGB", (big.width + 30, big.height + 16), (0, 0, 0)); canvas.paste(big, (30, 16))
d = ImageDraw.Draw(canvas)
for x in range(0, im.width + 1):
    c = (255, 60, 60) if (x + x0) % 8 == 0 else (70, 70, 70)
    if (x + x0) % 2 == 0: d.line([(30 + x * z, 16), (30 + x * z, canvas.height)], fill=c)
    if (x + x0) % 8 == 0: d.text((30 + x * z + 1, 2), str(x + x0), fill=(255, 255, 0))
for y in range(0, im.height + 1):
    c = (255, 60, 60) if (y + y0) % 8 == 0 else (70, 70, 70)
    if (y + y0) % 2 == 0: d.line([(30, 16 + y * z), (canvas.width, 16 + y * z)], fill=c)
    if (y + y0) % 8 == 0: d.text((2, 16 + y * z + 1), str(y + y0), fill=(255, 255, 0))
canvas.save(out)
