"""Verify augment.json (I'm the quality gate) and merge it two-toned into the spine."""
import json, os, collections
HERE=os.path.dirname(os.path.abspath(__file__)); TOY=os.path.dirname(HERE)
S=json.load(open(os.path.join(TOY,"tree_spine.json")))
A=json.load(open(os.path.join(HERE,"augment.json")))
sn=S["nodes"]; se=set(tuple(e) for e in S["edges"])
an=A["nodes"]; ae=A["edges"]
CLADES={"religion","philosophy","social","science","history","scholar"}
CONF={"documented","consensus","contested","inferred-oral"}

# --- validate ---
prob=[]
for q,n in an.items():
    if not n.get("label"): prob.append(f"node {q} no label")
    if n.get("clade") not in CLADES: prob.append(f"node {q} bad clade {n.get('clade')}")
    if not n.get("source"): prob.append(f"node {q} no source")
labels={**{q:v[0] for q,v in sn.items()}, **{q:n["label"] for q,n in an.items()}}
selfloop=danglefrom=dangleto=nosrc=badconf=0
conf=collections.Counter()
for e in ae:
    f,t=e.get("from"),e.get("to")
    if f==t: selfloop+=1
    if f not in labels: danglefrom+=1
    if t not in labels: dangleto+=1
    if not e.get("source"): nosrc+=1
    if e.get("confidence") not in CONF: badconf+=1
    conf[e.get("confidence")]+=1
print(f"nodes: {len(an)} authored | edges: {len(ae)}")
print(f"confidence: {dict(conf)}")
print(f"CHECKS  self-loops={selfloop} dangling_from={danglefrom} dangling_to={dangleto} no-source={nosrc} bad-confidence={badconf} node-problems={len(prob)}")
if prob[:5]: print("  ", prob[:5])
touch=sum(1 for e in ae if e["from"] in sn or e["to"] in sn)
between=sum(1 for e in ae if e["from"] in sn and e["to"] in sn)
print(f"edges touching a spine node: {touch} | wholly between two spine nodes: {between}")

# --- spot-check marquee chains (resolve labels; verify direction from=influenced -> to=ancestor) ---
def lab(q): return labels.get(q, q+"(?)")
aeset={(e["from"],e["to"]) for e in ae}
allE=se|aeset
def has(a,b): return (a,b) in allE
print("\nMARQUEE EDGE CHECK (influenced <- ancestor; label resolves confirm Q-id correctness):")
chains=[("Q9438","Q160556","Aquinas<-Averroes"),("Q160556","Q8011","Averroes<-Avicenna"),
        ("Q8011","Q59138","Avicenna<-al-Farabi"),("Q127398","Q8011","Maimonides<-Avicenna"),
        ("Q9358","Q38193","Nietzsche<-Schopenhauer"),("Q38193","Q9068","Schopenhauer<-(Kant/ctrl)")]
for a,b,desc in chains:
    print(f"  {desc:26} {lab(a):24} <- {lab(b):24} : {'YES' if has(a,b) else 'no'}")
# Amenemope->Proverbs (authored ids)
prov=[e for e in ae if 'proverb' in lab(e['from']).lower() or 'amenemope' in lab(e['to']).lower()]
for e in prov[:3]: print(f"  Amenemope check: {lab(e['from'])} <- {lab(e['to'])}  [{e['confidence']}]  src={e['source'][:40]}")

# --- connectivity gain: largest component spine-only vs merged ---
def largest(edges, nodeset):
    adj=collections.defaultdict(set)
    for a,b in edges:
        if a in nodeset and b in nodeset: adj[a].add(b); adj[b].add(a)
    seen=set(); best=0
    for n in nodeset:
        if n in seen: continue
        st=[n]; c=0
        while st:
            x=st.pop()
            if x in seen: continue
            seen.add(x); c+=1; st.extend(adj[x]-seen)
        best=max(best,c)
    return best
allnodes=set(sn)|set(an)
before=largest(se, set(sn))
after=largest(se|aeset, allnodes)
print(f"\nCONNECTIVITY  largest component: spine-only={before} ({100*before/len(sn):.0f}%)  ->  merged={after} ({100*after/len(allnodes):.0f}%)")

# --- merge two-toned ---
mn={}
for q,v in sn.items(): mn[q]={"label":v[0],"year":v[1],"clade":v[2],"src":"wikidata"}
for q,n in an.items():
    if q in mn: mn[q]["tradition"]=n.get("tradition"); mn[q]["src"]="both"
    else: mn[q]={"label":n["label"],"year":n.get("year"),"clade":n["clade"],"tradition":n.get("tradition"),"region":n.get("region"),"src":"authored"}
me=[{"f":a,"t":b,"src":"wikidata","conf":"documented"} for a,b in S["edges"]]
seen=set(map(tuple,S["edges"]))
for e in ae:
    if (e["from"],e["to"]) in seen: continue
    me.append({"f":e["from"],"t":e["to"],"src":"authored","conf":e["confidence"],"source":e.get("source")})
out={"meta":{"spine":"Wikidata P737 (documented)","augment":"deep-research, cited (authored)","two_toned":True,
     "note":"src: wikidata=documented spine, authored=research branch, both=augmented node."},
     "nodes":mn,"edges":me}
json.dump(out, open(os.path.join(TOY,"tree.json"),"w"), separators=(",",":"))
print(f"\nwrote tree.json: {len(mn)} nodes ({sum(1 for n in mn.values() if n['src']!='wikidata')} authored/both), {len(me)} edges")
