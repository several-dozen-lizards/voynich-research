"""Known synthetic image stimuli only; never appended to real RATER files."""
from common import *
from plain_api import vision,IsolatedOllama,json_object,http
from PIL import Image,ImageDraw,ImageFont
import math,argparse

DEST=ROOT/'rater-interface-control'
def prepare():
    DEST.mkdir(exist_ok=True)
    tasks=[]
    for kind in ['STAR','VESSEL']:
        im=Image.new('RGB',(480,350),'#f5efda');d=ImageDraw.Draw(im)
        if kind=='STAR':
            points=[(210+(105 if i%2==0 else 43)*math.sin(i*math.pi/5),170-(105 if i%2==0 else 43)*math.cos(i*math.pi/5)) for i in range(10)]
            d.polygon(points,fill='#f2d679',outline='black',width=4)
        else:
            d.rounded_rectangle((125,110,270,280),radius=35,outline='black',width=5)
            d.rectangle((165,65,230,115),fill='#f5efda',outline='black',width=5)
            d.ellipse((165,55,230,77),fill='#f5efda',outline='black',width=4)
        d.text((330,160),'abcd',fill='black',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22))
        d.rectangle((322,150,400,192),outline='#e600cc',width=3)
        thumb=im.copy();thumb.thumbnail((170,140));canvas=Image.new('RGB',(675,350),'white');canvas.paste(im,(0,0));canvas.paste(thumb,(500,0))
        path=DEST/(kind+'.png');canvas.save(path);tasks.append(dict(id=kind,image=str(path),truth=kind,sha256=sha(path)))
    save(DEST/'PLAN.json',dict(status='ENGINEERING_STIMULI_FROZEN_BEFORE_CALLS',tasks=tasks,manual_sha256=sha(ROOT/'MANUAL.md'),
        limits='Two authored cartoon fixtures check transport/schema/coarse class use; not manuscript rater reliability or agreement qualification.'))

def run():
    plan=load(DEST/'PLAN.json');manual=(ROOT/'MANUAL.md').read_text(encoding='utf-8')
    before=http('http://127.0.0.1:11434/api/ps',timeout=5)
    try:
        with IsolatedOllama() as server:
            for task in plan['tasks']:
                for who,provider,model in [('A','zai','glm-4.6v-flashx'),('B','ollama','moondream:latest')]:
                    dest=DEST/task['id']/who
                    if (dest/'completion.json').exists() or (dest/'failure.json').exists():continue
                    print('interface fixture',task['id'],who,flush=True)
                    try:vision(provider,model,manual,task['image'],dest,base=server.base if provider=='ollama' else None,max_tokens=256)
                    except RuntimeError as error:print(type(error).__name__,flush=True)
    finally:
        after=http('http://127.0.0.1:11434/api/ps',timeout=5)
        save(DEST/'ISOLATION.json',dict(before=before,after=after,main_generation_calls=0,isolated_CPU_server_closed=True))
    results=[]
    for task in plan['tasks']:
        for who in ['A','B']:
            dest=DEST/task['id']/who;row=dict(stimulus=task['id'],rater=who,truth=task['truth'])
            try:
                data=json_object(load(dest/'completion.json')['content']);row.update(returned=data,schema_ok=data.get('class') in CLASSES,
                    correct=data.get('class')==task['truth'])
            except Exception as error:row.update(schema_ok=False,correct=False,error_type=type(error).__name__)
            results.append(row)
    save(DEST/'RESULTS.json',dict(status='PASS_INTERFACE_ONLY' if all(r['correct'] and r['schema_ok'] for r in results) else 'FAIL_INTERFACE',results=results,
        real_ratings=0,manuscript_reliability_established=False))
    print(load(DEST/'RESULTS.json')['status'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','run']);args=ap.parse_args();globals()[args.stage]()
