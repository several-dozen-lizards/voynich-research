"""Fresh source-only review; never receives prose notes or object-rating data."""
from common import *
from plain_api import vision,json_object
from PIL import Image,ImageDraw

pilot=ROOT/'registration-pilot';plan=load(pilot/'PLAN.json')
save(pilot/'SECOND-PASS-PLAN.json',dict(status='FROZEN_BEFORE_SECOND_PASS',provider='zai',model='glm-4.6v',
    independent_request=True,same_model_family_as_proposer=True,
    forwarded='Only task IDs, rectangles and source-order locators. Proposer notes are withheld.',
    provenance='User explicitly approved Z.AI registration and ratings after automatic review rejection.',
    client_sha256=sha(ROOT/'plain_api.py'),script_sha256=sha(Path(__file__)),
    limitation='Independent stateless requests are not independent model families; source geometry still requires both passes and all hard acceptance rules.'))
for task in plan['tasks']:
    dest=pilot/task['page']/'reviewer-GLM'
    if (dest/'completion.json').exists():continue
    data=json_object(load(pilot/task['page']/'proposer-GLM/completion.json')['content'])
    rows=[{k:r.get(k) for k in ['task_id','bbox']} for r in data.get('rows',[])]
    im=Image.open(task['image']).convert('RGB');draw=ImageDraw.Draw(im)
    for i,r in enumerate(rows):
        if r['bbox']:
            x,y,w,h=r['bbox'];draw.rectangle((x,y,x+w,y+h),outline='#e600cc',width=5);draw.text((x,y),str(i+1),fill='#e600cc')
    image=pilot/task['page']/'second-review-overlay.png';im.save(image)
    prompt=Path(task['prompt']).read_text(encoding='utf-8')+'\nIndependent second-pass source-only verification. Magenta rectangles are UNVERIFIED proposals, numbered in this order. Reject wrong text, paragraph blocks, boxes containing several unrelated lines, or uncertain locus identity. Supply your own writing-only rectangle only if confidently associated with the exact locator. Supply a nonempty physical_label_id only when justified. Do not transcribe or classify. Proposals:\n'+json.dumps(rows)
    print('second review',task['page'],flush=True)
    vision('zai','glm-4.6v',prompt,image,dest,max_tokens=4096)
print('Source-only second pass complete')
