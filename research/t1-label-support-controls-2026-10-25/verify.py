"""Verify receipts, isolation and declared support/control decisions without native text."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict
import json,csv,hashlib,math
P=Path(__file__).parent;ROOT=P.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};label=read(P/'LABEL-RESOLUTION-FREEZE.json');support=read(P/'SUPPORT.json');rows=read(P/'SUPPORT-ROWS.json');masks=read(P/'READABILITY-MASKS.json');q=read(P/'QUALIFICATION.json');trials=read(P/'CONTROL-TRIALS.json');plan=read(P/'CONTROL-FREEZE.json')
checks['frozen_inputs_unchanged']=all(sha(ROOT/n)==s for n,s in label['source_hashes'].items())
checks['support_freeze_unchanged']=all(sha(P/n)==s for n,s in read(P/'SUPPORT-CODE-FREEZE.json')['files'].items())
checks['controls_freeze_unchanged']=all(sha(P/n)==s for n,s in read(P/'CONTROL-CODE-FREEZE.json')['files'].items())
checks['final_control_code_pinned']=sha(P/'controls-v2.py')==read(P/'IMPLEMENTATION-PRESTART-REPAIR.json')['code_sha256']
resolved=read(P/'LABELS.json');checks['complete_original_label_population']=len(resolved)==len({r['id'] for r in resolved})==1145
checks['consensus_rule_exact']=all(r['label']==(r['A'] if r['A']==r['B'] else None) for r in resolved)
checks['disagreements_retained_not_NO']=sum(r['label'] is None for r in resolved)==233 and support['unresolved_physical_lines']==233 and support['consensus_physical_lines']==912
checks['H_F_separate_no_substitution']=len(masks['rows'])==2290 and Counter(r['reading'] for r in masks['rows'])=={'H':1145,'F':1145} and sum(not r['available'] for r in masks['rows'] if r['reading']=='F')==29
allowed={'id','folio','reading','locus','available','reason','original_slots','initial_slot_present','initial_readable','noninitial_mask'}
checks['readability_masks_no_real_features']=all(set(r)<=allowed and (not r['available'] or all(type(v) is bool for v in r['noninitial_mask'])) for r in masks['rows']) and masks['raw_tokens_exported']==masks['real_word_classes_computed']==masks['image_label_files_read']==0
checks['physical_first_slot_not_promoted']=all(not r['available'] or len(r['noninitial_mask'])==max(0,r['original_slots']-1) for r in masks['rows'])
checks['reserved_bodies_not_tokenized']=masks['reserved_bodies_tokenized']==0 and all(r['folio'] not in {'f72v1','f72v2','f73r','f73v'} for rr in rows.values() for r in rr)
checks['support_counts_recomputed']=True
labelmap={r['id']:r['label'] for r in resolved};maskmap={(r['reading'],r['id']):r for r in masks['rows']}
for reading in ('H','F'):
 rr=rows[reading];ss=support['readings'][reading]
 checks['support_counts_recomputed'] &= len(rr)==ss['audit']['consensus_lines'] and sum(r['n'] for r in rr)==ss['audit']['readable_noninitial_slots'] and sum(r['unknown'] for r in rr)==ss['audit']['unknown_noninitial_slots']
 for r in rr:
  source=maskmap[(reading,r['id'])];checks['support_counts_recomputed'] &= r['n']==sum(source['noninitial_mask']) and r['label']==labelmap[r['id']] and r['reading']==reading
checks['primary_design_gate_preserved']=all(not s['primary']['design_gate'] and s['primary']['informative_folios']==0 for s in support['readings'].values())
checks['equivalence_not_inferred']=all(not s['equivalence_all15_design_gate'] for s in support['readings'].values())
groups=defaultdict(list)
for r in trials:groups[(r['reading'],r['scenario'])].append(r)
checks['all2000_trials_and10_cells']=len(trials)==2000 and len(groups)==10 and all(sorted(r['trial'] for r in rr)==list(range(200)) for rr in groups.values())
checks['no_primary_undefined_as_negative']=all(r['primary'].get('p') is None and r['primary']['status']=='NOT_ESTIMABLE' for r in trials) and all(v['primary_false_flag_rate'] is None and not v['primary_gate'] for v in q['cells'].values())
checks['full17_scan_family_and_MC_resolution']=all(len(r['scan_p'])==len(r['scan_holm'])==len(r['scan_first_failure'])==17 and all(p is None or 1/10001<=p<=1 and abs(p*10001-round(p*10001))<1e-8 for p in r['scan_p']) for r in trials)
checks['Holm_and_flags_recomputed']=True
for r in trials:
 ps=r['scan_p'];order=sorted(range(17),key=lambda j:1 if ps[j] is None else ps[j]);adj=[None]*17;previous=0.
 for rank,j in enumerate(order):
  previous=max(previous,min(1.,(17-rank)*(ps[j] if ps[j] is not None else 1.)));adj[j]=previous if ps[j] is not None else None
 checks['Holm_and_flags_recomputed'] &= adj==r['scan_holm'] and r['scan_family_flag']==any(p is not None and p<.05 for p in adj)
checks['synthetic_reference_engine_agrees']=read(P/'ENGINEERING.json')['status']=='PASS' and read(P/'REFERENCE-NULL-REPLAY.json')['status']=='EXACT_REFERENCE_P_MATCH'
checks['complete_family_reference_engine_agrees']=read(P/'REFERENCE-COMPLETE-NULL-REPLAY.json')['status']=='EXACT_REFERENCE_P_MATCH'
checks['no_real_outcome_join_or_vault']=q['real_word_classes_computed']==0 and q['real_word_outcome_join'] is False and q['vault']=='CLOSED'
checks['qualification_not_rescued']=q['status']=='NOT_QUALIFIED_ON_DECLARED_REAL_SUPPORT'
# Retain flag frequencies even when a complete estimable family was unavailable; do not call abstention validated absence.
diagnostics={}
for (reading,scenario),rr in groups.items():
 complete=[r for r in rr if r['scan_estimable_classes']==17];flags=sum(r['scan_family_flag'] for r in rr);completeflags=sum(r['scan_family_flag'] for r in complete)
 diagnostics[reading+':'+scenario]=dict(n=200,complete_families=len(complete),family_flags_any_defined_classes=flags,flags_in_complete_families=completeflags,flag_fraction_all_trials=flags/200,complete_flag_fraction_all_trials=completeflags/200,qok_Holm_detections=sum(r['qok_scan_flag'] for r in rr),not_a_validated_full_family_false_positive_rate=len(complete)!=200)
result=dict(status='VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,control_diagnostics=diagnostics,qualified=False,real_outcome_join=False,vault='CLOSED')
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status=result['status'],checks=checks,diagnostics=diagnostics),indent=2));sys.exit(not all(checks.values()))
