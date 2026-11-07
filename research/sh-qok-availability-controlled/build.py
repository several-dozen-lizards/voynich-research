from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent
score='''
def availability_score(rows):
 groups=matched['extract'](rows);dist={0:1};observed=0;V=0.;informative=0;strata_count=0
 for original_v,entries in groups:
  strata=collections.defaultdict(list)
  for ri,j,k,left in entries:
   ws=rows[ri][1];pattern=(not ws[j+1].startswith(('sh','ch')),not ws[k+1].startswith(('sh','ch')))
   strata[pattern].append((left,int(ws[j+1].startswith('qok'))-int(ws[k+1].startswith('qok'))))
  for pattern,items in strata.items():
   n=len(items);ns=sum(x for x,d in items);V+=ns*(n-ns)/n;strata_count+=1
   local=m.subset([d for x,d in items],ns);assert sum(local.values())==math.comb(n,ns)
   lo=min(local);observed+=sum(x*d for x,d in items)-lo
   if len(local)>1:informative+=1
   new=collections.Counter()
   for s,c in dist.items():
    for t,z in local.items():new[s+t-lo]+=c*z
   dist=dict(new)
 p=min(1.,8*sum(c for s,c in dist.items() if s>=observed)/sum(dist.values())) if len(dist)>1 else None
 return dict(V=V,p_adjusted=p,flag=p is not None and p<=.05,availability_strata=strata_count,informative=informative,not_estimable=p is None)
env['score']=availability_score
'''
for mode,seed in [('sh',1520000),('ch',1620000),('both',1720000)]:
 src=P/('sh-qok-feasibility-boundary/run.py' if mode=='sh' else f'sh-qok-ch-both-boundary/{mode}/run.py')
 code=src.read_text();start=code.index("if sys.argv[1]=='freeze':");end=code.index('for p,h in json.loads',start)
 freeze=f'''if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh {mode}-boundary availability-conditioned qualification. Synthetic only; no manuscript/HF data.',generator='Reuse prior {mode} boundary geometry and masks with fresh seed{seed}+attempt and outcome seed{seed+5000000}+attempt.200accepted required; retain original cap and all rejects. Initial V≈82.29 is old support only, not qualification of new conditional support.',revision='Within each preselected exactpage/length/body discordant group, split by ordered pair of follower-availability booleans. Preserve left-sh count separately in each pattern. Exact subset-sum null then preserves line composition, position margins and prefix-availability margins. Constant-score outcomes notestimable. No smoothing or pooling.',estimand='Association beyond structural follower availability. Positive probability.20 after ch and.35 after sh AMONG AVAILABLE matched followers; structuralzeros unchanged. This is a new15point conditional target, not the previous15point aggregate effect. Nulls .2,.6 or additivepage/line/position remain independent of prefix amongavailablefollowers.',gates='Eachcell200required. PositiveWilson95lowerpower>=.80; eachnullupperfalseflag<=.05. New conditionalV/constant-scorefrequency reported; oldV80rule does not transfer. Anyfailedgate failsqualification. Preserve allfailures and no retuning.',verification='Exact distribution preserves number of sh assignments per availabilitypattern byconstruction. In each pattern line-row counts remain1 and columnsh count fixed. Independent small-orbit oracle checks marginal constraints and score distribution before simulation. Fixed blockers not inferred from qok outcomes.',limits='Artificial balancedfourbody masks; conditional exchangeability not guaranteed for arbitrary nuisance. Historical sparsepower unqualified. H/F separate; manuscript staysclosed.'))
 save('FREEZE.json',{{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES}});print('Frozen');sys.exit()
'''
 code=code[:start]+freeze+code[end:]
 if mode=='sh':code=code.replace('P=R.parent;FILES=','P=R.parent.parent;FILES=')
 oldseed={'sh':1280000,'ch':1320000,'both':1420000}[mode]
 code=code.replace(f'{oldseed}+attempt',f'{seed}+attempt').replace(f'{oldseed+5000000}+attempt',f'{seed+5000000}+attempt')
 code=code.replace("(.25 if a else .1)/f[a]","(.35 if a else .2)")
 # Run exact oracle before any layouts. Count orientations with the same pattern-specific margins.
 oracle='''
for pattern in [(1,1),(1,0),(0,1),(0,0)]:
 for n in range(1,6):
  weights=[pattern[0]*(i%2)-pattern[1]*((i+1)%2) for i in range(n)]
  for k in range(n+1):
   brute=collections.Counter(sum(weights[i] for i in ix) for ix in itertools.combinations(range(n),k))
   assert m.subset(weights,k)==brute
'''
 code=code.replace('attempts=[];designs=[];records=[]',score+oracle+'\nattempts=[];designs=[];records=[]')
 d=R/mode;d.mkdir(exist_ok=True);(d/'run.py').write_text(code,encoding='utf-8')
print('Three candidates built before freezing/outcomes.')
