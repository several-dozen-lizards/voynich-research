from pathlib import Path
import json,re,hashlib,collections,random,itertools,html,sys
R=Path(__file__).resolve().parent;P=R.parent
RAW=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fol(p):return re.match(r'f\d+',p)[0]
def unit(w,kind):return list(w) if kind=='character' else re.findall(r'cth|ckh|cph|cfh|ch|sh|[a-z]',w)
def reductions(w,kind):
 u=unit(w,kind);return (''.join(u[1:]),''.join(u[:-1])) if len(u)>1 else ('','')
def structural():
 flags={};previous={};raws={}
 for line in RAW.read_bytes().decode('latin-1').splitlines():
  m=re.match(r'^<(f\d+[rv]\d*)\.(P[^.]*)\.([^;]+);([HF])>\s*(.*)',line)
  if not m:continue
  page,place,num,tr,text=m.groups();loc=f'{page}.{place}.{num}';clean=re.sub(r'\{[^}]*\}','',text.split('#')[0]).strip();prev=previous.get((tr,page));first=bool(re.fullmatch(r'1',num))
  if first:status=True;reason='explicit locus line 1'
  elif prev and prev['end']=='=':status=True;reason='previous source line ends ='
  elif prev and prev['end']=='-' and prev['place']==place:status=False;reason='continuation after - in same locus series'
  else:status=None;reason='ambiguous/missing structural predecessor'
  end=clean[-1:] if clean[-1:] in ('=','-') else None;flags[(tr,loc)]={'opening':status,'reason':reason,'previous':prev['locator'] if prev else None};raws[(tr,loc)]=text;previous[(tr,page)]={'end':end,'place':place,'locator':loc}
 return flags,raws
def pvalue(vals,seed):
 obs=sum(vals)/len(vals)
 if len(vals)<=16:
  n=2**len(vals);tail=sum(sum(v*s for v,s in zip(vals,ss))/len(vals)>=obs-1e-12 for ss in itertools.product((-1,1),repeat=len(vals)));return tail/n,'exact folio sign flip'
 rng=random.Random(seed);tail=sum(sum(v*rng.choice((-1,1)) for v in vals)/len(vals)>=obs-1e-12 for _ in range(9999));return (tail+1)/10000,'9999 folio sign flips'
stage=sys.argv[1]
if stage=='freeze':
 protocol={'scope':'Paragraph P only, shared H/F loci with agreeing definite paragraph-start flags. Separate hand, section, Currier variety, format and transcription. Use v65 whole-numbered-folio allocation unchanged: training vocabulary independent of application folios; retrospective, previously inspected corpus.', 'paragraph_starts':'Read EVT structure only: locus line1 or previous P source line ending =. Continuation only after - in same page/locus series. Otherwise ambiguous. H/F structure disagreement and unknown first token retained but excluded; never promote next readable token.', 'units':['one EVA character','one longest-match cth|ckh|cph|cfh|ch|sh|[a-z] group'], 'vocabulary':'All readable training tokens except first token of paragraph openings; ambiguous/disagreeing lines excluded. Same stratum only. Original-word training frequency uses all readable eligible training tokens. >=3 training folios/100 vocabulary tokens; otherwise unsupported.', 'comparisons':'Held-out paragraph-first words vs (1) first words of definite continuation lines, primary position-matched control, (2) interior words, secondary. Match within same numbered folio, exact original length in chosen units and exact original-word training count. No unmatched controls or adaptive bins. Equal cell weight within folio; equal folio weight. Preserve unmatched openers.', 'outcomes':'A: opening minus control difference in probability that first-unit removal leaves exact nonempty vocabulary word. B: difference-in-differences: first-removal minus final-removal advantage in openings vs controls. Raw identity lookup also retained. >=5 matched test folios; folio sign-flip one-sided/exact<=16 else9999. Bonferroni across all estimated outcomes/panels/units/control-types. Support for opening-specific addition requires both A/B corrected<=.05 and positive. H/F agreement requires same stratum/unit/control passes both readings.', 'limits':'Vocab membership is written-form recurrence not meaning. Signs/characters are operational definitions. Position flags are transcription conventions, not independent image registration. Sign-flip symmetry assumed; sparse matches not absence of phenomenon. No alphabetic/syllabic decoding.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',RAW,P/'frequency-atlas-v48/rows.json',P/'template-breaker-v65/ALLOCATION.json']});print('Method frozen')
elif stage=='run':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 assert reductions('pchody','character')==('chody','pchod') and reductions('cthody','group')==('ody','cthod')
 vocab={'chody','ody'};assert reductions('pchody','character')[0] in vocab and reductions('chodyp','character')[1] in vocab
 flags,raws=structural();rows=load(P/'frequency-atlas-v48/rows.json');alloc=load(P/'template-breaker-v65/ALLOCATION.json');cov=collections.defaultdict(set)
 for r in rows:cov[r[6]].add(r[0])
 panels=collections.defaultdict(list);exceptions=[]
 for r in rows:
  if r[5]!='P' or r[0] not in ('H','F'):continue
  f=flags.get((r[0],r[6]));other=flags.get(('F' if r[0]=='H' else 'H',r[6]));reason=None
  if cov[r[6]]!={'H','F'}:reason='no paired source locus'
  elif f is None or other is None or f['opening'] is None or other['opening'] is None:reason='ambiguous paragraph structure'
  elif f['opening']!=other['opening']:reason='H/F paragraph boundary disagreement'
  if reason:exceptions.append({'transcription':r[0],'locator':r[6],'reason':reason,'flag':f,'other_flag':other,'words':r[7]});continue
  panels['|'.join([r[0],r[3],r[4],r[2],r[5]])].append((r,f['opening']))
 vocabs={};counts={};support={}
 for key,rr in panels.items():
  training=[(r,op) for r,op in rr if fol(r[1]) in alloc['training']];v=collections.Counter(w for r,op in training for i,w in enumerate(r[7]) if w is not None and not(op and i==0));c=collections.Counter(w for r,op in training for w in r[7] if w is not None);nf=len({fol(r[1]) for r,op in training});vocabs[key]=dict(v);counts[key]=dict(c);support[key]={'training_folios':nf,'vocabulary_tokens':sum(v.values()),'eligible':nf>=3 and sum(v.values())>=100}
 save('VOCABULARIES.json',vocabs);save('ORIGINAL-FREQUENCIES.json',counts);save('VOCABULARY-SUPPORT.json',support);save('VOCABULARY-FREEZE.json',{n:sha(R/n) for n in ['VOCABULARIES.json','ORIGINAL-FREQUENCIES.json','VOCABULARY-SUPPORT.json']})
 # Frozen vocabulary built only from designated training folios before outcome scoring.
 events=[];tests=[];unmatched=[]
 for pi,(key,rr) in enumerate(sorted(panels.items())):
  if not support[key]['eligible']:tests.append({'stratum':key,'status':'insufficient training vocabulary'});continue
  v=vocabs[key];c=counts[key]
  for kind in ['character','group']:
   buckets=collections.defaultdict(lambda:collections.defaultdict(list))
   for r,op in rr:
    if fol(r[1]) not in alloc['test']:continue
    if op and (not r[7] or r[7][0] is None):exceptions.append({'transcription':r[0],'locator':r[6],'reason':'unknown paragraph-first token; no promotion','words':r[7]})
    for i,w in enumerate(r[7]):
     if w is None:continue
     category='opening' if i==0 and op else 'continuation_first' if i==0 and not op else 'interior' if 0<i<len(r[7])-1 else None
     if category is None:continue
     left,right=reductions(w,kind);event={'stratum':key,'unit':kind,'folio':fol(r[1]),'locator':r[6],'index':i,'word':w,'category':category,'length':len(unit(w,kind)),'training_count':c.get(w,0),'first_removed':left,'final_removed':right,'first_hit':bool(left and left in v),'final_hit':bool(right and right in v),'identity_hit':w in v,'line':r[7],'raw':raws.get((r[0],r[6]))};events.append(event);buckets[(event['folio'],event['length'],event['training_count'])][category].append(event)
   for control in ['continuation_first','interior']:
    folios=collections.defaultdict(list);cells=[]
    for (folio,length,freq),cats in buckets.items():
     opens=cats.get('opening',[]);others=cats.get(control,[])
     if not opens:continue
     if not others:unmatched.extend({'stratum':key,'unit':kind,'control':control,'locator':x['locator'],'word':x['word'],'reason':'no exact same-folio length/frequency match'} for x in opens);continue
     mean=lambda es,k:sum(x[k] for x in es)/len(es)
     a=mean(opens,'first_hit')-mean(others,'first_hit');b=a-(mean(opens,'final_hit')-mean(others,'final_hit'));folios[folio].append((a,b));cells.append({'folio':folio,'length':length,'training_count':freq,'openers':[(x['locator'],x['word']) for x in opens],'controls':[(x['locator'],x['word']) for x in others],'opening_first_rate':mean(opens,'first_hit'),'control_first_rate':mean(others,'first_hit'),'opening_final_rate':mean(opens,'final_hit'),'control_final_rate':mean(others,'final_hit')})
    diffs={f:[sum(x[j] for x in vv)/len(vv) for j in [0,1]] for f,vv in folios.items()};result={'stratum':key,'unit':kind,'control':control,'matched_folios':len(diffs),'folio_effects':diffs,'cells':cells,'status':'estimated' if len(diffs)>=5 else 'insufficient matched folios'}
    if len(diffs)>=5:
     result['outcomes']=[]
     for j,name in enumerate(['first_removal_excess','first_vs_final_interaction']):
      vals=[v[j] for v in diffs.values()];p,method=pvalue(vals,73000+pi*10+j);result['outcomes'].append({'name':name,'effect':sum(vals)/len(vals),'p':p,'method':method})
    tests.append(result)
 M=sum(len(x.get('outcomes',[])) for x in tests)
 for x in tests:
  for y in x.get('outcomes',[]):y['adjusted_p']=min(1,y['p']*M);y['passes']=y['effect']>0 and y['adjusted_p']<=.05
  if 'outcomes' in x:x['both_pass']=all(y['passes'] for y in x['outcomes'])
 save('EVENTS.json',events);save('TESTS.json',tests);save('EXCEPTIONS.json',exceptions);save('UNMATCHED-OPENERS.json',unmatched)
 summary={'eligible_vocabularies':sum(x['eligible'] for x in support.values()),'estimated_comparisons':sum(x['status']=='estimated' for x in tests),'corrected_outcomes':M,'comparisons_passing_both':sum(x.get('both_pass',False) for x in tests),'opening_events_by_unit':dict(collections.Counter(x['unit'] for x in events if x['category']=='opening')),'exceptions':len(exceptions),'unmatched_opener_comparisons':len(unmatched),'limits':'Exact matched retrospective test, sparse coverage, written-form membership only. H/F are alternate readings.'};save('SUMMARY.json',summary)
 body='<h1>Paragraph-opening removal — v73</h1><p>Paragraph starts from source markers, never chosen from spelling. Separate training-folio vocabularies; exact same-folio length and training-frequency controls. Character and grouped-unit definitions frozen; final-removal comparison retained.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre>'
 for x in tests:
  if x['status']=='estimated':body+='<pre>'+html.escape(json.dumps({k:v for k,v in x.items() if k not in ['cells','folio_effects']},indent=2))+'</pre>'
 body+='<h2>Opening examples, including failures</h2>'
 for x in events:
  if x['category']=='opening':body+='<details><summary>'+html.escape(x['stratum']+' '+x['locator']+' '+x['unit']+' '+x['word'])+'</summary><p>'+html.escape(f"First removal: {x['first_removed']} ({x['first_hit']}); final removal: {x['final_removed']} ({x['final_hit']})")+'</p><p>'+html.escape(' · '.join(w or '[UNKNOWN]' for w in x['line']))+'</p></details>'
 for n in ['PROTOCOL.json','FREEZE.json','VOCABULARY-FREEZE.json','VOCABULARY-SUPPORT.json','VOCABULARIES.json','EVENTS.json','TESTS.json','EXCEPTIONS.json','UNMATCHED-OPENERS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Opening removal v73</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}details{padding:8px}</style>'+body,encoding='utf-8');print(json.dumps(summary));print(json.dumps([{k:v for k,v in x.items() if k not in ['cells','folio_effects']} for x in tests if x['status']=='estimated']))
