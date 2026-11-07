from common import *
from qualify import interval
from datetime import datetime,timezone
from scipy.stats import binom
import shutil

summary=load(ROOT/'controls/SUMMARY.json')
# A reporting correction: exact singleton-orbit proofs are four fixtures, not
# 100 independent simulations per fixture. Preserve the generated output intact.
if not (ROOT/'controls/SUMMARY-generated.json').exists():
    shutil.copy2(ROOT/'controls/SUMMARY.json',ROOT/'controls/SUMMARY-generated.json')
for r in summary['results']:
    if r['regime']=='page_only':
        r['n']=1;r['evidence_unit']='One exact singleton-orbit proof; not 100 independent observations'
save(ROOT/'controls/SUMMARY.json',summary)
save(ROOT/'controls/REPORTING-CORRECTION.json',dict(field='page_only.n',generated_value=100,corrected_value=1,
    scope='Reporting only. These controls proved a singleton within-page permutation orbit; no 100 independent page datasets were generated.',
    original_sha256=sha(ROOT/'controls/SUMMARY-generated.json'),decisions_changed=False,overall_still='FAIL'))
save(ROOT/'controls/NULL-RATE-DIAGNOSIS.json',dict(
    H_two_class=dict(flags=6,n=100,wilson95=interval(6,100),binomial_reference_probability_at_least_this_many=float(binom.sf(5,100,.05))),
    F_two_class=dict(flags=7,n=100,wilson95=interval(7,100),binomial_reference_probability_at_least_this_many=float(binom.sf(6,100,.05))),
    conclusion='Frozen empirical gate failed. These finite counts do not establish true inflation; intervals include .05. No seed, threshold, trial count or feature rule was retuned after outcomes.',
    qualification='Remains FAIL. A further replication must have its own prospective plan and preserve this result.',
    exchangeability_argument='For fixed features/folds/page margins, observed and uniformly permuted labels give exchangeable deterministic CV scores. The add-one rank p value is marginally super-uniform; Holm controls the family under that null. This argument does not establish exchangeability for real manuscript object attachments.',
    caveat='Shared conditional banks induce dependence across simulated trials. Reference binomial calculations are descriptive, not a separate gate or proof that the engine is calibrated.'))
save(ROOT/'QUALIFICATION.json',dict(status='FAIL_T1_FALSE_POSITIVE_CONTROL',scientific_gate_passed=False,
    protocol_sha256=sha(ROOT/'PROTOCOL.json'),control_plan_sha256=sha(ROOT/'CONTROL-PLAN.json'),
    parity=load(ROOT/'controls/PARITY.json'),T1=summary,
    permutations_per_bank=5000,conditional_banks=8,trial_records=1200,
    T2_statistical_calibration=load(ROOT/'controls/T2-BINOMIAL-CALIBRATION.json')['status'],
    T2_shuffled_match_image_control='NOT_RUN_NO_ACCEPTED_DRAWING_GEOMETRY_OR_TEXT_MASKS',
    registration_pilots=dict(original_accepted=0,repaired_accepted=0,physical_loci_attempted=12),
    rater_interface=load(ROOT/'rater-interface-control/RESULTS.json'),
    important_limit='Positive power is conditional on strong synthetic finite-prototype signals at realistic counts; not a guarantee for weak or historical-script effects.'))
reg=load(ROOT/'LABEL-REGISTRATION.json');attempted={r['task_id'] for r in load(ROOT/'registration-pilot-v2/AUDIT.json')['rows']}
for row in reg['rows']:
    if row['task_id'] in attempted:
        row.update(status='UNREGISTERED_FAILED_TWO_PASS_PILOTS',pilot_receipts=['registration-pilot/AUDIT.json','registration-pilot-v2/AUDIT.json'])
save(ROOT/'LABEL-REGISTRATION.json',reg)
write_csv(ROOT/'DROPPED-LABELS.csv',['task_id','locus','page','reason'],[dict(task_id=r['task_id'],locus=r['locus'],page=r['page'],reason=r['status']) for r in reg['rows']])
t1=load(ROOT/'T1.json');t1.update(status='NOT_RUN_QUALIFICATION_FAILED_AND_NO_REGISTERED_OBJECTS',
    reason='Two-class section-only null exceeded the frozen <=5% empirical gate. No accepted label geometry or independent A/B object ratings.',
    pharma_HF_headline='NOT_ESTIMABLE_FROM_THIS_SOURCE');save(ROOT/'T1.json',t1)
t2=load(ROOT/'T2.json');t2.update(status='TEXT_SCHEDULE_FROZEN_IMAGE_TRIALS_NOT_READY',
    scheduled=load(ROOT/'T2-SCHEDULE-FREEZE.json')['scheduled'],fresh_decided_trials=0,p_value=None,
    statistical_calibration='PASS_EXACT_BINOMIAL_ONLY',image_control='NOT_RUN',
    reason='37 H text-only candidates, 0 F scheduled; distinct drawings, exhaustive writing masks and qualified independent raters remain required.');save(ROOT/'T2.json',t2)
save(ROOT/'AGREEMENT.json',dict(status='NOT_RUN_NO_ACCEPTED_LABEL_GEOMETRY_OR_REAL_AB_VOTES',join_open=False,
    synthetic_interface='Separate engineering fixtures: GLM classes 2/2; Moondream 0/2 and one invalid class code. No real votes imputed.'))
rows=summary['results']
table='| Control | Classes | H flags | F flags | H/F joint | Gate |\n|---|---:|---:|---:|---:|---|\n'
for r in rows:
    if r['regime']=='page_only':continue
    table+=f"| {r['regime']} | {r['classes']} | {r['H_flags']}/100 | {r['F_flags']}/100 | {r['HF_joint_flags']}/100 | {'PASS' if r['passed'] else 'FAIL'} |\n"
report='''# Label-to-object v6.1 — frozen protocol, failed qualification, registration pilots

24 October 2026. **No manuscript label–object claim test or outcome join has run.**
The protocol details are resolved and sealed, but the scientific and registration gates do not pass.

## What changed

The original delivered checkpoint is retained under history/infrastructure-v6.0.
PROTOCOL.json and FREEZE.json now record v6.1, sealed before label geometry acceptance,
object ratings, joining and the control suite. The original word-shape class reference
could not be recovered. v6.1 explicitly introduces a deterministic operational scaffold
from the project's v70 grouped-EVA segmentation: gallows/bench classes and e/i-run
structure, without assigning vowel, consonant, sound or meaning. Both code-character
and grouped-EVA presence remain explicit operational proxies. H and F stay separate.

T2 now has a fixed H primary / F sensitivity convention, single-word eligibility,
conservative earlier-source-page exclusions, exact-before-edit1 selection, same-scribe
unmatched distractors, nonreuse rules, deterministic side randomisation, consensus
choices, abstention handling, mask requirements and folio-dependence reporting.
The text-only frozen schedule contains **37 H candidates and 0 F candidates**.
Candidates are not decided trials, identified plants or verified independent drawings.

## Scientific controls

'''+table+'''
All eight conditional banks use **5,000 permutations**, each evaluated through the
complete nested CV fitting and tuning pipeline. The fast finite-prototype solver
passed numerical comparison with the original scikit-learn engine for binary and
multinomial models in H and F. Gains, fitted probabilities and selected C values
matched the frozen tolerances. Every bank and trial outcome is retained.

Both positive regimes pass the >=.80 point-estimate power gate: joint H/F detection
100/100, Wilson 95% interval about [.963, 1]. These are strong planted prototype
effects at 144/180 rows across 12 physical folios, not power for subtle real effects.

The two-class section-only null fails the <=.05 empirical false-positive gate:
H 6/100, F 7/100, joint 6/100. Finite-sample intervals include .05; this does not
establish true inflation. It still fails the frozen gate. No threshold, seed, feature
rule or trial count was changed to obtain a pass. QUALIFICATION.json remains FAIL.

Four page-only fixtures have exact singleton within-page permutation orbits, hence
p=1 and no possible flags. They are four exact proofs, not 400 independent simulations.
A generated reporting count said 100 per fixture; REPORTING-CORRECTION.json corrects
that to one proof each, preserving SUMMARY-generated.json and all original decisions.

Exact binomial statistical calibration passed for every n from 15 through 80.
That does not replace T2's actual shuffled-match image control, which has not run.
Shared-bank conditional simulation, finite prototype vocabularies and limited nuisance
generators remain explicit limits. A further calibration replication needs a new
prospective plan; it must not erase this failed qualification.

## Independent registration and ratings

The frozen image-ready hash order selected f42v (1 locus) and f83r (11 loci).
The first pilot used a source-only GLM proposal and fresh source-only review; it
failed schema, identity and geometry checks. Nonblind analyst QA vetoed obvious
paragraph-block substitutions and supplied no replacement coordinates.

The repaired pilot supplied complete EVT HEADER structure, neutral positions and
normalised corner coordinates to two unanchored stateless calls. Neither pass saw
word bodies, categories, analyses or the other pass's answer. **Zero of 12 loci met
the two-pass acceptance rules.** Both pilots and every raw request/response remain.
The two registrar calls are from one trained family; process isolation is not
independent-family validation or human verification.

An isolated CPU-only LLaVA test failed memory allocation. The smaller local Moondream
route ran, but failed both authored object-class fixtures (0/2; one nonconforming
class code). It is rejected as B for this workflow. GLM returned correct classes on
both fixtures, which is only a tiny interface check, not manuscript reliability.
No synthetic votes entered the real RATER files. No actual manuscript A/B/C ratings,
agreement, label geometry or object assignments are claimed.

The main resident Ollama server received read-only inventory/status requests;
generation was on separate CPU-only servers, all closed afterward. No resident
model was deliberately loaded/unloaded or reconfigured. Concurrent server state
is retained in snapshots rather than represented as fully controlled.

The external manuscript calls ran only after explicit user approval for api.z.ai,
following automatic review's initial rejection. No rejected payload was bypassed.

## Concrete continuation materials

* human-registration-only.zip: clean source-only native images, complete header
  locators and a local rectangle tool for two independent human registrars.
  It includes no transcription bodies, object manual, ratings or analysis.
* human-registration/index.html: the same tool unpacked. Save/export actual
  observations; no data are transmitted. No human observations exist yet.
* T2-TEXT-SCHEDULE.csv and T2-SCHEDULE-FREEZE.json: prospective candidates, still
  blocked on independently identified drawings and exhaustive writing masks.
* controls/: frozen banks, original-engine parity, all 1,200 trial-section-reading
  records, exact calibration, failures and the reporting correction.

The historical multilingual comparator search is retained in HISTORICAL-COMPARATORS.md.
No catalogue excerpt was promoted into a qualified historical template corpus.

## Coverage and remaining boundary

The inventory still has **1,062 candidate EVT loci** and **1,076 H/F reading rows**.
The pharma/Recipes source limit remains **230 H rows versus 2 F rows, only 1 fully
readable F row**. The required pharma H/F headline cannot be estimated from this
EVT; no alternative reading has been substituted. Other sections still require
actual reliable registration, object votes and successful scientific qualification.

Object joining and manuscript scoring remain guarded. A reliable independent
registrar and B rater are not currently established. The human source-only packet
is ready; supplying real independent observations or qualifying a new vision route
is the next practical registration step. Further statistical work must investigate
the preserved null-control failure under a new prospective plan before scoring.

Run `python verify_v61.py` for the current reproducibility audit. `build.py`,
`finalize.py` and the original `verify.py` describe the preserved v6.0 checkpoint;
they are not v6.1 continuation commands. Do not rerun the freeze scripts to rewrite
timing, or overwrite failed API receipts, controls or study outputs.
'''
(ROOT/'REPORT.md').write_text(report,encoding='utf-8')
save(ROOT/'STATUS.json',dict(version='v6.1',protocol='FROZEN',T1_qualification='FAIL',accepted_label_geometry=0,
    registration_attempted_loci=12,registration_pilots=2,real_raters=0,outcome_join='CLOSED',manuscript_inference='NOT_RUN',
    T2_H_text_candidates=37,T2_F_text_candidates=0,pharma_HF_limit_preserved=True,human_packet_ready=True,utc=datetime.now(timezone.utc).isoformat()))
print('v6.1 results reconciled; qualification FAIL, zero accepted geometry, no inference')
