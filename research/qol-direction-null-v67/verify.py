from pathlib import Path
import collections,hashlib,json
import numpy as np
from engine import calibrate,subsets
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');old=load(P/'neighbor-patterns-v66/FORM-PAIR-SUPPLEMENT.json')
# Independent direct-comparison check of pooled ranks, ties, subsets and minP.
toy=np.array([[2,-1,0],[1,1,0],[0,-2,1],[2,0,-1],[-1,2,1]],dtype=np.int32)
toysets=subsets(3);toyvalues=[toy[:,s].sum(axis=1) for s in toysets]
tails=[np.array([min(np.mean(v>=z),np.mean(v<=z)) for z in v]) for v in toyvalues]
rowmin=np.min(tails,axis=0)
for calc,v,t in zip(calibrate(toy,toysets),toyvalues,tails):
 assert calc['p_upper']==np.mean(v>=v[0]) and calc['p_lower']==np.mean(v<=v[0])
 assert calc['p_search_family']==np.mean(rowmin<=t[0]+1e-14)
for name,digest in load(R/'FREEZE.json').items():
 p=R/name if name in ('engine.py','run.py') else P/name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
for panel in d['panels']:
 scores=np.load(R/(panel['reading']+'-'+panel['mode']+'-null.npz'))['pair_scores']
 assert scores.shape==(2000,len(panel['pairs']))
 replay=calibrate(scores,subsets(len(panel['pairs'])))
 for r,v in zip(panel['records'],replay):
  assert all(r[k]==value for k,value in v.items())
  assert r['p_four_panels']==min(1,4*r['p_search_family'])
 assert sum(panel['noticed_folio_D'].values())==panel['noticed_result']['observed']
 for pair in [('qokedy','kedy'),('qokeedy','keedy')]:
  i=panel['pairs'].index(list(pair));cells=panel['cells'][i]
  ref=next(p for p in old['pairs'] if p['anchor']=='qol' and p['reading']==panel['reading'] and (p['prefixed'],p['base'])==pair)
  assert all(cells[key]==ref[key]['count'] for key in cells)
 # Every source event contributes exactly the direction indicated by its neighbours.
 evsum=sum((1 if e['left'] in ('qokedy','qokeedy') else -1 if e['left'] in ('kedy','keedy') else 0)+(1 if e['right'] in ('kedy','keedy') else -1 if e['right'] in ('qokedy','qokeedy') else 0) for e in panel['noticed_events'])
 assert evsum==panel['noticed_result']['observed']
v=load(R/'VERIFICATION.json');v.update(numerical_replay='all four saved matrices reproduce every p-value',independent_small_matrix_rank_and_minP_check='pass',original_cells='match v66 supplement',folio_and_source_event_D_conservation='pass',frozen_inputs_and_methods='pass',report_scope='retrospective conditional form test; no semantic inference')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
print('All four score matrices replayed; original counts and source/folio contributions match.')
