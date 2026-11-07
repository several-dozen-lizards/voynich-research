"""Synthetic-only stateless picture-interface test; never reads manuscript data."""
from pathlib import Path
import json,subprocess,shutil,uuid,base64,sys
from isolation_probe import W
R=Path(__file__).resolve().parent
def main():
 exe=shutil.which('claude');assert exe
 manual=(W/'MANUAL.md').read_text(encoding='utf-8')+'\nBox coordinates are [left/image_width, top/image_height, box_width/image_width, box_height/image_height], fractions from 0 to 1 measured on the supplied image itself. Use the tight enclosing rectangle of each picture element. Do not include blank page margins or writing as part of a picture box.\n'
 schema=json.loads((W/'schema.json').read_text())
 message=dict(type='user',message=dict(role='user',content=[dict(type='image',source=dict(type='base64',media_type='image/png',data=base64.b64encode((W/'image.png').read_bytes()).decode()))]))
 cmd=[exe,'--print','--output-format','stream-json','--input-format','stream-json','--verbose','--tools','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--setting-sources','','--disable-slash-commands','--system-prompt',manual,'--json-schema',json.dumps(schema),'--session-id',str(uuid.uuid4())]
 if len(sys.argv)>1:cmd+=['--model',sys.argv[1]]
 (R/'claude-probe-command.json').write_text(json.dumps(cmd,indent=2),encoding='utf-8')
 p=subprocess.run(cmd,input=json.dumps(message)+'\n',capture_output=True,text=True,encoding='utf-8',cwd=W,timeout=180)
 tag=sys.argv[1] if len(sys.argv)>1 else 'default-explicit-coordinates'
 (R/('claude-probe-'+tag+'-events.jsonl')).write_text(p.stdout,encoding='utf-8');(R/('claude-probe-'+tag+'-stderr.txt')).write_text(p.stderr,encoding='utf-8')
 summary=[]
 for line in p.stdout.splitlines():
  try:d=json.loads(line)
  except:continue
  if d.get('type')=='system':summary.append({k:d.get(k) for k in ['type','subtype','tools','mcp_servers','model','claude_code_version','session_id']})
  if d.get('type')=='result':summary.append({k:d.get(k) for k in ['type','subtype','is_error','result','structured_output','duration_ms']})
 print(json.dumps(dict(exit_code=p.returncode,summary=summary,stderr_tail=p.stderr[-1000:]),indent=2))
if __name__=='__main__':main()
