"""Representation and no-wrap size controls for acquired language sources."""
from pathlib import Path
import json,sys
from collections import Counter
from core import save,sha,group_rank_mapping,render_groups

ROOT=Path(__file__).resolve().parent

def plan():
    path=ROOT/'SOURCE-COVERAGE-PLAN.json'
    if path.exists():raise FileExistsError(path)
    files=['core.py','qualify_source_coverage.py','SOURCE-INVENTORY.json','LANGUAGE-SOURCE-SPLITS.json','CELLS.json','EVA-GROUP-INVENTORIES.json']
    files += [f'{lang}-SOURCE-UNITS.json' for lang in ('LATIN','GERMAN','ITALIAN','CZECH','OCCITAN')]
    save(path,dict(tier='sandbox',H1_H8=False,policy='All development words establish the source unit inventory; no spelling/diacritic merging. Transfer first1000 available reserve words; unseen-unit words abstain with every unit recorded. Ten separate target inventories. No source wrap or padding. Size adequacy per source partition and manuscript cell.',
        files={n:sha(ROOT/n) for n in files}))

def run():
    assert not (ROOT/'FREEZE.json').exists()
    plan=json.loads((ROOT/'SOURCE-COVERAGE-PLAN.json').read_text());assert all(sha(ROOT/n)==h for n,h in plan['files'].items())
    sources=json.loads((ROOT/'SOURCE-INVENTORY.json').read_text());splits=json.loads((ROOT/'LANGUAGE-SOURCE-SPLITS.json').read_text())
    targets=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text());cells=json.loads((ROOT/'CELLS.json').read_text())
    maps=[];sizes=[]
    for language,record in sources.items():
        units=json.loads((ROOT/(language.upper()+'-SOURCE-UNITS.json')).read_text())
        groups={part:set(data['units']) for part,data in splits[language].items()}
        dev=[list(w) for u in units if u['unit'] in groups['development'] for w in u['words']]
        reserve=[list(w) for u in units if u['unit'] in groups['reserve'] for w in u['words']][:1000]
        for cell,target in targets.items():
            try:
                receipt=group_rank_mapping(dev,target)
                unknown=sorted({u for w in reserve for u in w if u not in receipt['mapping']})
                admitted=[w for w in reserve if all(u in receipt['mapping'] for u in w)]
                rendered=render_groups(admitted,receipt)
                maps.append(dict(language=language,cell=cell,development_mapping='PASS',transfer='PASS' if not unknown else 'UNSEEN_UNITS_ABSTAIN',
                    unknown_units=unknown,reserve_sample_words=len(reserve),reserve_words_mapped=len(rendered['words']),receipt=receipt))
            except ValueError as error:maps.append(dict(language=language,cell=cell,development_mapping='CAPACITY_ABSTAIN',reason=str(error)))
        for cell in cells:
            size=cell['known_words'];parts={part:data['words']>=size for part,data in splits[language].items()}
            sizes.append(dict(language=language,cell='-'.join((cell['currier'],cell['scribe'],cell['reading'])),target_readable_tokens=size,
                 full_source_tokens=record['words'],full_source_no_wrap=record['words']>=size,source_part_no_wrap=parts))
    save(ROOT/'LANGUAGE-MAPPING-CONTROLS.json',maps);save(ROOT/'SOURCE-SIZE-CONTROLS.json',sizes)
    result=dict(status='SOURCE_REPRESENTATION_CONTROLS_COMPLETE',development_maps=dict(Counter(m['development_mapping'] for m in maps)),
        transfer=dict(Counter(m.get('transfer','NOT_ATTEMPTED') for m in maps)),
        full_source_no_wrap_supported=sum(s['full_source_no_wrap'] for s in sizes),size_checks=len(sizes),
        partition_size_failures=sum(not value for s in sizes for value in s['source_part_no_wrap'].values()),
        H3='UNRESOLVED',held_scoring=False,real_G2_survival='NOT_RUN',plan_sha256=sha(ROOT/'SOURCE-COVERAGE-PLAN.json'),
        note='Transfer abstention and insufficient reserved source length are retained controls, not rejected production families.')
    save(ROOT/'SOURCE-COVERAGE-RESULTS.json',result);print(json.dumps(result))

if __name__=='__main__':{'plan':plan,'run':run}[sys.argv[1]]()
