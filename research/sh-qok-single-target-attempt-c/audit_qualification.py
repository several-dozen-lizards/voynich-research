"""Replay frozen synthetic labels and independently check every trial quota/gate."""
import json,hashlib,math
from collections import Counter,defaultdict
from pathlib import Path
import engine

R=Path(__file__).resolve().parent

def main():
    mask=json.loads((R/'MASKED.json').read_text());events={c:[v for v in mask if v['cell']==c] for c in engine.CELLS}
    trials=[json.loads(v) for v in (R/'SYNTHETIC-TRIALS.jsonl').read_text().splitlines()]
    assert len(trials)==5000
    assert len({(r['cell'],r['kind'],r['scenario'],r['trial']) for r in trials})==5000
    seeds=set();groups=defaultdict(list)
    for r in trials:
        assert r['seed'] not in seeds;seeds.add(r['seed'])
        y=engine.synthetic(events[r['cell']],r['scenario'],r['seed'],r['kind']=='H2')
        assert hashlib.sha256(y.astype('uint8').tobytes()).hexdigest()==r['synthetic_outcome_sha256']
        p=r['result']['p'];flag=p is not None and p<.0125
        if r['kind']=='H2':flag=flag and r['result']['gain_bits']>0
        assert flag==r['flag'];groups[r['kind'],r['cell'],r['scenario']].append(r)
    qual=json.loads((R/'QUALIFICATION.json').read_text())['results'];gatechecks=0
    for (kind,cell,scene),rr in groups.items():
        n=len(rr);assert n==(200 if kind=='H1' else 100)
        k=sum(r['flag'] for r in rr);p=k/n;z=1.959963984540054
        lohi=[(2*n*p+z*z+sign*z*math.sqrt(z*z+4*n*p*(1-p)))/(2*(n+z*z)) for sign in [-1,1]]
        rec=next(v for v in qual[kind][cell]['controls'] if v['scenario']==scene)
        assert max(abs(a-b) for a,b in zip(lohi,rec['wilson95']))<1e-12
        assert rec['flags']==k
        gate=lohi[0]>=.8 if rec['role']=='power' else lohi[1]<=.05 if rec['role']=='null' else None
        assert gate==rec['gate'];gatechecks+=1
    output=dict(status='PASS',trial_count=5000,unique_seed_count=len(seeds),all_synthetic_outcome_hashes_replayed=True,all_flags_recomputed=True,independent_Wilson_gate_checks=gatechecks)
    (R/'QUALIFICATION-AUDIT.json').write_text(json.dumps(output,indent=2),encoding='utf-8');print(json.dumps(output,indent=2))

if __name__=='__main__':main()
