from pathlib import Path
import json,sys,hashlib,math,collections,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;P=T.parent.parent;sys.path.insert(0,str(P/'system-types-v5'))
from GENERATORS import generate

def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 p=R/p;tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
def spans(pp,d,early_only=False):
 w=d+2
 for pi,p in enumerate(pp):
  a=p['tokens']
  for i in range(1,min(len(a)-w+1,16-w) if early_only else len(a)-w+1):
   x=a[i:i+w]
   if None not in x:yield pi,p,i,x

def discover(pp):
 fs={};opp={d:[0,0] for d in [1,2,3]}
 for d in [1,2,3]:
  for pi,p,i,x in spans(pp,d,True):
   opp[d][0]+=1;k=(x[0],x[-1],d);v=tuple(x[1:-1])
   if k not in fs:fs[k]={'inside':0,'outside':0,'paras':set(),'variants':{}}
   r=fs[k];r['inside']+=1;r['paras'].add(pi)
   if v not in r['variants']:r['variants'][v]={'count':0,'folios':set()}
   r['variants'][v]['count']+=1;r['variants'][v]['folios'].add(p['folio'])
 possible={}
 for k,r in fs.items():
  if len(r['paras'])/len(pp)<.5:continue
  vv=sorted(r['variants'],key=lambda v:(-r['variants'][v]['count'],json.dumps(v,separators=(',',':'))))[:16]
  if len(vv)<2 or sum(r['variants'][v]['count'] for v in vv)/r['inside']<.8 or sum(len(r['variants'][v]['folios'])>=2 for v in vv)<2:continue
  possible[k]=(r,vv)
 if not possible:return dict(screened=len(fs),eligible=0,candidate=None)
 for d in [1,2,3]:
  for pi,p,i,x in spans(pp,d):
   if i+d+2<=15:continue
   opp[d][1]+=1;k=(x[0],x[-1],d)
   if k in possible:possible[k][0]['outside']+=1
 eligible=[]
 for k,(r,vv) in possible.items():
  oi,oo=opp[k[2]]
  if not oi or not oo:continue
  rr=(r['inside']/oi)/(r['outside']/oo) if r['outside'] else math.inf
  if rr<2:continue
  eligible.append(dict(left=k[0],right=k[1],gap=k[2],variants=[list(v) for v in vv],presence=len(r['paras'])/len(pp),concentration=rr,inside=r['inside'],outside=r['outside'],oi=oi,oo=oo))
 eligible.sort(key=lambda c:(-c['presence'],-c['concentration'],c['gap'],json.dumps([c['left'],c['right'],c['gap']],separators=(',',':'))))
 return dict(screened=len(fs),eligible=len(eligible),candidate=eligible[0] if eligible else None)

def measure(pp,c):
 w=c['gap']+2;oi=oo=ai=bo=0;hit=set();variants={};known={tuple(x) for x in c['variants']}
 for pi,p,i,x in spans(pp,c['gap']):
  inside=i+w<=15
  if inside:oi+=1
  else:oo+=1
  if x[0]!=c['left'] or x[-1]!=c['right']:continue
  if not inside:bo+=1;continue
  ai+=1;hit.add(pi);v=tuple(x[1:-1]);r=variants.setdefault(v,{'count':0,'folios':set()});r['count']+=1;r['folios'].add(p['folio'])
 ratio=(ai/oi)/(bo/oo) if oi and oo and bo else math.inf if oi and oo and ai else None
 cover=sum(v['count'] for k,v in variants.items() if k in known)/ai if ai else None;new=[k for k in variants if k not in known];rec=sum(len(v['folios'])>=2 for k,v in variants.items() if k in known)
 ok=len({p['folio'] for p in pp})>=8 and len(hit)/len(pp)>=.5 and ratio is not None and ratio>=1.5 and cover is not None and cover>=.7 and len(new)<=4 and rec>=2
 return dict(present_paragraphs=len(hit),presence=len(hit)/len(pp),early_occurrences=ai,outside_occurrences=bo,early_opportunities=oi,outside_opportunities=oo,concentration=ratio,frozen_coverage=cover,new_types=[list(k) for k in new],recurrent_frozen_types=rec,pass_=ok)

def check_metric(m,r):
 for k in ['present_paragraphs','presence','early_occurrences','outside_occurrences','early_opportunities','outside_opportunities','frozen_coverage','recurrent_frozen_types']:assert m[k]==r[k],(k,m[k],r[k])
 assert m['pass_']==r['pass']
 if m['concentration'] is None:assert r['concentration'] is None
 elif math.isinf(m['concentration']):assert r['concentration']=='POSITIVE_INFINITY'
 else:assert abs(m['concentration']-r['concentration'])<=1e-12*max(1,abs(m['concentration']))
 assert sorted(m['new_types'])==sorted(r['new_types'])

def rand(seed):
 x=seed&0xffffffff
 while True:
  x=(x+0x6D2B79F5)&0xffffffff;t=((x^(x>>15))*(x|1))&0xffffffff;t=(t^((t+((t^(t>>7))*(t|61)&0xffffffff))&0xffffffff))&0xffffffff;yield((t^(t>>14))&0xffffffff)/4294967296

def main():
 results=[];allresults=load('LATIN-RESULTS.json');fixtures=load('PERMUTATION-REFERENCE-FIXTURES.json')
 for r in allresults:
  n=r['cell'];pp=load('latin/'+n+'/DISCOVERY.json');fr=load('latin/'+n+'/CANDIDATE-FREEZE.json');ref=discover(pp);c=fr['discovery']['candidate'];assert ref['screened']==fr['discovery']['screened_early_frames'];assert ref['eligible']==fr['discovery']['eligible_candidates'];assert all(ref['candidate'][k]==c[k] for k in ['left','right','gap','variants']);test=load('latin/'+n+'/CONFIRMATION.json');check_metric(measure(test,c),r['confirmation']['observed']);rng=rand(r['confirmation']['seed']);ff=[f for f in fixtures if f['cell']==n]
  for f in ff:
   qq=[]
   for p in test:
    a=p['tokens'][:]
    for i in range(len(a)-1,1,-1):
     j=1+int(next(rng)*i);a[i],a[j]=a[j],a[i]
    qq.append(dict(p,tokens=a))
   digest=hashlib.sha256(json.dumps([p['tokens'] for p in qq],separators=(',',':')).encode()).hexdigest();assert digest==f['tokens_sha256'];check_metric(measure(qq,c),f['metrics'])
  results.append(dict(cell=n,discovery_exact=True,confirmation_exact=True,independent_permutation_draws=len(ff)))
 save('INDEPENDENT-LATIN-AUDIT.json',dict(status='PASS',cells=results,permutation_draws=len(fixtures)))
 ledger=load('GENERATION-LEDGER.json');audit=[];g6replayed=0
 for num,row in enumerate(ledger,1):
  d='controls/'+row['name'];folder=R/d;pp=load(d+'/PARAGRAPHS.json');geo=load(d+'/GEOMETRY.json');assert sha(folder/'PARAGRAPHS.json')==row['paragraphs_sha256'];assert sha(folder/'GEOMETRY.json')==row['geometry_sha256'];assert len(pp)==len(geo)
  if row['family']=='G5':
   files=list((folder/'generated').glob('*.txt'));assert len(files)==1;ln=[s.split() for s in files[0].read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')];assert len(ln)==row['native_lines'];assert row['seed_line_excluded'];words=[w for line in ln[1:] for w in line];assert len(words)==row['generated_tokens'];assert len(words)-row['original_slots']==row['unused_tail_tokens']
  else:
   gg=generate('G6',{},row['seed'],line_lengths=[g['length'] for g in geo]);native=load(d+'/NATIVE-MECHANISM.json');assert gg['table']==native['table'] and json.loads(json.dumps(gg['draws']))==native['draws'];words=[''.join(w) for line in gg['lines'] for w in line];g6replayed+=1
  at=0
  for p,g in zip(pp,geo):
   expected=words[at:at+g['length']];at+=g['length']
   for j in g['unknown']:expected[j]=None
   assert expected==p['tokens'];assert p['folio']==g['folio'] and p['arm']==g['arm'];assert ('DISCOVERY' if int(hashlib.sha256(('v8-T3:'+p['folio']).encode()).hexdigest(),16)%2==0 else 'CONFIRMATION')==p['arm']
  train=[p for p in pp if p['arm']=='DISCOVERY'];fr=load(d+'/CANDIDATE-FREEZE.json')['discovery'];ref=discover(train);assert ref['screened']==fr['screened_early_frames'];assert ref['eligible']==fr['eligible_candidates']==0 and ref['candidate'] is None and fr['candidate'] is None;ev=load(d+'/EVALUATION.json');assert ev['status']=='NO CANDIDATE' and not ev['raw_pass'];audit.append(dict(name=row['name'],native_slots_exact=True,independent_no_candidate=True))
  if num%50==0:save('INDEPENDENT-CONTROL-AUDIT-PROGRESS.json',dict(completed=num,total=1200,G6_seed_replays=g6replayed));print('audited',num,flush=True)
 save('INDEPENDENT-CONTROL-AUDIT.json',dict(status='PASS',datasets=len(audit),G5_native_prefix_replays=600,G6_full_seed_replays=g6replayed,results=audit));print('INDEPENDENT AUDIT COMPLETE',flush=True)
if __name__=='__main__':main()
