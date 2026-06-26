import json, os, time, re, urllib.request
TOKEN=os.environ["PF_TOKEN"]; SHA=os.environ["ART_SHA"]; OUT=os.environ["OUT"]; SCRATCH=os.environ["SCRATCH"]
RAW="https://raw.githubusercontent.com/useroadmap/someplace/{sha}/assets/prints/capsule/{f}"
prods=json.load(open("/home/user/someplace/assets/capsule.json"))
CATVAR=json.load(open(f"{SCRATCH}/catalog_variants.json"))
SLEEVE_PL={"sleeve_left","sleeve_right","inside_yoke"}
VISIBLE={"front","back","sleeve_left","sleeve_right","default","top_front","top_back",
 "top","bottom","bottom_front","bottom_back","belt","leg_left","leg_right","hood",
 "outside_front","outside_back","details"}
def api(m,u,b=None):
    data=json.dumps(b).encode() if b else None
    r=urllib.request.Request(u,data=data,method=m,headers={"Authorization":f"Bearer {TOKEN}","X-PF-Store-Id":"18371850","Content-Type":"application/json"})
    try:
        x=urllib.request.urlopen(r,timeout=120); return x.status,json.load(x)
    except urllib.error.HTTPError as e:
        try: return e.code,json.loads(e.read().decode())
        except: return e.code,None
def dims(cid):
    st,d=api("GET",f"https://api.printful.com/mockup-generator/printfiles/{cid}")
    res=d["result"]; pf={p["printfile_id"]:(p["width"],p["height"]) for p in res["printfiles"]}
    vp=res["variant_printfiles"][0]["placements"]; return {pl:pf[i] for pl,i in vp.items()}
def front_style(cid):
    st,d=api("GET",f"https://api.printful.com/v2/catalog-products/{cid}/mockup-styles?limit=60")
    uniq=[]; seen=set()
    for pl in d.get("data",[]):
        for s in pl.get("mockup_styles",[]):
            i=s.get("id")
            if i in seen: continue
            seen.add(i); uniq.append((s.get("category_name"),(s.get("view_name") or ""),i))
    for want in ["Flat","Ghost"]:
        for c,v,i in uniq:
            if c==want and v.lower()=="front": return i
    for c,v,i in uniq:
        if v.lower()=="front": return i
    return uniq[0][2] if uniq else None
def wait(res):
    m=re.search(r"after (\d+) second",str(res)); return (int(m.group(1))+3) if m else 35
paths=json.load(open(f"{OUT}/index.json")) if os.path.exists(f"{OUT}/index.json") else {}
last=0
for it in prods:
    slug=it["slug"]
    if slug in paths: continue
    cid=it["catalog_id"]; dm=dims(cid); sid=front_style(cid)
    prim=RAW.format(sha=SHA,f=it["files"]["primary"]); slv=RAW.format(sha=SHA,f=it["files"].get("sleeve",it["files"]["primary"]))
    files=[]
    for pl,(w,hh) in dm.items():
        if pl not in VISIBLE: continue
        url=slv if pl in SLEEVE_PL else prim
        files.append({"placement":pl,"image_url":url,"position":{"area_width":w,"area_height":hh,"width":w,"height":hh,"top":0,"left":0}})
    sizes=CATVAR[str(cid)]["sizes"]; vid=sizes.get("M") or next(iter(sizes.values()))
    body={"variant_ids":[vid],"format":"jpg","files":files}
    if sid: body["mockup_style_ids"]=[sid]
    g=32-(time.time()-last)
    if g>0: time.sleep(g)
    last=time.time(); key=None
    for _ in range(8):
        st,d=api("POST",f"https://api.printful.com/mockup-generator/create-task/{cid}",body)
        res=(d or {}).get("result")
        if isinstance(res,dict) and res.get("task_key"): key=res["task_key"]; print("create",slug,"style",sid,key,flush=True); break
        print(slug,"wait",wait(res),flush=True); time.sleep(wait(res)); last=time.time()
    if not key: print("nokey",slug,flush=True); continue
    for _ in range(25):
        time.sleep(7)
        st,d=api("GET",f"https://api.printful.com/mockup-generator/task?task_key={key}")
        res=(d or {}).get("result"); status=res.get("status") if isinstance(res,dict) else None
        if status=="completed":
            mk=res["mockups"]; front=next((m for m in mk if m.get("placement")=="front"), mk[0])
            fn=f"{OUT}/{slug}.jpg"; urllib.request.urlretrieve(front["mockup_url"],fn)
            paths[slug]={"path":fn,"label":it["label"],"name":it["name"],"price":it["price"],"gender":it["gender"]}
            print("done",slug,flush=True); break
        if status=="failed": print("FAIL",slug,json.dumps(d)[:160],flush=True); break
    json.dump(paths,open(f"{OUT}/index.json","w"))
print("ALLDONE",len(paths),flush=True)
