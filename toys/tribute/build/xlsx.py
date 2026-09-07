"""Minimal xlsx reader (no deps): returns sheet as list-of-rows of cell values."""
import zipfile, re, xml.etree.ElementTree as ET
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def colnum(ref):
    m=re.match(r"([A-Z]+)(\d+)",ref); c=m.group(1); n=0
    for ch in c: n=n*26+(ord(ch)-64)
    return n-1, int(m.group(2))-1
def read(path, sheet="xl/worksheets/sheet1.xml"):
    z=zipfile.ZipFile(path)
    shared=[]
    if "xl/sharedStrings.xml" in z.namelist():
        r=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in r.findall("m:si",NS):
            shared.append("".join(t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
    root=ET.fromstring(z.read(sheet)); rows=[]
    for row in root.find("m:sheetData",NS).findall("m:row",NS):
        cells={}
        for c in row.findall("m:c",NS):
            ci,ri=colnum(c.get("r")); t=c.get("t"); v=c.find("m:v",NS)
            if v is None: val=""
            elif t=="s": val=shared[int(v.text)]
            else:
                try: val=float(v.text)
                except: val=v.text
            cells[ci]=val
        if cells:
            w=max(cells)+1; rows.append([cells.get(i,"") for i in range(w)])
    return rows
if __name__=="__main__":
    import sys
    rows=read(sys.argv[1])
    for i,r in enumerate(rows[:60]):
        cells=[f"{j}:{str(v)[:26]}" for j,v in enumerate(r) if v!="" ]
        if cells: print(i, "|".join(cells))
