from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent.parent;FILES=[P/'sh-qok-matched-effect/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh ch boundary synthetic controls only. No manuscript or H/F data.',generator='Same12page4targetbody7linebalanced structure,V576/7. Direct conditional mask generation: choose available ch count uniformly34..40 of336; sh count uniformly134..140 of336. Sample positions uniformly within each prefix class. This deliberately conditions masks on prefix, NOT independent-mask rejection sampling; all masks precede qok outcomes. Fixed chx blockers preserve target support. Conditional mask construction is part of the selection challenge.',gate='Require80<=V<84,>=8pages,maxshare<=.25,.10<=f_ch<=.12 and .39<=f_sh<=.43.200freshlayouts,cap200attempts; failed designs retained, never replaced. Seeds1320000+attempt; outcome seeds6320000+attempt.',outcomes='Independent nonorigin-qok nulls .2,.6 and additive page/line/position logits; no prefix calibration in nulls. Positive availablematched followers .10/f_ch and.25/f_sh for weightedgap.15. Existing exact reference null andBonferroni8 unchanged. Nullclass labels describe no direct qok choice dependence among available followers; masks themselves can induce dependence and the test must reject specificity if falsely promoted as controlled.',gates='All200needed. PositiveWilson95lower>=.80; eachnullupper<=.05. Anyfailedcell failsqualification. No postoutcome correction, rescoring or threshold change. Keep expected structural gap, every outcome, masks and failures.',limits='Prefix-conditioned mask selection may bias the unchanged reference null. This run tests that risk, not a proof of exchangeability. Artificial blockers and balanced overlap are not historical coverage. H/F stay separate; manuscript closed.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[2],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(FILES[1],['matching','events','score','ci'],env)
matched=dict(collections=collections,env=env);load(FILES[0],['extract','rates'],matched)
attempts=[];designs=[];records=[]
for attempt in range(200):
 seed=1320000+attempt;rng=np.random.default_rng(seed);rows=[];followers=[]
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
 nc=int(rng.integers(34,41));ns=int(rng.integers(134,141))
 available=set(int(x) for x in rng.choice(byclass[0],nc,replace=False))|set(int(x) for x in rng.choice(byclass[1],ns,replace=False))
 for ix,(ri,pos) in enumerate(followers):
  if ix not in available:rows[ri][1][pos]='chx'
 groups=matched['extract'](rows);V=sum(v for v,e in groups);f=matched['rates'](rows,groups,True);pv=[0.]*12
 for v,e in groups:pv[rows[e[0][0]][0]]+=v
 ok=80<=V<84 and sum(x>0 for x in pv)>=8 and max(pv)/V<=.25 and .1<=f[0]<=.12 and .39<=f[1]<=.43
 attempts.append(dict(seed=seed,V=V,availability=f,accepted=ok))
 if not ok:continue
 assert abs(V-576/7)<1e-9 and abs(f[0]-nc/336)<1e-12 and abs(f[1]-ns/336)<1e-12
 designs.append(dict(seed=seed,V=V,availability=f,rows=rows));qrng=np.random.default_rng(6320000+attempt)
 for scenario in ['null_low','null_high','null_line','positive']:
  probs={}
  if scenario=='positive':
   for v,e in groups:
    for ri,j,k,left in e:
     for pos,a in [(j,left),(k,1-left)]:
      if rows[ri][1][pos+1]!='chx':probs[ri,pos+1]=(.25 if a else .1)/f[a]
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
