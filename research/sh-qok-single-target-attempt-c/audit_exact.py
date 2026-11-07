"""Additional independent integer-count oracle for manuscript conditional p-values.

Does not import the numerical test engine. Integer coefficients count every
sh-label assignment with fixed stratum margins; this avoids hypergeom PMFs.
"""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,math,hashlib

R=Path(__file__).resolve().parent

def audit():
    rows=list(csv.DictReader((R/'EVENTS.csv').open(encoding='utf-8',newline='')))
    primary=json.loads((R/'PRIMARY.json').read_text());checks=[]
    for result in primary:
        if result['p'] is None:
            checks.append(dict(cell=result['cell'],status='NO_INFERENTIAL_P_TO_CHECK'));continue
        groups=defaultdict(list)
        for row in rows:
            if row['cell']==result['cell'] and not row['exclusion_reason']:groups[row['folio'],row['family']].append(row)
        dist=Counter({0:1});denominator=1;observed=0
        for group in groups.values():
            n=len(group);ns=sum(r['origin'].startswith('sh') for r in group);t=sum(int(r['outcome']) for r in group)
            observed+=sum(int(r['outcome']) for r in group if r['origin'].startswith('sh'))
            local={k:math.comb(t,k)*math.comb(n-t,ns-k) for k in range(max(0,ns-(n-t)),min(ns,t)+1)}
            denominator*=math.comb(n,ns);new=Counter()
            for k,v in dist.items():
                for j,w in local.items():new[k+j]+=v*w
            dist=new
        assert sum(dist.values())==denominator
        numerator=sum(v for k,v in dist.items() if k>=observed);p=numerator/denominator
        assert abs(p-result['p'])<1e-11,(p,result['p'])
        checks.append(dict(cell=result['cell'],status='PASS',integer_count_p=p,engine_p=result['p'],denominator_bits=denominator.bit_length(),conditional_support=len(dist)))
    out=dict(status='PASS',method='Independent exact integer assignment enumeration via polynomial counts',checks=checks,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (R/'EXACT-INTEGER-AUDIT.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))

if __name__=='__main__':audit()
