import json, os, collections, re
TOY=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T=json.load(open(os.path.join(TOY,"tree.json")))
N=T["nodes"]; E=[(e["f"],e["t"]) for e in T["edges"]]; Eset=set(E)
byid={q:n["label"] for q,n in N.items()}
def find(sub):
    sub=sub.lower(); return [q for q,n in N.items() if sub in (n["label"] or "").lower()]
def one(sub):
    r=find(sub); return r[0] if r else None
def has(a,b): return (a,b) in Eset

print("=== MARQUEE CHAIN, verified BY LABEL (influenced <- ancestor) ===")
chain=["Aristotle","al-Far","Avicenna","Averroes","Aquinas"]
ids={c:one(c) for c in chain}
print("  resolved:", {c:(ids[c],byid.get(ids[c])) for c in chain})
pairs=[("Aquinas","Averroes"),("Averroes","Avicenna"),("Avicenna","al-Far"),("Avicenna","Aristotle"),
       ("Aquinas","Avicenna"),("Aquinas","Aristotle")]
for a,b in pairs:
    ia,ib=ids.get(a) or one(a), ids.get(b) or one(b)
    print(f"  {byid.get(ia,a):20} <- {byid.get(ib,b):20}: {'YES' if ia and ib and has(ia,ib) else 'no'}")
for a,b in [("Nietzsche","Schopenhauer"),("Schopenhauer","Buddha"),("Emerson","Thoreau"),
            ("Thoreau","Emerson"),("Leibniz","Confucius"),("Proverbs","Amenemope"),
            ("Aquinas","Maimonides"),("Tsongkhapa","Nagarjuna")]:
    ia,ib=one(a),one(b)
    ok='YES' if ia and ib and has(ia,ib) else ('no' if ia and ib else 'MISSING NODE')
    print(f"  {a:14} <- {b:14}: {ok}  ({byid.get(ia,'?')} <- {byid.get(ib,'?')})")

print("\n=== CONNECTIVITY (honest) ===")
adj=collections.defaultdict(set)
for a,b in E: adj[a].add(b); adj[b].add(a)
def comps(edges):
    ad=collections.defaultdict(set)
    for a,b in edges: ad[a].add(b); ad[b].add(a)
    seen=set(); cs=[]
    for n in N:
        if n in seen: continue
        st=[n]; c=[]
        while st:
            x=st.pop()
            if x in seen: continue
            seen.add(x); c.append(x); st.extend(ad[x]-seen)
        cs.append(c)
    return cs
spine_edges=[(e["f"],e["t"]) for e in T["edges"] if e["src"]=="wikidata"]
cs_before=comps(spine_edges); cs_after=comps(E)
nontrivial=lambda cs: sum(1 for c in cs if len(c)>=3)
print(f"  components (size>=3): before={nontrivial(cs_before)}  after={nontrivial(cs_after)}")
cs_after.sort(key=len,reverse=True)
print("  largest components after merge (id count · a few members):")
for c in cs_after[:8]:
    labs=[byid[q] for q in c[:6] if byid.get(q)]
    print(f"    {len(c):5}  {', '.join(labs[:5])}")
