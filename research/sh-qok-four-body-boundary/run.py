from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;FILES=[P/'sh-qok-matched-effect/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Constructive four-body synthetic boundary qualification only. No manuscript/HF data loaded.',generator='200fresh layouts.12pages,4exactbodies aedy,beey,cey,dy;7lines/body/page. Eachpage randomly selects2positions from1,3,5,7 in length10 lines. Eachline has thatbody at both positions, remaining tokens dar. For eachbody randomly choose3of7lines sh-left/ch-right; remaining4ch-left/sh-right. Randomize lineorder. Expected V=12*4*(3*4/7)=576/7=82.285714; all12pages equalshare. All followers available: f_ch=f_sh=1. No rejection sampling or outcome-based design.',joint_rule='Unchanged V>=80,>=8pages,maxshare<=.25,f_ch>=.10,f_sh>=.25; boundary80<=V<84. Gate evaluated by frozen actualextractor, not assumed from construction. Any design failure retained and not replaced.',fresh_seeds='1250000+trial for structure;2250000+trial for outcomes.',scenarios='Independent draws per accepted layout: null_low probability.2;null_high.6;null_line logistic(randompage±.7+randomline±.7+position±.7) on available nonorigins, independent of variants;positive matched chfollowers.1,shfollowers.25,others.2. Exact score unchanged Bonferroni8. No null prefix calibration.',gates='Require all200layouts supportverified; positive lowerWilson95power>=.80;eachnullupperfalseflag<=.05. Anyfailedcell failsqualification. Check support,pages,shares,availability,all4bodies,matching unchanged afteroutcomes; preserve everylayout seed and outcome. No reruns.',limits='Deliberately constructed balanced overlap, not sparse historical coverage. Feasibilityalways1: tests joint rule in feasible interiors, not close to feasibilityboundary. Vonlyone value near82.29; not all80..84. Finite controls, no universal sufficiency or claim manuscriptcanpass.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[2],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(FILES[1],['matching','events','score','ci'],env)
matched=dict(collections=collections,env=env);load(FILES[0],['extract','rates'],matched)
records=[];designs=[]
for trial in range(200):
 rng=np.random.default_rng(1250000+trial);qrng=np.random.default_rng(2250000+trial);rows=[]
 for pg in range(12):
  j,k=sorted(int(x) for x in rng.choice([1,3,5,7],2,replace=False));lines=[]
  for body in ['aedy','beey','cey','dy']:
   left=set(int(x) for x in rng.choice(7,3,replace=False))
   for line in range(7):
    ws=['dar']*10;ws[j]=('sh' if line in left else 'ch')+body;ws[k]=('ch' if line in left else 'sh')+body;lines.append((pg,ws))
  rng.shuffle(lines);rows.extend(lines)
 groups=matched['extract'](rows);V=sum(v for v,e in groups);f=matched['rates'](rows,groups,True);pv=[0.]*12
 for v,e in groups:pv[rows[e[0][0]][0]]+=v
 passed=80<=V<84 and sum(x>0 for x in pv)>=8 and max(pv)/V<=.25 and f[0]>=.1 and f[1]>=.25
 designs.append(dict(trial=trial,seed=1250000+trial,V=V,availability=f,pages=pv,admitted=passed,rows=rows))
 if not passed:continue
 assert abs(V-576/7)<1e-9 and f==[1.,1.]
 for scenario in ['null_low','null_high','null_line','positive']:
  probs={}
  if scenario=='positive':
   for v,e in groups:
    for ri,j,k,left in e:
     for pos,a in [(j,left),(k,1-left)]:assert (ri,pos+1) not in probs;probs[ri,pos+1]=.25 if a else .1
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
  result=env['score'](new);assert abs(result['V']-V)<1e-9;rates=matched['rates'](new,groups)
  records.append(dict(trial=trial,scenario=scenario,observed_gap=rates[1]-rates[0],**result))
 if (trial+1)%50==0:print(trial+1,'layouts complete',flush=True)
summary=[]
for scenario in ['null_low','null_high','null_line','positive']:
 rr=[r for r in records if r['scenario']==scenario];n=len(rr);k=sum(r['flag'] for r in rr);ci=env['ci'](k,n) if n else [0,1]
 summary.append(dict(scenario=scenario,n=n,flags=k,wilson95=ci,pass_gate=n==200 and (ci[0]>=.8 if scenario=='positive' else ci[1]<=.05),mean_observed_gap=float(np.mean([r['observed_gap'] for r in rr])) if rr else None))
save('DESIGNS.json',designs);save('TRIALS.json',records);save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),admitted=sum(d['admitted'] for d in designs),total=200,records=len(records),manuscript_read=False))
