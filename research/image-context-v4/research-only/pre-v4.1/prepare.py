from pathlib import Path
import json,hashlib,urllib.request,concurrent.futures,zipfile,shutil
from PIL import Image
R=Path(__file__).resolve().parent;P=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 private=R/'research-only';private.mkdir(exist_ok=True)
 queue=json.loads((P/'image-context-rater-v1/research-only/TASK-KEY.json').read_text())
 packet=R/'rater-only';(packet/'images').mkdir(parents=True,exist_ok=True)
 # All tasks are from unique exact canvas labels; never download composite/reserved candidates.
 tasks=queue['tasks'];assert len(tasks)==168
 assert not {'f72v1','f72v2','f73r','f73v'}.intersection(t['folio'] for t in tasks)
 freeze=dict(status='PACKET PREPARATION FROZEN; RATING RELEASE CLOSED PENDING AGREEMENT DEFINITION',manual_sha256=sha(R/'MANUAL.md'),notes_sha256=sha(R/'PROTOCOL-NOTES.md'),source_manifest_sha256=sha(P/'g-ending-audit-v89/YALE-MANIFEST.json'),event_cohort_sha256=sha(P/'sh-qok-context-map-v3/EVENTS.csv'),task_key_sha256=sha(P/'image-context-rater-v1/research-only/TASK-KEY.json'),phase_order=['protocol','manual','blind_rating','agreement','registration','masked_support','controls','join','test'],prohibited='No new Rosettes leave-out grids. v103 parked. No new text/image result.')
 if (R/'PROTOCOL.json').exists():assert json.loads((R/'PROTOCOL.json').read_text())==freeze
 else:save(R/'PROTOCOL.json',freeze)
 def fetch(t):
  p=packet/t['image']
  try:
   if not p.exists():
    with urllib.request.urlopen(t['url'],timeout=45) as f:content=f.read()
    tmp=p.with_suffix('.partial');tmp.write_bytes(content)
    with Image.open(tmp) as im:im.verify()
    tmp.replace(p)
   with Image.open(p) as im:im.verify()
   return dict(task_id=t['task_id'],status='READY',sha256=sha(p),bytes=p.stat().st_size)
  except Exception as e:return dict(task_id=t['task_id'],status='IMAGE_UNAVAILABLE',error=str(e))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  receipts=[]
  for i,r in enumerate(pool.map(fetch,tasks)):
   receipts.append(r)
   if (i+1)%20==0:print('Native images',i+1,'/',len(tasks),flush=True)
 save(private/'IMAGE-RECEIPTS.json',receipts);save(private/'TASK-KEY.json',queue)
 ready={r['task_id'] for r in receipts if r['status']=='READY'}
 public=[{k:v for k,v in t.items() if k in ('task_id','image','native_width','native_height')} for t in tasks if t['task_id'] in ready]
 save(packet/'TASKS.json',public);shutil.copy2(R/'MANUAL.md',packet/'MANUAL.md')
 template=(R/'tool-template.html').read_text(encoding='utf-8')
 manual=(R/'MANUAL.md').read_text(encoding='utf-8')
 import html
 (packet/'index.html').write_text(template.replace('__MANUAL__',html.escape(manual)).replace('__TASKS__',json.dumps(public)),encoding='utf-8')
 old=P/'image-context-rater-v1/research-only'
 shutil.copy2(old/'LINE-REGISTRATION-QUEUE.json',private/'LINE-REGISTRATION-QUEUE.json')
 for p in old.glob('legacy-*'):shutil.copy2(p,private/p.name)
 shutil.copytree(old/'registration',private/'registration',dirs_exist_ok=True)
 for name in ('RATER-A','RATER-B','RATER-C'):
  (private/(name+'.csv.template')).write_text('rater_id,page,kind,block,line_number,x,y,width,height,category,note\n',encoding='utf-8')
 status=dict(status='PREPARED FOR REVIEW; BLIND RATING RELEASE PENDING AGREEMENT CLARIFICATION',cohort_folios=202,ready_pages=len(public),withheld_panel_registration=len(queue['withheld']),image_failures=len(tasks)-len(ready),raters=0,ratings=0,agreement='NOT RUN',registration='NOT RUN',support='NOT RUN',controls='NOT RUN',join='CLOSED',tests='NOT RUN',reserved_excluded=True,legacy_pilot='Original tool/scorer archived research-only; separate old rater ZIP remains plant-match endpoint, not v4.')
 save(R/'STATUS.json',status)
 with zipfile.ZipFile(R/'v4-rater-only.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(packet.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(packet))
 save(R/'SHA256SUMS.json',{str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 print(json.dumps(status),flush=True)
if __name__=='__main__':main()
