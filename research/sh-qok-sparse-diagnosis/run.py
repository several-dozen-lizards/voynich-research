from pathlib import Path
import json,hashlib,ast,types,collections,itertools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-expanded-null/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic diagnosis only. No Voynich reads, no H/F pooling or rescoring.',factorial='12pages; lines/page6,24,96; bodies independent across cells (fragmented) versus four repeated position bodies shared across lines (aligned). Prefix/outcome effect0 under additive page+line+position logit nuisance, or strong+.45 and smaller+.15 with random prefix p=.5 and outcome baseline.2. 100 independent datasets per18cells. Fresh seeds995000+cell_index*1000+trial.',methods='Fixed original position pairs versus body-only selected matching. Enumerate all105 perfect matchings of8positions perpage, select maximum sum overbodygroups n*(n-1)/2 where n counts lines with matching body in paired slots. Tie lexicographically. Selection never reads prefix or qok. Same dataset and margins for both. This changes selected disjoint subspace, not complete-fiber enumeration; it does not guarantee a superset of the fixed null.',statistics='Exact conditional subset-sum null as previous engine, primary exactbody only, Bonferroni8. Record actual p, best attainable corrected p=maxscore mass/total*8, log2 assignments, nonconstant score, number groups. Outcome-constant records kept notestimable. Maximum-score floor conditional on fixed qok, not unconditional power.',interpretation='Paired method improvement at same data implicates excluded arrangements. Quantity improvement within same layout/method implicates support volume. Alignment improvement at same quantity implicates distribution of comparable bodies, not a change to matching rules. No improvement does not prove complete-fiber exhaustion. Report all outcomes and intervals, no posthoc winner.',checks='Exhaustive oracle subset distribution;105unique matchings cover everyposition once. Null screening Wilson95 upperflagbound<=.10 in each diagnosticcell/method; power descriptive with lowerbound>=.80 marked qualified only for that synthetic cell, not Voynich. Report failures. No repairs after outcomes.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),SRC,R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
tree=ast.parse(SRC.read_text());m=types.ModuleType('prior');m.__dict__.update(collections=collections,np=np,math=math)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='subset'],type_ignores=[]),str(SRC),'exec'),m.__dict__)
def matchings(xs):
 if not xs:yield ();return
 a=xs[0]
 for b in xs[1:]:
  for rest in matchings([x for x in xs[1:] if x!=b]):yield ((a,b),)+rest
MATCH=list(matchings(list(range(8))));assert len(set(MATCH))==105
assert all(sorted(x for pair in mm for x in pair)==list(range(8)) for mm in MATCH)
for w in [[-1,0,1,1],[1,-1,0,1,-1]]:
 for k in range(len(w)+1):assert m.subset(w,k)==collections.Counter(sum(w[i] for i in inds) for inds in itertools.combinations(range(len(w)),k))
def test(a,q,b,method):
 dist={0:1};obs=0;groups=0
 for pg in range(12):
  pairs=tuple((j,j+4) for j in range(4))
  if method=='body_selected':
   score={}
   for j in range(8):
    for k in range(j+1,8):
     counts=collections.Counter(b[pg,l,j] for l in range(a.shape[1]) if b[pg,l,j]==b[pg,l,k]);score[j,k]=sum(n*(n-1)//2 for n in counts.values())
   pairs=max(MATCH,key=lambda mm:sum(score[p] for p in mm))
  for j,k in pairs:
   groups_by_body={}
   for line in range(a.shape[1]):
    if b[pg,line,j]==b[pg,line,k] and a[pg,line,j]!=a[pg,line,k]:groups_by_body.setdefault(int(b[pg,line,j]),[]).append(line)
   for lines in groups_by_body.values():
    left=a[pg,lines,j];weights=q[pg,lines,j]-q[pg,lines,k];count=int(left.sum());local=m.subset(weights,count)
    assert sum(local.values())==math.comb(len(lines),count)
    lo=min(local);obs+=int((left*weights).sum())-lo;local={s-lo:c for s,c in local.items()}
    if len(local)>1:groups+=1
    new=collections.Counter()
    for s,c in dist.items():
     for t,d in local.items():new[s+t]+=c*d
    dist=dict(new)
 total=sum(dist.values());floor=min(1.,8*dist[max(dist)]/total);p=min(1.,8*sum(c for s,c in dist.items() if s>=obs)/total)
 return dict(flag=p<=.05,p_adjusted=p if len(dist)>1 else None,best_attainable_p=floor,threshold_attainable=floor<=.05,log2_assignments=math.log2(total),informative_groups=groups)
def generate(L,layout,effect,rng):
 shape=(12,L,8);b=rng.integers(4,size=shape) if layout=='fragmented' else np.broadcast_to(np.arange(8)%4,shape).copy()
 if effect==0:
  z=rng.choice([-1.5,1.5],size=(12,1,1))+rng.choice([-1.5,1.5],size=(12,L,1))+np.array([-1.5,1.5]*4)[None,None,:];p=1/(1+np.exp(-z));a=(rng.random(shape)<p).astype(int);q=(rng.random(shape)<p).astype(int)
 else:a=(rng.random(shape)<.5).astype(int);q=(rng.random(shape)<.2+effect*a).astype(int)
 return a,q,b
def ci(k,n):
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [max(0.,c-h),min(1.,c+h)]
records=[];cells=list(itertools.product([6,24,96],['fragmented','aligned'],[0,.15,.45]))
for ix,(L,layout,effect) in enumerate(cells):
 for trial in range(100):
  seed=995000+ix*1000+trial;a,q,b=generate(L,layout,effect,np.random.default_rng(seed))
  for method in ['fixed','body_selected']:records.append(dict(lines=L,layout=layout,effect=effect,trial=trial,seed=seed,method=method,**test(a,q,b,method)))
 save('TRIALS.json',records);print(L,layout,effect,'complete',flush=True)
summary=[]
for L,layout,effect in cells:
 for method in ['fixed','body_selected']:
  rr=[r for r in records if (r['lines'],r['layout'],r['effect'],r['method'])==(L,layout,effect,method)];flags=sum(r['flag'] for r in rr);bounds=ci(flags,100)
  summary.append(dict(lines=L,layout=layout,effect=effect,method=method,flags=flags,n=100,wilson95=bounds,criterion_pass=bounds[1]<=.10 if effect==0 else bounds[0]>=.80,attainable=sum(r['threshold_attainable'] for r in rr),not_estimable=sum(r['p_adjusted'] is None for r in rr),median_log2_assignments=float(np.median([r['log2_assignments'] for r in rr]))))
save('SUMMARY.json',summary);save('VERIFICATION.json',dict(frozen_hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),matching_checks=True,subset_oracle=True,records=len(records),manuscript_read=False))
