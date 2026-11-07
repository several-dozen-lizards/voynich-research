from pathlib import Path
import json,hashlib,collections,random,math
P=Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for section in ['local','external']:
 for n,h in load('FREEZE.json')[section].items():assert sha(P/n if section=='local' else Path(n))==h,n
checks['initial_code_protocol_source_freeze_intact']=True
for freeze in ['INPUT-FREEZE.json','SURFACE-PARSER-FREEZE.json','SUPERVISED-DIAGNOSTIC-FREEZE.json']:
 for n,h in load(freeze).items():assert sha(P/n)==h,n
checks['admitted_inputs_and_supplement_freezes_intact']=True
assert sha(P/'ASSIGNMENTS.json')==load('ASSIGNMENT-FREEZE.json')['sha256'];checks['saved_assignments_hash_intact']=True
trials=[json.loads(l) for l in (P/'synthetic-trials.jsonl').read_text().splitlines()];qual=load('QUALIFICATION.json');assert len(trials)==240
for r in qual['regimes']:
 ts=[t for t in trials if t['regime']==r['regime']];assert len(ts)==40 and sorted(t['trial'] for t in ts)==list(range(40));n=sum(t['selected_k']==t['true_k'] for t in ts);assert n==r['exact'] and r['pass']==(n>=r['required'])
assert qual['status']=='FAIL' and not all(r['pass'] for r in qual['regimes']);checks['all240_controls_and_failed_gate_recounted']=True
inp=load('BLIND-INPUT.json');key=load('ANSWER-KEY.json');result=load('RESULTS.json');fits={(f['stratum'],f['arm']):f for f in load('ASSIGNMENTS.json')};assert len(fits)==8 and not result['automatic_historical_run'];checks['failed_selector_never_applied_to_historical_data']=True
assert len(inp)==len(key)==2254;checks['2254_occurrences_and_gold_keys_agree']=True
assert set(key)=={r['id'] for r in inp}
def independent_ari(y,z):
 n=len(y);total=n*(n-1)//2
 if not total:return None
 choose=lambda counts:sum(v*(v-1)/2 for v in counts.values())
 aa=choose(collections.Counter(y));bb=choose(collections.Counter(z));ab=choose(collections.Counter(zip(y,z)));exp=aa*bb/total;den=(aa+bb)/2-exp
 return (ab-exp)/den if den else 0.
for saved in result['results']:
 rs=[r for r in inp if r['stratum']==saved['stratum']];roles=load('PROTOCOL.json')['historical']['targets'][rs[0]['target']];fit=fits[(saved['stratum'],saved['arm'])]
 for arm,outkey in [('actual','actual'),('null','context_null')]:
  ass=fit[arm]['assignments'];train=[a for a in ass if a['split']=='train' and key[a['id']]['upos'] in roles];test=[a for a in ass if a['split']=='test' and key[a['id']]['upos'] in roles];bycluster=collections.defaultdict(collections.Counter)
  for a in train:bycluster[a['cluster']][key[a['id']]['upos']]+=1
  mapping={c:min(v,key=lambda x:(-v[x],x)) for c,v in bycluster.items()};yy=[key[a['id']]['upos'] for a in test];zz=[a['cluster'] for a in test];pp=[mapping.get(z,'UNKNOWN') for z in zz];n=collections.Counter(yy);acc=sum(sum(y==r and p==r for y,p in zip(yy,pp))/n[r] for r in n)/len(n)
  savedout=saved[outkey];assert abs(savedout['balanced_recall']-acc)<1e-12;ar=independent_ari(yy,zz);assert abs(savedout['ARI']-ar)<1e-12
  rng=random.Random(1074602);nn=0
  for _ in range(199):
   perm=yy.copy();rng.shuffle(perm);nn+=independent_ari(perm,zz)>=ar
  p=(1+nn)/200;assert savedout['p_raw']==p and savedout['p_bonferroni8']==min(1,8*p)
  assert savedout['test_counts']==dict(n)
  rows={r['id']:r for r in rs};blocks=len({rows[a['id']]['page'] for a in test});assert blocks==savedout['test_blocks'];tc=collections.Counter(key[a['id']]['upos'] for a in train);support=all(tc[r]>=20 and n[r]>=20 for r in roles) and blocks>=5;assert support==savedout['support']
  assert savedout['predictions']==[{'id':a['id'],'gold':y,'cluster':z,'prediction':pr} for a,y,z,pr in zip(test,yy,zz,pp)]
 a,b=saved['actual'],saved['context_null'];passed=a['support'] and fit['actual']['k']==2 and a['balanced_recall']>=.8 and a['ARI']>=.5 and a['p_bonferroni8']<=.05 and a['balanced_recall']-b['balanced_recall']>=.1
 assert saved['status']==('PASS' if passed else 'FAIL' if a['support'] else 'NOT_ESTIMABLE')
checks['all16_actual_and_null_metrics_independently_recomputed']=True
checks['all8_support_and_recovery_decisions_recomputed']=True
for f in load('SUPERVISED-DIAGNOSTIC.json'):
 pred=f['predictions'];n=collections.Counter(p['gold'] for p in pred);correct=collections.Counter(p['gold'] for p in pred if p['gold']==p['prediction']);acc=sum(correct[y]/n[y] for y in n)/len(n) if len(n)==2 else None;assert f['balanced_recall']==acc
checks['supervised_diagnostic_recalls_recounted']=True
assert all(load('INDEPENDENT-INPUT-AUDIT.json')['checks'].values());checks['independent_javascript_input_reconstruction_passed']=True
out={'status':'PASS','checks':checks,'scientific_qualification':'FAIL, not overridden by engineering checks','historical_status_counts':dict(collections.Counter(r['status'] for r in result['results']))}
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
