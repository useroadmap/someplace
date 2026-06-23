#!/usr/bin/env python3
"""
Someplace — house print generator.

Renders the seven house prints (Sun, Palm, Tide, Terrazzo, Tile, Dot, Stripe)
plus house solids as seamless all-over-print files, sized to each Printful
product's printfile dimensions.

Design rules (from the brand handoff):
  - The clothing leads: prints are confident but not loud, flat/editorial.
  - Warm bone + espresso palette, small neon/tangerine accents.
  - NOT location-themed. A "colorway" (Core, Marrakech, ...) is just a palette.

Approach: each print is authored as a SEAMLESS square tile, rendered with
supersampling for clean anti-aliasing, then tiled to cover the target
printfile (cover fill_mode). This keeps memory sane and repeats crisp.

Usage:
  python3 generate_prints.py --print sun --colorway core \
      --width 5700 --height 7500 --out ../prints/sun-core-5700x7500.png
  python3 generate_prints.py --list
"""
import argparse
import math
import os
import random

from PIL import Image, ImageDraw

# --------------------------------------------------------------------------
# Palettes. Roles are referenced by the print functions; a colorway just
# remaps the roles. Hex from the brand tokens / house print system.
# --------------------------------------------------------------------------
def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

PALETTES = {
    # Default house colors, exactly as specified per print.
    "core": {
        "bone":  _hex("#f4f0e8"),
        "cream": _hex("#efe9dd"),
        "ink":   _hex("#221d17"),
        "ink2":  _hex("#33302b"),
        "tang":  _hex("#ff5a36"),
        "olive": _hex("#9aa68f"),
        "cyan":  _hex("#15c7d6"),
        "clay":  _hex("#c0917e"),
        "sand":  _hex("#cdbba0"),
        "lime":  _hex("#9be021"),
        "terra": _hex("#b75e39"),
        "pink":  _hex("#ff2e88"),
    },
    # Marrakech drop: warmer, clay/terracotta-led; cyan retired for clay.
    # (Palette only — no location motifs.)
    "marrakech": {
        "bone":  _hex("#f1e9da"),
        "cream": _hex("#ece2cf"),
        "ink":   _hex("#2a2017"),
        "ink2":  _hex("#3a2c20"),
        "tang":  _hex("#ff5a36"),
        "olive": _hex("#8d8a63"),
        "cyan":  _hex("#cf7a4e"),   # swapped warm
        "clay":  _hex("#b75e39"),
        "sand":  _hex("#d8c39f"),
        "lime":  _hex("#c2cf4e"),
        "terra": _hex("#9c4a2b"),
        "pink":  _hex("#e0563f"),
    },
}

SS = 3          # supersample factor for tile anti-aliasing
TILE = 1100     # base seamless tile size (px) before tiling to target


# --------------------------------------------------------------------------
# Seamless-draw helper: draw an element and its wraps so the tile repeats.
# --------------------------------------------------------------------------
def wrapped(fn, x, y, size, draw, *a, **k):
    """Call fn(draw, x+dx, y+dy, *a) for the 9 neighbour offsets when the
    element (radius ~size) is near an edge, so nothing is clipped at seams."""
    for dx in (-size, 0, size):
        for dy in (-size, 0, size):
            fn(draw, x + dx, y + dy, *a, **k)


def _new_tile(bg):
    img = Image.new("RGB", (TILE * SS, TILE * SS), bg)
    return img, ImageDraw.Draw(img, "RGBA")


def _finish(img):
    return img.resize((TILE, TILE), Image.LANCZOS)


# --------------------------------------------------------------------------
# The seven house prints. Each returns a seamless TILE×TILE RGB image.
# --------------------------------------------------------------------------
def print_sun(p, seed=7):
    """Concentric tangerine arcs/rings (rising-sun motif) on bone."""
    img, d = _new_tile(p["bone"])
    s = SS
    step = TILE * s // 2          # 2x2 grid of suns, offset rows
    r_outer = int(step * 0.42)
    rings = 5
    accents = [p["tang"], p["terra"], p["tang"]]
    centers = []
    for gy in range(0, TILE * s + step, step):
        row = gy // step
        offset = step // 2 if row % 2 else 0
        for gx in range(-step, TILE * s + step, step):
            centers.append((gx + offset, gy))

    def draw_sun(dr, cx, cy):
        for i in range(rings):
            rr = int(r_outer * (1 - i / rings))
            if rr <= 0:
                continue
            col = accents[i % len(accents)]
            w = max(2, int(r_outer * 0.085))
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                       outline=col, width=w)
        # solid core disc
        rc = int(r_outer * 0.13)
        dr.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=p["tang"])

    for (cx, cy) in centers:
        wrapped(draw_sun, cx, cy, TILE * s, d)
    return _finish(img)


def print_palm(p, seed=11):
    """Olive fronds + small tangerine sun discs on bone."""
    random.seed(seed)
    img, d = _new_tile(p["bone"])
    s = SS

    def draw_frond(dr, cx, cy, ang, length):
        # central stem (gently bowed)
        stem_w = max(3, int(length * 0.035))
        pts = []
        for i in range(21):
            t = i / 20
            bow = math.sin(t * math.pi) * length * 0.10
            sx = cx + math.cos(ang) * length * t + math.cos(ang + math.pi / 2) * bow
            sy = cy + math.sin(ang) * length * t + math.sin(ang + math.pi / 2) * bow
            pts.append((sx, sy))
        dr.line(pts, fill=p["olive"], width=stem_w, joint="curve")
        # leaflets along the stem, shrinking toward the tip
        n = 14
        for i in range(1, n + 1):
            t = i / (n + 1)
            bow = math.sin(t * math.pi) * length * 0.10
            px = cx + math.cos(ang) * length * t + math.cos(ang + math.pi / 2) * bow
            py = cy + math.sin(ang) * length * t + math.sin(ang + math.pi / 2) * bow
            leaf = length * 0.40 * (1 - t * 0.6)
            for side in (-1, 1):
                la = ang + side * math.radians(48) - (1 - t) * 0.25 * side
                lx = px + math.cos(la) * leaf
                ly = py + math.sin(la) * leaf
                dr.line([px, py, lx, ly], fill=p["olive"],
                        width=max(2, int(stem_w * 0.85)))

    def draw_disc(dr, cx, cy, r):
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=p["tang"])

    full = TILE * s
    fronds = [
        (full * 0.16, full * 0.26, math.radians(-58), full * 0.34),
        (full * 0.62, full * 0.20, math.radians(-118), full * 0.32),
        (full * 0.38, full * 0.80, math.radians(58), full * 0.34),
        (full * 0.88, full * 0.74, math.radians(122), full * 0.30),
        (full * 0.05, full * 0.92, math.radians(-22), full * 0.28),
        (full * 0.96, full * 0.10, math.radians(150), full * 0.26),
    ]
    for (x, y, a, l) in fronds:
        wrapped(draw_frond, x, y, full, d, a, l)
    discs = [(full * 0.50, full * 0.14, full * 0.05),
             (full * 0.10, full * 0.60, full * 0.04),
             (full * 0.80, full * 0.44, full * 0.055),
             (full * 0.34, full * 0.50, full * 0.032)]
    for (x, y, r) in discs:
        wrapped(draw_disc, x, y, full, d, r)
    return _finish(img)


def print_tide(p, seed=3):
    """Horizontal cyan sine lines on cream."""
    img, d = _new_tile(p["cream"])
    s = SS
    full = TILE * s
    rows = 9
    gap = full / rows
    amp = gap * 0.32
    period = full / 2          # 2 full waves across → seamless in x
    w = max(2, int(gap * 0.13))
    for r in range(rows):
        y0 = r * gap + gap / 2
        col = p["cyan"] if r % 3 else p["tang"]
        pts = []
        for x in range(0, full + 1, max(2, s)):
            y = y0 + math.sin(2 * math.pi * x / period + r) * amp
            pts.append((x, y))
        d.line(pts, fill=col, width=w, joint="curve")
    return _finish(img)


def print_terrazzo(p, seed=42):
    """Sand ground with scattered multicolour specks."""
    random.seed(seed)
    img, d = _new_tile(p["sand"])
    s = SS
    full = TILE * s
    cols = [p["ink"], p["tang"], p["olive"], p["cyan"],
            p["clay"], p["lime"], p["terra"]]

    def draw_speck(dr, x, y, r, col, rot, sides):
        pts = []
        for i in range(sides):
            a = rot + i * 2 * math.pi / sides
            rr = r * (0.7 + random.random() * 0.5)
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        dr.polygon(pts, fill=col)

    n = 220
    for _ in range(n):
        x = random.random() * full
        y = random.random() * full
        r = full * (0.008 + random.random() * 0.022)
        col = random.choice(cols)
        rot = random.random() * math.pi
        sides = random.choice([3, 4, 5, 6])
        # re-seed deterministically per speck shape for wraps to match
        st = random.getstate()
        for dx in (-full, 0, full):
            for dy in (-full, 0, full):
                random.setstate(st)
                draw_speck(d, x + dx, y + dy, r, col, rot, sides)
        random.setstate(st)
        random.random()  # advance
    return _finish(img)


def print_tile(p, seed=5):
    """Ink ground with tangerine diamonds (argyle)."""
    img, d = _new_tile(p["ink"])
    s = SS
    full = TILE * s
    n = 4                       # diamonds across
    step = full / n
    half = step / 2
    for iy in range(-1, n + 1):
        for ix in range(-1, n + 1):
            cx = ix * step + (half if iy % 2 else 0)
            cy = iy * half
            col = p["tang"] if (ix + iy) % 2 == 0 else p["clay"]
            r = half * 0.62
            d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                      fill=col)
            # thin outline accent
            r2 = half * 0.82
            d.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)],
                      outline=p["bone"], width=max(1, int(step * 0.012)))
    return _finish(img)


def print_dot(p, seed=9):
    """Clay ground with bone polka dots, offset rows."""
    img, d = _new_tile(p["clay"])
    s = SS
    full = TILE * s
    n = 6
    step = full / n
    r = step * 0.22
    for iy in range(0, n + 1):
        for ix in range(-1, n + 1):
            cx = ix * step + (step / 2 if iy % 2 else 0)
            cy = iy * step
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=p["bone"])
    return _finish(img)


def print_stripe(p, seed=1):
    """Vertical bone/ink awning stripe."""
    img, d = _new_tile(p["bone"])
    s = SS
    full = TILE * s
    n = 8                       # stripe pairs
    bw = full / (n * 2)
    for i in range(n * 2):
        if i % 2 == 0:
            d.rectangle([i * bw, 0, (i + 1) * bw, full], fill=p["ink"])
    return _finish(img)


PRINTS = {
    "sun": print_sun, "palm": print_palm, "tide": print_tide,
    "terrazzo": print_terrazzo, "tile": print_tile, "dot": print_dot,
    "stripe": print_stripe,
}

# House solids
SOLIDS = {
    "solid-sand": "sand", "solid-olive": "olive",
    "solid-clay": "clay", "solid-ink": "ink2",
}


def build(print_name, colorway, width, height, out):
    pal = PALETTES[colorway]
    if print_name in SOLIDS:
        canvas = Image.new("RGB", (width, height), pal[SOLIDS[print_name]])
        canvas.save(out, "PNG")
        return out
    tile = PRINTS[print_name](pal)
    # Tile to cover the target printfile dimensions.
    tw, th = tile.size
    canvas = Image.new("RGB", (width, height))
    for y in range(0, height, th):
        for x in range(0, width, tw):
            canvas.paste(tile, (x, y))
    canvas.save(out, "PNG")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="print_name")
    ap.add_argument("--colorway", default="core")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("prints:", ", ".join(PRINTS))
        print("solids:", ", ".join(SOLIDS))
        print("colorways:", ", ".join(PALETTES))
        return
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    path = build(a.print_name, a.colorway, a.width, a.height, a.out)
    print("wrote", path)


if __name__ == "__main__":
    main()
