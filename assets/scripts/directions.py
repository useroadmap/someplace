#!/usr/bin/env python3
"""
Someplace — print DIRECTION board for upscale resortwear.
Four distinct lanes, two swatches each, restrained tonal palettes.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 3
T = 1000

P = {
    "paper": (239, 233, 221), "ecru": (230, 220, 199), "sand": (220, 206, 178),
    "stone": (201, 189, 166), "putty": (179, 167, 141), "sage": (141, 154, 132),
    "clay": (181, 138, 113), "espresso": (44, 39, 34), "taupe": (154, 142, 123),
    "ink": (58, 52, 45),
}


def tile(bg):
    im = Image.new("RGB", (T*SS, T*SS), bg)
    return im, ImageDraw.Draw(im, "RGBA")

def fin(im):
    return im.resize((T, T), Image.LANCZOS)

def wrap(fn, x, y, n, *a):
    for dx in (-n, 0, n):
        for dy in (-n, 0, n):
            fn(x+dx, y+dy, *a)


# ---- A · ATELIER (quiet luxe) ----
def a_pinstripe():
    im, d = tile(P["paper"]); n = T*SS
    x = 0; group = n/9
    while x < n:
        # a cluster of fine stripes then a gap
        for off, col, w in [(0, P["espresso"], 0.006), (0.10, P["taupe"], 0.010),
                            (0.16, P["espresso"], 0.006)]:
            xx = x + off*group
            d.rectangle([xx, 0, xx+n*w, n], fill=col)
        x += group
    return fin(im)

def a_windowpane():
    im, d = tile(P["paper"]); n = T*SS; step = n/6
    for i in range(7):
        d.rectangle([i*step, 0, i*step+n*0.004, n], fill=P["ink"])
        d.rectangle([0, i*step, n, i*step+n*0.004], fill=P["ink"])
    return fin(im)


# ---- B · DECO (architectural) ----
def b_arches():
    im, d = tile(P["ecru"]); n = T*SS; step = n/3
    cols = [P["clay"], P["stone"], P["sage"]]
    def arch(cx, cy, up):
        for k, c in enumerate(cols):
            r = step*0.46*(1-k*0.26)
            box = [cx-r, cy-r, cx+r, cy+r]
            d.pieslice(box, 180, 360, fill=None, outline=c, width=max(3, int(step*0.05)))
    for gy in range(-1, 4):
        for gx in range(-1, 5):
            cx = gx*step + (step/2 if gy % 2 else 0)
            wrap(arch, cx, gy*step, n, True)
    return fin(im)

def b_scallop():
    im, d = tile(P["paper"]); n = T*SS; step = n/6; r = step*0.62
    for row in range(-1, 8):
        for col in range(-1, 8):
            cx = col*step + (step/2 if row % 2 else 0)
            cy = row*step*0.6
            d.arc([cx-r, cy-r, cx+r, cy+r], 200, 340, fill=P["ink"], width=max(2, int(step*0.04)))
    return fin(im)


# ---- C · LINE BOTANICAL (modern toile) ----
def c_line_palm():
    im, d = tile(P["paper"]); n = T*SS
    col = P["espresso"]; w = max(2, int(n*0.0035))
    def frond(cx, cy, ang, L):
        ex, ey = cx+math.cos(ang)*L, cy+math.sin(ang)*L
        d.line([cx, cy, ex, ey], fill=col, width=w)
        for i in range(1, 12):
            t = i/12; px, py = cx+math.cos(ang)*L*t, cy+math.sin(ang)*L*t
            ll = L*0.26*(1-t*0.5)
            for s in (-1, 1):
                la = ang+s*math.radians(45)
                d.line([px, py, px+math.cos(la)*ll, py+math.sin(la)*ll], fill=col, width=w)
    for cx, cy, a, L in [(0.25, 0.30, -50, 0.34), (0.72, 0.66, 130, 0.34),
                         (0.55, 0.10, -110, 0.28), (0.05, 0.85, 30, 0.26),
                         (0.92, 0.20, -150, 0.24)]:
        wrap(frond, n*cx, n*cy, n, math.radians(a), n*L)
    return fin(im)

def c_contour():
    im, d = tile(P["paper"]); n = T*SS
    col = P["ink"]; w = max(2, int(n*0.003)); rows = 10
    for r in range(rows+1):
        y0 = r*n/rows
        pts = [(x, y0 + math.sin(x/n*math.pi*4 + r*0.7)*n*0.03) for x in range(0, n+1, 6)]
        d.line(pts, fill=col, width=w, joint="curve")
    return fin(im)


# ---- D · PAINTERLY ABSTRACT (Matisse-ish) ----
def d_cutout():
    im, d = tile(P["paper"]); n = T*SS; step = n/2.5
    def leaf(cx, cy, ang, L, col):
        ux, uy = math.cos(ang), math.sin(ang); px, py = -uy, ux
        pts = []
        for i in range(25):
            t = i/24; w = L*0.34*math.sin(math.pi*t)**0.6
            sx, sy = cx+ux*L*t, cy+uy*L*t
            pts.append((sx+px*w, sy+py*w))
        for i in range(24, -1, -1):
            t = i/24; w = L*0.34*math.sin(math.pi*t)**0.6
            sx, sy = cx+ux*L*t, cy+uy*L*t
            pts.append((sx-px*w, sy-py*w))
        d.polygon(pts, fill=col)
    items = [(0.25, 0.28, -55, 0.5, P["sage"]), (0.72, 0.68, 120, 0.46, P["clay"]),
             (0.55, 0.95, -100, 0.4, P["sage"]), (0.92, 0.12, 150, 0.4, P["clay"]),
             (0.05, 0.62, 20, 0.36, P["putty"])]
    for cx, cy, a, L, c in items:
        wrap(leaf, n*cx, n*cy, n, math.radians(a), n*L, c)
    return fin(im)

def d_terrazzo():
    import random; random.seed(7)
    im, d = tile(P["sand"]); n = T*SS
    cols = [P["espresso"], P["sage"], P["clay"], P["taupe"]]
    for _ in range(160):
        x, y = random.random()*n, random.random()*n
        r = n*(0.006+random.random()*0.014); c = random.choice(cols)
        k = random.choice([3, 4, 5]); rot = random.random()*math.pi
        pts = [(x+math.cos(rot+i*2*math.pi/k)*r, y+math.sin(rot+i*2*math.pi/k)*r) for i in range(k)]
        d.polygon(pts, fill=c)
    return fin(im)


DIRECTIONS = [
    ("A · ATELIER", "Quiet luxe — tonal shirting stripes & windowpane",
     [a_pinstripe, a_windowpane]),
    ("B · DECO", "Architectural — arches & scallops, one warm accent",
     [b_arches, b_scallop]),
    ("C · MODERN TOILE", "Editorial line-art botanicals, single ink tone",
     [c_line_palm, c_contour]),
    ("D · PAINTERLY", "Matisse-ish cut-outs & fine tonal terrazzo",
     [d_cutout, d_terrazzo]),
]


def board(path):
    sw, pad, head = 360, 26, 64
    cols = 2
    blockw = cols*sw + (cols+1)*pad
    W = blockw
    rowh = head + sw + pad
    H = pad + len(DIRECTIONS)*rowh
    im = Image.new("RGB", (W, H), (250, 248, 243))
    d = ImageDraw.Draw(im)
    def font(s, b=False):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else "")
        return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()
    for ri, (title, desc, fns) in enumerate(DIRECTIONS):
        y = pad + ri*rowh
        d.text((pad, y+6), title, fill=P["espresso"], font=font(30, True))
        d.text((pad, y+42), desc, fill=P["putty"], font=font(18))
        for ci, fn in enumerate(fns):
            sw_im = fn().resize((sw, sw), Image.LANCZOS)
            im.paste(sw_im, (pad+ci*(sw+pad), y+head))
    im.save(path)
    print("wrote", path, im.size)


if __name__ == "__main__":
    board(os.environ.get("OUT", "/tmp/directions.png"))
