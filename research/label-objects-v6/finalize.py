"""Write honest phase statuses and a hash seal of the infrastructure."""
from common import *
from collections import Counter,defaultdict
from datetime import datetime,timezone

def main():
    if load(ROOT/'PROTOCOL.json').get('version')=='v6.1':
        raise RuntimeError('v6.1 is sealed; finalize.py cannot restore the old incomplete-protocol checkpoint')
    if (ROOT/'OUTCOME-JOIN.json').exists() or any(read_csv(ROOT/f'RATER-{r}.csv') for r in ['A','B','C']):
        raise RuntimeError('Cannot reset statuses after actual ratings or a join')
    if any(r['status']=='REGISTERED' for r in load(ROOT/'LABEL-REGISTRATION.json')['rows']):
        raise RuntimeError('Cannot reset statuses after accepted geometry')
    source_manifest=load(ROOT/'SOURCE-MANIFEST.json')
    inventory=read_csv(ROOT/'LABEL-INVENTORY.csv');features=read_csv(ROOT/'FEATURES.csv')
    template_pending=True
    protocol=dict(version='v6',date='2026-10-24',tier='INFRASTRUCTURE_BUILT; CLAIM_SPEC_PARTIALLY_FROZEN',
        claim_freeze_status='INCOMPLETE',outcome_join='CLOSED',
        unresolved=['Existing word-shape template classes have not been recovered or defined.',
                    'T2 independent trial unit, one-to-many match selection and primary reading require a frozen amendment.',
                    'Whole-drawing geometry and complete text masks are required for T2.',
                    'Broader earlier-pair exposure audit is required before calling non-nine pairs fresh.'],
        units=dict(source_sha256=sha(EVT),reserved=sorted(RESERVED),included_units_sha256=sha(ROOT/'UNIT-TYPE-AUDIT.csv'),
            policy='Source descriptions, not object votes. Include labels, titles, captions, letters and radial inscriptions; exclude paragraph and continuous circular text. No length-based selection.',
            H_F='Separate alternate readings, never independent object observations.',
            multiline='One row per EVT line locus, as requested. Shared physical-label grouping must be recorded during registration and addressed before treating lines as independent trials.'),
        registration=dict(independent=True,accepted_geometry=0,automatic_proposals='Never accepted by counts alone',
            prior_v4='Paragraph geometry is not reused as label geometry',unregistered='Drop/list; no invented coordinates'),
        agreement=dict(threshold=.60,full=CLASSES,collapse=COLLAPSE,
            collapse_unmapped=['ROSETTE','ANIMAL','OTHER','NONE','UNCLEAR'],
            collapsed_denominator='Only loci where both A and B votes map to the four named groups; list exclusions and full-class confusion matrix.',
            selection='Use full classes if full kappa passes; otherwise collapse if collapsed kappa passes; both fail means NOT_RELIABLE. Undefined kappa never passes.',
            provenance='Different model families or human raters; fresh plain API call with manual + one composite image only; no tools or agent harness.'),
        features=dict(length='Concatenated readable EVA code-character count; no phonetic length claim',
            opener_order=['qo','q','ch','sh','ot','ok','d','other'],q_and_qo_merged=True,
            ending_order=['aiin','ain','iin','in','eedy','edy','eey','ey','dy','y','ol','or','ar','al','am','om','m','n','r','l','other'],
            glyph='EVA code-character presence; grouped physical glyph identification not assumed',ngrams='Binary unbounded-vocabulary code-character 1–3-grams',
            multiword='Concatenate readable tokens, retain word count in ledger. Mixed uncertain loci excluded from T1.',
            template='UNRESOLVED; no replacement smuggled into the feature set'),
        T1=dict(min_labels_per_class=30,min_physical_folios_per_class=6,min_classes=2,
            class_policy='Only independently attached object classes meeting both support rules; NONE/UNCLEAR/OTHER and excluded collapse outside target set.',
            cv='5 outer and 4 inner folds, reduced only to number of physical folios. Hash-sorted physical folios, all sides and foldout panels together; identical folds for observed and null.',
            model='L2 logistic regression; C grid [.01,.1,1,10]; smaller C wins ties; inner pooled held-out log-loss; no class weighting.',
            preprocessing='Training-only dictionary vocabulary and sparse standardisation inside every inner and outer fit.',
            baseline='Leave-one-label-out true page class mix with add-half smoothing; peer outcomes from held-out page explicitly allowed only for this conditional baseline. Never feed peer outcomes to model.',
            primary='Pooled outer log-loss gain relative to page prior',secondary='Balanced accuracy, descriptive; no alternate route to a pass',
            permutations=5000,null='Within each exact page/panel, permute classes; rerun all nested tuning and outer fitting.',
            p='(1 + null gains >= observed gain)/(5001); one-sided; Holm over estimable sections in each reading.',
            headline='Positive gain and Holm p <= .05 in H and F in the same section',
            failures='Missing training classes or nonconvergence => not estimable, never silently omit a fold'),
        T2=dict(matching='All exact word matches; edit distance <=1 only when both words have >=5 EVA code characters; readings separate; all candidate page pairs listed before image judgment.',
            previous_nine='Nine prior word records expand to eleven supplied page pairs; exact source retained.',
            distractor='Unmatched herbal plant from same scribe; writing fully masked on all three images; randomised left/right.',
            test='Share of matched choices among fresh decided trials; one-sided exact binomial p; minimum 15 decided pairs.',
            unresolved='Many candidate pairs reuse words/pages/plants; cannot pretend those are independent binomial trials. Schedule must be frozen before judgment.',
            claim_limit='A similarity preference supports visual correspondence under this choice design; it does not establish identical species or word meaning.'),
        controls=dict(status='NOT_RUN',T1=['Feature-planted positive','Page-only confound null','Section-only null'],T2=['Shuffled word matches'],
            power_gate='At least .80; repeated simulations of the complete corrected pipeline required, not an authored fixture.',
            false_positive_gate='At most .05; preserve all trials, fixed seeds, counts and intervals before manuscript scoring'),
        claims=dict(T1='Conditional form/object-class association; compatible with referential information, not proof of naming or a unique semantic mechanism.',
            T2='Visual similarity over same-scribe distractors under a frozen pair design; identity and linguistic meaning need additional evidence.',
            fail='A qualified, adequately powered failure concerns this feature/class resolution; it does not reject all naming-label systems. Not estimable is not negative.'))
    save(ROOT/'PROTOCOL.json',protocol)
    save(ROOT/'AGREEMENT.json',dict(status='NOT_RUN',reason='No independent A/B ratings or accepted label geometry',join_open=False))
    panels=defaultdict(list)
    meta={r['task_id']:r for r in inventory}
    for r in features: panels[(r['reading'],meta[r['task_id']]['section'])].append(r)
    coverage=[]
    for (reading,section),rr in sorted(panels.items()):
        usable=[r for r in rr if r['eligible']=='True']
        coverage.append(dict(reading=reading,section=section,rows=len(rr),fully_readable_rows=len(usable),
            folios=len({meta[r['task_id']]['folio'] for r in usable}),
            support_upper_bound='IMPOSSIBLE_TWO_CLASSES_30_EACH' if len(usable)<60 else 'OBJECT_RATINGS_REQUIRED'))
    save(ROOT/'T1.json',dict(status='NOT_RUN_NO_OBJECT_JOIN',coverage_upper_bounds=coverage,
        pharma_HF_headline='NOT_ESTIMABLE_FROM_THIS_SOURCE',
        reason='Pharma/Recipes F has two rows, one fully readable; fewer than 60 required for two classes. No alternate reading substituted.'))
    pairs=read_csv(ROOT/'T2-MATCHED-PAIRS.csv')
    save(ROOT/'T2.json',dict(status='MATCH_CANDIDATES_BUILT_JUDGMENTS_NOT_RUN',candidates=len(pairs),
        counts={str(k):v for k,v in Counter((r['reading'],r['match'],r['previously_seen']) for r in pairs).items()},
        fresh_decided_trials=0,p_value=None,claim='NOT_ESTIMABLE_YET_NO_JUDGMENTS',
        warning='Candidate matches are not independent trials or anchors. Freshness currently means absent from nine-word ledger only.'))
    save(ROOT/'QUALIFICATION.json',dict(status='SCIENTIFIC_CONTROLS_NOT_RUN',scientific_gate_passed=False,
        power=None,false_positive_rate=None,engineering_verification='See VERIFICATION.json; not power qualification'))
    report=f'''# Label-to-object dataset v6 — infrastructure checkpoint

Built on 24 October 2026. Object ratings, label geometry and claim tests remain uncompleted.

The source ledger contains **{len(inventory):,} candidate EVT loci** across all available readings.
H/F have **{len(features):,} separate reading rows**. There are {source_manifest['image_ready_loci']} loci on
currently available exact single-page canvases; other loci retain explicit panel-registration exclusions.
Every unit type was audited, including lowercase pharma codes and letters/titles/radial inscriptions.
Reserved Virgo, Libra, Scorpio and Sagittarius folios are excluded. No word was assigned a meaning.

**The planned pharma H/F headline cannot be estimated from this EVT.** Pharma is named
“Recipes” in Davis metadata: H has 230 rows; F has only 2, of which 1 is fully readable.
The threshold requires at least two classes of 30 labels each. This source-level upper bound
does not depend on object judgments. Other sections still need registration and actual ratings.

T2 has {len(pairs):,} mechanically matched candidate records, including repeated words and pages.
These are not {len(pairs):,} independent pairs. The earlier nine records contain eleven supplied
source/target page pairs; these are flagged. Other earlier visual/text exposures remain to be
audited before a primary fresh subset can be certified. No image-choice trials have been run.

## What is built

* Source-linked locus inventory, unit decisions, counts per section/type/reading, and H/F feature ledger.
* Header-only registrar input with native canvas hashes; no object descriptions or transcription bodies.
* Geometry validator, fixed-context crop/thumbnail packet builder, independent-vote validator,
  pre-adjudication kappa gate and guarded join.
* Nested physical-folio CV engine, training-only feature preprocessing, peer-page baseline,
  within-page permutation pipeline and per-reading Holm correction. No manuscript run.
* Exact candidate-match list and preserved prior-nine evidence.
* Multilingual historical comparator search with access/coverage limits in HISTORICAL-COMPARATORS.md.

## What remains

The claim freeze is deliberately marked INCOMPLETE: the existing word-shape class definition
has not been found; T2 needs a frozen independent-trial schedule and primary-reading convention.
The historical catalogues do not supply a word-shape class inventory. No new feature has been
passed off as an existing one.

All labels are currently UNREGISTERED. The v4 geometry is paragraph geometry and is not reused.
An independent registrar must inspect source images and submit writing boxes; unavailable
foldout panels require exact native-canvas registration. Two independent raters then receive
only anonymous image stimuli plus MANUAL.md. Models must use fresh plain API calls, without
tools or agent harness; different families or a human are required. No compatible two-family
rater setup was established in this session. Empty RATER files are templates, not observations.

The four-way collapse retains only paired votes within CELESTIAL/PLANT/VESSEL/FIGURE-WATER;
ROSETTE/ANIMAL/OTHER/NONE/UNCLEAR remain in the full-class gate. Exclusions are reported.
Actual scientific controls, including repeated power and confound-null qualification, are outstanding.
T2 also needs independently attached drawing crops and complete writing masks before rating.

## Reproduce and continue

`python build.py` rebuilds source infrastructure only while no outcome join exists.
`python verify.py` verifies engineering and boundaries; it is not a power study.
`python workflow.py geometry independent-registration.json` validates supplied blind geometry.
`python workflow.py packet` creates image-only rater stimuli for accepted boxes.
`python workflow.py agreement` computes actual independent A/B agreement.
`python workflow.py join` and `python t1.py` refuse incomplete claim freezes and missing gates.

The current FREEZE.json is an infrastructure hash seal. It is **not** a completed claim preregistration.
Do not flip the status flag manually. Resolve definitions, implement/qualify the remaining protocol,
then issue a versioned claim freeze before joining any object outcomes. Previous research folders
and v4 owners are untouched.

A T1 association can support referential information but does not identify meanings or exclude
all scribal/register explanations. A T2 similarity preference does not establish species identity.
An unestimable result is not evidence against naming labels.
'''
    (ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    files=['PROTOCOL.json','MANUAL.md','UNIT-TYPE-AUDIT.csv','TYPE-COUNTS.csv','LABEL-INVENTORY.csv','FEATURES.csv',
           'T2-MATCHED-PAIRS.csv','PREVIOUS-NINE.json','common.py','build.py','workflow.py','t1.py','finalize.py','verify.py','SPEC-original.md','HISTORICAL-COMPARATORS.md']
    save(ROOT/'FREEZE.json',dict(tier='INFRASTRUCTURE_ONLY_NOT_A_COMPLETED_CLAIM_FREEZE',
        frozen_utc=datetime.now(timezone.utc).isoformat(),hashes={p:sha(ROOT/p) for p in files},outcome_joined=False))
    print(json.dumps(dict(status=protocol['tier'],coverage=coverage,candidates=len(pairs))))

if __name__=='__main__': main()
