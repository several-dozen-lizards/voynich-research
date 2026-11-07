from pathlib import Path
import json,hashlib,collections,itertools,re,datetime,importlib.util,tempfile
from fractions import Fraction
from contextlib import nullcontext
R=Path(__file__).resolve().parent;B=R.parent;P=B.parent
checks=[]
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,ok):checks.append({'check':name,'pass':bool(ok)})
plan=load(R/'PLAN.json');pre=load(R/'PRE-SCORE-FREEZE.json');code=load(R/'CODE-FREEZE.json');result=load(R/'C2-PRETEST.json');log=load(R/'LOOK-LOG.json');rows=load(R/'ADMITTED-ROWS.json');records=load(R/'ALLOWED-SOURCE-RECORDS.json');coverage=load(R/'COVERAGE.json')
check('plan unchanged',sha(R/'PLAN.json')==pre['plan_sha256'])
for f,h in code['files'].items():check('code unchanged '+f,sha(R/f)==h)
check('five looks logged once',log['looks_used']==5 and len(log['looks'])==5 and len({x['look'] for x in log['looks']})==5)
check('ten look cap respected',log['looks_used']<=log['look_cap']==10)
check('all logs completed',all(x['status']=='COMPLETED' for x in log['looks']))
check('no adaptive look scheduled',not log['adaptive_looks_authorized'])
check('source result predates no plan',datetime.datetime.fromisoformat(pre['utc'])<datetime.datetime.fromisoformat(code['utc'])<datetime.datetime.fromisoformat(log['looks'][0]['started_utc']))
check('no reserved rows in production outputs',all(x['folio'] not in plan['reserved_signs'] for x in rows+records))
check('no other reading substituted',all(x['reading'] in ['H','F'] for x in rows+records))
check('unique observation IDs',len({(x['id'],x['reading']) for x in rows})==len(rows))
check('complete admitted labels only',all(x['words'] and all(re.fullmatch('[a-z]+',w) for w in x['words']) for x in rows))
check('missing F preserved',result['readings']['F']['status']=='NOT_ESTIMABLE' and result['readings']['F']['coverage']['zodiac']==0)
check('not false NO_MARKER',result['joint_marker_outcome']=='NOT_ESTIMABLE' and result['NO_MARKER'] is False)
check('no joint removal admitted',all(v is None for v in result['joint_removal_candidates'].values()))
check('no alignment or vault scoring',result['C3_alignment_run'] is False and result['vault_open'] is False and result['vault_tests_run']==0)
check('extra-top group outside ring statistic',all(x['unit']!='f72r2.S0' for x in rows if x['set']=='zodiac'))

def independent_feature(r,f):
 if f['kind']=='opener':return next((p for p in ['ot','ok','qo','ch','sh','d'] if r['words'][0].startswith(p)),'other')
 if f['kind']=='ending_family':return next((s for s in plan['ending_families'] if s!='other' and r['words'][-1].endswith(s)),'other')
 word=r['words'][-1];u=[]
 while word:
  g=next((g for g in ['cth','ckh','cph','cfh','ch','sh'] if word.startswith(g)),word[0]);u.append(g);word=word[len(g):]
 return ''.join(u[-f['width']:]) if len(u)>=f['width'] else None

for f in plan['planned_looks']:
 artifact='LOOK-%02d.json'%f['look'];data=load(R/artifact)
 item=next(x for x in log['looks'] if x['look']==f['look'])
 check(artifact+' ledger hash',sha(R/artifact)==item['result_sha256'])
 check(artifact+' exact frozen feature',data['feature']==f)
 for reading in ['H','F']:
  z=[r for r in rows if r['reading']==reading and r['set']=='zodiac'];o=[r for r in rows if r['reading']==reading and r['set'] in ['star','plant-jar','rosette']]
  zv=[independent_feature(r,f) for r in z];ov=[independent_feature(r,f) for r in o]
  wh=collections.Counter();dh=collections.Counter();bh=collections.Counter();wd=dd=bd=0
  for i,j in itertools.permutations(range(len(z)),2):
   same=z[i]['unit']==z[j]['unit'] and z[i]['folio']==z[j]['folio']
   if same:wd+=1
   else:dd+=1
   if zv[i]==zv[j] and zv[i] is not None:
    if same:wh[zv[i]]+=1
    else:dh[zv[i]]+=1
  for i,j in itertools.permutations(range(len(o)),2):
   bd+=1
   if ov[i]==ov[j] and ov[i] is not None:bh[ov[i]]+=1
  metrics=data['readings'][reading]['metrics']
  for m in metrics:
   v=m['value'];prefix=artifact+':'+reading+':'+v
   check(prefix+' within direct pair enumeration',m['within_ring']['numerator']==wh[v] and m['within_ring']['denominator']==wd)
   check(prefix+' between direct pair enumeration',m['different_ring_same_section']['numerator']==dh[v] and m['different_ring_same_section']['denominator']==dd)
   check(prefix+' other direct pair enumeration',m['nonzodiac_pair_baseline']['numerator']==bh[v] and m['nonzodiac_pair_baseline']['denominator']==bd)
   expected=None if not wd or not bd or not bh[v] else Fraction(wh[v]*bd,wd*bh[v])
   rat=m['constancy_ratio']
   check(prefix+' exact ratio',rat is None if expected is None else rat is not None and Fraction(rat['numerator'],rat['denominator'])==expected)
   check(prefix+' zodiac prevalence',m['shares']['zodiac']['count']==zv.count(v) and m['shares']['zodiac']['n']==len(z))
# Test the actual adapter on a synthetic mixed-scope container. No real reserved data involved.
spec=importlib.util.spec_from_file_location('run_c2_for_guard_test',R/'run_c2.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
(R/'synthetic-guard-fixture').mkdir(exist_ok=True)
with nullcontext(str(R/'synthetic-guard-fixture')) as td:
 t=Path(td);mod.R=t
 fake=t/'fake.evt'
 fake.write_bytes(b'<f70v2.S1.1;H> qokeedy\n<f73r.S1.1;H> VAULT_PAYLOAD_SENTINEL\n<f70v2.S1.1;V> OTHER_READING_SENTINEL\n<f68r1.S.1;H> daiin\n<f69r.P.1;H> OUTSIDE_SENTINEL\n')
 units=[dict(unit='f70v2.S1',folio='f70v2',set='zodiac',HF_header_counts={'H':1,'F':0}),dict(unit='f68r1.S',folio='f68r1',set='star',HF_header_counts={'H':1,'F':0})]
 (t/'METADATA-INVENTORY.json').write_text(json.dumps(dict(units=[dict(unit=u['unit'],HF_locators={'H':['1'],'F':[]}) for u in units])))
 p=dict(source_evt=str(fake),units=units,reserved_signs=plan['reserved_signs'],reading_codes=['H','F'])
 out=mod.adapt(p);outputs=''.join(x.read_text() for x in t.glob('*.json'))
 check('adapter reserved payload sentinel never retained','VAULT_PAYLOAD_SENTINEL' not in outputs)
 check('adapter replacement reading sentinel never retained','OTHER_READING_SENTINEL' not in outputs)
 check('adapter out of scope sentinel never retained','OUTSIDE_SENTINEL' not in outputs)
 check('adapter admits exactly allowed fixture records',len(out)==2 and {x['words'][0] for x in out}=={'qokeedy','daiin'})
 check('adapter decodes only allowed fixture payloads',load(t/'COVERAGE.json')['adapter_audit']['allowed_payloads_decoded']==2)
# Verify the entire unchanged historical source freeze, plus administrative locks.
c1=B/'C1-source-freeze-v1';freeze=load(c1/'FREEZE.json')
check('C1 freeze unchanged',sha(c1/'FREEZE.json')==pre['source_set_freeze_sha256'])
for f in freeze['files']+freeze['external_source_dependencies']:check('C1 sealed dependency '+f['path'],sha(c1/f['path'])==f['sha256'])
check('budget unchanged',sha(B/'BUDGET.json')==pre['budget_sha256'])
check('original C2 placeholder preserved',sha(B/'C2-PRETEST.json')==pre['prior_C2_state_sha256'])
check('qualification unchanged',sha(B/'attempt-3-v7.2/QUALIFICATION.json')==pre['harness_qualification_sha256'])
check('original geometry unchanged',sha(P/'zodiac-mapping-v84/GEOMETRY.json')==pre['geometry_sha256'] and sha(P/'zodiac-mapping-v84/ANNOTATIONS.json')==pre['annotation_sha256'])
summary=dict(status='PASS' if all(x['pass'] for x in checks) else 'FAIL',checks_run=len(checks),failed=[x for x in checks if not x['pass']],checks=checks,verification_is_new_look=False,scope='Independent direct enumeration of production pair counts; production guard tested on synthetic container; preservation/hash checks. No feature selection changes or additional manuscript look.')
(R/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:summary[k] for k in ['status','checks_run','failed']}))
if summary['status']!='PASS':raise SystemExit(1)
