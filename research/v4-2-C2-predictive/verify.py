"""Independent scalar likelihood, leakage and preservation checks."""
from pathlib import Path
from collections import defaultdict
import csv,json,hashlib,math,re
R=Path(__file__).resolve().parent
CONTEXTS=['C1','C2','C3','C4','C5','C6','C7','C8-4','C8-5']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(x,why):
    if not x:raise RuntimeError(why)
def group(pg):
    number=re.fullmatch(r'f(\d+)[rv]\d*',pg)[1]
    return 'rosettes-foldout' if int(number) in (85,86) else 'f'+number
def ll(a,ns,nc,k,beta):
    support=range(max(0,k-nc),min(ns,k)+1)
    logs=[math.log(math.comb(ns,j))+math.log(math.comb(nc,k-j))+j*beta for j in support]
    largest=max(logs);normalizer=largest+math.log(math.fsum(math.exp(v-largest) for v in logs))
    return math.log(math.comb(ns,a))+math.log(math.comb(nc,k-a))+a*beta-normalizer
def main():
    manifest=json.loads((R/'SOURCE-MANIFEST.json').read_text())
    check(all(sha(p)==h for p,h in manifest['files'].items()),'Original source changed')
    protocol=json.loads((R/'PROTOCOL.json').read_text())
    check(all(sha(R/n)==h for n,h in protocol['code_hashes'].items()),'Frozen code changed')
    phases=[];prefix=b''
    for line in (R/'PHASES.jsonl').read_bytes().splitlines(keepends=True):
        phase=json.loads(line);check(phase['previous_log_sha256']==(hashlib.sha256(prefix).hexdigest() if prefix else None),'Phase hash chain failed')
        check(all(sha(R/n)==h for n,h in phase['hashes'].items()),'Sealed artifact drift')
        phases.append(phase['phase']);prefix+=line
    check(phases.index('fixed_synthetic_controls_complete_before_manuscript_CV')<phases.index('one_shot_manuscript_predictive_comparison_complete'),'Controls not before manuscript')
    source={}
    with (R/'inputs/STRATUM-TABLES.csv').open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            if row['view']!='available' or row['context'] not in CONTEXTS:continue
            a,b,c,d=[int(row[k]) for k in ('a','b','c','d')]
            source[row['reading'],row['folio'],row['family']]=dict(a=a,ns=a+b,nc=c+d,k=a+c,context=row['context'])
    data=json.loads((R/'RESULTS.json').read_text());foldings=json.loads((R/'FOLDS.json').read_text())
    arithmetic_checks=0;max_error=0.;fallback_checks=0
    for co in ('H','F'):
        result=data['results'][co]
        for repeat in [result['primary']]+result['partition_sensitivities']:
            folds=foldings[repeat['partition_seed']];scores=repeat['rows'];fits={f['fold']:f for f in repeat['fits']}
            keys=[(co,s['folio'],s['family']) for s in scores]
            check(len(keys)==len(set(keys)) and set(keys)=={k for k in source if k[0]==co},'OOF coverage failed')
            dc=0.;common=0.;vary=0.
            for score in scores:
                row=source[co,score['folio'],score['family']];fold=folds[group(score['folio'])]
                check(fold==score['fold'] and group(score['folio'])==score['group'],'Fold/physical group mismatch')
                f=fits[fold];i=CONTEXTS.index(row['context'])
                lc=ll(row['a'],row['ns'],row['nc'],row['k'],f['common']['beta'][i])
                lv=ll(row['a'],row['ns'],row['nc'],row['k'],f['varying']['beta'][i])
                error=max(abs(lc-score['common_LL']),abs(lv-score['varying_LL']),abs((lv-lc)-score['delta_LL']))
                check(error<1e-9,'Independent scalar likelihood mismatch');max_error=max(error,max_error);arithmetic_checks+=2
                common+=lc;vary+=lv;dc+=lv-lc
                if row['context'] in f['varying']['unseen_contexts']:
                    check(abs(f['varying']['beta'][i]-f['varying']['shared_beta'])<1e-12,'Unseen context fallback failed');fallback_checks+=1
            check(abs(common-repeat['common_LL'])<1e-8 and abs(vary-repeat['varying_LL'])<1e-8 and abs(dc-repeat['delta_LL_nats'])<1e-8,'OOF totals mismatch')
    controls=json.loads((R/'CONTROLS.json').read_text());coords=[(r['reading'],r['scenario'],r['trial']) for r in controls['records']]
    check(len(coords)==160 and len(set(coords))==160,'Fixed simulation trials missing/duplicated')
    state=json.loads((R.parent/'voynich-loop/LEDGER.json').read_text())
    check(state['mode']=='STAGED' and not state['cycles'],'Loop activated')
    output=dict(status='PASS',scalar_likelihood_checks=arithmetic_checks,max_scalar_error=max_error,
        unseen_context_fallback_checks=fallback_checks,all_heldout_rows_scored_once_per_partition=True,
        fixed_control_datasets=len(coords),source_files_unchanged=len(manifest['files']),loop_inactive=True,
        no_vault_access=True,retrospective=True,phase_order=phases,
        artifacts={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'})
    (R/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='artifacts'},indent=2))
if __name__=='__main__':main()
