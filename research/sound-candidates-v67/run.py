from pathlib import Path
import json,hashlib,importlib.util,random,sys,collections,html
R=Path(__file__).resolve().parent;P=R.parent
OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-page-decoding-v41')
s=importlib.util.spec_from_file_location('decoder',OLD/'qualify.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def score(w,m):
 import math
 return -sum(math.log((m['pairs'].get(a+b,0)+.5)/(m['totals'].get(a,0)+.5*len(m['alphabet']))) for a,b in zip('^'+w,w+'$'))/(len(w)+1)
stage=sys.argv[1]
if stage=='freeze':
 protocol={'scope':'Narrow fixed monoalphabetic orthographic mapping proxy, not phoneme inference, syllabic or pictorial rebus search. Latin/MiddleEnglish/German existing corpus models retained with exact provenance. No claim of period matching or exhaustive language search.', 'selection':'Use only v65 training folios f26/f31/f33, H hand2 botanical P. Rank unique words of >=4 EVA characters with training count<=2 by frozen v65 surprise; top20, lexical ties. Save full source lines and F alternatives. A selected unusual type need not itself be a name.', 'qualification':'For each language take 3 fixed-seed sets from last20% of source corpus (language model trained first60%), training20 words exactly matching selected EVA lengths, plus20 separately sampled test words with same lengths. Encrypt with random fixed alphabet; infer key using unchanged v41 search. Freeze recovered keys before held-out scoring. Require >=90% held-out letter recovery in all3 cases perlanguage; otherwise no manuscript decoding for that language. Failure is solver/sample limitation, not evidence against encoding.', 'manuscript_stage':'Only languages passing qualification may be searched. One fixed character-to-letter key, no deletions/reversals/context exceptions. Fit training selected words only. Freeze mappings before held-out scoring. H/F same key, no refit. Statistical word likelihood alone cannot establish semantic sense; no independent botanical-name anchors available. If no language qualifies, preserve failure and leave manuscript decoding closed.', 'heldout_limit':'v65 already exposed statistical summaries and some anomaly words from test folios. Any later transfer is retrospective, not virgin confirmation.'}
 save('PROTOCOL.json',protocol)
 rows=load(P/'frequency-atlas-v48/rows.json');alloc=load(P/'template-breaker-v65/ALLOCATION.json');m=load(P/'template-breaker-v65/MODELS.json')['H|2|B|Botanical|P'];freq=m['frequencies']
 words=sorted([w for w,n in freq.items() if n<=2 and len(w)>=4],key=lambda w:(-score(w,m['model']),w))[:20]
 index={(r[0],r[6]):r for r in rows};examples=[]
 import re
 for r in rows:
  if r[0]=='H' and r[2:6]==['Botanical','2','B','P'] and re.match(r'f\d+',r[1])[0] in alloc['training'] and any(w in words for w in r[7]):examples.append({'locator':r[6],'H':r[7],'F':index.get(('F',r[6]),[None]*8)[7]})
 save('TRAINING-PACKET.json',{'words':[{'word':w,'length':len(w),'training_count':freq[w],'surprise':score(w,m['model'])} for w in words],'examples':examples,'selection':'training only; no test word selection inspected'})
 files=[Path(__file__),R/'PROTOCOL.json',R/'TRAINING-PACKET.json',OLD/'qualify.py',P/'template-breaker-v65/MODELS.json',P/'template-breaker-v65/ALLOCATION.json']+list(d.sources.values())+[OLD/(l+'-model.npz') for l in d.sources]
 save('FREEZE.json',{str(p):sha(p) for p in files});print('Method and training packet frozen',words)
elif stage=='fit-controls':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 lengths=[x['length'] for x in load(R/'TRAINING-PACKET.json')['words']];controls=[]
 for li,(lang,path) in enumerate(d.sources.items()):
  ws=d.sourcewords(path);pool=ws[int(.8*len(ws)):];bylen=collections.defaultdict(list)
  for i,w in enumerate(pool):bylen[len(w)].append((i,w))
  model=d.np.load(OLD/(lang+'-model.npz'))
  for case in range(3):
   rng=random.Random(67000+li*100+case);used=set();samples=[];positions=[]
   for fold in range(2):
    one=[];ix=[]
    for length in lengths:
     available=[(i,w) for i,w in bylen[length] if i not in used]
     assert available,'Insufficient length match; no adaptive relaxation'
     i,w=rng.choice(available);used.add(i);one.append(w);ix.append(i)
    samples.append(' '.join(one));positions.append(ix)
   enc=d.np.arange(27,dtype=d.np.int16);enc[:26]=d.np.random.default_rng(67100+li*100+case).permutation(26)
   cipher=[d.apply(x,enc) for x in samples];key,fit=d.decode(cipher[0],model['table'],model['freq'],67200+li*100+case)
   controls.append({'language':lang,'case':case,'source':str(path),'source_positions':positions,'plaintext_train':samples[0],'plaintext_test':samples[1],'cipher_train':cipher[0],'cipher_test':cipher[1],'key':key.tolist(),'training_output':d.apply(cipher[0],key),'training_score':fit})
   print('fit',lang,case,flush=True)
 save('CONTROL-KEYS.json',controls);save('CONTROL-KEY-FREEZE.json',{'sha256':sha(R/'CONTROL-KEYS.json')})
elif stage=='test-controls':
 assert sha(R/'CONTROL-KEYS.json')==load(R/'CONTROL-KEY-FREEZE.json')['sha256']
 results=[]
 for x in load(R/'CONTROL-KEYS.json'):
  out=d.apply(x['cipher_test'],x['key']);truth=x['plaintext_test'];acc=sum(a==b for a,b in zip(out,truth) if b!=' ')/sum(b!=' ' for b in truth);x.update({'heldout_output':out,'letter_accuracy':acc,'exact_word_fraction':sum(a==b for a,b in zip(out.split(),truth.split()))/len(truth.split()),'passes':acc>=.9});results.append(x)
 gate={lang:all(x['passes'] for x in results if x['language']==lang) for lang in d.sources};save('CONTROL-RESULTS.json',results);save('GATE.json',gate)
 summary={'gates':gate,'manuscript_decoded':False,'status':'qualification failed; no manuscript keys fitted' if not any(gate.values()) else 'some languages qualify; manuscript stage pending','limits':'Only short-sample monoalphabetic orthographic recovery evaluated. No rejection of phonetic/rebus hypothesis; no meaning inferred.'};save('RESULTS.json',summary)
 body='<h1>Unusual-word sound-reading search: qualification</h1><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><p>The source training packet was frozen before qualification. Recovered control keys were frozen before applying to held-out known words. These controls contain a real, perfectly consistent substitution rule; failure means this search cannot reliably recover it at the available sample size.</p><table><tr><th>Language</th><th>Case</th><th>Held-out letters</th><th>Exact words</th></tr>'
 for x in results:body+=f"<tr><td>{x['language']}</td><td>{x['case']}</td><td>{x['letter_accuracy']:.1%}</td><td>{x['exact_word_fraction']:.1%}</td></tr>"
 body+='</table><h2>Frozen unusual training words</h2><pre>'+html.escape(json.dumps(load(R/'TRAINING-PACKET.json'),indent=2))+'</pre>'
 for n in ['PROTOCOL.json','FREEZE.json','CONTROL-RESULTS.json','CONTROL-KEY-FREEZE.json','TRAINING-PACKET.json','GATE.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Sound candidates v67</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}td,th{padding:10px;text-align:left}</style>'+body,encoding='utf-8');print(json.dumps(summary));print([(x['language'],x['case'],round(x['letter_accuracy'],3)) for x in results])
