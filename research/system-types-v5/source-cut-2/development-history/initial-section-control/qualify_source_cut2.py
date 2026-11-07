"""Development support/capacity qualification only; fresh reserves and S_held stay inaccessible."""
import json
from collections import Counter
from pathlib import Path
from core import sha,load_evt,panels
from sandbox import DATA
from source_cut2 import CUT,ROOT,dump,load_cut2_development,validate_selection
from source_contract import load_development_corpus,produce_from_development
from transfer_policy import fit_development_codebook
from source_controls import parse_alto

def main():
    assert not (ROOT/'FREEZE.json').exists();plan=validate_selection()
    files=['SELECTION.json','DEVELOPMENT-SEAL.json','DEVELOPMENT-UNITS.json','ABBREVIATED-LATIN-ROWS.json','JAUFRE-LINES.json','JAUFRE-PROVENANCE.json']
    owners=['source_cut2.py','qualify_source_cut2.py','source_contract.py','transfer_policy.py','registry.py','GENERATORS/__init__.py','core.py','source_controls.py']
    path=CUT/'QUALIFICATION-PLAN.json'
    if not path.exists():dump(path,dict(tier='development qualification, NOT claim FREEZE',files={n:sha(CUT/n) for n in files},owners={n:sha(ROOT/n) for n in owners},
        scope='Known-unit attestation;60development-only codebook capacity checks (5language+realLatin x10EVA inventories);22previously size-rejected source-entrypoint generations using original geometry. No reserve transfer, no H1-H8, no model survival.',
        seed=82001,H3='UNRESOLVED',held_scoring=False))
    sealed=json.loads(path.read_text());assert all(sha(CUT/n)==h for n,h in sealed['files'].items());assert all(sha(ROOT/n)==h for n,h in sealed['owners'].items())
    assert not any('Latin16195' in str(p) for p in (CUT/'development').rglob('*'))
    units=json.loads((CUT/'DEVELOPMENT-UNITS.json').read_text());inventories=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text());mapping=[];evidence=[]
    for lang in ('Latin','Italian','German','Czech','Occitan'):
        prior=load_development_corpus(ROOT,lang)
        words=[w for _,_,tokens in prior.runs for w in tokens if w is not None]
        new=[u for u in units if u['language']==lang]
        words += [w for u in new for w in u['words'] if w is not None]
        for cell,inventory in inventories.items():
            try:
                book=fit_development_codebook(words,inventory,'development')
                mapping.append(dict(source=lang,cell=cell,status='PASS',training_sha256=book.training_sha256,target_inventory_sha256=book.target_inventory_sha256,mapping=dict(book.entries),prior_development_sha256=prior.development_sha256,new_development_units=[u['unit'] for u in new]))
            except ValueError as error:mapping.append(dict(source=lang,cell=cell,status='CAPACITY_ABSTAIN',reason=str(error)))
        wanted={'Italian':['\u00e4','x'],'Czech':['w'],'Occitan':['\u00e7']}.get(lang,[])
        for u in new:
            for i,w in enumerate(u['words']):
                hit=sorted(set(w or '')&set(wanted))
                if hit:evidence.append(dict(language=lang,work=u['work'],unit=u['unit'],slot=i,written_word=w,units=hit,source_path=u['source_path'],source_sha256=u['source_sha256']))
    # Earlier known development medical manuscripts remain explicitly identified.
    rows=json.loads((CUT/'ABBREVIATED-LATIN-ROWS.json').read_text())
    for ms in ('H318','CLM13027'):
        for path in sorted((ROOT/'SOURCES/cremma-lat/data'/ms).glob('*.chocomufin.xml')):
            rows+=parse_alto(path,ms)[0]
    words=[s['units'] for row in rows for s in row['slots'] if s['units'] is not None]
    for cell,inventory in inventories.items():
        try:
            book=fit_development_codebook(words,inventory,'development')
            mapping.append(dict(source='AbbreviatedLatin',cell=cell,status='PASS',training_sha256=book.training_sha256,target_inventory_sha256=book.target_inventory_sha256,mapping=dict(book.entries),manuscripts=sorted(set(r['manuscript'] for r in rows))))
        except ValueError as error:mapping.append(dict(source='AbbreviatedLatin',cell=cell,status='CAPACITY_ABSTAIN',reason=str(error)))
    dump(CUT/'DEVELOPMENT-CODEBOOKS.json',mapping);dump(CUT/'LANGUAGE-GAP-EVIDENCE.json',evidence)
    oldcases=json.loads((CUT/'SEVEN-SHORT-SOURCE-CASES.json').read_text());rows,_=load_evt(DATA/'text16e6.original.evt',DATA/'Davis-hands.original.csv');geometry={'-'.join(k):[len(r['tokens']) for r in v] for k,v in panels(rows).items()};trials=[]
    for case in oldcases:
        lang=case['language'];corpus=load_cut2_development(lang)
        for family in (('G1','G2','G3','G4') if lang=='Latin' else ('G1',)):
            generated=produce_from_development(family,{},82001,corpus=corpus,inventory=inventories[case['cell']],line_lengths=geometry[case['cell']])
            assert [len(line) for line in generated['lines']]==geometry[case['cell']]
            receipt=generated['source_receipt'];assert receipt['source_wraps']==0 and receipt['stop']-receipt['start']==case['required_slots']
            trials.append(dict(language=lang,cell=case['cell'],family=family,status='PASS',source_receipt=receipt))
    dump(CUT/'SOURCE-ENTRYPOINT-TRIALS.json',trials)
    summary=dict(status='INDEPENDENT_DEVELOPMENT_CUT_QUALIFIED_CLAIM_LOCKED',known_gap_inventory_coverage=all(not d['uncovered'] for d in json.loads((CUT/'DEVELOPMENT-INVENTORY.json').read_text()).values()),
        source_size_cases=len(oldcases),source_size_supported=sum(c['status']=='SUPPORTED_AT_SIZE' for c in oldcases),source_entrypoint_trials=len(trials),
        development_codebook_trials=len(mapping),development_codebook_statuses=dict(Counter(r['status'] for r in mapping)),
        fresh_reserve_bodies_read=0,reserve_transfer_qualification='NOT_RUN',reserve_used_for_fitting=False,
        old_cut_results='retained unchanged; new coverage does not retroactively pass old controls',
        limitations=['Latin long-source evidence is nonmedical political prose.','Jaufre broadens Occitan dialect/register; not Gascon legal replication.','Purgatorio/Paradiso share Dante/Commedia with Inferno; section independence only.','Latin diplomatic manuscripts include later/genre strata; identical marks do not establish identical functions.','Alphabet coverage of exposed old gaps does not predict fresh-reserve coverage.'],
        H3='UNRESOLVED',held_scoring=False,recovery_executed=False,qualification_plan_sha256=sha(CUT/'QUALIFICATION-PLAN.json'))
    dump(CUT/'RESULTS.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
