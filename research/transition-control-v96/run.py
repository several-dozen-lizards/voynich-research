from pathlib import Path
import collections,hashlib,json,re,sys
from engine import state,edges,score,distribution,convolve,assess,BudgetExceeded
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
if load(R/'QUALIFICATION.json')['status']!='PASS':raise SystemExit('Conditional-control qualification failed; manuscript not accessed.')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','qualify.py','run.py'] else P/n).read_bytes()).hexdigest()==h
raw=load(P/'frequency-atlas-v48/rows.json');old=load(P/'opening-order-audit-v75/RESULTS.json');meta=[p for p in old['panels'] if (p['section'],p['hand'],p['variety'],p['format']) in [('Balneological','2','B','P'),('Starred paragraphs','3','B','P')]];assert len(meta)==4
panels=[];nulls=[]
for p in meta:
 idx=p['panel_index'];tr=p['reading'];rr=[r for r in raw if tuple(r[2:6])==(p['section'],p['hand'],p['variety'],p['format'])];loci={t:{r[6] for r in rr if r[0]==t} for t in ['H','F']};shared=loci['H']&loci['F'];rr=[r for r in rr if r[0]==tr and r[6] in shared];spanrecs=[];spans=[]
 for r in rr:
  begin=0
  for i in range(len(r[7])+1):
   if i<len(r[7]) and r[7][i] is not None:continue
   ws=r[7][begin:i]
   if ws:spans.append((r,begin,ws))
   begin=i+1
 print('START',idx,tr,'spans',len(spans),flush=True)
 panel=dict(original_panel_index=idx,reading=tr,section=p['section'],hand=p['hand'],variety=p['variety'],format=p['format'],opening_pairs=p['class_pairs'],rows=len(rr),spans=len(spans),views=[],status='complete')
 for neutral in [False,True]:
  view='non_target_middle' if neutral else 'any_middle';poly={0:1};observed=0;variable=0;movable=0;records=[]
  try:
   for si,(r,begin,ws) in enumerate(spans):
    seq=tuple(map(state,ws));ec=edges(seq);dist,calls=distribution(seq[0],seq[-1],ec,neutral);d=score(seq,neutral);assert dist.get(d,0)>0
    observed+=d;variable+=len(dist)>1;movable+=sum(dist.values())>1;poly=convolve(poly,dist)
    records.append(dict(locator=r[6],folio=re.match(r'f\d+',r[1])[0],start_ordinal=begin+1,tokens=ws,classes=list(seq),adjacent_class_counts=list(ec),observed_D=d,class_paths_hex=hex(sum(dist.values())),score_support={str(k):hex(v) for k,v in dist.items()},memo_states=calls))
    if (si+1)%250==0:print(idx,view,si+1,'support',len(poly),flush=True)
  except BudgetExceeded as exc:
   panel['status']='blocked exact-resource budget';panel['views'].append(dict(view=view,status='blocked',reason=str(exc),processed_spans=len(records)));break
  result=assess(poly,observed,28*p['class_pairs']);panel['views'].append(dict(view=view,status='complete',result=result,variable_score_spans=variable,alternative_class_order_spans=movable,span_records=records));nulls.append(dict(original_panel_index=idx,view=view,total_ways_hex=hex(sum(poly.values())),weights_hex={str(k):hex(v) for k,v in sorted(poly.items())}))
  print('DONE',idx,view,result, 'variable',variable,flush=True)
 panels.append(panel);save('PROGRESS.json',dict(completed=len(panels),panels=[{k:v for k,v in x.items() if k!='views'} for x in panels]))
save('RESULTS.json',dict(qualification='PASS before manuscript data access',protocol=load(R/'PROTOCOL.json'),panels=panels));save('NULL-DISTRIBUTIONS.json',nulls);save('SUMMARY.json',[dict(original_panel_index=p['original_panel_index'],reading=p['reading'],section=p['section'],hand=p['hand'],status=p['status'],views=[{k:v for k,v in x.items() if k!='span_records'} for x in p['views']]) for p in panels])
