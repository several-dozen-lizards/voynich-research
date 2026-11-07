from pathlib import Path
import ast,types,json,hashlib,itertools,collections,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
FILES=[P/'sh-qok-support-rule/run.py',P/'sh-qok-sparse-diagnosis/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh synthetic boundary qualification; no manuscript/H/F data loaded.',support='Unchanged body-selected matching and support rule, restricted to80<=V<84, >=8supported pages and <=.25 maximum page share. Selection uses only bodies/prefixes/positions. Outcomes generated after acceptance.',sampling='For each aligned/fragmented body layout and iid/additive prefix design accept first200 qualifying independent datasets, cap20000attempts.12pages8positions. Uniform random line count14..26 aligned,56..112 fragmented. iid prefixes p=.5; additive logit page+line+position amplitudes.5. Body layout as previous diagnostic. All attempted support records retained. Fresh seed1030000+layout_index*10000+design_index*1000+attempt; separate outcome rng seed+500000.',outcomes='For each accepted iid dataset independent qok draws in four scenarios: null baseline.2, null baseline.6, positive baseline.2 plus.15*sh, positive baseline.6 plus.15*sh. Additive accepted datasets receive independent qok with same nuisance probabilities as prefixes, no direct association. Reused prefix design across scenarios is paired, not independent replication.',test='Unchanged exact conditional engine, body-selected matching, one-sided Bonferroni8. Exactbody only. V80not changed. No postoutcome filtering.',gates='Each of10layout/scenario cells requires200accepted datasets. Each positive Wilson95 lower power>=.80; each null Wilson95 upper falseflag<=.05 (stricter than previous .10). Any failure or missingquota fails boundary qualification. Record notestimable, pvalues, support and rejected attempts. Never rescore manuscript.',limits='Tests narrow support band under these two architectures and effects only; not proof of universal sufficiency. No claim that80 is smallest sufficient threshold. Parsing and actual coverage untested.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,env):exec(compile(ast.Module(body=[x for x in ast.parse(path.read_text()).body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),str(path),'exec'),env)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[2],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,itertools=itertools,m=m);load(FILES[1],['matchings','test','ci'],env);env['MATCH']=list(env['matchings'](list(range(8))));se=dict(np=np,collections=collections,env=env);load(FILES[0],['support'],se)
records=[];attempts=[]
for li,layout in enumerate(['aligned','fragmented']):
 for di,design in enumerate(['iid','additive']):
  accepted=0
  for attempt in range(20000):
   seed=1030000+li*10000+di*1000+attempt;rng=np.random.default_rng(seed);L=int(rng.integers(14,27) if layout=='aligned' else rng.integers(56,113));shape=(12,L,8)
   b=np.broadcast_to(np.arange(8)%4,shape).copy() if layout=='aligned' else rng.integers(4,size=shape)
   prob=np.full(shape,.5)
   if design=='additive':
    z=rng.choice([-.5,.5],size=(12,1,1))+rng.choice([-.5,.5],size=(12,L,1))+np.array([-.5,.5]*4)[None,None,:];prob=1/(1+np.exp(-z))
   a=(rng.random(shape)<prob).astype(int);s=se['support'](a,b);ok=s['admitted'] and 80<=s['V']<84
   attempts.append(dict(layout=layout,design=design,attempt=attempt,seed=seed,lines=L,accepted=ok,**s))
   if not ok:continue
   qrng=np.random.default_rng(seed+500000)
   scenarios=[('additive_null',prob)] if design=='additive' else [('null_low',.2),('null_high',.6),('positive_low',.2+.15*a),('positive_high',.6+.15*a)]
   for scenario,qp in scenarios:
    q=(qrng.random(shape)<qp).astype(int);result=env['test'](a,q,b,'body_selected')
    records.append(dict(layout=layout,scenario=scenario,seed=seed,lines=L,**s,**result))
   accepted+=1
   if accepted==200:break
  save('ATTEMPTS.json',attempts);save('TRIALS.json',records);print(layout,design,'accepted',accepted,'attempts',attempt+1,flush=True)
summary=[]
for layout in ['aligned','fragmented']:
 for scenario in ['null_low','null_high','positive_low','positive_high','additive_null']:
  rr=[r for r in records if r['layout']==layout and r['scenario']==scenario];n=len(rr);k=sum(r['flag'] for r in rr);ci=env['ci'](k,n) if n else [0,1]
  passed=n==200 and (ci[0]>=.80 if scenario.startswith('positive') else ci[1]<=.05)
  summary.append(dict(layout=layout,scenario=scenario,n=n,flags=k,wilson95=ci,pass_gate=passed,V_range=[min(r['V'] for r in rr),max(r['V'] for r in rr)] if rr else [],not_estimable=sum(r['p_adjusted'] is None for r in rr)))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary))
save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),outcomes_generated_after_acceptance=True,records=len(records),attempts=len(attempts),manuscript_read=False))
