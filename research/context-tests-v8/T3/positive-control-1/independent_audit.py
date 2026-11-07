from pathlib import Path
import json,sys,hashlib,importlib.util,collections,math
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;P=T.parent.parent;sys.path.insert(0,str(P/'system-types-v5'))
from core import group_inventory,group_rank_mapping,canonical_hash
spec=importlib.util.spec_from_file_location('positive_adapter',R/'generate_positive.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def segment(w):
 ps=['qok','qo','ot','ok','d','ch','sh','k','t','p','f','y','o','a','s'];es=['aiin','ain','air','ar','al','edy','eey','ey','y','ol','or'];op=max([p for p in ps if w.startswith(p)]+[''],key=len);rest=w[len(op):];end=max([s for s in es if rest.endswith(s)]+[''],key=len);core=rest[:-len(end)] if end else rest;return (op,core),end
source=load('SOURCE-ENTRIES.json')['entries'];cached=json.loads((T/'DISCOVERY-PARAGRAPHS.json').read_text());checks=[];panels=[]
for family,fi in [('G2',0),('G3',100)]:
 for scribe in ['1','2']:
  name=family+'-s'+scribe;seed=848200+fi+int(scribe);entries=[e for e in source if e['arm']=='DISCOVERY'];g=adapter.transformed(entries,family,seed);saved=load(name+'/DISCOVERY-TRANSFORM.json');assert g==saved;checks.append(name+' exact native generation replay')
  target=[w for p in cached if p['scribe']==scribe for w in p['tokens'] if w];inventory=group_inventory(target,max_atoms=3);assert inventory==load(name+'/INVENTORY.json');fit=[w for w in g['groups'] if w is not None];model=load(name+'/MODEL.json');receipt=group_rank_mapping(fit,inventory,seed=848300+fi+int(scribe));assert receipt==model['mapping'];assert canonical_hash(fit)==model['training_sha256'];checks.append(name+' discovery-only inventory and mapping replay')
  pp=load(name+'/DISCOVERY.json');flattened=[w for p in pp for w in p['tokens']];mapping=receipt['mapping'];expected=[None if w is None else ''.join(mapping[u] for u in w) for w in g['groups']];assert flattened==expected;checks.append(name+' exact slot-preserving transfer')
  data=[];allkeys=set()
  for p in pp:
   row=[segment(w) if w else None for w in p['tokens']];data.append(row)
   allkeys.update(s[0] for s in row[1:] if s)
  possible=[k for k in allkeys if sum(any(s and s[0]==k for s in row[1:]) for row in data)*2>=len(data)]
  candidates=0;closed_pass=0;pc_pass=0
  for k in possible:
   wordtypes={w for p,row in zip(pp,data) for w,s in zip(p['tokens'][1:],row[1:]) if s and s[0]==k}
   for lo in range(2,16):
    for hi in range(lo,16):
     inside=outside=ci=co=hit=0;variants=collections.Counter()
     for p,row in zip(pp,data):
      present=False
      for j,s in enumerate(row[1:],2):
       if s is None:continue
       iw=lo<=j<=hi
       if iw:inside+=1
       else:outside+=1
       if s[0]!=k:continue
       if iw:ci+=1;present=True;variants[p['tokens'][j-1] if len(wordtypes)==1 else s[1]]+=1
       else:co+=1
      hit+=present
     if not inside or not outside:continue
     ratio=(ci/inside)/(co/outside) if co else math.inf if ci else None
     if hit/len(pp)<.5 or ratio is None or ratio<2:continue
     pc_pass+=1;cum=0;closed=False
     if len(variants)>=4:
      for n,(v,c) in enumerate(sorted(variants.items(),key=lambda kv:(-kv[1],kv[0]))[:16],1):
       cum+=c
       if n>=4 and cum/ci>=.8:closed=True;break
     if closed:candidates+=1
  frozen=load(name+'/CANDIDATE-FREEZE.json')['discovery'];assert len(allkeys)==frozen['tested_classes'];assert candidates==0==frozen['eligible_candidates'];assert frozen['selected'] is None;assert not (R/name/'CONFIRMATION.json').exists();checks.append(name+' independent full criterion audit with presence-only pruning')
  panels.append(dict(cell=name,classes=len(allkeys),possible_presence_classes=len(possible),presence_and_concentration_windows=pc_pass,all_three_windows=candidates,confirmation_generated=False))
result=dict(status='PASS',scope='engineering/integrity audit; scientific positive FAIL',checks=checks,panels=panels,manuscript_confirmation_opened=False)
(R/'INDEPENDENT-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='PASS',checks=len(checks),panels=panels)))
