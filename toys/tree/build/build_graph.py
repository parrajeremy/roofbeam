"""Build the influence-graph spine from Wikidata P737 edges.
Node = thinker (Q-id, label, birth year). Edge = [influenced_qid, influencer_qid]
i.e. 'p was influenced by i' -> in the tree, i is the parent/ancestor of p.
Emits graph.json + a sanity report.
"""
import json, os, collections
HERE=os.path.dirname(os.path.abspath(__file__))
raw=json.load(open(os.path.join(HERE,"edges_raw.json")))["results"]["bindings"]

def qid(u): return u.rsplit("/",1)[-1]
def yr(b,k):
    if k in b:
        try: return int(b[k]["value"])
        except: return None
    return None

nodes={}   # qid -> {label, year}
edges=set()
def note(u,label,year):
    q=qid(u); n=nodes.setdefault(q,{"label":None,"year":None})
    if label and not n["label"]: n["label"]=label
    if year is not None and n["year"] is None: n["year"]=year

for b in raw:
    p=b["p"]["value"]; i=b["i"]["value"]
    note(p, b.get("pLabel",{}).get("value"), yr(b,"py"))
    note(i, b.get("iLabel",{}).get("value"), yr(b,"iy"))
    edges.add((qid(p), qid(i)))   # p influenced-by i

edges=sorted(edges)
withyr=sum(1 for n in nodes.values() if n["year"] is not None)
years=[n["year"] for n in nodes.values() if n["year"] is not None]
print(f"nodes={len(nodes)}  edges={len(edges)}  nodes_with_year={withyr} ({100*withyr/len(nodes):.0f}%)")
print(f"year range: {min(years)} .. {max(years)}")

# connected components (undirected) to find the main intellectual mass
adj=collections.defaultdict(set)
for a,b in edges: adj[a].add(b); adj[b].add(a)
seen=set(); comps=[]
for n in nodes:
    if n in seen: continue
    stack=[n]; comp=[]
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x); comp.append(x); stack.extend(adj[x]-seen)
    comps.append(comp)
comps.sort(key=len, reverse=True)
print(f"components: {len(comps)}  | largest={len(comps[0])} ({100*len(comps[0])/len(nodes):.0f}% of nodes)")

# sanity: known lineages (edge = influenced-by present?)
lab={q:(n["label"] or q) for q,n in nodes.items()}
def has(a,b): return (a,b) in edges
checks=[("Q859","Q913","Plato ← Socrates"),("Q868","Q859","Aristotle ← Plato"),
        ("Q9438","Q868","Aquinas ← Aristotle"),("Q9312","Q36740","Kant ← Hume"),
        ("Q619","Q859","Copernicus? (control)"),("Q1234","Q913","(control)")]
print("sanity (influenced-by edge present?):")
for a,b,desc in checks[:4]:
    print(f"  {desc:24} {lab.get(a,a)} ← {lab.get(b,b)}: {'YES' if has(a,b) else 'no'}")
# oldest / most-influential
indeg=collections.Counter(b for a,b in edges)  # how many were influenced BY this node
print("most-cited ancestors (in-degree = # who name them an influence):")
for q,c in indeg.most_common(12):
    y=nodes[q]["year"]; print(f"  {c:4}  {lab.get(q,q)}  ({y if y else '?'})")

out={"meta":{"source":"Wikidata P737 'influenced by', pulled 2026-09-13","note":"edge [a,b] = a was influenced by b (b is ancestor). Sparse/biased toward well-documented (Western, modern) thinkers — an honest floor, not the whole tree."},
     "nodes":{q:[n["label"],n["year"]] for q,n in nodes.items()},
     "edges":edges}
json.dump(out, open(os.path.join(HERE,"..","graph.json"),"w"), separators=(",",":"))
print(f"wrote graph.json ({os.path.getsize(os.path.join(HERE,'..','graph.json')):,} b)")
