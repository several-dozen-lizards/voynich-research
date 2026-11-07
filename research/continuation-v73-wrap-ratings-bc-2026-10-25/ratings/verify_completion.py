import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction
from collections import Counter
import json,csv,hashlib
P=Path(__file__).parent;ROOT=P.parents[1];OLD=ROOT/'image-context-v4/ratings'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=read(P/'AGREEMENT-COMPLETED.json');checks={};seal=read(OLD/'AGREEMENT-FINAL-SEAL.json')
checks['legacy_1357_files_intact']=all(sha(OLD/n)==s for group in ('files','data') for n,s in seal[group].items())
checks['same_population_full_pairs']=report['registered_physical_lines']==report['paired_physical_lines']==1145 and report['added_line_pairs']==233
checks['no_original_accepted_replacement']=all(not (OLD/'responses'/r['role']/(r['task_id']+'.json')).exists() for r in report['selection'])
checks['first_valid_only']=True;checks['raw_transport_matches']=True;checks['rater_isolation']=True
sessions=[];costs=[]
for selection in report['selection']:
 path=ROOT/selection['response_path'];record=read(path);assert sha(path)==selection['response_sha256'];sessions.append(record['session_id']);phase=selection['phase'];task=record['task_id'];role=record['role'];wave=path.parents[2]
 raw=wave/'raw'/role/(task+'.jsonl');events=[]
 for line in raw.read_text(encoding='utf-8').splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 init=next(e for e in events if e.get('type')=='system' and e.get('subtype')=='init');final=next(e for e in reversed(events) if e.get('type')=='result')
 checks['rater_isolation'] &= init['model']==record['model'] and init['tools']==['StructuredOutput'] and init['mcp_servers']==[] and not init.get('skills') and not init.get('plugins')
 for e in events:
  for c in e.get('message',{}).get('content',[]):
   if c.get('type')=='tool_use':checks['rater_isolation'] &= c.get('name')=='StructuredOutput'
 original=final['structured_output'];converted=record['annotation']
 if phase=='corners':
  expect=json.loads(json.dumps(original))
  for p in expect['pictures']:
   l,t,r,b=p['box'];p['box']=[l,t,r-l,b-t]
  checks['raw_transport_matches'] &= expect==converted
 else:checks['raw_transport_matches'] &= original==converted
 phasecalls=read(P/phase/'CALLS.json');matching=[r for r in phasecalls if r['role']==role and r['task_id']==task and r['accepted']];checks['first_valid_only'] &= len(matching)==1
checks['fresh_selected_sessions']=len(sessions)==len(set(sessions))==19
checks['explicit_corner_authorization']=read(P/'corners/HUMAN-AUTHORIZATION.json')['answer']=='Approve corner-coordinate completion'
# Independent Fraction recomputation from emitted physical-line labels.
labels={}
for role in ('A','B'):
 with (P/f'LINE-CONTEXT-{role}-COMPLETED.csv').open(encoding='utf-8',newline='') as f:labels[role]={r['shared_line_id']:r['label'] for r in csv.DictReader(f)}
checks['no_duplicate_or_missing_label_rows']=len(labels['A'])==len(labels['B'])==1145 and set(labels['A'])==set(labels['B'])
def exact_kappa(binary):
 pairs=[(('PL' if x=='PL' else 'not-PL'),('PL' if labels['B'][i]=='PL' else 'not-PL')) if binary else (x,labels['B'][i]) for i,x in labels['A'].items()]
 n=len(pairs);left=Counter(x for x,y in pairs);right=Counter(y for x,y in pairs);agree=sum(x==y for x,y in pairs);pe=sum(Fraction(left[c]*right[c],n*n) for c in left);return (Fraction(agree,n)-pe)/(1-pe)
checks['independent_G6_exact']=str(exact_kappa(False))==report['G6']['exact_kappa'];checks['independent_G2_exact']=str(exact_kappa(True))==report['G2']['exact_kappa'];checks['gates_on_full_population']=all(g['pass_gate']==(Fraction(g['exact_kappa'])>=Fraction(3,5)) for g in (report['G6'],report['G2']))
for phase in ('transport-repair','corners'):
 for p in (P/phase).glob('wave-*/attempts/*/*.json'):
  z=read(p)
  if z.get('provider_cost_estimate_usd') is not None:costs.append(z['provider_cost_estimate_usd'])
out=dict(status='VERIFIED' if all(checks.values()) else 'FAIL',checks=checks,selected_completion_responses=19,provider_reported_completion_cost_usd=sum(costs),cost_coverage='Includes reported costs for all38 repaired xywh attempts plus5 corner calls; initial57 permission-failure costs unreported, not assumed zero.',G6_exact=report['G6']['exact_kappa'],G2_exact=report['G2']['exact_kappa'],T1_join='CLOSED',vault='CLOSED')
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2));sys.exit(not all(checks.values()))
