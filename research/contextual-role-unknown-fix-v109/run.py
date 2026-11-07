from pathlib import Path
import json,hashlib,collections,math,random,time
P=Path(__file__).resolve().parent;OLD=P.parent/'contextual-role-recovery-v107';AUDIT=P.parent/'contextual-role-error-audit-v108'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def features(r):
 c=r['context'];return [str(i)+':'+v for i,v in enumerate(c)]+['L:'+c[0]+'|'+c[1],'R:'+c[2]+'|'+c[3]]
def fit(rows,key,roles):
 counts={r:collections.Counter() for r in roles};n=collections.Counter();vocab=set()
 for row in rows:
  y=key[row['id']]
  if y not in roles:continue
  ff=features(row);counts[y].update(ff);vocab.update(ff);n[y]+=1
 return {'counts':counts,'totals':{y:sum(c.values()) for y,c in counts.items()},'n':n,'vocab':vocab,'roles':sorted(roles)}
def score(ff,model,repair):
 used=[f for f in ff if f in model['vocab']] if repair else ff
 s={y:sum(math.log((model['counts'][y][f]+1)/(model['totals'][y]+len(model['vocab'])+1)) for f in used) for y in model['roles']}
 tied=abs(s[model['roles'][0]]-s[model['roles'][1]])<=1e-12
 pred=None if repair and tied else max(model['roles'],key=lambda y:s[y]);top=max(s.values());exp={y:math.exp(v-top) for y,v in s.items()};z=sum(exp.values());prob={y:v/z for y,v in exp.items()}
 if repair and tied:prob={y:.5 for y in model['roles']}
 return {'prediction':pred,'scores':s,'probabilities':prob,'known_features':sum(f in model['vocab'] for f in ff),'abstained':pred is None}
def predict(rows,key,model,repair):
 out=[]
 for r in rows:
  y=key[r['id']]
  if y not in model['roles']:continue
  a=score(features(r),model,repair);credit=.5 if a['prediction'] is None else float(a['prediction']==y)
  out.append({'id':r['id'],'block':r['page'],'gold':y,**a,'correct_credit':credit,'strict_correct':float(a['prediction']==y),'log_loss':-math.log(a['probabilities'][y]),'brier':sum((a['probabilities'][z]-float(z==y))**2 for z in model['roles'])})
 return out
def metric(pred,roles):
 by={}
 for y in roles:
  rr=[r for r in pred if r['gold']==y];n=len(rr);by[y]={'n':n,'correct_credit':sum(r['correct_credit'] for r in rr),'strict_correct':sum(r['strict_correct'] for r in rr),'abstentions':sum(r['abstained'] for r in rr),'log_loss_sum':sum(r['log_loss'] for r in rr),'brier_sum':sum(r['brier'] for r in rr)}
 if not all(v['n'] for v in by.values()):return {'n':len(pred),'by_role':by,'defined':False}
 return {'n':len(pred),'by_role':by,'defined':True,'balanced_correct_credit':sum(v['correct_credit']/v['n'] for v in by.values())/2,'strict_balanced_recall':sum(v['strict_correct']/v['n'] for v in by.values())/2,'coverage':1-sum(v['abstentions'] for v in by.values())/len(pred),'balanced_log_loss':sum(v['log_loss_sum']/v['n'] for v in by.values())/2,'balanced_brier':sum(v['brier_sum']/v['n'] for v in by.values())/2}
def shuffle_context(rows,seed):
 out=[dict(r,context=r['context'].copy()) for r in rows];rng=random.Random(seed)
 for block in sorted({r['page'] for r in out}):
  ix=[i for i,r in enumerate(out) if r['page']==block]
  for col in range(4):
   vals=[out[i]['context'][col] for i in ix];rng.shuffle(vals)
   for i,v in zip(ix,vals):out[i]['context'][col]=v
 return out
def shuffle_labels(rows,key,seed):
 out=key.copy();rng=random.Random(seed)
 for block in sorted({r['page'] for r in rows}):
  ids=[r['id'] for r in rows if r['page']==block];ys=[key[i] for i in ids];rng.shuffle(ys)
  for i,y in zip(ids,ys):out[i]=y
 return out
def quantile(a,q):
 a=sorted(a);p=(len(a)-1)*q;i=int(p);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(p-i) if a else None
def delta(a,b):return {'balanced_correct_credit':b['balanced_correct_credit']-a['balanced_correct_credit'],'strict_balanced_recall':b['strict_balanced_recall']-a['strict_balanced_recall'],'balanced_log_loss':b['balanced_log_loss']-a['balanced_log_loss'],'balanced_brier':b['balanced_brier']-a['balanced_brier']}
def bootstrap(old,new,roles,seed):
 blocks=sorted({r['block'] for r in old});a={b:[r for r in old if r['block']==b] for b in blocks};bb={b:[r for r in new if r['block']==b] for b in blocks};rng=random.Random(seed);ds=[];undefined=0
 for _ in range(2000):
  sample=rng.choices(blocks,k=len(blocks));ma=metric([r for b in sample for r in a[b]],roles);mb=metric([r for b in sample for r in bb[b]],roles)
  if not ma['defined'] or not mb['defined']:ds.append(None);undefined+=1
  else:ds.append(delta(ma,mb))
 keys=['balanced_correct_credit','strict_balanced_recall','balanced_log_loss','balanced_brier'];return {'seed':seed,'blocks':len(blocks),'n_draws':2000,'undefined':undefined,'intervals95':{k:[quantile([d[k] for d in ds if d is not None],q) for q in [.025,.975]] for k in keys}},ds
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for folder,entry in [('prior',OLD),('audit',AUDIT)]:
  for n,h in f[folder].items():assert sha(entry/n)==h,n

def fixtures():
 verify();roles=['A','B'];rows=[];key={}
 for i in range(10):
  y='A' if i<8 else 'B';r={'id':str(i),'page':str(i),'context':['a','b','c','d'] if y=='A' else ['e','f','g','h']};rows.append(r);key[r['id']]=y
 model=fit(rows,key,roles);u=['never_seen_one','never_seen_two'];z=score(u,model,True);assert z['prediction'] is None and z['scores']=={'A':0,'B':0} and z['probabilities']=={'A':.5,'B':.5}
 known=features(rows[0]);a=score(known,model,True);b=score(known+u,model,True);assert a['scores']==b['scores'] and a['prediction']==b['prediction']
 assert score(known,model,False)['scores']==a['scores'];assert a['prediction']=='A';assert all(model['counts']['B'][f]==0 for f in known)
 rev=score(known[::-1],model,True);assert all(abs(rev['scores'][y]-a['scores'][y])<1e-12 for y in roles)
 key2={i:('B' if y=='A' else 'A') for i,y in key.items()};m2=fit(rows,key2,roles);assert score(u,m2,True)['prediction'] is None
 assert score(u,model,False)['prediction']=='B'
 checks={'unequal_training_classes_no_evidence_abstains':True,'zero_evidence_probabilities_equal':True,'globally_unknown_features_leave_known_margin_unchanged':True,'known_only_scores_identical_to_old':True,'class_specific_absence_still_supplies_evidence':True,'feature_order_invariant':True,'class_rename_does_not_create_unknown_preference':True,'old_small_class_bias_reproduced':True};dump('FIXTURES.json',{'status':'PASS','checks':checks});print(json.dumps(checks))

def run():
 verify();assert load(P/'FIXTURES.json')['status']=='PASS';assert not (P/'RESULTS.json').exists();rows=load(OLD/'BLIND-INPUT.json');key={i:v['upos'] for i,v in load(OLD/'ANSWER-KEY.json').items()};cfg=load(OLD/'PROTOCOL.json')['historical'];prior={r['stratum']:r for r in load(OLD/'RESULTS.json')['results']};saved={r['stratum']:r for r in load(OLD/'SUPERVISED-DIAGNOSTIC.json')};results=[];allpred=[];models=[];draws={}
 for si,st in enumerate(sorted(prior)):
  roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];model=fit(tr,key,roles);old=predict(te,key,model,False);new=predict(te,key,model,True)
  assert [(r['id'],r['gold'],r['prediction']) for r in old]==[(r['id'],r['gold'],r['prediction']) for r in saved[st]['predictions']]
  om,nm=metric(old,roles),metric(new,roles);assert abs(om['balanced_correct_credit']-saved[st]['balanced_recall'])<1e-12
  observed_old=[r for r in old if r['known_features']>0];observed_new=[r for r in new if r['known_features']>0];unsupported_old=[r for r in old if r['known_features']==0];unsupported_new=[r for r in new if r['known_features']==0]
  bm,bd=bootstrap(old,new,roles,1093000+si);draws[st]=bd;trans=collections.Counter()
  for a,b in zip(old,new):
   name=('correct' if a['strict_correct'] else 'wrong')+'_to_'+('abstain' if b['abstained'] else 'correct' if b['strict_correct'] else 'wrong');trans[name]+=1
   allpred.append({'stratum':st,'old':a,'new':b,'transition':name})
  models.append({'stratum':st,'class_counts':{y:dict(model['counts'][y]) for y in model['roles']},'class_totals':model['totals'],'training_role_occurrences':dict(model['n']),'vocabulary':sorted(model['vocab'])})
  record={'stratum':st,'prior_status':prior[st]['status'],'primary_supported':prior[st]['status']!='NOT_ESTIMABLE','old':om,'new':nm,'delta':delta(om,nm),'evidence_bearing_only':{'old':metric(observed_old,roles),'new':metric(observed_new,roles)},'zero_known_features':{'old':metric(unsupported_old,roles),'new':metric(unsupported_new,roles)},'transitions':dict(trans),'bootstrap':bm};results.append(record);print(st,'old',om['balanced_correct_credit'],'new',nm['balanced_correct_credit'],'strict',nm['strict_balanced_recall'],'coverage',nm['coverage'],flush=True)
 dump('PREDICTIONS.json',allpred);dump('MODELS.json',models);dump('BOOTSTRAP-DRAWS.json',draws)
 # Both controls preserve train/test source blocks; supervised labels never enter representation.
 with (P/'CONTROL-TRIALS.jsonl').open('x',encoding='utf8') as logfile:
  for si,rec in enumerate(results):
   st=rec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];control_summary=[]
   for kind,seedbase in [('context_shuffle',1091000),('training_label_shuffle',1092000)]:
    vals=[]
    for j in range(199):
     seed=seedbase+si*10000+j*2
     if kind=='context_shuffle':ctr=shuffle_context(tr,seed);cte=shuffle_context(te,seed+1);ckey=key
     else:ctr=tr;cte=te;ckey=shuffle_labels([r for r in tr if key[r['id']] in roles],key,seed)
     m=fit(ctr,ckey,roles);pr=predict(cte,key,m,True);me=metric(pr,roles);vals.append(me['balanced_correct_credit']);logfile.write(json.dumps({'stratum':st,'kind':kind,'trial':j,'seed':seed,'metric':me})+'\n');logfile.flush()
    p=(1+sum(v>=rec['new']['balanced_correct_credit']-1e-12 for v in vals))/200;control_summary.append({'kind':kind,'n':199,'mean_recovery':sum(vals)/199,'median_recovery':quantile(vals,.5),'range':[min(vals),max(vals)],'p_raw_descriptive':p,'p_bonferroni8_descriptive':min(1,8*p),'all_values':vals})
   rec['controls']=control_summary;print('controls complete',st,flush=True)
 supported=[r for r in results if r['primary_supported']];keys=list(supported[0]['delta']);overall={'panels':[r['stratum'] for r in supported],'n_panels':len(supported),'equal_panel_mean_delta':{k:sum(r['delta'][k] for r in supported)/len(supported) for k in keys},'bootstrap_intervals95':{}}
 for k in keys:
  vals=[]
  for j in range(2000):
   v=[draws[r['stratum']][j] for r in supported]
   if all(x is not None for x in v):vals.append(sum(x[k] for x in v)/len(v))
  overall['bootstrap_intervals95'][k]=[quantile(vals,q) for q in [.025,.975]]
 overall['old_equal_panel_mean_recovery']=sum(r['old']['balanced_correct_credit'] for r in supported)/len(supported);overall['new_equal_panel_mean_recovery']=sum(r['new']['balanced_correct_credit'] for r in supported)/len(supported)
 dump('RESULTS.json',{'scope':'Exposed development comparison only. Supervised scorer repaired; representation and clustering unchanged. No fresh-source qualification.','panels':results,'supported_overall':overall});verify()
if __name__=='__main__':
 import sys
 command=sys.argv[1]
 if command=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'prior':load(OLD/'SHA256SUMS.json'),'audit':load(AUDIT/'SHA256SUMS.json')});print('Fixed repair and evaluation frozen before repaired scores.')
 elif command=='fixtures':fixtures()
 elif command=='run':run()
