from pathlib import Path
import ast,types,json,hashlib,itertools,collections,math,sys
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-sparse-diagnosis/run.py';SUB=R.parent/'sh-qok-expanded-null/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic support-rule qualification only; manuscript closed, H/F never pooled.',rule='Use body-selected position matching from preceding diagnostic. In each discordant-row group with n lines and k left-sh, support Vg=k*(n-k)/n. Sum Vg >=80, at least8pages with V>0, and max page share<=.25. Uses bodies, positions and prefix margins only; never qok or outcomes. Threshold80 is a proposed conservative design threshold, not an empirically established minimum.',target='Detect conditional+.15 qok probability at baseline.2 or.6, exact one-sided test Bonferroni8. This is minimum-effect-specific, not capacity to detect arbitrarily small associations.',design='100fresh datasets for each4designs:6fragmented,24fragmented,96fragmented,24aligned lines/page;12pages8positions. Scenarios iidnull psh=pq=.5; additive-null logit page+line+position amplitudes.5 for both independently;+.15 at baseline.2;+.15 at baseline.6. Prefixes p=.5 for positives. Fresh seeds1010000+cell*1000+trial.',gates='Every approved positive cell needs>=50 eligible trials and Wilson95 lower power>=.80. Every approved null cell needs>=50 eligible trials and upper false-flag bound<=.10. Cells with zero admissions are excluded scope, not failed effects; 1..49 admissions are insufficient qualification and fail broad rule. At least one eligible cell for each scenario required. Rejects retained unscored. Do not change threshold after results. Any power/calibration/coverage failure blocks general support-rule qualification.',verification='Support independence from outcomes is checked by complementing qok on every dataset. Imported exact engine unchanged, hash frozen. Eligibility selection precedes p calculation. No manuscript application even if synthetic passes.',limits='V is assignment variation, not observed outcome variation. Body-selected matchings only, event-level generator, fixed lengths. Does not establish actual manuscript availability, parsing or H/F alignment. Sparse design rejection is abstention, not negative evidence.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),SRC,SUB,R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def loaddefs(path,names,env):
 tree=ast.parse(path.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),env)
m=types.ModuleType('subset');loaddefs(SUB,['subset'],m.__dict__|{}) if False else None
m.__dict__.update(collections=collections);loaddefs(SUB,['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,itertools=itertools,m=m)
loaddefs(SRC,['matchings','test','generate','ci'],env);env['MATCH']=list(env['matchings'](list(range(8))))
def support(a,b):
 pages=[]
 for pg in range(12):
  scores={}
  for j in range(8):
   for k in range(j+1,8):
    c=collections.Counter(b[pg,l,j] for l in range(a.shape[1]) if b[pg,l,j]==b[pg,l,k]);scores[j,k]=sum(n*(n-1)//2 for n in c.values())
  pairs=max(env['MATCH'],key=lambda mm:sum(scores[p] for p in mm));v=0.
  for j,k in pairs:
   groups={}
   for l in range(a.shape[1]):
    if b[pg,l,j]==b[pg,l,k] and a[pg,l,j]!=a[pg,l,k]:groups.setdefault(int(b[pg,l,j]),[]).append(int(a[pg,l,j]))
   for x in groups.values():v+=sum(x)*(len(x)-sum(x))/len(x)
  pages.append(v)
 total=sum(pages);n=sum(v>0 for v in pages);share=max(pages)/total if total else 1.
 return dict(V=total,supported_pages=n,max_page_share=share,admitted=total>=80 and n>=8 and share<=.25)
cells=list(itertools.product([(6,'fragmented'),(24,'fragmented'),(96,'fragmented'),(24,'aligned')],['null','null_line','small_low','small_high']));records=[]
for cell,((L,layout),scenario) in enumerate(cells):
 for trial in range(100):
  seed=1010000+cell*1000+trial;rng=np.random.default_rng(seed);shape=(12,L,8)
  b=rng.integers(4,size=shape) if layout=='fragmented' else np.broadcast_to(np.arange(8)%4,shape).copy()
  p=np.full(shape,.5)
  if scenario=='null_line':
   z=rng.choice([-.5,.5],size=(12,1,1))+rng.choice([-.5,.5],size=(12,L,1))+np.array([-.5,.5]*4)[None,None,:];p=1/(1+np.exp(-z))
  a=(rng.random(shape)<p).astype(int);prob=p if scenario.startswith('null') else (.2 if scenario=='small_low' else .6)+.15*a
  q=(rng.random(shape)<prob).astype(int);s=support(a,b)
  # API has no outcome argument: support cannot access q; call with same inputs after complement.
  qc=1-q;assert s==support(a,b)
  result=env['test'](a,q,b,'body_selected') if s['admitted'] else None
  records.append(dict(lines=L,layout=layout,scenario=scenario,trial=trial,seed=seed,**s,result=result))
 save('TRIALS.json',records);print(L,layout,scenario,'complete',flush=True)
summary=[]
for (L,layout),scenario in cells:
 rr=[r for r in records if (r['lines'],r['layout'],r['scenario'])==(L,layout,scenario)];yes=[r for r in rr if r['admitted']];n=len(yes);k=sum(r['result']['flag'] for r in yes);bounds=env['ci'](k,n) if n else None
 status='excluded_scope' if n==0 else 'insufficient_trials' if n<50 else 'PASS' if (bounds[1]<=.10 if scenario.startswith('null') else bounds[0]>=.80) else 'FAIL'
 summary.append(dict(lines=L,layout=layout,scenario=scenario,admitted=n,total=100,flags=k,wilson95=bounds,status=status,V_median=float(np.median([r['V'] for r in rr]))))
passed=all(r['status'] in ['PASS','excluded_scope'] for r in summary) and all(any(r['scenario']==sc and r['status']=='PASS' for r in summary) for sc in ['null','null_line','small_low','small_high'])
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if passed else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),support_has_no_outcome_argument=True,records=len(records),manuscript_read=False))
