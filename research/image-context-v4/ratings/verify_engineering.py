"""Authored controls only: distance/ties, normalization, missing data and Cohen kappa."""
from pathlib import Path
import json,copy,hashlib
from agreement import validate_response,assign,kappa,CATS
R=Path(__file__).resolve().parent
def main():
 d=dict(completed=True,pictures=[dict(box=[.2,.2,.2,.2],category='PL',note='authored fixture')]);validate_response(d)
 failures=0
 for fn in [lambda x:x.update(completed=False),lambda x:x['pictures'][0].update(box=[-.1,0,.2,.2]),lambda x:x['pictures'][0].update(box=[0,0,0,.2]),lambda x:x['pictures'][0].update(box=[0,0,float('nan'),.2]),lambda x:x['pictures'][0].update(category='NO'),lambda x:x['pictures'].append(dict(box=[.2,.2,.2,.2],category='VE',note='conflict'))]:
  x=copy.deepcopy(d);fn(x)
  try:validate_response(x)
  except ValueError:failures+=1
 assert failures==6
 line=dict(box=[0,0,10,10]);assert assign(line,[],100,100)['label']=='NO'
 assert assign(line,[dict(box=[.3,0,.1,.1],category='VE')],100,100)['label']=='VE' # edge distance20 = exactly2 heights
 assert assign(line,[dict(box=[.301,0,.1,.1],category='VE')],100,100)['label']=='NO'
 assert assign(line,[dict(box=[.05,.05,.1,.1],category='FG')],100,100)['distance_line_heights']==0
 # Edge-tied category decisions depend on proximity, not input order or a PL preference.
 pictures=[dict(box=[.05,.05,.8,.8],category='PL'),dict(box=[.05,.05,.1,.1],category='VE')]
 assert assign(line,pictures,100,100)['label']==assign(line,list(reversed(pictures)),100,100)['label']=='VE'
 assert kappa(CATS,CATS,CATS)['kappa']==1
 assert kappa(['PL','PL','NO','NO'],['PL','NO','PL','NO'],CATS)['kappa']==0
 assert kappa(['PL','NO'],['NO','PL'],CATS)['kappa']==-1
 assert kappa(['NO','NO'],['NO','NO'],CATS)['kappa'] is None
 assert kappa([],[],CATS)['kappa'] is None
 # Exact0.60 threshold, not rounded headline comparison.
 assert kappa(['PL']*5+['NO']*5,['PL']*4+['NO']+['PL']+['NO']*4,CATS)['exact_kappa']=='3/5'
 out=dict(status='PASS_ENGINEERING_ONLY; NOT MODEL_COORDINATE_QUALIFICATION',invalid_responses_rejected=failures,distance_and_tie_cases=5,kappa_cases=6,scientific_responses_generated=0,adjudication='NOT RUN')
 (R/'ENGINEERING.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
