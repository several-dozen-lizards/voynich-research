"""Separate amended full-population agreement; no text join or legacy writes."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,csv,hashlib
P=Path(__file__).parent;ROOT=P.parents[1];OLD=ROOT/'image-context-v4/ratings';sys.path.insert(0,str(OLD))
from agreement import validate_response,assign,kappa,CATS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 seal=read(OLD/'AGREEMENT-FINAL-SEAL.json');changed=[]
 for group in ('files','data'):
  for rel,expected in seal[group].items():
   if sha(OLD/rel)!=expected:changed.append(rel)
 assert not changed,changed
 freeze=read(OLD/'RATING-FREEZE.json');geometry=ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json';assert sha(geometry)==freeze['geometry_sha256'];lines=read(geometry)['lines'];tasks={t['task_id']:t for t in read(ROOT/'image-context-v4/rater-only/TASKS.json')}
 additions={};selection=[]
 for phase in ('transport-repair','corners'):
  for call in read(P/phase/'CALLS.json'):
   if not call['accepted']:continue
   identity=(call['role'],call['task_id']);assert identity not in additions
   path=ROOT/call['response_path'];record=read(path);assert record['status']=='VALID' and record['model']==freeze['models'][call['role']];assert record['available_tools']==['StructuredOutput'] and record['mcp_servers']==[];validate_response(record['annotation'])
   additions[identity]=record;selection.append(dict(role=identity[0],task_id=identity[1],phase=phase,response_path=str(path.relative_to(ROOT)),response_sha256=sha(path)))
 labels={};coverage={};evidence={}
 for role in ('A','B'):
  labels[role]={};coverage[role]=0
  for line in lines:
   tid=line['task_id'];old=OLD/'responses'/role/(tid+'.json')
   if old.exists():record=read(old);origin=str(old.relative_to(ROOT))
   else:
    record=additions.get((role,tid));origin='completion:'+role+':'+tid
   if record is None:continue
   validate_response(record['annotation']);task=tasks[tid];context=assign(line,record['annotation']['pictures'],task['native_width'],task['native_height']);labels[role][line['shared_line_id']]=context;coverage[role]+=1
  with (P/f'LINE-CONTEXT-{role}-COMPLETED.csv').open('w',newline='',encoding='utf-8') as f:
   fields=['shared_line_id','label','distance_line_heights','picture_index','tie'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(dict(shared_line_id=lid,**z) for lid,z in labels[role].items())
 ids=[l['shared_line_id'] for l in lines if l['shared_line_id'] in labels['A'] and l['shared_line_id'] in labels['B']];a=[labels['A'][i]['label'] for i in ids];b=[labels['B'][i]['label'] for i in ids]
 g6=kappa(a,b,CATS);g2=kappa(['PL' if x=='PL' else 'not-PL' for x in a],['PL' if x=='PL' else 'not-PL' for x in b],['PL','not-PL']);complete=len(ids)==1145
 for g in (g6,g2):g['gate_status']='PASS' if complete and g['pass_gate'] else 'NOT RELIABLE' if complete else 'NOT ESTIMABLE: MISSING REGISTERED-LINE RATINGS';g['pass_gate']=complete and g['pass_gate']
 out=dict(status='AMENDED_COMPLETION_PRE_ADJUDICATION_AGREEMENT',registered_physical_lines=1145,paired_physical_lines=len(ids),G6=g6,G2=g2,added_role_pages=len(additions),added_line_pairs=len(ids)-912,coverage=coverage,models=freeze['models'],geometry_sha256=sha(geometry),original_agreement_sha256=sha(OLD/'AGREEMENT.json'),legacy_seal_files_verified=len(seal['files'])+len(seal['data']),legacy_changed=changed,completion_protocols=['COMPLETION-FREEZE.json','transport-repair/TRANSPORT-AMENDMENT.json','corners/COMPLETION-FREEZE.json','corners/HUMAN-AUTHORIZATION.json'],selection=selection,classification='Post-original-collection completion amendment. Original valid ratings retained; missing-slot-only collection and representation changes fully recorded. Not a backdated original gate.',coordinate_accuracy='Not scientifically qualified; format transport verification is not external annotation truth.',adjudication='NOT RUN',OT_merge='NOT RUN',T1_text_join='CLOSED',vault='CLOSED')
 (P/'AGREEMENT-COMPLETED.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:out[k] for k in ('paired_physical_lines','G6','G2','added_line_pairs','legacy_seal_files_verified','legacy_changed')},indent=2))
if __name__=='__main__':main()
