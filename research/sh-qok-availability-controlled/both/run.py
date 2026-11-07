from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent.parent;FILES=[P/'sh-qok-matched-effect/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh both-boundary availability-conditioned qualification. Synthetic only; no manuscript/HF data.',generator='Reuse prior both boundary geometry and masks with fresh seed1720000+attempt and outcome seed6720000+attempt.200accepted required; retain original cap and all rejects. Initial V≈82.29 is old support only, not qualification of new conditional support.',revision='Within each preselected exactpage/length/body discordant group, split by ordered pair of follower-availability booleans. Preserve left-sh count separately in each pattern. Exact subset-sum null then preserves line composition, position margins and prefix-availability margins. Constant-score outcomes notestimable. No smoothing or pooling.',estimand='Association beyond structural follower availability. Positive probability.20 after ch and.35 after sh AMONG AVAILABLE matched followers; structuralzeros unchanged. This is a new15point conditional target, not the previous15point aggregate effect. Nulls .2,.6 or additivepage/line/position remain independent of prefix amongavailablefollowers.',gates='Eachcell200required. PositiveWilson95lowerpower>=.80; eachnullupperfalseflag<=.05. New conditionalV/constant-scorefrequency reported; oldV80rule does not transfer. Anyfailedgate failsqualification. Preserve allfailures and no retuning.',verification='Exact distribution preserves number of sh assignments per availabilitypattern byconstruction. In each pattern line-row counts remain1 and columnsh count fixed. Independent small-orbit oracle checks marginal constraints and score distribution before simulation. Fixed blockers not inferred from qok outcomes.',limits='Artificial balancedfourbody masks; conditional exchangeability not guaranteed for arbitrary nuisance. Historical sparsepower unqualified. H/F separate; manuscript staysclosed.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[2],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(FILES[1],['matching','events','score','ci'],env)
matched=dict(collections=collections,env=env);load(FILES[0],['extract','rates'],matched)

def availability_score(rows):
 groups=matched['extract'](rows);dist={0:1};observed=0;V=0.;informative=0;strata_count=0
 for original_v,entries in groups:
  strata=collections.defaultdict(list)
  for ri,j,k,left in entries:
   ws=rows[ri][1];pattern=(not ws[j+1].startswith(('sh','ch')),not ws[k+1].startswith(('sh','ch')))
   strata[pattern].append((left,int(ws[j+1].startswith('qok'))-int(ws[k+1].startswith('qok'))))
  for pattern,items in strata.items():
   n=len(items);ns=sum(x for x,d in items);V+=ns*(n-ns)/n;strata_count+=1
   local=m.subset([d for x,d in items],ns);assert sum(local.values())==math.comb(n,ns)
   lo=min(local);observed+=sum(x*d for x,d in items)-lo
   if len(local)>1:informative+=1
   new=collections.Counter()
   for s,c in dist.items():
    for t,z in local.items():new[s+t-lo]+=c*z
   dist=dict(new)
 p=min(1.,8*sum(c for s,c in dist.items() if s>=observed)/sum(dist.values())) if len(dist)>1 else None
 return dict(V=V,p_adjusted=p,flag=p is not None and p<=.05,availability_strata=strata_count,informative=informative,not_estimable=p is None)
env['score']=availability_score

for pattern in [(1,1),(1,0),(0,1),(0,0)]:
 for n in range(1,6):
  weights=[pattern[0]*(i%2)-pattern[1]*((i+1)%2) for i in range(n)]
  for k in range(n+1):
   brute=collections.Counter(sum(weights[i] for i in ix) for ix in itertools.combinations(range(n),k))
   assert m.subset(weights,k)==brute

attempts=[];designs=[];records=[]
for attempt in range(200):
 seed=1720000+attempt;rng=np.random.default_rng(seed);rows=[];followers=[]
 for pg in range(12):
  j,k=sorted(int(x) for x in rng.choice([1,3,5,7],2,replace=False));lines=[]
  for body in ['aedy','beey','cey','dy']:
   left=set(int(x) for x in rng.choice(7,3,replace=False))
   for line in range(7):
    ws=['dar']*10;ws[j]=('sh' if line in left else 'ch')+body;ws[k]=('ch' if line in left else 'sh')+body;lines.append(ws)
  rng.shuffle(lines)
  for ws in lines:
   ri=len(rows);rows.append((pg,ws));followers.extend([(ri,j+1),(ri,k+1)])
 byclass={0:[],1:[]}
 for idx,(ri,pos) in enumerate(followers):byclass[int(rows[ri][1][pos-1].startswith('sh'))].append(idx)
 assert all(len(v)==336 for v in byclass.values())
 nc=int(rng.integers(34,41));ns=int(rng.integers(84,91))
 available=set(int(x) for x in rng.choice(byclass[0],nc,replace=False))|set(int(x) for x in rng.choice(byclass[1],ns,replace=False))
 for ix,(ri,pos) in enumerate(followers):
  if ix not in available:rows[ri][1][pos]='chx'
 groups=matched['extract'](rows);V=sum(v for v,e in groups);f=matched['rates'](rows,groups,True);pv=[0.]*12
 for v,e in groups:pv[rows[e[0][0]][0]]+=v
 ok=80<=V<84 and sum(x>0 for x in pv)>=8 and max(pv)/V<=.25 and .1<=f[0]<=.12 and .25-1e-12<=f[1]<=.27
 attempts.append(dict(seed=seed,V=V,availability=f,accepted=ok))
 if not ok:continue
 assert abs(V-576/7)<1e-9 and abs(f[0]-nc/336)<1e-12 and abs(f[1]-ns/336)<1e-12
 designs.append(dict(seed=seed,V=V,availability=f,rows=rows));qrng=np.random.default_rng(6720000+attempt)
 for scenario in ['null_low','null_high','null_line','positive']:
  probs={}
  if scenario=='positive':
   for v,e in groups:
    for ri,j,k,left in e:
     for pos,a in [(j,left),(k,1-left)]:
      if rows[ri][1][pos+1]!='chx':probs[ri,pos+1]=(.35 if a else .2)
   assert max(probs.values())<=1+1e-12
  pe=qrng.choice([-.7,.7],size=12);new=[]
  for ri,(pg,ws) in enumerate(rows):
   le=float(qrng.choice([-.7,.7]));out=[]
   for j,w in enumerate(ws):
    if w.startswith(('sh','ch')):out.append(w);continue
    prob=1/(1+math.exp(-(pe[pg]+le+(.7 if j%2 else -.7)))) if scenario=='null_line' else .6 if scenario=='null_high' else .2
    if scenario=='positive':prob=probs.get((ri,j),.2)
    out.append('qokam' if qrng.random()<prob else 'dar')
   new.append((pg,out))
  assert matched['extract'](new)==groups
  result=env['score'](new);rr=matched['rates'](new,groups)
  records.append(dict(seed=seed,scenario=scenario,availability=f,observed_gap=rr[1]-rr[0],**result))
 if len(designs)%50==0:print(len(designs),'accepted after',attempt+1,flush=True)
 if len(designs)==200:break
save('ATTEMPTS.json',attempts);save('DESIGNS.json',designs);save('TRIALS.json',records)
summary=[]
for scenario in ['null_low','null_high','null_line','positive']:
 rr=[r for r in records if r['scenario']==scenario];n=len(rr);k=sum(r['flag'] for r in rr);ci=env['ci'](k,n) if n else [0,1]
 summary.append(dict(scenario=scenario,n=n,flags=k,wilson95=ci,pass_gate=n==200 and (ci[0]>=.8 if scenario=='positive' else ci[1]<=.05),mean_observed_gap=float(np.mean([r['observed_gap'] for r in rr])) if rr else None))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),admitted=len(designs),attempts=len(attempts),matching_unchanged=True,manuscript_read=False))
