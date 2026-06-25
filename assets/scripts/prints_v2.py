#!/usr/bin/env python3
"""
Someplace — refined upscale print system (chosen direction: A2/C2/D2).
Three quiet, textural prints — Windowpane, Contour, Terrazzo — plus house
solids, in a set of muted resort colorways. Seamless square tiles; caller tiles
to printfile size (cover).
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw

SS = 3
T = 1100

def _h(s):
    s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

# colorway -> ground / line / speck palette. Cool, rich, coastal (chosen set).
COLORWAYS = {
    "marine":   {"g": _h("#f4efe4"), "line": _h("#1f3a5f"), "soft": _h("#8295ad"),
                 "specks": ["#1f3a5f", "#e7613f", "#1f3a5f", "#9fb0c4"]},
    "verde":    {"g": _h("#f1efe2"), "line": _h("#234339"), "soft": _h("#7e9183"),
                 "specks": ["#234339", "#bf4a2c", "#e7dfca", "#234339"]},
    "midnight": {"g": _h("#1f2d3d"), "line": _h("#ede4cf"), "soft": _h("#7e8ba0"),
                 "specks": ["#ede4cf", "#d98a5b", "#9fb0c4", "#ede4cf"]},
}


def _tile(bg):
    im = Image.new("RGB", (T*SS, T*SS), bg); return im, ImageDraw.Draw(im, "RGBA")

def _fin(im):
    return im.resize((T, T), Image.LANCZOS)


def windowpane(p):
    """Tailored windowpane: clean primary grid + a fine paired line."""
    im, d = _tile(p["g"]); n = T*SS; step = n/5
    main = max(3, int(n*0.0042)); thin = max(2, int(n*0.0022))
    for i in range(6):
        x = i*step
        d.rectangle([x, 0, x+main, n], fill=p["line"])
        d.rectangle([x+step*0.10, 0, x+step*0.10+thin, n], fill=p["soft"])
        y = i*step
        d.rectangle([0, y, n, y+main], fill=p["line"])
        d.rectangle([0, y+step*0.10, n, y+step*0.10+thin], fill=p["soft"])
    return _fin(im)


def contour(p):
    """Undulating contour lines, gently varied — organic and quiet."""
    im, d = _tile(p["g"]); n = T*SS; rows = 11
    w = max(2, int(n*0.0034))
    for r in range(rows+1):
        y0 = r*n/rows
        amp = n*(0.018 + 0.012*math.sin(r*0.9))
        pts = [(x, y0 + math.sin(x/n*math.pi*4 + r*0.6)*amp) for x in range(0, n+1, 6)]
        col = p["line"] if r % 3 else p["soft"]
        d.line(pts, fill=col, width=w, joint="curve")
    return _fin(im)


def terrazzo(p):
    """Fine, refined terrazzo speckle, seamless."""
    random.seed(11)
    im, d = _tile(p["g"]); n = T*SS
    cols = [_h(c) for c in p["specks"]]
    for _ in range(230):
        x, y = random.random()*n, random.random()*n
        r = n*(0.005 + random.random()*0.012); c = random.choice(cols)
        k = random.choice([3, 4, 5, 6]); rot = random.random()*math.pi
        st = random.getstate()
        for dx in (-n, 0, n):
            for dy in (-n, 0, n):
                random.setstate(st)
                pts = [(x+dx+math.cos(rot+i*2*math.pi/k)*r*(0.7+random.random()*0.5),
                        y+dy+math.sin(rot+i*2*math.pi/k)*r*(0.7+random.random()*0.5))
                       for i in range(k)]
                d.polygon(pts, fill=c)
        random.setstate(st); random.random()
    return _fin(im)


# windowpane retired (too "nerdy"); line now runs on contour + terrazzo + solids.
PRINTS = {"contour": contour, "terrazzo": terrazzo}
SOLIDS = {"solid-ivory": "#f4efe4", "solid-navy": "#1f3a5f",
          "solid-emerald": "#234339", "solid-coral": "#e7613f",
          "solid-terracotta": "#bf4a2c"}


def build(name, colorway, w, h, out):
    if name in SOLIDS:
        Image.new("RGB", (w, h), _h(SOLIDS[name])).save(out, "PNG"); return out
    t = PRINTS[name](COLORWAYS[colorway])
    tw, th = t.size; canvas = Image.new("RGB", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            canvas.paste(t, (x, y))
    canvas.save(out, "PNG"); return out


if __name__ == "__main__":
    cways = ["bone", "sand", "sage", "clay", "espresso"]
    names = list(PRINTS)
    sw, pad = 300, 12
    W = len(cways)*sw + (len(cways)+1)*pad
    H = (len(names)+1)*sw + (len(names)+2)*pad + 20
    from PIL import ImageDraw as ID
    sheet = Image.new("RGB", (W, H), (250, 248, 243)); dd = ID.Draw(sheet)
    for ri, nm in enumerate(names):
        for ci, cw in enumerate(cways):
            t = PRINTS[nm](COLORWAYS[cw]).resize((sw, sw), Image.LANCZOS)
            x = pad+ci*(sw+pad); y = pad+ri*(sw+pad)
            sheet.paste(t, (x, y)); dd.text((x+5, y+5), f"{nm}/{cw}", fill=(40, 36, 30))
    # solids strip
    y = pad+len(names)*(sw+pad)
    for ci, (sn, sv) in enumerate(SOLIDS.items()):
        x = pad+ci*(sw+pad)
        sheet.paste(Image.new("RGB", (sw, sw), _h(sv)), (x, y)); dd.text((x+5, y+5), sn, fill=(120,110,95))
    out = os.environ.get("OUT", "/tmp/prints_v2.png"); sheet.save(out); print("wrote", out, sheet.size)
