from pathlib import Path
import collections,hashlib,importlib.util,json,re
import numpy as np
from engine import run
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
if load(R/'QUALIFICATION.json')['status']!='PASS':raise SystemExit('Gap counter/numerical qualification failed: no manuscript gap scoring.')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','qualify.py','run.py'] else P/n).read_bytes()).hexdigest()==h
spec=importlib.util.spec_from_file_location('maxT',P/'opening-maxT-qualification-v77/method.py');method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
old=load(P/'opening-order-audit-v75/RESULTS.json');raw=load(P/'frequency-atlas-v48/rows.json');panels=[];observed=[]
chosen=[p for p in old['panels'] if (p['section'],p['hand'],p['variety'],p['format']) in [('Balneological','2','B','P'),('Starred paragraphs','3','B','P')]];assert len(chosen)==4
for prior in chosen:
 tr=prior['reading'];key=(prior['section'],prior['hand'],prior['variety'],prior['format']);rr=[r for r in raw if tuple(r[2:6])==key];ls={t:{r[6] for r in rr if r[0]==t} for t in ['H','F']};shared=ls['H']&ls['F'];rows=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in rr if r[0]==tr and r[6] in shared]
 idx=prior['panel_index'];print('START',idx,tr,key,flush=True);p,scores,cells,col,sign=run(rows,4999,7800+idx,lambda b:print('progress',idx,b,flush=True));assert p['labels']==prior['labels']
 for mode,sc in scores.items():
  mean,sd,mx=method.maximums(sc);result=method.target_result(sc,col,sign,mx,mean,sd,28);out=dict(original_panel_index=idx,reading=tr,section=key[0],hand=key[1],variety=key[2],format=key[3],view=mode,class_pairs=len(p['ia']),lines=len(rows),folios=len({r['folio'] for r in rows}),cells=cells[mode],result=result)
  panels.append(out);np.savez_compressed(R/(f'panel-{idx:02d}-{mode}-null.npz'),scores=sc,mean=mean,sd=sd,maxima=mx);print('DONE',idx,mode,result,flush=True)
 ev=[];folios={r['folio']:dict(forward=0,reverse=0,neutral_forward=0,neutral_reverse=0) for r in rows};unknown=0;middle=collections.defaultdict(lambda:collections.Counter())
 for r in rows:
  ws=r['tokens']
  for i in range(len(ws)-2):
   a,m,b=ws[i:i+3]
   if a is None or b is None:continue
   f=a.startswith('sh') and b.startswith('qok');rev=a.startswith('qok') and b.startswith('sh')
   if not(f or rev):continue
   if m is None:unknown+=1;continue
   neutral=not m.startswith(('sh','qok'));orientation='forward' if f else 'reverse';folios[r['folio']][orientation]+=1
   if neutral:folios[r['folio']]['neutral_'+orientation]+=1
   middle[m][orientation]+=1;ev.append(dict(r,ordinal=i+1,first=a,middle=m,last=b,orientation=orientation,neutral_middle=neutral))
 observed.append(dict(original_panel_index=idx,reading=tr,section=key[0],hand=key[1],events=ev,folios=folios,unknown_middle_excluded=unknown,middle_words={w:dict(v) for w,v in sorted(middle.items())}))
save('RESULTS.json',dict(qualification='PASS before manuscript gap scoring',protocol=load(R/'PROTOCOL.json'),panels=panels,observed=observed));save('SUMMARY.json',panels)
