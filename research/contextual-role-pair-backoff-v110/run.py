from pathlib import Path
import json,hashlib,collections,importlib.util,time,math
P=Path(__file__).resolve().parent;BASE=P.parent/'contextual-role-unknown-fix-v109';OLD=P.parent/'contextual-role-recovery-v107'
sp=importlib.util.spec_from_file_location('fixed_v109',BASE/'run.py');B=importlib.util.module_from_spec(sp);sp.loader.exec_module(B)
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def support(f,model):return sum(model['counts'][y][f] for y in model['roles'])
def active(ff,model):return ff[:4]+[f for f in ff[4:] if support(f,model)>=2]
def prediction(rows,key,model,backoff):
 out=[]
 for r in rows:
  gold=key[r['id']]
  if gold not in model['roles']:continue
  ff=B.features(r);chosen=active(ff,model) if backoff else ff;score=B.score(chosen,model,True);credit=.5 if score['prediction'] is None else float(score['prediction']==gold)
  out.append({'id':r['id'],'block':r['page'],'gold':gold,**score,'correct_credit':credit,'strict_correct':float(score['prediction']==gold),'log_loss':-math.log(score['probabilities'][gold]),'brier':sum((score['probabilities'][y]-float(y==gold))**2 for y in model['roles']),'baseline_known_features':sum(f in model['vocab'] for f in ff),'removed_singletons':[{'feature':f,'support':support(f,model)} for f in ff[4:] if support(f,model)==1] if backoff else [],'active_features':chosen})
 return out
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for n,h in f['baseline'].items():assert sha(BASE/n)==h,n
 for n,h in f['prior'].items():assert sha(OLD/n)==h,n

def fixtures():
 verify();rows=[];key={}
 for i,(y,c) in enumerate([('A',['x','y','u','v']),('A',['x','y','u','v']),('B',['q','r','s','t']),('B',['q','r','s','t']),('A',['j','k','m','n'])]):
  rows.append({'id':str(i),'page':str(i),'context':c});key[str(i)]=y
 model=B.fit(rows,key,['A','B']);rare=B.features(rows[-1]);chosen=active(rare,model);assert chosen==rare[:4];assert all(support(f,model)==1 for f in rare[4:]);assert active(B.features(rows[0]),model)==B.features(rows[0]);assert len(set(chosen))==4
 ff=B.features({'context':['x','y','unseen','else']});literal=ff[:4]+[f for f in ff[4:] if f in model['vocab']];assert B.score(ff,model,True)['scores']==B.score(literal,model,True)['scores']
 a=B.score(rare,model,True);b=B.score(chosen,model,True)
 for y in model['roles']:
  removed=sum(math.log((model['counts'][y][f]+1)/(model['totals'][y]+len(model['vocab'])+1)) for f in rare[4:]);assert abs(a['scores'][y]-b['scores'][y]-removed)<1e-12
 unknown=B.features({'context':['never1','never2','never3','never4']});zero=B.score(active(unknown,model),model,True);assert zero['prediction'] is None and all(v==0 for v in zero['scores'].values())
 checks={'unknown_pair_fallback_is_noop':True,'singleton_pair_suppressed':True,'repeated_pair_retained':True,'four_components_retained_once':True,'score_change_exactly_removed_singleton_terms':True,'only_training_counts_define_support':True,'zero_evidence_remains_neutral':True};dump('FIXTURES.json',{'status':'PASS','checks':checks});print(json.dumps(checks))

def run():
 verify();assert load(P/'FIXTURES.json')['status']=='PASS';assert not (P/'RESULTS.json').exists();rows=load(OLD/'BLIND-INPUT.json');key={i:v['upos'] for i,v in load(OLD/'ANSWER-KEY.json').items()};cfg=load(OLD/'PROTOCOL.json')['historical'];baseline=load(BASE/'RESULTS.json');saved={}
 for p in load(BASE/'PREDICTIONS.json'):saved[p['new']['id']]=p['new']
 result=[];preds=[];draws={};plans=[];metrics=['balanced_correct_credit','strict_balanced_recall','balanced_log_loss','balanced_brier']
 for si,oldrec in enumerate(baseline['panels']):
  st=oldrec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];model=B.fit(tr,key,roles);a=prediction(te,key,model,False);b=prediction(te,key,model,True)
  for aa,bb in zip(a,b):
   prior=saved[aa['id']];assert aa['prediction']==prior['prediction'] and aa['gold']==prior['gold']
   for y in model['roles']:assert aa['scores'][y]==prior['scores'][y] and aa['probabilities'][y]==prior['probabilities'][y]
   assert (aa['known_features']==0)==(bb['known_features']==0)
   ff=aa['active_features'];literal=ff[:4]+[f for f in ff[4:] if f in model['vocab']];assert B.score(literal,model,True)['scores']==aa['scores']
  ma,mb=B.metric(a,roles),B.metric(b,roles);boot,ds=B.bootstrap(a,b,roles,1103000+si);draws[st]=ds;trans=collections.Counter()
  for aa,bb in zip(a,b):
   state=lambda r:'abstain' if r['abstained'] else 'correct' if r['strict_correct'] else 'wrong';t=state(aa)+'_to_'+state(bb);trans[t]+=1;preds.append({'stratum':st,'baseline':aa,'backoff':bb,'transition':t})
  ea=[r for r in a if r['baseline_known_features']>0];eb=[r for r in b if r['baseline_known_features']>0]
  pairfreq={f:support(f,model) for f in model['vocab'] if f.startswith(('L:','R:'))};plans.append({'stratum':st,'training_singleton_pairs':sum(v==1 for v in pairfreq.values()),'training_repeated_pairs':sum(v>=2 for v in pairfreq.values()),'pooled_pair_frequencies':dict(sorted(pairfreq.items())),'counts_unchanged':True,'model_vocab':len(model['vocab']),'model_totals':model['totals']})
  rec={'stratum':st,'prior_status':oldrec['prior_status'],'primary_supported':oldrec['primary_supported'],'baseline':ma,'backoff':mb,'delta':B.delta(ma,mb),'coverage_delta':mb['coverage']-ma['coverage'],'fixed_baseline_evidence_subset':{'baseline':B.metric(ea,roles),'backoff':B.metric(eb,roles)},'cases_with_singleton_pair':sum(bool(r['removed_singletons']) for r in b),'singleton_pair_events_removed':sum(len(r['removed_singletons']) for r in b),'transitions':dict(trans),'bootstrap':boot};result.append(rec);print(st,'base',ma['balanced_correct_credit'],'backoff',mb['balanced_correct_credit'],'coverage',ma['coverage'],mb['coverage'],flush=True)
 dump('PREDICTIONS.json',preds);dump('PAIR-ACTIVATION.json',plans);dump('BOOTSTRAP-DRAWS.json',draws)
 with (P/'CONTROL-TRIALS.jsonl').open('x',encoding='utf8') as out:
  for si,rec in enumerate(result):
   st=rec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];control=[]
   for kind,seedbase in [('context_shuffle',1101000),('training_label_shuffle',1102000)]:
    vals=[];diffs=[]
    for j in range(199):
     seed=seedbase+si*10000+j*2
     if kind=='context_shuffle':ctr=B.shuffle_context(tr,seed);cte=B.shuffle_context(te,seed+1);ckey=key
     else:ctr=tr;cte=te;ckey=B.shuffle_labels([r for r in tr if key[r['id']] in roles],key,seed)
     model=B.fit(ctr,ckey,roles);a=B.metric(prediction(cte,key,model,False),roles);b=B.metric(prediction(cte,key,model,True),roles);delta=B.delta(a,b);vals.append(b['balanced_correct_credit']);diffs.append(delta['balanced_correct_credit']);out.write(json.dumps({'stratum':st,'kind':kind,'trial':j,'seed':seed,'baseline':a,'backoff':b,'delta':delta,'coverage_delta':b['coverage']-a['coverage']})+'\n');out.flush()
    p=(1+sum(v>=rec['backoff']['balanced_correct_credit']-1e-12 for v in vals))/200;dp=(1+sum(v>=rec['delta']['balanced_correct_credit']-1e-12 for v in diffs))/200;control.append({'kind':kind,'n':199,'mean_backoff_recovery':sum(vals)/199,'mean_paired_delta':sum(diffs)/199,'p_recovery_descriptive':p,'p_recovery_bonferroni8_descriptive':min(1,8*p),'p_delta_descriptive':dp,'p_delta_bonferroni8_descriptive':min(1,8*dp),'backoff_values':vals,'paired_deltas':diffs})
   rec['controls']=control;print('controls complete',st,flush=True)
 supported=[r for r in result if r['primary_supported']];overall={'panels':[r['stratum'] for r in supported],'n_panels':len(supported),'baseline_equal_panel_mean':{k:sum(r['baseline'][k] for r in supported)/len(supported) for k in metrics+['coverage']},'backoff_equal_panel_mean':{k:sum(r['backoff'][k] for r in supported)/len(supported) for k in metrics+['coverage']},'equal_panel_mean_delta':{k:sum(r['delta'][k] for r in supported)/len(supported) for k in metrics},'bootstrap_intervals95':{}}
 for k in metrics:
  vals=[]
  for j in range(2000):
   dd=[draws[r['stratum']][j] for r in supported]
   if all(v is not None for v in dd):vals.append(sum(v[k] for v in dd)/len(dd))
  overall['bootstrap_intervals95'][k]=[B.quantile(vals,q) for q in [.025,.975]]
 dump('RESULTS.json',{'scope':'One frozen singleton-pair activation backoff with unchanged v109 scorer and count models. Exposed development only.','panels':result,'supported_overall':overall,'literal_unknown_fallback':'Exhaustively verified identical to baseline for every actual test occurrence; components already present.'});verify()
if __name__=='__main__':
 import sys
 if sys.argv[1]=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'baseline':load(BASE/'SHA256SUMS.json'),'prior':load(OLD/'SHA256SUMS.json')});print('Backoff rule and comparisons frozen before scoring.')
 elif sys.argv[1]=='fixtures':fixtures()
 else:run()
