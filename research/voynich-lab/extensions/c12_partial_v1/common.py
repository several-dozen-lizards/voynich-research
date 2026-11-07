from pathlib import Path
import sys,json,csv,hashlib,os
R=Path(__file__).resolve().parent;LAB=R.parents[1];I=R/'instrument'
sys.path.insert(0,str(I));sys.path.insert(0,str(LAB/'.analysis-runtime'));sys.path.insert(0,str(LAB/'.runtime'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=True,allow_nan=False)+'\n',encoding='utf8')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def typed(rows):return [{**r,'is_para_start':None if r.get('is_para_start','')=='' else r['is_para_start']=='True'} for r in rows]
def table(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def settings():
    out=[dict(setting='P00',mode='paired_zero',fraction=0.,sequence_length=1,slot_rigidity=0.,old_reference=None)]
    for mode,fraction in [('sigla_only',None),('subset25',.25),('subset50',.5),('subset75',.75),('full',1.)]:
        for li,l in enumerate([2,3,4]):
            for ri,r in enumerate([0.,.5,1.]):out.append(dict(setting=f'P{len(out):02d}',mode=mode,fraction=fraction,sequence_length=l,slot_rigidity=r,old_reference=f'SW{9+li*3+ri:02d}' if mode=='full' else None))
    out.append(dict(setting=f'P{len(out):02d}',mode='C5_external',fraction=0.,sequence_length=1,slot_rigidity=0.,old_reference='SW04'))
    return out
def tensor_fingerprint(prepared,config):
    h=hashlib.sha256();h.update(json.dumps(dict(vocabulary=prepared['vocabulary'],training=config),sort_keys=True).encode())
    for k in ['train','validation','test']:
        a=prepared['tensors'][k].numpy();h.update(str(a.shape).encode());h.update(a.tobytes());h.update(prepared['escape'][k].tobytes());h.update(str(prepared['character_counts'][k]).encode())
    return h.hexdigest()
