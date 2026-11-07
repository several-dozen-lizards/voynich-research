"""Image labels + geometry + readability masks only. No EVT/text/features loader."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,hashlib,itertools
P=Path(__file__).parent;ROOT=P.parent
LABELS=('PL','VE','FG','CE','OT','NO')
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def csvread(rel):
 with (ROOT/rel).open(encoding='utf-8',newline='') as f:return {r['shared_line_id']:r for r in csv.DictReader(f)}
def design(rows,left=('FG','VE'),right=('PL','NO')):
 totals=defaultdict(lambda:[0,0]);strata=defaultdict(lambda:[0,0])
 for r in rows:
  group=0 if r['label'] in left else 1 if r['label'] in right else None
  if group is None:continue
  totals[r['folio']][group]+=r['n'];strata[(r['folio'],r['length_bin'])][group]+=r['n']
 eligible={f for f,(a,b) in totals.items() if a>=30 and b>=30};weights=defaultdict(float)
 for (f,bin),(a,b) in strata.items():
  if f in eligible and a and b:weights[f]+=a*b/(a+b)
 total=sum(weights.values());maxw=max(weights.values())/total if total else None
 return dict(exposure_eligible_folios=len(eligible),informative_folios=len(weights),maximum_folio_weight=maxw,eligible=sorted(eligible),weights={f:w/total for f,w in weights.items()},exposures={f:{'left':a,'right':b} for f,(a,b) in sorted(totals.items())},design_gate=len(weights)>=8 and maxw is not None and maxw<=.25)
def main():
 freeze=read('t1-label-support-controls-2026-10-25/LABEL-RESOLUTION-FREEZE.json')
 for rel,sha in freeze['source_hashes'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha,rel
 agreement=read('continuation-v73-wrap-ratings-bc-2026-10-25/ratings/AGREEMENT-COMPLETED.json');assert agreement['paired_physical_lines']==1145 and agreement['G6']['pass_gate'] and agreement['G2']['pass_gate']
 base='continuation-v73-wrap-ratings-bc-2026-10-25/ratings/';a=csvread(base+'LINE-CONTEXT-A-COMPLETED.csv');b=csvread(base+'LINE-CONTEXT-B-COMPLETED.csv');geo=read('image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines'];wrap={r['shared_line_id']:r for r in read('continuation-v73-wrap-ratings-bc-2026-10-25/wrap/WRAP-FLAGS.json')['rows']}
 assert set(a)==set(b)=={r['shared_line_id'] for r in geo}
 labels={};resolution=[]
 for r in geo:
  lid=r['shared_line_id'];assert r['folio'] not in {'f72v1','f72v2','f73r','f73v'};x,y=a[lid]['label'],b[lid]['label'];assert x in LABELS and y in LABELS
  label=x if x==y else None;labels[lid]=label;resolution.append(dict(id=lid,label=label,A=x,B=y,status='CONSENSUS' if label else 'UNRESOLVED_DISAGREEMENT'))
 masks=read('t1-label-support-controls-2026-10-25/READABILITY-MASKS.json');allowed={'id','folio','reading','locus','available','reason','original_slots','initial_slot_present','initial_readable','noninitial_mask'}
 byread={};support={}
 for reading in ('H','F'):
  rows=[];excluded=[];audit=Counter();gm={r['shared_line_id']:r for r in geo}
  for source in masks['rows']:
   assert set(source)<=allowed
   if source['reading']!=reading:continue
   lid=source['id'];label=labels[lid]
   if not source['available']:audit['unavailable_reading_lines']+=1;excluded.append(dict(id=lid,reason=source['reason']));continue
   mask=source['noninitial_mask'];assert all(type(v) is bool for v in mask);audit['all_registered_readable_noninitial']+=sum(mask);audit['all_registered_unknown_noninitial']+=len(mask)-sum(mask)
   if label is None:audit['unresolved_image_lines']+=1;excluded.append(dict(id=lid,reason='IMAGE_LABEL_DISAGREEMENT'));continue
   g=gm[lid];row=dict(id=lid,folio=source['folio'],reading=reading,label=label,length_bin=wrap[lid]['length_bin'],n=sum(mask),unknown=len(mask)-sum(mask),mask=mask,original_slots=source['original_slots'],initial_readable=source['initial_readable'],block_id=g['block_id'],line_number=g['line_number'])
   rows.append(row);audit['consensus_lines']+=1;audit['readable_noninitial_slots']+=row['n'];audit['unknown_noninitial_slots']+=row['unknown'];audit['physical_initial_slots_excluded']+=int(source['initial_slot_present'])
  strata=defaultdict(Counter)
  for r in rows:strata[(r['folio'],r['length_bin'])][r['label']]+=r['n']
  scanfolios={f for (f,bin),ex in strata.items() if sum(v>0 for v in ex.values())>=2}
  pairs={a+':'+b:design(rows,(a,),(b,)) for a,b in itertools.combinations(LABELS,2)}
  support[reading]=dict(audit=dict(audit),by_label={label:dict(lines=sum(r['label']==label for r in rows),slots=sum(r['n'] for r in rows if r['label']==label)) for label in LABELS},primary=design(rows),scan_design_upper_bound_folios=len(scanfolios),scan_possible_folios=sorted(scanfolios),equivalence_pair_design=pairs,equivalence_all15_design_gate=all(v['design_gate'] for v in pairs.values()),excluded=excluded,real_class_counts_computed=False)
  byread[reading]=rows
 result=dict(status='OUTCOME_BLIND_SUPPORT_COMPLETE',full_rating_population=1145,consensus_physical_lines=sum(v is not None for v in labels.values()),unresolved_physical_lines=sum(v is None for v in labels.values()),label_rule='Exact A/B agreement only; unresolved never NO',readings=support,word_class_outcome_join=False,vault='CLOSED')
 for name,obj in [('LABELS.json',resolution),('SUPPORT-ROWS.json',byread),('SUPPORT.json',result)]: (P/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='readings'}));print(json.dumps({reading:{'audit':s['audit'],'primary':s['primary'],'scan_upper_bound':s['scan_design_upper_bound_folios'],'equivalence_design':s['equivalence_all15_design_gate']} for reading,s in support.items()}))
if __name__=='__main__':main()
