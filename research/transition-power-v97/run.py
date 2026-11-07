from pathlib import Path
import hashlib,itertools,json,math
from fractions import Fraction
from engine import convolve,tilt_integer,moments,rejection_regions,evaluate
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
protocol={
 'task':'Audit v96 power on its ACTUAL saved conditional span distributions; no rescore of observed manuscript D or p, and no manuscript rescore even if benchmarks pass.',
 'scope':'Four original Bathhand2/B/P and Starredhand3/B/P H/F panels, each of v96 anymiddle andmiddleN views separate. Reuse all spans, fixed transition fibers, pinned endpoints and word multiset. No pooling readings/hands, no dropped low-mobility spans.',
 'effects_frozen_before_power':'Weight ratios per +1D:11/10,5/4,3/2,2,3,4; forward favors larger D, reverse uses reciprocal. Null ratio1. All hypothetical alternative probabilities proportional to original conditional counts times r^D. No fit to observed D, no outcome-targeted shift or selected manuscript score.',
 'meaning':'This is an exponential tilt inside each allowed transition fiber; it changes relative preference among compatible orders, not adjacent class counts or words/endpoints. A r multiplier per +1netgapcount is not r times as many observed pairs. In two-path +/-1 fiber its positive-path probability is r^2/(1+r^2). Each panel/view has a separate hypothetical alternative, not a shared synthetic manuscript or independent H/F replication.',
 'coverage':'All, half, quarter of variable-score spans. Partial subsets are first ceil(fraction*variablecount) under SHA256 of fixed v97/panel/view/locator/startordinal; no observed score or effect direction used. Other spans retain null law, including all constant spans. Selected and remaining null histograms convolve to original null. Tilt selected pooled histogram then convolve with remaining; exact rational integer weighting.',
 'test_fixed':'Same v96 exact two-sided mean-distance rejection region, raw p times originalprefixpairsx28, alpha.05. Correct-direction detection uses D above/below NULL mean according to planted sign; wrong-direction and any-rejection probabilities retained. No relaxation of correction, lag, classes or endpoint constraints.',
 'benchmarks':'Full-coverage forward r=3/2 must have>=.80power; r=2 must have>=.90power, for EACH of8panelviews. Report each gate and overall; partial/reverse/loweffects are sensitivity diagnostics, not used to tune the grid or gates. Computational qualification separate. Failure limits exclusion claims at those effects, not DP correctness or prior adjacency result.',
 'qualification':'Before actual-layout power: tilt normalization versus exact binomial oracle for n1/4/16 and r1/11/10/5/4/3/2/2/3/4 in both signs; rejection tails versus independently enumerated asymmetric finite law; enumerated2^6two-path product probabilities and rejection powers; selected+remaining recomposition identities. Any arithmetic failure stops.',
 'calculation':'Exact integer/rational masses, no MonteCarlo trials or confidence intervals. Report mean shifts in D/nullSD and first FROZEN forward grid point attaining80%fullcoverage power. This is descriptive grid summary, not fitting a new effect size.',
 'preserve':'Every312layout/effect/coverage case inclnull, reverse, partial and failedbenchmarks; hashed selected-span ledger; null criticalregions, source mobility and exact probability numerators/denominators. Old v96 outputs unchanged.',
 'limits':'Layouts and null spectra already exposed; effect grid frozen before power calculations. One family of homogeneous-within-selected-spans alternatives, not power against all grammar or biological/semantic mechanisms. Conditional-independent span assumption inherited; copying/heterogeneous effects may differ. No new observation test.'}
inputs=[P/'transition-control-v96/RESULTS.json',P/'transition-control-v96/NULL-DISTRIBUTIONS.json',P/'transition-control-v96/FREEZE.json']
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)

ratios=[Fraction(11,10),Fraction(5,4),Fraction(3,2),Fraction(2),Fraction(3),Fraction(4)]
checks=0
for n in [1,4,16]:
 null={2*k-n:math.comb(n,k) for k in range(n+1)}
 for r in [Fraction(1),*ratios,*[1/r for r in ratios]]:
  tilted=tilt_integer(null,r);total=sum(tilted.values());q=r*r/(1+r*r)
  for k in range(n+1):assert Fraction(tilted[2*k-n],total)==math.comb(n,k)*q**k*(1-q)**(n-k);checks+=1
asym={-2:1,0:2,1:3,4:1};total,mu,var=moments(asym)
for budget in [1,28,272440]:
 reg=rejection_regions(asym,budget)
 for d in asym:
  direct=Fraction(sum(n for x,n in asym.items() if abs(Fraction(x)-mu)>=abs(Fraction(d)-mu)),total)
  assert reg['tails'][d]==direct
  assert (d in reg['forward'] or d in reg['reverse'])==(direct*budget<=Fraction(1,20));checks+=1
base={2*k-6:math.comb(6,k) for k in range(7)}
for r in [Fraction(1),Fraction(5,4),Fraction(3,2),Fraction(2)]:
 for direction in ['forward','reverse']:
  rr=r if direction=='forward' else 1/r;tilted=tilt_integer(base,rr);reg=rejection_regions(base,1);denom=(rr+1/rr)**6;oracle=Fraction(0)
  for seq in itertools.product([-1,1],repeat=6):
   score=sum(seq);prob=rr**score/denom
   if score in reg[direction]:oracle+=prob
  result=evaluate(tilted,reg,direction);assert float(oracle)==result['correct_direction_power'];checks+=1
assert convolve({-1:1,1:1},{-1:1,1:1})=={-2:1,0:2,2:1}
save('COMPUTATION-QUALIFICATION.json',dict(status='PASS',exact_oracle_checks=checks,binomial_tilt_normalization='pass',asymmetric_exact_rejection_tails='pass',enumerated_product_power='pass',limits='Numerical identities, not corpus power gates or independent empirical controls.'))

# From this point: saved NULL laws and span score-support metadata only.
# Existing observed_D fields are intentionally never accessed or tested.
old=load(inputs[0]);nulls=load(inputs[1]);results=[];layouts=[]
for panel in old['panels']:
 if panel['status']!='complete':raise RuntimeError('Source panel incomplete: cannot omit it from the audit.')
 for view in panel['views']:
  if view['status']!='complete':raise RuntimeError('Source view incomplete: cannot omit it from the audit.')
  idx=panel['original_panel_index'];mode=view['view'];rec=next(n for n in nulls if n['original_panel_index']==idx and n['view']==mode);null={int(k):int(v,16) for k,v in rec['weights_hex'].items()};budget=28*panel['opening_pairs'];reg=rejection_regions(null,budget)
  spans=[]
  for s in view['span_records']:
   hist={int(k):int(v,16) for k,v in s['score_support'].items()};key=f"v97|{idx}|{mode}|{s['locator']}|{s['start_ordinal']}";rank=hashlib.sha256(key.encode()).hexdigest();spans.append(dict(locator=s['locator'],start_ordinal=s['start_ordinal'],hist=hist,variable=len(hist)>1,rank=rank))
  variable=sorted([s for s in spans if s['variable']],key=lambda s:s['rank']);layout=dict(original_panel_index=idx,section=panel['section'],hand=panel['hand'],reading=panel['reading'],view=mode,spans=len(spans),variable_spans=len(variable),correction=budget,null_mean=float(reg['mean']),null_SD=math.sqrt(float(reg['variance'])),critical_forward_min=min(reg['forward']) if reg['forward'] else None,critical_reverse_max=max(reg['reverse']) if reg['reverse'] else None,forward_region=sorted(reg['forward']),reverse_region=sorted(reg['reverse']),coverage=[])
  for fraction in [Fraction(1),Fraction(1,2),Fraction(1,4)]:
   nselect=math.ceil(fraction*len(variable));selected_ranks={s['rank'] for s in variable[:nselect]};chosen={0:1};remaining={0:1}
   for s in spans:
    if s['rank'] in selected_ranks:chosen=convolve(chosen,s['hist'])
    else:remaining=convolve(remaining,s['hist'])
   assert convolve(chosen,remaining)==null
   layout['coverage'].append(dict(fraction=str(fraction),selected_variable_spans=nselect,selected=[dict(locator=s['locator'],start_ordinal=s['start_ordinal'],rank=s['rank']) for s in variable[:nselect]]))
   effects=[('null',Fraction(1))]+[(direction,r) for direction in ['forward','reverse'] for r in ratios]
   for direction,r in effects:
    applied=r if direction!='reverse' else 1/r;alt=convolve(tilt_integer(chosen,applied),remaining);power=evaluate(alt,reg,direction)
    results.append(dict(original_panel_index=idx,section=panel['section'],hand=panel['hand'],reading=panel['reading'],view=mode,coverage=str(fraction),selected_variable_spans=nselect,direction=direction,weight_ratio=str(r),applied_ratio=str(applied),**power))
   print(idx,mode,'coverage',fraction,'done',flush=True)
  primary=[r for r in results if r['original_panel_index']==idx and r['view']==mode and r['coverage']=='1' and r['direction']=='forward'];p15=next(r['correct_direction_power'] for r in primary if r['weight_ratio']=='3/2');p2=next(r['correct_direction_power'] for r in primary if r['weight_ratio']=='2')
  layout['benchmark_moderate_power']=p15;layout['benchmark_strong_power']=p2;layout['moderate_gate']=p15>=.8;layout['strong_gate']=p2>=.9;layout['power_benchmarks_pass']=layout['moderate_gate'] and layout['strong_gate'];layout['first_frozen_forward_ratio_with_80pct_power']=next((r['weight_ratio'] for r in primary if r['correct_direction_power']>=.8),None);layouts.append(layout)
save('RESULTS.json',dict(protocol=protocol,computation_qualification='PASS',manuscript_rescore='NOT PERFORMED',status='POWER BENCHMARKS MET' if all(x['power_benchmarks_pass'] for x in layouts) else 'POWER BENCHMARKS NOT MET',layouts=layouts,power_cases=results));save('SUMMARY.json',[{k:v for k,v in x.items() if k!='coverage'} for x in layouts]);print('Audit complete:',len(results),'cases; no manuscript rescore.',flush=True)
