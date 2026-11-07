import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,math
P=Path(__file__).parent;ROOT=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
q=read(P/'QUALIFICATION.json');nq=read(P/'NUMERAL-QUALIFICATION.json');checks={}
before=read(ROOT/'bc-adapter-qualification-2026-10-25/attempt-2/BASELINE-BEFORE.json');changed=[n for n,s in before['files'].items() if sha(ROOT/n)!=s];checks['all346_baseline_files_unchanged']=not changed
oldroot=ROOT/'ordered-name-lists-v7c/attempt-3-v7.2';now={str(p.relative_to(ROOT)).replace('\\','/') for p in oldroot.rglob('*') if p.is_file()};previous={n for n in before['files'] if n.startswith('ordered-name-lists-v7c/attempt-3-v7.2/')};checks['no_baseline_file_added_removed']=now==previous
checks['initial_plan_and_code_preserved']=all(sha(P/n)==s for n,s in read(P/'FREEZE.json')['files'].items())
checks['final_execution_code_pinned']=sha(P/'bridge-v6-native.py')==read(P/'EXACT-NATIVE-EXECUTION.json')['code_sha256']
checks['native_equivalence']=read(P/'NATIVE-VERIFICATION.json')['status']=='EXACT_ACCELERATOR_VERIFIED'
checks['all_E2_qualification_gates']=all(q['gates'].values())
checks['12_exact_unchanged_projections']=q['raw_projection_regressions']==12
checks['compiled_E2_reference_replays']=q['e2_reference_checks']>=36
banks=list(P.glob('C2-BANK-*.json'));checks['all12_C2_banks_complete']=len(banks)==12
for p in banks:
 b=read(p);checks['all12_C2_banks_complete'] &= len(b['key_hashes'])==len(set(b['key_hashes']))==len(b['scores'])==1000
 checks['all12_C2_banks_complete'] &= all(z['E2']['n']==q['paired_spans'] and z['E3']['value'] is not None and z['E4']['value'] is not None for z in b['scores'])
negative=read(P/'NEGATIVE.json');checks['400_fresh_proposals_complete']=len(negative)==len({r['key_sha256'] for r in negative})==400 and all(len([r for r in negative if r['cohort']==c])==200 for c in ('original','role'))
checks['9_profiles_179_positions']=q['list_profiles']==9 and q['list_positions']==179
checks['six_source_reflows_recorded']={r['family'] for r in read(P/'C2-REFLOW.json')}=={'G1','G2','G3','G4','G5','G6'}
trials=read(P/'NUMERAL-TRIALS.json');groups=defaultdict(list)
for row in trials:groups[(tuple(row['geometry']),row['reading'],row['scenario'])].append(row)
checks['numeral1600_trials_complete']=len(trials)==1600 and len(groups)==8 and all(sorted(r['trial'] for r in rs)==list(range(200)) for rs in groups.values())
checks['all_numeral_gates']=all(v['gate'] for v in nq['cells'].values())
checks['native_and_compiled_execution_statistical_rules_fixed']=read(P/'EXACT-NATIVE-EXECUTION.json')['method_change'] is False and read(P/'EXECUTION-COMPILED-E2.json')['method_change'] is False
checks['no_full_B_C_admission']=not q['full_B_C_admission'] and not nq['full_B_C_admission'] and q['vault']==nq['vault']=='CLOSED'
counts={c:dict(Counter(r['combined']['verdict'] for r in negative if r['cohort']==c)) for c in ('original','role')}
out=dict(status='VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,baseline_files=346,baseline_changed=changed,negative_tallies=counts,E2_reference_checks=q['e2_reference_checks'],numeral_source_replays=nq['source_panel_replays'],overall_component_scope_qualified=all(q['gates'].values()) and all(v['gate'] for v in nq['cells'].values()),full_B_C_admission=False,vault='CLOSED')
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2));sys.exit(not all(checks.values()))
