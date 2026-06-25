#!/usr/bin/env python3
"""
Someplace — full line build (v2 system: contour/terrazzo/solids in
marine/verde/midnight). Balanced ~50/50 solids vs prints.

Generates one printfile per product (+ sleeve file where the garment has a
distinct sleeve printfile) into assets/prints/v2/, and writes products2.json.
City is a marketing/lookbook grouping only (NOT on the garment).
"""
import json, os
import prints_v2 as pv

HERE = os.path.dirname(os.path.abspath(__file__))
PRIMARY = {514:(5100,7200),315:(8550,4500),198:(6975,6000),314:(8550,4500),
 202:(6900,4650),272:(3750,5250),469:(3375,2850),470:(3375,2850),668:(7500,3300),
 669:(7500,3300),659:(5700,7500),276:(4050,5100),330:(6900,3600),571:(7650,4050),
 390:(4650,5400),615:(5100,5700),388:(6000,6000),400:(4950,7500),654:(2700,3150),
 259:(11100,5700),274:(3150,5550),84:(2550,2475)}
SLEEVE = {659:(5700,3000), 514:(5100,1950), 390:(7950,2700)}

# name, slug, cid, price, print, colorway, city, collections
P = [
 ("The Resort Shirt","resort-shirt",659,108,"contour","marine","Lisbon",["Men","Unisex","Shirts","New arrivals","Most wanted"]),
 ("The Linen-look Shirt","linen-shirt",659,98,"solid","ivory","Lisbon",["Men","Unisex","Shirts"]),
 ("The Camp Shirt","camp-shirt",659,108,"terrazzo","midnight","Tulum",["Unisex","Shirts","New arrivals"]),
 ("The Beach Dress","beach-dress",514,98,"terrazzo","verde","Bali",["Women","Dresses","Beach dresses & layers","Most wanted"]),
 ("The Skater Dress","skater-dress",315,118,"solid","terracotta","Marrakech",["Women","Dresses"]),
 ("The Bodycon","bodycon",198,108,"contour","midnight","Tulum",["Women","Dresses"]),
 ("The Skater Skirt","skater-skirt",314,78,"solid","navy","Lisbon",["Women"]),
 ("The Beach Tank — Women","beach-tank-w",202,52,"solid","ivory","Bali",["Women","New arrivals"]),
 ("The One-Piece","one-piece",272,98,"terrazzo","midnight","Tulum",["Women","Swim","Swimwear","Most wanted"]),
 ("High-Waist Bikini Top","hw-bikini-top",469,48,"solid","coral","Bali",["Women","Swim","Swimwear"]),
 ("High-Waist Bikini Bottom","hw-bikini-btm",470,44,"solid","coral","Bali",["Women","Swim","Swimwear"]),
 ("String Bikini Top","string-bikini-top",668,46,"terrazzo","midnight","Tulum",["Women","Swim","Swimwear"]),
 ("String Bikini Bottom","string-bikini-btm",669,42,"terrazzo","midnight","Tulum",["Women","Swim","Swimwear"]),
 ("The Beach Tank — Men","beach-tank-m",276,54,"solid","navy","Bali",["Men","New arrivals"]),
 ("The Resort Short","resort-short",330,72,"contour","verde","Marrakech",["Men"]),
 ("The Swim Trunk","swim-trunk",571,78,"terrazzo","marine","Bali",["Men","Swim","Swimwear"]),
 ("The Bomber","bomber",390,148,"solid","emerald","Lisbon",["Unisex","Most wanted"]),
 ("The Windbreaker","windbreaker",615,138,"solid","navy","Lisbon",["Unisex"]),
 ("The Lounge Hoodie","lounge-hoodie",388,98,"solid","ivory","Marrakech",["Unisex"]),
 ("The Sweatpant","sweatpant",400,88,"solid","navy","Marrakech",["Unisex"]),
 ("The Bucket Hat","bucket-hat",654,42,"terrazzo","midnight","Tulum",["Accessories","Unisex"]),
 ("The Beach Towel","beach-towel",259,58,"terrazzo","midnight","Bali",["Accessories"]),
 ("The Beach Bag","beach-bag",274,54,"terrazzo","verde","Marrakech",["Accessories"]),
 ("The Tote","tote",84,34,"contour","midnight","Lisbon",["Accessories"]),
]

HOOKS = {  # short on-brand copy; refine later
 "resort-shirt":"The flagship camp-collar shirt, head-to-hem print, cut for long golden hours.",
 "linen-shirt":"An easy open-collar shirt in a soft tonal solid — the off-duty staple.",
 "camp-shirt":"A boxy camp-collar shirt in a fine speckled terrazzo. Pool to plaza.",
 "beach-dress":"A breezy t-shirt dress in a quiet terrazzo. Sand to street.",
 "skater-dress":"A fit-and-flare dress in a rich tonal solid. Made for spinning.",
 "bodycon":"A second-skin dress traced with soft contour lines.",
 "skater-skirt":"A flippy skirt in deep marine. Clean and confident.",
 "beach-tank-w":"A relaxed tank in an elevated ivory. Throw it on, walk out.",
 "one-piece":"A sculpted one-piece in midnight terrazzo. Built to be seen.",
 "hw-bikini-top":"A padded high-waist set top in a coral pop.",
 "hw-bikini-btm":"High-waisted, high-confidence — the matching bottom.",
 "string-bikini-top":"A padded string top in fine marine terrazzo.",
 "string-bikini-btm":"The string bottom that finishes the set.",
 "beach-tank-m":"A soft, lived-in tank in deep navy.",
 "resort-short":"A pull-on short traced in verde contour lines.",
 "swim-trunk":"Recycled trunks in marine terrazzo. Quick to dry, slow to leave.",
 "bomber":"A clean-lined bomber in deep emerald. The travel-day layer.",
 "windbreaker":"A packable windbreaker in marine. For the unpredictable coast.",
 "lounge-hoodie":"A heavyweight recycled hoodie in soft ivory.",
 "sweatpant":"Recycled joggers in deep navy. The other half of the hoodie.",
 "bucket-hat":"A reversible bucket hat in midnight terrazzo. Shade, sorted.",
 "beach-towel":"An oversized towel traced in marine contour.",
 "beach-bag":"A roomy tote with inner pocket, in verde terrazzo.",
 "tote":"An everyday tote in verde contour. Market runs and gallery days.",
}
MTO = ("Made to order — printed and shipped just for you in 5–7 days, so we "
       "make less and waste less.")


def art_name(print_, colorway):
    return f"solid-{colorway}" if print_ == "solid" else print_


def manifest():
    out = []
    for name, slug, cid, price, pr, cw, city, cols in P:
        an = art_name(pr, cw)
        files = {"primary": f"{slug}-{an}.png"}
        if cid in SLEEVE:
            files["sleeve"] = f"{slug}-{an}-slv.png"
        out.append({"name":name,"slug":slug,"catalog_id":cid,"price":price,
                    "print":pr,"colorway":cw,"art":an,"city":city,
                    "collections":cols,"files":files,
                    "label":f"{pr if pr!='solid' else 'solid'} · {cw}",
                    "description":f"{HOOKS.get(slug,'')}\n\n{MTO}"})
    return out


def main():
    d = os.path.normpath(os.path.join(HERE, "..", "prints", "v2"))
    os.makedirs(d, exist_ok=True)
    for it in manifest():
        cid = it["catalog_id"]; w, h = PRIMARY[cid]; an = it["art"]
        cw = it["colorway"] if it["print"] != "solid" else "marine"  # cw unused for solids
        pv.build(an if it["print"] != "solid" else an, cw, w, h,
                 os.path.join(d, it["files"]["primary"]))
        if "sleeve" in it["files"]:
            sw, sh = SLEEVE[cid]
            pv.build(an, cw, sw, sh, os.path.join(d, it["files"]["sleeve"]))
        print(f"{it['slug']:20} {an:18} {w}x{h}")
    man = manifest()
    json.dump(man, open(os.path.normpath(os.path.join(HERE, "..", "products2.json")), "w"), indent=2)
    print("wrote products2.json", len(man))


if __name__ == "__main__":
    main()
