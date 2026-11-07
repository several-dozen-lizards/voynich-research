"""Source-only repair: full header structure; two unanchored independent requests.
Prior failed pilot is retained. No word bodies or object categories are supplied.
"""
from common import *
from plain_api import vision,json_object
from workflow import box_ok
from register_pilot import iou
from PIL import Image
import argparse

OUT=ROOT/'registration-pilot-v2'
MANUAL='''Locate the marked target inscription locators on this manuscript image using source position and reading order. This is geometry only: do not transcribe text or identify/classify drawings. The complete source HEADER STRUCTURE includes paragraph and nonparagraph locators so you can distinguish the short target lines from running paragraph text. Header numbers are identifiers, not coordinates. Count agreement alone is insufficient. Only return a box when the exact target identity AND full writing extent can be verified visually. Otherwise abstain. Return JSON only: {"rows":[{"task_id":"...","box_1000":[left,top,right,bottom] or null,"physical_label_id":"stable page-local label identifier" or null,"single_line":true or false,"locus_identity_confirmed":true or false,"review_note":"geometric basis, no word transcription"}]}. Coordinates are NORMALISED 0..1000 across the supplied full native page, with right>left and bottom>top. Include exactly one row per target. Adjacent lines of a single physical label must share physical_label_id.'''

def prepare():
    if (OUT/'PLAN.json').exists():raise ValueError('Plan already frozen')
    OUT.mkdir();old=load(ROOT/'registration-pilot/PLAN.json');units,allrows=source();tasks=[]
    for task in old['tasks']:
        structure=[]
        for unit in sorted({r['unit'] for r in allrows if r['page']==task['page']},key=lambda u:units[u]['source_line']):
            present=[r for r in allrows if r['unit']==unit and r['reading'] in ['H','F']]
            if not present:continue
            structure.append(dict(unit=unit,reading_headers={t:[r['locus'] for r in present if r['reading']==t] for t in ['H','F']}))
        targets=[{k:r[k] for k in ['task_id','locus','unit','line']} for r in load(ROOT/'registrar-only/LOCI.json') if r['task_id'] in task['task_ids']]
        original=Path(task['prompt']).read_text(encoding='utf-8');neutral=json.loads(original.split('LOCATORS:\n')[1])['neutral_positions']
        prompt=MANUAL+'\n'+json.dumps(dict(targets=targets,neutral_positions=neutral,complete_header_structure=structure))
        path=OUT/(task['page']+'-prompt.txt');path.write_text(prompt,encoding='utf-8')
        tasks.append(dict(task,prompt=str(path),prompt_sha256=sha(path)))
    save(OUT/'PLAN.json',dict(status='FROZEN_BEFORE_V2_CALLS',tasks=tasks,models=['glm-4.6v','glm-4.6v-flashx'],
        source_only=True,word_bodies=False,object_categories=False,other_pass_outputs_seen=False,
        repair='Full source headers and explicit normalised corner coordinates; two passes never see each other. Same predefined two pages; original failed pilot preserved.',
        acceptance='Both independently confirm identity, physical grouping and native writing boxes; IoU>=.70; all bounds valid; no duplicated/overlapping boxes; any ambiguity drops.',
        script_sha256=sha(Path(__file__)),client_sha256=sha(ROOT/'plain_api.py'),
        limitation='Same provider/model family; independent stateless processes, not independent trained families or human validation.'))

def run():
    plan=load(OUT/'PLAN.json')
    for task in plan['tasks']:
        for name,model in [('pass-A','glm-4.6v'),('pass-B','glm-4.6v-flashx')]:
            dest=OUT/task['page']/name
            if (dest/'completion.json').exists() or (dest/'failure.json').exists():continue
            assert sha(task['image'])==task['image_sha256'] and sha(task['prompt'])==task['prompt_sha256']
            print('registration v2',task['page'],name,flush=True)
            try:vision('zai',model,Path(task['prompt']).read_text(encoding='utf-8'),task['image'],dest,max_tokens=4096)
            except RuntimeError as e:print(type(e).__name__,flush=True)

def audit():
    accepted=[];rows=[];pages={p['page']:p for p in load(ROOT/'registrar-only/PAGES.json')}
    for task in load(OUT/'PLAN.json')['tasks']:
        parsed=[];errors=[];page=pages[task['page']]
        for name in ['pass-A','pass-B']:
            try:
                data=json_object(load(OUT/task['page']/name/'completion.json')['content']);rr=data['rows']
                if len(rr)!=len({r['task_id'] for r in rr}) or {r['task_id'] for r in rr}!=set(task['task_ids']):raise ValueError('Incomplete/duplicate IDs')
                parsed.append({r['task_id']:r for r in rr})
            except Exception as error:parsed.append({});errors.append(name+':'+type(error).__name__)
        for tid in task['task_ids']:
            a,b=[d.get(tid,{}) for d in parsed];okay=not errors
            boxes=[]
            for r in [a,b]:
                bb=r.get('box_1000')
                if not isinstance(bb,list) or len(bb)!=4:okay=False;boxes.append(None);continue
                native=[bb[0]/1000*page['native_width'],bb[1]/1000*page['native_height'],(bb[2]-bb[0])/1000*page['native_width'],(bb[3]-bb[1])/1000*page['native_height']]
                boxes.append(native)
                okay=okay and box_ok(native,page['native_width'],page['native_height']) and r.get('locus_identity_confirmed') is True and bool(r.get('physical_label_id')) and bool(r.get('review_note'))
            overlap=iou(*boxes) if okay else None
            okay=bool(okay and overlap>=.70)
            row=dict(task_id=tid,page=task['page'],accepted=okay,iou=overlap,pass_A=a,pass_B=b,schema_errors=errors)
            rows.append(row)
            if okay:
                accepted.append(dict(task_id=tid,bbox=boxes[1],physical_label_id=b['physical_label_id'],single_line=a.get('single_line') is True and b.get('single_line') is True,
                    source_image_sha256=task['image_sha256'],review_note=b['review_note'],proposer_response_sha256=sha(OUT/task['page']/'pass-A/response.json'),
                    reviewer_response_sha256=sha(OUT/task['page']/'pass-B/response.json'),review_iou=overlap))
    pageof={r['task_id']:r['page'] for r in rows};bad=set()
    for i,a in enumerate(accepted):
        for b in accepted[i+1:]:
            if pageof[a['task_id']]==pageof[b['task_id']] and iou(a['bbox'],b['bbox'])>.2:bad.update([a['task_id'],b['task_id']])
    for r in rows:
        if r['task_id'] in bad:r.update(accepted=False,drop='OVERLAPPING_DUPLICATE')
    accepted=[r for r in accepted if r['task_id'] not in bad]
    save(OUT/'AUDIT.json',dict(accepted=len(accepted),dropped=len(rows)-len(accepted),rows=rows))
    save(OUT/'ACCEPTED.json',dict(registrar_id='GLM-unanchored-two-pass-source-only',outcome_blind=True,object_categories_unseen=True,picture_ratings_unseen=True,two_pass_verified=True,rows=accepted))
    print('v2 accepted',len(accepted),'of',len(rows))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','run','audit']);args=ap.parse_args();globals()[args.stage]()
