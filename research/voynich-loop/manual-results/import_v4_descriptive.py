from pathlib import Path
import sys,copy,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from loop import Store,filehash,utc
R=Path(__file__).resolve().parents[1];P=R.parent
items=[('D-v4.2-C',P/'v4-2-C-odds-ratio-map','descriptive','COMPLETED'),('D-v4.2-C2',P/'v4-2-C2-predictive','descriptive','COMPLETED'),('I-v4.3-qok-rate',P/'image-qok-rate-v4-3','infrastructure','DESIGN_FROZEN_JOIN_BLOCKED')]
store=Store(R)
with store.lock():
 s,h,n=store.load();store.audit(s);assert s['mode']=='STAGED'
 changed=False
 for id,folder,tier,result in items:
  files=['PROTOCOL.json','RESULTS.json','VERIFICATION.json','FINDINGS.md'] if tier=='descriptive' else ['PROTOCOL.json','FINAL-SEAL.json','QUALIFICATION.json','BOOTSTRAP-QUALIFICATION.json']
  evidence={str(folder/f):filehash(folder/f) for f in files};store.evidence(evidence)
  found=next((e for e in s['entries'] if e['id']==id),None)
  if found:
   assert found['evidence']==evidence;continue
  s['entries'].append(dict(id=id,tier=tier,result=result,evidence=evidence,retrospective=True,held_up=False,alpha_spent=0,lead='sh-qok-context-structure',related_manual_look=(tier=='descriptive'),utc=utc(),authority='User authorized these manual analyses/design; neither autonomous execution nor claim promotion is authorized.'))
  changed=True
 if changed:
  for task in s['queue']:
   if task['id']=='v4.2-C':
    task.update(status='COMPLETE',reason='Separate manual retrospective OR map completed; original primaries preserved.',sources={str(P/'v4-2-C-odds-ratio-map/PROTOCOL.json'):filehash(P/'v4-2-C-odds-ratio-map/PROTOCOL.json'),str(P/'v4-2-C-odds-ratio-map/VERIFICATION.json'):filehash(P/'v4-2-C-odds-ratio-map/VERIFICATION.json')})
  for id,folder,tier,status,reason in [('v4.2-C2',P/'v4-2-C2-predictive','descriptive','COMPLETE','Manual grouped conditional predictive comparison completed; no equivalence declaration.'),('v4.3-qok-rate',P/'image-qok-rate-v4-3','infrastructure','BLOCKED','Design and synthetic implementation qualified; source-owner pre-join timing/cohort receipt absent. No image/text join authorized.')]:
   if not any(t['id']==id for t in s['queue']):s['queue'].append(dict(id=id,tier=tier,status=status,reason=reason,sources={str(folder/'PROTOCOL.json'):filehash(folder/'PROTOCOL.json')},priority=0,expected_information=None,cost=None,ranking='Administrative manual-completion record; no prospective dispatch ranking.'))
  store.commit(s,'import_manual_v4_descriptive_results_and_blocked_image_design',h,n)
 print(json.dumps(dict(mode=s['mode'],entries=[dict(id=e['id'],tier=e['tier'],result=e['result'],held_up=e['held_up']) for e in s['entries']],vault_closed=True),indent=2))
