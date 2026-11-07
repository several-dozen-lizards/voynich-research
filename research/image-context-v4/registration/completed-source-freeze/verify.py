"""Independent coverage and authored registration checks; no outcomes or picture ratings."""
from pathlib import Path
import json,importlib.util,copy,hashlib,subprocess
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('registrar',R/'register.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 p=dict(task_id='fixture',folio='f0r',native_width=100,native_height=100)
 def unit(co,n):return dict(folio='f0r',unit='P',reading=co,line_count=n,lines=[dict(locus=f'f0r.P.{i+1}',source_line_number=str(i+1)) for i in range(n)])
 block=dict(block_id='b',unit='P',decision='VERIFIED',reason='AUTHORED ENGINEERING FIXTURE',box=[0,0,80,80],lines=[dict(line_number=1,box=[1,1,50,10]),dict(line_number=2,box=[1,20,50,10])])
 review=dict(registrar_id='ENGINEERING_ONLY',fresh_context=True,outcome_blind=True,picture_boxes_unseen=True,pages=[dict(task_id='fixture',reviewed=True,blocks=[block])])
 r=m.build([p],[unit('H',2),unit('F',2)],[],review);assert len(r['accepted'])==2 and len(r['shared_lines'])==2 and not r['dropped']
 r=m.build([p],[unit('H',2),unit('F',1)],[],review);assert len(r['accepted'])==1 and r['dropped'][0]['reason']=='LINE_COUNT_MISMATCH'
 r=m.build([p],[unit('H',2)],[],None);assert r['dropped'][0]['status']=='PENDING' and not r['shared_lines']
 r=m.build([],[unit('H',2)],[],None);assert r['dropped'][0]['reason']=='IMAGE_PANEL_UNREGISTERED'
 r=m.build([p],[unit('H',2)],[],review);assert len(r['accepted'])==1 and r['accepted'][0]['reading']=='H' and len(r['shared_lines'])==2 and r['dropped'][0]['reason']=='READING_UNIT_ABSENT'
 bad=0
 for fn in [lambda d:d.update(outcome_blind=False),lambda d:d.update(picture_boxes_unseen=False),lambda d:d.update(fresh_context=False),lambda d:d['pages'][0]['blocks'][0]['lines'][0].update(box=[0,0,-1,10]),lambda d:d['pages'][0]['blocks'][0]['lines'][0].update(line_number=2),lambda d:d['pages'][0].update(reviewed=False)]:
  d=copy.deepcopy(review);fn(d)
  try:m.build([p],[unit('H',2)],[],d)
  except ValueError:bad+=1
 assert bad==6
 inputs=json.loads((R/'PROTOCOL.json').read_text());checked=0
 for n,h in inputs['input_hashes'].items():assert sha(W/n)==h,n;checked+=1
 structure=json.loads((W/'EVT-STRUCTURE.json').read_text())
 for u in structure:
  assert set(u)=={'folio','unit','reading','line_count','lines'}
  for line in u['lines']:assert set(line)=={'locus','source_line_number'}
 data=json.loads((R/'REGISTRATION.json').read_text());expected={(u['folio'],u['unit'],u['reading']) for u in structure};seen=[]
 for r in data['accepted']+data['dropped']:
  k=(r['folio'],r['unit'],r['reading'])
  if k in expected:seen.append(k)
 assert len(seen)==len(set(seen))==len(expected) and set(seen)==expected
 geometry=json.loads((R/'SHARED-LINE-GEOMETRY.json').read_text())['lines'];ids=[x['shared_line_id'] for x in geometry];assert len(ids)==len(set(ids))
 refs={x['shared_line_id'] for b in data['accepted'] for x in b['line_map']};assert refs==set(ids)
 html=(W/'index.html').read_text(encoding='utf-8');script=html.split('<script>')[1].split('</script>')[0];(R/'tool.syntax.js').write_text(script,encoding='utf-8');subprocess.run(['node','--check',str(R/'tool.syntax.js')],check=True,capture_output=True)
 baseline=json.loads((R/'BASELINE-45-LINES.json').read_text())['lines'];by_id={l['shared_line_id']:l for l in geometry};assert len(baseline)==45 and all(by_id.get(l['shared_line_id'])==l for l in baseline)
 combined=json.loads((R/'REVIEW-COMBINED.json').read_text());complete=len(combined.get('unreviewed_pages',[]))==0
 checks=dict(authored_registration_scenarios=5,invalid_reviews_rejected=bad,allowlisted_input_hashes_verified=checked,header_only_EVT_manifest=True,all_expected_reading_units_accounted_once=len(expected),unique_shared_lines=len(ids),shared_line_references_match=True,registrar_tool_JS_syntax=True,retained_original45_unchanged=True,full_available_page_queue_reviewed=complete,absent_reading_never_imputed=True)
 out=dict(status='PASS_ENGINEERING_AND_COVERAGE; AVAILABLE_SOURCE_QUEUE_REVIEW_COMPLETE' if complete else 'PASS_ENGINEERING_AND_COVERAGE; VISUAL_REVIEW_COVERAGE_REMAINS_PARTIAL',checks=checks,outcomes_joined=False,picture_ratings_used=False,limitations=['Accepted geometry relies on independent registrar visual checks, not line-count equality alone.','Withheld panels and visually ambiguous blocks remain excluded; completed review is not complete registration of all manuscript lines.','No image-context labels, agreement or inferential results computed.','v4.2 pre-registration timing exception remains explicit.'])
 (R/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
