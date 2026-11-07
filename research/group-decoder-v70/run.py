from pathlib import Path
import json,re,hashlib,importlib.util,random,html,sys
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('masked',P/'masked-decoder-v69/run.py')
# Import the standalone earlier decoder only; task scripts execute their stages at import.
OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-page-decoding-v41')
s=importlib.util.spec_from_file_location('decoder',OLD/'qualify.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
PAT=r'cth|ckh|cph|cfh|ch|sh|[a-z]'
def units(w):return re.findall(PAT,w)
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(text,lang,seed):
 m=d.np.load(OLD/(lang+'-model.npz'));runs=[]
 for j in range(4):
  key,score=d.decode(text,m['table'],m['freq'],seed+10000*j);runs.append({'key':key.tolist(),'score':score,'seed':seed+10000*j})
 return {'runs':runs,'selected':max(range(4),key=lambda j:runs[j]['score']),'seen':sorted(set(text)-{' '})}
def renderword(w,alphabet,key,seen):return ''.join(chr(97+key[ord(alphabet[u])-97]) if u in alphabet and alphabet[u] in seen else '?' for u in units(w))
def frozen():
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
stage=sys.argv[1]
if stage=='freeze':
 windows=load(P/'masked-decoder-v69/WINDOWS.json');words=[w for r in windows['rows']['train'] if None not in r[7] for w in r[7]];alphabet={u:chr(97+i) for i,u in enumerate(sorted({u for w in words for u in units(w)}))};assert len(alphabet)<=26
 protocol={'scope':'Fixed longest-match EVA grouping cth|ckh|cph|cfh|ch|sh|[a-z]. Each complete group maps to one alphabetic output symbol; not a syllable-to-sound or pictorial rebus model. Fixed segmentation, not learned.', 'search':'Same v69 four-search decoder, select highest training objective; unseen groups unresolved as ?. No silent splitting of an unknown group into known letters.', 'controls':'Latin/German only; MiddleEnglish excluded due v69 source-language contamination. Fresh same-work60-80% source positions offsets120,620,1120,100train+20test, disjoint from v68/v69. Encode letters as a random permutation of26 group codes:23 observed training units plus b,v,x. No within-word group separators supplied. Longest-match tokenization must round-trip exactly; freeze learned keys before test.3/3 perlanguage resolved-letter accuracy>=.90,coverage>=.80,exact segmentation and correct unseen masking. Positive engineering controls only; no real unknown-script segmentation qualification.', 'manuscript':'Reuse frozen v69 windows234words training and45testlines; no reselection. Training groups H only, same key applied to H/F. Fit actual and within-word group-order-shuffle diagnostic with same effort. Freeze keys before decoding test. Preserve raw groups, joined/split alternatives and all outputs. No semantic score or meaning inference from dictionary overlap.', 'limits':'v69 test text already inspected: retrospective comparison. English excluded. Training-derived alphabet/segmentation conventions do not prove manuscript glyph inventory. No exhaustive syllabic search.'}
 save('PROTOCOL.json',protocol);save('ALPHABET.json',alphabet);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',R/'ALPHABET.json',P/'masked-decoder-v69/WINDOWS.json',P/'frequency-atlas-v48/rows.json',OLD/'qualify.py']+[d.sources[l] for l in ['Latin','German']]+[OLD/(l+'-model.npz') for l in ['Latin','German']]});print('Frozen',len(alphabet),'training groups')
elif stage=='fit-controls':
 frozen();codes=sorted(list(load(R/'ALPHABET.json'))+['b','v','x']);assert len(codes)==26;out=[]
 for li,lang in enumerate(['Latin','German']):
  ws=d.sourcewords(d.sources[lang]);start=int(.6*len(ws))
  for case,offset in enumerate([120,620,1120]):
   plain=ws[start+offset:start+offset+120];rng=random.Random(70000+li*100+case);code=codes[:];rng.shuffle(code);mapping=dict(zip('abcdefghijklmnopqrstuvwxyz',code));alphabet={u:chr(97+i) for i,u in enumerate(codes)}
   encoded=[''.join(mapping[c] for c in w) for w in plain];exact=all(units(e)==[mapping[c] for c in w] for w,e in zip(plain,encoded));assert exact,'Segmentation qualification failed; stop'
   train=' '.join(''.join(alphabet[u] for u in units(w)) for w in encoded[:100]);result=fit(train,lang,70100+li*100+case)
   out.append(dict(result,language=lang,case=case,alphabet=alphabet,training_plain=plain[:100],test_plain=plain[100:],test_encoded=encoded[100:],segmentation_exact=exact,source_range=[start+offset,start+offset+120]));print('control',lang,case,flush=True)
 save('CONTROL-KEYS.json',out);save('CONTROL-FREEZE.json',{'sha256':sha(R/'CONTROL-KEYS.json')})
elif stage=='test-controls':
 frozen();assert sha(R/'CONTROL-KEYS.json')==load(R/'CONTROL-FREEZE.json')['sha256'];out=[]
 for x in load(R/'CONTROL-KEYS.json'):
  key=x['runs'][x['selected']]['key'];decoded=[renderword(w,x['alphabet'],key,x['seen']) for w in x['test_encoded']];pairs=list(zip(''.join(decoded),''.join(x['test_plain'])));resolved=[(a,b) for a,b in pairs if a!='?'];coverage=len(resolved)/len(pairs);accuracy=sum(a==b for a,b in resolved)/len(resolved);mask=all((z=='?')==(x['alphabet'][u] not in x['seen']) for w,dd in zip(x['test_encoded'],decoded) for u,z in zip(units(w),dd));out.append({'language':x['language'],'case':x['case'],'coverage':coverage,'resolved_accuracy':accuracy,'mask_correct':mask,'segmentation_exact':x['segmentation_exact'],'passes':coverage>=.8 and accuracy>=.9 and mask and x['segmentation_exact'],'decoded':decoded,'truth':x['test_plain']})
 gate={l:all(x['passes'] for x in out if x['language']==l) for l in ['Latin','German']};save('CONTROL-RESULTS.json',out);save('GATE.json',gate);print(json.dumps(out));print(gate)
elif stage=='fit-manuscript':
 frozen();a=load(R/'ALPHABET.json');windows=load(P/'masked-decoder-v69/WINDOWS.json');ws=[w for r in windows['rows']['train'] if None not in r[7] for w in r[7]];fits=[]
 for li,(lang,gate) in enumerate(load(R/'GATE.json').items()):
  if not gate:continue
  for arm in ['actual','group-shuffle']:
   rng=random.Random(70200);groups=[units(w) for w in ws]
   if arm=='group-shuffle':
    for g in groups:rng.shuffle(g)
   text=' '.join(''.join(a[u] for u in g) for g in groups);result=fit(text,lang,70300+li*100);fits.append(dict(result,language=lang,arm=arm,training_words=len(ws),alphabet=a));print('manuscript fit',lang,arm,flush=True)
 save('MANUSCRIPT-KEYS.json',fits);save('MANUSCRIPT-FREEZE.json',{n:sha(R/n) for n in ['MANUSCRIPT-KEYS.json','GATE.json','ALPHABET.json']})
elif stage=='test-manuscript':
 frozen()
 for n,h in load(R/'MANUSCRIPT-FREEZE.json').items():assert sha(R/n)==h
 windows=load(P/'masked-decoder-v69/WINDOWS.json');rows=load(P/'frequency-atlas-v48/rows.json');index={(r[0],r[6]):r for r in rows};outputs=[]
 for x in load(R/'MANUSCRIPT-KEYS.json'):
  words=d.sourcewords(d.sources[x['language']]);vocab=set(words[:int(.6*len(words))]);key=x['runs'][x['selected']]['key'];a=x['alphabet']
  for tr in ['H','F']:
   rng=random.Random(70400);lines=[];known=[];total=resolved=0
   for r in windows['rows']['test']:
    rr=index.get((tr,r[6]));ws=rr[7] if rr else None
    if ws is None:lines.append({'locator':r[6],'missing':True});continue
    decoded=[];allgroups=[]
    for w in ws:
     if w is None:decoded.append('[UNKNOWN]');allgroups.append(None);continue
     groups=units(w);allgroups.append(groups[:])
     if x['arm']=='group-shuffle':rng.shuffle(groups)
     out=''.join(chr(97+key[ord(a[u])-97]) if u in a and a[u] in x['seen'] else '?' for u in groups);decoded.append(out);known.append(out);total+=len(out);resolved+=sum(c!='?' for c in out)
    lines.append({'locator':r[6],'source':ws,'groups':allgroups,'decoded':decoded})
   outputs.append({'language':x['language'],'arm':x['arm'],'transcription':tr,'coverage':resolved/max(total,1),'dictionary_fraction':sum(w in vocab for w in known)/max(len(known),1),'lines':lines})
 save('OUTPUTS.json',outputs);body='<h1>Glyph-group decoder — v70</h1><p>Fixed ch/sh/benched-gallows groups map to individual alphabetic symbols. Not a syllabary or decipherment. Unseen groups remain ?, uncertain tokens remain [UNKNOWN]. Fixed H-trained keys, same heldout windows and alternate F readings.</p><h2>Known-text qualification</h2><pre>'+html.escape(json.dumps(load(R/'CONTROL-RESULTS.json'),indent=2))+'</pre>'
 for x in outputs:
  body+='<h2>'+x['language']+' / '+x['arm']+' / '+x['transcription']+'</h2><p>Group coverage '+f"{x['coverage']:.1%}"+'; vocabulary matches '+f"{x['dictionary_fraction']:.1%}"+'. These are not semantic scores.</p>'
  for line in x['lines']:body+='<details><summary>'+line['locator']+'</summary><p>'+html.escape(' '.join(w or '[UNKNOWN]' for w in line.get('source',[])))+'</p><p>'+html.escape(' '.join(line.get('decoded',[])))+'</p></details>'
 for n in ['PROTOCOL.json','FREEZE.json','ALPHABET.json','CONTROL-RESULTS.json','GATE.json','MANUSCRIPT-KEYS.json','MANUSCRIPT-FREEZE.json','OUTPUTS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Glyph groups v70</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}details{padding:8px}</style>'+body,encoding='utf-8');print(json.dumps([{k:v for k,v in x.items() if k!='lines'} for x in outputs]))
