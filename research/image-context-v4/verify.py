"""Engineering checks only; no rater responses or scientific outcomes generated."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,copy,importlib.util
R=Path(__file__).resolve().parent;P=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks={};packet=R/'rater-only';tasks=json.loads((packet/'TASKS.json').read_text());assert tasks
 assert all(set(t)=={'task_id','image','native_width','native_height'} for t in tasks)
 assert len({t['task_id'] for t in tasks})==len(tasks);checks['anonymous_tasks_unique_no_text_or_results']=len(tasks)
 assert (packet/'MANUAL.md').read_bytes()==(R/'MANUAL.md').read_bytes();checks['manual_identical']=True
 key=json.loads((R/'research-only/TASK-KEY.json').read_text());reserved={'f72v1','f72v2','f73r','f73v'}
 assert not reserved.intersection(t['folio'] for t in key['tasks']);checks['reserved_excluded']=True
 receipts=json.loads((R/'research-only/IMAGE-RECEIPTS.json').read_text());ready={x['task_id']:x for x in receipts if x['status']=='READY'}
 for t in tasks:assert sha(packet/t['image'])==ready[t['task_id']]['sha256']
 checks['all_image_hashes_verified']=len(tasks)
 with zipfile.ZipFile(R/'v4-rater-only.zip') as z:
  assert set(z.namelist())=={str(p.relative_to(packet)).replace('\\','/') for p in packet.rglob('*') if p.is_file()}
  assert not any(s in n.lower() for n in z.namelist() for s in ['key','protocol','evt','score','result','legacy'])
  assert z.testzip() is None
 checks['zip_contents_and_crc']=True
 spec=importlib.util.spec_from_file_location('v4validate',R/'validate_ratings.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 # Only in-memory authored geometry; never stored as rater data.
 t=tasks[0];page=t['task_id'];sample=dict(schema='v4-blind-boxes',rater_id='ENGINEERING_ONLY',rows=[dict(page=page,kind='block',block='a',line_number=None,box=[0,0,100,100],category=None,note='fixture'),dict(page=page,kind='line',block='a',line_number=1,box=[5,5,80,10],category=None,note='fixture')])
 assert m.validate(sample)['outcomes_joined'] is False
 failures=0
 for mutate in [lambda d:d.update(rows=[]),lambda d:d['rows'][1].update(page='unknown'),lambda d:d['rows'][1].update(box=[0,0,-1,1]),lambda d:d['rows'][1].update(box=[0,0,float('nan'),1]),lambda d:d['rows'][1].update(line_number=2),lambda d:d['rows'][1].update(block='missing'),lambda d:d['rows'].append(copy.deepcopy(d['rows'][1]))]:
  d=copy.deepcopy(sample);mutate(d)
  try:m.validate(d)
  except ValueError:failures+=1
 assert failures==7;checks['authored_validator_rejections']=failures
 script=(packet/'index.html').read_text(encoding='utf-8').split('<script>')[1].split('</script>')[0];(R/'tool.syntax.js').write_text(script,encoding='utf-8')
 subprocess.run(['node','--check',str(R/'tool.syntax.js')],check=True,capture_output=True);checks['javascript_syntax']=True
 subprocess.run(['node',str(R/'verify-tool.js')],check=True,capture_output=True);checks['tool_authored_geometry_and_entry_checks']=True
 v=P/'sh-qok-context-map-v3';verification=json.loads((v/'VERIFICATION.json').read_text());mismatches=[]
 for n,h in verification['delivery_hashes'].items():
  if sha(v/'delivery'/n)!=h:mismatches.append(n)
 assert not mismatches;checks['v3_delivery_hashes_verified']=len(verification['delivery_hashes'])
 for line in (v/'PHASES.jsonl').read_text().splitlines():
  phase=json.loads(line)
  for n,h in phase['hashes'].items():assert sha(v/n)==h,(phase['phase'],n)
 checks['v3_phase_seals_verified']=True
 result=dict(status='PASS_ENGINEERING_AND_PROVENANCE; NO SCIENTIFIC RATINGS OR SCORES',checks=checks,limitations=['No blind raters have been run.','No visual UI screenshot review performed.','Agreement definition pending; no kappa computed.','34 ambiguous/composite folios withheld; no inferred panel crops.','Amendment 3.2 has not been supplied.'])
 (R/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 (R/'SHA256SUMS.json').write_text(json.dumps({str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
