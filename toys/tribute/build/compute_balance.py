"""Compute + INSPECT the state balance of payments before visualizing.
Payer side  = IRS Data Book Table 5, Total Internal Revenue collections (all federal taxes).
Receiver side = USAspending FY2022 spending by state (place of performance).
Ratio = spending received per $1 of federal tax collected.  >1 = net receiver, <1 = net payer.
"""
import json, os
from xlsx import read
HERE=os.path.dirname(os.path.abspath(__file__))

AB={"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
"Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI",
"Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
"Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
"Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ",
"New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
"Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
"Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
"West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"}
POP={"AL":5074,"AK":733,"AZ":7359,"AR":3046,"CA":39029,"CO":5840,"CT":3626,"DE":1018,"DC":671,"FL":22245,
"GA":10912,"HI":1440,"ID":1939,"IL":12582,"IN":6833,"IA":3200,"KS":2937,"KY":4512,"LA":4590,"ME":1385,
"MD":6164,"MA":6982,"MI":10034,"MN":5717,"MS":2940,"MO":6178,"MT":1123,"NE":1967,"NV":3178,"NH":1395,
"NJ":9261,"NM":2113,"NY":19677,"NC":10698,"ND":779,"OH":11756,"OK":4019,"OR":4240,"PA":12972,"RI":1094,
"SC":5283,"SD":909,"TN":7051,"TX":30029,"UT":3381,"VT":647,"VA":8684,"WA":7786,"WV":1775,"WI":5893,"WY":581}

# collections (payer) by abbr
rows=read(os.path.join(HERE,"irs_collections.xlsx"))
coll={}
for r in rows:
    nm=str(r[0]).strip()
    if nm in AB and len(r)>1 and isinstance(r[1],float):
        coll[AB[nm]]=r[1]*1000.0
# spending (receiver) by abbr
sp={}
for x in json.load(open(os.path.join(HERE,"spending_pop.json")))["results"]:
    sp[x["shape_code"]]=x["aggregated_amount"]

rec=[]
for ab in POP:
    if ab in coll and ab in sp and coll[ab]>0:
        c=coll[ab]; s=sp[ab]; p=POP[ab]*1000
        rec.append({"ab":ab,"coll":c,"sp":s,"ratio":s/c,"net_pc":(s-c)/p})
tc=sum(r["coll"] for r in rec); ts=sum(r["sp"] for r in rec)
print(f"NATIONAL: collections=${tc/1e12:.2f}T  spending(USAspending)=${ts/1e12:.2f}T  ratio={ts/tc:.2f}")
print(f"  (USAspending place-of-perf undercounts outlays ~$6.3T -> national ratio biased low; read RELATIVE)\n")
rec.sort(key=lambda r:-r["ratio"])
print("TOP RECEIVERS ($ back per $1 paid):")
for r in rec[:8]: print(f"  {r['ab']}  {r['ratio']:.2f}   net/capita ${r['net_pc']:>8,.0f}")
print("TOP PAYERS:")
for r in rec[-8:]: print(f"  {r['ab']}  {r['ratio']:.2f}   net/capita ${r['net_pc']:>8,.0f}")
print("\nANOMALY CHECK (attribution-distorted):")
for ab in ["DC","DE","VA","MD","MN","NM","WV","MS","CT","NJ"]:
    r=[x for x in rec if x["ab"]==ab]
    if r: r=r[0]; print(f"  {ab}  ratio={r['ratio']:.2f}  coll=${r['coll']/1e9:.0f}B  sp=${r['sp']/1e9:.0f}B")
