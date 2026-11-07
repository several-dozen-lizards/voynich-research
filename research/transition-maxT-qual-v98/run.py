from pathlib import Path
import collections,hashlib,importlib.util,itertools,json,math
from fractions import Fraction
import numpy as np
from scipy.stats import rankdata,binomtest
from engine import build,draw,invariants,score_batch,state,edgecounts,paths
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
spec=importlib.util.spec_from_file_location('power_engine',P/'transition-power-v97/engine.py');power=importlib.util.module_from_spec(spec);spec.loader.exec_module(power)
protocol={
 'task':'QUALIFICATION ONLY: transition-preserving full-family maxT on actual bath/starred conditional layouts. Never score original source arrangement or rescore manuscript p, even if qualificationPASS.',
 'scope':'All4same v96/v97 Bathhand2/B/P and Starredhand3/B/P panels, H/F separate, same shared loci/endpoints/unknown spans/whole-word multisets/9S-Q-Nadjacentclasscounts. Full unchanged original opening-pair family and both signs, both gapmiddle views; correctionx28 retained.',
 'sampler':'Enumerate distinct compatible opening-class sequences per span; choose uniformly, then independently Fisher-Yates-shuffle literal interior words within each class, keeping span literalendpoints. Constant literal assignment multiplicity makes this uniform conditional word order. No labelled-edge bias/MCMC. Frozen20000path/span enumeration cap; any overflow blocks the whole panel, no source dropping. Sampling batches256.',
 'candidate_maxT':'Independent-pilot regularized maxT, an explicitly new candidate method. Pilot2048conditional null layouts estimate each column mean and sqrt(variance+1count^2). Separate4096calibration layouts produce max absolute standardized contrast across ALL original columns. Prospective target p=(1+#calibrationmax>=abs(targetZ))/4097 then x28. Pilot independent of calibration/observation; unlike v77 pooled symmetric studentization. Ties conservative; no Gaussian tails.',
 'effects_and_power':'Unchanged full v97 ratios11/10,5/4,3/2,2,3,4, null1 and reciprocal reverse effects. Same all/half/quarter hashed variable-span subsets from v97; do not reselect. Exact alternative target-D laws inside actual conditional fibers, not arbitrary score spikes. Compute exact correct-direction power conditional on the pilot/calibration banks; whole-family cutoff uses joint null, every column retained. No observed_D or source p used.',
 'gates':'Computational exact-orbit sampler/count identities and rank arithmetic must pass. Each actual panel/view must pass target null size<=.05/28, attainable target correctedp<=.01, empirical target-null CDF binomial audit (family alpha.001 across planned3banks x8views x maxsource support points), and unchanged fullcoverageforwardpower>=.80 at r1.5 and>=.90 at r2. No gate relaxed after results. Other effects/coverages/reverse cases reported, not tuned.',
 'staging':'StageA one pilot/calibration bank perpanel, finish all4panels/bothviews despite any failures. StageB two further independent banks perpanel ONLY if every StageA gate passes. OverallPASS requires all completed/planned3banks to pass; failure stops with remaining robustness banks explicitly NOT RUN. Seeds98000+1000*bankindex+originalpanelindex. No manuscript rescore in any case.',
 'computational_checks':'Before actual-layout banks, exhaustive authored S/Q/N fibers lengths1..7 vs sampler path library; literal assignment multiplicity; enumerate Fisher-Yates choices up to4items including repeats; toy batch invariants and full-family gap counts vs direct word comparison. Validate exact null count probabilities from saved v96 against sampled target CDF without using source observed arrangement.',
 'precision_and_dependence':'Power values exact given calibration banks, but cutoffs have simulation variability. StageB checks further banks only after StageA success; a StageA failure is not averaged away. Exact null size here is focal-target conditional on banks, not independent empirical FWER proof. Calibration row ranks and Bonf28 provide global-null arithmetic bound; pilot independence is essential. H/F and two views are not independent replicas.',
 'preserve':'Every stage failure, both middle views, all312effect/coverage cases PER BANK, all score columns, pilot moments, calibrationmaxima, source invariants, CDF audit, hashed subset ledgers and prior v96/v97failures. Full observed manuscript score never computed.',
 'limits':'Conditional model preserves opening-class transitions, not every literalword bigram/character junction. Numeric/sampling qualification not semantic or historical validation. Effects are view-specific exponential tilts, not one shared synthetic manuscript. Exact source class spectra and vocab already exposed, no fresh confirmation.'}
files=[P/'transition-control-v96/RESULTS.json',P/'transition-control-v96/NULL-DISTRIBUTIONS.json',P/'transition-power-v97/RESULTS.json',P/'opening-order-audit-v75/RESULTS.json',P/'opening-order-audit-v75/engine.py',P/'one-gap-order-v78/engine.py',P/'transition-power-v97/engine.py']
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)

# Exhaustive path-library oracle, before actual source data are read.
fibers=collections.defaultdict(set)
for n in range(1,8):
 for s in itertools.product(range(3),repeat=n):fibers[(s[0],s[-1],edgecounts(s))].add(s)
for (start,end,ec),ss in fibers.items():assert {tuple(map(int,v)) for v in paths(start,end,ec)}==ss
fychecks=0
for initial in [(0,1),(0,1,2),(0,1,2,3),(0,0,1)]:
 tally=collections.Counter()
 for swaps in itertools.product(*(range(j+1) for j in range(len(initial)-1,0,-1))):
  x=list(initial)
  for j,k in zip(range(len(initial)-1,0,-1),swaps):x[j],x[k]=x[k],x[j]
  tally[tuple(x)]+=1
 assert len(set(tally.values()))==1;fychecks+=1
toy=[dict(page='toy',folio='f1',locator='toy1',tokens=['shaa','na','nb','qokbb','nc','shaa']),dict(page='toy',folio='f2',locator='toy2',tokens=['EDGE','shaa',None,'qokbb','x','END'])]
tp,ts=build(toy);ta=draw(tp,ts,128,np.random.default_rng(98999));invariants(ta,tp,ts);ss=score_batch(ta,tp)
for view,mat in ss.items():
 for i,arr in enumerate(ta):
  for col,(ai,bi) in enumerate(zip(tp['ia'],tp['ib'])):
   A,B=tp['labels'][ai],tp['labels'][bi];f=b=0
   for li,mi,ri in zip(tp['li'],tp['mi'],tp['ri']):
    x,m,z=(tp['words'][arr[j]] for j in (li,mi,ri))
    if view=='non_target_middle' and m.startswith(('sh','qok')):continue
    from engine import gap
    f+=gap.base.belongs(x,A) and gap.base.belongs(z,B);b+=gap.base.belongs(x,B) and gap.base.belongs(z,A)
   assert mat[i,col]==f-b
save('COMPUTATION-QUALIFICATION.json',dict(status='PASS',exact_fibers=len(fibers),exact_sequences=sum(map(len,fibers.values())),Fisher_Yates_oracles=fychecks,toy_null_draws=128,span_word_transition_endpoint_unknown_invariants='pass',independent_full_family_gap_counts='pass',no_manuscript_arrangement_scored=True))

old=load(files[0]);nulls=load(files[1]);previous=load(files[2]);family=load(files[3]);bypanel={p['panel_index']:p for p in family['panels']};nullmap={(n['original_panel_index'],n['view']):{int(k):int(v,16) for k,v in n['weights_hex'].items()} for n in nulls};maxsupport=max(map(len,nullmap.values()));records=[];allcases=[]
# Source row layout is reconstructed without calling a score on original tokens.
raw=load(P/'frequency-atlas-v48/rows.json');source_rows={}
for panel in old['panels']:
 idx=panel['original_panel_index'];tr=panel['reading'];rr=[r for r in raw if tuple(r[2:6])==(panel['section'],panel['hand'],panel['variety'],panel['format'])];other={r[6] for r in rr if r[0]!=tr};source_rows[idx]=[dict(page=r[1],folio=r[1].split('.')[0],locator=r[6],tokens=r[7]) for r in rr if r[0]==tr and r[6] in other]

for bank in range(3):
 stage_records=[]
 for panel in old['panels']:
  idx=panel['original_panel_index'];p,specs=build(source_rows[idx]);assert p['labels']==bypanel[idx]['labels'];rng=np.random.default_rng(98000+1000*bank+idx);Npilot,Ncal=2048,4096;full={v:np.empty((Npilot+Ncal,len(p['ia'])),dtype=np.int16) for v in ['any_middle','non_target_middle']}
  print('START bank',bank+1,'panel',idx,'family',len(p['ia']),flush=True)
  for lo in range(0,Npilot+Ncal,256):
   hi=min(lo+256,Npilot+Ncal);a=draw(p,specs,hi-lo,rng)
   if lo==0:invariants(a,p,specs)
   scores=score_batch(a,p)
   for v in full:full[v][lo:hi]=scores[v]
   if hi%1024==0:print('sampled',idx,hi,flush=True)
  target=bypanel[idx]['reported_rules'][0];col=target['column'];sign=target['sign']
  for view,mat in full.items():
   pilot=mat[:Npilot].astype(float);mu=pilot.mean(axis=0);sd=np.sqrt(pilot.var(axis=0)+1);cal=mat[Npilot:];maxima=np.zeros(Ncal)
   for lo in range(0,cal.shape[1],128):maxima=np.maximum(maxima,np.abs((cal[:,lo:lo+128]-mu[lo:lo+128])/sd[lo:lo+128]).max(axis=1))
   null=nullmap[(idx,view)];T=sum(null.values());moment=sum(d*n for d,n in null.items());mean=Fraction(moment,T);mu_target=mu[col]*sign;sd_target=sd[col];forward=set();reverse=set();pmap={}
   for d in null:
    z=abs((d-mu_target)/sd_target);pv=min(1,28*(1+int(np.sum(maxima>=z-1e-12)))/(Ncal+1));pmap[d]=pv
    if pv<=.05:
     if Fraction(d)>mean:forward.add(d)
     elif Fraction(d)<mean:reverse.add(d)
   regions=dict(mean=mean,variance=Fraction(sum(d*d*n for d,n in null.items()),T)-mean*mean,forward=forward,reverse=reverse)
   nullsize=Fraction(sum(n for d,n in null.items() if d in forward or d in reverse),T);emp=np.concatenate([mat[:Npilot,col],cal[:,col]])*sign;cdf_checks=[];cum=0;alpha=.001/(3*8*maxsupport)
   for d,n in sorted(null.items()):
    cum+=n;q0=float(Fraction(cum,T));k=int(np.sum(emp<=d));pv=1. if q0 in (0.,1.) and k==int(q0*len(emp)) else float(binomtest(k,len(emp),q0).pvalue);cdf_checks.append(dict(d=d,cumulative_null_probability=q0,empirical_count=k,p_value=pv))
   cdfpass=all(x['p_value']>=alpha for x in cdf_checks);precision=min(pmap.values())<=.01
   base_layout=next(x for x in previous['layouts'] if x['original_panel_index']==idx and x['view']==view);spanmeta=next(v for v in panel['views'] if v['view']==view)['span_records'];cases=[]
   for coverage in base_layout['coverage']:
    selected={(x['locator'],x['start_ordinal']) for x in coverage['selected']};chosen={0:1};remaining={0:1}
    for s in spanmeta:
     hist={int(k):int(v,16) for k,v in s['score_support'].items()}
     if (s['locator'],s['start_ordinal']) in selected:chosen=power.convolve(chosen,hist)
     else:remaining=power.convolve(remaining,hist)
    assert power.convolve(chosen,remaining)==null
    for direction,ratio in [('null',Fraction(1))]+[(d,Fraction(r)) for d in ['forward','reverse'] for r in ['11/10','5/4','3/2','2','3','4']]:
     applied=ratio if direction!='reverse' else 1/ratio;alt=power.convolve(power.tilt_integer(chosen,applied),remaining);ev=power.evaluate(alt,regions,direction);cases.append(dict(bank=bank+1,original_panel_index=idx,section=panel['section'],hand=panel['hand'],reading=panel['reading'],view=view,coverage=coverage['fraction'],direction=direction,weight_ratio=str(ratio),**ev))
   primary=[c for c in cases if c['coverage']=='1' and c['direction']=='forward'];moderate=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='3/2');strong=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='2');rankps=28*rankdata(-maxima,method='max')/Ncal;rankgate=np.count_nonzero(rankps<=.05)<=math.floor(.05*Ncal/28)
   rec=dict(bank=bank+1,original_panel_index=idx,section=panel['section'],hand=panel['hand'],reading=panel['reading'],view=view,search_pairs=len(p['ia']),pilot_rows=Npilot,calibration_rows=Ncal,pilot_target_mean=float(mu_target),pilot_target_scale=float(sd_target),critical_forward_min=min(forward) if forward else None,critical_reverse_max=max(reverse) if reverse else None,exact_focal_null_size=float(nullsize),empirical_CDF_alpha=alpha,CDF_min_p=min(x['p_value'] for x in cdf_checks),moderate_power=moderate,strong_power=strong,forward_region=sorted(forward),reverse_region=sorted(reverse),gates=dict(null_size=nullsize<=Fraction(1,560),precision=precision,sampler_CDF=cdfpass,rank_bound=bool(rankgate),moderate_power=moderate>=.8,strong_power=strong>=.9));rec['passes']=all(rec['gates'].values());records.append(rec);stage_records.append(rec);allcases.extend(cases)
   np.savez_compressed(R/f'bank-{bank+1}-panel-{idx:02d}-{view}.npz',pilot_scores=mat[:Npilot],calibration_scores=cal,mean=mu,sd=sd,maxima=maxima);save(f'bank-{bank+1}-panel-{idx:02d}-{view}-CDF.json',cdf_checks);print('DONE',bank+1,idx,view,'powers',moderate,strong,'gates',rec['gates'],flush=True)
  save('PROGRESS.json',dict(records=records))
 if not all(r['passes'] for r in stage_records):break
status='PASS' if len(records)==24 and all(r['passes'] for r in records) else 'FAIL';save('QUALIFICATION.json',dict(status=status,banks_completed=max(r['bank'] for r in records),robustness_banks_not_run=list(range(max(r['bank'] for r in records)+1,4)),records=records,all_power_cases=allcases,manuscript_rescore='NOT PERFORMED',limits='Exact power conditional on simulated independent-pilot/calibration banks. Full future-bank robustness not established if stopped at StageA. No original source arrangement scored.'))
save('SUMMARY.json',records);print(status,'no manuscript rescore',flush=True)
