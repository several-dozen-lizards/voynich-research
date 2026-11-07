"""Post-freeze exposure diagnostic only. Never changes the consensus rule."""
from pathlib import Path
import importlib.util,json,csv
P=Path(__file__).parent;ROOT=P.parent
s=importlib.util.spec_from_file_location('support',P/'resolve_support.py');mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
base=ROOT/'continuation-v73-wrap-ratings-bc-2026-10-25/ratings'
labels={}
for role in ('A','B'):
 with (base/f'LINE-CONTEXT-{role}-COMPLETED.csv').open(encoding='utf-8',newline='') as f:labels[role]={r['shared_line_id']:r['label'] for r in csv.DictReader(f)}
masks=json.loads((P/'READABILITY-MASKS.json').read_text(encoding='utf-8'))['rows'];wrap={r['shared_line_id']:r for r in json.loads((ROOT/'continuation-v73-wrap-ratings-bc-2026-10-25/wrap/WRAP-FLAGS.json').read_text(encoding='utf-8'))['rows']}
out={}
for reading in ('H','F'):
 out[reading]={}
 for role in ('A','B'):
  rows=[dict(id=r['id'],folio=r['folio'],label=labels[role][r['id']],length_bin=wrap[r['id']]['length_bin'],n=sum(r['noninitial_mask'])) for r in masks if r['reading']==reading and r['available']]
  out[reading][role]=mod.design(rows)
receipt=dict(status='EXPOSURE_DIAGNOSTIC_ONLY; NOT A LABEL_RULE_CANDIDATE_OR_RESCUE',frozen_consensus_unchanged=True,real_feature_counts_used=False,diagnostic=out)
(P/'RATER-ONLY-SUPPORT-DIAGNOSTIC.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({reading:{r:{'eligible_folios':d['informative_folios'],'gate':d['design_gate']} for r,d in rr.items()} for reading,rr in out.items()}))
