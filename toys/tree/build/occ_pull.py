"""Pull occupations for the exact node set (batched VALUES) — avoids the heavy open query."""
import json, os, time, urllib.parse, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
UA="RoofbeamTreeOfThought/0.1 (https://roofbeam.net; parra.jeremy@gmail.com)"
nodes=json.load(open(os.path.join(HERE,"..","graph.json")))["nodes"]
qids=list(nodes.keys())

def sparql(q):
    data=urllib.parse.urlencode({"query":q}).encode()
    req=urllib.request.Request("https://query.wikidata.org/sparql", data=data,
        headers={"Accept":"application/sparql-results+json","User-Agent":UA,
                 "Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)

occ={}  # qid -> set(occupation label)
B=1200
for k in range(0, len(qids), B):
    batch=qids[k:k+B]
    vals=" ".join("wd:"+q for q in batch)
    q=f"SELECT ?n ?ocL WHERE {{ VALUES ?n {{ {vals} }} ?n wdt:P106 ?oc. ?oc rdfs:label ?ocL. FILTER(LANG(?ocL)='en') }}"
    for _ in range(3):
        try:
            d=sparql(q); break
        except Exception as e:
            print("  retry", e); time.sleep(3)
    else:
        print("  batch failed", k); continue
    for b in d["results"]["bindings"]:
        n=b["n"]["value"].rsplit("/",1)[-1]; occ.setdefault(n,set()).add(b["ocL"]["value"])
    print(f"  {k+len(batch)}/{len(qids)} nodes, {len(occ)} with occ")
    time.sleep(1)

json.dump({q:sorted(v) for q,v in occ.items()}, open(os.path.join(HERE,"occ.json"),"w"))
# tally
from collections import Counter
c=Counter()
for v in occ.values():
    for o in v: c[o]+=1
print("\ntop occupations in the influence graph:")
for o,n in c.most_common(30): print(f"  {n:5}  {o}")
print(f"\nwrote occ.json ({len(occ)} nodes)")
