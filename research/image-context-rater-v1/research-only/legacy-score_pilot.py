"""Score actual exported responses; no fabricated scientific outcomes."""
from run_topic import *
def score(data):
    key=read(ROOT/'pilot-frozen-key.json');ready={x['trial_id']:x for x in key['trials'] if x['status']=='PAGE_SCREEN_READY'}
    if not data.get('rater_id') or data.get('prior_exposure') not in ('yes','no'):raise ValueError('Rater and prior-exposure declaration required')
    rr=data.get('responses',[])
    if len(rr)!=len(ready) or {x['trial_id'] for x in rr}!=set(ready):raise ValueError('Exactly one response for every released screen required')
    if len({x['trial_id'] for x in rr})!=len(rr):raise ValueError('Duplicate trial')
    outcomes=[];dist=np.array([1.]);hits=0
    for o in rr:
        t=ready[o['trial_id']];choice=o.get('choice')
        if choice not in tuple('ABCDEF')+('none','unreadable'):raise ValueError('Invalid choice')
        if str(o.get('confidence')) not in ('0','1','2','3'):raise ValueError('Confidence0..3 required')
        if not o.get('evidence','').strip() or not o.get('contradictions','').strip():raise ValueError('Evidence and contradictory features required')
        if o.get('recognized') not in ('yes','no'):raise ValueError('Recognition declaration required')
        hit=int(choice in t['correct_choices']);hits+=hit;p=len(t['correct_choices'])/6;dist=np.convolve(dist,[1-p,p])
        outcomes.append({'trial_id':o['trial_id'],'source_page':t['source_page'],'choice':choice,'chosen_page':t['choices'].get(choice),'hit':hit,'conditional_chance':p,'blind_eligible':data['prior_exposure']=='no' and o['recognized']=='no','rater_record':o})
    return {'rater_id':data['rater_id'],'actual_response_required':True,'screens':len(rr),'hits':hits,'per_screen':outcomes,
      'conditional_uniform_choice_tail_reference':float(dist[hits:].sum()),'reference_only_not_confirmatory':True,'independent_numbered_source_folios':len({int(re.search(r'\d+',x['source_page'])[0]) for x in outcomes}),
      'limits':['Exploratory source-page screen; not a specific label/plant-name test.','Two released references share one numbered folio; no independent-document significance claim.','Recognition, style, composite image content and non-random discovery selection can confound visual correspondence.']}
def main():
    if len(sys.argv)!=2:raise SystemExit('Usage: python score_pilot.py actual-pilot-responses.json')
    p=Path(sys.argv[1]);result=score(read(p));dump('actual-pilot-score.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
