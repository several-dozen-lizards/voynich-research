from pathlib import Path
import json,hashlib,importlib.util,random,sys,html
R=Path(__file__).resolve().parent;P=R.parent
OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-page-decoding-v41')
s=importlib.util.spec_from_file_location('decoder',OLD/'qualify.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objective(text,table):
 a=d.arr(text).astype(d.np.int32);ix=((a[:-3]*27+a[1:-2])*27+a[2:-1])*27+a[3:];return float(table[ix].mean())
def acc(a,b):return sum(x==y for x,y in zip(a,b) if y!=' ')/sum(y!=' ' for y in b)
def fit(text,model,seed):
 runs=[]
 for j in range(4):
  key,sc=d.decode(text,model['table'],model['freq'],seed+j*10000);runs.append({'seed':seed+j*10000,'key':key.tolist(),'score':sc})
 return runs
stage=sys.argv[1]
if stage=='freeze':
 protocol={'question':'Search optimization versus short sample/context under fixed substitution controls; Voynich closed.', 'revision':'Unchanged quadgram objective and v41 solver; four independent full searches (16 internal restarts total), choose greatest training score. Baseline is first search. Seeds predeclared; no heldout selection.', 'old_diagnosis':'Replay all9 v67 controls with four new seeds; retain every attempt. Compare training likelihood to true plaintext score and heldout recovery. If wrong output scores above truth, objective ambiguity/mismatch is demonstrated; if below truth, optimization failure is demonstrated. Both may coexist.', 'fresh':'Same3 source works, fresh source positions from60-80% interval excluded from model training(first60%), v41qualification(last20%) and v67(last20%). Not new independent works or genres.3 disjoint120-word consecutive blocks per language at offsets0,500,1000 inside interval. First100 fitting, next20 heldout. Same cipher per block and same heldout across arms.', 'arms':'20consecutive(first20),20shuffled(same tokens permuted),100consecutive. Comparing20 vs100 combines extra data and context; shuffle20 isolates order at fixed token identity. Both baseline and revised evaluated from same fitted runs.', 'gate':'For each language/arm/method all3 cases >=90% heldout letter recovery. Report exact words and unseen-letter coverage; no language pooling to conceal failures. Candidate keys frozen before fresh heldout application. Passing long arm does not authorize short Voynich decoding.', 'limits':'Finite engineering controls; simple alphabet substitution only. No semantic qualification, no syllabic/rebus claim. Prior outputs preserved.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',OLD/'qualify.py',P/'sound-candidates-v67/CONTROL-RESULTS.json']+list(d.sources.values())+[OLD/(l+'-model.npz') for l in d.sources]});print('Revision frozen')
elif stage=='fit':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 old=[]
 for i,x in enumerate(load(P/'sound-candidates-v67/CONTROL-RESULTS.json')):
  model=d.np.load(OLD/(x['language']+'-model.npz'));runs=fit(x['cipher_train'],model,68000+i);best=max(runs,key=lambda z:z['score']);out=d.apply(x['cipher_test'],best['key']);truthscore=objective(x['plaintext_train'],model['table'])
  old.append({'language':x['language'],'case':x['case'],'old_accuracy':x['letter_accuracy'],'revised_accuracy':acc(out,x['plaintext_test']),'truth_training_score':truthscore,'best_training_score':best['score'],'wrong_but_beats_truth':acc(out,x['plaintext_test'])<.9 and best['score']>truthscore+1e-6,'below_truth':best['score']<truthscore-1e-6,'runs':runs,'heldout_output':out});print('old',x['language'],x['case'],flush=True)
 save('OLD-DIAGNOSIS.json',old);fresh=[]
 for li,(lang,path) in enumerate(d.sources.items()):
  ws=d.sourcewords(path);start=int(.6*len(ws));end=int(.8*len(ws));model=d.np.load(OLD/(lang+'-model.npz'))
  for case in range(3):
   offset=start+case*500;assert offset+120<=end;block=ws[offset:offset+120];enc=d.np.arange(27,dtype=d.np.int16);enc[:26]=d.np.random.default_rng(68100+li*100+case).permutation(26);shuffled=block[:20];random.Random(68200+li*100+case).shuffle(shuffled)
   for ai,(arm,words) in enumerate([('20consecutive',block[:20]),('20shuffled',shuffled),('100consecutive',block[:100])]):
    plain=' '.join(words);cipher=d.apply(plain,enc);runs=fit(cipher,model,68300+li*100+case*3+ai)
    fresh.append({'language':lang,'case':case,'arm':arm,'source':str(path),'train_source_range':[offset,offset+(100 if ai==2 else 20)],'test_source_range':[offset+100,offset+120],'plaintext_train':plain,'plaintext_test':' '.join(block[100:]),'cipher_train':cipher,'cipher_test':d.apply(' '.join(block[100:]),enc),'runs':runs,'selected':max(range(4),key=lambda j:runs[j]['score']),'truth_training_score':objective(plain,model['table'])});print('fresh fit',lang,case,arm,flush=True)
 save('FRESH-KEYS.json',fresh);save('KEY-FREEZE.json',{'sha256':sha(R/'FRESH-KEYS.json')});print('Fresh keys frozen')
elif stage=='test':
 assert sha(R/'FRESH-KEYS.json')==load(R/'KEY-FREEZE.json')['sha256'];out=[]
 for x in load(R/'FRESH-KEYS.json'):
  for method,j in [('baseline',0),('revised',x['selected'])]:
   fit=x['runs'][j];decoded=d.apply(x['cipher_test'],fit['key']);a=acc(decoded,x['plaintext_test']);trainchars=set(x['plaintext_train'])-{' '};testchars=[c for c in x['plaintext_test'] if c!=' ']
   out.append({'language':x['language'],'case':x['case'],'arm':x['arm'],'method':method,'letter_accuracy':a,'exact_word_fraction':sum(a==b for a,b in zip(decoded.split(),x['plaintext_test'].split()))/20,'passes':a>=.9,'training_score':fit['score'],'truth_training_score':x['truth_training_score'],'below_truth':fit['score']<x['truth_training_score']-1e-6,'wrong_but_beats_truth':a<.9 and fit['score']>x['truth_training_score']+1e-6,'test_letter_coverage':sum(c in trainchars for c in testchars)/len(testchars),'plaintext':x['plaintext_test'],'decoded':decoded})
 save('FRESH-RESULTS.json',out);summary=[]
 for lang in d.sources:
  for arm in ['20consecutive','20shuffled','100consecutive']:
   for method in ['baseline','revised']:
    rr=[x for x in out if (x['language'],x['arm'],x['method'])==(lang,arm,method)];summary.append({'language':lang,'arm':arm,'method':method,'passed':sum(x['passes'] for x in rr),'cases':3,'qualified':all(x['passes'] for x in rr),'accuracies':[round(x['letter_accuracy'],3) for x in rr]})
 save('SUMMARY.json',summary);body='<h1>Short-sample diagnosis — v68</h1><p>Four independent searches versus one; 20 consecutive, the same20 shuffled, and100 consecutive training words. Keys frozen before heldout scoring. Same source works, fresh positions; all failures retained. Voynich remains closed.</p><table><tr><th>Language</th><th>Arm</th><th>Method</th><th>Passed</th><th>Letter recovery</th></tr>'
 for x in summary:body+=f"<tr><td>{x['language']}</td><td>{x['arm']}</td><td>{x['method']}</td><td>{x['passed']}/3</td><td>{x['accuracies']}</td></tr>"
 body+='</table>'
 for n in ['PROTOCOL.json','FREEZE.json','OLD-DIAGNOSIS.json','FRESH-KEYS.json','KEY-FREEZE.json','FRESH-RESULTS.json','SUMMARY.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Search diagnosis v68</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}td,th{padding:9px;text-align:left}</style>'+body,encoding='utf-8');print(json.dumps(summary))
