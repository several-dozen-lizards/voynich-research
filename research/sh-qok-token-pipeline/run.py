from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,re,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
FILES=[P/'sh-qok-panel-support/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-matched-effect/run.py',P/'sh-qok-expanded-null/run.py',P/'sh-qok-availability-controlled/ch/run.py',P/'sh-qok-available-support/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Raw synthetic transcription to tokens to availabilitycontrolledtest. No manuscriptreads/HFpooling.',rule='Frozen W>=160,>=8pages,maxshare<=.25. W=k(n-k)/n times countavailablefollowers perpatternstratum; do not count blocked variation. ExacttestBonferroni8. Low-support cases abstain but diagnostic p retained separately.',design='Fresh200layouts:100dense,100sparse. Each12pages4bodies48activegroups plus48blocked. Active n7/k3 for twoavailable or n14/k7 for oneavailable; alternatebodytype=>W166.2857. Tokenize each row as dar.origin.follower.origin.follower.dar. Structural unavailable follower chx (excluded from eligible suffixes). Sparse:random0..3paddingtokens at each end,20%origins replaced dar,5%slots unknown*,suffixbody intact. These stress assumptions not fittedhistoricaldata.',raw='Serialize tokens with dots, inject ! inside readable words deterministically, retain terminal dash and trailing #comment. Parse with frozenatlaspolicy. Sparse uncertain tokens retain their slots. Separate fixed fixtures exercise commas,bracecomments,unknownbarriers and paragraphterminators. H/F-style alternatives use differing rawboundaries and stay in separate testfixtures, never pooled.',outcomes='Independent null.2,.6,nuisancepage/line/position logits; positive.2/.35 on availablefollowers of eligible ch/sh. Generate after sparse alterations; do not overwrite eligible origins or chx. Frozen seeds2050000+mode*10000+trial.4outcomes perlayout.',verification='Rawroundtrip every generatedline,independenteligibilityloop versus productionevents,selectedgroups invariant acrossoutcomes, denseextractedW equals166.2857, prefixavailabilitypatternsupport recalculated, availabilityscore directsum distribution via independent tuple assignment oracle smallfixture. Only rawparser and functions imported, never module toplevel/corpusreads.',gates='Anyverificationfailure stops. Dense eachcell100 accepted:positive lowerWilson95>=.80,nullupper<=.10. Sparse eachcell requires>=50supportaccepted trials then samegates; fewer is unsupportedqualification, not negativeeffect. Preserve all misses,excluded cases and diagnostic scores; no relaxedthresholds. Evenpass is synthetic only.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[3],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(FILES[1],['matching','events','ci'],env)
matched=dict(collections=collections,env=env);load(FILES[2],['extract'],matched)
sc=dict(collections=collections,math=math,m=m,matched=matched);load(FILES[4],['availability_score'],sc)
parser=dict(re=re);load(FILES[0],['parse'],parser);parse=parser['parse']
def independent(ws):
 result={}
 for i in range(1,len(ws)-1):
  w=ws[i]
  if w is None or ws[i+1] is None:continue
  if w[:2] not in ('ch','sh'):continue
  if not any(w[-len(s):]==s for s in ('edy','eey','ey','y')):continue
  result[i]=(w[2:],int(w[:2]=='sh'),int(ws[i+1][:3]=='qok'))
 return result
fixtures=[('a.sh!edy.*.chedy.dar-',['a','shedy',None,'chedy','dar']),('a.shedy,chedy.dar-',['a',None,None,'dar']),('a.{note}shedy.dar-',['a',None,'dar']),('a.shedy.dar={end} #comment',['a','shedy','dar'])]
for raw,want in fixtures:assert parse(raw)==want and env['events'](want)==independent(want)
# Separate alternate boundaries, never concatenate or align by repacking.
assert parse('a.shedy.dar-')!=parse('a.sh.edy.dar-')
for k in range(5):assert m.subset([-1,0,1,1],k)==collections.Counter(sum([-1,0,1,1][i] for i in ii) for ii in itertools.combinations(range(4),k))
def support(rows):
 groups=matched['extract'](rows);pv=collections.defaultdict(float)
 for v,entries in groups:
  strata=collections.defaultdict(list)
  for ri,j,k,left in entries:
   pattern=tuple(not rows[ri][1][p+1].startswith(('sh','ch')) for p in (j,k));strata[pattern].append(left)
  pg=rows[entries[0][0]][0]
  for pattern,a in strata.items():pv[pg]+=sum(a)*(len(a)-sum(a))/len(a)*sum(pattern)
 W=sum(pv.values());return dict(W=W,pages=sum(v>0 for v in pv.values()),share=max(pv.values())/W if W else None,admitted=W>=160 and sum(v>0 for v in pv.values())>=8 and max(pv.values())/W<=.25 if W else False)
def rawround(rows):
 out=[];raws=[]
 for pg,ws in rows:
  raw='.'.join('*' if w is None else w[0]+'!'+w[1:] for w in ws)+'- #synthetic';parsed=parse(raw);assert parsed==ws;assert env['events'](parsed)==independent(parsed);out.append((pg,parsed));raws.append(dict(page=pg,raw=raw))
 return out,raws
records=[];designs=[]
for mi,mode in enumerate(['dense','sparse']):
 for trial in range(100):
  seed=2050000+mi*10000+trial;rng=np.random.default_rng(seed);rows=[]
  for pg in range(12):
   for body in range(4):
    two=body%2==0;n,k=(7,3) if two else (14,7);active=[1]*k+[0]*(n-k);rng.shuffle(active);pattern=[1,1] if two else [1,0] if rng.random()<.5 else [0,1]
    for availability,labels in [(pattern,active),([0,0],[1]*10+[0]*10)]:
     for left in labels:
      stem='abcd'[body]+'edy';ws=['dar',('sh' if left else 'ch')+stem,'dar' if availability[0] else 'chx',('ch' if left else 'sh')+stem,'dar' if availability[1] else 'chx','dar']
      if mode=='sparse':
       for j in [1,3]:
        if rng.random()<.2:ws[j]='dar'
       ws=['dar']*int(rng.integers(4))+ws+['dar']*int(rng.integers(4));ws=[None if rng.random()<.05 else w for w in ws]
      rows.append((pg,ws))
  rows,raws=rawround(rows);s=support(rows);groups=matched['extract'](rows)
  if mode=='dense':assert abs(s['W']-166.2857142857143)<1e-8 and s['admitted']
  designs.append(dict(mode=mode,seed=seed,**s,raw_lines=raws))
  for scenario in ['null_low','null_high','null_nuisance','positive']:
   new=[];pe=rng.choice([-.7,.7],size=12)
   for pg,ws in rows:
    le=float(rng.choice([-.7,.7]));out=[]
    for j,w in enumerate(ws):
     if w is None or w.startswith(('sh','ch')):out.append(w);continue
     prob=.6 if scenario=='null_high' else 1/(1+math.exp(-(pe[pg]+le+(.7 if j%2 else -.7)))) if scenario=='null_nuisance' else .2
     if scenario=='positive' and j>0 and ws[j-1] and ws[j-1].startswith('sh'):prob=.35
     out.append('qokam' if rng.random()<prob else 'dar')
    new.append((pg,out))
   new,_=rawround(new);assert matched['extract'](new)==groups and support(new)==s
   score=sc['availability_score'](new);records.append(dict(mode=mode,trial=trial,seed=seed,scenario=scenario,**s,diagnostic_p=score['p_adjusted'],diagnostic_flag=score['flag'],flag=s['admitted'] and score['flag'],not_estimable=score['not_estimable']))
  if (trial+1)%25==0:print(mode,trial+1,flush=True)
 save('TRIALS.json',records);save('DESIGNS.json',designs)
summary=[]
for mode,scenario in itertools.product(['dense','sparse'],['null_low','null_high','null_nuisance','positive']):
 rr=[r for r in records if r['mode']==mode and r['scenario']==scenario];yes=[r for r in rr if r['admitted']];n=len(yes);k=sum(r['flag'] for r in yes);ci=env['ci'](k,n) if n else None
 status='UNSUPPORTED' if n<(100 if mode=='dense' else 50) else 'PASS' if (ci[0]>=.8 if scenario=='positive' else ci[1]<=.1) else 'FAIL'
 summary.append(dict(mode=mode,scenario=scenario,admitted=n,total=100,flags=k,wilson95=ci,status=status,medianW=float(np.median([r['W'] for r in rr])),diagnostic_flags=sum(r['diagnostic_flag'] for r in rr)))
save('SUMMARY.json',dict(status='PASS' if all(r['status']=='PASS' for r in summary) else 'NOT_FULLY_QUALIFIED',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),all_raw_roundtrips=True,independent_eligibility_checks=True,source_lengths_unknowns_preserved=True,matching_support_outcome_invariance=True,subset_oracle=True,records=len(records),manuscript_read=False))
