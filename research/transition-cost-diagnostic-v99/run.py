from pathlib import Path
import collections,hashlib,importlib.util,itertools,json,math
from fractions import Fraction
import numpy as np
from engine import loose_distribution
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
spec=importlib.util.spec_from_file_location('power',P/'transition-power-v97/engine.py');power=importlib.util.module_from_spec(spec);spec.loader.exec_module(power)
protocol={
 'task':'Frozen DIAGNOSTIC ONLY. Attribute sensitivity changes, do not relax v98 gates, resume robustness banks, or score/rescore any original manuscript D/p.',
 'scope':'Same8Bathhand2/B/P andStarredhand3/B/P H/F/view layouts. No pooling or dropped failed views. Keep all original opening-family columns in saved v98 banks.',
 'correction_factorial':'On the SAME v98 pilot/calibration banks and SAME strict transition-fiber alternatives, compare target-only p, target-only x28, panel-wide full-family maxT p, and original full-family maxT x28. All use identical pilot centering/scaling, two-sided absolute Z, plus-one calibration p, alpha.05. Four threshold rules are counterfactual diagnostics, NEVER replacement acceptance screens.',
 'clean_correction_cost':'Hold alternative probability law fixed. Report target->search->full staged losses and target->panelbudget->full losses, not an additive causal allocation: factors interact. Full-rule power must reproduce v98 exactly.',
 'constraint_controls':'New exact span-multiset-only null pins the SAME readable-span endpoints, full literal word multisets and unknown seams but removes9adjacentS/Q/Nedgecount constraints. Uniform class orders with original interior class counts; constant literal assignment weights. Exact DP counts, 250000memo-state/span cap; any failure blocks diagnostic panel rather than dropping spans.',
 'constraint_measures':'Compare number of variable spans, total class-order-space log2 ratio, and null variance/SD retention. Structural space shrinkage is not itself a causal percentage of power loss. Transition constraints can remove signal and noise.',
 'constraint_power':'Same v97 full-coverage r grid/null/reciprocals under BOTH own-base exponential-tilt laws, using the SAME exact-targeted .05 diagnostic tail algorithm. Different base laws mean these are not the same data-generating alternative; do not causally subtract them. Also apply the relaxed targeted rejection region to strict alternatives, including strict r1 baseline, to expose background-transition rejection.',
 'effects':'Unchanged ratios11/10,5/4,3/2,2,3,4/null1 andreverse reciprocity, and all/half/quarter same v97span subsets for correction comparisons. Constraint comparisons fullcoverageonly. No weights fitted to observed score. No new power qualification gates: original .80at1.5/.90at2 gates remain failed/unchanged.',
 'qualification':'Before actual diagnostics, authored S/Q/N strings lengths1..7 grouped by pinned endpoints/interiorcounts; loose DP histograms match direct enumeration for bothgapviews and multinomial total count. Exact literal assignment counting same class-frequency logic asv96. Verify rejection-region nesting across four correction conditions; full result must match savedv98. Any numerical identity failure stops.',
 'preserve':'Every threshold power/null size, every failed original view, negative/partial/loweffect case, every structural-span statistic, baseline rejection under model mismatch, and unrun robustness banks. Source original score is never tested.',
 'limits':'Correction comparisons are clean conditional-on-bank counterfactuals; constraints comparison changes model and alternative law and cannot yield a unique causal percent. One v98bank perpanel, no future-bank averaging. No semantic, grammatical or junction mechanism identification.'}
files=[P/'transition-maxT-qual-v98/QUALIFICATION.json',P/'transition-maxT-qual-v98/FREEZE.json',P/'transition-control-v96/RESULTS.json',P/'transition-control-v96/NULL-DISTRIBUTIONS.json',P/'transition-power-v97/RESULTS.json',P/'transition-power-v97/engine.py']
bankfiles=sorted((P/'transition-maxT-qual-v98').glob('bank-1-panel-*-*.npz'));assert len(bankfiles)==8
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files+bankfiles};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)

def seqscore(seq,neutral):return sum(1 if a==0 and c==1 else -1 if a==1 and c==0 else 0 for a,b,c in zip(seq,seq[1:],seq[2:]) if not neutral or b==2)
fibers=collections.defaultdict(list)
for n in range(1,8):
 for seq in itertools.product(range(3),repeat=n):fibers[(seq[0],seq[-1],tuple(seq[1:-1].count(i) for i in range(3)),n==1)].append(seq)
checks=0
for (start,end,inside,single),seqs in fibers.items():
 for neutral in [False,True]:
  dist,calls=loose_distribution(start,end,inside,neutral,single);assert dist==dict(collections.Counter(seqscore(s,neutral) for s in seqs))
  expected=1 if single else math.factorial(sum(inside))//math.prod(math.factorial(n) for n in inside);assert sum(dist.values())==expected;checks+=1
save('COMPUTATION-QUALIFICATION.json',dict(status='PASS',authored_sequences=sum(map(len,fibers.values())),fibers=len(fibers),view_checks=checks,loose_DP_exact_enumeration='pass',multinomial_path_totals='pass',limits='Implementation controls only; no relaxed acceptance or new manuscript test.'))

v98=load(files[0]);assert v98['status']=='FAIL' and v98['manuscript_rescore']=='NOT PERFORMED';strictsrc=load(files[2]);strictnulls=load(files[3]);v97=load(files[4]);layouts=[];cases=[];modelcases=[];nulldata=[]
ratios=[Fraction(11,10),Fraction(5,4),Fraction(3,2),Fraction(2),Fraction(3),Fraction(4)];effects=[('null',Fraction(1))]+[(d,r) for d in ['forward','reverse'] for r in ratios]
for rec in v98['records']:
 idx=rec['original_panel_index'];view=rec['view'];bank=np.load(P/'transition-maxT-qual-v98'/f'bank-1-panel-{idx:02d}-{view}.npz');mu,sd,mx,cal=bank['mean'],bank['sd'],bank['maxima'],bank['calibration_scores'];oldmeta=load(P/'opening-order-audit-v75/RESULTS.json');target=next(p for p in oldmeta['panels'] if p['panel_index']==idx)['reported_rules'][0];col,sign=target['column'],target['sign'];tm=mu[col]*sign;ts=sd[col];N=len(mx);single_z=np.abs((cal[:,col]-mu[col])/sd[col]);sr=next(p for p in strictsrc['panels'] if p['original_panel_index']==idx);spanrecords=next(v for v in sr['views'] if v['view']==view)['span_records'];rawnull=next(n for n in strictnulls if n['original_panel_index']==idx and n['view']==view);strict={int(k):int(n,16) for k,n in rawnull['weights_hex'].items()};T,mean,var=power.moments(strict)
 regimes={name:dict(mean=mean,variance=var,forward=set(),reverse=set()) for name in ['target_only','target_x28','search_only','search_x28']}
 for d in strict:
  z=abs((d-tm)/ts);ps=(1+int(np.sum(single_z>=z-1e-12)))/(N+1);pm=(1+int(np.sum(mx>=z-1e-12)))/(N+1)
  for name,pv in [('target_only',ps),('target_x28',min(1,ps*28)),('search_only',pm),('search_x28',min(1,pm*28))]:
   if pv<=.05:
    if Fraction(d)>mean:regimes[name]['forward'].add(d)
    elif Fraction(d)<mean:regimes[name]['reverse'].add(d)
 for side in ['forward','reverse']:
  assert regimes['search_x28'][side]<=regimes['search_only'][side]<=regimes['target_only'][side]
  assert regimes['search_x28'][side]<=regimes['target_x28'][side]<=regimes['target_only'][side]
 assert sorted(regimes['search_x28']['forward'])==rec['forward_region'] and sorted(regimes['search_x28']['reverse'])==rec['reverse_region']
 lay=dict(original_panel_index=idx,section=rec['section'],hand=rec['hand'],reading=rec['reading'],view=view,thresholds={k:dict(forward_min=min(r['forward']) if r['forward'] else None,reverse_max=max(r['reverse']) if r['reverse'] else None,exact_strict_null_size=float(Fraction(sum(n for d,n in strict.items() if d in r['forward'] or d in r['reverse']),T))) for k,r in regimes.items()})
 source_layout=next(l for l in v97['layouts'] if l['original_panel_index']==idx and l['view']==view)
 for coverage in source_layout['coverage']:
  selected={(s['locator'],s['start_ordinal']) for s in coverage['selected']};a={0:1};b={0:1}
  for s in spanrecords:
   hist={int(k):int(n,16) for k,n in s['score_support'].items()}
   if (s['locator'],s['start_ordinal']) in selected:a=power.convolve(a,hist)
   else:b=power.convolve(b,hist)
  assert power.convolve(a,b)==strict
  for direction,ratio in effects:
   applied=ratio if direction!='reverse' else 1/ratio;alt=power.convolve(power.tilt_integer(a,applied),b)
   for name,reg in regimes.items():
    ev=power.evaluate(alt,reg,direction);cases.append(dict(original_panel_index=idx,section=rec['section'],hand=rec['hand'],reading=rec['reading'],view=view,coverage=coverage['fraction'],direction=direction,weight_ratio=str(ratio),threshold=name,**ev))
    if name=='search_x28':
     original=next(c for c in v98['all_power_cases'] if c['original_panel_index']==idx and c['view']==view and c['coverage']==coverage['fraction'] and c['direction']==direction and c['weight_ratio']==str(ratio));assert all(original[k]==v for k,v in ev.items())
 # Remove transition constraints ONLY, keep endpoints/word multisets/seams.
 loose={0:1};entropy_loss=0.;variable_strict=variable_loose=0;spanledger=[]
 for s in spanrecords:
  seq=s['classes'];interior=tuple(seq[1:-1].count(i) for i in range(3));hist,calls=loose_distribution(seq[0],seq[-1],interior,view=='non_target_middle',len(seq)==1);oldhist={int(k):int(n,16) for k,n in s['score_support'].items()};assert all(n<=hist.get(k,0) for k,n in oldhist.items())
  nold,nnew=sum(oldhist.values()),sum(hist.values());bits=math.log2(nnew)-math.log2(nold);assert bits>=-1e-10;entropy_loss+=bits;variable_strict+=len(oldhist)>1;variable_loose+=len(hist)>1;loose=power.convolve(loose,hist);spanledger.append(dict(locator=s['locator'],start_ordinal=s['start_ordinal'],class_counts=[seq.count(i) for i in range(3)],strict_class_orders_hex=hex(nold),loose_class_orders_hex=hex(nnew),removed_log2_class_orders=bits,strict_support=len(oldhist),loose_support=len(hist),memo_states=calls))
 LT,LM,LV=power.moments(loose);strictreg=power.rejection_regions(strict,1);loosereg=power.rejection_regions(loose,1)
 lay['constraints']=dict(spans=len(spanrecords),strict_variable_spans=variable_strict,loose_variable_spans=variable_loose,strict_mean=float(mean),loose_mean=float(LM),strict_SD=math.sqrt(float(var)),loose_SD=math.sqrt(float(LV)),retained_variance_fraction=float(var/LV) if LV else None,removed_log2_class_orders=entropy_loss,span_ledger=spanledger)
 for direction,ratio in effects:
  applied=ratio if direction!='reverse' else 1/ratio;strictalt=power.tilt_integer(strict,applied);loosealt=power.tilt_integer(loose,applied)
  for name,alt,reg in [('strict_own_base',strictalt,strictreg),('loose_own_base',loosealt,loosereg),('strict_alternative_loose_test',strictalt,loosereg)]:modelcases.append(dict(original_panel_index=idx,section=rec['section'],hand=rec['hand'],reading=rec['reading'],view=view,direction=direction,weight_ratio=str(ratio),comparison=name,**power.evaluate(alt,reg,direction)))
 nulldata.append(dict(original_panel_index=idx,view=view,loose_null_hex={str(k):hex(n) for k,n in sorted(loose.items())}))
 layouts.append(lay);print('DONE',idx,view,'variance retained',lay['constraints']['retained_variance_fraction'],flush=True)
save('RESULTS.json',dict(protocol=protocol,status='DIAGNOSTIC ONLY; v98 FAIL unchanged',manuscript_rescore='NOT PERFORMED',layouts=layouts,correction_cases=cases,constraint_model_cases=modelcases));save('LOOSE-NULLS.json',nulldata)
summary=[]
for l in layouts:
 r=dict(original_panel_index=l['original_panel_index'],section=l['section'],hand=l['hand'],reading=l['reading'],view=l['view'],constraints={k:v for k,v in l['constraints'].items() if k!='span_ledger'},power={})
 for weight in ['3/2','2']:r['power'][weight]={name:next(c['correct_direction_power'] for c in cases if c['original_panel_index']==l['original_panel_index'] and c['view']==l['view'] and c['coverage']=='1' and c['direction']=='forward' and c['weight_ratio']==weight and c['threshold']==name) for name in regimes}
 summary.append(r)
save('SUMMARY.json',summary);print('Diagnostic complete; no gates changed or source scores tested.',flush=True)
