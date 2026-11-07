"""Outcome-blind registration pilot, two fresh source-only API passes."""
from common import *
from plain_api import vision,IsolatedOllama,json_object,http
from PIL import Image,ImageDraw
import argparse

PILOT=ROOT/'registration-pilot'
REGISTRAR='''You are an independent geometry registrar. You receive only the source image and the ordered inscription locators below. You have no transcription bodies, object classes, ratings, features or scientific analyses. Do not transcribe any writing or classify any drawing. Locate only the short inscriptions corresponding to the supplied locators, using native page coordinates, source position and source order. Ignore running paragraph text. Never accept a mapping merely because the counts match. If the exact locus identity or writing extent is uncertain, return bbox:null and explain why. Every rectangle must enclose the FULL writing for that one line. Do not include nearby drawing ink. Preserve multiline physical labels with a shared physical_label_id. Return JSON {"rows":[{"task_id":"...","bbox":[x,y,width,height] or null,"physical_label_id":"...","single_line":true or false,"locus_identity_confirmed":true or false,"review_note":"geometric basis or abstention"}]}. Coordinates are native pixels, not percentages.'''

def prepare():
    PILOT.mkdir(exist_ok=True);pages=load(ROOT/'registrar-only/PAGES.json');loci=load(ROOT/'registrar-only/LOCI.json')
    units,_=source();choice=sorted(pages,key=lambda x:digest('v61-registration:'+x['page']))[:2]
    tasks=[]
    for page in choice:
        rows=[r for r in loci if r['page']==page['page']]
        rows.sort(key=lambda r:(units[r['unit']]['source_line'],int(re.match(r'\d+',r['line'])[0]),r['line']))
        descriptions={}
        for row in rows:
            desc=next((s for s in units[row['unit']]['comments'] if s.strip()),'')
            desc=re.sub(r'(?i)\b(nymphs?|humans?|figures?|plants?|stars?|moons?|suns?|roots?|leaves|flowers?|tubs?|ponds?|pools?|vessels?|jars?|containers?|tubes?|structures?)\b','[drawing]',desc)
            descriptions[row['unit']]=desc
        inputs=dict(native_width=page['native_width'],native_height=page['native_height'],
                    ordered_loci=[{k:r[k] for k in ['task_id','locus','unit','line']} for r in rows],neutral_positions=descriptions)
        prompt=REGISTRAR+'\nLOCATORS:\n'+json.dumps(inputs)
        path=PILOT/(page['page']+'-registrar-prompt.txt');path.write_text(prompt,encoding='utf-8')
        tasks.append(dict(page=page['page'],image=page['source_image'],image_sha256=page['source_sha256'],prompt=str(path),prompt_sha256=sha(path),task_ids=[r['task_id'] for r in rows]))
    save(PILOT/'PLAN.json',dict(status='FROZEN_BEFORE_CALLS',selection='First two exact-canvas pages sorted by SHA256(v61-registration:page)',
        tasks=tasks,api_client_sha256=sha(ROOT/'plain_api.py'),registrar_script_sha256=sha(Path(__file__)),protocol_sha256=sha(ROOT/'PROTOCOL.json'),
        blinding='Source pixels, neutral positions, native dimensions and locators only; no categories or word bodies'))
    print([(t['page'],len(t['task_ids'])) for t in tasks])

def propose():
    for t in load(PILOT/'PLAN.json')['tasks']:
        assert sha(t['image'])==t['image_sha256'] and sha(t['prompt'])==t['prompt_sha256']
        dest=PILOT/t['page']/'proposer-GLM'
        if (dest/'completion.json').exists():continue
        print('proposing',t['page'],flush=True)
        vision('zai','glm-4.6v-flashx',Path(t['prompt']).read_text(encoding='utf-8'),t['image'],dest,max_tokens=4096)

def review():
    before=http('http://127.0.0.1:11434/api/ps',timeout=5)
    with IsolatedOllama() as server:
        for t in load(PILOT/'PLAN.json')['tasks']:
            dest=PILOT/t['page']/'reviewer-LLaVA'
            if (dest/'completion.json').exists():continue
            proposed=json_object(load(PILOT/t['page']/'proposer-GLM/completion.json')['content'])
            im=Image.open(t['image']).convert('RGB');draw=ImageDraw.Draw(im)
            for i,r in enumerate(proposed.get('rows',[])):
                if r.get('bbox'):
                    x,y,w,h=r['bbox'];draw.rectangle((x,y,x+w,y+h),outline='#e600cc',width=4);draw.text((x,y-15),str(i+1),fill='#e600cc')
            image=PILOT/t['page']/'proposed-overlay.png';im.save(image)
            prompt=Path(t['prompt']).read_text(encoding='utf-8')+'\nSECOND SOURCE-ONLY REVIEW: Boxes numbered in the image correspond to the ordered proposal rows. Independently verify full writing coverage and exact locus identity. Return your own corrected bbox or null; accept only when certain. Proposed geometry (no word bodies):\n'+json.dumps(proposed)
            print('reviewing',t['page'],flush=True)
            vision('ollama','llava:7b',prompt,image,dest,base=server.base,max_tokens=4096)
    after=http('http://127.0.0.1:11434/api/ps',timeout=5)
    save(PILOT/'MAIN-SERVER-READ-ONLY.json',dict(before=before,after=after,mutations_to_main=False,isolated_CPU_server_closed=True))

def iou(a,b):
    x=max(a[0],b[0]);y=max(a[1],b[1]);xx=min(a[0]+a[2],b[0]+b[2]);yy=min(a[1]+a[3],b[1]+b[3])
    intersection=max(0,xx-x)*max(0,yy-y)
    return intersection/(a[2]*a[3]+b[2]*b[3]-intersection)

def accept():
    from workflow import box_ok
    accepted=[];audit=[];pages={p['page']:p for p in load(ROOT/'registrar-only/PAGES.json')}
    for t in load(PILOT/'PLAN.json')['tasks']:
        outputs=[]
        for role in ['proposer-GLM','reviewer-LLaVA']:
            data=json_object(load(PILOT/t['page']/role/'completion.json')['content'])
            rows=data.get('rows',[])
            if len({r['task_id'] for r in rows})!=len(rows) or any(r['task_id'] not in t['task_ids'] for r in rows):raise ValueError('Unknown or duplicate registrar output')
            outputs.append({r['task_id']:r for r in rows})
        p=pages[t['page']]
        for tid in t['task_ids']:
            a,b=[d.get(tid,{}) for d in outputs];aa=a.get('bbox');bb=b.get('bbox');reason='UNREGISTERED_REVIEW_OR_IDENTITY_UNCERTAIN'
            okay=all(r.get('locus_identity_confirmed') is True and r.get('review_note') and r.get('physical_label_id') for r in [a,b])
            okay=okay and box_ok(aa,p['native_width'],p['native_height']) and box_ok(bb,p['native_width'],p['native_height'])
            overlap=iou(aa,bb) if okay else None
            if okay and overlap>=.70:
                accepted.append(dict(task_id=tid,bbox=bb,physical_label_id=b['physical_label_id'],single_line=b.get('single_line') is True,
                    source_image_sha256=t['image_sha256'],review_note=b['review_note'],proposer_response_sha256=sha(PILOT/t['page']/'proposer-GLM/response.json'),
                    reviewer_response_sha256=sha(PILOT/t['page']/'reviewer-LLaVA/response.json'),review_iou=overlap));reason='TWO_PASS_REGISTERED'
            audit.append(dict(task_id=tid,page=t['page'],status=reason,iou=overlap,proposed=aa,reviewed=bb))
    # Reject duplicated/overlapping boxes, rather than double-count a single inscription.
    pageof={r['task_id']:r['page'] for r in audit};bad=set()
    for i,a in enumerate(accepted):
        for b in accepted[i+1:]:
            if pageof[a['task_id']]==pageof[b['task_id']] and iou(a['bbox'],b['bbox'])>.2:bad.update([a['task_id'],b['task_id']])
    accepted=[r for r in accepted if r['task_id'] not in bad]
    for r in audit:
        if r['task_id'] in bad:r['status']='UNREGISTERED_OVERLAPPING_DUPLICATE'
    save(PILOT/'AUDIT.json',dict(rows=audit,accepted=len(accepted),dropped=len(audit)-len(accepted)))
    save(PILOT/'ACCEPTED.json',dict(registrar_id='GLM-propose_LLaVA-review_stateless_CPU',outcome_blind=True,object_categories_unseen=True,picture_ratings_unseen=True,
        two_pass_verified=True,rows=accepted))
    print('accepted',len(accepted),'of',len(audit))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','propose','review','accept']);args=ap.parse_args();globals()[args.stage]()
