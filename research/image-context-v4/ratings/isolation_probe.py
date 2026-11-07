"""Non-manuscript harness probe; cannot produce study ratings."""
from pathlib import Path
import json,subprocess,shutil,os
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
W=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\25\01a170af-9b54-7122-8b1a-552c946aea4c\vision-isolation-probe')
DISABLE=['memories','apps','shell_tool','unified_exec','multi_agent','skill_search','computer_use','browser_use','in_app_browser','view_image','image_generation','sleep_tool','goals','workspace_dependencies','tool_suggest']
CONFIG=['project_doc_max_bytes=0','memories.use_memories=false','memories.generate_memories=false','web_search="disabled"','features.skip_host_skill_discovery=true','personality="none"']
def options():
 a=[]
 for x in DISABLE:a+=['--disable',x]
 for x in CONFIG:a+=['-c',x]
 return a
def main():
 W.mkdir(parents=True,exist_ok=True);R.mkdir(exist_ok=True)
 im=Image.new('RGB',(500,500),'white');d=ImageDraw.Draw(im);d.rectangle((100,100,200,200),outline='black',width=3);im.save(W/'image.png')
 manual=(R.parent/'MANUAL.md').read_text(encoding='utf-8');(W/'MANUAL.md').write_text(manual,encoding='utf-8')
 schema=dict(type='object',properties=dict(completed=dict(type='boolean'),pictures=dict(type='array',items=dict(type='object',properties=dict(box=dict(type='array',items=dict(type='number'),minItems=4,maxItems=4,description='Normalized x,y,width,height fractions of image width/height, top-left origin.'),category=dict(type='string',enum=['PL','VE','FG','CE','OT']),note=dict(type='string')),required=['box','category','note'],additionalProperties=False))),required=['completed','pictures'],additionalProperties=False)
 (W/'schema.json').write_text(json.dumps(schema),encoding='utf-8');exe=shutil.which('codex');assert exe
 # Capture the constructed context locally; print only a contamination summary, never base64.
 debug=[exe,'-C',str(W),'debug','prompt-input',*options(),'-i',str(W/'image.png'),manual]
 result=subprocess.run(debug,cwd=W,capture_output=True,text=True,encoding='utf-8',timeout=60)
 (R/'probe-prompt.json').write_text(result.stdout,encoding='utf-8');(R/'probe-debug-stderr.txt').write_text(result.stderr,encoding='utf-8')
 if result.returncode:print(json.dumps(dict(stage='debug',exit_code=result.returncode,stderr=result.stderr[-1400:])));return
 payload=result.stdout
 flags={s:s.lower() in payload.lower() for s in ['MEMORY_SUMMARY','sh→qok','qok','v4.2','RETROSPECTIVE','JNSQ','Amendment','AGENTS.md instructions']}
 print(json.dumps(dict(stage='debug',exit_code=0,characters=len(payload),contamination_markers=flags)),flush=True)
 # Keep a bounded response from a single fresh synthetic session, using normal saved auth.
 cmd=[exe,'--no-daemon','-a','never','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','-C',str(W),*options(),'--json','--output-schema',str(W/'schema.json'),'-i',str(W/'image.png'),'-o',str(W/'result.json'),'-']
 (R/'probe-command.json').write_text(json.dumps(cmd,indent=2),encoding='utf-8')
 result=subprocess.run(cmd,input=manual,cwd=W,capture_output=True,text=True,encoding='utf-8',timeout=180)
 (R/'probe-events.jsonl').write_text(result.stdout,encoding='utf-8');(R/'probe-stderr.txt').write_text(result.stderr,encoding='utf-8')
 print(json.dumps(dict(stage='exec',exit_code=result.returncode,result_exists=(W/'result.json').exists(),stderr=result.stderr[-1800:])),flush=True)
if __name__=='__main__':main()
