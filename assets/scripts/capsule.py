#!/usr/bin/env python3
"""
Someplace — cohesive capsule (one design system across men's & women's).
Signature print: FINE terrazzo on midnight navy. Solids: navy/ivory/emerald/
terracotta. The signature recurs across genders so the line reads as one set.
"""
import math, os, random, json
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 3; T = 1000
NAVY = (31, 45, 61)
def _h(s): s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
SOLIDS = {"solid-navy": "#1f2d3d", "solid-ivory": "#f4efe4",
          "solid-emerald": "#234339", "solid-terracotta": "#bf4a2c"}
SPECKS = [_h(c) for c in ["#ede4cf", "#c4623a", "#8d9a84", "#9fb0c4", "#d8b48a"]]
WEIGHTS = [0.5, 0.16, 0.16, 0.10, 0.08]


def _sig_tile():
    """Fine terrazzo on midnight, seamless."""
    random.seed(1)
    im = Image.new("RGB", (T*SS, T*SS), NAVY); d = ImageDraw.Draw(im, "RGBA"); n = T*SS
    for _ in range(330):
        x, y = random.random()*n, random.random()*n
        r = n*(0.004 + random.random()*0.007)
        col = random.choices(SPECKS, weights=WEIGHTS)[0]
        verts = random.randint(5, 8); rot = random.random()*math.pi
        st = random.getstate()
        for dx in (-n, 0, n):
            for dy in (-n, 0, n):
                random.setstate(st)
                pts = [(x+dx+math.cos(rot+i*2*math.pi/verts)*r*(0.65+random.random()*0.7),
                        y+dy+math.sin(rot+i*2*math.pi/verts)*r*(0.65+random.random()*0.7))
                       for i in range(verts)]
                d.polygon(pts, fill=col)
        random.setstate(st); random.random()
    return im.resize((T, T), Image.LANCZOS)


_SIG = None
def build(art, w, h, out):
    global _SIG
    if art in SOLIDS:
        Image.new("RGB", (w, h), _h(SOLIDS[art])).save(out, "PNG"); return out
    if _SIG is None:
        _SIG = _sig_tile()
    tw, th = _SIG.size; canvas = Image.new("RGB", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            canvas.paste(_SIG, (x, y))
    canvas.save(out, "PNG"); return out


PRIMARY = {659:(5700,7500),514:(5100,7200),198:(6975,6000),272:(3750,5250),
 571:(7650,4050),330:(6900,3600),390:(4650,5400),388:(6000,6000),
 654:(2700,3150),84:(2550,2475)}
SLEEVE = {659:(5700,3000), 514:(5100,1950), 390:(7950,2700)}

# name, slug, cid, price, art, gender, collections
CAP = [
 ("The Resort Shirt","resort-shirt",659,108,"sig","Men",["Men","Unisex","Shirts","New arrivals","Most wanted"]),
 ("The Camp Shirt","camp-shirt",659,108,"solid-emerald","Unisex",["Unisex","Shirts"]),
 ("The Linen-look Shirt","linen-shirt",659,98,"solid-ivory","Men",["Men","Unisex","Shirts"]),
 ("The Beach Dress","beach-dress",514,98,"sig","Women",["Women","Dresses","New arrivals","Most wanted"]),
 ("The Bodycon","bodycon",198,108,"solid-navy","Women",["Women","Dresses"]),
 ("The One-Piece","one-piece",272,98,"solid-terracotta","Women",["Women","Swim","Swimwear"]),
 ("The Swim Trunk","swim-trunk",571,78,"sig","Men",["Men","Swim","Swimwear"]),
 ("The Resort Short","resort-short",330,72,"solid-navy","Men",["Men"]),
 ("The Bomber","bomber",390,148,"solid-emerald","Unisex",["Unisex","Most wanted"]),
 ("The Lounge Hoodie","lounge-hoodie",388,98,"solid-ivory","Unisex",["Unisex"]),
 ("The Bucket Hat","bucket-hat",654,42,"sig","Unisex",["Accessories","Unisex"]),
 ("The Tote","tote",84,34,"solid-navy","Unisex",["Accessories"]),
]
HOOKS = {
 "resort-shirt":"The flagship camp-collar shirt in our signature midnight terrazzo, printed head to hem.",
 "camp-shirt":"A boxy camp-collar shirt in deep emerald. Clean, grown-up, easy.",
 "linen-shirt":"An open-collar shirt in soft ivory — the off-duty staple.",
 "beach-dress":"A breezy t-shirt dress in the signature midnight terrazzo. Sand to street.",
 "bodycon":"A second-skin dress in deep navy. Quietly devastating.",
 "one-piece":"A sculpted one-piece in warm terracotta. Built to be seen.",
 "swim-trunk":"Recycled trunks in the signature midnight terrazzo. Quick to dry, slow to leave.",
 "resort-short":"A pull-on short in deep navy. Hammock to harbor bar.",
 "bomber":"A clean-lined bomber in deep emerald. The travel-day layer.",
 "lounge-hoodie":"A heavyweight recycled hoodie in soft ivory.",
 "bucket-hat":"A reversible bucket hat in the signature midnight terrazzo.",
 "tote":"An everyday tote in deep navy. Market runs and gallery days.",
}
MTO = ("Made to order — printed and shipped just for you in 5–7 days, so we "
       "make less and waste less.")


def manifest():
    out = []
    for name, slug, cid, price, art, gender, cols in CAP:
        files = {"primary": f"{slug}.png"}
        if cid in SLEEVE: files["sleeve"] = f"{slug}-slv.png"
        label = "signature terrazzo · midnight" if art == "sig" else art.replace("solid-", "solid ")
        out.append({"name":name,"slug":slug,"catalog_id":cid,"price":price,"art":art,
                    "gender":gender,"collections":cols,"files":files,"label":label,
                    "description":f"{HOOKS.get(slug,'')}\n\n{MTO}"})
    return out


def main():
    d = os.path.normpath(os.path.join(HERE, "..", "prints", "capsule"))
    os.makedirs(d, exist_ok=True)
    for it in manifest():
        cid = it["catalog_id"]; w, h = PRIMARY[cid]
        build(it["art"], w, h, os.path.join(d, it["files"]["primary"]))
        if "sleeve" in it["files"]:
            sw, sh = SLEEVE[cid]; build(it["art"], sw, sh, os.path.join(d, it["files"]["sleeve"]))
        print(f"{it['slug']:16} {it['art']:18} {w}x{h}")
    json.dump(manifest(), open(os.path.normpath(os.path.join(HERE, "..", "capsule.json")), "w"), indent=2)
    print("wrote capsule.json", len(manifest()))


if __name__ == "__main__":
    main()
