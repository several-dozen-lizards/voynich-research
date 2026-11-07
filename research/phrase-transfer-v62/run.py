from pathlib import Path
import json,re,hashlib,importlib.util,sys,collections,html
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('v61',P/'phrase-diagnosis-v61/run.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
SOURCE=P/'frequency-atlas-v48/rows.json'
def panels():
 rows=load(SOURCE);coverage=collections.defaultdict(set)
 for r in rows:coverage[r[6]].add(r[0])
 groups={}
 for hand,lang,section in [('1','A','Botanical'),('1','A','Recipes'),('2','B','Botanical'),('2','B','Balneological')]:
  rr=[r for r in rows if r[0] in ('H','F') and r[2:6]==[section,hand,lang,'P'] and coverage[r[6]]=={'H','F'}]
  fs=sorted({re.match(r'f\d+',r[1])[0] for r in rr},key=lambda f:hashlib.sha256(('v62-fixed:'+f).encode()).hexdigest())
  train=set(fs[:len(fs)//2]);test=set(fs[len(fs)//2:]);assert not train&test
  for tr in ('H','F'):
   key=f'{hand}-{lang}-{section}-{tr}';groups[key]={'train_folios':sorted(train),'test_folios':sorted(test),'train':[r for r in rr if r[0]==tr and re.match(r'f\d+',r[1])[0] in train],'test':[r for r in rr if r[0]==tr and re.match(r'f\d+',r[1])[0] in test]}
 return groups
def details(rows,phrase):
 fs=collections.Counter();loc=[]
 for r in rows:
  n=v.old.counts([r[7]],'interior','bigrams')[tuple(phrase.split())]
  if n:fs[re.match(r'f\d+',r[1])[0]]+=n;loc.append({'locator':r[6],'count':n,'line':r[7]})
 return {'folio_counts':dict(fs),'occurrences':loc}
def main(stage):
 groups=panels()
 if stage=='train':
  assert not (R/'FREEZE.json').exists(),'Frozen run exists; do not overwrite'
  protocol={'scope':'Four previously supported hand/Currier/section/P strata; shared H/F loci. Interior-start right bigrams only. No semantic interpretation.', 'split':'Hash order v62-fixed:<numbered folio>; first floor(n/2) training, remainder test; same H/F allocation; recto/verso/foldouts grouped. Prior analyses exposed these pages: retrospective held-out procedure, not untouched confirmation.', 'selection':'Exact v61 top five training pairs, count>=2, rank excess/sqrt(expected+1), lexical ties. 999 shuffles. No held-out feature selection.', 'null':'v59 unchanged: within-line contiguous readable interiors shuffled; first/last and unknown barriers fixed. Broad position preserved, not exact interior ordinal.', 'test':'999 permutations, fixed candidate phrase tails, within-panel Bonferroni candidate count and global Bonferroni total frozen tests. Positive excess and global p<=.05. Agreement requires exact phrase selected and passing in both H/F of same stratum; H/F not independent replication.', 'support':'Require >=3 training and >=3 test folios and >=100 readable words in each; otherwise unestimable without resplitting. All failures retained.'}
  save('PROTOCOL.json',protocol);out={};allocation={}
  for i,(key,g) in enumerate(groups.items()):
   allocation[key]={k:g[k] for k in ('train_folios','test_folios')}
   words={f:sum(w is not None for r in g[f] for w in r[7]) for f in ('train','test')}
   ok=min(len(g[f+'_folios']) for f in ('train','test'))>=3 and min(words.values())>=100
   res=v.test([r[7] for r in g['train']],62000+i)[:5] if ok else []
   out[key]={'status':'eligible' if ok else 'not estimable','words':words,'candidates':res}
   print('training',key,len(res),flush=True)
  save('ALLOCATION.json',allocation);save('FROZEN-CANDIDATES.json',out)
  save('FREEZE.json',{str(p):sha(p) for p in [R/'PROTOCOL.json',R/'ALLOCATION.json',R/'FROZEN-CANDIDATES.json',Path(__file__),SOURCE,P/'phrase-diagnosis-v61/run.py',P/'combination-null-v59/run.py']})
 elif stage=='test':
  for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h,p
  frozen=load(R/'FROZEN-CANDIDATES.json');total=sum(len(x['candidates']) for x in frozen.values());results={}
  for i,(key,g) in enumerate(groups.items()):
   targets=[tuple(x['phrase'].split()) for x in frozen[key]['candidates']]
   res=v.test([r[7] for r in g['test']],63000+i,targets) if targets else []
   for x in res:
    x['p_global']=min(1,x['p_phrase']*total);x['pass_global']=x['excess']>0 and x['p_global']<=.05;x.update(details(g['test'],x['phrase']))
   results[key]=res;print('test',key,sum(x['pass_global'] for x in res),flush=True)
  agreement=[]
  for key,res in results.items():
   if not key.endswith('-H'):continue
   other={x['phrase']:x for x in results[key[:-1]+'F']}
   for x in res:
    if x['phrase'] in other:agreement.append({'stratum':key[:-2],'phrase':x['phrase'],'H_p':x['p_global'],'F_p':other[x['phrase']]['p_global'],'both_pass':x['pass_global'] and other[x['phrase']]['pass_global']})
  save('TEST-RESULTS.json',results);save('AGREEMENT.json',agreement)
  summary={'frozen_tests':total,'global_passes':sum(x['pass_global'] for rs in results.values() for x in rs),'common_selected_pairs':len(agreement),'both_readings_pass':sum(x['both_pass'] for x in agreement),'old_results':'v59-v61 unchanged','limits':'Retrospective folio split; one split only. H/F alternate readings, not independent replication. Broad line position controlled; exact ordinal not controlled. Non-rejection is not proof of random language.'};save('RESULTS.json',summary)
  body='<h1>Held-out phrase transfer — v62</h1><p>Training folios selected the pairs; frozen lists preceded test scoring. Whole numbered folios stay together. H/F are separate readings. All candidates and failures are shown.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre>'
  for key,rs in results.items():
   body+='<h2>'+html.escape(key)+'</h2><table><tr><th>Pair</th><th>Observed</th><th>Null mean</th><th>Folios</th><th>Panel p</th><th>Global p</th></tr>'
   for x in rs:body+=f"<tr><td>{html.escape(x['phrase'])}</td><td>{x['observed']}</td><td>{x['expected']:.2f}</td><td>{len(x['folio_counts'])}</td><td>{x['p_fixed_candidates']:.3f}</td><td>{x['p_global']:.3f}</td></tr>"
   body+='</table>'
  for n in ['PROTOCOL.json','ALLOCATION.json','FROZEN-CANDIDATES.json','FREEZE.json','TEST-RESULTS.json','AGREEMENT.json']:body+=f'<p><a href="{n}">{n}</a></p>'
  (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Phrase transfer v62</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f5f2e9;color:#193c39}td,th{padding:8px;text-align:left;border-bottom:1px solid #ccc}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8')
  save('VERIFICATION.json',{'freeze_hashes_pass':True,'folio_disjoint':all(not set(g['train_folios'])&set(g['test_folios']) for g in groups.values()),'test_count':total});print(json.dumps(summary))
if __name__=='__main__':main(sys.argv[1])

