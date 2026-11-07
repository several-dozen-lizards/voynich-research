from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;P=R.parent
d=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'));rows=json.loads((P/'frequency-atlas-v48/rows.json').read_text(encoding='utf-8'))
locs=set()
for g in d['groups']:
 for tr,x in g['readings'].items():
  locs.update(e['locator'] for e in x['events'])
  for f in x['external_shared_frames']:locs.update(f['locators'])
sources={tr:{r[6]:r[7] for r in rows if r[0]==tr and r[6] in locs} for tr in ('H','F')}
(R/'source-lines.js').write_text('const SOURCE_LINES = '+json.dumps(sources,ensure_ascii=False)+';',encoding='utf-8')
# Retrospective descriptive supplement: inventory every observed qo + exact base pair,
# rather than just the two examples noticed in the primary output. No tests or labels.
pairs=[]
for g in d['groups']:
 for tr,x in g['readings'].items():
  inv={w['word']:w for w in x['inventory']}
  for w,profile in inv.items():
   if w.startswith('qo') and w[2:] in inv:
    pairs.append({'anchor':g['anchor'],'reading':tr,'prefixed':w,'base':w[2:],'prefixed_left':profile['left'],'prefixed_right':profile['right'],'base_left':inv[w[2:]]['left'],'base_right':inv[w[2:]]['right']})
(R/'FORM-PAIR-SUPPLEMENT.json').write_text(json.dumps({'status':'Postinspection descriptive written-form comparison; not part of frozen primary analysis. All exact qo-removal pairs present in each neighbour inventory, no inferred morphological or semantic relation.','pairs':pairs},indent=2),encoding='utf-8')
(R/'form-pairs.js').write_text('const FORM_PAIRS = '+json.dumps(pairs)+';',encoding='utf-8')
print(json.dumps({'source_loci':len(locs),'form_pairs':len(pairs),'source_sha256':hashlib.sha256((P/'frequency-atlas-v48/rows.json').read_bytes()).hexdigest()}))
