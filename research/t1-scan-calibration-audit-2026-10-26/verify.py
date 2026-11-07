"""Independent receipt checks; synthetic regeneration, no source-text access."""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,math,importlib.util
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(P/'AUDIT-FREEZE.json');repair=read(P/'REPAIR-FREEZE.json');seal=read(P/'REPAIR-CODE-SEAL.json');q=read(P/'REPAIRED-QUALIFICATION.json');trials=read(P/'REPAIRED-TRIALS.json');old=read(OLD/'CONTROL-TRIALS.json');oldby={(r['reading'],r['scenario'],r['trial']):r for r in old};checks={}
checks['audit_pinned_inputs_unchanged']=all(sha(ROOT/n)==h for n,h in freeze['inputs'].items())
checks['all_original_delivery_files_unchanged']=all(sha(OLD/n)==h for n,h in read(OLD/'DELIVERY-HASHES.json')['files'].items())
checks['all_original_source_freezes_unchanged']=all(sha(ROOT/n)==h for n,h in read(OLD/'LABEL-RESOLUTION-FREEZE.json')['source_hashes'].items())
checks['repair_code_and_freeze_unchanged']=all(sha(P/n)==h for n,h in seal['files'].items())
checks['cause_sealed_before_repair']=sha(P/'CAUSE.json')==repair['cause_sha256']
checks['cause_evidence_unchanged']=all(sha(P/n)==h for n,h in read(P/'CAUSE.json')['evidence_files'].items())
checks['same2000datasets']=len(trials)==2000 and len({(r['reading'],r['scenario'],r['trial']) for r in trials})==2000 and {(r['reading'],r['scenario'],r['trial']) for r in trials}==set(oldby)
checks['full17marginal_tests_and_MC_resolution']=all(len(r['scan_p'])==17 and all(p is None or 1/10001<=p<=1 and abs(p*10001-round(p*10001))<1e-8 for p in r['scan_p']) for r in trials)
checks['primary_unchanged_and_NE']=all(r['primary']==oldby[(r['reading'],r['scenario'],r['trial'])]['primary'] and r['primary']['p'] is None and r['primary']['status']=='NOT_ESTIMABLE' for r in trials)
checks['Holm_independent']=True;checks['flags_independent']=True;cells=defaultdict(list)
for r in trials:
 ps=r['scan_p'];order=sorted(range(17),key=lambda j:ps[j] if ps[j] is not None else 1.);adjusted=[None]*17;v=0.
 for rank,j in enumerate(order):
  v=max(v,min(1.,(17-rank)*(ps[j] if ps[j] is not None else 1.)))
  if ps[j] is not None:adjusted[j]=v
 checks['Holm_independent'] &= adjusted==r['scan_holm'];checks['flags_independent'] &= r['scan_family_flag']==any(p is not None and p<.05 for p in adjusted) and r['qok_scan_flag']==(adjusted[0] is not None and adjusted[0]<.05)
 cells[(r['reading'],r['scenario'])].append(r)
checks['all10cells200each']=len(cells)==10 and all(sorted(r['trial'] for r in rr)==list(range(200)) for rr in cells.values())
checks['summary_and_original_paired_flags_independent']=True;diagnostics={}
for (reading,scenario),rr in cells.items():
 n=len(rr);complete=sum(r['scan_estimable_classes']==17 for r in rr);flag=sum(r['scan_family_flag'] for r in rr);qok=sum(r['qok_scan_flag'] for r in rr);s=q['cells'][reading+':'+scenario];pos=scenario=='positive-1.5x'
 z=1.959963984540054;p=flag/n;upper=(p+z*z/(2*n)+z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n);gate=complete==200 and (qok/n>=.8 if pos else upper<=.05)
 oldflag=sum(oldby[(reading,scenario,r['trial'])]['scan_family_flag'] for r in rr)
 checks['summary_and_original_paired_flags_independent'] &= s['scan_complete_estimable']==complete and s['scan_family_flags']==flag and s['scan_qok_flags']==qok and s['scan_gate']==gate and s['original_family_flags']==oldflag and s['scan_false_family_flag_rate']==(flag/n if complete==200 and not pos else None)
 diagnostics[reading+':'+scenario]=dict(n=n,old_flags=oldflag,new_flags=flag,old_complete=s['original_complete'],new_complete=complete,old_qok=s['original_qok_flags'],new_qok=qok,complete_family_flags=s['complete_family_flags'],upper95_if_all_trials_defined=upper if complete==200 and not pos else None,gate=gate,observed_failures_by_class={str(j):sum(r['scan_p'][j] is None for r in rr) for j in range(17)})
# Recreate every synthetic dataset through the separately preserved old generator.
s=importlib.util.spec_from_file_location('old_generator',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);rows=read(OLD/'SUPPORT-ROWS.json');ml=defaultdict(int)
for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:ml[(r['task_id'],r['block_id'])]=max(ml[(r['task_id'],r['block_id'])],r['line_number'])
checks['all_original_generator_seed_replays']=True
for index,r in enumerate(trials):
 Y=c.simulate(rows[r['reading']],r['scenario'],r['reading'],r['trial'],ml);checks['all_original_generator_seed_replays'] &= hashlib.sha256(Y.astype('<i4').tobytes()).hexdigest()==r['synthetic_counts_sha256']
 if (index+1)%500==0:print('independent synthetic replays',index+1,flush=True)
checks['engineering_passed']=read(P/'REPAIR-ENGINEERING.json')['status']=='PASS' and q['oracles']['original_observed_support']==34000 and q['oracles']['partition_consistent_observed_datasets']==2000 and q['oracles']['original_conditional_reference_statistics']>0
checks['no_automatic_release_or_alpha']=q['outcome_join'] is False and q['vault']=='CLOSED' and q['real_word_classes_computed']==0 and q['T1_primary']=='NOT_ESTIMABLE' and q['T1_overall']=='NOT_QUALIFIED' and q['alpha_V']=='UNCHANGED_UNSPENT'
result=dict(status='VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,diagnostics=diagnostics,real_word_classes_computed=0,outcome_join=False,vault='CLOSED')
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2));sys.exit(not all(checks.values()))
