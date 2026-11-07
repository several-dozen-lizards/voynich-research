"""Receipt and custody verification; not a new scientific run."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
import hashlib,json,math
P=Path(__file__).parent;ROOT=P.parents[1]
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read('PLAN.json');freeze=read('CODE-FREEZE.json');checks={}
checks['frozen_files_unchanged']=all(sha(P/n)==expected for n,expected in freeze['files'].items())
checks['source_unchanged']=sha(ROOT/plan['inputs']['known_text'])==freeze['source_sha256']
checks['adapter_unchanged']=sha(ROOT/plan['inputs']['adapters'])==freeze['external_adapter_sha256']
before=read('BASELINE-BEFORE.json');after={n:sha(ROOT/n) for n in before['files']};changed=[n for n,s in before['files'].items() if after[n]!=s]
base=ROOT/'ordered-name-lists-v7c/attempt-3-v7.2'
current={str(p.relative_to(ROOT)).replace('\\','/') for p in base.rglob('*') if p.is_file()};previous={n for n in before['files'] if n.startswith('ordered-name-lists-v7c/attempt-3-v7.2/')}
checks['baseline_all_files_unchanged']=not changed and current==previous
(P/'BASELINE-AFTER.json').write_text(json.dumps(dict(files=after,changed=changed,added=sorted(current-previous),removed=sorted(previous-current)),indent=2)+'\n',encoding='utf-8')
q=read('QUALIFICATION.json');e2=read('E2-TRIALS.json');order=read('ORDER-TRIALS.json');wrong=read('WRONG-KEY-TRIALS.json');banks=read('KEY-BANKS.json');inputs=read('INPUTS.json')
checks['single_permitted_control_source']=q['data_reads']==inputs['read_allowlist']==[plan['inputs']['known_text']]
checks['vault_closed']=q['vault']=='CLOSED' and q['full_B_C_qualification'] is False
checks['all_key_banks_complete']=all(z['n']==1000 and z['distinct_keys']==1000 and len(z['scores'])==len(z['key_hashes'])==1000 for z in banks.values())
checks['fresh_wrong_key_cohorts']=all(len([r for r in wrong if r['bank']==b])==200 for b in ('original','role')) and len({r['key_sha256'] for r in wrong})==400 and not ({r['key_sha256'] for r in wrong}&{h for z in banks.values() for h in z['key_hashes']})
checks['frozen_200_per_cell']=True;checks['recomputed_decisions']=True;checks['valid_monte_carlo_p']=True
joint={};totals={}
for label,rows in [('E2',e2),('order',order)]:
    groups=defaultdict(list);bytrial=defaultdict(dict)
    for r in rows:
        prefix=(r['route'],str(r.get('geometry','')),r['scenario'])
        groups[prefix+(r['reading'],)].append(r);bytrial[prefix+(r['trial'],)][r['reading']]=r
        ps=list(r['p'].values()) if isinstance(r['p'],dict) else [r['p']]
        if r.get('rejected'):
            expected=False
        else:
            expected=all(p is not None and p<=plan['alpha'] for p in ps)
            for p in ps:
                if p is None or not 1/1001<=p<=1 or abs(p*1001-round(p*1001))>1e-8:checks['valid_monte_carlo_p']=False
        checks['recomputed_decisions'] &= r['flag']==expected
    for k,rs in groups.items():checks['frozen_200_per_cell'] &= sorted(r['trial'] for r in rs)==list(range(200))
    jgroups=defaultdict(list)
    for k,rr in bytrial.items():
        assert set(rr)=={'H','F'};jgroups[k[:-1]].append(rr['H']['flag'] and rr['F']['flag'])
    joint[label]={':'.join(k):dict(n=len(v),both_flags=sum(v),rate=sum(v)/len(v),interpretation='Dependent alternate readings; not independent replication') for k,v in jgroups.items()}
    totals[label]=dict(trials=len(rows),cells=len(groups))
checks['reported_gate_completeness']=len(q['gates'])==len(q['E2'])+len(q['order'])+4
checks['oracle_coverage']=q['oracles']['e2_panels']>=18000 and q['oracles']['alignment_panels']>=10000 and q['oracles']['exact_numeric_labels']>0
checks['qualification_label_matches_gates']=(q['status']=='QUALIFIED_ON_DECLARED_ADAPTER_CONTROL_SCOPE')==all(q['gates'].values())
out=dict(status='VERIFIED' if all(checks.values()) else 'VERIFICATION_FAILED',checks=checks,changed_baseline_files=changed,baseline_files=len(before['files']),totals=totals,joint=joint,scientific_status=q['status'],failed_cells=q['failed'],vault='CLOSED')
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status=out['status'],checks=checks,totals=totals,baseline_files=out['baseline_files'])))
sys.exit(not all(checks.values()))
