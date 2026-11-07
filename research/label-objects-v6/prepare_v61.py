from common import *
from datetime import datetime,timezone
import shutil

def main():
    archive=ROOT/'history/infrastructure-v6.0'
    if archive.exists():raise RuntimeError('Existing checkpoint: do not repeat amendment')
    archive.mkdir(parents=True)
    # Preserve the entire earlier delivered checkpoint, excluding this new code and native external images.
    for p in list(ROOT.iterdir()):
        if p.is_file() and p.name not in ['prepare_v61.py','batch_cv.py']:
            shutil.copy2(p,archive/p.name)
    save(archive/'CHECKPOINT-HASHES.json',{p.name:sha(p) for p in archive.iterdir() if p.is_file()})
    p=load(ROOT/'PROTOCOL.json');p.update(version='v6.1',date='2026-10-24',tier='CLAIM_PROTOCOL_FROZEN_BEFORE_GEOMETRY_RATINGS_JOIN',claim_freeze_status='FROZEN',unresolved=[])
    p['authority']='User: resolve remaining protocol details, qualify controls, work toward independent registration and ratings; H/F separate and pharma limit preserved.'
    p['features']['template']='New operational scaffold: longest grouped EVA segmentation from v70; k/t/p/f and benched variants -> G; ch/sh -> B; maximal e and i runs -> E and I; other symbols literal. Feature is one-hot full scaffold. Not a recovered historical class inventory.'
    p['features']['glyph']='Both literal EVA code-character and v70 longest-group presence; operational proxies, not asserted physical glyph boundaries.'
    p['units']['multiline']='Registrar records a physical_label_id. A multi-line physical label is excluded from T1 primary until all rows and reading boundaries can be consolidated under a versioned rule; never count its lines as independent labels.'
    p['T1']['class_policy']='All full-set classes except NONE and UNCLEAR are eligible when they meet support; OTHER is retained as specified full-set category. Four-way outside-domain votes excluded and reported.'
    p['T1']['support_failures']='Support assessed before all fits; per-class minimum 30 complete physical labels and 6 physical folios. Invalid folds and fit failures preserved as not estimable.'
    p['T2'].pop('unresolved',None)
    p['T2'].update(primary_reading='H primary; F separate sensitivity, no pooling or substitution. Any future F primary claim requires separate prospective amendment.',
        freshness='Fresh means no earlier source/target image-pair exposure found in specified paired-image ledgers, not previously unseen text. Exclude all source-page × target-page combinations shown in legacy pilot choices plus nine-record pairs; retain previously seen strata.',
        independent_unit='One single-word label, one unique EVA word, one distinct registered pharma drawing, one herbal plant/distractor pair per trial; none reused within a reading. Shared-folio dependence is reported and checked by a folio-cluster sensitivity; no binomial result alone establishes identity.',
        schedule='Hash-sort all exact candidates before edit1 candidates (seed v61-T2). Greedily retain nonreused pharma physical-label/word/drawing and herbal page IDs. Draw one same-scribe distractor with no exact/edit1 match to the source word; both target/distractor pages cannot be reused. No replacement if a frozen eligible trial abstains. Registration/mask failure is recorded and excludes before ratings.',
        matching_length='Both strings >=5 EVA code characters for edit1. Single fully readable word labels only for primary; multiword titles and letter columns remain infrastructure but are excluded from T2 primary.',
        choice='Two independent plain-API raters. Primary trial decided only when both choose the same herbal drawing; discordant or neither/unclear => abstain. No C adjudication of T2 primary. Report each rater separately.',
        randomisation='Hash bit of trial ID assigns matched plant left/right. Choice files contain no keys or text. Shuffled-match schedule uses independent hash seed, same scribe/exposure/nonreuse rules.',
        masked_images='All writing on each full drawing crop must have an independently verified exhaustive mask; masks and crop geometry frozen before choices. If uncertain, trial excluded.',
        gate='At least 15 fresh consensus-decided H trials; exact one-sided binomial p<=.05; shuffled-match image control must not pass; report folio-cluster uncertainty. Otherwise not estimable or failed control.')
    p['registration'].update(blind_process='Fresh plain API call with only native image, neutral registrar manual and header/order locators. No category manual, source word bodies, feature files, matches, section/scribe metadata or analysis.',
        acceptance='Two independent source-only visual passes, no counts-only acceptance. First proposes boxes and physical_label_id; second sees image and proposed boxes/locators and can reject. Accept only explicit unique locator identity and adequate IoU; preserve both raw outputs.',
        overlap_gate='Second reviewer must confirm full writing coverage and exact locus identity; proposed/review bbox IoU>=.70, no overlapping duplicate writing boxes. A disagreement remains UNREGISTERED.',
        pilot='Complete all label loci on the first two image-ready pages in deterministic hash order, never select by object class, words or anticipated effect. Engineering pilot is not study-wide agreement.')
    p['controls']=dict(status='PLAN_FROZEN_NOT_RUN',trials_per_regime=100,permutations=5000,
        seeds='protocol seed 610241; exact per-bank/per-trial seeds in CONTROL-PLAN.json',
        T1=['Two-class and three-class positives at 144 and 180 rows; 12 physical folios; 12% within-page label swaps preserve class margins.',
            'Two-/three-class page-only classes on 12/18 physical folios with six folios per class: within-page orbit is a singleton; exact p=1.',
            'Two synthetic sections with different fixed page class mixes and no lexical association; independent within-page null assignments; Holm across both sections per reading.'],
        reuse='Each 5000-assignment conditional null bank is evaluated through every nested fit and reused only for identical X, folds, class set and page margins. Each control trial has independently generated observed outcomes. Bank-conditional rates and uncertainty are explicit.',
        acceleration='Finite-prototype sufficient-count Newton solver; same scaled feature geometry, L2 objective, C grid, nested tuning and CV. Numerical parity against original sklearn engine must pass before qualification.',
        gates=dict(power='H/F joint pass rate >=.80, separately for two and three classes',false_positive='Per-reading section-Holm familywise rate and H/F headline rate <=.05; page singleton null must always p=1',
                   parity='All checked gain differences <=2e-5; exact selected C except inner gaps <=2e-5; fit probabilities <=2e-5'),
        intervals='Wilson 95% intervals; gates apply to point estimates as original spec, intervals always reported. Shared-bank simulation limitation explicit.',
        T2='Exact binomial type-I calibration against known chance, plus actual shuffled-match image control before T2 inference. Statistical calibration cannot replace image controls.')
    p['pharma_coverage_limit']=dict(H_rows=230,F_rows=2,F_fully_readable=1,headline='NOT_ESTIMABLE_FROM_CURRENT_EVT',no_substitution=True)
    save(ROOT/'PROTOCOL.json',p)
    features=read_csv(ROOT/'FEATURES.csv')
    for r in features:
        if r['eligible']=='True':
            word=r['eva'].replace('.','');r['features']=json.dumps(feature_dict(word),sort_keys=True);r['word_shape_template_class']=shape(word)
        r['template_status']='V6_1_OPERATIONAL_SCAFFOLD_NOT_HISTORICAL_TEMPLATE'
    write_csv(ROOT/'FEATURES.csv',list(features[0]),features)
    old=load(PROJECT/'image-context-rater-v1/research-only/legacy-pilot-frozen-key.json')
    exposed={(t['source_page'],target) for t in old['trials'] for target in t.get('choices',{}).values()}
    nine=load(ROOT/'PREVIOUS-NINE.json')['records']
    exposed|={(r['source_page'],target) for r in nine for target in r['supplied_targets']}
    save(ROOT/'T2-EXPOSURE-EXCLUSIONS.json',dict(scope='All combinations displayed in prior pilot choices, plus prior-nine supplied pairs',
        source_sha256=sha(PROJECT/'image-context-rater-v1/research-only/legacy-pilot-frozen-key.json'),pairs=[dict(pharma_page=a,herbal_page=b) for a,b in sorted(exposed)],
        limits='Defines fresh association judgments, not historically unseen manuscript words; remaining known paired image ledgers must be included before schedule release.'))
    save(ROOT/'CONTROL-PLAN.json',dict(trials=100,permutations=5000,base_seed=610241,bank_seeds={
        f'{K}-{reading}-{regime}':610241+K*10000+ri*1000+gi*100 for K in [2,3] for ri,reading in enumerate(['H','F']) for gi,regime in enumerate(['balanced','section'])},
        observed_seeds='610241 + K*100000 + regime_index*10000 + trial*10 + section; H/F use the same physical class outcomes, different spelling prototypes',
        H_prototypes=['qokal','shody','otaiin'],F_prototypes=['qokar','shedy','okaiin'],
        trials_status='FROZEN_BEFORE_RUN',timing=datetime.now(timezone.utc).isoformat()))
    print('v6.1 protocol and features prepared; claim seal follows code qualification setup, before any geometry/ratings/join.')

if __name__=='__main__':main()
