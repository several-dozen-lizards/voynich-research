from pathlib import Path
import json,math,collections,sys,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;Q=T/'class-multiword-v3-bank2'
spec=importlib.util.spec_from_file_location('qualified_classes',Q/'independent_audit.py');classes=importlib.util.module_from_spec(spec);spec.loader.exec_module(classes)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def key(x):return json.dumps(x,separators=(',',':'))
checks=0
def ck(v,msg):
 global checks
 checks+=1
 assert v,msg
panels=load(R/'DIAGNOSIS.json')['panels'];audit=[]
for panel in panels:
 name=panel['panel']
 if name.startswith('H-'):pp=[p for p in load(T/'DISCOVERY-PARAGRAPHS.json') if p['scribe']==name[-1]]
 else:pp=load(Q/'latin'/name.removeprefix('Latin-')/'DISCOVERY.json')
 pp=classes.classified(pp)
 frames={};opps={};folios={p['folio'] for p in pp}
 for d in [1,2,3]:
  w=d+2;o=dict(early_total=0,early_readable=0,early_blocked=0,outside_total=0,outside_readable=0,outside_blocked=0,paragraphs_with_readable_early=0,paragraphs_with_any_early_span=0)
  for pi,p in enumerate(pp):
   anyspan=False;readable=False
   for i in range(1,len(p['tokens'])-w+1):
    span=p['tokens'][i:i+w];early=i+w<=15;region='early' if early else 'outside';o[region+'_total']+=1
    if early:anyspan=True
    if None in span:o[region+'_blocked']+=1;continue
    o[region+'_readable']+=1
    if not early:continue
    readable=True;k=key([span[0],span[-1],d]);f=frames.setdefault(k,dict(early=0,outside=0,paras=set(),folios=set(),variants={},d=d));f['early']+=1;f['paras'].add(pi);f['folios'].add(p['folio']);v=tuple(span[1:-1]);vv=f['variants'].setdefault(v,dict(count=0,folios=set()));vv['count']+=1;vv['folios'].add(p['folio'])
   o['paragraphs_with_any_early_span']+=anyspan;o['paragraphs_with_readable_early']+=readable
  opps[str(d)]=o
 for d in [1,2,3]:
  w=d+2
  for p in pp:
   for i in range(max(1,16-w),len(p['tokens'])-w+1):
    a=p['tokens'][i:i+w]
    if None in a:continue
    f=frames.get(key([a[0],a[-1],d]))
    if f is not None:f['outside']+=1
 rows=load(R/(name+'-FRAMES.json'));ck(len(rows)==len(frames)==panel['screened_frames'],name+'frame universe');ck(opps==panel['opportunities'],name+'opportunities');ck(len(folios)==panel['support']['folios'] and len(folios)>=8,name+'support');flagslist=[]
 for r in rows:
  f=frames[r['key']];v=sorted(f['variants'],key=lambda v:(-f['variants'][v]['count'],key(v)));chosen=v[:16];o=opps[str(f['d'])];oi=o['early_readable'];oo=o['outside_readable'];ratio=(f['early']/oi)/(f['outside']/oo) if oi and oo and f['outside'] else math.inf if oi and oo else None;coverage=sum(f['variants'][v]['count'] for v in chosen)/f['early'];rec=sum(len(f['variants'][v]['folios'])>=2 for v in chosen);m=dict(present_paragraphs=len(f['paras']),presence=len(f['paras'])/len(pp),early_folios=len(f['folios']),early_occurrences=f['early'],outside_occurrences=f['outside'],early_opportunities=oi,outside_opportunities=oo,variant_types=len(v),frozen_variant_types=len(chosen),frozen_coverage=coverage,recurrent_frozen_types=rec)
  for k,val in m.items():ck(val==r['metrics'][k],name+r['key']+k)
  target=r['metrics']['concentration'];ck(target=='POSITIVE_INFINITY' if ratio==math.inf else target is None if ratio is None else abs(ratio-target)<=1e-12*max(1,abs(ratio)),name+'ratio')
  fl=dict(presence=m['presence']>=.5,concentration=ratio is not None and ratio>=2,minimum_types=len(chosen)>=2,coverage=coverage>=.8,recurrence=rec>=2);ck(fl==r['flags'],name+'gate flags');ck(all(fl.values())==r['eligible'],name+'eligibility');ck([k for k,val in fl.items() if not val]==r['failed'],name+'failures');ck([list(v) for v in chosen]==r['frozen_variants'],name+'variants');ck([dict(words=list(k),count=f['variants'][k]['count'],folios=len(f['variants'][k]['folios'])) for k in v]==r['all_variants'],name+'all variants');flagslist.append(fl)
 ck(sum(all(f.values()) for f in flagslist)==panel['eligible_frames'],name+'eligible total')
 for gate in flagslist[0]:ck(panel['marginal'][gate]=={'pass':sum(f[gate] for f in flagslist),'fail':sum(not f[gate] for f in flagslist),'sole_failure':sum(not f[gate] and sum(not b for b in f.values())==1 for f in flagslist)},name+'marginal')
 sig=collections.Counter('|'.join(k for k,v in f.items() if not v) or 'ALL PASS' for f in flagslist);ck(dict(sig)==panel['overlap_failure_signatures'],name+'overlap signatures');alive=flagslist
 for f in panel['cumulative_funnel']:
  before=len(alive);alive=[r for r in alive if r[f['gate']]];ck(f==dict(gate=f['gate'],before=before,eliminated=before-len(alive),survive=len(alive)),name+'funnel')
 ck(max(len(f['paras'])/len(pp) for f in frames.values())==panel['maximum_presence'],name+'maxpresence');audit.append(dict(panel=name,frames=len(rows),all_metrics_flags_variants_exact=True))
out=dict(status='PASS',checks=checks,panels=audit,frame_rows=sum(x['frames'] for x in audit),confirmation_bodies_parsed=0,thresholds_changed=False,scope='Separate Python classification and enumeration, same agent; full counts/variants/flags and opportunities checked, floating ratios within1e-12 relative tolerance')
(R/'INDEPENDENT-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
