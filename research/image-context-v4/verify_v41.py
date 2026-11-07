"""Authored engineering checks only; no ratings or agreement generated."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,copy,importlib.util
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 packet=R/'rater-only';tasks=json.loads((packet/'TASKS.json').read_text());checks={}
 f=json.loads((R/'PROTOCOL-v4.1.json').read_text())
 for k,p in [('amendment_sha256',R/'AMENDMENT-v4.1-agreement-unit.md'),('manual_sha256',R/'MANUAL.md'),('tool_sha256',packet/'index.html'),('tasks_sha256',packet/'TASKS.json')]:assert sha(p)==f[k]
 assert (R/'MANUAL.md').read_bytes()==(packet/'MANUAL.md').read_bytes();checks['amendment_manual_tool_freeze']=True
 with zipfile.ZipFile(R/'v4-rater-only.zip') as z:
  assert z.testzip() is None
  assert set(z.namelist())=={str(p.relative_to(packet)).replace('\\','/') for p in packet.rglob('*') if p.is_file()}
  assert not any(s in n.lower() for n in z.namelist() for s in ['key','protocol','evt','result','legacy','agreement'])
 checks['rater_zip_private_material_absent']=True
 receipts={r['task_id']:r for r in json.loads((R/'research-only/IMAGE-RECEIPTS.json').read_text())}
 for t in tasks:
  assert set(t)=={'task_id','image','native_width','native_height'}
  assert sha(packet/t['image'])==receipts[t['task_id']]['sha256']
 checks['unchanged_native_images']=len(tasks)
 spec=importlib.util.spec_from_file_location('v41validator',R/'validate_picture_ratings.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 d=dict(schema='v4.1-picture-boxes',rater_id='ENGINEERING_ONLY',completed_pages=[tasks[0]['task_id']],rows=[])
 assert m.validate(d)['reviewed_without_pictures']==d['completed_pages'];checks['zero_picture_reviewed_page_valid']=True
 d['rows']=[dict(page=tasks[0]['task_id'],box=[1,1,20,20],category='PL',note='authored engineering fixture')];assert m.validate(d)['outcomes_joined'] is False
 bad=[lambda x:x['rows'][0].update(kind='line'),lambda x:x['rows'][0].update(box=[0,0,-1,10]),lambda x:x['rows'][0].update(box=[0,0,float('nan'),10]),lambda x:x['rows'][0].update(category='NO'),lambda x:x['completed_pages'].append(x['completed_pages'][0]),lambda x:x['rows'].append(copy.deepcopy(x['rows'][0])),lambda x:x.update(schema='v4-blind-boxes')]
 for fn in bad:
  x=copy.deepcopy(d);fn(x)
  try:m.validate(x)
  except ValueError:pass
  else:raise AssertionError('Invalid fixture accepted')
 checks['invalid_picture_exports_rejected']=len(bad)
 script=(packet/'index.html').read_text(encoding='utf-8').split('<script>')[1].split('</script>')[0];(R/'tool.syntax.js').write_text(script,encoding='utf-8')
 subprocess.run(['node','--check',str(R/'tool.syntax.js')],check=True,capture_output=True)
 subprocess.run(['node',str(R/'verify-picture-tool.js')],check=True,capture_output=True);checks['picture_tool_syntax_coordinate_and_workflow_checks']=True
 result=dict(status='PASS_V4.1_ENGINEERING; NO SCIENTIFIC RATINGS OR AGREEMENT',checks=checks,ratings=0,registration='NOT RUN',G6='NOT RUN',G2='NOT RUN',limitations=['No visual UI screenshot review.','34 folios withheld for panel registration.','Independent shared geometry and two blind raters still required.'])
 (R/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 (R/'SHA256SUMS.json').write_text(json.dumps({str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'},indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
