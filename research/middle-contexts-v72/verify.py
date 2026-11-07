from pathlib import Path
import collections,hashlib,json
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');rows=load(P/'frequency-atlas-v48/rows.json');raw={(r[0],r[6]):r for r in rows}
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n=='run.py' else P/n).read_bytes()).hexdigest()==h
checked=0
for tr,x in d['readings'].items():
 for word,p in x['profiles'].items():
  assert p['retained']==len(p['events'])==sum(p['positions'].values())==sum(z['count'] for z in p['folio_profiles'].values())
  assert p['total_before_exclusion']==p['retained']+len(p['excluded_frame_centers'])
  for e in p['events']+p['excluded_frame_centers']:
   ws=raw[(tr,e['locator'])][7];i=e['ordinal']-1;assert ws==e['tokens'] and ws[i]==word;checked+=1
  assert all(not(e['left']==e['right']=='shedy') for e in p['events'])
  assert all(e['left']==e['right']=='shedy' for e in p['excluded_frame_centers'])
  for scope in ['all_positions','interior_only']:
   ev=[e for e in p['events'] if scope=='all_positions' or e['position']=='interior'];s=p[scope];assert len(ev)==s['events']
   for side in ['left','right']:
    assert sum(n['count'] for n in s['sides'][side]['known'])+sum(s['sides'][side]['unknown_or_edge'].values())==len(ev)
    for n in s['sides'][side]['known']:
     es=[e for e in ev if e[side]==n['word']];assert n['count']==len(es) and n['folios']==len({e['folio'] for e in es})
 for f in x['shared_frames']:
  assert not(f['left']==f['right']=='shedy')
  for word,p in f['members'].items():
   es=[e for e in x['profiles'][word]['events'] if (e['left'],e['right'])==(f['left'],f['right'])]
   assert p['count']==len(es) and p['folios']==len({e['folio'] for e in es})
 # Cross-stratum appendix must reproduce the primary bath profile without pooling.
 s=next(s for s in d['cross_stratum_inventory'] if (s['section'],s['hand'],s['variety'],s['format'])==('Balneological','2','B','P'))
 for word,p in x['profiles'].items():assert s['readings'][tr][word]['count']==p['retained'] and s['readings'][tr][word]['positions']==p['positions']
v=load(R/'VERIFICATION.json');v.update(exact_source_events_including_exclusions=checked,neighbor_and_position_conservation='pass',same_frame_center_exclusion='pass',shared_frame_source_counts='pass',stratum_appendix_primary_match='pass')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print('All source events, exclusions, neighbour totals and stratum separation verified.')
