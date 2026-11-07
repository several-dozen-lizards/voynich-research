from pathlib import Path
import json,re,math,collections,hashlib,random,sys,html
R=Path(__file__).resolve().parent;P=R.parent;SOURCE=P/'frequency-atlas-v48/rows.json'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fol(page):return re.match(r'f\d+',page)[0]
def train(words):
 c=collections.Counter();tot=collections.Counter();v=set('$')
 for w in words:
  v.update(w)
  for a,b in zip('^'+w,w+'$'):c[a+b]+=1;tot[a]+=1
 return {'pairs':dict(c),'totals':dict(tot),'alphabet':sorted(v|{'?'})}
def score(w,m):
 v=len(m['alphabet']);return -sum(math.log((m['pairs'].get(a+b,0)+.5)/(m['totals'].get(a,0)+.5*v)) for a,b in zip('^'+w,w+'$'))/(len(w)+1)
def paneldata():
 rows=load(SOURCE);cov=collections.defaultdict(set)
 for r in rows:cov[r[6]].add(r[0])
 eligible=[r for r in rows if cov[r[6]]=={'H','F'}];fs=sorted({fol(r[1]) for r in eligible},key=lambda x:sha_text('v65:'+x));training=set(fs[::2]);testing=set(fs[1::2]);panels=collections.defaultdict(lambda:{'train':[],'test':[]})
 for r in eligible:panels['|'.join([r[0],r[3],r[4],r[2],r[5]])]['train' if fol(r[1]) in training else 'test'].append(r)
 return panels,{'training':sorted(training),'test':sorted(testing)}
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def sign_test(vals,seed):
 rng=random.Random(seed);obs=sum(vals)/len(vals);tail=sum(sum(v*rng.choice((-1,1)) for v in vals)/len(vals)>=obs-1e-12 for _ in range(999));return obs,(tail+1)/1000
stage=sys.argv[1]
if stage=='freeze':
 protocol={'scope':'Shared H/F loci only. Global numbered-folio split by sha256(v65:folio), alternating train/test, same for both readings and every stratum. Hand, Currier, section and raw format separate. Earlier analyses saw corpus: retrospective validation, not untouched discovery.', 'model':'Add-half character-bigram language model with word-start and word-end boundaries. Mean negative log probability per transition. EVA characters are transcription symbols, not phonemes or indivisible manuscript glyphs. Unknown tokens excluded, barriers preserved. Train each stratum separately; >=3 training folios and >=200 readable tokens.', 'ranking':'Held-out types scored under frozen model. Within each stratum compare only distinct held-out types of EXACT same EVA length and EXACT training word count (zero includes unseen types). >=5 other types needed for percentile. Top10 by matched percentile then surprise for display only; all tokens/types including unsupported retained. Percentiles are exploratory, not p values.', 'test':'Predeclared first-source-token versus interior-source-token anomaly comparison within each held-out numbered folio and exact length/training-frequency cell. Exclude final/single/unknown anchors. Average matched cell differences equally within folio; >=5 matched folios per stratum. One-sided folio sign-flip999, Bonferroni all eligible H/F panels. Descriptive cell weighting; sign symmetry is an assumption. No cross-format test or paragraph-start inference. Exact repeat word types may appear in both folds; training frequency controlled, not type-disjoint.', 'qualification':'Before manuscript scoring, fixed synthetic templatic language with held-out typical and unusual strings; score must rank all unusual over typical. This is engineering qualification only, not calibrated realism or semantic validation.', 'exceptions':'Retain all scores, missing coverage, unseen forms, unrankable types, joined/split H/F line alternatives and non-significant panels. No phonetic assumption, no adapted thresholds after test results.'}
 save('PROTOCOL.json',protocol);save('METHOD-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SOURCE]});print('Method frozen.')
elif stage=='train':
 for p,h in load(R/'METHOD-FREEZE.json').items():assert sha(Path(p))==h
 synthetic=train(['abac','abec','ibac','ibec']*100);normal=[score(w,synthetic) for w in ['abac','abec','ibac','ibec']];odd=[score(w,synthetic) for w in ['caba','ceba','cabi','cebi']]
 gate=min(odd)>max(normal);save('QUALIFICATION.json',{'gate':gate,'normal':normal,'unusual':odd,'limit':'Finite artificial-template engineering check only; does not validate manuscript nuisance exchangeability.'});assert gate
 panels,allocation=paneldata();save('ALLOCATION.json',allocation);models={}
 for key,g in panels.items():
  words=[w for r in g['train'] for w in r[7] if w is not None];nfol=len({fol(r[1]) for r in g['train']});models[key]={'training_tokens':len(words),'training_folios':nfol,'status':'eligible' if len(words)>=200 and nfol>=3 else 'insufficient training support'}
  if models[key]['status']=='eligible':models[key].update({'model':train(words),'frequencies':dict(collections.Counter(words))})
 save('MODELS.json',models);save('TRAINING-FREEZE.json',{str(p):sha(p) for p in [R/'MODELS.json',R/'ALLOCATION.json',R/'QUALIFICATION.json',R/'METHOD-FREEZE.json']});print('Models frozen:',sum(x['status']=='eligible' for x in models.values()),'eligible of',len(models))
elif stage=='test':
 for fn in ['METHOD-FREEZE.json','TRAINING-FREEZE.json']:
  for p,h in load(R/fn).items():assert sha(Path(p))==h
 panels,allocation=paneldata();assert allocation==load(R/'ALLOCATION.json');models=load(R/'MODELS.json');records=[];types=[];tests=[]
 for ix,(key,g) in enumerate(sorted(panels.items())):
  model=models[key]
  if model['status']!='eligible':tests.append({'stratum':key,'status':model['status']});continue
  words={w for r in g['test'] for w in r[7] if w is not None};scores={w:score(w,model['model']) for w in words};freq=model['frequencies'];cells=collections.defaultdict(list)
  for w in words:cells[(len(w),freq.get(w,0))].append(w)
  for w in sorted(words):
   peers=[v for v in cells[(len(w),freq.get(w,0))] if v!=w];pct=sum(scores[v]<scores[w] for v in peers)/len(peers) if len(peers)>=5 else None
   types.append({'stratum':key,'word':w,'length':len(w),'training_count':freq.get(w,0),'surprise':scores[w],'matched_peers':len(peers),'percentile':pct})
  groups=collections.defaultdict(lambda:{'first':[],'interior':[]})
  for r in g['test']:
   for j,w in enumerate(r[7]):
    if w is None:continue
    pos='single' if len(r[7])==1 else 'first' if j==0 else 'last' if j==len(r[7])-1 else 'interior'
    records.append({'stratum':key,'locator':r[6],'index':j,'word':w,'score':scores[w],'position':pos,'training_count':freq.get(w,0),'line':r[7]})
    if pos in ('first','interior'):groups[(fol(r[1]),len(w),freq.get(w,0))][pos].append(scores[w])
  differences=collections.defaultdict(list);details=[]
  for (folio,length,n),v in groups.items():
   if v['first'] and v['interior']:
    diff=sum(v['first'])/len(v['first'])-sum(v['interior'])/len(v['interior']);differences[folio].append(diff);details.append({'folio':folio,'length':length,'training_count':n,'first_n':len(v['first']),'interior_n':len(v['interior']),'difference':diff})
  vals={f:sum(v)/len(v) for f,v in differences.items()};result={'stratum':key,'matched_folios':len(vals),'folio_differences':vals,'matched_cells':details,'status':'estimated' if len(vals)>=5 else 'insufficient matched test folios'}
  if len(vals)>=5:result['effect'],result['p']=sign_test(list(vals.values()),65000+ix)
  tests.append(result)
 m=sum(x['status']=='estimated' for x in tests)
 for x in tests:
  if 'p' in x:x['p_adjusted']=min(1,x['p']*m);x['passes']=x['effect']>0 and x['p_adjusted']<=.05
 save('ALL-TYPES.json',types);save('ALL-TOKENS.json',records);save('POSITION-TESTS.json',tests)
 top={}
 for key in models:top[key]=sorted([x for x in types if x['stratum']==key and x['percentile'] is not None],key=lambda x:(-x['percentile'],-x['surprise'],x['word']))[:10]
 save('DISPLAY-CANDIDATES.json',top)
 summary={'eligible_models':sum(x['status']=='eligible' for x in models.values()),'scored_types':len(types),'scored_tokens':len(records),'rankable_types':sum(x['percentile'] is not None for x in types),'position_tests':m,'positive_passes':sum(x.get('passes',False) for x in tests),'limits':'Character bigrams only, one retrospective split, sparse other formats, no phonetic or name interpretation. H/F alternate readings, not independent replication.'};save('RESULTS.json',summary)
 body='<h1>Frozen template-breaker test — v65</h1><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><p>Surprise is mean negative log probability under a training-only EVA-character bigram model. Matched ranks use exact word length and exact training frequency. A high score means atypical for this model, not phonetic.</p>'
 body+='<h2>Held-out first/interior comparisons</h2>'
 for x in tests:
  if x['status']=='estimated':body+='<pre>'+html.escape(json.dumps({k:v for k,v in x.items() if k not in ('matched_cells','folio_differences')},indent=2))+'</pre>'
 body+='<h2>Exploratory matched-score examples</h2>'
 for key,v in top.items():
  if v:body+='<details><summary>'+html.escape(key)+'</summary><pre>'+html.escape(json.dumps(v,indent=2))+'</pre></details>'
 for n in ['PROTOCOL.json','METHOD-FREEZE.json','TRAINING-FREEZE.json','ALLOCATION.json','QUALIFICATION.json','MODELS.json','ALL-TYPES.json','ALL-TOKENS.json','POSITION-TESTS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Template-breaker v65</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8');print(json.dumps(summary));print(json.dumps([{k:v for k,v in x.items() if k not in ('matched_cells','folio_differences')} for x in tests if x['status']=='estimated']))
