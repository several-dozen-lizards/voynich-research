"""Publish current sandbox status without creating a claim freeze."""
from pathlib import Path
import json,platform
import numpy,scipy,sklearn
from core import save,sha,canonical_hash

ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/'FREEZE.json').exists(),'held scoring must remain locked'
    q=json.loads((ROOT/'GENERATOR-QUALIFICATION.json').read_text())
    plan=json.loads((ROOT/'QUALIFICATION-PLAN-v3.json').read_text())
    assert q['plan_sha256']==sha(ROOT/'QUALIFICATION-PLAN-v3.json')
    assert all(sha(ROOT/n)==h for n,h in plan['files'].items()),'qualified code or source changed'
    assert q['status']=='SANDBOX_MECHANISMS_PASS' and q['mapping_passes']==1600 and q['mapping_failures']==0
    inventories=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text())
    trials=json.loads((ROOT/'GROUP-MAPPING-QUALIFICATION.json').read_text())
    old=json.loads((ROOT/'development-history/sandbox-1/PROTOCOL.json').read_text())
    unresolved=[b for b in old['blockers'] if b['id'] not in ('MAPPING','G2_G3','G5','G6','SOURCES')]
    for b in unresolved:
        if b['id']=='CLAIM_EXECUTION':b['detail']='Sandbox mechanics and mapping qualify. Exact held methods, all source-language coverage, layout/source-wrapping policy, priors/tolerances, real abbreviated-Latin control and full model recovery/discrimination remain before a claim freeze.'
    unresolved.extend([
        dict(id='SOURCES',status='PARTIAL_COVERAGE',detail='Edited Macer Latin herbal archived with revision/hash/attribution; Latin/German Bible sources also available. Italian/Czech/Occitan source coverage and real diplomatic abbreviated-Latin control still pending.'),
        dict(id='GENERATOR_HISTORICAL_SCOPE',status='LIMITED',detail='G2 uses sourced abbreviation rule types with synthetic probabilities. G3 default et symbol is attested; after-vowel variants are synthetic. G6 is a specified Rugg-style mechanism, not a unique historical table or human movement reconstruction.'),
        dict(id='LAYOUT',status='TO_FREEZE',detail='G1–G4/G6 controls use supplied word-count layouts; published G5 retains native character-count layout. Fair conditioning, seed-line handling and source wrapping/length must be declared before S_fit inference.')])
    old.update(version='v5-sandbox-3',status='SANDBOX_MECHANISMS_QUALIFIED_NOT_FROZEN',blockers=unresolved,
               qualification_plan='QUALIFICATION-PLAN-v3.json',candidate_entrypoint='registry.produce',
               G5='unmodified pinned published code; Python copy-modify surrogate retained as development control only',
               mapping='observed within-word1..3 EVA atoms, greedy longest-match operational atoms, rank within95%-position class; deterministic SHA256 ties; injective; no invented overflow units; retain unit boundaries',
               mapping_information_budget='Target overlapping within-word group counts and position classes enter the mapping. This is an explicit mapping input beyond the original single-character S_fit summary; no cross-word, line-start, ending-LM or held statistics enter.',
               candidate_overlap='Allowing multi-atom spellings for G1 makes its representation overlap G4. G4 adds positional code variants/nulls; boundary settings are not distinguishable families.',
               user_decisions=old['user_decisions']+[dict(decision='Continue mapping and generator qualification; leave H3 unresolved and held scoring locked',scope='current continuation')])
    save(ROOT/'PROTOCOL.json',old)
    mapping=dict(status='SANDBOX_QUALIFIED_NOT_CLAIM_FROZEN',version='EVA-group-rank-v1',seed=51024,
        atoms=dict(longest_match=['cth','ckh','cph','cfh','ch','sh'],fallback='one lowercase EVA character'),
        inventory='All observed overlapping within-word spans of1..3 atoms, separately per Currier×scribe×reading; never cross a word or unknown slot',
        position='whole-word span free; otherwise initial/final/medial by span endpoints; one class per written span when >=95% use, else free',
        rank='source unit frequency rank and target group frequency rank within class; tie SHA256(seed:unit)',
        widths='G4 maps each source-letter code unit to1..max_expansion EVA atoms, max_expansion<=3; default3. Exact narrow capacities can abstain.',
        overflow='raise error; never merge units, invent unattested target groups, widen the span, or borrow another class',
        unseen='raise error; mapping is re-estimated by the same registered procedure for each independent draw',
        boundaries='Mapped source-unit groups retained alongside concatenated EVA; flat strings are not asserted uniquely decodable. Longest-match reparsing may fuse across latent unit boundaries.',
        inventories='EVA-GROUP-INVENTORIES.json',inventory_sha256=canonical_hash(inventories),
        qualification=dict(trials=1600,passed=1600,failed=0,plan='QUALIFICATION-PLAN-v3.json'),
        first_failed_draft='development-history/sandbox-1/MAPPING-PREFLIGHT.json',
        failed_exact_width_cipher='development-history/group-qualification-1/QUALIFICATION-FAILURES.json')
    save(ROOT/'MAPPING.json',mapping)
    save(ROOT/'MAPPING-PREFLIGHT.json',[t for t in trials if t['seed']==61000 and t['layout']==0])
    priors=json.loads((ROOT/'development-history/sandbox-1/PRIORS-DRAFT.json').read_text())
    priors['G2']['rule_inventory']='RULE-SOURCES.json; sourced subset, probabilities synthetic'
    priors['G3']['symbol_inventory']='TIRONIAN_ET default only; synthetic context variants; broad domain inventory pending'
    priors['G4']['expansion_width']='assigned by deterministic target group map up to max_expansion; not an independently preassigned width per letter'
    priors['G5']['implementation']='registry.produce -> unmodified published Java; canFollow curveline/none only; corpus-derived built-in VMS follow tables rejected'
    priors['G6']=dict(table_rows=[40],table_blocks=[8],grille_offsets=[0,1,-1],row_steps=[-2,-1,0,1,2],note='qualified development settings; final priors still not frozen')
    save(ROOT/'PRIORS-DRAFT.json',priors)
    status=dict(status='SANDBOX_MECHANISMS_QUALIFIED_CLAIM_LOCKED',complete=False,mapping_qualified=True,
        generator_qualification_scope='200 known-source/mechanism trials,1600 EVA-group maps,5 published-G5 repeat pairs; no full recovery/confusion or held-out scoring',
        H3='UNRESOLVED',claim_freeze=False,blockers=unresolved,
        next_step='Resolve remaining held-method definitions and source/layout coverage; then freeze the complete claim protocol before any H1–H8 computation.',
        pending_claim_deliverables=['FREEZE.json','ABC-POSTERIORS/','PPC.csv','ELIMINATION.json','RECOVERY-CONFUSION.json','ABC-RF.json'])
    save(ROOT/'STATUS.json',status)
    save(ROOT/'TEST-RESULTS.json',dict(command='python -m unittest test_sandbox test_registry -v',tests=19,errors=0,failures=0,exit_code=0,
        scope='Engineering and production-entrypoint checks; separate from generator qualification and full claim recovery'))
    save(ROOT/'RETAINED-FAILURES.json',dict(single_character_maps=dict(failures=40,path='development-history/sandbox-1/MAPPING-PREFLIGHT.json'),
        exact_width_G4_maps=dict(failures=400,path='development-history/group-qualification-1/QUALIFICATION-FAILURES.json'),
        fixture_failure='development-history/group-qualification-1/DEVELOPMENT-FAILURE.json',
        download_failures=['Adoptium metadata API HTTP403; official GitHub fallback verified','first in-memory release download timed out; streamed retry succeeded'],
        failed_results_used_for_claim=False))
    report='''SANDBOX MECHANICS QUALIFIED — CLAIM SCORING LOCKED; H3 UNRESOLVED.

# Voynich system types v5: mapping and generator qualification

Recorded 24 October 2026, America/New_York. This continuation implements explicit EVA groups and qualifies the generator mechanics. It does not fit or eliminate manuscript production families.

## Results

- **19/19 engineering and candidate-entrypoint tests pass.**
- **200/200 known-source and mechanism trials pass**, across20 seeds and two layouts for G1–G4/G6.
- **1,600/1,600 EVA group maps pass**: four families ×20 seeds ×two layouts ×10 separate Currier/scribe/H-F cells. Every tested map is injective, all rendered groups are registered, and inverse recovery works with retained unit boundaries.
- **Published G5 passes five repeat pairs**: seeds19/23/31/43/59 each produce identical output on repetition and different output across seeds. All100 native lines parse. Its initial seed line is excluded from the fit-only summaries.
- **No H1–H8 computation ran. No claim FREEZE exists. H3 remains unresolved.**

`GENERATOR-QUALIFICATION.json`, `GROUP-MAPPING-QUALIFICATION.json`, `MECHANISM-CONTROLS.json`, `G5-PUBLISHED-QUALIFICATION.json` and `TEST-RESULTS.json` contain the results. The source/code/settings plan was hashed before each qualification run. `QUALIFICATION-PLAN-v3.json` is a sandbox seal, not a claim freeze.

## Mapping implemented

Longest-match atoms are `cth/ckh/cph/cfh/ch/sh`, then single lowercase EVA characters. These are operational transcription units, not established manuscript graphemes. Each target inventory contains every observed overlapping span of1–3 such atoms **within a readable word**. No word boundary, unknown slot, neighboring-word outcome, line-opening flag or H3 estimator contributes.

Each source unit and target span receives one position class from its own distribution: initial, medial or final at>=95%, otherwise free. Whole-word target spans and source singletons count as free. Units are ranked by frequency within class, with SHA256(seed:unit) ties. Assignments are injective. Capacity failure or an unseen source unit raises an error; there is no silent merging, invented span, wider fallback or borrowed class. The exact inventories and hashes are saved.

G4 maps each source letter/code variant to a span of1–3 atoms; its width comes from the fixed rank mapping. Optional null units and position variants are explicit. The earlier version independently preassigned widths and exhausted the one-atom position classes; all400 failures remain archived. Narrow max_expansion settings can still abstain honestly.

Mapped unit boundaries accompany the display strings. Concatenated EVA is not claimed uniquely decodable, and reparsing a flat string can fuse atoms across latent group boundaries. Fit summaries continue to use literal EVA characters as previously specified. Group counts and classes are an explicit target-informed mapping input beyond the single-character fit summaries; this information budget must be retained in the eventual claim protocol.

## Generator scope

| Family | What was qualified | Remaining scope limit |
|---|---|---|
| G1 | Source order/letters preserved; deterministic mapping on edited Latin herbal | Italian/Czech/Occitan coverage remains pending; current Latin/German Bible sources are not medical |
| G2 | Sourced abbreviation rule subset; probability0 identity; probability1 applies all eligible suffix rules; intermediate rate checked against binomial variation | Synthetic rule rates on expanded text; no real diplomatic abbreviated-Latin control |
| G3 | Reduces to G2 at symbol probability0; at probability1 all `et` opportunities get a separate symbol unit | `et` sign is attested; after-vowel/context variants are synthetic parameters; broad medical concept inventory pending |
| G4 | One letter/code variant per source letter,1–3-atom mapped groups, optional nulls, repeatability | Mapping and position/null boundary settings overlap G1; not independently identifiable there |
| G5 | Pinned **unmodified published Java source**, compiled and run with native layout; repeat-seed and distinct-seed controls | Full mechanism/model recovery remains unrun; seed-line policy and parameter priors still need claim freeze |
| G6 | Repeated prefix/root/suffix column blocks, explicit three-hole offsets, irregular vertical moves, blanks; every output reconstructed independently from cell coordinates | A specified Rugg-style parameterization, not a unique historical table or human movement law |

The candidate entrypoint is **`registry.produce`**. Its G5 route always runs the published implementation and rejects forced target token-count layouts. The earlier Python G5 surrogate remains available solely as a development control; it is not the qualified candidate. Corpus-derived built-in VMS follow tables are rejected; only `curveline`/`none` follow options are admitted here. Java is portable within this experiment; no system settings were changed. Download/archive checksums and source commit hashes are retained.

Source provenance: [Timm–Schinner published repository](https://github.com/TorstenTimm/SelfCitationTextgenerator); [Rugg's mechanism account](https://hydeandrugg.wordpress.com/2014/03/02/hoaxing-the-voynich-manuscript-part-7-producing-the-text/). The G6 implementation follows repeated three-column blocks with offset holes and variable vertical movement; its finite step law and edge handling are explicit modeling choices.

G2/G3 sources: [HMML abbreviation reference](https://hmmlschool.org/lexicon/14357/), [Ad fontes](https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/abkuerzungen), and [Folger's rum example](https://www.folger.edu/blogs/collation/abbreviations-and-signatures/). These support rule types, not the chosen probabilities or a particular herbal's usage. `RULE-SOURCES.json` links each rule and distinguishes attestation from synthetic choices.

## Known-source controls

The edited Latin [Macer / De viribus herbarum](https://la.wikisource.org/wiki/De_viribus_herbarum) was archived at Wikisource revision272959 with HTML, source-word hashes and attribution. It contains13,967 extracted words in77 poem sections. Entire sections were split first60% development / final40% qualification, and all qualification trials use the latter source sections. This is edited herbal verse with expanded orthography, not a14th–15th-century diplomatic source. Lowercase ASCII word extraction and source wrapping are explicit development policies; normalization/length robustness remain before the claim run. Source sections are disjoint; vocabulary is not.

The abbreviation sign units remain separate inside source words. The source/control results establish implementation behavior, not historical accuracy, language identification or readability of mapped EVA.

## Preserved failures and current boundaries

`development-history/sandbox-1/` preserves the original40 mapping abstentions. `development-history/group-qualification-1/` preserves all400 exact-width cipher failures and an insufficient-capacity test fixture; the fixture was corrected without relaxing the rejection rule. Qualification2's passing results remain archived before the production wrapper's corpus-table guard and candidate-entrypoint checks were added. Qualification3 replays the full schedule with current owner hashes. No held score was used to choose the repairs.

H3 remains **UNRESOLVED**. Its earlier noise correction and context construction have not been replaced. H1/H2 retain Re's approved move to log odds ratio with recomputed targets later; the old RD strengthening numbers are not reused. Exact H1/H2/H5/H6/H7/H8 definitions, H4's overlap with fitted position shares, fair layout/source-length conditioning, all source-language coverage, priors/tolerances, real abbreviated-Latin control and full recovery/confusion gates remain before a claim freeze.

“Mechanics qualified” is deliberately narrower than “family qualified for elimination.” The full recovery/confusion experiment requires H1–H8 and remains closed. No posterior samples, PPC percentiles, ABC model probabilities, survivors or eliminations have been produced.

## Reproduce

```powershell
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s system-types-v5 -p 'test_*.py' -v
python system-types-v5/qualify_generators.py run
python system-types-v5/prepare.py
```

The existing qualification plan must match its owners. Starting a new plan is a separate explicit sandbox cut, preserving the old trials first. `held.score` continues to refuse scoring without a complete valid claim freeze; its statistic dispatch remains unimplemented rather than returning surrogate scores.
'''
    (ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    runtime=json.loads((ROOT/'RUNTIME/MANIFEST.json').read_text())
    assert sha(ROOT/'RUNTIME/temurin8.zip')==runtime['archive_sha256']
    v=dict(status='SANDBOX_MECHANISMS_QUALIFIED_CLAIM_LOCKED',claim_ready=False,engineering_tests=19,failures=0,errors=0,
        mechanism_trials=200,mapping_trials=1600,mapping_failures=0,published_G5_repeat_pairs=5,
        H3='UNRESOLVED',claim_freeze_exists=False,held_statistics_computed_on_generator_output=False,
        held_statistics_computed_on_manuscript=False,manuscript_fit_performed=False,inference_performed=False,
        H_F_pooled=False,Currier_A_B_pooled=False,cells=10,source_hashes_checked=True,exclusions_checked=True,
        qualified_owner_hashes_unchanged=True,qualification_plan_sha256=sha(ROOT/'QUALIFICATION-PLAN-v3.json'),
        runtime_archive_verified=True,java_exe_sha256=sha(runtime['java']),javac_exe_sha256=sha(runtime['javac']),
        environment=dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__),
        report_sha256=sha(ROOT/'REPORT.md'),code_hashes={str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob('*.py')})
    v['code_hashes']['GENERATORS/__init__.py']=sha(ROOT/'GENERATORS/__init__.py')
    save(ROOT/'VERIFICATION.json',v)
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(ROOT/'RUNTIME')
           and not p.is_relative_to(ROOT/'G5-BUILD/classes') and p!=ROOT/'DELIVERY-HASHES.json']
    save(ROOT/'DELIVERY-HASHES.json',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    print(json.dumps(dict(status=v['status'],delivery_files=len(paths),tests=19,mapping_passes=1600,held_scoring=False)))

if __name__=='__main__':main()
