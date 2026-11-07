from pathlib import Path
import json,hashlib,ast,types,collections,itertools,math,sys,functools
import numpy as np
R=Path(__file__).resolve().parent;SRC=R.parent/'sh-qok-expanded-null/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic tokens only; no manuscript reads or scoring; H/F not pooled.',revision='Every source origin index1..length-2 considered. Match disjoint position pairs with exact maximum-weight matching perpage/exactlength. Edge weight=sum n*(n-1)/2 across literal bodies shared byboth positions in nlines. Uses origin eligibility and bodies, not prefix orientation or following identity. Deterministic lexicographic tie; zero-support edges omitted. Allpositions considered, not all necessarily selected.',null='Preserve line sh/ch counts, exact sourceposition margins, exactbody and length. Existing exact conditional subset-sum test within selectedpair/body groups. Discordant-row orientations permuted across compatible lines. Outcomes fixed, one-sidedBonferroni8. Constant score null=notestimable. No pooling lengths or bodies.',synthetic='12pages x24lines. sparse:uniformlength6..14, originprob.35,12bodies,independent2%unknownslots. dense diagnostic:length12,originprob.70,4bodies,nounknowns. Bodies literal unique cores plus disjoint edy/eey/ey/y. Origins assigned before outcomes; other tokens qokam/dar. qok never overwrites origins. Prefixvariant probability .5 or nuisance logistic. qok probability baseline.2/.6; positives+.15 or+.45 only if preceding origin is sh. Nuisance prefix and qok independently depend on additive page+line+position logits. First/last origins excluded; unknownfollowing blocks events; no repacking.',cells='100fresh datasets each sparse/dense x null_low,null_nuisance,positive_small_low,positive_small_high,positive_strong. Seeds1050000+cell*1000+trial.',gates='Each nullWilson95 upperflag<=.10; positive lowerpower>=.80 separately eachcell; all failures preserved. Broad qualification requiresallgates. Notestimable counts as nondetection for power, not negativeassociation. Report V>=80/eightpage/.25share coverage descriptively; earlier support qualification not automatically inherited. Require independent matchingoracle, subsetoracle, rawtokenboundary fixtures.',limits='Sparse controls are plausible authored stress scenarios, not fitted manuscript distributions. Dense control not a substitute for sparse power. Full corpus parsing/HF coverage remains unqualified. No rescoring even if passes.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SRC]});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
m=types.ModuleType('subset');m.__dict__.update(collections=collections)
exec(compile(ast.Module(body=[n for n in ast.parse(SRC.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='subset'],type_ignores=[]),str(SRC),'exec'),m.__dict__)
def matching(positions,weights):
 @functools.lru_cache(None)
 def solve(xs):
  if not xs:return (0,())
  a=xs[0];best=solve(xs[1:])
  for b in xs[1:]:
   w=weights.get((a,b),0)
   if w<=0:continue
   v,pairs=solve(tuple(x for x in xs[1:] if x!=b));cand=(v+w,((a,b),)+pairs)
   if cand[0]>best[0] or (cand[0]==best[0] and cand[1]<best[1]):best=cand
  return best
 return solve(tuple(positions))
assert matching(range(4),{(0,1):3,(0,2):4,(1,3):4,(2,3):3})[0]==8
def brute(xs,w):
 if not xs:return 0
 a=xs[0];return max([brute(xs[1:],w)]+[w.get((a,b),0)+brute([x for x in xs[1:] if x!=b],w) for b in xs[1:]])
for seed in range(20):
 rng=np.random.default_rng(seed);w={(a,b):int(rng.integers(5)) for a in range(6) for b in range(a+1,6)};assert matching(range(6),w)[0]==brute(list(range(6)),w)
for k in range(5):assert m.subset([-1,0,1,1],k)==collections.Counter(sum([-1,0,1,1][i] for i in ix) for ix in itertools.combinations(range(4),k))
def events(ws):
 return {i:(w[2:],int(w.startswith('sh')),int(ws[i+1].startswith('qok'))) for i,w in enumerate(ws) if 0<i<len(ws)-1 and w and ws[i+1] and w.startswith(('sh','ch')) and any(w.endswith(e) for e in ['edy','eey','ey','y'])}
assert events(['shedy','shedy',None,'chedy','dar','shedy'])=={3:('edy',0,0)}
def generate(layout,scenario,rng):
 rows=[];pool=['a','o','e','i','l','r','s','d','n','v','c','x'];ends=['edy','eey','ey','y']
 for pg in range(12):
  pe=float(rng.choice([-.7,.7]))
  for line in range(24):
   L=int(rng.integers(6,15)) if layout=='sparse' else 12;le=float(rng.choice([-.7,.7]));orig=rng.random(L)<(.35 if layout=='sparse' else .70)
   variant=[];prob=[]
   for j in range(L):
    p=1/(1+math.exp(-(pe+le+(.7 if j%2 else -.7)))) if scenario=='null_nuisance' else .5;prob.append(p);variant.append(int(rng.random()<p))
   ws=[]
   for j in range(L):
    if orig[j]:
     bi=int(rng.integers(12 if layout=='sparse' else 4));ws.append(('sh' if variant[j] else 'ch')+pool[bi]+ends[bi%4])
    else:
     base=prob[j] if scenario=='null_nuisance' else .6 if scenario=='positive_small_high' else .2
     effect=.45 if scenario=='positive_strong' else .15 if scenario.startswith('positive') else 0
     qp=base+effect*(j>0 and orig[j-1] and variant[j-1]);ws.append('qokam' if rng.random()<qp else 'dar')
   if layout=='sparse':ws=[None if rng.random()<.02 else w for w in ws]
   rows.append((pg,ws))
 return rows
def score(rows):
 strata=collections.defaultdict(list);eligible=0
 for pg,ws in rows:e=events(ws);eligible+=len(e);strata[pg,len(ws)].append(e)
 dist={0:1};obs=0;vpages=[0.]*12;pairs_count=0
 for (pg,L),lines in strata.items():
  weights={}
  for j in range(1,L-1):
   for k in range(j+1,L-1):
    cc=collections.Counter(e[j][0] for e in lines if j in e and k in e and e[j][0]==e[k][0]);weights[j,k]=sum(n*(n-1)//2 for n in cc.values())
  _,pairs=matching(range(1,L-1),weights);pairs_count+=len(pairs)
  for j,k in pairs:
   groups=collections.defaultdict(list)
   for e in lines:
    if j in e and k in e and e[j][0]==e[k][0] and e[j][1]!=e[k][1]:groups[e[j][0]].append((e[j][1],e[j][2]-e[k][2]))
   for group in groups.values():
    n=len(group);ns=sum(x for x,d in group);vpages[pg]+=ns*(n-ns)/n;local=m.subset([d for x,d in group],ns);assert sum(local.values())==math.comb(n,ns)
    lo=min(local);obs+=sum(x*d for x,d in group)-lo;new=collections.Counter()
    for s,c in dist.items():
     for t,z in local.items():new[s+t-lo]+=c*z
    dist=dict(new)
 V=sum(vpages);p=min(1.,8*sum(c for t,c in dist.items() if t>=obs)/sum(dist.values())) if len(dist)>1 else None
 return dict(p_adjusted=p,flag=p is not None and p<=.05,V=V,eligible_origins=eligible,selected_pairs=pairs_count,not_estimable=p is None,support_rule=V>=80 and sum(v>0 for v in vpages)>=8 and max(vpages)/V<=.25 if V else False)
def ci(k,n):
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d;return [max(0,c-h),min(1,c+h)]
cells=list(itertools.product(['sparse','dense'],['null_low','null_nuisance','positive_small_low','positive_small_high','positive_strong']));records=[]
for ix,(layout,scenario) in enumerate(cells):
 for trial in range(100):
  seed=1050000+ix*1000+trial;records.append(dict(layout=layout,scenario=scenario,trial=trial,seed=seed,**score(generate(layout,scenario,np.random.default_rng(seed)))))
 save('TRIALS.json',records);print(layout,scenario,'complete',flush=True)
summary=[]
for layout,scenario in cells:
 rr=[r for r in records if r['layout']==layout and r['scenario']==scenario];k=sum(r['flag'] for r in rr);bounds=ci(k,100)
 summary.append(dict(layout=layout,scenario=scenario,flags=k,n=100,wilson95=bounds,pass_gate=bounds[1]<=.10 if scenario.startswith('null') else bounds[0]>=.80,not_estimable=sum(r['not_estimable'] for r in rr),support_pass=sum(r['support_rule'] for r in rr),medianV=float(np.median([r['V'] for r in rr]))))
save('SUMMARY.json',dict(status='PASS' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),matching_oracles=20,subset_oracle=True,token_boundary_fixture=True,records=len(records),manuscript_read=False))
