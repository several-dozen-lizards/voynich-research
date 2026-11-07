"""Define recovery/discrimination and summarize supplied labels; never computes H1–H8."""
from pathlib import Path
import json,math
from core import save,sha

ROOT=Path(__file__).resolve().parent
FAMILIES=('G1','G2','G3','G4','G5','G6')

class RecoveryLocked(RuntimeError):pass

def require_recovery_release(root=ROOT):
    root=Path(root)
    protocol=json.loads((root/'RECOVERY-PROTOCOL.json').read_text())
    if protocol['H3']['status']!='RESOLVED_WITH_ORIGINAL_METHOD':
        raise RecoveryLocked('H3 unresolved: full recovery cannot run or silently omit it')
    from held import require_freeze
    return require_freeze(root)

def summarize_labels(records,expected_trials=100):
    """Decision-label checks only; inputs must come from a separately released pipeline."""
    if len(records)!=expected_trials:raise ValueError('incomplete recovery cell')
    if len({r['trial'] for r in records})!=expected_trials:raise ValueError('duplicate trial')
    if len({r['true_family'] for r in records})!=1:raise ValueError('one true-family cell required')
    allowed={'SURVIVES','ELIMINATED','CANNOT_MIMIC_BASICS','NOT_ESTIMABLE','BUDGET_EXHAUSTED'}
    survived=0;discriminated=0;incomplete=0
    for record in records:
        truth=record['true_family'];decisions=record['decisions']
        if truth not in FAMILIES or record['regime'] not in ('interior','boundary'):raise ValueError('invalid truth/regime')
        if set(decisions)!=set(FAMILIES) or not set(decisions.values())<=allowed:raise ValueError('missing or invalid family decision')
        if any(v in ('NOT_ESTIMABLE','BUDGET_EXHAUSTED') for v in decisions.values()):incomplete+=1
        survived+=decisions[truth]=='SURVIVES'
        if record['regime']=='interior':
            rejected=sum(decisions[f] in ('ELIMINATED','CANNOT_MIMIC_BASICS') for f in FAMILIES if f!=truth)
            discriminated+=rejected>=3 and decisions[truth]=='SURVIVES'
    interior=sum(r['regime']=='interior' for r in records)
    n=len(records);phat=survived/n;z=1.95996398454;den=1+z*z/n
    center=(phat+z*z/(2*n))/den;half=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    return dict(trials=len(records),correct_family_survived=survived,correct_family_survival_rate=phat,correct_family_survival_wilson95=[center-half,center+half],
                interior_trials=interior,interior_discriminated=discriminated,incomplete_trials=incomplete,
                survival_gate=survived/len(records)>=.8,
                discrimination_gate=interior>0 and discriminated/interior>=.8,
                interpretation_allowed=incomplete==0 and survived/len(records)>=.8 and interior>0 and discriminated/interior>=.8)

def build():
    assert not (ROOT/'FREEZE.json').exists()
    protocol=dict(version='recovery-discrimination-v1',tier='DESIGN_ONLY_NOT_CLAIM_FROZEN',execution='LOCKED',
        H3=dict(status='UNRESOLVED',policy='Original ending_lm v2 must be recovered and exactly specified; no replacement, no omission, no zero-filled result, no reduced-H run.'),
        release_requirements=['All H1–H8 adapters and component names defined and hashed, including original H3.','Complete claim FREEZE.json hashes code, sources, priors, mapping, layout, budgets, target/statistic adapters and this protocol.','Source-support, unknown-unit, layout and negative-control policies settled before any held scores.'],
        scope='Qualify this finite implementation/prior/source set at supported sizes; no mechanism-wide historical exclusion.',
        geometry=dict(primary='Existing ten Currier×Davis-scribe×reading cells; exact retained page/line/unknown-mask geometry; reserved zodiac never loaded.',
            recovery_units='100 independent pseudo-manuscripts per true family per reading-cell; six families ×ten cells =6000 datasets.',
            H_F='Separate fits and confusion matrices. H/F are alternative coverage/templates, not independent manuscript replications. Both reading-specific gates must pass for a Currier×scribe headline; do not multiply p-values or pretend separately generated pseudo-texts are paired transcriptions.',
            real_known_text='Additional primary real abbreviated-Latin control at its own five-page native size, not padded/repeated to match larger manuscript cells.15th-century scholastic and earlier medical sources are separate sensitivity strata.',
            source_length='UNKNOWN-AND-LENGTH-POLICY.json governs: development-only fitting/generation; original slot counts include unknowns; one contiguous same-work run, no gaps, source wrapping, padding, partition pooling or selective size reduction. Primary source-backed calls use source_contract.produce_from_development. Insufficient material is SOURCE_TOO_SHORT/UNSUPPORTED_AT_SIZE before generation, never family rejection.',
            layout='One declared conditioning contract for all families before freeze; preserve published G5 native character-count generation. Match target sample size by stopping/censoring at declared boundaries, never forcing outcomes. Do not include an exactly conditioned line statistic again as independent evidence.'),
        pseudo_truth=dict(regimes={'interior':80,'boundary':20},
            parameters='Draw from frozen priors with stratified quantiles; interior numeric probabilities in[.1,.9] of their permitted range, categorical factors balanced; all source/codebook nuisance draws recorded. Boundary20 exercise literal shared submodels, not expected identifications.',
            nested_cases=['G2 abbreviation probability0 reduces to G1 source representation.','G3 symbol probability0 reduces to G2.','G4 no nulls/no position variants overlaps G1 up to codebook representation.'],
            labels='Truth parameters/source IDs remain in sealed receipt, never predictor features or fitting inputs. Arbitrary code-unit names, mapping IDs, file names, seeds and family names must not enter summary vectors.',
            mapping='Rebuild the candidate mapping and bootstrap standardization against each pseudo-target exactly as for the manuscript. Never provide the true mapping/key to the inference code. Treat deterministic tie/label conventions as nuisance; relabeling negative controls must prevent artificial family recognition.'),
        fitting=dict(method='ABC-SMC on S_fit only for every candidate family, including the true family',
            particles_minimum=2000,final_weight_ESS_minimum=1000,
            particle_escalation='Allowed2000->4000->8000 only to meet final ESS, with unchanged priors/tolerances; record all stages and failures.',
            distance='Euclidean on registered S_fit blocks, standardized using each pseudo-target whole-page bootstrap SD; zero-SD mismatch remains infinity.',
            tolerance_calibration='Using S_fit only before claim freeze: final epsilon from the95th percentile of predeclared whole-page bootstrap standardized distances; fixed SMC schedule4×,2×,1× epsilon. Preserve full calibration draw table; do not choose on H1–H8 or classification performance.',
            simulator_calls_maximum_per_fit=250000,
            budget='Maximum250000 simulator calls per family/cell/trial, including all SMC stages/ESS escalation; checkpoint all attempts. Set wall-time caps from a separate S_fit-only runtime benchmark before release. Budget exhaustion or mapping failure must not be relabelled cannot mimic basics. A completed predeclared prior-predictive search may report CANNOT_MIMIC_BASICS only with its fit-distance evidence and explicitly bounded search scope, not proof about all possible parameters.',
            minimum_final_accepted_particles_all_recovery_cells=72000000,
            note='This is an expensive full protocol, not a job launched by this design. Three2000-particle generations alone imply at least216million accepted particles before proposal rejections.'),
        predictive=dict(draws_minimum=2000,ESS_minimum_per_vector_envelope_half=400,weighting='Use ABC importance weights; do not treat weighted accepted particles as equally likely.',
            scalar_rule='Weighted central95% posterior predictive interval, endpoints inclusive; outside gives one failed H-family.',
            vector_rule='H3/H6 vector components jointly count as at most one failed H-family. Predeclare component names. Deterministically split predictive draws into location/scale and calibration halves. Weighted median and MAD from first half; max absolute standardized component departure calibrated at weighted95th percentile on second half gives a simultaneous envelope. Zero spread: exact equality contributes0, otherwise infinity. Unsupported components invalidate that H-family; never drop components post hoc.',
            intervals='Report every component percentile and interval as descriptive alongside the one-family flag. One H3 context subcomponent is not interchangeable with the whole H3 test. An infinite calibrated vector threshold or inadequate predictive ESS is NOT_ESTIMABLE, not an automatic pass.',
            elimination='At least two failed H-families among H1,H2,H3,H6. Missing/unsupported makes overall elimination NOT_ESTIMABLE if it could change the decision; cannot count as passing. H4/H5/H7/H8 diagnostics do not add votes.',
            H2='Availability-strengthening targets must be recomputed on approved log-OR scale; legacy RD ratios are not numeric log-OR targets.'),
        gates=dict(correct_family_survival='At least80/100 per true-family×reading-cell, with95% binomial intervals reported. This keeps the stated80% empirical gate; uncertainty is not hidden.',
            interior_discrimination='In at least64/80 interior trials, true family survives and at least3 of5 wrong families are rejected. Report basic-fit rejection separately from H-specific elimination.',
            pairwise='Every family pair gets its own false-exclusion and survival/co-survival table. Do not infer that two families are distinguishable merely because the global majority gate passes.',
            boundaries='No correct-label selection requirement where families overlap. Shared mechanisms should co-survive. Report empirical equivalence sets and false exclusion of each shared representation.',
            parameter_recovery='For every preregistered identifiable numeric parameter: true value inside90% interval in>=80% of eligible interior trials; median absolute posterior-median error<=.20 prior-range; median interval width<=.60 prior-range. Seeds, offsets and label-permuted keys are nuisance, not identifiable targets. Categorical identifiable parameters: true category posterior mass>=.8 in>=80% eligible interior trials. Declare every exemption before scoring; retain failures.',
            incomplete='Every scheduled record must have a terminal auditable status. Mapping/unknown/source-size support or computation failures are not negative manuscript evidence. Unsupported recovery cells cannot qualify corresponding manuscript claims.',
            failure_terminal='Any required survival/discrimination/control gate fails => report PIPELINE_CANNOT_DISCRIMINATE for that scope, do not interpret manuscript model probabilities or elimination. No threshold repair in this cut.'),
        controls=['Identity/no-op G1→G2p0→G3p0 and G4 boundary representations.','Unit-label permutation and family-label permutation negatives; chance classification is expected under exchangeable/null labels.','Duplicate/near-duplicate source works stay in one partition; repeated seed/text leakage audit.','Real abbreviated-Latin reserve never fits abbreviation rates or rule vocabulary; all unseen-sign abstentions retained.','Source genre/date/orthography contrasts reported separately; no Italian literary or Gascon legal result relabelled as a medical-genre test.','Known text controls also pass representation/unknown-unit gates before attempting survival scoring.'],
        random_forest=dict(role='Descriptive only after all required discrimination gates pass; not used to change elimination thresholds.',
            reference_table='At least5000 independent prior-predictive records per family per supported geometry, disjoint truth/test seeds and source partitions. Group duplicate latent texts/source blocks in folds. No held-statistic reference table may be generated before claim freeze.',
            probability='Pudlo-style selected-model probability from out-of-bag allocation-error regression; forest vote fractions are descriptive. Do not invent probabilities for all families.'),
        deliverables=['RECOVERY-TRUTH.jsonl','RECOVERY-FITS.jsonl','RECOVERY-CONFUSION.json','RECOVERY-PARAMETERS.csv','RECOVERY-BOUNDARIES.json','REAL-LATIN-CONTROL.json','RECOVERY-FAILURES.json','RECOVERY-VERIFICATION.json'],
        source_contract=dict(policy='UNKNOWN-AND-LENGTH-POLICY.json',policy_sha256=sha(ROOT/'UNKNOWN-AND-LENGTH-POLICY.json') if (ROOT/'UNKNOWN-AND-LENGTH-POLICY.json').exists() else None,
            entrypoint='source_contract.produce_from_development',
            transfer='Development-only frozen codebooks; native transcription unknowns keep their registered mask. Newly unmappable originally readable words remain None barriers and invalidate full-transfer qualification. No reserve reranking, accent/digit completion or mark merging.',
            prior_diagnostics='Whole-reserve self-maps and earlier exposed Macer mapping trials are diagnostic-only; never initialize primary fitting or claim historically untouched reserves.',
            scope='Seven current development-language/reading-cell combinations lack full original-slot support. They do not enter a complete candidate comparison at that size until an independent source cut or separately frozen smaller comparison exists.'),
        current_state=dict(source_control='Real G2 survival NOT_RUN. Transfer/length policies settled; source gaps remain honest support limits.',recovery_executed=False,H1_H8_computed=False,claim_freeze_created=False),
        uncertainty='Binomial intervals quantify seed/draw variation conditional on the fixed corpus/geometry; they are not independent-language or independent-manuscript population intervals.')
    save(ROOT/'RECOVERY-PROTOCOL.json',protocol)
    save(ROOT/'RECOVERY-DESIGN-SEAL.json',dict(tier='design only; not FREEZE',protocol_sha256=sha(ROOT/'RECOVERY-PROTOCOL.json'),code_sha256=sha(Path(__file__)),execution='LOCKED'))
    print('Recovery/discrimination protocol defined and hashed; execution remains locked.')

if __name__=='__main__':build()
