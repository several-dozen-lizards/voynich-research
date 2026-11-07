"""Save the requested spec, decisions and an honest pre-freeze development report."""
from pathlib import Path
import json
import shutil
from core import save, sha

ROOT = Path(__file__).resolve().parent
ATTACHMENT = Path(r'C:\Users\lewis\.codex\attachments\11e63142-0bea-481c-9865-1ad75f213561\Pasted text.txt')

def main():
    if (ROOT/'FREEZE.json').exists():
        raise RuntimeError('do not rewrite a frozen experiment')
    if (ROOT/'held-definition-development/RESULTS.json').exists():
        from finalize_definition_development import main as finalize
        return finalize()
    if (ROOT/'source-cut-2/RESULTS.json').exists():
        from finalize_source_cut2 import main as finalize
        return finalize()
    if (ROOT/'TRANSFER-DIAGNOSTIC-RESULTS.json').exists():
        from finalize_transfer import main as finalize
        return finalize()
    if (ROOT/'SOURCE-COVERAGE-RESULTS.json').exists():
        from finalize_sources import main as finalize
        return finalize()
    if (ROOT/'QUALIFICATION-PLAN-v2.json').exists():
        from finalize_development import main as finalize
        return finalize()
    if not (ROOT/'SPEC-v5.md').exists():
        shutil.copyfile(ATTACHMENT, ROOT/'SPEC-v5.md')
    elif sha(ATTACHMENT) != sha(ROOT/'SPEC-v5.md'):
        raise RuntimeError('original spec changed')
    verification = json.loads((ROOT/'VERIFICATION.json').read_text(encoding='utf-8'))
    cells = json.loads((ROOT/'CELLS.json').read_text(encoding='utf-8'))
    mappings = json.loads((ROOT/'MAPPING-PREFLIGHT.json').read_text(encoding='utf-8'))
    blockers = [
        dict(id='H3', status='NEEDS_ORIGINAL_METHOD', detail='ending_lm v2 exact estimator, noise correction, ending inventory and ±48-sign construction not recovered in earlier chats or local artifacts. No replacement estimator has been substituted.'),
        dict(id='MAPPING', status='IMPLEMENTATION_DESIGN_REQUIRED', detail='Single-EVA-character, 95%-class, injective rank-map draft abstains in every G1–G4 × panel fixture. Need a declared glyph/group inventory, position-class rule, overflow and unseen-unit policy before freezing. This is not inability to mimic basics.'),
        dict(id='SOURCES', status='INCOMPLETE', detail='Latin/German Bible sources located; not medical/diplomatic. Italian/Czech/Occitan sources and source license/provenance manifests missing. No real heavily abbreviated Latin control yet.'),
        dict(id='G2_G3', status='ENGINEERING_FIXTURES_ONLY', detail='Illustrative suspension/contraction and symbol rules run; historical diplomatic/Cappelli rule inventories and probabilities not qualified.'),
        dict(id='G5', status='PUBLISHED_SOURCE_PINNED_NOT_INTEGRATED', detail='40 published source/license/docs files pinned and hash-verified. Java/java compiler/Maven not found on PATH. Python copy-modify fixture is explicitly a surrogate and cannot eliminate Timm–Schinner.'),
        dict(id='G6', status='PROTOTYPE_ONLY', detail='Three-column tables with explicit coupled grille offsets run. Published mechanism fidelity, table priors and movement law still need qualification.'),
        dict(id='H1_H2_H5', status='NEW_SCALE_APPROVED_DEFINITIONS_PENDING', detail='User selected MH log OR and recomputed targets. Old 1.16–1.32 is RD strengthening, not an OR target. Freeze zero-cell/no-support policy, opener/context selection, availability and section heterogeneity estimator before recomputation.'),
        dict(id='H4', status='OVERLAPS_S_FIT', detail='H4 is a function of glyph position shares already fitted. Keep as a declared diagnostic; do not call it independent held-out evidence.'),
        dict(id='H6', status='DEFINITION_TO_FREEZE', detail='Normalized edit-distance convention, page boundaries, eligible candidate windows, equal-size random baselines, pair restriction and vector-to-one-failure rule need explicit definitions. Zero-support cases must be missing, not zero.'),
        dict(id='H7_H8', status='LEGACY_METHOD_MISMATCH', detail='Original p/r result recovered: matched remainders, 12/12 versus9/45, not generic p frequency. v65 is line-first template surprise and explicitly excludes paragraph-start inference. Exact method underlying paragraph15.5% vs3.4% not recovered.'),
        dict(id='RECOVERY', status='NOT_RUN', detail='Correct-family survival alone does not establish discrimination. G2/G3/G4 contain G1-like boundaries; G3 contains G2 at p=0. Preserve expected non-identifiability rather than require arbitrary wrong-family elimination. Freeze number of pseudo-manuscripts, parameter-recovery tolerance and off-diagonal gate.'),
        dict(id='CLAIM_EXECUTION', status='NOT_READY', detail='No qualified full generators, frozen prior ranges/tolerance schedule, simulation budget, PPC multicomponent rule or recovery matrix yet. No manuscript ABC/PPC/RF or elimination was run.'),
    ]
    protocol = dict(version='v5-sandbox-1', tier='sandbox', status='DRAFT_NOT_FROZEN', local_date='2026-10-24',
                    original_spec_sha256=sha(ROOT/'SPEC-v5.md'),
                    user_decisions=[dict(decision='Use log odds ratio; recompute targets', scope='H1/H2; historical RD target retained only as provenance'),
                                    dict(decision='Check previous conversations for H3', outcome='Checked earlier Voynich chats/attachments/artifacts; exact ending_lm v2 not recovered')],
                    families=['G1','G2','G3','G4','G5','G6'],
                    population='P-unit H/F rows, exact Currier A/B × Davis scribe1..5; separate cells',
                    reserved_folios=['f72v1','f72v2','f73r','f73v'],
                    source_manifest='DATA-MANIFEST.json',
                    s_fit_implementation=dict(word_length='1..30 plus overflow', unigram='registered EVA characters',
                                              bigram_entropy='word-internal, no word-boundary transitions',
                                              growth='type/token ratio at .1,.25,.5,.75,1 of readable ordered words',
                                              words_per_line='original token slots including unknowns; 0..40 plus overflow',
                                              glyph_positions='initial/medial/final/free-singleton; conditional shares per glyph'),
                    s_fit_scale='whole-physical-page bootstrap; zero SD mismatch=>infinite distance, no arbitrary epsilon',
                    claim_particle_minimum=2000, abc_engine='bounded uniform-prior ABC-SMC; weighted mixture proposals; generation seeds/distances/ESS retained',
                    abc_rf='Pudlo-style OOB allocation-error regressor estimates selected-model probability. Vote fractions descriptive, not all-family posterior probabilities.',
                    proposed_elimination='At least two failed statistic families among H1,H2,H3,H6; require same Currier×scribe cell to agree across H/F. Missing/unsupported is indeterminate. No live decisions exist.',
                    blockers=blockers)
    save(ROOT/'PROTOCOL.json', protocol)
    save(ROOT/'MAPPING.json', dict(status='DRAFT_NOT_CLAIM_READY', seed=51024, draft_position_threshold=.95,
                                 draft_target_units='literal EVA characters only', draft_collision_policy='abstain, no many-to-one merge',
                                 preflight='MAPPING-PREFLIGHT.json', abstentions=len(mappings),
                                 final_group_inventory=None, note='No generator output was scored on H1–H8.'))
    save(ROOT/'PRIORS-DRAFT.json', dict(status='NOT_FROZEN_NOT_FOR_INFERENCE',
        G1=dict(language_candidates=['Latin','Italian','German','Czech','Occitan'], free_tuning_parameters=[]),
        G2=dict(abbreviation_probability=[0.,1.], rule_inventory='PENDING historical source'),
        G3=dict(abbreviation_probability=[0.,1.], symbol_probability=[0.,1.], context_variants=[False,True], symbol_inventory='PENDING historical source'),
        G4=dict(max_expansion=[1,2,3], null_probability=[0.,.2], position_variants=[False,True]),
        G5=dict(published_properties='SOURCES/timm-schinner/source/src/main/resources/conf.properties', prior_ranges='PENDING integration, not surrogate parameters'),
        G6=dict(table_inventory='PENDING', grille_offsets='PENDING', movement_prior='PENDING')))
    history = dict(status='SEARCHED_NOT_RECOVERED', method='read_thread plus targeted local session/attachment/artifact search',
                   query='ending_lm / noise-relative / ending freedom / ±48 signs',
                   chats=[dict(id='01a15c3d-56da-7f02-bc15-2522dc396abd', title='Analyze Voynich manuscript'),
                          dict(id='01a160c1-c17b-7c13-9255-3817d6dc0147', title='Resume Voynich analysis handoff'),
                          dict(id='01a160c2-56f0-7303-b3bf-ed8594c6ec40', title='Review Voynich handoff', scope='selected recent turns plus artifact search'),
                          dict(id='01a169fe-ddd8-7c01-90be-0e6bf7932177', title='Explore Voynich word categories'),
                          dict(id='01a16ff2-0158-7b60-a624-317903618103', title='Summarize Voynich research attempts'),
                          dict(id='6ad916c3-6fc4-83ea-9095-cb461c47d508', title='Voynich Decipherments Explained')],
                   found=['original p/r matched-remainder line-position result and source owner', 'v65 line-first template method; not the stated paragraph-first anomaly method'],
                   not_found='exact H3 ending_lm v2, and exact H8 paragraph anomaly estimator',
                   limitation='Does not prove absence from every earlier conversation or external Claude project.')
    save(ROOT/'HISTORY-SEARCH.json', history)
    pending = ['FREEZE.json','ABC-POSTERIORS/','PPC.csv','ELIMINATION.json','RECOVERY-CONFUSION.json','ABC-RF.json']
    save(ROOT/'STATUS.json', dict(status='SANDBOX_IMPLEMENTED_CLAIM_NOT_READY', complete=False,
                                 completed=['source loader/exclusion hashes','S_fit summaries/bootstrap','six reproducible mechanism fixtures','rank-map capacity preflight','ABC-SMC core','ABC-RF core','engineering controls','published G5 source archive','history search'],
                                 pending_claim_deliverables=pending, blockers=blockers,
                                 next_step='Recover exact H3/H8 source methods; complete historical source/generator/mapping qualification before freeze.'))
    cell_table = '\n'.join(f"| {c['currier']} | {c['scribe']} | {c['reading']} | {c['pages']} | {c['lines']} | {c['known_words']} | {c['unknown_slots']} |" for c in cells)
    blocker_text = '\n\n'.join(f"- **{b['id']} — {b['status']}:** {b['detail']}" for b in blockers)
    report = f'''SANDBOX ONLY — NO MODEL ELIMINATION OR SURVIVAL RESULT. CLAIM RUN INCOMPLETE.

# Voynich system types v5: development report

Recorded 24 October 2026, America/New_York. The original request is preserved byte-for-byte in `SPEC-v5.md`. This is a development cut, not the final simulate-and-compare experiment.

## What exists and was verified

The EVT and Davis metadata match their expected source hashes. Reserved Virgo/Libra/Scorpio/Sagittarius folios (`f72v1`, `f72v2`, `f73r`, `f73v`) are excluded before tokenization. Original unknown slots remain barriers. H/F alternate readings and Currier A/B stay in separate cells. `DATA-MANIFEST.json` hashes the exclusion policy and all retained rows.

`core.py` implements the five S_fit blocks and whole-page bootstrap scaling. `S-FIT-TARGETS.json` contains those basic targets only, not H1–H8 outcomes. Zero-variance bootstrap dimensions cannot be rescued with a small denominator: a mismatch gives infinite distance.

`GENERATORS/` contains reproducible runnable mechanisms for all six families. These are development fixtures: G2/G3 use unsourced illustrative rules, G5 is a copy-modify surrogate, G6 is a coupled three-column grille prototype. G1/G4 mechanics run but still lack a full source and mapping specification. No fixture is a historically qualified family implementation. Six 800-word fixtures, raw source-unit marks and G5 genealogy are saved under `SANDBOX-SAMPLES/`.

The published Timm–Schinner source is pinned at commit `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`; all **40** downloaded source/license/documentation files match their manifest hashes. They have not been executed or silently replaced by the surrogate. The published code has page/position source selection, several mutation operations, follow constraints and suggestion logic. Source: [Timm–Schinner repository](https://github.com/TorstenTimm/SelfCitationTextgenerator).

`abc_smc.py` implements bounded uniform-prior ABC-SMC with proper importance weights, recorded seeds, distances and ESS. A planted scalar location and an independent density calculation verify the sampler mechanics. That is not the six-family recovery gate. No manuscript fitting was performed. Required particle count remains at least 2,000 per qualified family/cell.

`abc_rf.py` implements classification plus OOB allocation-error regression for a selected-model probability approximation. It explicitly distinguishes forest votes from posterior probabilities and does not invent probabilities for all other models. Source: [Pudlo et al., Reliable ABC model choice via random forests](https://arxiv.org/abs/1406.6288).

**{verification['engineering_tests']} engineering tests passed.** Tests cover tokenizer/barriers, exclusion before tokenization, source-hash mismatch, all generators' reproducibility, separate abbreviation units, verbose expansion, causal/windowed parent receipts, mapping injection/abstention, hand-calculated fit statistics, zero bootstrap variance, freeze absence/incompleteness/tampering, ABC weights/recovery and RF behavior. The initial development test-file indentation failure was repaired before this successful run; no scientific result was produced by the failed invocation.

`held.py` refuses H1–H8 scoring without a valid complete `FREEZE.json` and matching source-owner hashes; its actual statistic dispatch is still unimplemented. No FREEZE has been created. Neither generator nor manuscript H1–H8 values were computed in this cut.

## Population retained

| Currier | Scribe | Reading | Pages | Lines | Known words | Unknown slots |
|---|---|---|---:|---:|---:|---:|
{cell_table}

P-locus and metadata eligibility are explicit draft choices. Other formats and missing/ambiguous Currier/scribe assignments are excluded and counted in the data manifest. No missing cell is interpreted as a failed mechanism.

## User decision and recovered history

Re selected **log odds ratio; recompute targets** for H1/H2. The historical 1.16–1.32 availability-strengthening interval is from a risk-difference estimand and is not reused as a log-OR target.

At Re's request, earlier Voynich conversations, attachments and saved experiment owners were searched. The original p/r matched-remainder layout result was recovered: 12/12 eligible line-start forms used p, versus9/45 elsewhere; that is not the share of all line-start words containing p. The exact `ending_lm v2` method was not recovered. The saved v65 template method concerns line-first words and explicitly does not establish the paragraph-first H8 method or its quoted15.5%/3.4% targets. `HISTORY-SEARCH.json` records scope and limits; this is not a claim that the missing work never existed.

## Mapping preflight

The strict single-character rank-map draft produced **{len(mappings)}/{len(mappings)} capacity abstentions** across four source-unit fixtures × ten manuscript panels. This shows the draft mapping cannot represent those source inventories within the selected position classes. It does not eliminate G1–G4, establish a fit failure, or demonstrate anything about the manuscript mechanism. The spec permits EVA groups, but their inventory, segmentation, class rules, reuse/overflow and unseen-unit behavior must be made explicit. No many-to-one fallback was inserted.

## Work remaining before a claim freeze

{blocker_text}

These gaps are not inferential failures. The code and evidence are reviewable, but this experiment has not reached the requested claim tier. `PROTOCOL.json`, `MAPPING.json` and `PRIORS-DRAFT.json` are explicitly drafts. The following requested result artifacts are absent because their computations have not run: {', '.join('`'+p+'`' for p in pending)}.

The finite family/parameter/source choices define what could be excluded. Even a qualified exclusion would concern that implementation and prior support, not every conceivable natural-language, abbreviation, cipher or copying mechanism. A survivor would remain compatible with the measured features, not a decipherment.

## Reproduce this sandbox cut

From the project folder:

```powershell
python system-types-v5/sandbox.py --bootstrap 100
python system-types-v5/prepare.py
```

No live services, other research branches or reserved-folio content were modified. `VERIFICATION.json` records the environment, engineering checks and code hashes; `DELIVERY-HASHES.json` inventories this development cut without calling it a claim freeze.
'''
    (ROOT/'REPORT.md').write_text(report, encoding='utf-8')
    paths = [ROOT/name for name in ('core.py','held.py','abc_smc.py','abc_rf.py','sandbox.py','prepare.py','test_sandbox.py','GENERATORS/__init__.py','fetch_published.py')]
    verification['code_hashes'] = {str(p.relative_to(ROOT)):sha(p) for p in paths}
    verification['draft_protocol_sha256'] = sha(ROOT/'PROTOCOL.json')
    verification['report_sha256'] = sha(ROOT/'REPORT.md')
    save(ROOT/'VERIFICATION.json', verification)
    deliverables = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'DELIVERY-HASHES.json']
    save(ROOT/'DELIVERY-HASHES.json', {str(p.relative_to(ROOT)):sha(p) for p in deliverables})
    print(json.dumps(dict(status='SANDBOX_IMPLEMENTED_CLAIM_NOT_READY', files_hashed=len(deliverables), held_scored=False, report=str(ROOT/'REPORT.md'))))

if __name__ == '__main__':
    main()
