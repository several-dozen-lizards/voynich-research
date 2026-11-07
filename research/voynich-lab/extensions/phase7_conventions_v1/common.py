from pathlib import Path
import sys,json,csv,hashlib,random,math,statistics,re,gzip,pickle
from collections import Counter,defaultdict
R=Path(__file__).resolve().parent;LAB=R.parents[1];OLD=R.parent/'phase7_two_table_v1'
sys.path.insert(0,str(LAB));sys.path.insert(0,str(LAB/'.analysis-runtime'));sys.path.insert(0,str(LAB/'.runtime'))
SEEDS=[1729,1733,1741,1753,1777]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,allow_nan=False)+'\n',encoding='utf8')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for x in rows for k in x)));w.writeheader();w.writerows(rows)
def sid(*args):return int.from_bytes(hashlib.sha256(':'.join(map(str,args)).encode()).digest()[:8],'big')
def page(folio):return re.match(r'f\d+[rv]',folio)[0]
def leaf(folio):return int(re.match(r'f(\d+)',folio)[1])
def physical():return json.loads((R/'PHYSICAL.json').read_text())
def pages(rows):
    by=defaultdict(list)
    for row in rows:by[page(row['folio'])].append(row)
    return [dict(page=p,leaf=leaf(p),rows=rs) for p,rs in sorted(by.items(),key=lambda x:(leaf(x[0]),x[0]))]
def verify():
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items()),'Registration drift'
def gzwrite(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(p,'wt',encoding='utf8') as f:json.dump(value,f)
def gzread(p):
    with gzip.open(p,'rt',encoding='utf8') as f:return json.load(f)
