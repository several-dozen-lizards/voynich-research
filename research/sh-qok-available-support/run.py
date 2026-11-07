from pathlib import Path
import json,hashlib,sys,collections,itertools,math
import numpy as np
R=Path(__file__).resolve().parent
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic conditional-stratum support qualification only; no manuscript,H/Fdata or pooling.',rule='W=sum over availability-pattern strata k(n-k)/n*(a_left+a_right). Bothblocked contributes0,oneavailable contributesV,bothavailable2V. RequireW>=160,>=8pageswithW,maxpageshare<=.25. Proposed threshold, not proven minimal. Uses only prefixmargins and structuralavailability, never qok.',design='200fresh datasets each architecture:twoavailable,oneavailable,mixed.12pages4bodies. Twoavailable strata n7,k3,pattern11 =>W164.5714;oneavailable n14,k7,pattern10or01 =>W168;mixed alternatesbodytype=>W166.2857. Add one pattern00stratum n20,k10 perpage/body to challenge blocked-support inflation. Randomize orientations within each stratum, and singleavailable side. Same exact conditional count null as prior availability test. Group-level synthetic fixtures, not tokenpipeline qualification.',outcomes='Independent available follower Bernoulli .2 or.6 nulls; nuisance null logisticpage+line+position±.7, independent oforientation; positives .2afterch/.35aftersh amongavailable. Pattern00outcomes zero. Fresh seeds1850000+architecture*10000+trial. Four independentlydrawn scenarios perdesign; no outcomeselection.',gates='Eachcell200. PositiveWilson95 lowerpower>=.80; eachnullupperfalseflag<=.05; anyfailureblocks general qualification. Verify exactdistribution with exhaustiveoracle, Wunchanged by blockedstrata and outcomechanges, structuraloutcomes zero. Keep allfailures. Belowthreshold n2/k1 companion support fixture must be rejected; no power claim for that fixture.',limits='Balanced constructed strata atW164..168,not near160exactly,not sparse historicalsupport; conditionalmodel finite. Wdepends hypothetical variation,not observed qok. Arbitrary interactions and source parsing unqualified. No manuscriptapplication evenifpass.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def subset(w,k):
 dp=[collections.Counter() for _ in range(k+1)];dp[0][0]=1
 for v in w:
  for j in range(k,0,-1):
   for s,c in list(dp[j-1].items()):dp[j][s+int(v)]+=c
 return dp[k]
for n in range(1,7):
 w=[i%3-1 for i in range(n)]
 for k in range(n+1):assert subset(w,k)==collections.Counter(sum(w[i] for i in ii) for ii in itertools.combinations(range(n),k))
def support(groups):
 pages=collections.defaultdict(float)
 for g in groups:
  n=len(g['left']);k=sum(g['left']);pages[g['page']]+=k*(n-k)/n*sum(g['pattern'])
 W=sum(pages.values());return dict(W=W,pages=sum(x>0 for x in pages.values()),max_share=max(pages.values())/W if W else None,pass_rule=W>=160 and sum(x>0 for x in pages.values())>=8 and max(pages.values())/W<=.25 if W else False)
def test(groups,scenario,rng):
 dist={0:1};obs=0;pe=rng.choice([-.7,.7],size=12)
 for g in groups:
  a=np.array(g['left']);n=len(a);pattern=g['pattern'];q=np.zeros((n,2),dtype=int);le=rng.choice([-.7,.7],size=n)
  for side in range(2):
   if not pattern[side]:continue
   variant=a if side==0 else 1-a
   p=.2+.15*variant if scenario=='positive' else .6 if scenario=='null_high' else 1/(1+np.exp(-(pe[g['page']]+le+(.7 if side else -.7)))) if scenario=='null_nuisance' else .2
   q[:,side]=rng.random(n)<p
  assert all(pattern[j] or not q[:,j].any() for j in range(2))
  w=q[:,0]-q[:,1];local=subset(w,int(a.sum()));assert sum(local.values())==math.comb(n,int(a.sum()));lo=min(local);obs+=int((a*w).sum())-lo
  # Score-constant factors cancel exactly; omit their multiplicity.
  if len(local)==1:continue
  new=collections.Counter()
  for s,c in dist.items():
   for t,z in local.items():new[s+t-lo]+=c*z
  dist=dict(new)
 p=min(1.,8*sum(c for s,c in dist.items() if s>=obs)/sum(dist.values())) if len(dist)>1 else None
 return dict(p_adjusted=p,flag=p is not None and p<=.05,not_estimable=p is None)
designs=[];records=[]
for ai,architecture in enumerate(['two_available','one_available','mixed']):
 for trial in range(200):
  seed=1850000+ai*10000+trial;rng=np.random.default_rng(seed);groups=[]
  for pg in range(12):
   for body in range(4):
    two=architecture=='two_available' or architecture=='mixed' and body%2==0;n,k=(7,3) if two else (14,7);a=[1]*k+[0]*(n-k);rng.shuffle(a)
    pattern=[1,1] if two else [1,0] if rng.random()<.5 else [0,1]
    groups.append(dict(page=pg,body=body,pattern=pattern,left=a))
    blocked=[1]*10+[0]*10;rng.shuffle(blocked);groups.append(dict(page=pg,body=body,pattern=[0,0],left=blocked))
  supp=support(groups);assert supp==support([g for g in groups if any(g['pattern'])]);assert supp['pass_rule']
  low=[dict(g,left=[0,1]) for g in groups];assert not support(low)['pass_rule']
  designs.append(dict(architecture=architecture,seed=seed,**supp,groups=groups))
  for scenario in ['null_low','null_high','null_nuisance','positive']:records.append(dict(architecture=architecture,trial=trial,seed=seed,scenario=scenario,**supp,**test(groups,scenario,rng)))
  if (trial+1)%50==0:print(architecture,trial+1,flush=True)
 save('TRIALS.json',records);save('DESIGNS.json',designs)
def ci(k,n):
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d;return [max(0,c-h),min(1,c+h)]
summary=[]
for architecture,scenario in itertools.product(['two_available','one_available','mixed'],['null_low','null_high','null_nuisance','positive']):
 rr=[r for r in records if r['architecture']==architecture and r['scenario']==scenario];k=sum(r['flag'] for r in rr);bounds=ci(k,200)
 summary.append(dict(architecture=architecture,scenario=scenario,n=200,flags=k,wilson95=bounds,pass_gate=bounds[0]>=.8 if scenario=='positive' else bounds[1]<=.05,W=rr[0]['W']))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),exact_oracle=True,blocked_support_invariance=True,low_support_rejected=True,records=len(records),manuscript_read=False))
