from pathlib import Path
import json,sys,hashlib,math,re,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;Q=T/'multiword-v2';spec=importlib.util.spec_from_file_location('positional_reference',R/'reference.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
book={(x['opener'],x['ending']):x['id'] for x in load('CLASS-CODEBOOK.json')['classes']};prefixes=['qok','qo','ot','ok','ch','sh','d','k','t','p','f','y','o','a','s'];suffixes=['aiin','ain','air','edy','eey','ar','al','ey','ol','or','y'];cache={}
def classifyword(w):
 if w is None:return None
 if w in cache:return cache[w]
 assert re.fullmatch('[a-z]+',w);p=next((x for x in prefixes if w.startswith(x)),'');remaining=w[len(p):];s=next((x for x in suffixes if remaining.endswith(x)),'');cat='other-gallows' if p in ['k','t','p','f'] else p or 'other';end='a-family' if s in ['aiin','ain','air','ar','al'] else 'y-family' if s in ['edy','eey','ey','y'] else 'ol-or' if s in ['ol','or'] else 'other';cache[w]=book[(cat,end)];return cache[w]
def classified(pp):return [dict(p,tokens=[classifyword(w) for w in p['tokens']]) for p in pp]
def digesttokens(pp):return hashlib.sha256(json.dumps([p['tokens'] for p in pp],separators=(',',':')).encode()).hexdigest()
def verifycandidate(pp,d):
 rr=ref.discover(classified(pp));assert rr['screened_slots']==d['screened_slots'] and rr['eligible']==d['eligible_candidates'];c=d['candidate']
 if c is None:assert rr['candidate'] is None
 else:assert all(rr['candidate'][k]==c[k] for k in ['start','end','width','variants'])
 return rr
GOLD={e['unit']:e['gold_slots'] for e in json.loads((T/'positive-control-1/GOLD-AUDIT.json').read_text(encoding='utf-8'))['entries']}
def oracle(pp,c):
 total=correct=0;forms={};w=c['width'];at=c['start']-1;known={tuple(v) for v in c['variants']}
 for p in pp:
  a=p['tokens'][at:at+w]
  if len(a)!=w or None in a or tuple(classifyword(x) for x in a) not in known:continue
  total+=1;correct+=any(s['word'] not in ['gradu','gra','principio','medio'] and at<=s['pos']-1<at+w for s in GOLD.get(p['unit'],[]));v=json.dumps(p['source_tokens'][at:at+w],separators=(',',':'));forms[v]=forms.get(v,0)+1
 return dict(early_occurrences=total,quality_degree_value_occurrences=correct,precision=correct/total if total else None,source_gap_forms=forms,pass_=bool(total and correct/total>=.8))
def checkgold(x,y):
 for k in ['early_occurrences','quality_degree_value_occurrences','precision','source_gap_forms']:assert x[k]==y[k]
 assert x['pass_']==y['pass']
def latin():
 results=load('LATIN-RESULTS.json');fixtures=load('PERMUTATION-REFERENCE-FIXTURES.json');aud=[]
 for r in results:
  cell=r['cell'];pp=load('latin/'+cell+'/DISCOVERY.json');fr=load('latin/'+cell+'/CANDIDATE-FREEZE.json');verifycandidate(pp,fr['discovery']);c=r['candidate']
  if c is None:aud.append(dict(cell=cell,status='NO CANDIDATE'));continue
  test=load('latin/'+cell+'/CONFIRMATION.json');ref.check_metric(ref.measure(classified(test),c),r['observed']);checkgold(oracle(pp,c),r['discovery_gold']);checkgold(oracle(test,c),r['confirmation_gold']);ff=[f for f in fixtures if f['cell']==cell];rng=ref.rand(r['confirmation']['seed']) if r.get('confirmation') else None
  for f in ff:
   qq=[]
   for p in test:
    a=p['tokens'][:]
    for i in range(len(a)-1,1,-1):
     j=1+int(next(rng)*i);a[i],a[j]=a[j],a[i]
    qq.append(dict(p,tokens=a))
   assert digesttokens(qq)==f['raw_tokens_sha256'];cl=classified(qq);assert digesttokens(cl)==f['class_tokens_sha256'];ref.check_metric(ref.measure(cl,c),f['metrics'])
  aud.append(dict(cell=cell,discovery_exact=True,confirmation_exact=True,gold_exact=True,permutation_reference_draws=len(ff)))
 save('INDEPENDENT-LATIN-AUDIT.json',dict(status='PASS',cells=aud,reference_draws=len(fixtures),distinct_source_words_classified=len(cache)));print('LATIN AUDIT PASS',flush=True)
def controls():
 ledger=load('GENERATION-LEDGER.json');evs={r['name']:r for r in load('CONTROL-EVALUATIONS.json')};assert len(ledger)==1200;aud=[];g6=0
 for i,row in enumerate(ledger,1):
  name=row['name'];d='controls/'+name;folder=R/d
  if row['status']!='GENERATED':
   ev=evs[name];assert ev.get('invalid') and ev['status']=='ERROR' and not ev['raw_pass'] and ev.get('confirmation') is None;assert load(d+'/GENERATION.json')==row;aud.append(dict(name=name,status='INVALID GENERATION RETAINED',error=row.get('error'),counted_as_clean_negative=False));continue
  geo=load(d+'/GEOMETRY.json');pp=load(d+'/PARAGRAPHS.json');assert sha(folder/'PARAGRAPHS.json')==row['paragraphs_sha256'] and sha(folder/'GEOMETRY.json')==row['geometry_sha256']
  if row['family']=='G5':
   ff=list((folder/'generated').glob('*.txt'));assert len(ff)==1;lines=[s.split() for s in ff[0].read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')];assert len(lines)==row['native_lines'] and row['seed_line_excluded'];words=[w for line in lines[1:] for w in line];assert len(words)==row['generated_tokens'] and len(words)-row['original_slots']==row['unused_tail_tokens']
  else:
   native=load(d+'/NATIVE-MECHANISM.json');gg=ref.generate('G6',{},row['seed'],line_lengths=[g['length'] for g in geo]);assert gg['table']==native['table'] and json.loads(json.dumps(gg['draws']))==native['draws'] and json.loads(json.dumps(gg['grille_offsets']))==native['grille_offsets'] and json.loads(json.dumps(gg['fidelity']))==native['fidelity'];words=[''.join(w) for line in gg['lines'] for w in line];g6+=1;del gg,native
  at=0
  for p,g in zip(pp,geo):
   a=words[at:at+g['length']];at+=g['length']
   for j in g['unknown']:a[j]=None
   assert a==p['tokens'] and p['folio']==g['folio'] and p['arm']==g['arm'];assert ('DISCOVERY' if int(hashlib.sha256(('v8-T3:'+p['folio']).encode()).hexdigest(),16)%2==0 else 'CONFIRMATION')==p['arm']
  train=[p for p in pp if p['arm']=='DISCOVERY'];dsc=load(d+'/CANDIDATE-FREEZE.json')['discovery'];verifycandidate(train,dsc);ev=evs[name]
  if dsc['candidate'] is None:assert ev['status']=='NO CANDIDATE' and not ev['raw_pass']
  else:
   test=[p for p in pp if p['arm']=='CONFIRMATION'];ref.check_metric(ref.measure(classified(test),dsc['candidate']),ev['observed'])
   if not ev['observed']['pass']:assert ev['status']=='FAIL PREDICTIONS' and ev.get('confirmation') is None and not ev['raw_pass']
   else:assert ev['confirmation']['shuffles']==10000
  aud.append(dict(name=name,native_and_class_selection_exact=True));
  del words,pp,geo,train
  import gc;gc.collect()
  if i%50==0:save('INDEPENDENT-CONTROL-PROGRESS.json',dict(completed=i,total=1200,G6_seed_replays=g6));print('audited',i,flush=True)
 save('INDEPENDENT-CONTROL-AUDIT.json',dict(status='PASS',datasets=len(aud),G5_native_prefixes=sum(r['status']=='GENERATED' and r['family']=='G5' for r in ledger),G6_seed_replays=g6,invalid_generation_trials=sum(r['status']!='GENERATED' for r in ledger),results=aud,distinct_source_words_classified=len(cache)));print('CONTROL AUDIT PASS',flush=True)
if __name__=='__main__':
 latin()
 if '--latin-only' not in sys.argv:controls()
