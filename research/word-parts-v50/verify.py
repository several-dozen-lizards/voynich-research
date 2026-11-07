import json,importlib.util,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('run',R/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert 'internal:od' in m.feats('qody')
assert 'internal:od' not in m.feats('ody') and 'internal:od' not in m.feats('qod')
assert {'word:qody','prefix:qody','suffix:qody','prefix:q','suffix:y'}<=m.feats('qody')
assert len(m.feats('a'))==3
r=json.loads((R/'RESULTS.json').read_text());a=json.loads((R/'FAMILY-AUDIT.json').read_text())
for p in r['results']:
 for f in p['features']:assert 0<=f['rate_a']<=1 and 0<=f['rate_b']<=1 and 0<=f['p_family']<=1
for x in a:
 sets=[set(f['test_folios']) for f in x['folds']]
 assert not any(sets[i]&sets[j] for i in range(3) for j in range(i))
 assert all(f['heldout']['difference_pp'] is not None for f in x['folds'])
for x in a[::2]:
 y=next(y for y in a if y['feature']==x['feature'] and y['tr']=='F')
 assert [f['test_folios'] for f in x['folds']]==[f['test_folios'] for f in y['folds']]
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
(R/'VERIFICATION.json').write_text(json.dumps({'boundary_fixtures':'pass','rates_and_p_ranges':'pass','disjoint_folio_folds':'pass','same_H_F_folds':'pass','freeze_integrity':'pass','visual_review':'not performed','interpretation':'retrospective stability, not untouched validation'},indent=2))
print('Verification passed')
