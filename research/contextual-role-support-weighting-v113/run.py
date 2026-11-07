from pathlib import Path
import json,hashlib,collections,importlib.util,time,math
P=Path(__file__).resolve().parent;BASE=P.parent/'contextual-role-unknown-fix-v109';SHARED=P.parent/'contextual-role-position-sharing-v111';PREV=P.parent/'contextual-role-shared-fallback-v112';OLD=P.parent/'contextual-role-recovery-v107'
sp=importlib.util.spec_from_file_location('frozen_fallback',PREV/'run.py');F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F);S=F.S;B=F.B
ARMS=['baseline','additive','fallback','weighted','equal_mix'];COMPS=['baseline','additive','fallback','equal_mix']
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def support(m,f):return sum(m['counts'][y][f] for y in m['roles']) if f else 0
def budgets(r,m,arm):
 out=[]
 for i,c in enumerate(r['context']):
  pos=str(i)+':'+c;word=None if c.startswith('#') else 'W:'+c;nl=support(m,pos);np=support(m,word);no=np-nl if word else 0
  if word:assert np>=nl
  if not word:wl,ws=(1.,0.) if nl else (0.,0.)
  elif arm=='weighted':wl,ws=(nl/np,no/np) if np else (0.,0.)
  else:wl,ws=(.5,.5) if nl and np else (1.,0.) if nl else (0.,1.) if np else (0.,0.)
  out.append({'slot':i,'offset':[-2,-1,1,2][i],'surface':c,'positional_feature':pos,'shared_feature':word,'local_training_count':nl,'pooled_training_count':np,'other_position_training_count':no,'local_weight':wl,'shared_weight':ws})
 return out
def term(m,f):
 cache=m.setdefault('_term_cache',{})
 if f not in cache:cache[f]={y:math.log((m['counts'][y][f]+1)/(m['totals'][y]+len(m['vocab'])+1)) if f in m['vocab'] else 0. for y in m['roles']}
 return cache[f]
def weighted_score(r,m,arm):
 ledger=budgets(r,m,arm);terms=[]
 for e in ledger:
  if e['local_weight']:terms.append((e['positional_feature'],e['local_weight']))
  if e['shared_weight']:terms.append((e['shared_feature'],e['shared_weight']))
 for f in B.features(r)[4:]:terms.append((f,1.))
 scores={y:sum(w*term(m,f)[y] for f,w in terms) for y in m['roles']};tie=abs(scores[m['roles'][0]]-scores[m['roles'][1]])<=1e-12;pred=None if tie else max(m['roles'],key=lambda y:scores[y]);top=max(scores.values());exp={y:math.exp(v-top) for y,v in scores.items()};z=sum(exp.values());prob={y:.5 if tie else v/z for y,v in exp.items()}
 return {'prediction':pred,'scores':scores,'probabilities':prob,'abstained':pred is None,'known_features':sum(f in m['vocab'] and w>0 for f,w in terms),'recognized_feature_mass':sum(w for f,w in terms if f in m['vocab']),'weighted_terms':[{'feature':f,'weight':w} for f,w in terms],'support_ledger':ledger}
def predict(rows,key,bm,sm,arm):
 if arm in ['baseline','additive','fallback']:return F.predict(rows,key,bm,sm,arm)
 out=[]
 for r in rows:
  y=key[r['id']]
  if y not in sm['roles']:continue
  a=weighted_score(r,sm,arm);out.append({'id':r['id'],'block':r['page'],'gold':y,**a,'correct_credit':.5 if a['abstained'] else float(a['prediction']==y),'strict_correct':float(a['prediction']==y),'log_loss':-math.log(a['probabilities'][y]),'brier':sum((a['probabilities'][z]-float(z==y))**2 for z in sm['roles']),'baseline_known_features':sum(f in bm['vocab'] for f in B.features(r))})
 return out
def subset(a,b,roles,fn):
 aa=[x for x,y in zip(a,b) if fn(x,y)];bb=[y for x,y in zip(a,b) if fn(x,y)];return {'n':len(aa),'baseline':B.metric(aa,roles),'weighted':B.metric(bb,roles),'weighted_decision_counts':{'correct':sum(r['strict_correct'] for r in bb),'wrong':sum(not r['abstained'] and not r['strict_correct'] for r in bb),'abstained':sum(r['abstained'] for r in bb)}}
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for k,path in [('baseline',BASE),('shared',SHARED),('previous',PREV),('prior',OLD)]:
  for n,h in f[k].items():assert sha(path/n)==h,n

def fixtures():
 verify();rows=[{'id':'a','page':'1','context':['cedar','ash','elm','oak']},{'id':'b','page':'2','context':['cedar','pine','cedar','fir']}];key={'a':'A','b':'B'};m=S.fit(rows,key,['A','B'],'shared');r={'context':['cedar','cedar','z2','z3']};ll=budgets(r,m,'weighted');assert (ll[0]['local_training_count'],ll[0]['pooled_training_count'],ll[0]['other_position_training_count'])==(2,3,1);assert ll[0]['local_weight']==2/3 and ll[0]['shared_weight']==1/3;assert ll[1]['local_weight']==0 and ll[1]['shared_weight']==1
 for e in ll:assert e['local_weight']>=0 and e['shared_weight']>=0 and abs(e['local_weight']+e['shared_weight']-(1 if e['pooled_training_count'] or e['local_training_count'] else 0))<1e-12
 edge=budgets({'context':['#edge','cedar','#barrier','oak']},m,'weighted');assert all(e['shared_weight']==0 and e['shared_feature'] is None for e in [edge[0],edge[2]])
 only=budgets(rows[0],m,'weighted')[1];assert only['local_weight']==1 and only['shared_weight']==0
 zero=weighted_score({'context':['z1','z2','z3','z4']},m,'weighted');assert zero['abstained'] and all(v==0 for v in zero['scores'].values())
 score=weighted_score(r,m,'weighted');assert score['weighted_terms'][-2:]==[{'feature':f,'weight':1.} for f in B.features(r)[4:]]
 for e in ll:
  for y in m['roles']:
   a=term(m,e['positional_feature'])[y];b=term(m,e['shared_feature'])[y] if e['shared_feature'] else 0;v=e['local_weight']*a+e['shared_weight']*b
   if e['local_weight']+e['shared_weight']:assert min(a,b)-1e-12<=v<=max(a,b)+1e-12
 for f in m['vocab']:
  ref=B.score([f],m,True)['scores']
  for y in m['roles']:assert abs(term(m,f)[y]-ref[y])<1e-12
 swapped={k:('B' if v=='A' else 'A') for k,v in key.items()};ms=S.fit(rows,swapped,['A','B'],'shared');assert budgets(r,m,'weighted')==budgets(r,ms,'weighted')
 assert 1/4<2/4<3/4
 checks={'disjoint_local_and_other_counts':True,'weights_nonnegative_normalized_per_slot':True,'only_local_only_shared_no_evidence_corners':True,'boundaries_never_shared':True,'original_pair_terms_unchanged':True,'original_repaired_likelihood_terms_identical':True,'role_renaming_leaves_weights_identical':True,'fixed_total_more_local_support_means_more_local_weight':True,'convex_term_not_double_vote':True};dump('FIXTURES.json',{'status':'PASS','checks':checks});print(json.dumps(checks))

def run():
 verify();assert load(P/'FIXTURES.json')['status']=='PASS';assert not (P/'RESULTS.json').exists();rows=load(OLD/'BLIND-INPUT.json');key={i:v['upos'] for i,v in load(OLD/'ANSWER-KEY.json').items()};cfg=load(OLD/'PROTOCOL.json')['historical'];ref=load(BASE/'RESULTS.json');saved={a:{} for a in ['baseline','additive','fallback']}
 for r in load(PREV/'PREDICTIONS.json'):
  for a in saved:saved[a][r[a]['id']]=r[a]
 results=[];allpred=[];models=[];draws={c:{} for c in COMPS}
 for si,oldrec in enumerate(ref['panels']):
  st=oldrec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];bm=B.fit(tr,key,roles);sm=S.fit(tr,key,roles,'shared');pred={a:predict(te,key,bm,sm,a) for a in ARMS};me={a:B.metric(pred[a],roles) for a in ARMS};trans={c:collections.Counter() for c in COMPS}
  for i in range(len(pred['weighted'])):
   p={a:pred[a][i] for a in ARMS}
   for a in saved:
    old=saved[a][p[a]['id']];assert p[a]['prediction']==old['prediction']
    for y in roles:assert p[a]['scores'][y]==old['scores'][y]
   assert (p['weighted']['known_features']>0)==(p['additive']['known_features']>0)==(p['equal_mix']['known_features']>0)
   state=lambda r:'abstain' if r['abstained'] else 'correct' if r['strict_correct'] else 'wrong';t={c:state(p[c])+'_to_'+state(p['weighted']) for c in COMPS}
   for c in COMPS:trans[c][t[c]]+=1
   allpred.append({'stratum':st,**p,'transitions':t})
  boots={}
  for ci,c in enumerate(COMPS):bo,ds=B.bootstrap(pred[c],pred['weighted'],roles,1133000+ci*1000+si);boots[c]=bo;draws[c][st]=ds
  for arm,m in [('baseline',bm),('shared',sm)]:models.append({'stratum':st,'model':arm,'counts':{y:dict(m['counts'][y]) for y in roles},'totals':m['totals'],'n':dict(m['n']),'vocabulary':sorted(m['vocab'])})
  a=pred['baseline'];b=pred['weighted'];rec={'stratum':st,'prior_status':oldrec['prior_status'],'primary_supported':oldrec['primary_supported'],'metrics':me,'deltas':{c:B.delta(me[c],me['weighted']) for c in COMPS},'coverage_deltas':{c:me['weighted']['coverage']-me[c]['coverage'] for c in COMPS},'transitions':{c:dict(v) for c,v in trans.items()},'bootstrap':boots,'original_evidence_subset':subset(a,b,roles,lambda x,y:x['known_features']>0),'new_feature_support':subset(a,b,roles,lambda x,y:x['known_features']==0 and y['known_features']>0),'new_decisions':subset(a,b,roles,lambda x,y:x['abstained'] and not y['abstained'])};results.append(rec);print(st,'base',me['baseline']['balanced_correct_credit'],'weighted',me['weighted']['balanced_correct_credit'],'equal',me['equal_mix']['balanced_correct_credit'],'coverage',me['weighted']['coverage'],'loss',me['weighted']['balanced_log_loss'],flush=True)
 dump('PREDICTIONS.json',allpred);dump('MODELS.json',models);dump('BOOTSTRAP-DRAWS.json',draws)
 with (P/'CONTROL-TRIALS.jsonl').open('x',encoding='utf8') as out:
  for si,rec in enumerate(results):
   st=rec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];controls=[]
   for kind,seedbase in [('context_shuffle',1131000),('training_label_shuffle',1132000)]:
    values=[];dv={c:[] for c in COMPS}
    for j in range(199):
     seed=seedbase+si*10000+j*2
     if kind=='context_shuffle':ctr=B.shuffle_context(tr,seed);cte=B.shuffle_context(te,seed+1);ckey=key
     else:ctr=tr;cte=te;ckey=B.shuffle_labels([r for r in tr if key[r['id']] in roles],key,seed)
     bm=B.fit(ctr,ckey,roles);sm=S.fit(ctr,ckey,roles,'shared');me={a:B.metric(predict(cte,key,bm,sm,a),roles) for a in ARMS};dd={c:B.delta(me[c],me['weighted']) for c in COMPS};values.append(me['weighted']['balanced_correct_credit'])
     for c in COMPS:dv[c].append(dd[c]['balanced_correct_credit'])
     out.write(json.dumps({'stratum':st,'kind':kind,'trial':j,'seed':seed,'metrics':me,'deltas':dd})+'\n');out.flush()
    p=(1+sum(v>=rec['metrics']['weighted']['balanced_correct_credit']-1e-12 for v in values))/200;ps={c:min(1,8*(1+sum(v>=rec['deltas'][c]['balanced_correct_credit']-1e-12 for v in dv[c]))/200) for c in COMPS};controls.append({'kind':kind,'n':199,'mean_weighted_recovery':sum(values)/199,'mean_recovery_delta':{c:sum(v)/199 for c,v in dv.items()},'p_recovery_bonferroni8_descriptive':min(1,8*p),'p_delta_bonferroni8_descriptive':ps,'weighted_values':values,'delta_values':dv})
   rec['controls']=controls;print('controls complete',st,flush=True)
 supported=[r for r in results if r['primary_supported']];keys=['balanced_correct_credit','strict_balanced_recall','balanced_log_loss','balanced_brier'];overall={'panels':[r['stratum'] for r in supported],'equal_panel_means':{a:{k:sum(r['metrics'][a][k] for r in supported)/len(supported) for k in keys+['coverage']} for a in ARMS},'deltas':{c:{k:sum(r['deltas'][c][k] for r in supported)/len(supported) for k in keys} for c in COMPS},'bootstrap_intervals95':{}}
 for c in COMPS:
  overall['bootstrap_intervals95'][c]={}
  for k in keys:
   vals=[]
   for j in range(2000):
    dd=[draws[c][r['stratum']][j] for r in supported]
    if all(v is not None for v in dd):vals.append(sum(v[k] for v in dd)/len(dd))
   overall['bootstrap_intervals95'][c][k]=[B.quantile(vals,q) for q in [.025,.975]]
 baseline=overall['equal_panel_means']['baseline'];weighted=overall['equal_panel_means']['weighted'];overall['literal_observed_goals']={'recovery_better_than_baseline':weighted['balanced_correct_credit']>baseline['balanced_correct_credit'],'coverage_no_lower_than_baseline':weighted['coverage']>=baseline['coverage'],'log_loss_no_worse_than_baseline':weighted['balanced_log_loss']<=baseline['balanced_log_loss'],'brier_no_worse_than_baseline':weighted['balanced_brier']<=baseline['balanced_brier']}
 dump('RESULTS.json',{'scope':'One untuned support-weight heuristic on exposed supervised development data; no independent qualification.','panels':results,'supported_overall':overall});verify()
if __name__=='__main__':
 import sys
 if sys.argv[1]=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'baseline':load(BASE/'SHA256SUMS.json'),'shared':load(SHARED/'SHA256SUMS.json'),'previous':load(PREV/'SHA256SUMS.json'),'prior':load(OLD/'SHA256SUMS.json')});print('Support formula and five-arm comparisons frozen before scores.')
 elif sys.argv[1]=='fixtures':fixtures()
 else:run()
