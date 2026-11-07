from pathlib import Path
import re,json,collections,subprocess
R=Path(__file__).resolve().parent
s=(R/'report.html').read_text(encoding='utf8');js=re.findall(r'<script>(.*?)</script>',s,re.S)[0]
# Offline JS evaluation of data aggregation with a minimal element fixture; no browser or UI automation.
fixture="""const elements={};for(const id of ['tr','hand','lang','format','pos','mode','len','query','shared','units','coverage','detail','sections','context','neighbors','examples'])elements[id]={value:({tr:'H',hand:'all',lang:'all',format:'all',pos:'all',mode:'prefix',len:'2',query:'qo',shared:'all'})[id]||'',innerHTML:'',textContent:'',addEventListener(){}};const document={getElementById:id=>elements[id]};\n"""
extra="""\nif(!elements.sections.innerHTML.includes('Balneological'))throw Error('Section absent');let before=elements.coverage.textContent;elements.hand.value='1';update();if(before===elements.coverage.textContent)throw Error('Hand filter inactive');elements.mode.value='word';elements.query.value='qokedy';update();elements.tr.value='F';elements.shared.value='shared';update();console.log(JSON.stringify({offline_logic:'passed',coverage:elements.coverage.textContent,visual_check:'blocked by local-file URL policy'}));"""
(R/'verify-logic.js').write_text(fixture+(R/'data.js').read_text(encoding='utf8')+'\n'+js+extra,encoding='utf8')
p=subprocess.run(['node',str(R/'verify-logic.js')],capture_output=True,text=True);assert p.returncode==0,p.stderr
rows=json.loads((R/'rows.json').read_text());stats=[]
for sec in sorted(set(r[2] for r in rows)):
 ws=[w for r in rows if r[0]=='H' and r[2]==sec for w in r[7] if w]
 stats.append(dict(section=sec,N=len(ws),prefix_percent={x:100*sum(w.startswith(x) for w in ws)/max(1,len(ws)) for x in ['q','qo','ot']},suffix_dy_percent=100*sum(w.endswith('dy') for w in ws)/max(1,len(ws))))
for x in stats:print(x)
(R/'EXAMPLE-COUNTS.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
(R/'VERIFICATION.json').write_text(p.stdout,encoding='utf8');print(p.stdout)
