"""Verify the Phase 10 source STOP and frozen receipts without opening target data."""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent
def read(name):
    return json.loads((root/name).read_text(encoding='utf-8-sig'))
checks=[]
def check(name, condition):
    checks.append({'name':name,'pass':bool(condition)})

reg=read('REGISTRATION.json'); freeze=read('SOURCE_FREEZE.json')
for name,expected in freeze['files'].items():
    check('frozen_sha256:'+name,hashlib.sha256((root/name).read_bytes()).hexdigest()==expected)
check('original_protocol_registration',reg['files']['PROTOCOL.md']==freeze['files']['PROTOCOL.md'])
def timestamp(value):
    # PowerShell emits seven fractional digits; Python 3.10 accepts six.
    return datetime.fromisoformat(re.sub(r'(\.\d{6})\d+',r'\1',value.replace('Z','+00:00')))
check('registration_precedes_source_freeze',timestamp(reg['registered_utc']) < timestamp(freeze['frozen_utc']))
rows=read('MATCHES.json');sources=read('SOURCES.json');status=read('STATUS.json')
check('unique_picture_pairs',len({(r['pharma_folio'],r['petersen_item'],r['herbal_folio']) for r in rows})==len(rows))
check('confidence_accounting',dict(Counter(r['confidence'] for r in rows))==freeze['counts']=={'confident':9,'tentative':24,'contested':2})
check('source_threshold_failed',freeze['counts']['confident']<freeze['required_confident']==15)
primary={r['petersen_item']:r['herbal_folio'] for r in rows if r['confidence']=='confident'}
check('primary_exact_set',primary=={54:'f48v',61:'f48r',203:'f37v',204:'f1v',205:'f47v',206:'f32v',212:'f18v',213:'f23r',240:'f19r'})
check('nine_distinct_primary_pages',len(set(primary.values()))==9)
for r in rows:
    check('citation:'+r['pair_id'],all(s in sources for s in r['source_ids']) and bool(r['source_locator']))
    check('no_target_values:'+r['pair_id'],r['label']==r['position']=='NOT LOADED' and r['statistic']==r['matched_words']=='NOT RUN')
with (root/'MATCHES.csv').open(encoding='utf-8',newline='') as f:
    csvrows=list(csv.DictReader(f))
check('csv_json_agree',len(csvrows)==len(rows) and all(c['pair_id']==j['pair_id'] and c['herbal_folio']==j['herbal_folio'] and c['confidence']==j['confidence'] for c,j in zip(csvrows,rows)))
check('calibration_not_run',status['calibration'].startswith('NOT RUN'))
check('transcriptions_closed',status['ZL']==status['LSI_H']=='NOT LOADED')
check('statistics_not_run',status['S1_S2_S3']=='NOT RUN')
check('no_name_claim',not status['candidate_native_name_loci_established'] and not status['meaning_claim'])
exposure=read('EXPOSURE_AND_RETRIEVAL.json')
check('exposure_disclosed',exposure['incidental_web_exposure'] and not exposure['local_voynich_transcription_files_opened'])
result={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','scope':'Source receipt integrity and accounting only; not independent visual/source adjudication or calibration qualification','checks':checks,'checks_passed':sum(c['pass'] for c in checks),'checks_total':len(checks)}
(root/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
if result['status']!='PASS':
    raise SystemExit(1)
