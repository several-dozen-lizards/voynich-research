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
def final_settings():
    out=[]
    for agg in [.65,.8,.9,1.]:
        for mode,fraction in [('sigla_only',None),('subset25',.25)]:
            for rigidity in [0.,1.]:
                out.append(dict(setting=f'T{len(out):02d}',mode=mode,fraction=fraction,sequence_length=2,slot_rigidity=rigidity,aggressiveness=agg,old_reference=None,role='terminal'))
    return out
def settings():
    out=final_settings()
    for name in ['C15_Italian_52','C15_Italian_78','C15_Latin_52','C15_Latin_78','C9','C18_bigraph2','C18_addB']:
        out.append(dict(setting=name,mode=name,fraction=None,sequence_length=None,slot_rigidity=None,aggressiveness=None,old_reference=None,role='comparison'))
    return out+json.loads((R/'HISTORICAL_SETTINGS.json').read_text())
def tensor_fingerprint(prepared,config):
    h=hashlib.sha256();h.update(json.dumps(dict(vocabulary=prepared['vocabulary'],training=config),sort_keys=True).encode())
    for k in ['train','validation','test']:
        a=prepared['tensors'][k].numpy();h.update(str(a.shape).encode());h.update(a.tobytes());h.update(prepared['escape'][k].tobytes());h.update(str(prepared['character_counts'][k]).encode())
    return h.hexdigest()
