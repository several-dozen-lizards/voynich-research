from pathlib import Path
import json,hashlib,random,collections,importlib.util,sys,re,html
R=Path(__file__).resolve().parent;P=R.parent;OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-page-decoding-v41')
s=importlib.util.spec_from_file_location('decoder',OLD/'qualify.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def render(text,key,seen):return ''.join(' ' if c==' ' else chr(97+int(key[ord(c)-97])) if c in seen else '?' for c in text)
def fit(text,lang,seed):
 model=d.np.load(OLD/(lang+'-model.npz'));runs=[]
 for j in range(4):
  key,score=d.decode(text,model['table'],model['freq'],seed+j*10000);runs.append({'key':key.tolist(),'score':score,'seed':seed+j*10000})
 return {'runs':runs,'selected':max(range(4),key=lambda j:runs[j]['score']),'seen':sorted(set(text)-{' '})}
def frozen():
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
def accuracy(out,truth):
 letters=[(a,b) for a,b in zip(out,truth) if b!=' '];resolved=[(a,b) for a,b in letters if a!='?'];return {'coverage':len(resolved)/len(letters),'resolved_accuracy':sum(a==b for a,b in resolved)/max(1,len(resolved)),'overall_accuracy':sum(a==b for a,b in letters)/len(letters),'output':out}
stage=sys.argv[1]
if stage=='freeze':
 protocol={'method':'Unchanged v68 four-search best-training-score monoalphabetic decoder. Render every symbol not present in fitting text as ?. Never infer unseen assignments from test material; uncertainty at original token level retained as [UNKNOWN]. EVA letters are not assumed phonemes.', 'controls':'Fresh same-work positions in60-80% interval, offsets1500/3000/4500; disjoint from v68. First400-word pool; withhold least frequent letter with >=3 occurrences, lexical ties; take first100 words not containing it. Next600words: first20-word consecutive window containing withheld letter. Fixed random substitution. Freeze keys before test. Require3/3 perlanguage: resolved accuracy>=.90,coverage>=.80,all withheld-symbol occurrences masked,zero masking of seen symbols. This is abstention-aware recovery, not complete decryption.', 'manuscript':'Only qualifying languages. H training v65 folios; freeze v67 top20 anomaly-word sites plus previous/next P line within same page. Fit all readable complete H lines in those windows; exclude lines with uncertain tokens from fitting, preserve in output. Fit one key perlanguage, no retuning to F. Heldout H top20 rare(count<=2 in training),length>=4 types ranked by frozenv65 surprise, then same context window. Source-line joins become spaces in fitting objective, not inferred clauses.', 'comparison':'One matched within-word letter-shuffle arm with same search effort, training and test shuffled deterministically. This is a diagnostic, not a calibrated significance test. Dictionary fraction uses language-model training vocabulary; model score and word matches are not semantic coherence. Show full decoded windows and every failed language/control.', 'limits':'Retrospective split, no independent named-plant anchors, no semantic validation or syllabic/rebus search. H/F are readings of one manuscript. This stage tests a narrow fixed alphabet reading with context.'}
 save('PROTOCOL.json',protocol);files=[Path(__file__),R/'PROTOCOL.json',OLD/'qualify.py',P/'template-breaker-v65/MODELS.json',P/'template-breaker-v65/ALLOCATION.json',P/'sound-candidates-v67/TRAINING-PACKET.json',P/'frequency-atlas-v48/rows.json']+list(d.sources.values())+[OLD/(l+'-model.npz') for l in d.sources];save('FREEZE.json',{str(p):sha(p) for p in files});print('Frozen')
elif stage=='fit-controls':
 frozen();out=[]
 for li,(lang,path) in enumerate(d.sources.items()):
  words=d.sourcewords(path);start=int(.6*len(words));end=int(.8*len(words))
  for case,off in enumerate([1500,3000,4500]):
   at=start+off;assert at+1000<=end;pool=words[at:at+400];counts=collections.Counter(''.join(pool));withheld=min((c for c,n in counts.items() if n>=3),key=lambda c:(counts[c],c));train=[w for w in pool if withheld not in w][:100];assert len(train)==100
   tail=words[at+400:at+1000];idx=next(i for i in range(581) if withheld in ''.join(tail[i:i+20]));truth=' '.join(tail[idx:idx+20]);plain=' '.join(train);enc=d.np.arange(27,dtype=d.np.int16);enc[:26]=d.np.random.default_rng(69000+li*100+case).permutation(26);ct=d.apply(plain,enc);test=d.apply(truth,enc);result=fit(ct,lang,69100+li*100+case)
   out.append(dict(result,language=lang,case=case,withheld_plain=withheld,withheld_cipher=d.apply(withheld,enc),plaintext_train=plain,plaintext_test=truth,cipher_test=test,source_train_pool=[at,at+400],source_test=[at+400+idx,at+420+idx]));print('control fit',lang,case,flush=True)
 save('CONTROL-KEYS.json',out);save('CONTROL-FREEZE.json',{'sha256':sha(R/'CONTROL-KEYS.json')})
elif stage=='test-controls':
 frozen();assert sha(R/'CONTROL-KEYS.json')==load(R/'CONTROL-FREEZE.json')['sha256'];out=[]
 for x in load(R/'CONTROL-KEYS.json'):
  key=x['runs'][x['selected']]['key'];decoded=render(x['cipher_test'],key,set(x['seen']));result=accuracy(decoded,x['plaintext_test']);correct=all((a=='?')==(c not in x['seen']) for a,c in zip(decoded,x['cipher_test']) if c!=' ');result.update({'language':x['language'],'case':x['case'],'withheld_letter':x['withheld_plain'],'masking_correct':correct,'passes':result['coverage']>=.8 and result['resolved_accuracy']>=.9 and correct});out.append(result)
 gate={l:all(x['passes'] for x in out if x['language']==l) for l in d.sources};save('CONTROL-RESULTS.json',out);save('GATE.json',gate);print(json.dumps(out));print(gate)
elif stage=='fit-manuscript':
 frozen();gate=load(R/'GATE.json');rows=load(P/'frequency-atlas-v48/rows.json');alloc=load(P/'template-breaker-v65/ALLOCATION.json');m=load(P/'template-breaker-v65/MODELS.json')['H|2|B|Botanical|P'];freq=m['frequencies'];trainwords={x['word'] for x in load(P/'sound-candidates-v67/TRAINING-PACKET.json')['words']};base=[r for r in rows if r[0]=='H' and r[2:6]==['Botanical','2','B','P']]
 import math
 def surprise(w):
  mod=m['model'];return -sum(math.log((mod['pairs'].get(a+b,0)+.5)/(mod['totals'].get(a,0)+.5*len(mod['alphabet']))) for a,b in zip('^'+w,w+'$'))/(len(w)+1)
 testrows=[r for r in base if re.match(r'f\d+',r[1])[0] in alloc['test']];testwords=sorted({w for r in testrows for w in r[7] if w is not None and len(w)>=4 and freq.get(w,0)<=2},key=lambda w:(-surprise(w),w))[:20]
 windows={}
 for fold,targets in [('train',trainwords),('test',set(testwords))]:
  rr=[r for r in base if re.match(r'f\d+',r[1])[0] in alloc['training' if fold=='train' else 'test']];selected=set()
  for i,r in enumerate(rr):
   if any(w in targets for w in r[7]):
    selected.add(i)
    for j in [i-1,i+1]:
     if 0<=j<len(rr) and rr[j][1]==r[1]:selected.add(j)
  windows[fold]=[rr[i] for i in sorted(selected)]
 save('WINDOWS.json',{'training_targets':sorted(trainwords),'test_targets':testwords,'rows':windows,'excluded_fitting_lines':[r[6] for r in windows['train'] if None in r[7]]})
 fitting=' '.join(w for r in windows['train'] if None not in r[7] for w in r[7]);assert len(fitting.split())>=100;fits=[]
 for li,(lang,qualified) in enumerate(gate.items()):
  if not qualified:continue
  for arm in ['actual','letter-shuffle']:
   rng=random.Random(69200);text=fitting if arm=='actual' else ' '.join(''.join(rng.sample(w,len(w))) for w in fitting.split());result=fit(text,lang,69300+li*100);fits.append(dict(result,language=lang,arm=arm,training_words=len(text.split()),training_text=text));print('manuscript fit',lang,arm,flush=True)
 save('MANUSCRIPT-KEYS.json',fits);save('MANUSCRIPT-FREEZE.json',{n:sha(R/n) for n in ['MANUSCRIPT-KEYS.json','WINDOWS.json','GATE.json']})
elif stage=='test-manuscript':
 frozen()
 for n,h in load(R/'MANUSCRIPT-FREEZE.json').items():assert sha(R/n)==h
 windows=load(R/'WINDOWS.json');rows=load(P/'frequency-atlas-v48/rows.json');index={(r[0],r[6]):r for r in rows};outputs=[]
 for x in load(R/'MANUSCRIPT-KEYS.json'):
  vocabwords=d.sourcewords(d.sources[x['language']]);vocab=set(vocabwords[:int(.6*len(vocabwords))]);key=x['runs'][x['selected']]['key']
  for tr in ['H','F']:
   rng=random.Random(69400);lines=[];known=[];resolved=total=0
   for r in windows['rows']['test']:
    other=index.get((tr,r[6]));ws=other[7] if other else None
    if ws is None:lines.append({'locator':r[6],'status':'missing reading'});continue
    decoded=[]
    for w in ws:
     if w is None:decoded.append('[UNKNOWN]');continue
     transformed=w if x['arm']=='actual' else ''.join(rng.sample(w,len(w)));out=render(transformed,key,set(x['seen']));decoded.append(out);known.append(out);total+=len(w);resolved+=sum(c!='?' for c in out)
    lines.append({'locator':r[6],'source':ws,'decoded':decoded})
   outputs.append({'language':x['language'],'arm':x['arm'],'transcription':tr,'coverage':resolved/max(1,total),'dictionary_fraction':sum(w in vocab for w in known)/max(1,len(known)),'lines':lines})
 save('OUTPUTS.json',outputs);body='<h1>Masked decoder — v69</h1><p>Unseen cipher symbols remain ?. Original uncertain tokens remain [UNKNOWN]. Fixed H-trained keys apply to H/F held-out folios without refitting. These are orthographic candidate strings, not translations.</p><h2>Fresh qualification</h2><pre>'+html.escape(json.dumps(load(R/'CONTROL-RESULTS.json'),indent=2))+'</pre>'
 for x in outputs:
  body+='<h2>'+x['language']+' / '+x['arm']+' / '+x['transcription']+'</h2><p>Resolved-symbol coverage '+f"{x['coverage']:.1%}"+'; training-vocabulary word matches '+f"{x['dictionary_fraction']:.1%}"+'. Word matches do not demonstrate coherent meaning.</p>'
  for line in x['lines']:
   body+='<details><summary>'+line['locator']+'</summary><p>'+html.escape(' '.join(w or '[UNKNOWN]' for w in line.get('source',[])))+'</p><p>'+html.escape(' '.join(line.get('decoded',[])))+'</p></details>'
 for n in ['PROTOCOL.json','GATE.json','WINDOWS.json','MANUSCRIPT-KEYS.json','MANUSCRIPT-FREEZE.json','OUTPUTS.json','CONTROL-RESULTS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Masked decoder v69</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}details{padding:8px}</style>'+body,encoding='utf-8');print(json.dumps([{k:v for k,v in x.items() if k!='lines'} for x in outputs]))
