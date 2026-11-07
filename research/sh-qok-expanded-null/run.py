from pathlib import Path
import json,hashlib,sys,ast,types,itertools,collections,math
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-line-position/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic only; no manuscript reads or H/F pooling.',revision='Fixed disjoint position pairs (j,j+4), j=0..3, corresponding to source indices(1,9),(3,11),(5,13),(7,15). Within page and exact length group all lines whose two bodies are the same literal body. Secondary uses correct ending family. Keep concordant prefix rows pinned. Among discordant rows enumerate every assignment preserving the number of sh in the left column. Each arrangement preserves each line prefix/body composition and each exact-position prefix/body margin. Other cells pinned.',selection='Coordinates selected before outcomes. Bodies used for grouping; no qok or prefix-driven optimization of pairing. This is an expanded conditional subset, not all possible corpus rearrangements.',score='Total sh*qok; exact integer dynamic programming of subset sums conditional on left-sh count, convolved across disjoint groups. Uniform conditional assignments; no Monte Carlo. One-sided Bonferroni8. Score-constant null=notestimable.',fresh_seeds='984000+regime_index*1000+trial',trials=200,regimes=['page','position','line','combined','body','positive_strong','positive_small','sparse_strong','no_overlap'],generators='Reuse frozen previous generators without changes; fresh seeds. 12pages x24lines x8origins; sparse6lines and independently varying bodies. Effects .45 or .15. Run old rectangle engine on same generated data as descriptive paired comparison, not another tuning criterion.',gates='Exact oracle and margin invariants required. Primary exact-body: each nuisance Wilson95 upper flag bound<=.05; strong, small and sparse positives lower power bound>=.80; nooverlap allnotestimable. Any failure prohibits manuscript scoring. Secondary reported separately. No revised thresholds after outcomes.',limits='Synthetic event engine only. Additive-logit nuisance exchangeability, not arbitrary interactions. Four preset position-pairs may discard useful support. H/F remain separate in any future application. No manuscript rescore permitted even if pass.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),SRC,R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
# Import only function definitions from the preserved engine; no file I/O or trials.
tree=ast.parse(SRC.read_text());defs=ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)],type_ignores=[])
old=types.ModuleType('old');old.__dict__.update(np=np,math=math,itertools=itertools,ENDINGS=('edy','eey','ey','y'))
exec(compile(defs,str(SRC),'exec'),old.__dict__)
assert [old.ending(w) for w in ['shedy','sheey','shey','shy']]==['edy','eey','ey','y']
def subset(weights,k):
 dp=[collections.Counter() for _ in range(k+1)];dp[0][0]=1
 for w in weights:
  for n in range(k,0,-1):
   for total,c in list(dp[n-1].items()):dp[n][total+int(w)]+=c
 return dp[k]
for n in range(1,8):
 weights=[i%3-1 for i in range(n)]
 for k in range(n+1):
  expected=collections.Counter(sum(weights[i] for i in ix) for ix in itertools.combinations(range(n),k))
  assert subset(weights,k)==expected
def expanded(a,q,b,view):
 dist={0:1};obs=0;groups=0;informative=0
 for pg in range(a.shape[0]):
  for j in range(4):
   k=j+4;bybody={}
   for line in range(a.shape[1]):
    left,right=b[pg,line,j],b[pg,line,k]
    if view=='ending_family':left,right=old.ending(left),old.ending(right)
    if left==right and a[pg,line,j]!=a[pg,line,k]:bybody.setdefault(str(left),[]).append(line)
   for lines in bybody.values():
    groups+=1;left=a[pg,lines,j];count=int(left.sum());weights=q[pg,lines,j]-q[pg,lines,k];local=subset(weights,count)
    assert sum(local.values())==math.comb(len(lines),count)
    # Every legal orientation has one sh per selected line and count sh in left position.
    assert all(a[pg,l,j]+a[pg,l,k]==1 for l in lines)
    observed=int((left*weights).sum());lo=min(local);local={s-lo:c for s,c in local.items()};obs+=observed-lo
    if len(local)>1:informative+=1
    result=collections.Counter()
    for s,c in dist.items():
     for t,d in local.items():result[s+t]+=c*d
    dist=dict(result)
 if len(dist)==1:return dict(p_adjusted=None,flag=False,informative=0,groups=groups)
 p=min(1.,8*sum(c for s,c in dist.items() if s>=obs)/sum(dist.values()))
 return dict(p_adjusted=p,flag=p<=.05,informative=informative,groups=groups)
REG=['page','position','line','combined','body','positive_strong','positive_small','sparse_strong','no_overlap'];records=[]
for ri,reg in enumerate(REG):
 for trial in range(200):
  seed=984000+ri*1000+trial;a,q,b=old.generate(reg,np.random.default_rng(seed))
  for view in ['exact_body','ending_family']:
   z=expanded(a,q,b,view);prior=old.test(a,q,b,view)
   records.append(dict(regime=reg,trial=trial,seed=seed,view=view,**z,old_flag=prior['flag'],old_informative=prior['informative']))
 save('TRIALS.json',records);print(reg,'complete',flush=True)
summary=[]
for reg in REG:
 for view in ['exact_body','ending_family']:
  rr=[r for r in records if r['regime']==reg and r['view']==view];flags=sum(r['flag'] for r in rr);ne=sum(r['informative']==0 for r in rr);ci=old.ci(flags,200)
  passed=ne==200 if reg=='no_overlap' else ci[0]>=.8 if reg in ['positive_strong','positive_small','sparse_strong'] else ci[1]<=.05
  summary.append(dict(regime=reg,view=view,flags=flags,old_flags=sum(r['old_flag'] for r in rr),n=200,not_estimable=ne,wilson95=ci,pass_gate=passed))
save('SUMMARY.json',dict(status='PASS' if all(r['pass_gate'] for r in summary if r['view']=='exact_body') else 'FAIL',results=summary))
save('VERIFICATION.json',dict(frozen_hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),subset_oracle_checks=35,ending_unit_checks=True,records=len(records),manuscript_read=False))
