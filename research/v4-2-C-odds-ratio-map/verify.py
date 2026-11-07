"""Independent table arithmetic and preservation audit; no original analysis run."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import csv
import hashlib
import json
import math
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(x,why):
    if not x:raise RuntimeError(why)


def main():
    manifest=json.loads((R/'SOURCE-MANIFEST.json').read_text(encoding='utf-8'))
    require(all(sha(p)==h for p,h in manifest['files'].items()),'Original source changed')
    protocol=json.loads((R/'PROTOCOL.json').read_text(encoding='utf-8'))
    require(all(sha(R/p)==h for p,h in protocol['code_hashes'].items()),'Frozen code changed')
    prefix=b'';phases=[]
    for line in (R/'PHASES.jsonl').read_bytes().splitlines(keepends=True):
        record=json.loads(line)
        require(record['previous_log_sha256']==(hashlib.sha256(prefix).hexdigest() if prefix else None),'Phase chain broken')
        require(all(sha(R/n)==h for n,h in record['hashes'].items()),'Phase artifact changed')
        phases.append(record['phase']);prefix+=line
    require(phases.index('engineering_qualified_before_outcome_join')<phases.index('one_shot_descriptive_map_complete'),'Qualification order invalid')
    rows=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'))['results']
    grouped=defaultdict(list)
    with (R/'STRATUM-TABLES.csv').open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):grouped[f"{r['context']}-{r['reading']}-{r['view']}"].append(r)
    oracle=[]
    for key,out in rows.items():
        numerator=Fraction(0);denominator=Fraction(0);rdn=Fraction(0);rdd=Fraction(0)
        for row in grouped[key]:
            a,b,c,d=[int(row[k]) for k in ('a','b','c','d')];n=a+b+c+d
            numerator+=Fraction(a*d,n);denominator+=Fraction(b*c,n)
            rdn+=Fraction(a*(c+d)-c*(a+b),n);rdd+=Fraction((a+b)*(c+d),n)
        if out['status'].startswith('COUNTS'):continue
        expected=None if not numerator and not denominator else 'Infinity' if not denominator else float(numerator/denominator)
        got=out['OR']
        require((expected==got) if expected is None or isinstance(expected,str) else math.isclose(expected,got,rel_tol=1e-12,abs_tol=1e-12),'Independent OR mismatch: '+key)
        if rdd:require(math.isclose(100*float(rdn/rdd),out['MH_RD_points'],rel_tol=1e-12,abs_tol=1e-12),'Independent RD mismatch: '+key)
        boot=out['bootstrap']
        require(sum(boot[n] for n in ('finite_OR_draws','zero_OR_draws','infinite_OR_draws','undefined_OR_draws'))==4999 if boot['draws'] else True,'Bootstrap accounting mismatch')
        if boot.get('undefined_OR_draws',0):require(boot['OR_CI95'] is None,'Invalid draws silently removed')
        oracle.append(key)
    state=json.loads((R.parent/'voynich-loop/LEDGER.json').read_text(encoding='utf-8'))
    require(state['mode']=='STAGED' and not state['cycles'],'Autonomous loop state changed')
    artifacts={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('VERIFICATION.json','STDOUT.txt','STDERR.txt')}
    result=dict(status='PASS',independent_rational_OR_RD_checks=len(oracle),source_files_unchanged=len(manifest['files']),
        phase_order=phases,loop_inactive=True,no_alpha_spend=True,retrospective=True,descriptive_only=True,
        artifacts=artifacts)
    (R/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='artifacts'},indent=2))


if __name__=='__main__':main()
