from pathlib import Path
import importlib.util,json,collections,math,hashlib
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('role',P/'run.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
f=m.load(P/'SUPERVISED-DIAGNOSTIC-FREEZE.json')
for n,h in f.items():assert m.sha(P/n)==h,n
assert (P/'ASSIGNMENT-FREEZE.json').exists()
assert m.sha(P/'ASSIGNMENTS.json')==m.load(P/'ASSIGNMENT-FREEZE.json')['sha256']
rows=m.load(P/'BLIND-INPUT.json');gold=m.load(P/'ANSWER-KEY.json');cfg=m.load(P/'PROTOCOL.json')['historical'];out=[]
for st in sorted({r['stratum'] for r in rows}):
 rs=[r for r in rows if r['stratum']==st];roles=cfg['targets'][rs[0]['target']];tr=[r for r in rs if r['split']=='train' and gold[r['id']]['upos'] in roles];te=[r for r in rs if r['split']=='test' and gold[r['id']]['upos'] in roles];counts=collections.defaultdict(collections.Counter);total=collections.Counter();vocab=set()
 for r in tr:
  y=gold[r['id']]['upos'];features=m.E.fs(r);counts[y].update(features);total[y]+=len(features);vocab.update(features)
 labels=sorted(counts);predictions=[];correct=collections.Counter();n=collections.Counter()
 if len(labels)==2:
  for r in te:
   y=gold[r['id']]['upos'];pred=max(labels,key=lambda z:sum(math.log((counts[z][v]+1)/(total[z]+len(vocab)+1)) for v in m.E.fs(r)));n[y]+=1;correct[y]+=pred==y;predictions.append({'id':r['id'],'gold':y,'prediction':pred})
 out.append({'stratum':st,'train_counts':dict(collections.Counter(gold[r['id']]['upos'] for r in tr)),'test_counts':dict(n),'balanced_recall':sum(correct[y]/n[y] for y in n)/len(n) if len(n)==2 else None,'predictions':predictions,'status':'Diagnostic supervised benchmark, not blind qualification'})
m.dump('SUPERVISED-DIAGNOSTIC.json',out)
for r in out:print(r['stratum'],r['balanced_recall'])
