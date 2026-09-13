"""Backfill labels for spine nodes whose label is under Wikidata's 'mul' code, not 'en'."""
import json, os, re, time, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__)); TOY=os.path.dirname(HERE)
UA="RoofbeamTreeOfThought/0.1 (parra.jeremy@gmail.com)"
S=json.load(open(os.path.join(TOY,"tree_spine.json"))); nodes=S["nodes"]
miss=[q for q,v in nodes.items() if v[0] is None or v[0]==q or re.match(r'^Q\d+$',str(v[0]))]
print(f"backfilling {len(miss)} nodes")
def best(labs):
    for lg in ("en","mul","la","el","de","fr"):
        if lg in labs: return labs[lg]["value"]
    return next(iter(labs.values()))["value"] if labs else None
fixed=0
for k in range(0,len(miss),50):
    ids="|".join(miss[k:k+50])
    url=f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids}&props=labels&format=json"
    req=urllib.request.Request(url, headers={"User-Agent":UA})
    for _ in range(3):
        try:
            d=json.load(urllib.request.urlopen(req, timeout=60)); break
        except Exception as e: print("  retry",e); time.sleep(2)
    else: continue
    for q,ent in d.get("entities",{}).items():
        lab=best(ent.get("labels",{}))
        if lab and q in nodes: nodes[q][0]=lab; fixed+=1
    time.sleep(0.5)
print(f"fixed {fixed}")
for q in ["Q9061","Q9312","Q9358","Q48301"]:
    if q in nodes: print(f"  {q} -> {nodes[q][0]}")
json.dump(S, open(os.path.join(TOY,"tree_spine.json"),"w"), separators=(",",":"))
