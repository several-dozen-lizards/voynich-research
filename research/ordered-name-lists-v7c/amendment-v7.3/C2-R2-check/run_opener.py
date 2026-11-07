import re,json,hashlib,collections,datetime,os,sys
from pathlib import Path
from c2_roles import tokens,compute_look,choose
R=Path(__file__).parent;V=R.parent;B=V.parent;C2=B/'C2-open-v1'
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):
 p=R/n;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,indent=2)+'\n');os.replace(t,p)
def main():
 p=load(R/'PLAN.json');freeze=load(R/'CODE-FREEZE.json');choice=load(V/'R2-CHOICE-FREEZE.json')
 for f,h in freeze['files'].items():assert sha(R/f)==h,f
 assert sha(V/'R2-CHOICE-FREEZE.json')==p['choice_freeze_sha256']
 assert sha(V/'AMENDMENT-FREEZE.json')==p['amendment_freeze_sha256']
 assert sha(C2/'c2_engine.py')==p['old_engine_sha256']
 assert sha(C2/'C2-PRETEST.json')==p['old_H_result_sha256']
 assert sha(C2/'LOOK-LOG.json')==p['old_look_log_sha256']
 assert choice['PartC_and_B']['code']==p['selected_source_code'] and choice['PartC_and_B']['half_H_gate']
 assert sha(p['source_evt'])==p['expected_evt_sha256']
 if (R/'RESULT.json').exists():print('EXISTING_RESULT_NO_RESCORING');return
 units={u['unit']:u for u in p['units'] if u['set']!='paragraph'}
 code=p['selected_source_code'];headers=[];bad=collections.defaultdict(set)
 with Path(p['source_evt']).open('rb') as inp:
  for lineno,b in enumerate(inp,1):
   m=re.match(rb'^<(f[0-9]+[rv][0-9]*)[.]([^.]+)[.]([^;]+);([A-Z])>',b)
   if not m:continue
   folio,u,n,c=[s.decode('ascii') for s in m.groups()];unit=folio+'.'+u
   if folio in p['reserved_signs'] or unit not in units or c!=code:continue
   headers.append((unit,n))
   if re.fullmatch(r'[0-9]+[a-z]+',n):bad[unit].add(re.match(r'[0-9]+',n)[0])
 rows=[];excluded=[];audit=collections.Counter();source_records=[]
 with Path(p['source_evt']).open('rb') as inp:
  for lineno,b in enumerate(inp,1):
   m=re.match(rb'^<(f[0-9]+[rv][0-9]*)[.]([^.]+)[.]([^;]+);([A-Z])>',b)
   if not m:continue
   folio,u,n,c=[s.decode('ascii') for s in m.groups()];unit=folio+'.'+u
   if folio in p['reserved_signs']:audit['reserved_before_payload_decode']+=1;continue
   if unit not in units or c!=code:continue
   category=units[unit]['set'];locus=unit+'.'+n
   rec=dict(id=locus,unit=unit,folio=folio,set=category,reading='R2',source_reading=code,source_line=lineno)
   base=re.match(r'[0-9]+',n)
   if not re.fullmatch(r'[0-9]+',n) or (base and base[0] in bad[unit]):
    excluded.append(dict(**rec,reason='UNRESOLVED_MULTILINE_OR_INSERTED_LOCUS_GROUP',payload_decoded=False));continue
   payload=b[m.end():].decode('latin1').strip();audit['selected_R2_payloads_decoded']+=1
   words=tokens(payload);source_records.append(dict(**rec,raw=payload,word_slots=words))
   if words and all(words):rows.append(dict(**rec,words=words))
   else:excluded.append(dict(**rec,reason='INCOMPLETE_OR_UNCERTAIN_LABEL',payload_decoded=True))
 assert all(x['source_reading']==code and x['folio'] not in p['reserved_signs'] for x in rows+source_records)
 save('ROWS.json',rows);save('EXCLUSIONS.json',excluded);save('SOURCE-RECORDS.json',source_records)
 save('COVERAGE.json',dict(headers=len(headers),admitted_by_set=dict(collections.Counter(x['set'] for x in rows)),excluded_by_reason=dict(collections.Counter(x['reason'] for x in excluded)),by_panel={f:sum(x['folio']==f and x['set']=='zodiac' for x in rows) for f in p['open_signs']},audit=dict(audit),first_new_R2_decode_after_choice_freeze=True,choice_freeze_utc=choice['utc'],decode_completed_utc=now()))
 ledger_path=V/'COMBINED-C2-LOOK-LOG.json'
 log=load(ledger_path)
 assert log['looks_used']==5 and log['look_cap']==10 and not any(x['look']==6 for x in log['looks'])
 entry=dict(look=6,feature=p['planned_looks'][0],reading_role='R2',source_code=code,status='STARTED',started_utc=now(),rows_sha256=sha(R/'ROWS.json'),plan_sha256=sha(R/'PLAN.json'))
 log['looks'].append(entry);log['looks_used']+=1
 ledger_path.write_text(json.dumps(log,indent=2)+'\n')
 look=compute_look(rows,p['planned_looks'][0],p);save('LOOK-06.json',look)
 best=choose([look],'R2','opener');winner=best if best and best['exceeds_two'] else None
 h=load(C2/'C2-PRETEST.json')['readings']['H']['M_star']
 reproduced=bool(winner and h and winner['value']==h['value']=='ok' and winner['removal_operation']==h['removal_operation'])
 result=dict(version='v7.3',reading_role='R2',source_code=code,best_opener=best,M_star=winner,H_M_star_preserved=h,R2_reproduces_ok=reproduced,C_MRK_disposition='RETAIN_CONDITIONAL' if reproduced else 'DROP_NO_R2_REPRODUCTION',looks_used=6,look_cap=10,suffix_arm='DROPPED_NO_REPLACEMENT',paragraph_tests_keep_HF=True,vault_open=False,C3_scored=False,completed_utc=now())
 entry.update(status='COMPLETED',completed_utc=now(),result='C2-R2-check/LOOK-06.json',result_sha256=sha(R/'LOOK-06.json'))
 ledger_path.write_text(json.dumps(log,indent=2)+'\n');save('RESULT.json',result)
 print(json.dumps(result))
if __name__=='__main__':main()
