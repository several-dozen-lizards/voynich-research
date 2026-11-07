"""Clean source-only manual-registration packet; no observations fabricated."""
from common import *
import shutil,zipfile

DEST=ROOT/'human-registration';DEST.mkdir(exist_ok=True)
old=load(ROOT/'registration-pilot-v2/PLAN.json');tasks=[]
for index,t in enumerate(old['tasks']):
    image=f'page-{index+1}.jpg';shutil.copy2(t['image'],DEST/image)
    _,structure=source()
    headers={unit:{reading:[r['locus'] for r in structure if r['unit']==unit and r['reading']==reading] for reading in ['H','F']}
             for unit in sorted({r['unit'] for r in structure if r['page']==t['page']})}
    locs=[r for r in load(ROOT/'registrar-only/LOCI.json') if r['task_id'] in t['task_ids']]
    tasks.append(dict(page=t['page'],image=image,image_sha256=t['image_sha256'],headers=headers,targets=locs))
html='''<!doctype html><meta charset="utf-8"><title>Independent writing registration</title>
<style>body{font:16px/1.5 system-ui;margin:24px;color:#17252b}button,input,select{font:inherit;margin:4px;padding:7px}canvas{display:block;max-width:100%;touch-action:none;outline:1px solid #888}pre{white-space:pre-wrap}label{display:block}.panel{position:sticky;top:0;background:#fff;padding:8px;border-bottom:2px solid #777;z-index:2}</style>
<h1>Independent writing registration</h1>
<p>Use only the source images and locator headers here. Do not read the parent research folder, transcription bodies, object categories, or the other registrar's work. Two different independent people must each receive a clean copy. Identify the exact target writing by source position and order; count agreement alone is insufficient. Leave uncertainty unregistered.</p>
<p>Select a target, then drag a rectangle tightly around its full writing. Use a shared physical-label ID for lines belonging to one inscription. Avoid nearby drawing ink. Do not transcribe or classify drawings. Headers are identifiers, not coordinates. Export observations before closing; nothing is transmitted.</p>
<div class="panel"><input id="person" placeholder="Your independent registrar ID"><select id="page"></select><select id="target"></select><input id="physical" placeholder="Physical label ID"><label><input type="checkbox" id="single"> This physical label consists of one line</label><input id="note" size="70" placeholder="Geometric basis or reason for abstaining"><button id="save">Save rectangle</button><button id="unclear">Unregistered / uncertain</button><button id="export">Export JSON</button><p id="status"></p></div>
<details><summary>Complete header structure</summary><pre id="headers"></pre></details><canvas id="canvas"></canvas>
<label><input type="checkbox" id="blind"> I have not seen object categories, transcription bodies, scientific outcomes, or the other registrar's work.</label>
<script>const TASKS=__TASKS__;
const $=id=>document.getElementById(id),c=$('canvas'),ctx=c.getContext('2d'),records={},img=new Image();let current=0,start=null,pending=null;
TASKS.forEach((t,i)=>$('page').add(new Option(t.page,i)));
function selected(){return TASKS[current].targets.find(t=>t.task_id===$('target').value)}
function redraw(){ctx.clearRect(0,0,c.width,c.height);ctx.drawImage(img,0,0);for(const t of TASKS[current].targets){let r=records[t.task_id];if(r&&r.bbox){ctx.strokeStyle='#b400bd';ctx.lineWidth=5;ctx.strokeRect(...r.bbox)}}if(pending){ctx.strokeStyle='#008475';ctx.lineWidth=5;ctx.strokeRect(...pending)}}
function loadPage(){current=+$('page').value;let t=TASKS[current];$('target').innerHTML='';t.targets.forEach(x=>$('target').add(new Option(x.locus,x.task_id)));$('headers').textContent=JSON.stringify(t.headers,null,2);pending=null;img.src=t.image;}
img.onload=()=>{c.width=img.naturalWidth;c.height=img.naturalHeight;redraw()};
function point(e){let b=c.getBoundingClientRect();return[Math.max(0,Math.min(c.width,(e.clientX-b.left)*c.width/b.width)),Math.max(0,Math.min(c.height,(e.clientY-b.top)*c.height/b.height))]}
c.onpointerdown=e=>{c.setPointerCapture(e.pointerId);start=point(e)};
c.onpointermove=e=>{if(!start)return;let p=point(e);pending=[Math.min(start[0],p[0]),Math.min(start[1],p[1]),Math.abs(start[0]-p[0]),Math.abs(start[1]-p[1])];redraw()};
c.onpointerup=e=>{if(start){let p=point(e);pending=[Math.min(start[0],p[0]),Math.min(start[1],p[1]),Math.abs(start[0]-p[0]),Math.abs(start[1]-p[1])];start=null;redraw()}};
function store(abstain){let t=selected();if(!$('note').value.trim())return alert('Record a geometric basis or uncertainty.');if(!abstain&&(!pending||pending[2]<=0||pending[3]<=0||!$('physical').value.trim()))return alert('A valid rectangle and physical-label ID are required.');records[t.task_id]={task_id:t.task_id,page:TASKS[current].page,bbox:abstain?null:pending,physical_label_id:abstain?null:$('physical').value.trim(),single_line:$('single').checked,locus_identity_confirmed:!abstain,review_note:$('note').value.trim(),source_image_sha256:TASKS[current].image_sha256};pending=null;$('status').textContent=Object.keys(records).length+' targets reviewed';redraw()}
$('save').onclick=()=>store(false);$('unclear').onclick=()=>store(true);$('page').onchange=loadPage;$('target').onchange=()=>{pending=null;$('note').value='';redraw()};
$('export').onclick=()=>{if(!$('person').value.trim()||!$('blind').checked)return alert('Registrar ID and blindness declaration are required.');let total=TASKS.reduce((s,t)=>s+t.targets.length,0);let data={registrar_id:$('person').value.trim(),outcome_blind:true,object_categories_unseen:true,picture_ratings_unseen:true,other_registrar_unseen:true,reviewed:Object.keys(records).length,total,rows:Object.values(records)};let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='independent-registration.json';a.click();URL.revokeObjectURL(a.href)};loadPage();</script>'''
(DEST/'index.html').write_text(html.replace('__TASKS__',json.dumps(tasks)),encoding='utf-8')
save(DEST/'SOURCE-MANIFEST.json',dict(images={t['image']:t['image_sha256'] for t in tasks},
    contents='Native images and transcription HEADER locators only; no word bodies, class manual, hypotheses, ratings or results.',
    tasks=sum(len(t['targets']) for t in tasks),independent_people_required=2,completed_registrars=0))
with zipfile.ZipFile(ROOT/'human-registration-only.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in DEST.iterdir():z.write(p,p.name)
print('Source-only human packet ready:',sum(len(t['targets']) for t in tasks),'targets; zero human observations')
