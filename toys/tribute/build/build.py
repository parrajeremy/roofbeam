#!/usr/bin/env python3
"""Build the Tribute data pack: federal individual tax liability by state / county / ZIP.

Sources (all IRS SOI TY2022 + Census 2023 geo):
  - county: https://www.irs.gov/pub/irs-soi/22incyallagi.csv   (A10300 total tax liability, A00100 AGI, N1 returns)
  - zip:    https://www.irs.gov/pub/irs-soi/22zpallagi.csv
  - ZCTA centroids: Census 2023 gazetteer
  - boundaries: us-atlas counties-10m.json (nation/states/counties topojson)

Amounts in SOI are $thousands -> multiplied to dollars here. Measure = A10300 (total tax
liability: income tax + SE tax + AMT etc.), the fullest individual federal tribute.
Output: ../tribute.json  and  ../us.json
"""
import csv, io, json, os, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # toys/tribute/
COUNTY_URL = "https://www.irs.gov/pub/irs-soi/22incyallagi.csv"
ZIP_URL = "https://www.irs.gov/pub/irs-soi/22zpallagi.csv"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_zcta_national.zip"
ATLAS_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json"

def fetch(url, path, binary=False):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  cached {os.path.basename(path)} ({os.path.getsize(path):,} b)"); return
    print(f"  downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())
    print(f"    -> {os.path.getsize(path):,} b")

STATE_NAMES = {
 "01":"Alabama","02":"Alaska","04":"Arizona","05":"Arkansas","06":"California","08":"Colorado",
 "09":"Connecticut","10":"Delaware","11":"District of Columbia","12":"Florida","13":"Georgia",
 "15":"Hawaii","16":"Idaho","17":"Illinois","18":"Indiana","19":"Iowa","20":"Kansas","21":"Kentucky",
 "22":"Louisiana","23":"Maine","24":"Maryland","25":"Massachusetts","26":"Michigan","27":"Minnesota",
 "28":"Mississippi","29":"Missouri","30":"Montana","31":"Nebraska","32":"Nevada","33":"New Hampshire",
 "34":"New Jersey","35":"New Mexico","36":"New York","37":"North Carolina","38":"North Dakota","39":"Ohio",
 "40":"Oklahoma","41":"Oregon","42":"Pennsylvania","44":"Rhode Island","45":"South Carolina",
 "46":"South Dakota","47":"Tennessee","48":"Texas","49":"Utah","50":"Vermont","51":"Virginia",
 "53":"Washington","54":"West Virginia","55":"Wisconsin","56":"Wyoming"}

def f(x):
    try: return float(x)
    except: return 0.0

def main():
    cpath = os.path.join(HERE, "22incyallagi.csv")
    zpath = os.path.join(HERE, "22zpallagi.csv")
    gpath = os.path.join(HERE, "gaz_zcta.zip")
    apath = os.path.join(OUT, "us.json")
    print("== fetch ==")
    fetch(COUNTY_URL, cpath); fetch(ZIP_URL, zpath); fetch(GAZ_URL, gpath); fetch(ATLAS_URL, apath)

    # --- county file -> states (COUNTYFIPS==000) + counties ---
    print("== county/state aggregate ==")
    states = {}   # fips2 -> [tax, agi, ret]
    counties = {} # fips5 -> [tax, agi, ret]
    cnames = {}   # fips5 -> county name
    with open(cpath, newline="", encoding="latin-1") as fh:
        r = csv.DictReader(fh)
        for row in r:
            sf = row["STATEFIPS"].zfill(2); cf = row["COUNTYFIPS"].zfill(3)
            tax = f(row["A10300"]) * 1000.0; agi = f(row["A00100"]) * 1000.0; ret = f(row["N1"])
            if cf == "000":
                a = states.setdefault(sf, [0.0,0.0,0.0])
            else:
                a = counties.setdefault(sf+cf, [0.0,0.0,0.0])
                cnames[sf+cf] = (row.get("COUNTYNAME") or "").strip()
            a[0]+=tax; a[1]+=agi; a[2]+=ret
    print(f"  states={len(states)} counties={len(counties)}")

    # --- zip file -> per zipcode (exclude 00000 / 99999 pseudo) ---
    print("== zip aggregate ==")
    zips = {}  # zip5 -> [tax, agi, ret]
    with open(zpath, newline="", encoding="latin-1") as fh:
        r = csv.DictReader(fh)
        for row in r:
            z = row["zipcode"].zfill(5)
            if z in ("00000","99999"): continue
            tax = f(row["A10300"]) * 1000.0; agi = f(row["A00100"]) * 1000.0; ret = f(row["N1"])
            a = zips.setdefault(z, [0.0,0.0,0.0]); a[0]+=tax; a[1]+=agi; a[2]+=ret
    print(f"  zips with data={len(zips)}")

    # --- ZCTA centroids ---
    print("== zcta centroids ==")
    cent = {}
    with zipfile.ZipFile(gpath) as zf:
        name = [n for n in zf.namelist() if n.lower().endswith(".txt")][0]
        data = zf.read(name).decode("latin-1")
    rr = csv.DictReader(io.StringIO(data), delimiter="\t")
    for row in rr:
        row = { (k or "").strip(): (v or "").strip() for k,v in row.items() }
        gid = (row.get("GEOID") or "").zfill(5)
        try: cent[gid] = [round(float(row["INTPTLONG"]),4), round(float(row["INTPTLAT"]),4)]
        except: pass
    print(f"  centroids={len(cent)}")

    # --- emit ---
    print("== emit ==")
    def pack3(a): return [round(a[0]), round(a[1]), round(a[2])]  # tax$, agi$, returns
    zip_rows = []
    matched = 0
    for z, a in zips.items():
        c = cent.get(z)
        if not c: continue
        matched += 1
        zip_rows.append([z, c[0], c[1], round(a[0]), round(a[1]), round(a[2])])
    out = {
        "meta": {
            "measure": "A10300 total individual federal tax liability (income tax + SE tax + AMT etc.)",
            "source": "IRS SOI TY2022 (county 22incyallagi, zip 22zpallagi); Census 2023 ZCTA centroids",
            "dollars": True, "year": 2022,
            "note": "Individual (Form 1040) only. Excludes payroll (FICA), corporate, and excise taxes.",
        },
        "states": {sf: [STATE_NAMES.get(sf, sf)] + pack3(a) for sf, a in states.items()},
        "counties": {fp: [cnames.get(fp, fp)] + pack3(a) for fp, a in counties.items()},
        "zips": zip_rows,
    }
    with open(os.path.join(OUT, "tribute.json"), "w") as fo:
        json.dump(out, fo, separators=(",",":"))
    sz = os.path.getsize(os.path.join(OUT, "tribute.json"))
    print(f"  wrote tribute.json ({sz:,} b): {len(out['states'])} states, {len(counties)} counties, {matched} zips (of {len(zips)} with data)")
    print("  wrote us.json (topojson)")

if __name__ == "__main__":
    main()
