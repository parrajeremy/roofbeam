"""Induce the 'thought' subgraph: keep nodes with an intellectual occupation, assign a clade."""
import json, os, collections
HERE=os.path.dirname(os.path.abspath(__file__))
G=json.load(open(os.path.join(HERE,"..","graph.json")))
occ={q:set(v) for q,v in json.load(open(os.path.join(HERE,"occ.json"))).items()}

# clade keyword sets, in priority order (first match wins)
CLADES=[
 ("religion",["theolog","priest","monk","nun","friar","abbot","bishop","pope","cardinal","rabbi",
              "imam","mufti","ayatollah","mystic","prophet","saint","cleric","religious","sufi","guru"]),
 ("philosophy",["philosoph","logician"]),
 ("social",["econom","sociolog","anthropolog","psycholog","political scien","social scien",
            "jurist","legal schol","linguist","philolog","pedagog"]),
 ("science",["scientist","physicist","mathematic","biolog","chemist","astronom","naturalist",
             "physician","cosmolog","geolog"]),
 ("history",["histori"]),
 ("scholar",["scholar","orientalist","philosopher of"]),
]
def clade(os_):
    low=[o.lower() for o in os_]
    for name,kws in CLADES:
        if any(any(k in o for k in kws) for o in low): return name
    return None

keep={}
for q,(label,year) in G["nodes"].items():
    c=clade(occ.get(q,[]))
    if c: keep[q]=[label,year,c]
E=[[a,b] for a,b in G["edges"] if a in keep and b in keep]
print(f"thinkers kept: {len(keep)} of {len(G['nodes'])} | edges in subgraph: {len(E)}")
fc=collections.Counter(v[2] for v in keep.values())
print("clades:", dict(fc.most_common()))
yrs=[v[1] for v in keep.values() if v[1] is not None]
print(f"year coverage: {sum(1 for v in keep.values() if v[1] is not None)}/{len(keep)}  range {min(yrs)}..{max(yrs)}")

# largest component
adj=collections.defaultdict(set)
for a,b in E: adj[a].add(b); adj[b].add(a)
seen=set(); big=[]
for n in keep:
    if n in seen: continue
    st=[n]; comp=[]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x); comp.append(x); st.extend(adj[x]-seen)
    if len(comp)>len(big): big=comp
print(f"largest connected component: {len(big)} thinkers ({100*len(big)/len(keep):.0f}%)")

# top ancestors — should now be thinkers, not pop culture
lab={q:v[0] for q,v in keep.items()}
indeg=collections.Counter(b for a,b in E)
print("most-named intellectual ancestors:")
for q,c in indeg.most_common(15):
    y=keep[q][1]; print(f"  {c:4}  {lab.get(q,q):28} {keep[q][2]:11} ({y if y else '?'})")

out={"meta":{"source":"Wikidata P737 'influenced by' (pulled 2026-09-13), scoped to intellectual occupations.",
     "honesty":"Sparse + biased toward well-documented Western/modern thinkers; pre-writing thought absent by construction (the evidence-horizon root). Edge [a,b] = a influenced-by b.",
     "clades":list(dict(fc).keys())},
     "nodes":keep, "edges":E}
json.dump(out, open(os.path.join(HERE,"..","tree_spine.json"),"w"), separators=(",",":"))
print(f"wrote tree_spine.json ({os.path.getsize(os.path.join(HERE,'..','tree_spine.json')):,} b)")
