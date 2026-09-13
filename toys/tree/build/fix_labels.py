"""Re-fetch English labels for spine nodes that came back unlabeled (bare Q-id)."""
import json, os, re, time, urllib.parse, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__)); TOY=os.path.dirname(HERE)
UA="RoofbeamTreeOfThought/0.1 (https://roofbeam.net; parra.jeremy@gmail.com)"
S=json.load(open(os.path.join(TOY,"tree_spine.json")))
nodes=S["nodes"]
def unlabeled(q,v):
    l=v[0]; return (l is None) or (l==q) or bool(re.match(r'^Q\d+$', str(l)))
miss=[q for q,v in nodes.items() if unlabeled(q,v)]
print(f"unlabeled spine nodes: {len(miss)} of {len(nodes)}")

def sparql(q):
    data=urllib.parse.urlencode({"query":q}).encode()
    req=urllib.request.Request("https://query.wikidata.org/sparql", data=data,
        headers={"Accept":"application/sparql-results+json","User-Agent":UA,"Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)

fixed=0
for k in range(0,len(miss),400):
    batch=miss[k:k+400]
    vals=" ".join("wd:"+q for q in batch)
    d=sparql(f"SELECT ?n ?l WHERE {{ VALUES ?n {{ {vals} }} ?n rdfs:label ?l. FILTER(LANG(?l)='en') }}")
    for b in d["results"]["bindings"]:
        q=b["n"]["value"].rsplit("/",1)[-1]
        if q in nodes: nodes[q][0]=b["l"]["value"]; fixed+=1
    time.sleep(1)
print(f"labels fixed: {fixed}")
for q in ["Q9061","Q9312","Q9358","Q48301"]:
    if q in nodes: print(f"  {q} -> {nodes[q][0]}")
still=[q for q,v in nodes.items() if unlabeled(q,v)]
print(f"still unlabeled (no en label on Wikidata): {len(still)}")
json.dump(S, open(os.path.join(TOY,"tree_spine.json"),"w"), separators=(",",":"))
print("saved tree_spine.json")
