"""Read-only source/preservation verification; no scorer or generator imports."""
from pathlib import Path
from collections import Counter
import hashlib,json
R=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(n,p):checks.append({'name':n,'pass':bool(p)})
snap=load(R/'SOURCE_AUDIT_SNAPSHOT.json')
for group in ['files','source_files']:
 for name,digest in snap[group].items():check(group+':'+name,(R/name).is_file() and sha(R/name)==digest)
reg=load(R/'DESIGN_REGISTRATION.json')
for name,digest in reg['files'].items():check('design:'+name,sha(R/name)==digest)
prior=load(R/'PHASE9_PRESERVATION_BEFORE.json');base=Path(prior['root'])
drift=[]
for name,digest in prior['files'].items():
 p=base/name;ok=p.is_file() and sha(p)==digest
 check('Phase9:'+name,ok)
 if not ok:drift.append(name)
additions=sorted(str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() and str(p.relative_to(base)) not in prior['files'])
check('Phase9:no_added_files',not additions)
rows=load(R/'CANDIDATES.json');counts=load(R/'COUNTS.json')
check('all_128_records_retained',len(rows)==128)
check('unique_record_ids',len(set(r['id'] for r in rows))==len(rows))
for row in rows:
 check('provenance:'+row['id'],all(k in row for k in ['date','region','variety','url','locator','status','form','month']))
 if row['status'].startswith('DATED_FORM'):
  check('period:'+row['id'],row['date'] is not None and 1350<=row['date'][0]<=row['date'][1]<=1550)
for lang,c in counts.items():
 rs=[r for r in rows if r['language']==lang]
 dated=[r for r in rs if r['status'] in {'DATED_FORM_VERIFIED','DATED_FORM_REGION_PENDING'}]
 keys={(r['month'],r['normalized']) for r in dated}
 check('counts:'+lang,len(keys)==c['distinct_dated_normalized_variants'] and len(dated)==c['dated_form_records'])
 check('coverage:'+lang,[m for m in range(3,13) if not any(mm==m for mm,v in keys)]==c['missing_months'])
state=load(R/'RUN_STATE.json')
check('no_calibration_claim',state['calibration']=='NOT RUN')
check('target_and_native_closed',state['annotation_target_fit']==state['native_tracks']=='CLOSED')
check('no_false_inseparability_result',state['inseparability_conclusion'].startswith('NOT ESTABLISHED'))
check('not_a_scoring_freeze',state['variant_scoring_freeze']=='NOT READY')
result={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','scope':'Audit integrity, provenance structure, date/coverage accounting and Phase 9 preservation only; not source exhaustiveness, independent paleography or calibration qualification',
 'passed':sum(c['pass'] for c in checks),'total':len(checks),'phase9_baseline_files':len(prior['files']),
 'phase9_changed_or_missing':drift,'phase9_added':additions,'checks':checks}
(R/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
if result['status']!='PASS':raise SystemExit(1)
