#!/usr/bin/env python3
"""
Someplace — Printful fulfillment sync.

For a Shopify-connected Printful store you cannot create products via API; the
product is created in Shopify, Printful imports it as an UNSYNCED sync product,
and you then make it fulfillment-ready by attaching a catalog variant + print
file to each sync variant via:

    PATCH /v2/sync-products/{id}   (with the full sync_variants array)

This module:
  1. polls GET /v2/sync-products for the imported product (matched by the
     Shopify product id stored in external_id),
  2. matches each imported sync variant to a Printful catalog variant by size,
  3. PATCHes the product to attach our hosted print file to every visible
     placement -> Printful renders mockups and marks it "synced".

Env:
  PF_TOKEN     Printful API token
  ART_SHA      git SHA the printfiles are committed at (for raw URLs)
Usage:
  python3 sync_printful.py <shopify_product_id> <slug>
  python3 sync_printful.py --dry <slug>      # print the PATCH body only
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = "18371850"
RAW = "https://raw.githubusercontent.com/useroadmap/someplace/{sha}/assets/prints/{f}"

# Placements we actually print (skip labels / internal / lining).
VISIBLE = {"front", "back", "sleeve_left", "sleeve_right", "default",
           "top_front", "top_back", "top", "bottom", "bottom_front",
           "bottom_back", "belt", "leg_left", "leg_right", "hood",
           "outside_front", "outside_back", "pocket", "front_large"}

PRODUCTS = {p["slug"]: p for p in json.load(open(os.path.join(HERE, "..", "products.json")))}


def _token():
    t = os.environ.get("PF_TOKEN")
    if not t:
        sys.exit("PF_TOKEN not set")
    return t


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        "https://api.printful.com" + path, data=data, method=method,
        headers={"Authorization": f"Bearer {_token()}", "X-PF-Store-Id": STORE,
                 "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=120)
        return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, None


def catalog_info(cid):
    """default technique + available placements for a catalog product."""
    st, d = api("GET", f"/v2/catalog-products/{cid}")
    d = d["data"]
    tech = next((t["key"] for t in d.get("techniques", []) if t.get("is_default")),
                d.get("techniques", [{}])[0].get("key", "cut-sew"))
    placements = [pl["placement"] for pl in d.get("placements", [])]
    return tech, placements


def size_to_catalog_variant(cid):
    """size -> catalog_variant_id (first variant per size)."""
    out, off = {}, 0
    while True:
        st, d = api("GET", f"/v2/catalog-products/{cid}/catalog-variants?limit=100&offset={off}")
        data = d.get("data", [])
        for v in data:
            out.setdefault(v.get("size"), v["id"])
        tot = d.get("paging", {}).get("total", len(data))
        off += len(data)
        if off >= tot or not data:
            break
    return out


def find_imported(shopify_pid, tries=30, delay=6):
    """Poll until Printful has imported the Shopify product."""
    ext = str(shopify_pid)
    for _ in range(tries):
        off = 0
        while True:
            st, d = api("GET", f"/v2/sync-products?limit=100&offset={off}")
            for p in d.get("data", []):
                if str(p.get("external_id")) == ext:
                    return p
            data = d.get("data", [])
            tot = d.get("paging", {}).get("total", 0)
            off += len(data)
            if off >= tot or not data:
                break
        time.sleep(delay)
    return None


def build_patch(prod, sync_variants, tech, placements):
    """Construct the PATCH sync_variants array attaching files by size."""
    size_map = size_to_catalog_variant(prod["catalog_id"])
    url = RAW.format(sha=os.environ["ART_SHA"], f=prod["printfile"])
    use = [pl for pl in placements if pl in VISIBLE] or ["front"]
    files = [{"placement": pl, "technique": tech,
              "layers": [{"type": "file", "url": url}]} for pl in use]
    out = []
    for sv in sync_variants:
        size = (sv.get("name", "").split("/")[-1].strip()
                or sv.get("size"))
        cvid = size_map.get(size) or size_map.get(size.upper())
        if not cvid:
            # fall back: single-size products
            cvid = next(iter(size_map.values())) if len(size_map) == 1 else None
        item = {"id": sv["id"], "retail_price": f"{prod['price']:.2f}",
                "placements": files}
        if cvid:
            item["catalog_variant_id"] = cvid
        out.append(item)
    return out


def sync(shopify_pid, slug):
    prod = PRODUCTS[slug]
    tech, placements = catalog_info(prod["catalog_id"])
    print(f"[{slug}] technique={tech} placements={placements}")
    p = find_imported(shopify_pid)
    if not p:
        sys.exit(f"[{slug}] Printful never imported Shopify product {shopify_pid}")
    pid = p["id"]
    st, d = api("GET", f"/v2/sync-products/{pid}/sync-variants")
    svs = d.get("data", [])
    patch = build_patch(prod, svs, tech, placements)
    st, d = api("PATCH", f"/v2/sync-products/{pid}",
                {"sync_product": {"name": prod["name"]}, "sync_variants": patch})
    print(f"[{slug}] PATCH /v2/sync-products/{pid} -> {st}")
    print(json.dumps(d, indent=2)[:1200])
    return st, d


if __name__ == "__main__":
    if sys.argv[1] == "--dry":
        slug = sys.argv[2]
        prod = PRODUCTS[slug]
        os.environ.setdefault("ART_SHA", "DRYSHA")
        tech, placements = catalog_info(prod["catalog_id"])
        fake = [{"id": 1, "name": f"{prod['name']} / M"}]
        print(json.dumps(build_patch(prod, fake, tech, placements), indent=2))
    else:
        sync(sys.argv[1], sys.argv[2])
