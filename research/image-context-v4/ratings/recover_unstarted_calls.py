"""One recorded serial retry only for proven no-annotation native/transport failures."""
from pathlib import Path
import json,hashlib,shutil,datetime
import collect
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def eligible(record,events,raw):
 if record.get('status')!='FAILED' or any(e.get('type')=='assistant' for e in events):return False
 if any(e.get('structured_output') for e in events):return False
 usage=record.get('provider_usage') or {}
 if any(usage.get(k,0) for k in ['input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens']):return False
 native=record.get('exit_code')==3221226505 and not events
 sharp=record.get('exit_code')==0 and 'Could not load the \\"sharp\\" module' in raw
 # JSON escaping varies; identify the exact observed pre-inference loader failure.
 sharp=sharp or record.get('exit_code')==0 and 'sharp' in raw and 'win32-x64 runtime' in raw and any(e.get('subtype')=='error_during_execution' for e in events)
 return native or sharp
def main():
 assert not (R/'AGREEMENT.json').exists(),'Do not select recovery after seeing agreement.'
 assert (R/'COLLECTION-STATUS.json').exists(),'Complete original planned pass first.'
 supplement=json.loads((R/'TRANSPORT-RECOVERY-FREEZE.json').read_text());repair=R/'TRANSPORT-RECOVERY-EXECUTION-REPAIR.json';expected=json.loads(repair.read_text())['new_code_sha256'] if repair.exists() else supplement['code_sha256'];assert sha(Path(__file__))==expected
 frozen=json.loads((R/'RATING-FREEZE.json').read_text());tasks={t['task_id']:t for t in json.loads((R.parent/'rater-only/TASKS.json').read_text())}
 dest=R/'transport-recovery-v1';dest.mkdir(exist_ok=True)
 for name in ['MANUAL-RATER.md','RESPONSE-SCHEMA.json']:shutil.copy2(R/name,dest/name)
 candidates=[]
 for role in ['A','B']:
  for path in sorted((R/'attempts'/role).glob('*.json')):
   d=json.loads(path.read_text())
   if d['status']!='FAILED':continue
   raw=(R/'raw'/role/(d['task_id']+'.jsonl')).read_text(encoding='utf-8');events=[];malformed=False
   for line in raw.splitlines():
    if not line.strip():continue
    try:events.append(json.loads(line))
    except json.JSONDecodeError:malformed=True
   if malformed:continue # Cannot certify absent semantic content in truncated/non-JSON output.
   if eligible(d,events,raw):candidates.append((role,d['task_id'],sha(path)))
 collect.R=dest;receipt=[]
 for role,tid,original_sha in candidates:
  assert not (R/'responses'/role/(tid+'.json')).exists()
  result=collect.call_one((role,tasks[tid]),frozen)
  recovered=dest/'responses'/role/(tid+'.json')
  if recovered.exists():
   record=json.loads(recovered.read_text());record['transport_recovery']=dict(original_attempt_sha256=original_sha,supplement_sha256=sha(R/'TRANSPORT-RECOVERY-FREEZE.json'),actual_annotation='First completed semantic response; no original assistant event or model tokens.');collect.save(R/'responses'/role/(tid+'.json'),record)
  receipt.append(dict(role=role,task_id=tid,original_attempt_sha256=original_sha,result=result,recovery_valid=recovered.exists()))
 collect.save(R/'TRANSPORT-RECOVERY-RECEIPT.json',dict(status='RECORDED NO_ANNOTATION_NATIVE_FAILURE_RECOVERY',calls=len(receipt),records=receipt,semantic_reratings=0,original_failures_unchanged=True))
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
