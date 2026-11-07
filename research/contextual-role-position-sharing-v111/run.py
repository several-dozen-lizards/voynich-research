from pathlib import Path
import json,hashlib,collections,importlib.util,time,math
P=Path(__file__).resolve().parent;BASE=P.parent/'contextual-role-unknown-fix-v109';OLD=P.parent/'contextual-role-recovery-v107'
sp=importlib.util.spec_from_file_location('fixed_v109',BASE/'run.py');B=importlib.util.module_from_spec(sp);sp.loader.exec_module(B)
ARMS=['baseline','shared','duplicate']
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(r,arm):
 ff=B.features(r)
 if arm=='baseline':return ff
 return ff+[(f'W{i}:'+c if c.startswith('#') or arm=='duplicate' else 'W:'+c) for i,c in enumerate(r['context'])]
def fit(rows,key,roles,arm):
 if arm=='baseline':return B.fit(rows,key,roles)
 counts={r:collections.Counter() for r in roles};n=collections.Counter();vocab=set()
 for row in rows:
  y=key[row['id']]
  if y not in roles:continue
  ff=encode(row,arm);counts[y].update(ff);vocab.update(ff);n[y]+=1
 return {'counts':counts,'totals':{y:sum(c.values()) for y,c in counts.items()},'n':n,'vocab':vocab,'roles':sorted(roles)}
def predict(rows,key,model,arm,basemodel):
 out=[]
 for r in rows:
  y=key[r['id']]
  if y not in model['roles']:continue
  ff=encode(r,arm);s=B.score(ff,model,True);oldff=B.features(r);baseknown=sum(f in basemodel['vocab'] for f in oldff);real_shared=[('W:'+c) for c in r['context'] if not c.startswith('#')];newpos=sum(not c.startswith('#') and oldff[i] not in basemodel['vocab'] and 'W:'+c in model['vocab'] for i,c in enumerate(r['context'])) if arm=='shared' else 0
  out.append({'id':r['id'],'block':r['page'],'gold':y,**s,'correct_credit':.5 if s['abstained'] else float(s['prediction']==y),'strict_correct':float(s['prediction']==y),'log_loss':-math.log(s['probabilities'][y]),'brier':sum((s['probabilities'][z]-float(z==y))**2 for z in model['roles']),'baseline_known_features':baseknown,'shared_known_real_events':sum(f in model['vocab'] for f in real_shared) if arm=='shared' else 0,'word_positions_gaining_shared_match':newpos,'encoded_features':ff})
 return out
def subset_report(a,b,roles,condition):
 aa=[x for x,y in zip(a,b) if condition(x,y)];bb=[y for x,y in zip(a,b) if condition(x,y)];return {'n':len(aa),'baseline':B.metric(aa,roles),'shared':B.metric(bb,roles),'shared_decision_counts':{'correct':sum(x['strict_correct'] for x in bb),'wrong':sum(not x['abstained'] and not x['strict_correct'] for x in bb),'abstained':sum(x['abstained'] for x in bb)}}
def verify():
 f=load(P/'FREEZE.json')
 for n,h in f['local'].items():assert sha(P/n)==h,n
 for group,path in [('baseline',BASE),('prior',OLD)]:
  for n,h in f[group].items():assert sha(path/n)==h,n

def fixtures():
 verify();a={'context':['cedar','ash','elm','oak']};b={'context':['ash','cedar','elm','oak']};sa=encode(a,'shared');sb=encode(b,'shared');assert sa[:6]==B.features(a) and sb[:6]==B.features(b);assert collections.Counter(sa[6:])==collections.Counter(sb[6:]) and sa[:4]!=sb[:4]
 rows=[{'id':'a','page':'1','context':['cedar','ash','elm','oak']},{'id':'b','page':'2','context':['pine','fir','lime','beech']}];key={'a':'A','b':'B'};roles=['A','B'];m=fit(rows,key,roles,'shared');du=fit(rows,key,roles,'duplicate');bm=fit(rows,key,roles,'baseline')
 q={'context':['never','cedar','nothere','missing']};ff=encode(q,'shared');assert '1:cedar' not in bm['vocab'] and 'W:cedar' in m['vocab'];assert sum(f in du['vocab'] for f in encode(q,'duplicate'))==0
 edge=encode({'context':['#edge','ash','elm','#barrier']},'shared');assert 'W0:#edge' in edge and 'W3:#barrier' in edge and 'W:#edge' not in edge and 'W:#barrier' not in edge
 repeated=encode({'context':['cedar','cedar','cedar','cedar']},'shared');assert repeated.count('W:cedar')==4 and len(repeated)==10
 zero=B.score(encode({'context':['z1','z2','z3','z4']},'shared'),m,True);assert zero['abstained'] and all(v==0 for v in zero['scores'].values())
 assert encode(a,'duplicate')[:6]==B.features(a) and len(encode(a,'duplicate'))==10
 checks={'word_identity_shared_across_offsets':True,'explicit_word_position_features_change_with_offsets':True,'all_original_six_features_retained':True,'cross_position_only_word_gains_match':True,'duplicate_control_cannot_gain_unknown_support':True,'boundary_markers_remain_position_specific':True,'repeated_words_preserve_event_multiplicity':True,'all_unseen_features_remain_neutral':True};dump('FIXTURES.json',{'status':'PASS','checks':checks});print(json.dumps(checks))

def run():
 verify();assert load(P/'FIXTURES.json')['status']=='PASS';assert not (P/'RESULTS.json').exists();rows=load(OLD/'BLIND-INPUT.json');key={i:v['upos'] for i,v in load(OLD/'ANSWER-KEY.json').items()};cfg=load(OLD/'PROTOCOL.json')['historical'];baseline=load(BASE/'RESULTS.json');saved={r['new']['id']:r['new'] for r in load(BASE/'PREDICTIONS.json')};results=[];allpred=[];allmodels=[];draws={'versus_baseline':{},'versus_duplicate':{}}
 for si,oldrec in enumerate(baseline['panels']):
  st=oldrec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];models={arm:fit(tr,key,roles,arm) for arm in ARMS};pred={arm:predict(te,key,models[arm],arm,models['baseline']) for arm in ARMS};metrics={arm:B.metric(pred[arm],roles) for arm in ARMS};a,b,c=(pred[k] for k in ARMS);trans=collections.Counter();duptr=collections.Counter()
  for aa,bb,cc in zip(a,b,c):
   orig=saved[aa['id']];assert aa['prediction']==orig['prediction'] and aa['gold']==orig['gold']
   for y in roles:assert aa['scores'][y]==orig['scores'][y] and aa['probabilities'][y]==orig['probabilities'][y]
   assert aa['encoded_features']==bb['encoded_features'][:6]==cc['encoded_features'][:6]
   if aa['known_features']==0:assert cc['known_features']==0 and cc['abstained']
   if aa['known_features']>0:assert bb['known_features']>0
   if aa['known_features']==0 and bb['known_features']>0:assert bb['shared_known_real_events']>0
   state=lambda r:'abstain' if r['abstained'] else 'correct' if r['strict_correct'] else 'wrong';t=state(aa)+'_to_'+state(bb);dt=state(cc)+'_to_'+state(bb);trans[t]+=1;duptr[dt]+=1;allpred.append({'stratum':st,'baseline':aa,'shared':bb,'duplicate':cc,'transition':t,'duplicate_to_shared_transition':dt})
  bm,bd=B.bootstrap(a,b,roles,1113000+si);cm,cd=B.bootstrap(c,b,roles,1114000+si);draws['versus_baseline'][st]=bd;draws['versus_duplicate'][st]=cd
  for arm,m in models.items():
   events=6 if arm=='baseline' else 10;assert all(m['totals'][y]==events*m['n'][y] for y in roles);allmodels.append({'stratum':st,'arm':arm,'counts':{y:dict(m['counts'][y]) for y in roles},'totals':m['totals'],'n':dict(m['n']),'vocabulary':sorted(m['vocab']),'feature_events_per_row':events})
  rec={'stratum':st,'prior_status':oldrec['prior_status'],'primary_supported':oldrec['primary_supported'],'metrics':metrics,'delta_vs_baseline':B.delta(metrics['baseline'],metrics['shared']),'delta_vs_duplicate':B.delta(metrics['duplicate'],metrics['shared']),'coverage_delta_vs_baseline':metrics['shared']['coverage']-metrics['baseline']['coverage'],'coverage_delta_vs_duplicate':metrics['shared']['coverage']-metrics['duplicate']['coverage'],'transitions':dict(trans),'duplicate_transitions':dict(duptr),'baseline_evidence_subset':subset_report(a,b,roles,lambda x,y:x['known_features']>0),'new_feature_support':subset_report(a,b,roles,lambda x,y:x['known_features']==0 and y['known_features']>0),'new_decisions':subset_report(a,b,roles,lambda x,y:x['abstained'] and not y['abstained']),'old_zero_evidence':subset_report(a,b,roles,lambda x,y:x['known_features']==0),'known_feature_counts':{arm:sum(r['known_features'] for r in pred[arm]) for arm in ARMS},'bootstrap_vs_baseline':bm,'bootstrap_vs_duplicate':cm};results.append(rec);print(st,'baseline',metrics['baseline']['balanced_correct_credit'],'shared',metrics['shared']['balanced_correct_credit'],'duplicate',metrics['duplicate']['balanced_correct_credit'],'coverage',metrics['baseline']['coverage'],metrics['shared']['coverage'],'new_support',rec['new_feature_support']['n'],flush=True)
 dump('PREDICTIONS.json',allpred);dump('MODELS.json',allmodels);dump('BOOTSTRAP-DRAWS.json',draws)
 with (P/'CONTROL-TRIALS.jsonl').open('x',encoding='utf8') as out:
  for si,rec in enumerate(results):
   st=rec['stratum'];roles=cfg['targets'][st.split('|')[1]];rs=[r for r in rows if r['stratum']==st];tr=[r for r in rs if r['split']=='train'];te=[r for r in rs if r['split']=='test'];control=[]
   for kind,seedbase in [('context_shuffle',1111000),('training_label_shuffle',1112000)]:
    vals=[];diffs=[];dupvals=[]
    for j in range(199):
     seed=seedbase+si*10000+j*2
     if kind=='context_shuffle':ctr=B.shuffle_context(tr,seed);cte=B.shuffle_context(te,seed+1);ckey=key
     else:ctr=tr;cte=te;ckey=B.shuffle_labels([r for r in tr if key[r['id']] in roles],key,seed)
     models={arm:fit(ctr,ckey,roles,arm) for arm in ARMS};me={arm:B.metric(predict(cte,key,models[arm],arm,models['baseline']),roles) for arm in ARMS};db=B.delta(me['baseline'],me['shared']);dd=B.delta(me['duplicate'],me['shared']);vals.append(me['shared']['balanced_correct_credit']);diffs.append(db['balanced_correct_credit']);dupvals.append(dd['balanced_correct_credit']);out.write(json.dumps({'stratum':st,'kind':kind,'trial':j,'seed':seed,'metrics':me,'delta_vs_baseline':db,'delta_vs_duplicate':dd})+'\n');out.flush()
    p=(1+sum(v>=rec['metrics']['shared']['balanced_correct_credit']-1e-12 for v in vals))/200;dp=(1+sum(v>=rec['delta_vs_baseline']['balanced_correct_credit']-1e-12 for v in diffs))/200;up=(1+sum(v>=rec['delta_vs_duplicate']['balanced_correct_credit']-1e-12 for v in dupvals))/200
    control.append({'kind':kind,'n':199,'mean_shared_recovery':sum(vals)/199,'mean_delta_vs_baseline':sum(diffs)/199,'mean_delta_vs_duplicate':sum(dupvals)/199,'p_recovery_bonferroni8_descriptive':min(1,8*p),'p_delta_baseline_bonferroni8_descriptive':min(1,8*dp),'p_delta_duplicate_bonferroni8_descriptive':min(1,8*up),'shared_values':vals,'baseline_deltas':diffs,'duplicate_deltas':dupvals})
   rec['controls']=control;print('controls complete',st,flush=True)
 supported=[r for r in results if r['primary_supported']];keys=['balanced_correct_credit','strict_balanced_recall','balanced_log_loss','balanced_brier'];overall={'panels':[r['stratum'] for r in supported],'equal_panel_means':{arm:{k:sum(r['metrics'][arm][k] for r in supported)/len(supported) for k in keys+['coverage']} for arm in ARMS},'delta_vs_baseline':{k:sum(r['delta_vs_baseline'][k] for r in supported)/len(supported) for k in keys},'delta_vs_duplicate':{k:sum(r['delta_vs_duplicate'][k] for r in supported)/len(supported) for k in keys},'bootstrap_intervals95':{}}
 for comp in ['versus_baseline','versus_duplicate']:
  overall['bootstrap_intervals95'][comp]={}
  for k in keys:
   vals=[]
   for j in range(2000):
    dd=[draws[comp][r['stratum']][j] for r in supported]
    if all(v is not None for v in dd):vals.append(sum(v[k] for v in dd)/len(dd))
   overall['bootstrap_intervals95'][comp][k]=[B.quantile(vals,q) for q in [.025,.975]]
 dump('RESULTS.json',{'scope':'Exposed supervised development experiment, shared identity plus explicit position; no independent confirmation or manuscript scoring.','panels':results,'supported_overall':overall});verify()
if __name__=='__main__':
 import sys
 if sys.argv[1]=='freeze':
  assert not (P/'FREEZE.json').exists();dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in ['run.py','PROTOCOL.json']},'baseline':load(BASE/'SHA256SUMS.json'),'prior':load(OLD/'SHA256SUMS.json')});print('Shared representation, duplication control and comparison frozen before scoring.')
 elif sys.argv[1]=='fixtures':fixtures()
 else:run()
