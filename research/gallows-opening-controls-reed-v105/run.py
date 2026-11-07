from pathlib import Path
import collections,hashlib,html,json,math,re
R=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=load(R/'INPUT-FREEZE.json')
assert all(sha(Path(p))==h for p,h in frozen.items())
events=load(R.parent/'fp-boundary-transfer-reed-v102/PROSE-EVENTS.json')
protocol=load(R/'PROTOCOL.json')
save('METHOD-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',R/'INPUT-FREEZE.json']})

def frame(w):
    if re.search('cth|ckh|cph|cfh',w):return None,'benched'
    indices=[i for i,c in enumerate(w) if c in 'ktfp']
    if len(indices)!=1:return None,'no_gallows' if not indices else 'multiple_gallows'
    i=indices[0];return (w[:i]+'_'+w[i+1:],w[i],i),None

def estimate(a,b,c,d):
    # Opening class A/B then continuation A/B.
    n=a+b;m=c+d
    if not n or not m or not a+c or not b+d:return None
    return {'gap':a/n-c/m,'weight':n*m/(n+m),'opening_A':a/n,'continuation_A':c/m}

checks=[estimate(3,1,1,3)['gap']==.5,estimate(1,3,3,1)['gap']==-.5,
        estimate(2,2,2,2)['gap']==0,estimate(2,0,3,0) is None,
        estimate(3,1,2,6)['weight']==8/3,
        frame('qopchedy')[0]==('qo_chedy','p',2),frame('cfhedy')[1]=='benched',
        frame('pchek')[1]=='multiple_gallows',frame('chey')[1]=='no_gallows']
assert all(checks)
exclusions=collections.Counter();usable=[]
for x in events:
    if x['n']<2:exclusions[x['tr']+'_short_lines']+=1;continue
    f,reason=frame(x['word'])
    if reason:exclusions[x['tr']+'_'+reason]+=1;continue
    masked,ch,offset=f
    assert masked.replace('_',ch)==x['word']
    usable.append({**x,'frame':masked,'gallows':ch,'offset':offset})
save('SINGLE-GALLOWS-EVENTS.json',usable)
save('EXCLUSIONS.json',dict(exclusions))

pairings=protocol['frozen_comparisons']['pairings']
def panel(tr,aa,bb,position,view,split):
    buckets=collections.defaultdict(lambda:{'opening':[],'continuation':[]})
    for x in usable:
        if x['tr']!=tr or x['split']!=split or (x['index']==0)!=(position=='first'):continue
        if x['gallows'] not in aa+bb:continue
        if view=='shared_structure' and not x['paired_structure']:continue
        key=(x['page'],x['hand'],x['language'],x['section'],x['frame'],x['index'])
        if view=='exact_line_length':key+=(x['n'],)
        buckets[key]['opening' if x['opening'] else 'continuation'].append(x)
    cells=[];pages=collections.defaultdict(list);unmatched=collections.Counter()
    for key,bs in sorted(buckets.items()):
        op=bs['opening'];co=bs['continuation']
        a=sum(x['gallows'] in aa for x in op);b=len(op)-a
        c=sum(x['gallows'] in aa for x in co);d=len(co)-c
        e=estimate(a,b,c,d)
        why='informative' if e else 'missing_position' if not op or not co else 'single_class'
        unmatched[why]+=1
        cell={'key':key,'counts':[a,b,c,d],'status':why,'estimate':e,
              'opening_events':[(x['loc'],x['index'],x['word']) for x in op],
              'continuation_events':[(x['loc'],x['index'],x['word']) for x in co]}
        cells.append(cell)
        if e:pages[key[0]].append(e)
    page_effects=[]
    for page,es in sorted(pages.items()):
        weight=sum(x['weight'] for x in es);gap=sum(x['gap']*x['weight'] for x in es)/weight
        page_effects.append({'page':page,'gap':gap,'cells':len(es),'cell_weight':weight})
    gap=sum(x['gap'] for x in page_effects)/len(page_effects) if page_effects else None
    return {'transcriber':tr,'A':aa,'B':bb,'position':position,'view':view,'split':split,
            'gap':gap,'eligible_pages':len(page_effects),'informative_cells':sum(x['status']=='informative' for x in cells),
            'cell_status_counts':dict(unmatched),'positive_pages':sum(x['gap']>0 for x in page_effects),
            'negative_pages':sum(x['gap']<0 for x in page_effects),'tie_pages':sum(x['gap']==0 for x in page_effects),
            'page_effects':page_effects,'cells':cells}

training=[panel(tr,a,b,pos,view,'train') for tr in ['H','F'] for a,b in pairings
          for pos in ['first','other'] for view in ['main','exact_line_length','shared_structure']]
save('TRAINING-RESULTS.json',training)
directions=[{'transcriber':p['transcriber'],'A':p['A'],'B':p['B'],'position':p['position'],'view':p['view'],
             'training_gap':p['gap'],'direction':None if p['gap'] is None else 1 if p['gap']>0 else -1 if p['gap']<0 else 0}
            for p in training]
save('FROZEN-TRAINING-DIRECTIONS.json',directions)
save('TRAINING-FREEZE.json',{n:sha(R/n) for n in ['METHOD-FREEZE.json','TRAINING-RESULTS.json','FROZEN-TRAINING-DIRECTIONS.json']})

test=[panel(tr,a,b,pos,view,'test') for tr in ['H','F'] for a,b in pairings
      for pos in ['first','other'] for view in ['main','exact_line_length','shared_structure']]
save('TEST-RESULTS.json',test)
summary=[]
for tr,te,d in zip(training,test,directions):
    assert all(tr[k]==te[k]==d[k] for k in ['transcriber','A','B','position','view'])
    summary.append({k:tr[k] for k in ['transcriber','A','B','position','view']}|{
        'training':{k:tr[k] for k in ['gap','eligible_pages','informative_cells','positive_pages','negative_pages','tie_pages']},
        'test':{k:te[k] for k in ['gap','eligible_pages','informative_cells','positive_pages','negative_pages','tie_pages']},
        'direction_agrees':None if tr['gap'] is None or te['gap'] is None or not d['direction'] else te['gap']*d['direction']>0})
save('SUMMARY.json',summary)
trainfol={re.match(r'f\d+',x['page'])[0] for x in events if x['split']=='train'}
testfol={re.match(r'f\d+',x['page'])[0] for x in events if x['split']=='test'}
assert not trainfol&testfol
verification={'arithmetic_and_frame_checks':len(checks),'all_checks_passed':all(checks),
    'train_test_numbered_folios_disjoint':not bool(trainfol&testfol),
    'all_original_word_frames_reconstruct':all(x['frame'].replace('_',x['gallows'])==x['word'] for x in usable),
    'inputs_unchanged':all(sha(Path(p))==h for p,h in frozen.items()),
    'training_freeze_unchanged':all(sha(R/n)==h for n,h in load(R/'TRAINING-FREEZE.json').items()),
    'panel_count':len(summary),'known_limit':'Arithmetic and provenance checks only; no statistical null qualification or untouched validation.'}
save('VERIFICATION.json',verification)
for s in summary:
    if s['view']=='main':print(json.dumps(s))
