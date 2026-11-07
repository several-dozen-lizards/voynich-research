from pathlib import Path
import json
R=Path(__file__).resolve().parent;P=R.parent
data=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'));rows=json.loads((P/'frequency-atlas-v48/rows.json').read_text(encoding='utf-8'))
locs={e['locator'] for d in data['readings'].values() for p in d['profiles'].values() for e in p['events']}
bank={tr:{r[6]:r[7] for r in rows if r[0]==tr and r[6] in locs} for tr in ['H','F']}
(R/'source-lines.js').write_text('const SOURCE_LINES = '+json.dumps(bank,ensure_ascii=False)+';',encoding='utf-8')
print(json.dumps({'source_loci':len(locs),'strata':len(data['cross_stratum_inventory'])}))
