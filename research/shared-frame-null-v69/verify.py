from pathlib import Path
import collections,hashlib,json,re
import numpy as np
from engine import frames
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');raw=load(P/'frequency-atlas-v48/rows.json');lookup={(r[0],r[6]):r for r in raw}
for name,h in load(R/'FREEZE.json').items():
 p=R/name if name in ['engine.py','run.py'] else P/name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
for tr,o in d['observed'].items():
 for mid,m in o['members'].items():
  assert m['count']==len(m['events']) and m['folios']==len({e['folio'] for e in m['events']})
  for ev in m['events']:
   ws=lookup[(tr,ev['locator'])][7];i=ev['ordinal']-1
   assert ev['tokens']==ws and ws[i-1:i+2]==['shedy',mid,'shedy']
 T=sum(m['count'] for m in o['members'].values());Rcount=sum(m['folios']>=2 for m in o['members'].values())
 for p in [p for p in d['panels'] if p['reading']==tr]:
  arr=np.load(R/(tr+'-'+p['mode']+'-null.npz'));scores,maxima=arr['scores'],arr['maxima']
  assert scores.shape==maxima.shape==(1999,2) and np.all(maxima>=scores)
  assert [x['observed'] for x in p['results']]==[T,Rcount]
  for j,x in enumerate(p['results']):
   assert x['p_raw']==(1+int(np.sum(scores[:,j]>=x['observed'])))/2000
   assert x['p_all_frames_max']==(1+int(np.sum(maxima[:,j]>=x['observed'])))/2000
   assert x['p_eight_panels']==min(1,x['p_all_frames_max']*8)
   assert x['null_mean']==float(scores[:,j].mean())
   assert x['null_95']==[float(v) for v in np.quantile(scores[:,j],[.025,.975])]
 # Verify original discovered middle-word subset without forcing old restricted totals.
 prior=next(g for g in load(P/'neighbor-patterns-v66/RESULTS.json')['groups'] if g['id']=='bath')['readings'][tr]
 old=next(f for f in prior['external_shared_frames'] if f['left']==f['right']=='shedy')
 for w,p in old['members'].items():assert o['members'][w]['count']==p['count'] and o['members'][w]['folios']==p['folios']
 assert sum(x['count'] for x in old['members'].values())==8
 # Independent dictionary enumeration of complete observed target frames.
 ref=collections.defaultdict(list)
 allowed=[r for r in raw if r[0]==tr and tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0]!='f75']
 otherloc={r[6] for r in raw if r[0]!=tr and tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0]!='f75'}
 for r in allowed:
  if r[6] not in otherloc:continue
  for i in range(len(r[7])-2):
   if r[7][i]==r[7][i+2]=='shedy' and r[7][i+1] is not None:ref[r[7][i+1]].append(r[6])
 assert {w:len(locs) for w,locs in ref.items()}=={w:m['count'] for w,m in o['members'].items()}
v=load(R/'VERIFICATION.json');v.update(saved_null_numerical_replay='all four matrices/all eight tests pass',source_tokens_and_frame_counts='pass',original_v66_subset_counts='preserved; all-middle expansion explicitly documented',independent_observed_target_enumeration='pass',browser_visual_review='not performed; prior local-file policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
print('Source enumeration, prior subset, and all eight saved-null results verified.')
