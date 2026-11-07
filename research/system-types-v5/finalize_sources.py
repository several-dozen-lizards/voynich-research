"""Update current records after source controls, leaving claim execution closed."""
from pathlib import Path
import json,platform
from core import save,sha
from held import score,ClaimLocked
from recovery_design import require_recovery_release,RecoveryLocked

ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/'FREEZE.json').exists()
    for plan_name in ('QUALIFICATION-PLAN-v3.json','SOURCE-CONTROL-PLAN-v3.json','SOURCE-COVERAGE-PLAN.json'):
        p=json.loads((ROOT/plan_name).read_text());assert all(sha(ROOT/n)==h for n,h in p['files'].items()),plan_name
    for call,error in [(lambda:score(ROOT,'H3',[]),ClaimLocked),(lambda:require_recovery_release(ROOT),RecoveryLocked)]:
        try:call()
        except error:pass
        else:raise AssertionError('claim/recovery gate opened')
    sources=json.loads((ROOT/'SOURCE-INVENTORY.json').read_text())
    real=json.loads((ROOT/'SOURCE-CONTROL-RESULTS.json').read_text())
    coverage=json.loads((ROOT/'SOURCE-COVERAGE-RESULTS.json').read_text())
    primary=real['primary_control']
    old=json.loads((ROOT/'development-history/source-controls-start/PROTOCOL.json').read_text())
    prior=json.loads((ROOT/'development-history/source-controls-start/STATUS.json').read_text())
    blockers=[b for b in prior['blockers'] if b['id'] not in ('SOURCES','RECOVERY','CLAIM_EXECUTION')]
    blockers.extend([
        dict(id='REAL_LATIN_TRANSFER',status='ABSTAINS',detail='Earlier-medical development maps lack some written units in reserved14th-century medical text. All10 transfer checks abstain; no guessed expansions or default mappings. Real G2 survival remains unrun.'),
        dict(id='PARTITION_SOURCE_LENGTH',status='LIMITED',detail='Full source pools support all50 language×geometry size checks without repetition.47 of150 partition×cell checks lack sufficient disjoint text. Future recovery/control sizes must respect these support limits.'),
        dict(id='CLAIM_EXECUTION',status='LOCKED',detail='Recovery/discrimination is now operationally specified in RECOVERY-PROTOCOL.json but not run. Original H3, exact other held definitions, final priors/layout/resource settings and claim freeze still required.')])
    old.update(version='v5-source-controls-4',status='SOURCE_CONTROLS_COMPLETE_CLAIM_LOCKED',blockers=blockers,
        source_controls='SOURCE-CONTROL-RESULTS.json',source_coverage='SOURCE-COVERAGE-RESULTS.json',recovery_design='RECOVERY-PROTOCOL.json',
        source_policy='Use complete historical language sources with provenance; keep genres, editions, diplomatic signs and disjoint source partitions explicit. Never repeat a short reserve to claim manuscript-size support.',
        H3='UNRESOLVED',claim_freeze_created=False)
    save(ROOT/'PROTOCOL.json',old)
    status=dict(status='SOURCE_CONTROLS_COMPLETE_RECOVERY_DEFINED_CLAIM_LOCKED',complete=False,H3='UNRESOLVED',claim_freeze=False,
        source_languages=list(sources),real_abbreviated_Latin='INGESTION/REPRESENTATION_PASS; DEVELOPMENT_TRANSFER_ABSTAINS',
        recovery_protocol='DEFINED_NOT_EXECUTED',blockers=blockers,
        next_step='Recover original H3 and settle remaining held definitions/unknown-unit/layout/prior/resource policies; run full recovery only after a complete claim freeze.',
        pending_claim_deliverables=prior['pending_claim_deliverables'])
    save(ROOT/'STATUS.json',status)
    table='\n'.join(f"| {language} | {s['words']:,} | {s['source_units']} | {s['kind']} |" for language,s in sorted(sources.items()))
    report=f'''SOURCE CONTROLS COMPLETE; RECOVERY/DISCRIMINATION DEFINED — H3 UNRESOLVED, CLAIM SCORING LOCKED.

# Voynich system types v5: source controls and recovery design

Recorded24 October2026, America/New_York. This continuation acquires and controls real source texts, preserves real abbreviated Latin, and defines the later recovery/discrimination experiment. **No H1–H8 statistic, manuscript ABC fit, model survival/elimination, or full recovery run was performed.**

## Real abbreviated Latin

The primary reserve is the14th-century **Tractatus de Sterilitate**, Philadelphia College of Physicians10a135. All five pages are reserved from abbreviation-rule fitting. CREMMA's manually transcribed, post-ChocoMufin **ALTO** ground truth preserves abbreviation signs rather than expanding them. The repository is pinned at commit292525969ad98380b398e6606a9c2a36d51913ae and declares CC-BY4.0. [Source and methods](https://github.com/HTR-United/CREMMA-Medieval-LAT).

The reserve contains **{primary['readable_words']:,} readable written-token slots in139 main-text lines**, including symbol-only units. **938 slots ({primary['marked_word_share']:.1%})** contain explicit signs or combining marks. This passes the predeclared source-support and10% marked-share gate. It is not a semantic expansion count: some marks also encode interlinear additions, and the transcription already standardizes some glyph variants.

Written signs, combining marks, numerals, medical unit glyphs and private-use glyphs remain separate units. Every included lexical span round-trips to its normalized written form with raw offsets retained. No missing letters were inferred. Main text is selected from explicit ALTO MainZone labels; excluded blocks remain in `REAL-LATIN-EXCLUSIONS.json`. Two earlier medical manuscripts (H318 and CLM13027) are development sources;15th-century PalLat373 is a scholastic chronology sensitivity, not relabelled as medical.

**Representation succeeds in10/10 EVA inventories. Cross-manuscript mapping transfer abstains in10/10.** The earlier-medical inventory lacks some units found in the reserved manuscript. `REAL-LATIN-MAPPING.json` retains every unknown and supported-word count. We did not learn missing units or rule probabilities from the reserve to turn this into a passing transfer result. Real G2 survival is **NOT RUN**.

The reserve was selected from genre/date metadata before statistical controls. It is reserved from algorithmic rule fitting, not claimed historically unseen to the analyst: an opening line/XML structure was inspected during ingestion development.

## All five language sources

| Language | Extracted tokens | Source units | Source kind |
|---|---:|---:|---|
{table}

Italian and Czech use whole canto/chapter units. German uses source chapter/strophe sections from [TITUS's Buch der Natur edition](https://titus.uni-frankfurt.de/texte/etcs/germ/mhd/konrmeg/konrmt.htm), based on Pfeiffer1861, with metadata and editorial material excluded from the text selector. The complete [Czech1877 edition](https://cs.wikisource.org/wiki/R%C3%BDmovan%C3%A1_kronika_%C4%8Desk%C3%A1_tak_%C5%99e%C4%8Den%C3%A9ho_Dalimila) supplies106 main chapters; editorial introduction and later-redaction appendices are excluded. [Italian Inferno](https://it.wikisource.org/wiki/Divina_Commedia/Inferno) supplies34 cantos. [CorAG](https://github.com/UniversalDependencies/UD_Old_Occitan-CorAG) supplies six medieval legal works; the1564 source is excluded. Integer FORM tokens are counted once, empty nodes/multiword wrapper rows excluded, and original sentence IDs reconstruct order before whole-work splitting.

Macer remains the Latin herbal source. The earlier German Bible and Oxford Old Czech excerpt are retained as separate secondary controls, not pooled into the period-matched primary sources. NFC letters and diacritics are preserved; source extraction does not strip accents or rewrite historical spelling. Literary/chronicle/legal genre differences remain explicit.

Source HTML/XML, revisions/commits, attribution and hashes are archived. CREMMA is CC-BY4.0; CorAG is CC-BY-SA4.0; Wikisource pages retain their stated public-domain underlying edition and transcription terms. **No open redistribution license was established for the TITUS electronic transcription or Oxford excerpt**: those remain internal research sources and must not be included in public releases without appropriate permission. Historical underlying texts do not by themselves license a modern electronic transcription.

## Completed source controls and limits

- **50/50 development inventory mappings pass**, five languages ×ten EVA panels.
- **30/50 reserve transfers pass;20/50 abstain** on unseen units. All such units and affected-word counts remain in `LANGUAGE-MAPPING-CONTROLS.json`; no default spelling or unit merger was inserted.
- All **50/50 full-source size checks** contain at least the relevant manuscript cell's readable-token count without repetition.
- **47/150 partition-specific size checks are unsupported.** Availability of a complete work does not make each independent reserve long enough. `SOURCE-SIZE-CONTROLS.json` enumerates the supported cells; recovery may not pad or cycle a short source part.
- Seven new source/recovery-decision checks pass, including raw sign/medical-unit preservation, full source-character coverage, Unicode retention, unknown barriers, disjoint partitions, survival-versus-discrimination, and the H3 recovery lock. The earlier19 engineering tests remain qualified under unchanged owner hashes.

These are ingestion, representation, transfer and size controls. They establish neither language identity nor that a production family survives the manuscript's held-out tests.

## Recovery/discrimination protocol

`RECOVERY-PROTOCOL.json` defines the experiment; `RECOVERY-DESIGN-SEAL.json` hashes the design and decision code. **Neither is a claim FREEZE. Execution is locked.**

The full design schedules100 pseudo-manuscripts per true family per supported reading-cell:80 interior draws and20 shared-boundary cases. Across six families and ten cells this is6,000 datasets. Candidate mappings, source support and bootstrap scales must be rebuilt against each pseudo-target; truth keys, labels and source IDs cannot leak into fitting or predictors. H/F fits and confusion matrices stay separate, with both gates required for a shared headline.

Every candidate uses S_fit-only ABC-SMC with at least2,000 final accepted particles and ESS>=1,000. Predictive intervals use importance weights. Multiple components of H3 or H6 count as **one** statistic-family failure under a predeclared simultaneous envelope; they cannot supply two elimination votes. Missing components, infinite envelopes, insufficient source support and exhausted computation are not passing results or mechanism eliminations.

The true family must survive at least80/100 trials, with binomial uncertainty reported. Separately, at least64/80 interior trials must retain the true family while rejecting at least three of five wrong families. Pairwise co-survival and false-exclusion tables remain mandatory. Boundary cases must be allowed to co-survive: G2 at zero abbreviation, G3 at zero symbol substitution, and G4 with no positional/null additions overlap simpler mechanisms. An all-surviving system fails discrimination. Parameter recovery requires both coverage and informative accuracy/interval width, with every exemption declared before scoring.

Source-label and family-label permutation negatives, source/seed leakage audits, native-size real Latin controls and genre/date sensitivity strata are specified. A failed required gate yields **PIPELINE_CANNOT_DISCRIMINATE** for that scope; thresholds cannot be repaired after seeing that cut's results. Random forest model choice stays descriptive, uses disjoint reference data, and reports Pudlo-style selected-model probability rather than treating vote fractions as all-family posterior probabilities.

The full design is computationally substantial: at least **72 million final accepted particles**, or216 million across three2,000-particle generations, before rejected proposals and predictive simulations. Per-fit simulator budget is capped at250,000 calls; runtime and prior/tolerance settings must be finalized before claim release. **This design did not launch that workload.** Unsupported source-size cells remain unqualified rather than being silently filled.

H3 remains **UNRESOLVED**. `recovery_design.require_recovery_release` refuses the full run while H3 is unresolved, and `held.score` still refuses H1–H8 without a valid complete claim freeze. There is no reduced-H3 substitute run.

## Preserved development failures

`development-history/source-controls-1/` retains an ingestion defect that dropped an ounce/private-use glyph, plus the initial sentence-based Gascon partition. The corrected parser preserves those glyphs without guessing meanings and splits Gascon by whole work. The raw coverage test initially excluded a genuine punctuation-category abbreviation sign; its fixture was corrected while retaining the preservation requirement. `source-controls-2/` preserves the short Czech/Bible-only source stage before complete Czech and historical German acquisition. The original40 mapping abstentions and400 cipher-width failures remain in their earlier archives.

Acquisition failures are also recorded: the Italian index initially used absolute links; a full Czech fetch encountered429 and resumed from cached pages with one connection/backoff; German acquisition retained certificate validation, succeeded using the installed public CA bundle, and did not disable TLS checks.

Prior generator qualification: [preserved previous report](development-history/source-controls-start/REPORT.md). Current result owners: `SOURCE-CONTROL-RESULTS.json`, `SOURCE-COVERAGE-RESULTS.json`, `RECOVERY-PROTOCOL.json`, `STATUS.json`, `VERIFICATION.json`. Reproduce sources/control results with the hashed `SOURCE-CONTROL-PLAN-v3.json` and `SOURCE-COVERAGE-PLAN.json`; do not create a new plan over an old cut.
'''
    (ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    retained=json.loads((ROOT/'RETAINED-FAILURES.json').read_text())
    retained['source_ingestion_and_partition']='development-history/source-controls-1/INGESTION-AUDIT-FAILURES.json'
    retained['source_transfer']=dict(real_Latin_abstentions=10,language_abstentions=20,source_partition_size_failures=47)
    retained['acquisition']=['Italian absolute-link index guard failed, then repaired','German default CA issuer verification failed; public CA bundle retained verification and succeeded','Augsburg alternative endpoint503','Czech parallel download429; resumed only missing chapters using cached pages and one connection/backoff']
    retained['test_fixture']='Full-character oracle first excluded punctuation-category Tironian abbreviation; corrected to retain explicitly registered signs'
    save(ROOT/'RETAINED-FAILURES.json',retained)
    verification=json.loads((ROOT/'development-history/source-controls-start/VERIFICATION.json').read_text())
    verification.update(status=status['status'],claim_ready=False,engineering_tests=26,new_source_tests=7,
        source_ingestion_pass=True,real_Latin_primary_tokens=primary['readable_words'],real_Latin_marked_tokens=938,
        real_Latin_transfer_abstentions=10,language_mapping_passes=50,language_transfer_passes=30,language_transfer_abstentions=20,
        partition_size_failures=47,full_source_size_passes=50,claim_freeze_exists=False,H3='UNRESOLVED',
        held_statistics_computed_on_generator_output=False,held_statistics_computed_on_manuscript=False,
        recovery_defined=True,recovery_executed=False,recovery_gate_verified_locked=True,claim_G2_survival='NOT_RUN',
        qualified_owner_hashes_unchanged=True,source_control_owner_hashes_unchanged=True,
        report_sha256=sha(ROOT/'REPORT.md'),recovery_protocol_sha256=sha(ROOT/'RECOVERY-PROTOCOL.json'),
        code_hashes={str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob('*.py')})
    verification['code_hashes']['GENERATORS/__init__.py']=sha(ROOT/'GENERATORS/__init__.py')
    save(ROOT/'VERIFICATION.json',verification)
    save(ROOT/'TEST-RESULTS.json',dict(total_current_tests=26,prior_tests=19,new_source_recovery_tests=7,
        source_test_command='python -m unittest discover -s system-types-v5 -p test_source_controls.py -v',errors=0,failures=0,
        qualification_scope='Engineering/source representations and label-decision tests; no H1–H8 computation or full recovery.'))
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(ROOT/'RUNTIME') and not p.is_relative_to(ROOT/'G5-BUILD/classes') and p!=ROOT/'DELIVERY-HASHES.json']
    save(ROOT/'DELIVERY-HASHES.json',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    print(json.dumps(dict(status=status['status'],delivery_files=len(paths),real_Latin_tokens=primary['readable_words'],H3='UNRESOLVED',held_gate='LOCKED',recovery='DEFINED_NOT_RUN')))

if __name__=='__main__':main()
