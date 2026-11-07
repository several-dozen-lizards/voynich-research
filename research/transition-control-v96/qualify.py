from pathlib import Path
import collections,hashlib,itertools,json,math
from fractions import Fraction
from engine import edges,score,distribution,assess,binomial_null,exact_power,convolve
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
protocol={'scope':'Separate new first-order opening-class conditional control for the v78 one-word gap; Bathhand2/B/P and Starredhand3/B/P, H/F separate, same shared loci/all eligible folios. Read no manuscript tokens until qualificationPASS.',
 'state_partition':'S=literal startswith sh,Q=literal startswith qok,N=all other readable words. This preserves opening-class transitions only, not full word bigrams or character-junction counts.',
 'null':'Split source lines at unknown slots. For each readable span, fix its literal first/last words, whole-word multiset, and all nine directed S/Q/N adjacent-edge counts. Uniformly enumerate distinct compatible class sequences, then uniformly assign remaining literal words inside each class. Assignment multiplicity is constant across class sequences. Endpoints at unknown seams are pinned as a stronger added constraint, not claimed identical to the prior line-shuffle null.',
 'exact_engine':'Dynamic programming on previous/current class, remaining9edgecounts and fixed end class. Branch once per next class, NOT once per labelled edge. Return integer score histogram. Independent spans convolve exactly. No MCMC, no asymptotic tails, no MonteCarlo precision floor. Frozen250000memo-states/span budget; any budget failure blocks whole affected panel, never truncates spans or pools strata.',
 'statistics':'D2=#S X Q minus #Q X S. Primary anymiddle; sensitivity middleN only (same as prior non_target_middle). Sum over all fully readable three-token spans, never bridge unknowns/lines.',
 'correction':'Exact two-sided mean-distance randomization tail. Multiply by original v75 number of eligible opening pairs in that panel and by28 (historical14panels x2views). Conservative full-prefix-family Bonferroni bound instead of maxT, preserving original family budget without calculating all other prefix-pair tails. Their scores remain defined under the same fixed S/Q/N conditional word-order null. No new class/lag search or semantic interpretation.',
 'qualification':'Before manuscript: enumerate every authored S/Q/N string lengths1..7 and group by start/end/edgecount fiber; match exact DP histograms for both D2views and exact p rank bounds at.05, uncorrected and maximum opening-family budget. Verify literal-word assignment weights with distinct N words. Qualify exact convolution against binomial oracle of two-path fiber S N N Q N S vs S N Q N N S. Analytical power grid n32/64/128 and q.50/.65/.80/.95/1. Gates: all exact identities/rank bounds; at128informative spans and worst-casebudget, power>=.80 forq.80 and>=.90 forq.95; all-positive32-span corrected tail<=.05. Any fail prohibits manuscript scoring. Low-dose/small-sample failures retained; controls do not establish historical corpus power.',
 'mobility':'For manuscript report all span alternative-path counts, variable-score spans, exact null support/variance and minimum attainable corrected p. Constant or acceptance-floor>.05 means insufficient conditional resolution, not a decisive null. Preserve every panel/view and reverse/unknown/one-path case.',
 'limits':'Focused test of residual gap order after first-order opening-class transitions. Does not retest adjacency (conditioned fixed), prove a junction cause, establish grammar or assign meanings. Strong conditioning can remove signal and power. Corpus already inspected, H/F alternate readings not independent replication. Prior results and other recent ending/position-control failures unchanged.'}
inputs=[P/'opening-order-audit-v75/FAMILY-PRECISION.json',P/'one-gap-order-v78/PROTOCOL.json']
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','qualify.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
budget=28*max(p['comparisons'] for p in load(inputs[0]));fibers=collections.defaultdict(list)
for n in range(1,8):
 for seq in itertools.product(range(3),repeat=n):fibers[(seq[0],seq[-1],edges(seq))].append(seq)
checks=0;rankfail=[]
for fi,((start,end,ec),seqs) in enumerate(fibers.items()):
 for view in [False,True]:
  expected=dict(collections.Counter(score(s,view) for s in seqs));actual,calls=distribution(start,end,ec,view);assert actual==expected
  for correction in [1,budget]:
   flags=sum(n for v,n in actual.items() if assess(actual,v,correction)['corrected_p']<=.05);assert Fraction(flags,len(seqs))<=Fraction(1,20)
  checks+=1
 if (fi+1)%500==0:print('fibers',fi+1,flush=True)
# Literal assignments: two class sequences, each with 3! distinct N assignments.
words=['shaa','na','nb','nc','qokbb','shaa'];targetedges=edges((0,2,2,1,2,0));weights=collections.Counter()
for inside in set(itertools.permutations(words[1:-1])):
 ws=[words[0],*inside,words[-1]];seq=tuple(0 if w.startswith('sh') else 1 if w.startswith('qok') else 2 for w in ws)
 if edges(seq)==targetedges:weights[seq]+=1
assert len(weights)==2 and set(weights.values())=={math.factorial(3)}
fiber=distribution(0,0,targetedges,False)[0];assert fiber=={-1:1,1:1};assert distribution(0,0,targetedges,True)[0]==fiber
poly={0:1}
for n in range(1,129):
 poly=convolve(poly,fiber);assert poly==binomial_null(n)
power=[]
for n in [32,64,128]:
 for q in [Fraction(1,2),Fraction(13,20),Fraction(4,5),Fraction(19,20),Fraction(1)]:power.append(dict(informative_spans=n,positive_path_probability=str(q),power=exact_power(n,q,budget)))
p80=next(x['power'] for x in power if x['informative_spans']==128 and x['positive_path_probability']=='4/5');p95=next(x['power'] for x in power if x['informative_spans']==128 and x['positive_path_probability']=='19/20');strong32=assess(binomial_null(32),32,budget)['corrected_p']
gates=dict(exact_DP_oracle=True,rank_bounds=True,literal_assignment_constant=True,binomial_convolution=True,power80_at128=p80>=.8,power95_at128=p95>=.9,all_positive32_resolution=strong32<=.05)
out=dict(status='PASS' if all(gates.values()) else 'FAIL',gates=gates,authored_sequences=sum(len(v) for v in fibers.values()),fibers=len(fibers),DP_view_checks=checks,worst_case_correction=budget,power_grid=power,all_positive32_corrected_p=strong32,limits='Exact authored conditional controls, not independent historical labels or a corpus-specific power guarantee. Every low-power case retained.')
save('QUALIFICATION.json',out);print(out['status'],gates,p80,p95,flush=True)
