#!/usr/bin/env python3
"""
Batch-render a Printful mockup for every SKU in products.json using the hosted
printfiles, and save them locally for an approval contact sheet.

Env: PF_TOKEN, ART_SHA, OUT (dir)
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = "18371850"
TOKEN = os.environ["PF_TOKEN"]
SHA = os.environ["ART_SHA"]
OUT = os.environ.get("OUT", "/tmp/mockups")
os.makedirs(OUT, exist_ok=True)
RAW = "https://raw.githubusercontent.com/useroadmap/someplace/{sha}/assets/prints/{f}"
VISIBLE = {"front", "back", "sleeve_left", "sleeve_right", "default",
           "top_front", "top_back", "top", "bottom", "bottom_front",
           "bottom_back", "belt", "leg_left", "leg_right", "hood",
           "outside_front", "outside_back", "front_large"}
PRODUCTS = json.load(open(os.path.join(HERE, "..", "products.json")))
CATVAR = json.load(open(os.path.join(os.environ["SCRATCH"], "catalog_variants.json")))


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.printful.com" + path, data=data,
        method=method, headers={"Authorization": f"Bearer {TOKEN}",
        "X-PF-Store-Id": STORE, "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(req, timeout=120)
            return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode())
            except Exception:
                return e.code, None
        except Exception:
            time.sleep(2 * (attempt + 1))
    return 0, None


_pf_cache = {}
def printfile_dims(cid):
    if cid in _pf_cache:
        return _pf_cache[cid]
    st, d = api("GET", f"/mockup-generator/printfiles/{cid}")
    res = d["result"]
    pf = {p["printfile_id"]: (p["width"], p["height"]) for p in res["printfiles"]}
    vp = res["variant_printfiles"][0]["placements"]
    out = {pl: pf[pfid] for pl, pfid in vp.items()}
    _pf_cache[cid] = out
    return out


def rep_variant(cid):
    sizes = CATVAR[str(cid)]["sizes"]
    return sizes.get("M") or next(iter(sizes.values()))


def submit(prod):
    cid = prod["catalog_id"]
    url = RAW.format(sha=SHA, f=prod["printfile"])
    dims = printfile_dims(cid)
    files = []
    for pl, (w, h) in dims.items():
        if pl in VISIBLE:
            files.append({"placement": pl, "image_url": url,
                          "position": {"area_width": w, "area_height": h,
                                       "width": w, "height": h, "top": 0, "left": 0}})
    if not files:  # fall back to first non-label placement
        pl, (w, h) = next(iter(dims.items()))
        files = [{"placement": pl, "image_url": url,
                  "position": {"area_width": w, "area_height": h,
                               "width": w, "height": h, "top": 0, "left": 0}}]
    body = {"variant_ids": [rep_variant(cid)], "format": "jpg", "files": files}
    return body, cid


import re
def wait_secs(res):
    m = re.search(r"after (\d+) second", str(res))
    return int(m.group(1)) + 3 if m else 35


def create(prod):
    """Submit one create-task, honouring the ~2/min limit (parse 429 wait)."""
    body, cid = submit(prod)
    for attempt in range(8):
        st, d = api("POST", f"/mockup-generator/create-task/{cid}", body)
        res = (d or {}).get("result")
        if isinstance(res, dict) and res.get("task_key"):
            print(f"create {prod['slug']:20} -> key={res['task_key']}", flush=True)
            return res["task_key"]
        w = wait_secs(res)
        print(f"create {prod['slug']:20} -> {st} wait {w}s ({str(res)[:60]})", flush=True)
        time.sleep(w)
    return None


def poll(slug, key, results):
    for _ in range(30):
        time.sleep(8)
        st, d = api("GET", f"/mockup-generator/task?task_key={key}")
        res = (d or {}).get("result")
        if not isinstance(res, dict):           # rate-limited GET; back off
            time.sleep(wait_secs(res)); continue
        if res.get("status") == "completed":
            results[slug] = res["mockups"][0]["mockup_url"]
            print(f"done {slug}", flush=True)
            return True
        if res.get("status") == "failed":
            print(f"FAILED {slug}: {json.dumps(d)[:300]}", flush=True)
            return False
    print(f"timeout {slug}", flush=True)
    return False


def main():
    results, paths = {}, {}
    last = 0
    for p in PRODUCTS:
        gap = 32 - (time.time() - last)        # keep >=32s between creates
        if gap > 0:
            time.sleep(gap)
        last = time.time()
        key = create(p)
        if not key:
            continue
        if poll(p["slug"], key, results):
            try:
                fn = os.path.join(OUT, f"{p['slug']}.jpg")
                urllib.request.urlretrieve(results[p["slug"]], fn)
                paths[p["slug"]] = fn
            except Exception as e:
                print("dl fail", p["slug"], e, flush=True)
        json.dump(paths, open(os.path.join(OUT, "index.json"), "w"))
        print(f"--- progress {len(paths)}/{len(PRODUCTS)} ---", flush=True)
    print("DOWNLOADED", len(paths), "-> index.json", flush=True)


if __name__ == "__main__":
    main()
