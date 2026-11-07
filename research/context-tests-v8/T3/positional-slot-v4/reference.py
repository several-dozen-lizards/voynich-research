from pathlib import Path
import sys,math,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'system-types-v5'))
from GENERATORS import generate
def key(v):return json.dumps(v,separators=(',',':'))
def measure(pp,c):
 w=c['width'];at=c['start']-1;known={tuple(v) for v in c['variants']};oi=oo=ai=bo=0;vars={}
 for p in pp:
  a=p['tokens']
  if at+w<=len(a) and None not in a[at:at+w]:
   oi+=1;v=tuple(a[at:at+w]);r=vars.setdefault(v,dict(count=0,folios=set()));r['count']+=1;r['folios'].add(p['folio']);ai+=v in known
  for i in range(1,len(a)-w+1):
   if i==at or None in a[i:i+w]:continue
   oo+=1;bo+=tuple(a[i:i+w]) in known
 vv=sorted(vars,key=lambda v:(-vars[v]['count'],key(v)));rr=(ai/oi)/(bo/oo) if oi and oo and bo else math.inf if oi and oo and ai else None;coverage=ai/oi if oi else None;new=[v for v in vv if v not in known];rec=sum(len(vars[v]['folios'])>=2 for v in vv if v in known);nf=len({p['folio'] for p in pp});presence=ai/len(pp) if pp else None;passed=bool(nf>=8 and presence is not None and presence>=.5 and rr is not None and rr>=1.5 and coverage is not None and coverage>=.7 and len(new)<=4 and rec>=2)
 return dict(paragraphs=len(pp),folios=nf,present_paragraphs=ai,presence=presence,early_occurrences=ai,early_opportunities=oi,outside_occurrences=bo,outside_opportunities=oo,concentration=rr,frozen_coverage=coverage,new_types=[list(v) for v in new],recurrent_frozen_types=rec,variants=[dict(words=list(v),count=vars[v]['count'],folios=len(vars[v]['folios'])) for v in vv],pass_=passed)
def discover(pp):
 nf=len({p['folio'] for p in pp});eligible=[];estimable=0
 if nf<8:return dict(status='NOT ESTIMABLE',candidate=None)
 for w in [1,2,3]:
  for start in range(2,17-w):
   pool={};at=start-1
   for p in pp:
    a=p['tokens']
    if at+w>len(a) or None in a[at:at+w]:continue
    v=tuple(a[at:at+w]);pool[v]=pool.get(v,0)+1
   vv=sorted(pool,key=lambda v:(-pool[v],key(v)));variants=[list(v) for v in vv[:16]];c=dict(start=start,end=start+w-1,width=w,variants=variants);m=measure(pp,c)
   estimable+=m['early_opportunities']>0 and m['outside_opportunities']>0
   if len(variants)<2 or m['presence']<.5 or m['concentration'] is None or m['concentration']<2 or m['frozen_coverage']<.8 or m['recurrent_frozen_types']<2:continue
   d={k:v for k,v in m.items() if k not in ['pass_','new_types']};d.update(observed_variant_types=len(vv),frozen_variant_types=len(variants));c['discovery']=d;eligible.append(c)
 eligible.sort(key=lambda c:(-c['discovery']['presence'],-c['discovery']['concentration'],c['width'],c['start'],key(c['variants'])))
 return dict(status='CANDIDATE' if eligible else 'NO CANDIDATE' if estimable else 'NOT ESTIMABLE',screened_slots=39,estimable_slots=estimable,eligible_candidates=len(eligible),candidate=eligible[0] if eligible else None)
def check_metric(m,r):
 for k in ['paragraphs','folios','present_paragraphs','presence','early_occurrences','early_opportunities','outside_occurrences','outside_opportunities','frozen_coverage','new_types','recurrent_frozen_types','variants']:assert m[k]==r[k],(k,m[k],r[k])
 assert m['pass_']==r['pass'];a=m['concentration'];b=r['concentration'];assert (b=='POSITIVE_INFINITY' if a==math.inf else b is None if a is None else abs(a-b)<=1e-12*max(1,abs(a)))
def rand(seed):
 x=seed&0xffffffff
 while True:
  x=(x+0x6D2B79F5)&0xffffffff;t=((x^(x>>15))*(x|1))&0xffffffff;t=(t^((t+((t^(t>>7))*(t|61)&0xffffffff))&0xffffffff))&0xffffffff;yield((t^(t>>14))&0xffffffff)/4294967296
