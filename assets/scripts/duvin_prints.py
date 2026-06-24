#!/usr/bin/env python3
"""
Someplace — retro-leisure print system (Duvin-adjacent, resortwear not beach).

Seamless all-over prints with a vintage-leisure attitude: wavy checkerboards,
cabana stripes, clean illustrated icon repeats — warm retro palettes, confident
but cool. Rendered as seamless square tiles, tiled to printfile size by the
caller (cover fill).
"""
import math, os, importlib.util
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))


def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# Warm vintage-leisure palettes (per colorway).
PALETTES = {
    "havana": {  # cream / rust / olive — the core resort look
        "ground": _hex("#efe4cd"), "ink": _hex("#23201a"),
        "a": _hex("#b5532f"), "b": _hex("#6f7a4f"), "c": _hex("#d49a3c"),
        "d": _hex("#2f4a52"), "cream": _hex("#f3ead6"),
    },
    "riviera": {  # navy / cream / mustard — clubby
        "ground": _hex("#1f3340"), "ink": _hex("#0f1c24"),
        "a": _hex("#d8c08f"), "b": _hex("#c4623a"), "c": _hex("#e7d8b6"),
        "d": _hex("#6f9b8e"), "cream": _hex("#ecdfc4"),
    },
}

SS = 3
TILE = 1100


def _tile(bg):
    im = Image.new("RGB", (TILE*SS, TILE*SS), bg)
    return im, ImageDraw.Draw(im, "RGBA")

def _fin(im):
    return im.resize((TILE, TILE), Image.LANCZOS)


def p_checker(p):
    """Wavy melted checkerboard — the signature retro motif."""
    n = TILE * SS
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    cell = n / 8.0
    # gentle sine warp for a softly wavy (not melted) check
    xw = xx + np.sin(yy / n * math.pi * 4) * cell * 0.16
    yw = yy + np.sin(xx / n * math.pi * 4) * cell * 0.16
    chk = ((np.floor(xw / cell) + np.floor(yw / cell)) % 2).astype(bool)
    a = np.array(p["a"], np.uint8); g = np.array(p["cream"], np.uint8)
    arr = np.where(chk[..., None], a, g)
    return Image.fromarray(arr, "RGB").resize((TILE, TILE), Image.LANCZOS)


def p_cabana(p):
    """Cabana stripe — bold vertical bands + thin shadow line."""
    im, d = _tile(p["cream"])
    n = TILE * SS
    seq = [p["a"], p["b"], p["c"], p["d"]]
    bands = 6
    bw = n / bands
    for i in range(bands):
        col = seq[i % len(seq)]
        x0 = i * bw
        d.rectangle([x0, 0, x0 + bw * 0.72, n], fill=col)
        # thin ink hairline at the band edge
        d.rectangle([x0 + bw * 0.72, 0, x0 + bw * 0.78, n], fill=p["ink"])
    return _fin(im)


def p_citrus(p):
    """Retro citrus-slice repeat on a solid ground (half-drop grid)."""
    im, d = _tile(p["ground"])
    n = TILE * SS
    step = n / 3.0
    r = step * 0.34
    def slice_(cx, cy):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=p["c"])          # rind
        ri = r * 0.80
        d.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=p["cream"])   # flesh
        for k in range(8):                                         # segments
            a = k * math.pi / 4
            d.line([cx, cy, cx+math.cos(a)*ri, cy+math.sin(a)*ri],
                   fill=p["a"], width=max(2, int(r*0.05)))
        d.ellipse([cx-r*0.10, cy-r*0.10, cx+r*0.10, cy+r*0.10], fill=p["a"])
    for gy in range(-1, 4):
        for gx in range(-1, 5):
            cx = gx*step + (step/2 if gy % 2 else 0)
            cy = gy*step
            slice_(cx, cy)
    return _fin(im)


def p_groovy(p):
    """Groovy horizontal wave bands — soft retro op-art."""
    n = TILE * SS
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    band = n / 7.0
    yw = yy + np.sin(xx / n * math.pi * 4) * band * 0.55
    idx = (np.floor(yw / band) % 3).astype(int)
    cols = np.array([p["a"], p["cream"], p["b"]], np.uint8)
    arr = cols[idx]
    return Image.fromarray(arr, "RGB").resize((TILE, TILE), Image.LANCZOS)


def p_daisy(p):
    """Clean retro daisy repeat on a solid ground."""
    im, d = _tile(p["b"])
    n = TILE * SS
    step = n / 3.0
    R = step * 0.30
    def daisy(cx, cy):
        for k in range(8):
            a = k * math.pi / 4
            px, py = cx+math.cos(a)*R*0.62, cy+math.sin(a)*R*0.62
            pr = R*0.42
            d.ellipse([px-pr, py-pr, px+pr, py+pr], fill=p["cream"])
        cr = R*0.34
        d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=p["c"])
    for gy in range(-1, 4):
        for gx in range(-1, 5):
            cx = gx*step + (step/2 if gy % 2 else 0)
            cy = gy*step
            daisy(cx, cy)
    return _fin(im)


PRINTS = {"checker": p_checker, "cabana": p_cabana, "citrus": p_citrus,
          "groovy": p_groovy, "daisy": p_daisy}


def build(name, colorway, w, h, out):
    tile = PRINTS[name](PALETTES[colorway])
    tw, th = tile.size
    canvas = Image.new("RGB", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            canvas.paste(tile, (x, y))
    canvas.save(out, "PNG")
    return out


if __name__ == "__main__":
    # contact sheet for QA
    sw = 300; names = list(PRINTS); cways = list(PALETTES)
    pad = 12
    W = len(names)*sw + (len(names)+1)*pad
    H = len(cways)*sw + (len(cways)+1)*pad + 20
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    dd = ImageDraw.Draw(sheet)
    for ri, cw in enumerate(cways):
        for ci, nm in enumerate(names):
            t = PRINTS[nm](PALETTES[cw]).resize((sw, sw), Image.LANCZOS)
            x = pad+ci*(sw+pad); y = pad+ri*(sw+pad)
            sheet.paste(t, (x, y)); dd.text((x+4, y+4), f"{nm}/{cw}", fill=(0,0,0))
    out = os.environ.get("OUT", "/tmp/duvin_sheet.png")
    sheet.save(out); print("wrote", out, sheet.size)
