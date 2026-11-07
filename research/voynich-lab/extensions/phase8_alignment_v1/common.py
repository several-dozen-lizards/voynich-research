from pathlib import Path
import sys,os,json,csv,hashlib,random,math,statistics,pickle,gzip,re
from collections import Counter,defaultdict
R=Path(__file__).resolve().parent;LAB=R.parents[1];P7=R.parent/'phase7_two_table_v1';P7C=R.parent/'phase7_conventions_v1'
sys.dont_write_bytecode=True
sys.path.insert(0,str(LAB));sys.path.insert(0,str(LAB/'.analysis-runtime'));sys.path.insert(0,str(LAB/'.runtime'))
DEV=[1861,1867,1871,1873,1877];QUAL=[1729,1733,1741,1753,1777];NODES=48
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def sid(*parts):return int.from_bytes(hashlib.sha256(':'.join(map(str,parts)).encode()).digest()[:8],'big')
def leaf(p):return int(re.match(r'f(\d+)',p)[1])
def side(p):return re.match(r'f\d+[rv]',p)[0]
def verify():
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items()),'Frozen source/input drift'
def facts():return json.loads((R/'PHYSICAL.json').read_text())
def folds():return json.loads((R/'FOLDS.json').read_text())
def known_labels():return {int(k):v for k,v in json.loads((R/'AB_LEAVES.json').read_text()).items()}
def plan(stage):
    seeds=DEV if stage=='development' else QUAL;jobs=[]
    for base in ['C1','C2']:
        for orientation in [0,1]:
            for condition in ['SAME_ONE','SAME_TWO','DIFF_ONE','DIFF_TWO']:
                for seed in seeds:
                    for view in ['clean','noise']:jobs.append(dict(id=f'{stage}_{base}_o{orientation}_{condition}_s{seed}_{view}',stage=stage,base=base,orientation=orientation,condition=condition,seed=seed,view=view,fixture=False))
    if stage=='qualification':
        for base in ['C1','C2']:
            for orientation in [0,1]:
                for seed in QUAL:
                    for view in ['clean','noise']:jobs.append(dict(id=f'physical_{base}_o{orientation}_s{seed}_{view}',stage=stage,base=base,orientation=orientation,condition='SAME_TWO',seed=seed,view=view,fixture=True))
    return jobs
def category(condition):return 'DIFFERENT' if condition.startswith('DIFF') else 'ONE_KEY' if condition=='SAME_ONE' else 'SAME_TWO_KEYS'
