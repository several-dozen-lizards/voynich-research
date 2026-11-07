"""Execute only the five frozen C2 looks. No vault or name-alignment entrypoint."""
from pathlib import Path
import json,re,hashlib,collections,datetime,os,sys
from c2_engine import tokens,compute_look,summarize
R=Path(__file__).resolve().parent
B=R.parent
P=B.parent

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj):
 p=R/name;temp=p.with_suffix(p.suffix+'.tmp')
 temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,p)

def verify_gates():
 plan=load(R/'PLAN.json');pre=load(R/'PRE-SCORE-FREEZE.json');code=load(R/'CODE-FREEZE.json')
 if sha(R/'PLAN.json')!=pre['plan_sha256']:raise RuntimeError('Plan changed')
 if sha(R/'METADATA-INVENTORY.json')!=pre['metadata_sha256']:raise RuntimeError('Metadata changed')
 for name,digest in code['files'].items():
  if sha(R/name)!=digest:raise RuntimeError('Code changed: '+name)
 c1=B/'C1-source-freeze-v1';seal=load(c1/'FREEZE.json')
 if sha(c1/'FREEZE.json')!=pre['source_set_freeze_sha256']:raise RuntimeError('Source set changed')
 for f in seal['files']+seal['external_source_dependencies']:
  if sha(c1/f['path'])!=f['sha256']:raise RuntimeError('Source freeze mismatch: '+f['path'])
 if sha(plan['source_evt'])!=plan['expected_evt_sha256']:raise RuntimeError('Transcription source changed')
 if sha(P/'zodiac-mapping-v84/GEOMETRY.json')!=pre['geometry_sha256']:raise RuntimeError('Geometry rules changed')
 if sha(P/'zodiac-mapping-v84/ANNOTATIONS.json')!=pre['annotation_sha256']:raise RuntimeError('Geometry inventory changed')
 q=load(B/'attempt-3-v7.2/QUALIFICATION.json')
 if sha(B/'attempt-3-v7.2/QUALIFICATION.json')!=pre['harness_qualification_sha256'] or q['status']!='QUALIFIED_V7.2_ON_DECLARED_SCOPE' or not all(q['gates'].values()):raise RuntimeError('Current Part A qualification gate failed')
 if sha(B/'BUDGET.json')!=pre['budget_sha256']:raise RuntimeError('Budget changed; recheck before continuing')
 if len(plan['planned_looks'])+plan['previous_feature_looks']>plan['look_cap']:raise RuntimeError('Look cap exceeded')
 return plan,pre

def adapt(plan):
 allowed={x['unit']:x for x in plan['units']};metadata=load(R/'METADATA-INVENTORY.json')
 uncertain_bases={}
 for u in metadata['units']:
  for reading,locs in u['HF_locators'].items():
   uncertain_bases[(u['unit'],reading)]={re.match(r'[0-9]+',n)[0] for n in locs if re.fullmatch(r'[0-9]+[a-z]+',n)}
 rows=[];excluded=[];heads=collections.Counter();audit=collections.Counter();rawcounts=collections.Counter();records=[]
 with Path(plan['source_evt']).open('rb') as f:
  for lineno,b in enumerate(f,1):
   m=re.match(rb'^<(f[0-9]+[rv][0-9]*)[.]([^.]+)[.]([^;]+);([A-Z])>',b)
   if not m:continue
   folio,unitcode,num,reading=[x.decode('ascii') for x in m.groups()]
   if folio in plan['reserved_signs']:
    audit['reserved_headers_skipped_before_payload_decode']+=1;continue
   if reading not in plan['reading_codes']:
    audit['nonHF_headers_skipped_before_payload_decode']+=1;continue
   unit=folio+'.'+unitcode
   if unit not in allowed:
    audit['out_of_scope_headers_skipped_before_payload_decode']+=1;continue
   cfg=allowed[unit];category=cfg['set'];locus=unit+'.'+num
   heads[(unit,reading)]+=1;rawcounts[(category,reading)]+=1
   base=re.match(r'[0-9]+',num)
   if category!='paragraph' and (not re.fullmatch(r'[0-9]+',num) or (base and base[0] in uncertain_bases[(unit,reading)])):
    excluded.append(dict(id=locus,unit=unit,folio=folio,reading=reading,set=category,source_line=lineno,reason='UNRESOLVED_MULTILINE_OR_INSERTED_LOCUS_GROUP',payload_decoded=False));continue
   payload=b[m.end():].decode('latin1').strip();audit['allowed_payloads_decoded']+=1
   words=tokens(payload)
   records.append(dict(locus=locus,reading=reading,unit=unit,folio=folio,set=category,source_line=lineno,raw=payload,word_slots=words))
   if category=='paragraph':
    for i,w in enumerate(words):
     rec=dict(id=locus+'#'+str(i),unit=unit,folio=folio,reading=reading,set=category,source_line=lineno)
     if w:rows.append(dict(**rec,words=[w]))
     else:excluded.append(dict(**rec,reason='UNCERTAIN_OR_UNREADABLE_WORD_SLOT',payload_decoded=True))
   else:
    rec=dict(id=locus,unit=unit,folio=folio,reading=reading,set=category,source_line=lineno)
    if words and all(words):rows.append(dict(**rec,words=words))
    else:excluded.append(dict(**rec,reason='INCOMPLETE_OR_UNCERTAIN_LABEL',word_slots=words,payload_decoded=True))
 coverage=[]
 for unit,cfg in allowed.items():
  for reading in plan['reading_codes']:
   expected=cfg['HF_header_counts'][reading];seen=heads[(unit,reading)]
   if expected!=seen:raise RuntimeError('Header coverage differs from frozen metadata '+unit+reading)
   a=[r for r in rows if r['unit']==unit and r['reading']==reading]
   e=[r for r in excluded if r['unit']==unit and r['reading']==reading]
   coverage.append(dict(unit=unit,folio=cfg['folio'],set=cfg['set'],reading=reading,source_records=seen,admitted_items=len(a),excluded_items=len(e),exclusions_by_reason=dict(collections.Counter(x['reason'] for x in e))))
 if any(r['folio'] in plan['reserved_signs'] or r['reading'] not in plan['reading_codes'] for r in records+rows+excluded):raise RuntimeError('Forbidden payload admitted')
 save('ADMITTED-ROWS.json',rows);save('ALLOWED-SOURCE-RECORDS.json',records);save('EXCLUSIONS.json',excluded)
 save('COVERAGE.json',dict(by_unit=coverage,readings={a:{s:dict(source_records=rawcounts[(s,a)],admitted_items=sum(r['set']==s and r['reading']==a for r in rows),excluded_items=sum(r['set']==s and r['reading']==a for r in excluded)) for s in ('zodiac','zodiac-extra','star','plant-jar','rosette','paragraph')} for a in ('H','F')},adapter_audit=dict(audit),source_container_policy='Monolithic EVT streamed as bytes; reserved payloads were never decoded, retained, displayed or scored. No reserved-only file or image was opened.',all_output_rows_open_only=True,source_band_registration='Source-defined unit groups; not newly validated unique figure-to-label ownership.'))
 return rows

def main():
 plan,pre=verify_gates()
 if (R/'C2-PRETEST.json').exists():
  print(json.dumps(dict(status='EXISTING_RESULT_NO_RESCORING',result='C2-PRETEST.json')));return
 if (R/'ADMITTED-ROWS.json').exists():rows=load(R/'ADMITTED-ROWS.json')
 else:rows=adapt(plan)
 looks=[]
 log=load(R/'LOOK-LOG.json')
 for feature in plan['planned_looks']:
  n=feature['look'];artifact='LOOK-%02d.json'%n
  if (R/artifact).exists():
   look=load(R/artifact)
   if look['feature']!=feature:raise RuntimeError('Checkpoint feature mismatch')
   looks.append(look)
   if not any(x['look']==n and x['status']=='COMPLETED' for x in log['looks']):raise RuntimeError('Checkpoint exists without completed ledger; manual audit required')
   continue
  if any(x['look']==n for x in log['looks']):raise RuntimeError('Started look has no completed checkpoint; do not silently repeat')
  if log['looks_used']>=plan['look_cap']:raise RuntimeError('Ten-look cap reached')
  log['looks_used']+=1
  entry=dict(look=n,feature=feature,status='STARTED',started_utc=now(),rows_sha256=sha(R/'ADMITTED-ROWS.json'),plan_sha256=sha(R/'PLAN.json'))
  log['looks'].append(entry);save('LOOK-LOG.json',log)
  look=compute_look(rows,feature,plan);save(artifact,look)
  entry.update(status='COMPLETED',completed_utc=now(),result=artifact,result_sha256=sha(R/artifact))
  save('LOOK-LOG.json',log);looks.append(look)
 result=summarize(looks,plan);result.update(completed_utc=now(),plan_sha256=sha(R/'PLAN.json'),source_set_freeze_sha256=pre['source_set_freeze_sha256'],look_results=[dict(path='LOOK-%02d.json'%f['look'],sha256=sha(R/('LOOK-%02d.json'%f['look']))) for f in plan['planned_looks']])
 save('C2-PRETEST.json',result)
 print(json.dumps({k:result[k] for k in ('status','joint_marker_outcome','looks_used','look_cap','readings','vault_open')},ensure_ascii=False))
if __name__=='__main__':main()
