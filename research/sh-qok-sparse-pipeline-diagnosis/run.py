from pathlib import Path
import ast,json,hashlib,collections,itertools,functools,math,re,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;FILES=[P/'sh-qok-token-pipeline/run.py',P/'sh-qok-matched-effect/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-panel-support/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Paired raw-token SUPPORT diagnostic only; no outcome scoring or manuscriptreads; H/Fseparate.',base='100fresh layouts,12pages4bodies, same mixed-pattern strata as tokenpipeline:active n7/k3 twoavailable or n14/k7 oneavailable,blocked n20/k10. Core six-token lines padded to length12. BaselineW166.285714.',factorial='All16combinations of L,S,M,U on same layouts. L:append0..6dar tokens to randomize length without changing origins. S:move0..3of six fixedpaddingtokens from tail to front, preserveslength. M:replace20%of the two targetorigin words with dar (original pipeline intervention, eligibleword loss NOT physical deletion). U:mark5%of retained token identities unknown*. Random masks drawn once perlayout/line and reused across combinations; coreandpadding identities stable.',deletion='Two extra paired sensitivities:delete the M-selected origin tokens physically, alone or withL/S/U, instead of dar replacement. This changeslength/positions as well as wordpresence; report separately, not as clean factorialfactor.',seeds='Fresh2180000+trial. Fixed before any output. No qok tokens generated.',metrics='W,admission,pages,eligibleorigin count,unknownslots,meanline length,selected-group count andsource strata count. Save eachtrial/cell. Summarize pairedmeans,medians,5/95percentiles,isolatedloss and fullbackground rescue. Shapley allocation of Wloss across4factors averaged over24orders,exact identity checked; descriptive interaction allocation,not causal manuscriptattribution.',checks='Everyvariant rawserialized/reparsed with atlaspolicy; independenteligibility agrees; identitymapping preservesmaskpairing. BaselineWverified; shift-only equalbaseline lengths; L-only originpositions unchanged. Threshold160neverrelaxed. Anyfailure retained and stops; no rewriting afteroutcomes.',limits='Authored synthetic layouts; no scoring/powercalibration. Different sizepadding distribution from oldcombinedpipeline deliberate to isolate dimensions. M is replacement notdeletion. H/F realalignment untested.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
env=dict(np=np,collections=collections,functools=functools);load(FILES[2],['matching','events'],env)
matched=dict(collections=collections,env=env);load(FILES[1],['extract'],matched)
parser=dict(re=re);load(FILES[3],['parse'],parser)
ep=dict(collections=collections,matched=matched,env=env,parse=parser['parse']);load(FILES[0],['support','independent','rawround'],ep)
records=[];contributions=[]
for trial in range(100):
 seed=2180000+trial;rng=np.random.default_rng(seed);base=[]
 for pg in range(12):
  for body in range(4):
   two=body%2==0;n,k=(7,3) if two else (14,7);labels=[1]*k+[0]*(n-k);rng.shuffle(labels);pattern=[1,1] if two else [1,0] if rng.random()<.5 else [0,1]
   for available,aa in [(pattern,labels),([0,0],[1]*10+[0]*10)]:
    for left in aa:
     stem='abcd'[body]+'edy';core=['dar',('sh' if left else 'ch')+stem,'dar' if available[0] else 'chx',('ch' if left else 'sh')+stem,'dar' if available[1] else 'chx','dar']
     base.append((pg,core,int(rng.integers(7)),int(rng.integers(4)),rng.random(2)<.2,rng.random(18)<.05))
 values={}
 for cell in range(18):
  deletion=cell>=16;mask=0 if cell==16 else 15 if cell==17 else cell;rows=[]
  for pg,core,extra,shift,missing,unknown in base:
   tokens=list(enumerate(core));pad=[(6+i,'dar') for i in range(6)];front=shift if mask&2 else 0
   tokens=pad[:front]+tokens+pad[front:]
   if mask&1:tokens += [(12+i,'dar') for i in range(extra)]
   transformed=[]
   for identity,w in tokens:
    lose=identity in (1,3) and missing[0 if identity==1 else 1]
    if deletion and lose:continue
    if mask&4 and lose:w='dar'
    if mask&8 and unknown[identity]:w=None
    transformed.append(w)
   if mask==2 and not deletion:assert len(transformed)==12
   rows.append((pg,transformed))
  rows,_=ep['rawround'](rows);s=ep['support'](rows)
  if cell==0:assert abs(s['W']-166.2857142857143)<1e-8
  if cell<16:values[cell]=s['W']
  records.append(dict(trial=trial,seed=seed,cell=cell,**s,eligible_origins=sum(len(env['events'](ws)) for pg,ws in rows),unknown_slots=sum(w is None for pg,ws in rows for w in ws),mean_length=float(np.mean([len(ws) for pg,ws in rows])),page_length_strata=len({(pg,len(ws)) for pg,ws in rows}),selected_groups=len(matched['extract'](rows))))
 c=[0.]*4
 for order in itertools.permutations(range(4)):
  mask=0
  for f in order:new=mask|(1<<f);c[f]+=(values[mask]-values[new])/24;mask=new
 assert abs(sum(c)-(values[0]-values[15]))<1e-8
 contributions.append(dict(trial=trial,L=c[0],S=c[1],M=c[2],U=c[3]))
 if (trial+1)%10==0:save('TRIALS.json',records);print(trial+1,'paired layouts complete',flush=True)
summary=[]
for cell in range(18):
 rr=[r for r in records if r['cell']==cell];ww=[r['W'] for r in rr]
 summary.append(dict(cell=cell,label='deletion_only' if cell==16 else 'all_with_deletion' if cell==17 else ''.join(f for i,f in enumerate('LSMU') if cell&(1<<i)) or 'baseline',n=len(rr),meanW=float(np.mean(ww)),medianW=float(np.median(ww)),p05p95=[float(x) for x in np.quantile(ww,[.05,.95])],admitted=sum(r['admitted'] for r in rr),mean_eligible=float(np.mean([r['eligible_origins'] for r in rr]))))
save('SUMMARY.json',summary);save('SHAPLEY.json',dict(mean={f:float(np.mean([r[f] for r in contributions])) for f in 'LSMU'},trials=contributions));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),raw_roundtrips=True,independent_eligibility=True,baseline_support=True,shift_length_preserved=True,shapley_identity=True,records=len(records),outcomes_scored=False,manuscript_read=False))
