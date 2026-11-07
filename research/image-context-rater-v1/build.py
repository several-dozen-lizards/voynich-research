"""Prepare source-only annotations. Never infer image judgments or line coordinates."""
from pathlib import Path
import json,csv,hashlib,shutil,zipfile,urllib.request,concurrent.futures
from PIL import Image
R=Path(__file__).resolve().parent
P=R.parent
OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\review-pilot-v8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 public=R/'rater-only';private=R/'research-only'
 public.mkdir(exist_ok=True);private.mkdir(exist_ok=True);(public/'images').mkdir(exist_ok=True)
 manifest_path=P/'g-ending-audit-v89/YALE-MANIFEST.json'
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 rows=list(csv.DictReader((P/'sh-qok-context-map-v3/EVENTS.csv').open(encoding='utf-8')))
 pages=sorted({r['folio'] for r in rows});reserved={'f72v1','f72v2','f73r','f73v'};assert not reserved.intersection(pages)
 protocol=dict(status='FROZEN BEFORE RATER RESPONSES; REGISTRATION STAGE',cohort='All 202 folios in v3 EVENTS.csv, no selection by effect or image content; exact single-canvas labels only.',
  task='For each visible paragraph line, outline the line and adjacent pictured context; describe observable features. No word readings, meanings, plant identities or correspondence judgments requested.',
  blinding='No transcription, outcome, sh/ch/qok, context/scribe metadata or private line crosswalk in public packet. Pixels may reveal folio marks and section; recognition must be declared.',
  registration='Rater provides native-image line and adjacent-image rectangles. A separate registrar must crosswalk the line rectangle to a transcription locus, preserving ambiguity and alternate H/F readings. Never guess coordinates or use nearest-line automatic assignment.',
  labels=['plant_parts','human_figures','water_or_vessels','stars_or_circles','architecture','other'],
  feature_rule='Each visible feature independently yes/no/uncertain; multiple features allowed. none/unclear is a valid context status. These are visual descriptors, not meanings.',
  scoring='Validate actual annotations and report coverage only. No sh-qok test, inferential statistic, semantic score, automatic association or synthetic scientific responses. Freeze a separate analysis protocol before joining future ratings to outcomes.',
  image_rule='Native Yale IIIF JPEG, requested max 1800 pixels, no edits or invented crops. Composite or ambiguous canvas-to-panel registration stays withheld.',
  independence='One physical line receives one image annotation; H/F remain alternate transcriptions and never count as two independent judgments. Folio clustering needed in later analyses.',
  provenance=dict(manifest_id=manifest['id'],manifest_sha256=sha(manifest_path),events_sha256=sha(P/'sh-qok-context-map-v3/EVENTS.csv')))
 if (R/'PROTOCOL.json').exists():assert json.loads((R/'PROTOCOL.json').read_text())==protocol
 else:save(R/'PROTOCOL.json',protocol)
 bylabel={}
 for c in manifest['items']:
  label=next(iter(c['label'].values()))[0];bylabel.setdefault(label,[]).append(c)
 tasks=[];held=[]
 for page in pages:
  choices=bylabel.get(page[1:],[])
  if len(choices)!=1:
   held.append(dict(folio=page,status='WITHHELD_PANEL_REGISTRATION',reason='No unique exact single-page Yale canvas label.'));continue
  c=choices[0];tid='I'+hashlib.sha256(('context-v1/'+page).encode()).hexdigest()[:16]
  body=c['items'][0]['items'][0]['body'];url=body['service'][0]['@id']+'/full/!1800,1800/0/default.jpg'
  tasks.append(dict(task_id=tid,folio=page,canvas_id=c['id'],url=url,native_width=c['width'],native_height=c['height'],image='images/'+tid+'.jpg'))
 save(private/'TASK-KEY.json',dict(tasks=tasks,withheld=held))
 # A full line queue is private and outcome-free; both readings can map to one physical line.
 lines={}
 for row in rows:
  key=row['line'];o=lines.setdefault(key,dict(folio=row['folio'],line=key,readings=[],registration_status='PENDING',task_id=next((t['task_id'] for t in tasks if t['folio']==row['folio']),None)))
  if row['reading'] not in o['readings']:o['readings'].append(row['reading'])
 save(private/'LINE-REGISTRATION-QUEUE.json',list(lines.values()))
 def fetch(t):
  path=public/t['image']
  try:
   if not path.exists():
    with urllib.request.urlopen(t['url'],timeout=40) as f:data=f.read()
    with (path.with_suffix('.partial')).open('wb') as f:f.write(data)
    with Image.open(path.with_suffix('.partial')) as im:im.verify()
    path.with_suffix('.partial').replace(path)
   with Image.open(path) as im:im.verify()
   return dict(task_id=t['task_id'],status='READY',sha256=sha(path),bytes=path.stat().st_size)
  except Exception as exc:return dict(task_id=t['task_id'],status='IMAGE_FETCH_FAILED',error=str(exc))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  receipts=[]
  for i,receipt in enumerate(pool.map(fetch,tasks)):
   receipts.append(receipt)
   if (i+1)%20==0:print('Images',i+1,'/',len(tasks),flush=True)
 save(private/'IMAGE-RECEIPTS.json',receipts)
 ready={r['task_id'] for r in receipts if r['status']=='READY'}
 public_tasks=[{k:v for k,v in t.items() if k in ('task_id','native_width','native_height','image')} for t in tasks if t['task_id'] in ready]
 save(public/'TASKS.json',public_tasks)
 template=(R/'rater-template.html').read_text(encoding='utf-8');(public/'index.html').write_text(template.replace('__TASKS__',json.dumps(public_tasks)),encoding='utf-8')
 (public/'READ-ME.txt').write_text('Open index.html locally. Record one annotation per visible paragraph line. Outline the line and the pictured region beside it; do not transcribe or decode the text. Describe only what is visible. Export JSON before closing; import it to resume. No judgments have been supplied. Recognized pages and prior knowledge must be declared. Native folio marks can remain visible. Yale University Library, Beinecke MS 408.\n',encoding='utf-8')
 # Preserve the earlier ready-to-rate pilot and exact scorer/tool without silently changing its endpoint.
 legacy=R/'earlier-plant-pilot';legacy.mkdir(exist_ok=True)
 shutil.copytree(OLD/'rater-packet',legacy/'rater-only',dirs_exist_ok=True)
 for name in ['score_pilot.py','register-source.html','PROTOCOL.txt','pilot-frozen-key.json','pilot-status.json','pilot-image-provenance.json','source-registration-images.json','candidate-text-audit.json','run_topic.py','prepare_pilot.py']:
  shutil.copy2(OLD/name,private/('legacy-'+name))
 shutil.copytree(OLD/'registration',private/'registration',dirs_exist_ok=True)
 status=dict(stage='SOURCE_ONLY_RATER_PACKET_BUILT; LINE REGISTRATION AND RATINGS PENDING',cohort_folios=len(pages),ready_source_pages=len(public_tasks),withheld_panels=len(held),image_failures=len(tasks)-len(ready),private_line_loci=len(lines),ratings_collected=0,v3_amendment_3_2='MISSING TEXT; USER ASKED',legacy='Original two-screen plant-match pilot preserved separately. Its scorer is not an image-context scorer.')
 save(R/'STATUS.json',status)
 for folder,out in [(public,R/'image-context-rater-only.zip'),(legacy/'rater-only',R/'earlier-plant-rater-only.zip')]:
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(folder.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(folder))
 save(R/'SHA256SUMS.json',{str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 print(json.dumps(status),flush=True)
if __name__=='__main__':main()
