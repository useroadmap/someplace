#!/usr/bin/env python3
"""
Someplace — "Modern Flower" signature print (young & playful, flat).
Reproduces the approved Figma flat-flower motif at full printfile resolution:
clean retro-modern flowers (ring of petals + center) and confetti dots in a
fresh palette, seamless. Plus the fresh-palette solids for the rest of the line.
"""
import math, os
from PIL import Image, ImageDraw

SS = 3
TILE = 1200

def _h(s):
    s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

PALETTE = {
    "cream": "#efe7d6", "coral": "#f26b4e", "butter": "#f4b53c",
    "sky": "#7fb5c9", "pink": "#e68fb0", "green": "#6e9e63",
    "ink": "#22201c", "white": "#ffffff", "navy": "#234e63",
}
SOLIDS = {f"solid-{k}": v for k, v in PALETTE.items()}
PETALS = ["coral", "butter", "sky", "pink", "green"]
CENTERS = ["ink", "white"]


def _rng(seed):
    s = [seed]
    def r():
        s[0] = (s[0] * 9301 + 49297) % 233280
        return s[0] / 233280
    return r


def flower_tile(ground="cream"):
    n = TILE * SS
    img = Image.new("RGB", (n, n), _h(PALETTE[ground]))
    d = ImageDraw.Draw(img)
    r = _rng(7)

    def circle(cx, cy, rad, col):
        for dx in (-n, 0, n):
            for dy in (-n, 0, n):
                if -rad < cx+dx < n+rad and -rad < cy+dy < n+rad:
                    d.ellipse([cx+dx-rad, cy+dy-rad, cx+dx+rad, cy+dy+rad], fill=_h(PALETTE[col]))

    def flower(cx, cy, scale, pc, cc):
        pr, ring, k = 26*scale, 38*scale, 6
        for i in range(k):
            a = i*2*math.pi/k
            circle(cx+math.cos(a)*ring, cy+math.sin(a)*ring, pr, pc)
        circle(cx, cy, 22*scale, cc)

    gx, gy = 4, 4
    cw, ch = n/gx, n/gy
    for j in range(gy):
        for i in range(gx):
            cx = cw*(i+0.5) + (r()-0.5)*cw*0.5
            cy = ch*(j+0.5) + (r()-0.5)*ch*0.5
            flower(cx, cy, (0.85+r()*0.6)*SS, PETALS[int(r()*len(PETALS))], CENTERS[int(r()*len(CENTERS))])
    for _ in range(46):
        circle(r()*n, r()*n, (6+r()*6)*SS, "butter" if r() > 0.5 else "sky")
    return img.resize((TILE, TILE), Image.LANCZOS)


def build(art, w, h, out):
    if art in SOLIDS:
        Image.new("RGB", (w, h), _h(SOLIDS[art])).save(out, "PNG"); return out
    ground = "cream"
    if art.startswith("flower-"):
        ground = art.split("-", 1)[1]
    tile = flower_tile(ground)
    tw, th = tile.size; canvas = Image.new("RGB", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            canvas.paste(tile, (x, y))
    canvas.save(out, "PNG"); return out


if __name__ == "__main__":
    # 2x2 tiled swatch to confirm the look + seamless repeat
    t = flower_tile("cream")
    sz = 360
    sw = t.resize((sz, sz), Image.LANCZOS)
    board = Image.new("RGB", (sz*2, sz*2))
    for i in range(2):
        for j in range(2):
            board.paste(sw, (i*sz, j*sz))
    out = os.environ.get("OUT", "/tmp/flower.png")
    board.save(out); print("wrote", out, board.size)
