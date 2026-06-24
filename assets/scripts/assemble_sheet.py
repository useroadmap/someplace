#!/usr/bin/env python3
"""Assemble rendered SKU mockups into labelled approval contact sheets."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ["OUT"]
idx = json.load(open(os.path.join(OUT, "index.json")))
PRODUCTS = {p["slug"]: p for p in json.load(open(os.path.join(HERE, "..", "products.json")))}

INK = (34, 29, 23); BONE = (244, 240, 232); MUT = (138, 129, 112); TANG = (255, 90, 54)

def font(sz, bold=False):
    for pth in ([
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        if os.path.exists(pth):
            return ImageFont.truetype(pth, sz)
    return ImageFont.load_default()

def sheet(slugs, title, path, cols=4):
    cell, caph, pad = 460, 96, 26
    rows = (len(slugs) + cols - 1) // cols
    W = cols * cell + (cols + 1) * pad
    H = 120 + rows * (cell + caph) + (rows + 1) * pad
    im = Image.new("RGB", (W, H), BONE)
    d = ImageDraw.Draw(im)
    d.text((pad, 40), title, fill=INK, font=font(46, True))
    d.text((pad, 92), "Someplace — first-draft SKU mockups · made-to-order AOP", fill=MUT, font=font(20))
    for i, slug in enumerate(slugs):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = 120 + pad + r * (cell + caph + pad)
        p = PRODUCTS[slug]
        if slug in idx and os.path.exists(idx[slug]):
            m = Image.open(idx[slug]).convert("RGB")
            m.thumbnail((cell, cell), Image.LANCZOS)
            im.paste(m, (x + (cell - m.width) // 2, y + (cell - m.height) // 2))
        else:
            d.rectangle([x, y, x + cell, y + cell], outline=MUT, width=2)
            d.text((x + 20, y + cell // 2), "(render pending)", fill=MUT, font=font(22))
        ty = y + cell + 8
        d.text((x, ty), p["name"], fill=INK, font=font(24, True))
        d.text((x, ty + 32), f"${p['price']}", fill=TANG, font=font(22, True))
        d.text((x + 70, ty + 33), f"{p['print']} · {p['colorway']}", fill=MUT, font=font(20))
    im.save(path)
    print("wrote", path, im.size)

core = [s for s, p in PRODUCTS.items() if p["colorway"] == "core"]
mar = [s for s, p in PRODUCTS.items() if p["colorway"] == "marrakech"]
sheet(core, "THE LINE — Core", os.path.join(OUT, "sheet_core.png"))
sheet(mar, "THE DROP — Marrakech", os.path.join(OUT, "sheet_marrakech.png"))
