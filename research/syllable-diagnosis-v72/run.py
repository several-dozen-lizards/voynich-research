from pathlib import Path
import sys,importlib.util,json,hashlib,collections,random,html
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
stage=sys.argv[1];sys.argv[1]='library';s=importlib.util.spec_from_file_location('v71',P/'syllable-decoder-v71/run.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old);sys.argv[1]=stage
SOURCE=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-abbreviation-v33\claude-abbrev-2026-10-22\sources\Latin.xml')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def model(parsed):
 inventory=sorted({s for w in parsed for s in w});ids={s:i+1 for i,s in enumerate(inventory)};n=len(ids)+1;c=np.zeros((n,n));freq=np.zeros(n)
 for w in parsed:
  seq=[0]+[ids[s] for s in w]+[0]
  for a,b in zip(seq,seq[1:]):c[a,b]+=1;freq[b]+=1
 return inventory,ids,np.log((c+.1)/(c.sum(1,keepdims=True)+.1*n)),freq
def objective(cipher,mapping,log):
 return sum(log[a,b] for w in cipher for a,b in zip([0]+[mapping[u] for u in w],[mapping[u] for u in w]+[0]))
def refine(cipher,mapping,log):
 observed=sorted(mapping);loc={u:i for i,u in enumerate(observed)};M=len(loc);counts=collections.Counter()
 for w in cipher:
  seq=[M]+[loc[u] for u in w]+[M];counts.update(zip(seq,seq[1:]))
 pairs=np.array(list(counts));a,b=pairs.T;weights=np.array(list(counts.values()));key=np.array([mapping[u] for u in observed]+[0]);history=[];current=float(log[key[a],key[b]]@weights)
 for sweep in range(3):
  changes=0
  for i in range(M):
   candidates=np.tile(key,(len(log)-1,1));target=np.arange(1,len(log));candidates[:,i]=target
   for j,value in enumerate(key[:-1]):
    if j!=i:candidates[value-1,j]=key[i]
   scores=(log[candidates[:,a],candidates[:,b]]*weights).sum(axis=1);best=int(np.argmax(scores))
   if scores[best]>current+1e-8:key=candidates[best].copy();current=float(scores[best]);changes+=1
  history.append({'sweep':sweep,'changes':changes,'score':current})
  if not changes:break
 return {'mapping':{u:int(key[i]) for i,u in enumerate(observed)},'score':current,'sweeps':history}
def evaluate(mapping,inventory,testgroups,truth):
 decoded=[[inventory[mapping[u]-1] if u in mapping else '[UNK]' for u in w] for w in testgroups];pairs=[(a,b) for w,v in zip(decoded,truth) for a,b in zip(w,v)];resolved=[(a,b) for a,b in pairs if a!='[UNK]'];coverage=len(resolved)/len(pairs);accuracy=sum(a==b for a,b in resolved)/max(1,len(resolved));word=sum(a==b for a,b in zip(decoded,truth))/len(truth)
 return {'coverage':coverage,'resolved_accuracy':accuracy,'whole_word_accuracy':word,'passes':coverage>=.8 and accuracy>=.9 and word>=.8,'decoded':[''.join(w) for w in decoded]}
if stage=='freeze':
 protocol={'revision':'v71 objective/definitions unchanged; take best of same4 annealing starts, then up to3 deterministic coordinate sweeps. For each group evaluate every inventory syllable, swapping if occupied or replacing if unused; accept only strict objective improvement. No oracle initialization or test selection.', 'old_diagnosis':'Compare v71 fitted score with planted-map score where all training syllables in inventory; count unreachable true syllables, unseen-test coverage ceiling and segmentation invariants. Refine old keys only as diagnosis, retain original failures.', 'definitions':'Check round-trip and one-vowel-nucleus invariants, and a small fixed spelling-example list. These are implementation checks, not independent phonological labels. Encoding/decoding use same definitions, so semantic correctness of syllables remains unqualified. No revised syllabifier selected from outcomes.', 'fresh_source':'Latin.xml Bible; distinct work from v71 source, previously used elsewhere in project, fresh to this syllable pipeline. Exclude LiberJuratus.txt as a Latin control because opening passage is English. No claim of period/genre matching.', 'fresh_allocation':'First12000 raw words train syllable model. Raw offsets20000/22000/24000 each1200words: first900yield first300 retained fitting words; final300yield first20retained test words. Compare fitting first100 vs300 on identical test. Stop if support insufficient; no resampling. Same ciphertext key percase bothsizes.', 'gate':'For each size/method all3 fresh cases coverage>=.8,resolvedsyllableaccuracy>=.9,wholewordrecovery>=.8. Freeze all candidate mappings before applying heldout. Report within-source fresh control, not successful cross-work model transfer. Voynich remains closed regardless until result reviewed.', 'limits':'Higher sample size combines context/coverage; original objective is within-word syllable bigrams only, does not model cross-word syntax. Restricted definitions and sparse inventory may remain obstacles.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SOURCE,P/'syllable-decoder-v71/run.py',P/'syllable-decoder-v71/CONTROL-KEYS.json']});print('Revision frozen')
elif stage=='fit':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 words,inv,ids,log,freq,cov=old.prepare();diagnosis=[]
 for x in load(P/'syllable-decoder-v71/CONTROL-KEYS.json'):
  cipher=[[x['true_encoding'][s] for s in w] for w in x['training_syllables']];truthmap={x['true_encoding'][s]:ids[s] for w in x['training_syllables'] for s in w if s in ids};missing=sorted({s for w in x['training_syllables'] for s in w if s not in ids});base=x['attempts'][x['selected']];new=refine(cipher,base['mapping'],log);oracle=objective(cipher,truthmap,log) if not missing else None
  diagnosis.append({'case':x['case'],'old_score':base['score'],'refined_score':new['score'],'oracle_score':oracle,'missing_inventory_truth':missing,'refined_recovery':evaluate(new['mapping'],inv,x['test_groups'],x['test_syllables']),'refined_map':new,'all_roundtrip':all(''.join(ss)==w for ss,w in zip(x['training_syllables'],x['training_plain'])),'one_nucleus':all(sum(c in 'aeiou' for c in s)==1 for ss in x['training_syllables'] for s in ss)});print('old diagnosis',x['case'],flush=True)
 save('OLD-DIAGNOSIS.json',diagnosis)
 raw=old.d.sourcewords(SOURCE);parsed=[old.syllables(w) for w in raw[:12000]];good=[w for w in parsed if w];inv,ids,log,freq=model(good);save('INVENTORY.json',inv);save('SOURCE-COVERAGE.json',{'raw_training_words':12000,'retained':len(good),'inventory':len(inv)});fresh=[]
 for case,offset in enumerate([20000,22000,24000]):
  training=[old.syllables(w) for w in raw[offset:offset+900] if old.syllables(w)][:300];test=[old.syllables(w) for w in raw[offset+900:offset+1200] if old.syllables(w)][:20];assert len(training)==300 and len(test)==20
  allsy=sorted({s for w in training+test for s in w});labels=[f'G{i:03d}' for i in range(len(allsy))];random.Random(72000+case).shuffle(labels);encoding=dict(zip(allsy,labels))
  for size in [100,300]:
   cipher=[[encoding[s] for s in w] for w in training[:size]];base=old.fit(cipher,log,freq,72100+case*10+size);best=base['attempts'][base['selected']];new=refine(cipher,best['mapping'],log);missing=sorted({s for w in training[:size] for s in w if s not in ids});true={encoding[s]:ids[s] for w in training[:size] for s in w if s in ids};oracle=objective(cipher,true,log) if not missing else None
   fresh.append({'case':case,'size':size,'source_training_range':[offset,offset+900],'source_test_range':[offset+900,offset+1200],'baseline':base,'revised':new,'test_groups':[[encoding[s] for s in w] for w in test],'test_truth':test,'oracle_score_diagnostic':oracle,'missing_training_inventory':missing});print('fresh fitted',case,size,flush=True)
 save('FRESH-KEYS.json',fresh);save('KEY-FREEZE.json',{n:sha(R/n) for n in ['FRESH-KEYS.json','INVENTORY.json','SOURCE-COVERAGE.json']});print('Fresh keys frozen')
elif stage=='test':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 for n,h in load(R/'KEY-FREEZE.json').items():assert sha(R/n)==h
 inv=load(R/'INVENTORY.json');results=[]
 for x in load(R/'FRESH-KEYS.json'):
  for method in ['baseline','revised']:
   chosen=x['baseline']['attempts'][x['baseline']['selected']] if method=='baseline' else x['revised'];res=evaluate(chosen['mapping'],inv,x['test_groups'],x['test_truth']);results.append(dict(res,case=x['case'],size=x['size'],method=method,score=chosen['score'],oracle_score=x['oracle_score_diagnostic'],missing_training_inventory=x['missing_training_inventory'],truth=[''.join(w) for w in x['test_truth']]))
 save('FRESH-RESULTS.json',results);gates={f'{size}-{method}':all(x['passes'] for x in results if x['size']==size and x['method']==method) for size in [100,300] for method in ['baseline','revised']};save('GATE.json',gates)
 body='<h1>Syllable failure diagnosis — v72</h1><p>Search-only revision, fixed definitions; larger fitting samples and a distinct known-text source. All mappings frozen before fresh heldout scoring. Voynich remains closed.</p><pre>'+html.escape(json.dumps(gates,indent=2))+'</pre><table><tr><th>Case</th><th>Words</th><th>Method</th><th>Coverage</th><th>Resolved syllables correct</th><th>Words correct</th></tr>'
 for x in results:body+=f"<tr><td>{x['case']}</td><td>{x['size']}</td><td>{x['method']}</td><td>{x['coverage']:.1%}</td><td>{x['resolved_accuracy']:.1%}</td><td>{x['whole_word_accuracy']:.1%}</td></tr>"
 body+='</table>'
 for n in ['PROTOCOL.json','FREEZE.json','OLD-DIAGNOSIS.json','SOURCE-COVERAGE.json','INVENTORY.json','FRESH-KEYS.json','KEY-FREEZE.json','FRESH-RESULTS.json','GATE.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Syllable diagnosis v72</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}td,th{padding:8px}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8');print(json.dumps(gates));print(json.dumps([{k:v for k,v in x.items() if k not in ['truth','decoded','missing_training_inventory']} for x in results]))
