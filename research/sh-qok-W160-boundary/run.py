from pathlib import Path
import ast,json,hashlib,collections,itertools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-available-support/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh synthetic Wboundary test only; no manuscript,H/F or parsing.',rule='Unchanged W>=160,>=8supportedpages,maxshare<=.25. Boundarystrict160<W<161. Allarchitecture support verified beforeoutcomes. Frozen exacttestBonferroni8 and conditionalpositive.20ch/.35sh amongavailablefollowers.',construction='12pages4bodies;48activegroups plus48fullyblocked n20/k10 groups. Twoavailable:base n7/k3,randomly choose9or10groups to n6/k3 =>W160.286or160.714. Oneavailable:base n14/k7,random27or28groups n13/k6 =>W160.462or160.731. Mixed:24ofeachbase,random11twoavailable groups reduced plus3or4oneavailable reduced =>W160.763or160.495. Reducedgroup selections uniform beforeoutcomes,orientation and oneavailable side randomized. Fourbodylabels structural,not meanings.',seeds='Fresh1950000+architecture_index*10000+trial,200layouts perarchitecture. All four outcome scenarios independently drawn perlayout; paired not independentlayoutreplication.',gates='Eachpositive Wilson95lowerpower>=.80; eachnullupperfalseflag<=.05; eachcell200. Null scenarios low.2,high.6,additivepage/line/position. Anyfailedgate failsqualification; no retuning. Preserveeveryfalseflag/miss/design. Verify exact small-orbit oracle, blockedinvariance andsupportbounds beforeoutcomes.',limits='Balanced group-level synthetic strata,not tokenextractor. Narrow160.286..160.763,not proof precisely160 sufficient or globallyminimal. Arbitrarystratumimbalance/sparsecoverage unqualified. No manuscriptapplication.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),SRC,R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
env=dict(np=np,collections=collections,itertools=itertools,math=math)
tree=ast.parse(SRC.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['subset','support','test','ci']],type_ignores=[]),str(SRC),'exec'),env)
for n in range(1,7):
 w=[i%3-1 for i in range(n)]
 for k in range(n+1):assert env['subset'](w,k)==collections.Counter(sum(w[i] for i in ii) for ii in itertools.combinations(range(n),k))
designs=[];records=[]
for ai,architecture in enumerate(['two_available','one_available','mixed']):
 for trial in range(200):
  seed=1950000+ai*10000+trial;rng=np.random.default_rng(seed);types=[architecture=='two_available' or architecture=='mixed' and i%4%2==0 for i in range(48)]
  two=[i for i,x in enumerate(types) if x];one=[i for i,x in enumerate(types) if not x]
  nt=int(rng.choice([9,10])) if architecture=='two_available' else 11 if architecture=='mixed' else 0
  no=int(rng.choice([27,28])) if architecture=='one_available' else int(rng.choice([3,4])) if architecture=='mixed' else 0
  reduced=set(int(i) for i in rng.choice(two,nt,replace=False))|set(int(i) for i in rng.choice(one,no,replace=False));groups=[]
  for i,is_two in enumerate(types):
   n,k=((6,3) if i in reduced else (7,3)) if is_two else ((13,6) if i in reduced else (14,7));a=[1]*k+[0]*(n-k);rng.shuffle(a)
   pattern=[1,1] if is_two else [1,0] if rng.random()<.5 else [0,1]
   groups.append(dict(page=i//4,body=i%4,pattern=pattern,left=a));b=[1]*10+[0]*10;rng.shuffle(b);groups.append(dict(page=i//4,body=i%4,pattern=[0,0],left=b))
  s=env['support'](groups);assert 160<s['W']<161 and s['pass_rule'];assert s==env['support']([g for g in groups if any(g['pattern'])])
  designs.append(dict(architecture=architecture,seed=seed,**s,groups=groups))
  for scenario in ['null_low','null_high','null_nuisance','positive']:records.append(dict(architecture=architecture,trial=trial,seed=seed,scenario=scenario,**s,**env['test'](groups,scenario,rng)))
  if (trial+1)%50==0:print(architecture,trial+1,flush=True)
 save('TRIALS.json',records);save('DESIGNS.json',designs)
summary=[]
for architecture,scenario in itertools.product(['two_available','one_available','mixed'],['null_low','null_high','null_nuisance','positive']):
 rr=[r for r in records if r['architecture']==architecture and r['scenario']==scenario];k=sum(r['flag'] for r in rr);ci=env['ci'](k,200)
 summary.append(dict(architecture=architecture,scenario=scenario,flags=k,n=200,wilson95=ci,pass_gate=ci[0]>=.8 if scenario=='positive' else ci[1]<=.05,W_range=[min(r['W'] for r in rr),max(r['W'] for r in rr)],not_estimable=sum(r['not_estimable'] for r in rr)))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),exact_oracle=True,blocked_invariance=True,support_between160and161=True,records=len(records),manuscript_read=False))
