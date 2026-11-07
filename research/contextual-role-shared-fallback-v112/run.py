from pathlib import Path
import json,hashlib,collections,importlib.util,time,math
P=Path(__file__).resolve().parent;BASE=P.parent/'contextual-role-unknown-fix-v109';SHARED=P.parent/'contextual-role-position-sharing-v111';OLD=P.parent/'contextual-role-recovery-v107'
sp=importlib.util.spec_from_file_location('frozen_shared',SHARED/'run.py');S=importlib.util.module_from_spec(sp);sp.loader.exec_module(S);B=S.B
ARMS=['baseline','additive','fallback','local_only'];COMPS=['baseline','additive','local_only']
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fallback_features(r,model):
 ff=B.features(r);out=[];ledger=[]
 for i,c in enumerate(r['context']):
  pos=ff[i];word=None if c.startswith('#') else 'W:'+c;known=pos in model['vocab'];share=word in model['vocab'] if word else False;selected=pos if known or not share else word;out.append(selected);ledger.append({'slot':i,'offset':[-2,-1,1,2][i],'surface':c,'positional_feature':pos,'positional_supported':known,'shared_feature':word,'shared_supported':share,'selected_feature':selected,'uses_shared':selected!=pos})
 return out+ff[4:],ledger
def predict(rows,key,bm,sm,arm):
 m=bm if arm=='baseline' else sm;out=[]
 for r in rows:
  y=key[r['id']]
  if y not in m['roles']:continue
  ledger=[]
  if arm=='additive':ff=S.encode(r,'shared')
  elif arm=='fallback':ff,ledger=fallback_features(r,sm)
  else:ff=B.features(r)
  a=B.score(ff,m,True);out.append({'id':r['id'],'block':r['page'],'gold':y,**a,'correct_credit':.5 if a['abstained'] else float(a['prediction']==y),'strict_correct':float(a['prediction']==y),'log_loss':-math.log(a['probabilities'][y]),'brier':sum((a['probabilities'][z]-float(z==y))**2 for z in m['roles']),'baseline_known_features':sum(f in bm['vocab'] for f in B.features(r)),'additive_known_features':sum(f in sm['vocab'] for f in S.encode(r,'shared')),'encoded_features':ff,'fallback_slots':ledger,'n_shared_fallback_slots':sum(v['uses_shared'] for v in ledger)})
 return out
def subset(a,b,roles,fn):
 aa=[x for x,y in zip(a,b) if fn(x,y)];bb=[y for x,y in zip(a,b) if fn(x,y)];return {'n':len(aa),'baseline':B.metric(aa,roles),'fallback':B.metric(bb,roles),'fallback_decision_counts':{'correct':sum(x['strict_correct'] for x in bb),'wrong':sum(not x['abstained'] and not x['strict_correct'] for x in bb),'abstained':sum(x['abstained'] for x in bb)}}
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for k,path in [('baseline',BASE),('shared',SHARED),('prior',OLD)]:
  for n,h in f[k].items():assert sha(path/n)==h,n

def fixtures():
 verify();rows=[{'id':'a','page':'1','context':['cedar','ash','elm','oak']},{'id':'b','page':'2','context':['pine','fir','lime','beech']}];key={'a':'A','b':'B'};roles=['A','B'];m=S.fit(rows,key,roles,'shared');bm=B.fit(rows,key,roles)
 ff,ledger=fallback_features(rows[0],m);assert ff==B.features(rows[0]) and not any(v['uses_shared'] for v in ledger);assert m['counts']['B']['0:cedar']==0 and ledger[0]['positional_supported']
 r={'context':['never','cedar','else','missing']};ff,ll=fallback_features(r,m);assert ff[1]=='W:cedar' and ll[1]['uses_shared'];assert len(ff)==6 and '1:cedar' not in ff and ff.count('W:cedar')==1
 edge={'context':['#edge','cedar','#barrier','ash']};ef,el=fallback_features(edge,m);assert ef[0]=='0:#edge' and ef[2]=='2:#barrier' and not el[0]['uses_shared'] and not el[2]['uses_shared']
 rep,rl=fallback_features({'context':['cedar','cedar','cedar','cedar']},m);assert rep.count('W:cedar')==3 and rep[0]=='0:cedar'
 assert ff[4:]==B.features(r)[4:];zero=B.score(fallback_features({'context':['z1','z2','z3','z4']},m)[0],m,True);assert zero['abstained'] and all(v==0 for v in zero['scores'].values())
 for row in rows+[r,edge]:assert (B.score(fallback_features(row,m)[0],m,True)['known_features']>0)==(B.score(S.encode(row,'shared'),m,True)['known_features']>0)
 checks={'global_position_support_wins_even_if_one_class_absent':True,'shared_word_used_only_for_unseen_position':True,'one_identity_contribution_per_slot':True,'boundaries_never_shared':True,'repeated_words_keep_separate_occurrences':True,'original_pairs_retained':True,'no_evidence_remains_neutral':True,'recognized_support_matches_additive':True};dump('FIXTURES.json',{'status':'PASS','checks':checks});print(json.dumps(checks))

def run():
 verify();assert load(P/'FIXTURES.json')['status']=='PASS';assert not (P/'RESULTS.json').exists();rows=load(OLD/'BLIND-INPUT.json');key={i:v['upos'] for i,v in load(OLD/'ANSWER-KEY.json').items()};cfg=load(OLD/'PROTOCOL.json')['historical'];ref=load(BASE/'RESULTS.json');savedbase={r['new']['id']:r['new'] for r in load(BASE/'PREDICTIONS.json')};savedshared={r['shared']['id']:r['shared'] for r in load(SHARED/'PREDICTIONS.json')};results=[];allpred=[];models=[];draws={c:{} for c in COMPS}
 for si,oldrec in enumerate(ref['panels']):
  st=oldrec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];bm=B.fit(tr,key,roles);sm=S.fit(tr,key,roles,'shared');pred={a:predict(te,key,bm,sm,a) for a in ARMS};me={a:B.metric(pred[a],roles) for a in ARMS};trans={c:collections.Counter() for c in COMPS}
  for k in range(len(pred['fallback'])):
   a={arm:pred[arm][k] for arm in ARMS};fallback=a['fallback']
   for arm,saved in [('baseline',savedbase),('additive',savedshared)]:
    old=saved[a[arm]['id']];assert a[arm]['prediction']==old['prediction']
    for y in roles:assert a[arm]['scores'][y]==old['scores'][y] and a[arm]['probabilities'][y]==old['probabilities'][y]
   assert (fallback['known_features']>0)==(a['additive']['known_features']>0)
   state=lambda r:'abstain' if r['abstained'] else 'correct' if r['strict_correct'] else 'wrong'
   t={c:state(a[c])+'_to_'+state(fallback) for c in COMPS}
   for c in COMPS:trans[c][t[c]]+=1
   allpred.append({'stratum':st,**a,'transitions':t})
  boots={}
  for ci,c in enumerate(COMPS):boot,ds=B.bootstrap(pred[c],pred['fallback'],roles,1123000+ci*1000+si);boots[c]=boot;draws[c][st]=ds
  for arm,m in [('baseline',bm),('shared',sm)]:models.append({'stratum':st,'model':arm,'counts':{y:dict(m['counts'][y]) for y in roles},'totals':m['totals'],'n':dict(m['n']),'vocabulary':sorted(m['vocab'])})
  a=pred['baseline'];b=pred['fallback'];rec={'stratum':st,'prior_status':oldrec['prior_status'],'primary_supported':oldrec['primary_supported'],'metrics':me,'deltas':{c:B.delta(me[c],me['fallback']) for c in COMPS},'coverage_deltas':{c:me['fallback']['coverage']-me[c]['coverage'] for c in COMPS},'transitions':{c:dict(v) for c,v in trans.items()},'bootstrap':boots,'original_evidence_subset':subset(a,b,roles,lambda x,y:x['known_features']>0),'original_zero_evidence':subset(a,b,roles,lambda x,y:x['known_features']==0),'new_feature_support':subset(a,b,roles,lambda x,y:x['known_features']==0 and y['known_features']>0),'new_decisions':subset(a,b,roles,lambda x,y:x['abstained'] and not y['abstained']),'instances_using_fallback':sum(r['n_shared_fallback_slots']>0 for r in b),'fallback_slot_events':sum(r['n_shared_fallback_slots'] for r in b)};results.append(rec);print(st,'base',me['baseline']['balanced_correct_credit'],'add',me['additive']['balanced_correct_credit'],'fall',me['fallback']['balanced_correct_credit'],'local',me['local_only']['balanced_correct_credit'],'coverage',me['fallback']['coverage'],'loss',me['fallback']['balanced_log_loss'],flush=True)
 dump('PREDICTIONS.json',allpred);dump('MODELS.json',models);dump('BOOTSTRAP-DRAWS.json',draws)
 with (P/'CONTROL-TRIALS.jsonl').open('x',encoding='utf8') as out:
  for si,rec in enumerate(results):
   st=rec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];controls=[]
   for kind,seedbase in [('context_shuffle',1121000),('training_label_shuffle',1122000)]:
    values=[];delta_values={c:[] for c in COMPS}
    for j in range(199):
     seed=seedbase+si*10000+j*2
     if kind=='context_shuffle':ctr=B.shuffle_context(tr,seed);cte=B.shuffle_context(te,seed+1);ckey=key
     else:ctr=tr;cte=te;ckey=B.shuffle_labels([r for r in tr if key[r['id']] in roles],key,seed)
     bm=B.fit(ctr,ckey,roles);sm=S.fit(ctr,ckey,roles,'shared');me={a:B.metric(predict(cte,key,bm,sm,a),roles) for a in ARMS};dd={c:B.delta(me[c],me['fallback']) for c in COMPS};values.append(me['fallback']['balanced_correct_credit'])
     for c in COMPS:delta_values[c].append(dd[c]['balanced_correct_credit'])
     out.write(json.dumps({'stratum':st,'kind':kind,'trial':j,'seed':seed,'metrics':me,'deltas':dd})+'\n');out.flush()
    p=(1+sum(v>=rec['metrics']['fallback']['balanced_correct_credit']-1e-12 for v in values))/200;ps={c:min(1,8*(1+sum(v>=rec['deltas'][c]['balanced_correct_credit']-1e-12 for v in delta_values[c]))/200) for c in COMPS};controls.append({'kind':kind,'n':199,'mean_fallback_recovery':sum(values)/199,'mean_recovery_delta':{c:sum(v)/199 for c,v in delta_values.items()},'p_recovery_bonferroni8_descriptive':min(1,8*p),'p_delta_bonferroni8_descriptive':ps,'fallback_values':values,'delta_values':delta_values})
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
 base=overall['equal_panel_means']['baseline'];add=overall['equal_panel_means']['additive'];fall=overall['equal_panel_means']['fallback'];den=add['balanced_correct_credit']-base['balanced_correct_credit'];overall['additive_recovery_gain_retained_fraction']=(fall['balanced_correct_credit']-base['balanced_correct_credit'])/den if den else None;overall['literal_observed_goals']={'recovery_gain_over_baseline':fall['balanced_correct_credit']>base['balanced_correct_credit'],'full_additive_recovery_retained':fall['balanced_correct_credit']>=add['balanced_correct_credit'],'full_additive_decision_coverage_retained':fall['coverage']>=add['coverage'],'log_loss_no_worse_than_baseline':fall['balanced_log_loss']<=base['balanced_log_loss'],'brier_no_worse_than_baseline':fall['balanced_brier']<=base['balanced_brier']}
 dump('RESULTS.json',{'scope':'Exposed supervised development only; activation-only fallback uses frozen shared-model parameterization and unmodified repaired scorer.','panels':results,'supported_overall':overall});verify()
if __name__=='__main__':
 import sys
 if sys.argv[1]=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'baseline':load(BASE/'SHA256SUMS.json'),'shared':load(SHARED/'SHA256SUMS.json'),'prior':load(OLD/'SHA256SUMS.json')});print('Fallback activation, model reuse and comparisons frozen before scores.')
 elif sys.argv[1]=='fixtures':fixtures()
 else:run()
