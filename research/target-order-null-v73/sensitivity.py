from pathlib import Path
import collections,hashlib,json,re
import numpy as np
from engine import TARGETS,test,score
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
q=load(R/'QUALIFICATION.json');assert next(v for v in q['results'] if v['mode']=='within_line')['passes'];assert not next(v for v in q['results'] if v['mode']=='exact_slot')['passes']
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
protocol={'status':'Separately frozen sensitivity continuation after original whole-run gate aborted. Primary exact-slot manuscript test remains NOT RUN; its power diagnostic failure is not waived or repaired.',
 'scope':'Run only the mode that passed its own frozen diagnostic, within_line. Same rows, targets, exact-frame exclusion, six contrasts, 4999shuffles, original seeds7302H/7304F, triad minP and ORIGINAL factor4 retained despite only two panels being run.',
 'interpretation':'Limited broad-position/per-line-frequency sensitivity result only. No exact-position conclusion, no untouched confirmation, no semantic qualification. Original protocol, engine, gate and failure records unchanged. No outcome-dependent test tuning.',
 'preservation':'All six contrasts, original counts and folio contributions, reverse/self pair events, all retained qokedy contexts and excluded frame centers saved.'}
freeze={'sensitivity.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'engine.py':hashlib.sha256((R/'engine.py').read_bytes()).hexdigest(),'original_FREEZE.json':hashlib.sha256((R/'FREEZE.json').read_bytes()).hexdigest()}
if (R/'SENSITIVITY-FREEZE.json').exists():assert load(R/'SENSITIVITY-FREEZE.json')==freeze and load(R/'SENSITIVITY-PROTOCOL.json')==protocol
else:save('SENSITIVITY-FREEZE.json',freeze);save('SENSITIVITY-PROTOCOL.json',protocol)
raw=load(P/'frequency-atlas-v48/rows.json');old=load(P/'middle-contexts-v72/RESULTS.json')
base=[r for r in raw if tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0]!='f75'];loci={tr:{r[6] for r in base if r[0]==tr} for tr in ['H','F']};shared=loci['H']&loci['F'];panels=[];observed={}
for ti,tr in enumerate(['H','F']):
 rs=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in base if r[0]==tr and r[6] in shared];events=[];byfolio=collections.defaultdict(list)
 for r in rs:
  byfolio[r['folio']].append(r['tokens'])
  for i in range(len(r['tokens'])-1):
   a,b=r['tokens'][i:i+2]
   if a in TARGETS and b in TARGETS:events.append(dict(r,ordinal=i+1,first=a,second=b))
 observed[tr]=dict(events=events,excluded_centers={w:old['readings'][tr]['profiles'][w]['excluded_frame_centers'] for w in TARGETS},qokedy_profile=old['readings'][tr]['profiles']['qokedy'],folio_contrasts={f:score(lines)[0].tolist() for f,lines in byfolio.items()})
 out,scores=test(rs,'within_line',4999,7302+2*ti)
 for x in out['tests']:x['p_four_panels']=min(1,4*x['p_triad_family'])
 out.update(reading=tr,lines=len(rs),folios=len(byfolio));panels.append(out);np.savez_compressed(R/(tr+'-within_line-null.npz'),scores=scores)
 print(tr,out['tests'][4],flush=True)
save('RESULTS.json',dict(original_protocol=load(R/'PROTOCOL.json'),sensitivity_protocol=protocol,qualification=q,primary_status='NOT RUN: frozen exact-slot power diagnostic 7/20 failed 12/20 gate',panels=panels,observed=observed))
save('SUMMARY.json',[dict(reading=p['reading'],mode=p['mode'],noticed=p['tests'][4],all_tests=p['tests']) for p in panels]);save('VERIFICATION.json',dict(original_freeze_integrity='pass',sensitivity_freeze='pass',primary_manuscript_test='not run; original failure preserved',semantic_inference='none',browser_visual_review='not performed'))
