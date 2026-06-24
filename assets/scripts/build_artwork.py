#!/usr/bin/env python3
"""
Someplace — build manifest + artwork generator.

Defines the launch line (garment -> Printful catalog id, retail price, house
print, colorway) and renders ONE printfile per product at its primary (largest)
Printful printfile dimension. Printful's "cover" fill reuses that same file for
the product's other placements (sleeves, linings, etc.), so one file per
product is enough and stays pixel-sharp on the main body.

Writes:
  assets/prints/<slug>-<colorway>.png   (the printfiles, public via raw URL)
  assets/products.json                  (manifest consumed by the sync step)
"""
import json, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gp", os.path.join(HERE, "generate_prints.py"))
gp = importlib.util.module_from_spec(spec); spec.loader.exec_module(gp)

# Primary (largest-area) printfile dimension per catalog product — from
# GET /mockup-generator/printfiles/{id}. Used for the main body; cover handles
# the rest.
PRIMARY = {
    514:(5100,7200), 315:(8550,4500), 198:(6975,6000), 314:(8550,4500),
    202:(6900,4650), 272:(3750,5250), 469:(3375,2850), 470:(3375,2850),
    668:(7500,3300), 669:(7500,3300), 659:(5700,7500), 276:(4050,5100),
    330:(6900,3600), 571:(7650,4050), 390:(4650,5400), 615:(5100,5700),
    388:(6000,6000), 400:(4950,7500), 654:(2700,3150), 259:(11100,5700),
    274:(3150,5550), 84:(2550,2475),
}

# name, slug, catalog_id, price, print, colorway, collections
PRODUCTS = [
    # ---- Core line ----
    ("The Resort Shirt","resort-shirt",659,108,"palm","core",["Men","Unisex","Shirts","New arrivals","Most wanted"]),
    ("The Linen-look Shirt","linen-shirt",659,98,"solid-sand","core",["Men","Unisex","Shirts"]),
    ("The Camp Shirt","camp-shirt",659,108,"tile","core",["Unisex","Shirts","New arrivals"]),
    ("The Beach Dress","beach-dress",514,98,"tide","core",["Women","Dresses","Beach dresses & layers","Most wanted"]),
    ("The Skater Dress","skater-dress",315,118,"terrazzo","core",["Women","Dresses"]),
    ("The Bodycon","bodycon",198,108,"sun","core",["Women","Dresses"]),
    ("The Skater Skirt","skater-skirt",314,78,"stripe","core",["Women"]),
    ("The Beach Tank — Women","beach-tank-w",202,52,"palm","core",["Women","New arrivals"]),
    ("The One-Piece","one-piece",272,98,"sun","core",["Women","Swim","Swimwear","Most wanted"]),
    ("High-Waist Bikini Top","hw-bikini-top",469,48,"tide","core",["Women","Swim","Swimwear"]),
    ("High-Waist Bikini Bottom","hw-bikini-btm",470,44,"tide","core",["Women","Swim","Swimwear"]),
    ("String Bikini Top","string-bikini-top",668,46,"terrazzo","core",["Women","Swim","Swimwear"]),
    ("String Bikini Bottom","string-bikini-btm",669,42,"terrazzo","core",["Women","Swim","Swimwear"]),
    ("The Beach Tank — Men","beach-tank-m",276,54,"tide","core",["Men","New arrivals"]),
    ("The Resort Short","resort-short",330,72,"palm","core",["Men"]),
    ("The Swim Trunk","swim-trunk",571,78,"sun","core",["Men","Swim","Swimwear"]),
    ("The Bomber","bomber",390,148,"tile","core",["Unisex","Most wanted"]),
    ("The Windbreaker","windbreaker",615,138,"stripe","core",["Unisex"]),
    ("The Lounge Hoodie","lounge-hoodie",388,98,"terrazzo","core",["Unisex"]),
    ("The Sweatpant","sweatpant",400,88,"stripe","core",["Unisex"]),
    ("The Bucket Hat","bucket-hat",654,42,"palm","core",["Accessories","Unisex"]),
    ("The Beach Towel","beach-towel",259,58,"stripe","core",["Accessories"]),
    ("The Beach Bag","beach-bag",274,54,"palm","core",["Accessories"]),
    ("The Tote","tote",84,34,"sun","core",["Accessories"]),
    # ---- Marrakech hero drop ----
    ("The Resort Shirt — Marrakech","resort-shirt-mar",659,108,"palm","marrakech",["Men","Unisex","Shirts","New arrivals"]),
    ("The Beach Dress — Marrakech","beach-dress-mar",514,98,"terrazzo","marrakech",["Women","Dresses","New arrivals"]),
    ("The One-Piece — Marrakech","one-piece-mar",272,98,"sun","marrakech",["Women","Swim","Swimwear"]),
    ("The Bomber — Marrakech","bomber-mar",390,148,"tile","marrakech",["Unisex","New arrivals"]),
]


# Short on-brand hook per product (refined later; designs iterate first).
HOOKS = {
    "resort-shirt":"The flagship. A camp-collar shirt cut for long golden hours and longer dinners.",
    "linen-shirt":"An easy open-collar shirt with a soft textured hand — the one you live in off-duty.",
    "camp-shirt":"A boxy camp-collar shirt with a graphic tiled print. Equal parts pool and plaza.",
    "beach-dress":"A breezy t-shirt dress that moves from sand to street without a second thought.",
    "skater-dress":"A fit-and-flare dress with a painterly all-over print. Made for spinning.",
    "bodycon":"A second-skin dress in a sunlit all-over print. Quietly devastating.",
    "skater-skirt":"A flippy awning-striped skirt that does all the talking.",
    "beach-tank-w":"A relaxed tank in a layered botanical. Throw it on, walk out.",
    "one-piece":"A sculpted one-piece in a radiant sun print. Built to be seen.",
    "hw-bikini-top":"A padded high-waist set top in a watery all-over print.",
    "hw-bikini-btm":"High-waisted, high-confidence — the matching bottom.",
    "string-bikini-top":"A padded string top speckled in terrazzo brights.",
    "string-bikini-btm":"The string bottom that finishes the set.",
    "beach-tank-m":"A soft, lived-in tank in a rippling tide print.",
    "resort-short":"A pull-on short in a tonal palm. From hammock to harbor bar.",
    "swim-trunk":"Recycled swim trunks in a glowing sun print. Quick to dry, slow to leave.",
    "bomber":"A clean-lined bomber in a graphic tile print. The travel-day layer.",
    "windbreaker":"A packable windbreaker in awning stripe. For the unpredictable coast.",
    "lounge-hoodie":"A heavyweight recycled hoodie in a soft terrazzo. Airport to apartment.",
    "sweatpant":"Recycled joggers in a tonal stripe. The other half of the hoodie.",
    "bucket-hat":"A reversible bucket hat in a layered palm. Shade, sorted.",
    "beach-towel":"An oversized towel in classic awning stripe. Claim your sand.",
    "beach-bag":"A roomy tote with an inner pocket, in a tonal palm. Everything fits.",
    "tote":"An everyday tote in a sunlit print. Market runs and gallery days.",
    "resort-shirt-mar":"The flagship resort shirt in the warm Marrakech colorway.",
    "beach-dress-mar":"The t-shirt dress in terrazzo, warmed up for the Marrakech drop.",
    "one-piece-mar":"The sculpted one-piece in the warm Marrakech sun.",
    "bomber-mar":"The graphic bomber, reworked in warm Marrakech tones.",
}
MADE_TO_ORDER = ("Made to order — each piece is printed and shipped just for you in "
                 "5–7 days, so we make less and waste less.")


def description(slug):
    return f"{HOOKS.get(slug,'')}\n\n{MADE_TO_ORDER}"


def manifest():
    out = []
    for name, slug, cid, price, prnt, cw, cols in PRODUCTS:
        out.append({"name":name,"slug":slug,"catalog_id":cid,"price":price,
                    "print":prnt,"colorway":cw,"collections":cols,
                    "printfile":f"{slug}-{cw}.png",
                    "description":description(slug)})
    return out


def main():
    prints_dir = os.path.normpath(os.path.join(HERE, "..", "prints"))
    os.makedirs(prints_dir, exist_ok=True)
    seen = set()
    for name, slug, cid, price, prnt, cw, cols in PRODUCTS:
        w, h = PRIMARY[cid]
        out = os.path.join(prints_dir, f"{slug}-{cw}.png")
        if out in seen:
            continue
        seen.add(out)
        gp.build(prnt, cw, w, h, out)
        print(f"{slug:20} {prnt:11} {cw:9} {w}x{h}")
    man = manifest()
    with open(os.path.normpath(os.path.join(HERE, "..", "products.json")), "w") as f:
        json.dump(man, f, indent=2)
    print(f"wrote products.json ({len(man)} products)")


if __name__ == "__main__":
    main()
