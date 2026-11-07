from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-all-interior/run.py';SUB=R.parent/'sh-qok-expanded-null/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic diagnostic only; no manuscript or H/F pooling.',design='12pages24lines; density.35/.70; lengths uniform6..14 or fixed12; bodypool1/12.100fresh layouts each density/length; bodypools share origin locations, prefix variants, missingness and outcome uniforms.2%unknownslots in all designs. Seeds1070000+design*1000+trial. All origins body=core+edy; bodycounts change exact comparability only.',outcomes='Three scenarios: null qokprob.2 on every available nonorigin; diluted qokprob.1+.15*previous-sh on available following slots; calibrated target total eligible-origin qokprob.1 afterch and.25 aftersh. For each prefix group, compute availability fraction f over all readable interiororigins; set probability on its availablefollowers to target/f. If f<target or groupempty, retain as infeasible and do not score calibratedcase. Other nonorigins qokprob.1. Origins never overwritten. Same uniformdraws across pools/scenarios.',calibration='For calibratedcase record expected all-origin difference exactly.15 plus observed difference. This controls the global eligible-origin effect, not the conditional effect inside selected exact-body pairs. Record selected-testpower without claiming equal conditional signal. Calibratedconstruction is a powerdiagnostic, not a null model.',method='Unchanged allinterior exactmatching and exactnull,Bonferroni8. Preserve all line/position/body controls. Compare same layout across bodypool and effectscenario. No thresholdfitting.',criteria='Descriptivepaired diagnostic with Wilson95 intervals. Null upperbound<=.10 and positive lowerbound>=.80 shown percell; infeasiblecases count against practical detection denominator and remain visible. No manuscript qualification or scoring. Record V,notestimable,expected/realized effect and all failures.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SRC,SUB]});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(p,names,env):exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),env)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(SUB,['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(SRC,['matching','events','score','ci'],env)
records=[]
for di,(density,lengths) in enumerate(itertools.product([.35,.70],['variable','fixed'])):
 for trial in range(100):
  seed=1070000+di*1000+trial;rng=np.random.default_rng(seed);base=[];counts=[0,0];avail=[0,0]
  for pg in range(12):
   for line in range(24):
    L=int(rng.integers(6,15)) if lengths=='variable' else 12;o=rng.random(L)<density;a=rng.integers(2,size=L);unknown=rng.random(L)<.02;body=rng.integers(12,size=L);u=rng.random(L)
    for j in range(1,L-1):
     if o[j] and not unknown[j] and not unknown[j+1]:counts[a[j]]+=1;avail[a[j]]+=not o[j+1]
    base.append((pg,o,a,unknown,body,u))
  f=[avail[c]/counts[c] if counts[c] else 0 for c in range(2)];feasible=f[0]>=.1 and f[1]>=.25
  for pool in [1,12]:
   for scenario in ['null','diluted','calibrated']:
    common=dict(density=density,lengths=lengths,trial=trial,seed=seed,pool=pool,scenario=scenario,availability=f,feasible=feasible if scenario=='calibrated' else True)
    if scenario=='calibrated' and not feasible:records.append(common|dict(flag=False,p_adjusted=None,V=None,not_estimable=True,expected_gap=None,observed_gap=None));continue
    rows=[];success=[0,0]
    for pg,o,a,unknown,body,u in base:
     ws=[]
     for j in range(len(o)):
      if unknown[j]:ws.append(None)
      elif o[j]:ws.append(('sh' if a[j] else 'ch')+'abcdefghijkl'[body[j]%pool]+'edy')
      else:
       prob=.2 if scenario=='null' else .1
       if j>1 and o[j-1] and not unknown[j-1]:
        c=a[j-1]
        if scenario=='diluted':prob=.1+.15*c
        elif scenario=='calibrated':prob=(.1+.15*c)/f[c]
       ws.append('qokam' if u[j]<prob else 'dar')
     for j in range(1,len(ws)-1):
      if o[j] and ws[j] and ws[j+1]:success[a[j]]+=ws[j+1]=='qokam'
     rows.append((pg,ws))
    gap=success[1]/counts[1]-success[0]/counts[0];expected=.15 if scenario=='calibrated' else .25*f[1]-.1*f[0] if scenario=='diluted' else .2*(f[1]-f[0])
    records.append(common|env['score'](rows)|dict(expected_gap=expected,observed_gap=gap))
 save('TRIALS.json',records);print(density,lengths,'complete',flush=True)
summary=[]
for density,lengths,pool,scenario in itertools.product([.35,.70],['variable','fixed'],[1,12],['null','diluted','calibrated']):
 rr=[r for r in records if (r['density'],r['lengths'],r['pool'],r['scenario'])==(density,lengths,pool,scenario)];k=sum(r['flag'] for r in rr);ci=env['ci'](k,100);valid=[r for r in rr if r['feasible']]
 summary.append(dict(density=density,lengths=lengths,pool=pool,scenario=scenario,flags=k,n=100,infeasible=100-len(valid),not_estimable=sum(r['not_estimable'] for r in rr),medianV=float(np.median([r['V'] for r in valid])) if valid else None,mean_expected_gap=float(np.mean([r['expected_gap'] for r in valid])) if valid else None,mean_observed_gap=float(np.mean([r['observed_gap'] for r in valid])) if valid else None,wilson95=ci,criterion_pass=ci[1]<=.10 if scenario=='null' else ci[0]>=.80))
save('SUMMARY.json',summary);save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),records=len(records),manuscript_read=False))
