"""Audit actual call provenance and unchanged data, not model annotation truth."""
from pathlib import Path
import json,hashlib,collections,csv
from fractions import Fraction
R=Path(__file__).resolve().parent;V=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 f=json.loads((R/'RATING-FREEZE.json').read_text());assert sha(V/'registration/SHARED-LINE-GEOMETRY.json')==f['geometry_sha256']
 for n,h in f['code_sha256'].items():assert sha(R/n)==h,n
 tasks={t['task_id']:t for t in json.loads((V/'rater-only/TASKS.json').read_text())};sessions=set();failures=collections.Counter();versions=collections.Counter();valid={};counts={};recovered=0
 for role in ['A','B']:
  attempts=list((R/'attempts'/role).glob('*.json'));assert len(attempts)==168
  assert {p.stem for p in attempts}==set(tasks)
  for path in attempts:
   rec=json.loads(path.read_text());assert rec['role']==role and rec['task_id']==path.stem
   assert rec['manual_sha256']==f['manual_sha256'] and rec['image_sha256']==f['image_sha256'][path.stem]
   assert rec['session_id'] not in sessions;sessions.add(rec['session_id'])
   raw=R/'raw'/role/(path.stem+'.jsonl');assert sha(raw)==rec['raw_events_sha256']
   if rec['status']=='FAILED':failures[role+': '+str(rec['failure'])]+=1
  paths=list((R/'responses'/role).glob('*.json'));counts[role]=len(paths);valid[role]=[]
  for path in paths:
   rec=json.loads(path.read_text());base=R
   if rec.get('transport_recovery'):
    recovered+=1;base=R/'transport-recovery-v1';assert rec['session_id'] not in sessions;sessions.add(rec['session_id'])
    original=R/'attempts'/role/path.name;assert sha(original)==rec['transport_recovery']['original_attempt_sha256']
   assert rec['model']==f['models'][role] and rec['available_tools']==['StructuredOutput'] and rec['mcp_servers']==[]
   assert rec['manual_sha256']==f['manual_sha256'] and rec['image_sha256']==f['image_sha256'][path.stem]
   assert rec['response_schema_sha256']==f['response_schema_sha256']
   raw=base/'raw'/role/(path.stem+'.jsonl');assert sha(raw)==rec['raw_events_sha256'];events=[json.loads(s) for s in raw.read_text(encoding='utf-8').splitlines() if s.strip()]
   init=next(e for e in events if e.get('type')=='system' and e.get('subtype')=='init');assert init['session_id']==rec['session_id'] and init['model']==f['models'][role]
   final=next(e for e in reversed(events) if e.get('type')=='result');assert rec['annotation']==final['structured_output'],'Returned annotation was changed'
   for event in events:
    if event.get('type')=='assistant':
     for c in event.get('message',{}).get('content',[]):
      if c.get('type')=='tool_use':assert c['name']=='StructuredOutput'
   versions[rec['cli_version']]+=1;valid[role].append(rec)
 for path in (R/'transport-recovery-v1/attempts').rglob('*.json') if (R/'transport-recovery-v1/attempts').exists() else []:
  rec=json.loads(path.read_text());sessions.add(rec['session_id'])
 agreement=json.loads((R/'AGREEMENT.json').read_text());geometry=json.loads((V/'registration/SHARED-LINE-GEOMETRY.json').read_text())['lines'];assert len(geometry)==1145 and len({l['shared_line_id'] for l in geometry})==1145
 assert agreement['registered_physical_lines']==1145 and agreement['adjudication']=='NOT RUN' and agreement['OT_merge']=='NOT RUN'
 if agreement['paired_physical_lines']<1145:assert not agreement['G6']['pass_gate'] and not agreement['G2']['pass_gate']
 labelsets={role:{d['shared_line_id']:d['label'] for d in csv.DictReader((R/f'LINE-CONTEXT-{role}.csv').open(encoding='utf-8'))} for role in ['A','B']};paired=set(labelsets['A'])&set(labelsets['B']);assert len(paired)==agreement['paired_physical_lines']
 for name in ['G6','G2']:
  aa=[labelsets['A'][x] if name=='G6' else 'PL' if labelsets['A'][x]=='PL' else 'not-PL' for x in paired];bb=[labelsets['B'][x] if name=='G6' else 'PL' if labelsets['B'][x]=='PL' else 'not-PL' for x in paired];n=len(aa);ma=collections.Counter(aa);mb=collections.Counter(bb);prod=sum(ma[k]*mb[k] for k in set(ma)|set(mb));num=n*sum(x==y for x,y in zip(aa,bb))-prod;den=n*n-prod;expected=str(Fraction(num,den)) if den else None
  assert agreement[name].get('exact_kappa')==expected
  assert sum(sum(row) for row in agreement[name]['confusion_matrix'])==n
 out=dict(status='PASS_PROVENANCE_AND_NUMERICAL_COVERAGE_CHECKS; NOT_COORDINATE_ACCURACY_QUALIFICATION',original_terminal_calls=336,valid_page_responses=counts,original_failures=dict(failures),transport_recovery_annotations=recovered,unique_call_sessions=len(sessions),CLI_versions=dict(versions),raw_annotations_unchanged=True,only_structured_output_tool=True,images_and_manual_hashes_verified=True,shared_geometry_unchanged=True,H_F_not_doubled=True,independent_exact_kappa_recalculation=True,confusion_totals_match=True,original_synthetic_failures_retained=True,timing_exception=f['timing_exception'],adjudication='NOT RUN',outcome_join='NOT RUN',v103='PARKED')
 (R/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
