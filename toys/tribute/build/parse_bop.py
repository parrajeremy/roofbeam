"""Parse Rockefeller BoP report Table 1 (9-yr avg balance of payments, $M, with/without COVID).
Take the WITHOUT-COVID column (robust, ex-pandemic distortion) as the state balance.
Convert to per-capita with 2022 population. Emit balance.json + validate.
"""
import re, subprocess, os, json
HERE=os.path.dirname(os.path.abspath(__file__))
from compute_balance import AB, POP  # name->abbr, abbr->pop(thousands)

txt=subprocess.run(["pdftotext","-layout",os.path.join(HERE,"rockefeller_bop.pdf"),"-"],
                   capture_output=True,text=True).stdout
NAMES=sorted(AB, key=len, reverse=True)
money=re.compile(r"\(\$[\d,]+\)|\$[\d,]+")
def num(tok):
    neg=tok.startswith("("); v=float(re.sub(r"[^\d]","",tok)); return -v if neg else v

bal={}  # abbr -> bop_m (without covid, $millions)
for line in txt.splitlines():
    s=line.strip()
    nm=next((n for n in NAMES if s.startswith(n)), None)
    if not nm: continue
    toks=money.findall(s)
    if len(toks)>=2:
        ab=AB[nm]
        if ab not in bal:  # first occurrence = Table 1
            bal[ab]=num(toks[1])  # 2nd money col = without-COVID
print(f"parsed {len(bal)} states")
rows=[]
for ab,m in bal.items():
    pop=POP[ab]*1000
    rows.append({"ab":ab,"bop_m":m,"pc":m*1e6/pop})
rows.sort(key=lambda r:-r["pc"])
print("\nTOP per-capita RECEIVERS (9yr avg, ex-COVID):")
for r in rows[:6]: print(f"  {r['ab']}  ${r['pc']:>8,.0f}/person   (${r['bop_m']/1000:,.1f}B total)")
print("TOP per-capita PAYERS:")
for r in rows[-6:]: print(f"  {r['ab']}  ${r['pc']:>8,.0f}/person   (${r['bop_m']/1000:,.1f}B total)")
print("\nvalidation vs USAspending artifacts:")
for ab in ["MN","CT","ND","NJ","VA","NM","MA","WA"]:
    r=next((x for x in rows if x["ab"]==ab),None)
    if r: print(f"  {ab}: ${r['pc']:,.0f}/person  ({'RECEIVER' if r['pc']>0 else 'PAYER'})")
# emit — keyed by 2-digit state FIPS so it joins the topojson directly
ABFIPS={"AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11",
"FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21","LA":"22",
"ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31","NV":"32",
"NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41","PA":"42",
"RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54",
"WI":"55","WY":"56"}
out={ABFIPS[ab]:{"ab":ab,"bop_m":round(bal[ab]),"pc":round(bal[ab]*1e6/(POP[ab]*1000))} for ab in bal}
json.dump({"meta":{"source":"Rockefeller Institute, Giving or Getting? (8th ed.) — 9-year average (FY2015-2023) balance of payments, EXCLUDING COVID relief. Per capita = avg annual balance / 2022 population.","year":"2015-2023 avg (ex-COVID)"},"states":out},
          open(os.path.join(HERE,"..","balance.json"),"w"), separators=(",",":"))
print(f"\nwrote balance.json ({len(out)} states, keyed by FIPS)")
