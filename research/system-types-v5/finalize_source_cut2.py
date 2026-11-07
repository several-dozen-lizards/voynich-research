"""Publish the separate development cut, retaining prior controls and every claim lock."""
from pathlib import Path
import json,shutil
from core import sha
from held import score,ClaimLocked
from recovery_design import require_recovery_release,RecoveryLocked
from source_cut2 import ROOT,CUT,dump,validate_selection

def main():
    validate_selection();assert not (ROOT/'FREEZE.json').exists()
    result=json.loads((CUT/'RESULTS.json').read_text());tests=json.loads((CUT/'TEST-RESULTS.json').read_text())
    assert tests['passed'] and tests['tests']==50 and result['source_size_supported']==7
    assert result['development_codebook_statuses']=={'PASS':60} and result['source_entrypoint_trials']==22
    qualification=CUT/'QUALIFICATION-PLAN-v2.json';q=json.loads(qualification.read_text())
    assert result['qualification_plan_sha256']==sha(qualification)
    assert all(sha(CUT/n)==h for n,h in q['files'].items()) and all(sha(ROOT/n)==h for n,h in q['owners'].items())
    for name in ('QUALIFICATION-PLAN-v5.json','SOURCE-CONTROL-PLAN-v3.json','SOURCE-COVERAGE-PLAN.json','TRANSFER-DIAGNOSTIC-PLAN-v2.json','SOURCE-ENTRYPOINT-PLAN-v2.json'):
        plan=json.loads((ROOT/name).read_text());assert all(sha(ROOT/n)==h for n,h in plan['files'].items()),name
    for name in ('ACQUISITION.json','PETRARCH-ACQUISITION.json','JAUFRE-PROVENANCE.json'):
        for item in json.loads((CUT/name).read_text())['files']:assert sha(CUT/item['path'])==item['sha256']
    reserve=json.loads((CUT/'FRESH-RESERVE-SEAL.json').read_text())
    assert reserve['bodies_parsed']==0 and reserve['plan_sha256']==sha(CUT/'RESERVE-ACQUISITION-PLAN.json')
    assert all(r['status']=='OPAQUE_BYTES_SEALED' and sha(CUT/'fresh-reserves'/r['path'])==r['sha256'] for r in reserve['files'])
    for call,error in ((lambda:score(ROOT,'H3',[]),ClaimLocked),(lambda:require_recovery_release(ROOT),RecoveryLocked)):
        try:call()
        except error:pass
        else:raise AssertionError('claim gate opened')
    inv=json.loads((CUT/'DEVELOPMENT-INVENTORY.json').read_text());cases=json.loads((CUT/'SEVEN-SHORT-SOURCE-CASES.json').read_text());strata=json.loads((CUT/'ABBREVIATED-LATIN-STRATA.json').read_text())
    italian=inv['Italian']['known_gap_support_by_work']
    table='\n'.join(f"| {r['language']} / {r['cell']} | {r['required_slots']:,} | {r['new_longest_run']:,} |" for r in cases)
    attestation='\n'.join(f"| {work} | {counts.get(chr(228),0)} | {counts.get('x',0)} |" for work,counts in italian.items())
    report=f'''# Voynich v5: independent development source cut 2

The new development cut supplies every previously missing literal unit and supports all seven prior source-size failures. **This is development qualification. H3 remains unresolved; fresh-reserve transfer, H1–H8 scoring, model survival and full recovery remain unrun.** No claim `FREEZE.json` exists.

## Development material and scope

- **Latin:** Dante's *Monarchia*, all three books, {inv['Latin']['slots']:,} word slots in one work. This supplies length as 14th-century political prose; it does not qualify a long medical/herbal register.
- **Occitan:** *Jaufre*, Charmaine Lee's RIALC 2000/revised 2002 edition, all 10,974 numbered lines in order without gaps or duplicates, {inv['Occitan']['slots']:,} word slots. There are 153 literal `ç` occurrences. This is Old Occitan narrative, a dialect/register sensitivity alongside the earlier Gascon legal sources.
- **Italian:** all 33 *Purgatorio* cantos and the complete 366-poem Petrarch *Canzoniere* collection. Whole collections were selected before acquisition, rather than individual gap-bearing poems. Purgatorio shares Dante and the larger *Commedia* with the old Inferno control; Petrarch provides an independent author/work check. **Independent-author coverage of `ä` remains absent:** Petrarch supplies `x` but no `ä`. This is a retained independence limitation, not a reason to rewrite the letter or promote reserve text.
- **Czech:** Oxford's diplomatic *Mastickar* Muzejni fragment, {inv['Czech']['slots']:,} slots and304 literal `w` occurrences. Editorially supplied or uncertain forms remain opaque barriers. Modern stage directions and the parallel transliterated column are excluded. This is an alphabet supplement, not a full-length generation source.
- **Real abbreviated Latin:** 15 previously unused CREMMA manuscripts, 93 admitted pages, 4,279 lines and 38,399 written-token slots. Every missing digit (`0,1,2,3,4,6,7,8`) and U+0301 is attested. All nine units are already present in the nine manuscripts dated through 1399; the six 15th-century supplements are separately tabulated. Medical-only new material does not supply those nine units. The new coverage therefore belongs to the declared cross-genre graphematic pool, not a medical-only claim.

| Italian development work | `ä` occurrences | `x` occurrences |
|---|---:|---:|
{attestation}

The two acute-mark instances are literal transcriptions at CCCC-MSS-236/3r (`f́ornice`,1200–1225) and LaurentianusPluteus39.34/3r (`sb́`,15th century). Neither their matching Unicode labels nor their attestation establishes matching functions or an abbreviation expansion. `KNOWN-GAP-EVIDENCE.json`, `LANGUAGE-GAP-EVIDENCE.json` and `ABBREVIATED-LATIN-STRATA.json` retain exact manuscript/page/line or work/unit/slot provenance.

## Seven original-slot budgets

| Source/cell | Required slots | New consecutive same-work run |
|---|---:|---:|
{table}

`source_cut2.load_cut2_development` constructs immutable, hash-checked development runs and delegates generation to the existing `source_contract.produce_from_development`. Missing sections and work boundaries cannot be bridged; reserve/calibration requests and inventory-only supplements are rejected for generation. Starts are sampled uniformly over eligible positions. No wrapping, padding, cross-work stitching or partition pooling is used. The old development pool remains separately identified for alphabet fitting; old calibration/reserves never enter the new fits. Every readable development token contributes once to its declared source pool; no reserve-dependent weighting is fitted.

## Qualification and fresh reserves

**60/60 development codebooks pass capacity checks** across six source pools and ten EVA inventories. **22/22 actual-geometry generation checks pass** for the entrypoints previously blocked by these shortages: five Latin cells × G1–G4 and two Occitan cells × G1. These checks establish executable support at the stated sizes; they are not source-transfer or model-discrimination results. The earlier200-trial mechanism qualification remains a separate, earlier-source result.

**50/50 engineering tests pass.** The JVM initially failed before G5 could start, first with its default heap and then with a256MB bound. A64MB process-scoped heap with serial GC passes; the unmodified published generator source remains pinned. Test receipts retain both failures and the final command. No system-wide Java setting changed.

Fresh reserves were assigned before their bodies were acquired: *De vulgari eloquentia*, *Paradiso*, *Podkoni a zak*, manuscript Latin16195, and the10-page *Flamenca* manuscript GT sample at pinned gatmuza commit. **48 files are archived and byte-hashed separately; zero reserve bodies were parsed, counted for coverage, fitted or scored.** Source identity/readability and transfer support remain future gates; byte sealing does not certify them. The Flamenca sample is a native-page control, not an asserted manuscript-sized source. Paradiso/Purgatorio/Inferno remain same-author/larger-work related; Latin manuscripts are not automatically independent underlying texts.

The live RIALTO/RIALC certificate was expired. Jaufre was acquired from Internet Archive replays of the original scholarly edition; certificate verification was never disabled. Source URLs and hashes are in `JAUFRE-PROVENANCE.json`. CREMMA/gatmuza source attribution and CC-BY4.0 terms are retained; Wikisource attribution/declared licenses are retained. No open redistribution license was established for the RIALC electronic edition or Oxford teaching text: internal research only, not a public-source bundle.

## Preserved controls and remaining gates

The prior503-file delivery was verified byte-for-byte and its report, status, protocol and manifest preserved in `previous-cut/`. Its failed transfers remain failed controls. The initial cut2 section-only qualification is retained under `development-history/initial-section-control/`. New development attestation does not retroactively turn an exposed old reserve into a fresh test.

This cut has not been adopted into claim priors or the full recovery schedule. The existing recovery protocol and all held-statistic locks remain in force. H3 has no replacement estimator. Before claim execution, finish the unresolved definitions and freeze the source/register scope, mappings, priors, layout/runtime settings and reserve-access protocol.

Reproduce local checks with `python system-types-v5/source_cut2.py`, `python system-types-v5/qualify_source_cut2.py`, `python system-types-v5/check_source_cut2.py`, then `python system-types-v5/prepare.py`. Acquisition scripts are separate and are not needed to rerun these checks. Fresh reserve files remain outside every development loader.
'''
    (CUT/'REPORT.md').write_text(report,encoding='utf-8');(ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    old=json.loads((CUT/'previous-cut/STATUS.json').read_text());blockers=[b for b in old['blockers'] if b['id'] not in ('SOURCE_SUPPORT','FROZEN_TRANSFER','CLAIM_EXECUTION')]
    blockers += [dict(id='ITALIAN_INDEPENDENCE',status='DANTE_SECTION_ONLY_FOR_DIAERESIS_A',detail='New Purgatorio attests ä once; the complete independent Petrarch collection attests x78times but no ä. No independent-author ä support is claimed.'),
        dict(id='FRESH_TRANSFER',status='LOCKED_UNRUN',detail='New development supplies exposed gaps; fresh reserves are opaque/sealed. No new reserve coverage, transfer or family survival is claimed.'),
        dict(id='SOURCE_SCOPE',status='REVIEW_BEFORE_CLAIM_FREEZE',detail='Long Latin is nonmedical; Jaufre differs from Gascon legal prose; Dante canticas are related; real Latin pool spans genres and dates. Fix claim scope before scoring.'),
        dict(id='CLAIM_EXECUTION',status='LOCKED',detail='H3 and remaining held definitions, final priors/layout/runtime and full claim freeze remain required.')]
    status=dict(status=result['status'],source_cut_complete=True,complete=False,claim_ready=False,H3='UNRESOLVED',held_scoring=False,claim_freeze=False,
        active_development_source_cut='source-cut-2',known_gap_inventory_coverage=True,previous_size_failures_supported=7,
        new_source_entrypoint_trials=22,new_codebook_capacity_passes=60,engineering_tests=50,fresh_reserve_files_sealed=48,fresh_reserve_bodies_parsed=0,
        old_cut_source_failures_retained=7,old_cut_transfer_results_retained=True,blockers=blockers,pending_claim_deliverables=old['pending_claim_deliverables'])
    dump(ROOT/'STATUS.json',status)
    protocol=json.loads((CUT/'previous-cut/PROTOCOL.json').read_text());protocol.update(version='v5-source-cut2-development',status=status['status'],development_source_cut2='source-cut-2/SELECTION.json',
        source_cut2_loader='source_cut2.load_cut2_development',source_cut2_qualification='source-cut-2/QUALIFICATION-PLAN-v2.json',
        source_cut2_adopted_for_claim=False,fresh_reserve_manifest='source-cut-2/FRESH-RESERVE-SEAL.json',blockers=blockers,H3='UNRESOLVED',claim_freeze_created=False)
    dump(ROOT/'PROTOCOL.json',protocol);dump(ROOT/'TEST-RESULTS.json',tests)
    verification=dict(**status,old_frozen_owner_plans_unchanged=True,old_delivery_audit='source-cut-2/PREVIOUS-DELIVERY-AUDIT.json',
        held_statistics_computed_on_generator_output=False,held_statistics_computed_on_manuscript=False,manuscript_fit_performed=False,recovery_executed=False,
        qualification_plan_sha256=sha(qualification),fresh_reserve_seal_sha256=sha(CUT/'FRESH-RESERVE-SEAL.json'),report_sha256=sha(CUT/'REPORT.md'))
    dump(ROOT/'VERIFICATION.json',verification);dump(CUT/'VERIFICATION.json',verification)
    retained=json.loads((CUT/'previous-cut/RETAINED-FAILURES.json').read_text());retained['cut2']='source-cut-2/development-history/initial-section-control; old cut1 failures unchanged; initial JVM failures retained in source-cut-2/TEST-RESULTS.json'
    dump(ROOT/'RETAINED-FAILURES.json',retained)
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(ROOT/'RUNTIME') and not p.is_relative_to(ROOT/'G5-BUILD/classes') and p!=ROOT/'DELIVERY-HASHES.json']
    dump(ROOT/'DELIVERY-HASHES.json',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    print(json.dumps(dict(status=status['status'],tests=50,source_size_cases_supported=7,codebook_passes=60,entrypoint_passes=22,fresh_reserve_files=48,fresh_reserve_bodies_parsed=0,delivery_files=len(paths),H3='UNRESOLVED',held_scoring=False)))

if __name__=='__main__':main()
