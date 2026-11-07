"""Descriptive reserve coverage/provenance; all mapping estimation is development-only."""
from pathlib import Path
from collections import Counter
from dataclasses import asdict
import json,sys,unicodedata as U
from core import save,sha,canonical_hash
from transfer_policy import (ROOT,fit_development_codebook,transfer_slots,source_runs)

def unit_name(unit):
    if unit.startswith(('MARK:','SIGN:','DIGIT:','GLYPH:')):
        text=chr(int(unit.rsplit('+',1)[1],16))
    else:text=unit
    return dict(unit=unit,characters=text,codepoints=[f'U+{ord(c):04X}' for c in text],
                unicode_names=[U.name(c,'UNASSIGNED_OR_PRIVATE_USE') for c in text],
                interpretation='literal transcription unit only; no assigned meaning or normalization repair')

def language_data(language):
    units=json.loads((ROOT/(language.upper()+'-SOURCE-UNITS.json')).read_text())
    parts=json.loads((ROOT/'LANGUAGE-SOURCE-SPLITS.json').read_text())[language]
    grouped={name:[u for u in units if u['unit'] in set(meta['units'])] for name,meta in parts.items()}
    dev=[list(w) for u in grouped['development'] for w in u['words']]
    rows=[dict(source_unit=u['unit'],tokens=[list(w) for w in u['words']]) for u in grouped['reserve']]
    return units,parts,dev,rows

def plan():
    path=ROOT/'TRANSFER-DIAGNOSTIC-PLAN-v2.json'
    if path.exists():raise FileExistsError(path)
    files=['diagnose_transfer.py','transfer_policy.py','UNKNOWN-AND-LENGTH-POLICY.json','core.py','held.py',
           'LANGUAGE-SOURCE-SPLITS.json','CELLS.json','EVA-GROUP-INVENTORIES.json','REAL-LATIN-ROWS.json',
           'SOURCE-CONTROL-SELECTION.json','LANGUAGE-MAPPING-CONTROLS.json','REAL-LATIN-MAPPING.json']
    files += [f'{lang}-SOURCE-UNITS.json' for lang in ('LATIN','GERMAN','ITALIAN','CZECH','OCCITAN')]
    save(path,dict(tier='descriptive diagnostic, not claim freeze',prior_exposure='Prior first1000-word gaps and real-Latin gaps already exposed; do not claim new untouched validation.',
        analysis='Full reserve occurrence counts and positions; unchanged development-only codebooks; immutable barrier views; same-work contiguous source budgets including original unknown slots. No reserve-trained fix, performance threshold, H1–H8 score or ABC inference.',
        files={n:sha(ROOT/n) for n in files}))

def diagnose_one(name,dev,rows,targets,expected_books):
    results=[];masks=[];reference=None;training_digest=canonical_hash(dev)
    for cell,target in sorted(targets.items()):
        book=fit_development_codebook(dev,target,'development')
        expected=expected_books[cell]['receipt']['mapping']
        assert book.mapping==expected,'development-only fit does not reproduce frozen baseline'
        before=canonical_hash(asdict(book));occurrences=[];views=[];units_count=Counter();word_types=Counter();total=0;affected=0;baseline_unknown=0
        for row in rows:
            rendered=transfer_slots(row['tokens'],book);total+=len(row['tokens']);baseline_unknown+=rendered['baseline_unknown_slots']
            views.append(dict(source_unit=row['source_unit'],tokens=rendered['tokens'],events=rendered['events'],original_slots=len(row['tokens'])))
            for event in rendered['events']:
                if event['reason']!='unseen_unit':continue
                affected+=1;word=row['tokens'][event['slot']]
                for unit in word:
                    if unit not in book.mapping:units_count[unit]+=1
                word_types[''.join(word)]+=1
                occurrences.append(dict(source_unit=row['source_unit'],slot=event['slot'],written_units=word,unseen=event['units']))
        assert canonical_hash(asdict(book))==before
        # Counterfactual reserve perturbation may change coverage but never the model.
        transfer_slots([['DIAGNOSTIC_TEST_UNSEEN_UNIT']]*7,book)
        assert canonical_hash(asdict(book))==before and book.training_sha256==training_digest
        entry=dict(source=name,cell=cell,original_slots=total,affected_slots=affected,baseline_unknown_slots=baseline_unknown,known_slots=total-affected-baseline_unknown,
                   affected_fraction=affected/total if total else None,unseen_occurrences=dict(units_count),unseen_types=[unit_name(u) for u in sorted(units_count)],
                   primary_status='NOT_ESTIMABLE_FULL_TRANSFER' if affected else 'PASS',
                   training_sha256=book.training_sha256,codebook_sha256=before,baseline_mapping_unchanged=True,reserve_perturbation_changes_codebook=False)
        if reference is None:reference=dict(**entry,occurrences=occurrences,affected_written_forms=dict(word_types))
        else:assert entry['unseen_occurrences']==reference['unseen_occurrences'] and affected==reference['affected_slots']
        results.append(entry);masks.append(dict(source=name,cell=cell,views=views))
    return results,masks,reference

def run():
    assert not (ROOT/'FREEZE.json').exists()
    p=json.loads((ROOT/'TRANSFER-DIAGNOSTIC-PLAN-v2.json').read_text());assert all(sha(ROOT/n)==h for n,h in p['files'].items())
    targets=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text());cells=json.loads((ROOT/'CELLS.json').read_text())
    baseline=json.loads((ROOT/'LANGUAGE-MAPPING-CONTROLS.json').read_text())
    results=[];masks=[];references=[];sizes=[]
    for language in ('Latin','Italian','German','Czech','Occitan'):
        units,parts,dev,rows=language_data(language)
        expected={r['cell']:r for r in baseline if r['language']==language}
        rr,mm,reference=diagnose_one(language,dev,rows,targets,expected);results+=rr;masks+=mm;references.append(reference)
        for part,data in parts.items():
            runs=source_runs(units,data['units'],language)
            longest=max((len(r['tokens']) for r in runs),default=0)
            for cell in cells:
                required=cell['known_words']+cell['unknown_slots']
                sizes.append(dict(language=language,partition=part,cell='-'.join((cell['currier'],cell['scribe'],cell['reading'])),
                    required_original_slots=required,readable_only_count=cell['known_words'],available_aggregate_slots=data['words'],longest_same_work_run=longest,
                    eligible_start_positions=sum(max(0,len(r['tokens'])-required+1) for r in runs),
                    status='SUPPORTED_AT_SIZE' if longest>=required else 'SOURCE_TOO_SHORT',
                    admitted_for_generation=part=='development' and longest>=required))
    real=json.loads((ROOT/'REAL-LATIN-ROWS.json').read_text());selection=json.loads((ROOT/'SOURCE-CONTROL-SELECTION.json').read_text())
    dev=[s['units'] for r in real if r['manuscript'] in selection['Latin_development'] for s in r['slots'] if s['units'] is not None]
    rows=[dict(source_unit=r['page']+':'+r['block']+':'+r['line'],tokens=[s['units'] for s in r['slots']]) for r in real if r['manuscript']=='Phi_10a135']
    expected={r['cell']:r for r in json.loads((ROOT/'REAL-LATIN-MAPPING.json').read_text()) if r['view']=='development-map-transfer'}
    rr,mm,reference=diagnose_one('Real_Latin_14c',dev,rows,targets,expected);results+=rr;masks+=mm;references.append(reference)
    save(ROOT/'UNSEEN-UNIT-DIAGNOSIS.json',references);save(ROOT/'TRANSFER-CELL-STATUS.json',results)
    save(ROOT/'BARRIER-PRESERVING-RESERVE-VIEWS.json',masks);save(ROOT/'CONTIGUOUS-SOURCE-SUPPORT.json',sizes)
    prior_splits=json.loads((ROOT/'SOURCE-SPLIT.json').read_text())
    save(ROOT/'RESERVE-EXPOSURE-LEDGER.json',dict(status='EXPOSED_DIAGNOSTIC_SOURCES_NOT_UNTOUCHED',
        quarantined=['REAL-LATIN-MAPPING.json primary-representation maps use reserve distribution; descriptive only, not transfer proof.',
                     'GENERATOR-QUALIFICATION.json Macer fixture draws use old final40% source sections, overlapping later calibration/reserve partitions; these historical mapping fits cannot initialize frozen transfer.'],
        current_fitting='Only pre-existing development streams; exact mapping equality verified to frozen development baselines.',
        unknown_normalization_changed=False,reserve_used_to_expand_inventory=False,reserve_frequencies_used_to_fit=False,
        prior_Macer_qualification_split=prior_splits))
    summary=dict(status='UNSEEN_UNITS_DIAGNOSED_POLICIES_SETTLED',source_gaps={r['source']:dict(original_slots=r['original_slots'],affected_slots=r['affected_slots'],unseen_types=len(r['unseen_types'])) for r in references},
        full_reserve_statuses=dict(Counter(r['primary_status'] for r in results)),
        development_size_statuses=dict(Counter(r['status'] for r in sizes if r['partition']=='development')),
        all_partition_size_statuses=dict(Counter(r['status'] for r in sizes)),
        old_gap_counts_not_independent='Same source gaps repeat across10 inventories; no multiplication into independent source evidence.',
        development_maps_reproduce_frozen_baseline=True,codebook_perturbation_invariance=True,
        H3='UNRESOLVED',held_scoring=False,recovery_executed=False,plan_sha256=sha(ROOT/'TRANSFER-DIAGNOSTIC-PLAN-v2.json'))
    save(ROOT/'TRANSFER-DIAGNOSTIC-RESULTS.json',summary);print(json.dumps(summary))

if __name__=='__main__':{'plan':plan,'run':run}[sys.argv[1]]()
