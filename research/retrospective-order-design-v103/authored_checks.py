"""Small exact implementation checks, NOT full qualification or source power."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from itertools import product
import hashlib,json
from engine import edges,score,marginal,tails,calibrated
R=Path(__file__).resolve().parent
assert (R/'FREEZE.json').exists(),'Freeze design before authored checks'
freeze=json.loads((R/'FREEZE.json').read_text(encoding='utf-8'))
for name,digest in freeze['local_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest
# Includes overlapping A/B signatures and two distinct S signatures.
alphabet=((0,1),(0,3),(1,2),(2,0));fibers=defaultdict(lambda: [Counter(),Counter()]);sequences=0
for n in range(1,7):
    for seq in product(alphabet,repeat=n):
        interior=tuple(sorted(Counter(seq[1:-1]).items()));key=(seq[0],seq[-1],interior,edges(seq))
        for view in (0,1):fibers[key][view][score(seq,bool(view))]+=1
        sequences+=1
for (start,end,counts,ec),expected in fibers.items():
    for view in (0,1):
        actual,_=marginal(start,end,dict(counts),ec,bool(view))
        assert actual==expected[view]
# Exact two-sided marginal p-values and family minP rank bound on finite toy orbits.
families=0
for values in [list(product((-1,0,1),repeat=2)),[(0,0),(0,0),(1,-1),(-1,1),(2,0)],[(0,0)] ]:
    marginals=[Counter(v[j] for v in values) for j in range(2)];maps=list(map(tails,marginals))
    mins=[min(maps[j][v[j]] for j in range(2)) for v in values]
    adjusted=[Fraction(sum(x<=m for x in mins),len(mins)) for m in mins]
    for alpha in (Fraction(1,20),Fraction(1,4),Fraction(1,2),Fraction(1)):
        assert Fraction(sum(p<=alpha for p in adjusted),len(values))<=alpha
    # Duplicated columns never alter the minimum.
    assert mins==[min(maps[0][v[0]],maps[1][v[1]],maps[0][v[0]]) for v in values]
    families+=1
assert calibrated(Fraction(0),[Fraction(1)]*4096)==Fraction(28,4097)
assert calibrated(Fraction(1),[Fraction(1)]*4096)==1
assert all(p>0 for p in tails({-2:1,0:6,2:1}).values())
assert tails({5:1})=={5:Fraction(1)}
# Exact rank probability including ties, for B=2 calibration rows and a toy observation.
for scores in ([0,1,2],[0,0,1]):
    for alpha in (Fraction(1,3),Fraction(2,3),Fraction(1)):
        outcomes=list(product(scores,repeat=3))
        rejected=sum(Fraction(1+sum(c<=v[0] for c in v[1:]),3)<=alpha for v in outcomes)
        assert Fraction(rejected,len(outcomes))<=alpha
out=dict(status='PASS: AUTHORED ARITHMETIC ONLY',authored_sequences=sequences,signature_fibers=len(fibers),view_histograms_checked=2*len(fibers),toy_full_family_orbits=families,exact_minP_rank_and_duplicate_column_checks='PASS',plus_one_rank_tie_checks='PASS',manuscript_files_read=False,full_search_sampler_qualification='NOT RUN',actual_layout_power='NOT RUN',manuscript_scoring='CLOSED',old_failed_gates='unchanged')
(R/'AUTHORED-CHECKS.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
