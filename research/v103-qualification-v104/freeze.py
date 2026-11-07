from pathlib import Path
import datetime,hashlib,json
R=Path(__file__).resolve().parent;P=R.parent
save=lambda n,x:(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'FREEZE.json').exists(),'Never overwrite a frozen attempt'
old=json.loads((P/'opening-order-audit-v75/RESULTS.json').read_text(encoding='utf-8'))
panels=[]
for idx,want in zip((0,1,12,13),(4005,4371,9730,9316)):
    x=next(x for x in old['panels'] if x['panel_index']==idx)
    z={k:x[k] for k in ('panel_index','section','hand','variety','format','reading','labels','class_pairs')}
    assert z['class_pairs']==want and len(z['labels'])*(len(z['labels'])-1)//2==want
    panels.append(z)
save('FAMILY.json',panels)
fixtures=[
 dict(name='variable',rows=[['aa','shedy','ol','qokedy','or','aa']]),
 dict(name='repeat_literal',rows=[['aa','shedy','ol','qokedy','ol','aa']]),
 dict(name='two_lines_barriers',rows=[['aa','shedy','ol','qokedy','or','aa',None,'shaa'],['qokaa',None,'aa','shedy','ol','qokedy','ol','aa']]),
 dict(name='overlap_bodies',rows=[['aa','shaa','saiin','shbb','qokaa','ol','aa']]),
 dict(name='one_path',rows=[['aa','shedy','qokedy','or']]),
 dict(name='unknown_short',rows=[[None,None],[],['shedy'],['qokedy','ol'],[None,'shaa',None,'qokaa',None]]),
 dict(name='positive32',rows=[['aa','shedy','ol','qokedy','or','aa'] for _ in range(32)])]
save('FIXTURES.json',fixtures)
plan=dict(scope='Stage1 full-family qualification controls ONLY; not actual-layout power or scoring.',
 matrices=[[[1,1,1],[1,1,1],[1,1,1]],[[1,2,1],[1,2,1],[1,2,1]],[[4,1,1],[1,4,1],[1,1,4]],[[1,4,1],[1,1,4],[4,1,1]],[[1,1,4],[4,1,1],[1,4,1]]],
 matrix_rule='Each row normalized exactly to a rational probability. Positive initial class probabilities and uniform within-class literal assignment; within-fiber weights must be constant.',
 nuisance_regimes=['independent_words','page_specific','line_span_specific','hand_specific'],
 regime_selection='Independent: matrix1 for all spans. Page: (span_index//2)%5. Line/span: span_index%5. Hand: matrix2 for hand2, matrix3 for hand3 (zero-based matrix indexing). These are authored nuisance architectures, not empirical hand mechanisms.',
 sample_draws=4096,calibration_draws=4096,diagnostic_trials=200,
 seed_rule='SHA256 first8bytes big endian of v104/controls/{purpose}/{panel_index}/{fixture_or_regime}. No reruns or seed replacement.',
 family='All frozen 4005/4371/9730/9316 pairs; both signs via exact two-sided tails, both middle rules; correction28 unchanged. Identical complete signatures may share computation, columns never removed.',
 path_oracle='All 3^n class strings for n1..7; compare exact path sets to direct enumeration AND v98 paths. Fisher-Yates exhaustive choices for [0,1],[0,1,2],[0,1,2,3],[0,0,1].',
 full_orbit_fixtures='Every fixture except positive32: exhaustively enumerate distinct literal orders within span constraints, product across spans; 20000 whole-layout oracle cap, no truncation.',
 cdf_audit='Before any random draw freeze the sum over ALL family columns of (exact support size-1) for every panel/view/fixture plus (literal orbit size-1) per small fixture/panel. Hoeffding union bound alpha.001: absoluteCDFerror<=sqrt(log(2*M/.001)/(2*4096)). Identical queries may share computation but remain counted in M. Constants have no CDF interior support point.',
 size_audit='Exact complete-orbit full-family minP CDF rank at .05/28,.05,.1,.5,1, and matrix-weighted conditional family null rejection<=.05/28. MonteCarlo plus-one exhaustive B2 rank/tie check. Global conditional-null scope only, not arbitrary strong FWER.',
 positive_gate='Fixed authored positive32 source order is a planted positive, never manuscript. Target sign must be forward above exact null mean and full corrected target p<=.05 in every panel/view. This is deterministic engineering signal detection, not claimed >=80/90 power.',
 diagnostics=['position_weights','repeated_template','literal_junction'],
 diagnostic_definition='On the 12-order variable-span orbit, positive weights respectively 4^(I(slot1 starts sh)+I(slot3 starts qok)),16^(count exact shedy,ol,qokedy triple),4^(count shedy->ol plus ol->qokedy literal adjacent boundaries). Normalize exactly. Draw 32 independent spans/trial,200trials. Use SAME positive32 null calibration bank. Preserve empirical family/target flags and exact target rejection mass from histogram convolution. No nominal-size gate: these violate the uniform conditional null.',
 required_gates=['family identity','path and multiplicity oracle','all-family direct-score and exact marginal identities','endpoint multiset edge and barrier invariants','exact family rank and nuisance size','all planned sampler CDF checks','positive fixture full corrected target detection'],
 failure_rule='Finish all independently evaluable control cases. Any required failure blocks full Stage1 PASS; never change matrices, thresholds, families or seeds. Store exceptions as failures. No Stage2 or original source score entrypoint in this runner.',
 pending='Even Stage1 PASS does NOT qualify actual-layout power. The v103 Stage2 power gates and all three new banks remain required. v98 FAIL and unrun banks preserved.')
save('CONTROL-PLAN.json',plan)
files=['core.py','run.py','freeze.py','verify.py','report.py','FAMILY.json','FIXTURES.json','CONTROL-PLAN.json']
refs=['retrospective-order-design-v103/PROTOCOL.md','retrospective-order-design-v103/engine.py','retrospective-order-design-v103/EXPOSURE-CLARIFICATION.md','transition-maxT-qual-v98/engine.py','transition-maxT-qual-v98/QUALIFICATION.json']
save('FREEZE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),local_sha256={n:sha(R/n) for n in files},historical_sha256={n:sha(P/n) for n in refs},original_family_source_sha256=sha(P/'opening-order-audit-v75/RESULTS.json'),status='FROZEN BEFORE CONTROLS; scoring closed'))
print('Full control runner, exact fixtures, nuisance matrices, seeds and gates frozen.')
