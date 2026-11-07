import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,csv,hashlib,copy
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;P=R.parent;OLD=P/'sh-qok-context-map-v3';FOLLOW=P/'sh-qok-qualification-followup-v1';Q=FOLLOW/'run-2026-10-24'
sys.path.insert(0,str(OLD));import analysis as a
sys.path.insert(0,str(FOLLOW));from diagnose import oracle
ORDER=['A-P1-H','A-bath-H','A-starred-H','B-Q1-H','A-P1-F','A-bath-F','A-starred-F','B-Q1-F']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def verify_sources():
 preserved=json.loads((FOLLOW/'PRESERVED-ATTEMPT.json').read_text());assert all(sha(OLD/n)==h for n,h in preserved['hashes'].items())
 final=json.loads((Q/'FINAL-VERIFICATION.json').read_text());assert final['status']=='COMPLETE_FIXED_RUN_VERIFIED' and final['primary_trials']==396000 and final['new_manuscript_scores']==0
 assert all(sha(Q/n)==h for n,h in final['artifact_hashes'].items())
 plan=json.loads((FOLLOW/'FREEZE.json').read_text());assert all(sha(p)==h for p,h in plan['hashes'].items())
 assert json.loads((Q/'POSTRUN-AUDIT.json').read_text())['status']=='PASS'
 return preserved,final
def freeze():
 assert not (R/'FREEZE.json').exists();preserved,final=verify_sources();qualified=json.loads((Q/'PRIMARY-SUMMARY.json').read_text());assert all(qualified['cells'][k]['status']=='QUALIFIED' for k in ORDER)
 protocol=dict(status='FROZEN BEFORE SEPARATE RETROSPECTIVE RE-ADJUDICATION',authority='User explicitly authorized freeze and run in this chat',frozen_utc=datetime.now(timezone.utc).isoformat(),exposure='All manuscript material exposed/uncertified; prior outcomes and qualification results known. Neither prospective confirmation nor independent replication.',scope='Re-adjudicate unchanged v3.1 A-P1/A-bath/A-starred and B-Q1 under the completed frozen qualification follow-up. Preserve v3.1 and qualification artifacts. No new controls, folios, context pooling, glyph handling, semantic inference or heterogeneity scoring.',qualification_link=dict(source=str(Q/'PRIMARY-SUMMARY.json'),eligibility='Use only each exact matching cell-reading classified QUALIFIED by the fixed follow-up, with support still passing. Do not pool old200 and fresh controls or combine H/F. No new gates or interpretation of absence of nominal alarms as proof of exact calibration.',limits='Qualification applies to frozen geometry and authored generators. B-Q1 remains the unconditioned aggregate contrast; ordinary inherited synthetic generators can assign qok outcomes to blocked followers. Part A availability-only has the same marginal law as low-null after filtering.'),events='Reconstruct y from preserved EVENTS.csv for the exact existing MASKED-v3.1.json events, keyed reading/line/position. Require one-to-one eligible-event coverage, unchanged origin/family/available flag and frozen support for every cell. Do not open raw EVT or reserved zodiac material.',engine='Call unchanged attempt C exact one-sided sh>ch engine, folio x ending family. A uses available-only origins. B-Q1 uses C6+C7 all eligible origins. Degenerate exact distribution => NOT ESTIMABLE, p=null.',effect='Same MH risk difference and4999 percentile folio-bootstrap CIs as v3.1; fixed original seed7100000+index in cell_order. Require exact replay of saved estimates. Descriptive context map, aggregate estimates, strict sensitivity and paired surviving-share estimates are carried forward unchanged and retain their descriptive status.',cell_order=ORDER,support='Unchanged V>=80, >=8 supported pages, maximum page share<=.25. Replay against frozen v3.1 support.',multiplicity=dict(A_H=['A-P1-H','A-bath-H','A-starred-H'],A_F=['A-P1-F','A-bath-F','A-starred-F'],B_H=['B-Q1-H','B-Q2-H'],B_F=['B-Q1-F','B-Q2-F'],rule='Original Holm3 A and Holm2 B separately for each reading. Unsupported, blocked or degenerate slots occupy internal p=1 without dropping the slot and display no inferential p. Thus B-Q1 retains its factor2 while B-Q2 remains blocked. Recompute Holm for every A family rather than retaining old adjusted p-values.'),headline='PASS iff qualified, support-passing, nondegenerate, positive effect and Holm-adjusted p<=.05. NO PASS otherwise when scoreable. Both H/F must PASS for a cross-reading A-cell headline; H/F are alternate readings, not independent replications.',BQ2='UNQUALIFIED throughout. No new permutation, REML or inferential heterogeneity calculation. Internal Holm slot p=1; displayed inferential raw/adjusted p=null. Existing context estimates and heterogeneity summaries remain descriptive/unqualified. Leave both scribe2 sensitivities unqualified.',verification='Independent combinatorial p-value oracle for each scored cell; independent direct MH calculation from event outcomes; independent Holm formula; one-to-one event reconciliation; exact old effect/CI/support replay; original39 hashes and all frozen qualification artifact hashes before and after.',preservation='Write only this new directory. Original v3.1 files/statuses remain unchanged. New results are explicitly labeled separate retrospective re-adjudication; neither rewrite nor promotion inside original artifacts.')
 save('PROTOCOL.json',protocol);save('PRESERVATION.json',dict(v31=preserved,qualification_final_sha256=sha(Q/'FINAL-VERIFICATION.json'),qualification_run=str(Q)))
 paths=[R/'run.py',R/'PROTOCOL.json',R/'PRESERVATION.json',OLD/'EVENTS.csv',OLD/'MASKED-v3.1.json',OLD/'SUPPORT-v3.1.json',OLD/'PART-A.json',OLD/'PART-B-TESTS.json',OLD/'PART-B-ESTIMATES.json',OLD/'analysis.py',OLD/'preflight.py',P/'sh-qok-single-target-attempt-c/engine.py',FOLLOW/'diagnose.py',Q/'PRIMARY-SUMMARY.json',Q/'BQ2-SUMMARY.json',Q/'FINAL-VERIFICATION.json']
 save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),phase='BEFORE_NEW_MANUSCRIPT_SCORING',hashes={str(p):sha(p) for p in paths}));print('FROZEN',sha(R/'PROTOCOL.json'))
def independent_rd(vv):
 groups={}
 for v in vv:
  s=groups.setdefault((v['folio'],v['family']),[0,0,0,0]);x=v['x'];s[0]+=x;s[1]+=1-x;s[2]+=x*v['y'];s[3]+=(1-x)*v['y']
 num=den=0.
 for ns,nc,ys,yc in groups.values():
  if ns and nc:w=ns*nc/(ns+nc);num+=w*(ys/ns-yc/nc);den+=w
 return 100*num/den if den else None
def independent_holm(ps):
 order=sorted(range(len(ps)),key=lambda i:1 if ps[i] is None else ps[i]);out=[None]*len(ps)
 for rank,i in enumerate(order):
  val=min(1,max((len(ps)-j)*(ps[idx] if ps[idx] is not None else 1) for j,idx in enumerate(order[:rank+1])))
  if ps[i] is not None:out[i]=val
 return out
def execute():
 assert not (R/'PART-A.json').exists();verify_sources();frozen=json.loads((R/'FREEZE.json').read_text());assert all(sha(p)==h for p,h in frozen['hashes'].items())
 masked=json.loads((OLD/'MASKED-v3.1.json').read_text());assert all('y' not in v for v in masked)
 with (OLD/'EVENTS.csv').open(encoding='utf-8') as f:ledger=list(csv.DictReader(f))
 eligible={}
 for r in ledger:
  if r['exclusion_reason']:continue
  key=(r['reading'],r['line'],int(r['position']));assert key not in eligible;eligible[key]=r
 assert len(eligible)==len(masked);seen=set();events=[]
 for v in masked:
  key=(v['reading'],v['line'],v['position']);r=eligible[key];seen.add(key)
  assert r['origin']==v['origin'] and r['family']==v['family'] and (r['available']=='True')==v['available']
  y=int(r['outcome']);assert y==int(r['follower'].startswith('qok'));events.append(v|dict(y=y))
 assert seen==set(eligible);cc=a.cells(events);assert list(cc)==ORDER;supp=json.loads((OLD/'SUPPORT-v3.1.json').read_text());qual=json.loads((Q/'PRIMARY-SUMMARY.json').read_text());oldA=json.loads((OLD/'PART-A.json').read_text());oldB=json.loads((OLD/'PART-B-TESTS.json').read_text());old=oldA|oldB;results={};audit=[]
 for i,key in enumerate(ORDER):
  vv=cc[key];s=a.e.support(vv);assert s==supp[key];est=a.estimate(vv,7100000+i);assert est==old[key]['estimate'];assert independent_rd(vv)==est['effect_points'] or abs(independent_rd(vv)-est['effect_points'])<1e-11
  qualified=qual['cells'][key]['status']=='QUALIFIED';raw=a.e.exact(vv) if qualified and s['gate'] else dict(p=None,degenerate=None)
  if raw['p'] is not None:
   other=oracle(vv,a.np.array([v['y'] for v in vv]));assert abs(raw['p']-other)<1e-11;audit.append(dict(cell=key,p=raw['p'],independent_p=other,absolute_error=abs(raw['p']-other)))
  if old[key]['exact']['p'] is not None:assert raw==old[key]['exact']
  status='BLOCKED: QUALIFICATION' if not qualified else 'NOT ESTIMABLE' if not s['gate'] or raw['degenerate'] else 'SCORED'
  row=dict(status=status,qualification='QUALIFIED BY FIXED FOLLOW-UP',estimate=est,exact=raw,original_v31_status=old[key]['status'])
  if key.startswith('A-'):
   for field in ['aggregate','strict_sensitivity','surviving_share','A1b_identity']:row[field]=copy.deepcopy(oldA[key][field])
  results[key]=row
 for co in ['H','F']:
  results['B-Q2-'+co]=dict(status='UNQUALIFIED',p=None,holm_p=None,holm_internal_p=1,reason='Frozen exclusion: failed original qualification and structural zero-variance diagnostic; follow-up did not qualify B-Q2. No heterogeneity re-scoring.')
 families={}
 for co in ['H','F']:
  for family,keys in [('A',[f'A-{name}-{co}' for name in ['P1','bath','starred']]),('B',[f'B-Q1-{co}',f'B-Q2-{co}'])]:
   ps=[results[k]['exact']['p'] if 'exact' in results[k] else None for k in keys];adjusted=a.e.holm(ps);assert adjusted==independent_holm(ps)
   families[family+'-'+co]=dict(members=keys,raw_p=ps,internal_p=[1 if p is None else p for p in ps],adjusted_p=adjusted)
   for k,p in zip(keys,adjusted):
    results[k]['holm_p']=p
    if results[k]['status']=='SCORED':results[k]['status']='PASS' if p is not None and p<=.05 and results[k]['estimate']['effect_points']>0 else 'NO PASS'
 A={k:v for k,v in results.items() if k.startswith('A-')};B={k:v for k,v in results.items() if k.startswith('B-')};save('PART-A.json',A);save('PART-B-TESTS.json',B);save('HOLM-FAMILIES.json',families);save('SUPPORT-REPLAY.json',{k:a.e.support(v) for k,v in cc.items()});save('QUALIFICATION-LINK.json',dict(cells=qual['cells'],source=str(Q/'PRIMARY-SUMMARY.json'),source_sha256=sha(Q/'PRIMARY-SUMMARY.json'),BQ2='UNQUALIFIED'))
 # Carry-forward copies have no new inferential status.
 (R/'PART-B-ESTIMATES-DESCRIPTIVE.json').write_bytes((OLD/'PART-B-ESTIMATES.json').read_bytes())
 save('COVERAGE-REPLAY.json',dict(eligible_events=len(events),eligible_ledger_events=len(eligible),one_to_one=True,all_origins_families_flags_outcomes_consistent=True))
 def fmt(x):return 'NA' if x is None else f'{x:.6g}'
 lines=['RETROSPECTIVE — all material exposed or uncertified (v100/v102).','','Separate re-adjudication using the completed fixed qualification follow-up. v3.1 remains unchanged. No new material, independent replication or prospective confirmation.','','| Cell | Reading | Effect, points [folio-bootstrap 95% CI] | Raw p | Holm p | New status | v3.1 status retained |','|---|---|---|---|---|---|---|']
 for key in ORDER:
  r=results[key];est=r['estimate'];ci=est['CI95_points'];lines.append(f"| {key[:-2]} | {key[-1]} | {est['effect_points']:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}] | {fmt(r['exact']['p'])} | {fmt(r['holm_p'])} | {r['status']} | {r['original_v31_status']} |")
 lines+=['','Part A retains Holm over P1/bath/starred separately within H and F. Part B retains Holm over B-Q1/B-Q2 separately within H and F. B-Q2 is unqualified, represented internally by p=1 without deleting its slot; B-Q1 consequently retains the factor-two adjustment. B-Q2 displays no inferential raw or adjusted p.','','Cross-reading Part A headlines:']
 for name in ['P1','bath','starred']:lines.append(f"- {name}: {'PASS in both H and F' if all(A[f'A-{name}-{co}']['status']=='PASS' for co in ['H','F']) else 'NO BOTH-READING PASS'}.")
 lines+=['','B-Q1: '+('PASS in both H and F.' if all(B['B-Q1-'+co]['status']=='PASS' for co in ['H','F']) else 'No both-reading pass.')+' This is the original aggregate Currier-A association, not an available-only Currier-A test. Availability can contribute to an aggregate contrast; the qualification retains the inherited abstract generators. A pass supports this association in these samples, not a scribe-independent mechanism or grammar.','','Part A surviving shares are carried forward descriptively, using the original paired folio bootstrap:','','| Cell | H share [95% CI] | F share [95% CI] |','|---|---|---|']
 for name in ['P1','bath','starred']:
  vals=[]
  for co in ['H','F']:
   rr=A[f'A-{name}-{co}']['surviving_share'];vals.append(f"{rr['share']:.3f} [{rr['CI95'][0]:.3f}, {rr['CI95'][1]:.3f}]")
  lines.append(f"| {name} | {vals[0]} | {vals[1]} |")
 lines+=['','A surviving-share ratio above one is possible because the available-only and aggregate estimands have different denominators and stratum weights. These ratios are descriptive, not a causal mediation fraction. A both-reading Part A pass means the association survives the specified availability condition on these retrospective samples; it does not separate grammar, junction spelling or other available-follower structure.','','B-Q2 and both scribe-2 sensitivities remain UNQUALIFIED. No new heterogeneity statistics or permutation banks were computed. Existing context map and heterogeneity estimates remain descriptive and cannot establish heterogeneity or its absence. The old W sensitivity remains unsupported and outside the Holm families.','','All eight matched A/Q1 qualification cells passed the fixed follow-up gates. The old200 and fresh trials were not pooled. Qualification is finite to the authored generators and actual masked geometry. H/F are alternate readings; they were not pooled or treated as independent replications.','','Every effect, CI and support value replayed v3.1 exactly. Independent combinatorial p-values and direct MH effects matched; an independent Holm calculation verified each fixed family. The event ledger reconciled one-to-one against the frozen masked inventory. No raw EVT or reserved zodiac material was opened.','','Original manuscript statuses remain historical v3.1 results. The statuses in this directory belong only to this authorized, separately frozen retrospective re-adjudication. No meanings, sound values, plant identifications, glyph merges or causal mechanisms are assigned.']
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');preserved,final=verify_sources();assert all(sha(p)==h for p,h in frozen['hashes'].items())
 save('VERIFICATION.json',dict(status='PASS',freeze_preceded_new_scoring=True,eligible_events=len(events),independent_p_oracles=audit,effects_CIs_support_exactly_replayed=True,independent_Holm_verified=True,BQ2_unqualified_and_not_rescored=True,v31_preserved_files=len(preserved['hashes']),qualification_artifact_hashes_unchanged=True,artifact_hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='VERIFICATION.json'}))
 print(json.dumps({k:dict(status=v['status'],holm_p=v['holm_p']) for k,v in results.items()},indent=2))
if __name__=='__main__':{'freeze':freeze,'run':execute}[sys.argv[1]]()
