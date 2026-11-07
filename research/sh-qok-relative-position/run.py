from pathlib import Path
import ast,json,hashlib,collections,itertools,math,re,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
FILES=[P/'sh-qok-panel-support/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic raw-token qualification only. No manuscript files or H/F readings loaded.',candidate='Choose lexicographically first nonoverlapping eligible same-body pair per line without looking at prefix variant or follower outcome. Retain discordant sh/ch pairs. Group by page, exact body, ordered relative-position thirds floor(3*i/(L-1)) capped2, and ordered structural follower availability. Conditional exact subset test preserves one sh per retained line and stratum left-sh totals. Exact length and exact absolute positions no longer held fixed; this is the hypothesis being challenged.',support='W=sum k(n-k)/n times available followers. Retain W>=160, >=8positive pages, maxshare<=.25 as candidate gate, NOT inherited proof of power. Bonferroni8; alpha.05.',design='100fresh trials per volume1 and4, each12pages4bodies; perpage/body volume*(7twoavailable or14oneavailable) plus20blocked lines. Randomfront0..3, back6..12;20%origin replacement,5%unknown tokens. Extra volume explicitly adds data, not a rescue of original sample. Seeds2410000+volume*10000+trial*10+scenarioindex. Five scenarios: null_low .2, null_high .6, null_layout, null_nonlinear, positive .20ch/.35sh amongavailablefollowers. Every scenario has fresh token layouts.',layout_null='Shared placement only, no prefix term in follower probabilities. Left-sh probability sigmoid(5*(zleft-zright)); outcomes sigmoid(pageeffect+lineeffect+zposition). Smooth z=6*(relativeposition-.4). Nonlinear z=2.5 if absoluteindex even else -2.5, plus 2*sin(4*pi*relativeposition). This challenges residual within-bin trends and shifted parity. Null_low/high/positive use random.5 orientation. Availability blocked by literal chx independently of orientation.',gates='Each cell100 attempted; supportadmitted>=80. Conditional power Wilson95lower>=.80 and practical power overall100 lower>=.80. Each null admitted Wilson95upper<=.10. Unsupported below80 admission; failed rates retained even if unsupported. Allcells mustpass. Report diagnostics for all attempted, no thresholdchanges or new seeds after outcomes.',verification='Reuse parser/events as function-only AST loads. All generated raw lines roundtrip preserving unknown slots. Pair grouping and support invariant under outcomes. Exact subset smallcase exhaustive oracle. Frozen source/protocol/import hashes checked. Synthetic availability definition does not qualify real-world availability inference.',limits='First-pair selection and coarse thirds are frozen choices, not optimized. Additional sample volume is separate. Failure of this candidate does not rule out all shift-tolerant methods. No semantic or grammar claims.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(p,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),e)
e={'re':re,'math':math,'collections':collections};load(FILES[0],['parse'],e);load(FILES[1],['events','ci'],e);load(FILES[2],['subset'],e)
for n in range(1,7):
 for k in range(n+1):
  w=[i%3-1 for i in range(n)];assert e['subset'](w,k)==collections.Counter(sum(w[i] for i in ix) for ix in itertools.combinations(range(n),k))
def groups(rows):
 out=collections.defaultdict(list)
 for ri,(pg,ws) in enumerate(rows):
  ev=e['events'](ws);pairs=[(j,k) for j,k in itertools.combinations(sorted(ev),2) if k>j+1 and ev[j][0]==ev[k][0]]
  if not pairs:continue
  j,k=pairs[0]
  if ev[j][1]==ev[k][1]:continue
  bins=tuple(min(2,3*p//(len(ws)-1)) for p in (j,k));av=tuple(not ws[p+1].startswith(('sh','ch')) for p in (j,k))
  out[pg,ev[j][0],bins,av].append((ri,j,k,ev[j][1]))
 return dict(out)
def support(g):
 pv=collections.defaultdict(float)
 for (pg,b,bins,av),items in g.items():
  n=len(items);k=sum(x[3] for x in items);pv[pg]+=k*(n-k)/n*sum(av)
 W=sum(pv.values());pages=sum(v>0 for v in pv.values());share=max(pv.values(),default=0)/W if W else 0
 return dict(W=W,pages=pages,share=share,admitted=bool(W>=160 and pages>=8 and share<=.25))
def score(rows,g):
 dist=np.array([1.]);obs=0
 for key,items in g.items():
  if not any(key[3]):continue
  w=[int(rows[ri][1][j+1].startswith('qok'))-int(rows[ri][1][k+1].startswith('qok')) for ri,j,k,a in items];k=sum(x[3] for x in items)
  local=e['subset'](w,k);lo=min(local);hi=max(local);obs+=sum(a*d for (*_,a),d in zip(items,w))-lo
  total=sum(local.values());arr=np.array([local.get(x,0)/total for x in range(lo,hi+1)])
  dist=np.convolve(dist,arr);dist/=dist.sum()
 if len(dist)==1:return None
 return min(1.,8*float(dist[obs:].sum()))
def z(pos,L,nonlinear):
 r=pos/(L-1)
 return (2.5 if pos%2==0 else -2.5)+2*math.sin(4*math.pi*r) if nonlinear else 6*(r-.4)
def sigmoid(x):return 1/(1+math.exp(-x))
def roundtrip(rows):
 out=[]
 for pg,ws in rows:
  raw='.'.join('*' if w is None else w[0]+'!'+w[1:] for w in ws)+'- #synthetic';parsed=e['parse'](raw);assert parsed==ws;out.append((pg,parsed))
 return out
records=[]
scenarios=['null_low','null_high','null_layout','null_nonlinear','positive']
for volume in [1,4]:
 for trial in range(100):
  for si,scenario in enumerate(scenarios):
   seed=2410000+volume*10000+trial*10+si;rng=np.random.default_rng(seed);rows=[]
   for pg in range(12):
    for b in range(4):
     two=b%2==0;pattern=[1,1] if two else ([1,0] if rng.random()<.5 else [0,1]);stem='abcd'[b]+'edy'
     for av,n in [(pattern,volume*(7 if two else 14)),([0,0],20)]:
      for _ in range(n):
       front=int(rng.integers(4));back=int(rng.integers(6,13));L=front+6+back;j=front+1;k=front+3
       pr=sigmoid(5*(z(j,L,scenario=='null_nonlinear')-z(k,L,scenario=='null_nonlinear'))) if scenario in ('null_layout','null_nonlinear') else .5
       left=rng.random()<pr;ws=['dar']*front+['dar',('sh' if left else 'ch')+stem,'dar' if av[0] else 'chx',('ch' if left else 'sh')+stem,'dar' if av[1] else 'chx','dar']+['dar']*back
       for p in [j,k]:
        if rng.random()<.2:ws[p]='dar'
       ws=[None if rng.random()<.05 else w for w in ws];rows.append((pg,ws))
   rows=roundtrip(rows);g=groups(rows);s=support(g);new=[];pe=rng.choice([-.7,.7],12)
   for pg,ws in rows:
    le=float(rng.choice([-.7,.7]));out=[]
    for p,w in enumerate(ws):
     if w is None or w.startswith(('sh','ch')):out.append(w);continue
     prob=.6 if scenario=='null_high' else .2
     if scenario in ('null_layout','null_nonlinear'):prob=sigmoid(pe[pg]+le+z(p-1,len(ws),scenario=='null_nonlinear'))
     if scenario=='positive' and p>0 and ws[p-1] and ws[p-1].startswith('sh'):prob=.35
     out.append('qokam' if rng.random()<prob else 'dar')
    new.append((pg,out))
   new=roundtrip(new);assert groups(new)==g and support(groups(new))==s;p=score(new,g)
   records.append(dict(volume=volume,trial=trial,scenario=scenario,seed=seed,**s,p_adjusted=p,flag=p is not None and p<=.05))
  if (trial+1)%10==0:save('TRIALS.json',records);print(volume,trial+1,flush=True)
summary=[]
for volume,scenario in itertools.product([1,4],scenarios):
 rr=[r for r in records if r['volume']==volume and r['scenario']==scenario];aa=[r for r in rr if r['admitted']];n=len(aa);k=sum(r['flag'] for r in aa);ci=e['ci'](k,n) if n else [0,1];pr=e['ci'](k,100)
 rates=ci[0]>=.8 and pr[0]>=.8 if scenario=='positive' else ci[1]<=.1
 summary.append(dict(volume=volume,scenario=scenario,admitted=n,flags=k,diagnostic_flags=sum(r['flag'] for r in rr),wilson95=ci,practical_wilson95=pr,medianW=float(np.median([r['W'] for r in rr])),status='UNSUPPORTED' if n<80 else 'PASS' if rates else 'FAIL',rate_gate_pass=rates))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['status']=='PASS' for r in summary) else 'NOT_QUALIFIED',results=summary))
save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),raw_roundtrip=True,group_support_outcome_invariance=True,subset_exhaustive_oracle=True,records=len(records),manuscript_read=False))
