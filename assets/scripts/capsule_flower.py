#!/usr/bin/env python3
"""
Someplace — young & playful capsule built on the Modern Flower signature.
One cohesive system across men's & women's: the flower print on hero pieces,
fresh-palette solids (cream/sky/coral/butter/green/navy) on the rest.
Writes capsule.json + printfiles into assets/prints/capsule/.
"""
import json, os
import modern_flower as mf

HERE = os.path.dirname(os.path.abspath(__file__))
PRIMARY = {659:(5700,7500),514:(5100,7200),198:(6975,6000),272:(3750,5250),
 571:(7650,4050),330:(6900,3600),390:(4650,5400),388:(6000,6000),
 654:(2700,3150),84:(2550,2475)}
SLEEVE = {659:(5700,3000), 514:(5100,1950), 390:(7950,2700)}

# name, slug, cid, price, art, gender, collections
CAP = [
 ("The Resort Shirt","resort-shirt",659,108,"flower","Men",["Men","Unisex","Shirts","New arrivals","Most wanted"]),
 ("The Camp Shirt","camp-shirt",659,108,"solid-sky","Unisex",["Unisex","Shirts"]),
 ("The Linen-look Shirt","linen-shirt",659,98,"solid-butter","Men",["Men","Unisex","Shirts"]),
 ("The Beach Dress","beach-dress",514,98,"flower","Women",["Women","Dresses","New arrivals","Most wanted"]),
 ("The Bodycon","bodycon",198,108,"solid-coral","Women",["Women","Dresses"]),
 ("The One-Piece","one-piece",272,98,"solid-navy","Women",["Women","Swim","Swimwear"]),
 ("The Swim Trunk","swim-trunk",571,78,"flower","Men",["Men","Swim","Swimwear","New arrivals"]),
 ("The Resort Short","resort-short",330,72,"solid-navy","Men",["Men"]),
 ("The Bomber","bomber",390,148,"solid-green","Unisex",["Unisex","Most wanted"]),
 ("The Lounge Hoodie","lounge-hoodie",388,98,"solid-cream","Unisex",["Unisex"]),
 ("The Bucket Hat","bucket-hat",654,42,"flower","Unisex",["Accessories","Unisex"]),
 ("The Tote","tote",84,34,"flower","Unisex",["Accessories"]),
]
HOOKS = {
 "resort-shirt":"The flagship camp-collar shirt in our signature Modern Flower print, head to hem.",
 "camp-shirt":"A boxy camp-collar shirt in fresh sky blue. Clean and easy.",
 "linen-shirt":"An open-collar shirt in warm butter. The off-duty staple.",
 "beach-dress":"A breezy t-shirt dress in the Modern Flower print. Sand to street.",
 "bodycon":"A second-skin dress in bright coral. Quietly loud.",
 "one-piece":"A sculpted one-piece in deep navy. Built to be seen.",
 "swim-trunk":"Recycled trunks in the Modern Flower print. Quick to dry, slow to leave.",
 "resort-short":"A pull-on short in deep navy. Hammock to harbor bar.",
 "bomber":"A clean-lined bomber in grass green. The travel-day layer.",
 "lounge-hoodie":"A heavyweight recycled hoodie in soft cream.",
 "bucket-hat":"A reversible bucket hat in the Modern Flower print.",
 "tote":"An everyday tote in the Modern Flower print. Market runs and gallery days.",
}
MTO = ("Made to order — printed and shipped just for you in 5–7 days, so we "
       "make less and waste less.")


def manifest():
    out = []
    for name, slug, cid, price, art, gender, cols in CAP:
        files = {"primary": f"{slug}.png"}
        if cid in SLEEVE:
            files["sleeve"] = f"{slug}-slv.png"
        label = "Modern Flower print" if art == "flower" else art.replace("solid-", "solid ")
        out.append({"name":name,"slug":slug,"catalog_id":cid,"price":price,"art":art,
                    "gender":gender,"collections":cols,"files":files,"label":label,
                    "description":f"{HOOKS.get(slug,'')}\n\n{MTO}"})
    return out


def main():
    d = os.path.normpath(os.path.join(HERE, "..", "prints", "capsule"))
    os.makedirs(d, exist_ok=True)
    # clear old capsule prints
    for f in os.listdir(d):
        if f.endswith(".png"):
            os.remove(os.path.join(d, f))
    for it in manifest():
        cid = it["catalog_id"]; w, h = PRIMARY[cid]
        mf.build(it["art"], w, h, os.path.join(d, it["files"]["primary"]))
        if "sleeve" in it["files"]:
            sw, sh = SLEEVE[cid]
            mf.build(it["art"], sw, sh, os.path.join(d, it["files"]["sleeve"]))
        print(f"{it['slug']:16} {it['art']:16} {w}x{h}")
    json.dump(manifest(), open(os.path.normpath(os.path.join(HERE, "..", "capsule.json")), "w"), indent=2)
    print("wrote capsule.json", len(manifest()))


if __name__ == "__main__":
    main()
