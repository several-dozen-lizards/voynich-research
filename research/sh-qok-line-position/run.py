from pathlib import Path
import json,hashlib,sys,itertools,math
import numpy as np
R=Path(__file__).resolve().parent
ENDINGS=('edy','eey','ey','y')
REGIMES=['page','position','line','combined','body','positive_strong','positive_small','sparse_strong','no_overlap']
def save(n,x): (R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ending(w):return next((s for s in ENDINGS if w.endswith(s)),None)
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic only. No corpus files loaded. H/F never pooled; future application requires separate source readings and is not authorized by this qualification.',design='12 synthetic pages; 24 lines per page; 8 eligible interior origin positions at indices1,3,...15 in length18 lines. Pair lines consecutively within page/length using indices only. Within each line pair group positions by identical exact body in all four corners, then pair sorted positions consecutively. Secondary groups by correctly disjoint suffix instead of body. Rectangles disjoint; construction never uses sh/ch or qok. All outcomes fixed.',null='Only checkerboard sh/ch rectangles can flip orientation. Each flip preserves each line prefix count and exact-position prefix count, page and length, and body counts in primary. Non-checkerboards pinned. Independent fair flips conditional on each rectangle margins. This is a stronger conditioning test, potentially lower power; no MCMC.',statistic='Sum sh*qok over movable rectangles. Each orientation difference is d=q00-q01-q10+q11. Exact upper-tail distribution from convolution of independent two-point distributions; integer coefficients using arbitrary precision. Bonferroni8 reserved for2panels x2readings x2views. Zero nonzero-d rectangles = not estimable, p omitted, never negative evidence.',generator='Fresh seeds973000+regime_index*1000+trial. Independent Bernoulli sh/qok given logit nuisance state: page, position, line, combined additive logit page+line+position, or body. Body shared across lines by slot in standard controls; four distinct bodies edy,eey,ey,y. Positives: sh p=.5; qok p=.2+.45*sh or .2+.15*sh. Sparse positive uses6lines/page and independent body per cell. No-overlap makes prefix solely determined by position. Body labels carry no semantic interpretation.',trials=200,gates='Each of5nuisance regimes exact-body Wilson95 upper rejection bound<=.05; strong positive lower detection bound>=.80; no-overlap allnotestimable. Small-effect and sparse strong power are mandatory scope diagnostics: if either lower bound<.80, broad qualification fails and any limited pass must be labeled dense/strong-only. Secondary does not determine primary pass. Exact oracle, ending unit tests and all flip invariants must pass. No repair after outcomes.',limitations='Additive logit nuisance is exchangeable under these flips; arbitrary line-by-position interactions need not be. Synthetic event-level engine, not a validated corpus tokenizer. No manuscript rescore even if gates pass. Preserve all failures.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
assert [ending(w) for w in ['shedy','sheey','shey','shy','sheol']]==['edy','eey','ey','y',None]
def tail(weights,observed):
 counts=[1]
 for d in weights:
  d=abs(int(d));n=[0]*(len(counts)+d)
  for i,c in enumerate(counts):n[i]+=c;n[i+d]+=c
  counts=n
 return sum(counts[observed:])/sum(counts)
for weights in [[1],[2],[1,2,1],[2,2,1,1]]:
 vals=[sum(a*b for a,b in zip(weights,bits)) for bits in itertools.product([0,1],repeat=len(weights))]
 for t in range(sum(weights)+1):assert abs(tail(weights,t)-sum(v>=t for v in vals)/len(vals))<1e-12
def generate(reg,rng):
 L=6 if reg=='sparse_strong' else 24
 bodies=np.array(ENDINGS)[np.arange(8)%4];body=np.broadcast_to(bodies,(12,L,8)).copy()
 if reg=='sparse_strong':body=rng.choice(ENDINGS,size=(12,L,8))
 pg=rng.choice([-1.5,1.5],size=(12,1,1));ln=rng.choice([-1.5,1.5],size=(12,L,1));pos=np.array([-1.5,1.5]*4)[None,None,:]
 z=np.zeros((12,L,8))
 if reg in ['page','combined']:z=z+pg
 if reg in ['line','combined']:z=z+ln
 if reg in ['position','combined']:z=z+pos
 if reg=='body':z=np.where(body=='edy',1.5,-1.5)
 prob=1/(1+np.exp(-z));a=(rng.random(z.shape)<prob).astype(int);q=(rng.random(z.shape)<prob).astype(int)
 if reg in ['positive_strong','positive_small','sparse_strong']:
  q=(rng.random(z.shape)<(.2+(.15 if reg=='positive_small' else .45)*a)).astype(int)
 if reg=='no_overlap':a=np.broadcast_to(np.arange(8)%2,z.shape).copy()
 return a,q,body
def test(a,q,body,view):
 weights=[];observed=0;rectangles=0;movable=0
 for pg in range(a.shape[0]):
  for l in range(0,a.shape[1]-1,2):
   groups={}
   for j in range(a.shape[2]):
    b1,b2=body[pg,l,j],body[pg,l+1,j]
    if view=='ending_family':b1,b2=ending(b1),ending(b2)
    if b1==b2:groups.setdefault(str(b1),[]).append(j)
   for positions in groups.values():
    for j,k in zip(positions[::2],positions[1::2]):
     rectangles+=1;x=a[pg,l:l+2,[j,k]].copy();y=q[pg,l:l+2,[j,k]]
     if not (x[0,0]==x[1,1] and x[0,1]==x[1,0] and x[0,0]!=x[0,1]):continue
     movable+=1;flipped=1-x
     assert np.array_equal(x.sum(axis=0),flipped.sum(axis=0)) and np.array_equal(x.sum(axis=1),flipped.sum(axis=1))
     # Direct scores independently check the analytic orientation contrast.
     s=int((x*y).sum());other=int((flipped*y).sum());d=int(y[0,0]-y[0,1]-y[1,0]+y[1,1])
     assert abs(s-other)==abs(d)
     if d:weights.append(abs(d));observed+=s-min(s,other)
 if not weights:return dict(p_adjusted=None,flag=False,rectangles=rectangles,movable=movable,informative=0)
 p=min(1.,8*tail(weights,observed))
 return dict(p_adjusted=p,flag=p<=.05,rectangles=rectangles,movable=movable,informative=len(weights))
def ci(k,n):
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [max(0.,c-h),min(1.,c+h)]
records=[]
for ri,reg in enumerate(REGIMES):
 for trial in range(200):
  seed=973000+ri*1000+trial;a,q,b=generate(reg,np.random.default_rng(seed))
  for view in ['exact_body','ending_family']:records.append(dict(regime=reg,trial=trial,seed=seed,view=view,**test(a,q,b,view)))
 save('TRIALS.json',records);print(reg,'complete',flush=True)
summary=[]
for reg in REGIMES:
 for view in ['exact_body','ending_family']:
  rr=[r for r in records if r['regime']==reg and r['view']==view];k=sum(r['flag'] for r in rr);ne=sum(r['informative']==0 for r in rr);bounds=ci(k,200)
  passed=ne==200 if reg=='no_overlap' else bounds[0]>=.80 if 'positive' in reg or reg=='sparse_strong' else bounds[1]<=.05
  summary.append(dict(regime=reg,view=view,flags=k,total=200,not_estimable=ne,wilson95=bounds,criterion_pass=passed,informative_median=float(np.median([r['informative'] for r in rr]))))
save('SUMMARY.json',dict(status='PASS' if all(r['criterion_pass'] for r in summary if r['view']=='exact_body') else 'FAIL',results=summary,manuscript_read=False))
save('VERIFICATION.json',dict(freeze_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),ending_tests_pass=True,exact_oracle_pass=True,all_encountered_flip_margins_preserved=True,trial_records=len(records),manuscript_read=False))
