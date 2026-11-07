from pathlib import Path
import re,json,hashlib,random,math,collections,sys,importlib.util,html
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-page-decoding-v41')
s=importlib.util.spec_from_file_location('decoder',OLD/'qualify.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def syllables(w):
 # Restricted written-syllable subset; exclusions are part of the frozen coverage limit.
 if re.search(r'[jqxyz]|[aeiou]{2}|[bcdfgpt][lr]|ch|ph|th',w):return None
 vs=[i for i,c in enumerate(w) if c in 'aeiou']
 if not vs:return None
 cuts=[b-1 for a,b in zip(vs,vs[1:])];starts=[0]+cuts;ends=cuts+[len(w)]
 return [w[a:b] for a,b in zip(starts,ends)]
def prepare():
 words=d.sourcewords(d.sources['Latin']);cut=int(.6*len(words));parsed=[syllables(w) for w in words[:cut]];good=[x for x in parsed if x];inventory=sorted({s for w in good for s in w});ids={s:i+1 for i,s in enumerate(inventory)};n=len(inventory)+1;c=np.zeros((n,n));freq=np.zeros(n)
 for w in good:
  seq=[0]+[ids[s] for s in w]+[0]
  for a,b in zip(seq,seq[1:]):c[a,b]+=1;freq[b]+=1
 log=np.log((c+.1)/(c.sum(axis=1,keepdims=True)+.1*n))
 return words,inventory,ids,log,freq,{'source_training_tokens':cut,'retained_training_tokens':len(good),'excluded_training_tokens':cut-len(good),'syllable_types':len(inventory)}
def fit(cipher,log,freq,seed):
 observed=sorted({u for w in cipher for u in w});local={u:i for i,u in enumerate(observed)};N=len(log);M=len(observed);boundary=M;counts=collections.Counter()
 for w in cipher:
  seq=[boundary]+[local[u] for u in w]+[boundary]
  counts.update(zip(seq,seq[1:]))
 pairs=np.array(list(counts));weights=np.array(list(counts.values()));a,b=pairs.T;cf=collections.Counter(u for w in cipher for u in w);rank=sorted(range(M),key=lambda j:-cf[observed[j]]);target=np.argsort(-freq[1:])+1;initial=np.zeros(M+1,dtype=int)
 for j,v in zip(rank,target):initial[j]=v
 def objective(key):return float(log[key[a],key[b]]@weights)
 rng=np.random.default_rng(seed);attempts=[]
 for restart in range(4):
  key=initial.copy()
  if restart:
   for _ in range(10*restart):i,j=rng.choice(M,2,replace=False);key[i],key[j]=key[j],key[i]
  score=objective(key);best=score;bestkey=key.copy()
  for step in range(5000):
   i=int(rng.integers(M));old=int(key[i]);j=None
   if rng.random()<.5:
    j=int(rng.integers(M));key[i],key[j]=key[j],key[i]
   else:
    new=int(rng.integers(1,N))
    if new in key:continue
    key[i]=new
   proposed=objective(key);temperature=5*(.02**(step/4999))
   if proposed>=score or rng.random()<math.exp(max(-700,(proposed-score)/temperature)):score=proposed
   elif j is None:key[i]=old
   else:key[i],key[j]=key[j],key[i]
   if score>best:best=score;bestkey=key.copy()
  attempts.append({'score':best,'mapping':{u:int(bestkey[j]) for j,u in enumerate(observed)}})
 return {'attempts':attempts,'selected':max(range(4),key=lambda j:attempts[j]['score']),'observed_units':len(observed)}
stage=sys.argv[1]
if stage=='freeze':
 protocol={'scope':'Whole written syllable per cipher group; conservative Latin subset only. Actual group labels are opaque, not letter values. No German or mixed-language model. Not a universal phonological syllabifier.', 'syllabification':'One a/e/i/o/u nucleus per syllable; between nuclei put last consonant with next vowel, earlier consonants close preceding syllable. Exclude j/q/x/y/z, adjacent vowels (including diphthongs), stop-liquid clusters and ch/ph/th. Unknowns/excluded words remain recorded. No claim these cover every medieval pronunciation or morphological boundary.', 'source_reference':'https://dcc.dickinson.edu/grammar/latin/syllables', 'model':'Learn syllable inventory and add0.1 smoothed syllable-bigram transitions with word boundaries from first60% of existing Latin source. No letter substitution or syllable inventory supplied from test. Four annealing starts x5000 proposed moves; injective group-to-syllable map; swap or replace with unused inventory syllable. Best training objective only.', 'controls':'Fresh same-work60-80% region offsets5600/6300/7000. Each600-word block: first400 yields first100 retained words, final200 yields first20 retained words. No fallback/resampling if insufficient. Random opaque one-group-per-syllable encodings, with true group boundaries supplied: this is easier than Voynich segmentation. Three cases. Freeze inferred mappings before test. Gate all3: >=90% resolved syllable accuracy, >=80% group coverage, >=80% whole-word recovery. Unseen groups stay [UNK]. All known-control mappings and failures saved.', 'manuscript_if_pass':'Fixed v70 EVA grouping and v69 context windows; H-trained mapping applied unchanged to H/F, unseen groups unresolved, freeze before output. No manuscript scoring unless all controls pass; syllable output likelihood alone is not semantic evidence.', 'limits':'Restricted written syllables and same source work; synthetic qualification with supplied boundaries. Failure cannot reject syllabic Voynich. Conditional Latin syllabification excludes many actual source words, with coverage reported.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',d.sources['Latin'],OLD/'qualify.py']});print('Frozen')
elif stage=='fit-controls':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 assert syllables('medicina')==['me','di','ci','na'] and syllables('terra')==['ter','ra'] and syllables('dominus')==['do','mi','nus']
 words,inventory,ids,log,freq,coverage=prepare();save('SOURCE-COVERAGE.json',coverage);save('INVENTORY.json',inventory);controls=[];start=int(.6*len(words));end=int(.8*len(words))
 for case,offset in enumerate([5600,6300,7000]):
  at=start+offset;assert at+600<=end;rawtrain=words[at:at+400];rawtest=words[at+400:at+600];train=[(w,syllables(w)) for w in rawtrain if syllables(w)][:100];test=[(w,syllables(w)) for w in rawtest if syllables(w)][:20]
  if len(train)<100 or len(test)<20:save('INSUFFICIENT.json',{'case':case,'training':len(train),'test':len(test)});raise RuntimeError('Frozen sample support insufficient; no resampling')
  sy=sorted({s for w,ss in train+test for s in ss});rng=random.Random(71000+case);labels=[f'G{i:03d}' for i in range(len(sy))];rng.shuffle(labels);encoding=dict(zip(sy,labels));cipher=[[encoding[s] for s in ss] for w,ss in train];result=fit(cipher,log,freq,71100+case)
  controls.append(dict(result,case=case,training_plain=[w for w,ss in train],training_syllables=[ss for w,ss in train],test_plain=[w for w,ss in test],test_syllables=[ss for w,ss in test],test_groups=[[encoding[s] for s in ss] for w,ss in test],true_encoding=encoding,raw_source_range=[at,at+600],excluded_train=[w for w in rawtrain if not syllables(w)],excluded_test=[w for w in rawtest if not syllables(w)]));print('fit',case,'groups',result['observed_units'],flush=True)
 save('CONTROL-KEYS.json',controls);save('KEY-FREEZE.json',{n:sha(R/n) for n in ['CONTROL-KEYS.json','INVENTORY.json','SOURCE-COVERAGE.json']})
elif stage=='test-controls':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 for n,h in load(R/'KEY-FREEZE.json').items():assert sha(R/n)==h
 inventory=load(R/'INVENTORY.json');out=[]
 for x in load(R/'CONTROL-KEYS.json'):
  mapping=x['attempts'][x['selected']]['mapping'];decoded=[[inventory[mapping[u]-1] if u in mapping else '[UNK]' for u in w] for w in x['test_groups']];pairs=[(a,b) for w,v in zip(decoded,x['test_syllables']) for a,b in zip(w,v)];resolved=[(a,b) for a,b in pairs if a!='[UNK]'];coverage=len(resolved)/len(pairs);accuracy=sum(a==b for a,b in resolved)/max(1,len(resolved));wordaccuracy=sum(''.join(w)==truth for w,truth in zip(decoded,x['test_plain']))/len(decoded)
  out.append({'case':x['case'],'coverage':coverage,'resolved_syllable_accuracy':accuracy,'whole_word_accuracy':wordaccuracy,'passes':coverage>=.8 and accuracy>=.9 and wordaccuracy>=.8,'truth':x['test_plain'],'decoded':[''.join(w) for w in decoded],'decoded_syllables':decoded})
 save('CONTROL-RESULTS.json',out);summary={'qualified':all(x['passes'] for x in out),'cases_passed':sum(x['passes'] for x in out),'cases':len(out),'manuscript_scored':False,'status':'qualified; manuscript stage pending' if all(x['passes'] for x in out) else 'control failure; manuscript stage closed','limits':'Only one restricted Latin whole-syllable method tested; no rejection of syllabic encoding.'};save('RESULTS.json',summary)
 body='<h1>Whole-syllable decoder — v71</h1><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><p>Each cipher group maps to a complete candidate written syllable. Known controls supply true group boundaries, making this easier than unknown manuscript segmentation. Unknown groups remain [UNK]. The manuscript is not scored unless the fixed qualification gate passes.</p><h2>Coverage</h2><pre>'+html.escape(json.dumps(load(R/'SOURCE-COVERAGE.json'),indent=2))+'</pre><h2>Fresh controls and failures</h2><pre>'+html.escape(json.dumps(out,indent=2))+'</pre>'
 for n in ['PROTOCOL.json','FREEZE.json','INVENTORY.json','SOURCE-COVERAGE.json','CONTROL-KEYS.json','KEY-FREEZE.json','CONTROL-RESULTS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 body+='<p>Syllable-rule reference: <a href="https://dcc.dickinson.edu/grammar/latin/syllables">Allen and Greenough, via Dickinson College</a>. The implementation is a restricted approximation, not a complete syllabifier.</p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Syllable decoder v71</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8');print(json.dumps(summary));print(json.dumps([{k:v for k,v in x.items() if k not in ['truth','decoded','decoded_syllables']} for x in out]))
