import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from preflight import *
from scipy.optimize import minimize_scalar,brentq
from scipy.stats import chi2
from concurrent.futures import ProcessPoolExecutor
RESERVED={'f72v2','f72v1','f73r','f73v'}
SCENES=['null_low','null_high','additive','junction_only','availability_only','positive']
def selected_lines():
 src=json.loads((R/'PROTOCOL.json').read_text())['sources']
 assert all(sha(p)==h for p,h in src.items())
 source=next(Path(p) for p in src if 'text16e6' in p);meta=next(Path(p) for p in src if 'Davis-hands' in p)
 metadata={r['Folio']:r for r in csv.DictReader(meta.open(encoding='utf-8-sig'))};lines=[]
 for raw in source.read_text(encoding='latin1').splitlines():
  m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',raw)
  if not m:continue
  pg,place,num,co,text=m.groups()
  if co not in ('H','F') or not place.startswith('P') or pg not in metadata:continue
  if pg in RESERVED:continue
  info=metadata[pg];c=context(info,pg)
  if (info['Scribe'],info['Section'])==('4','Astronomy/Astrology'):c='C8-4'
  if c:lines.append(dict(panel=c,context=c,reading=co,folio=pg,line=f'{pg}.{place}.{num}',hand=info['Scribe'],section=info['Section'],tokens=e.tokens(text)))
 return lines
def collect(outcomes=False):
 lines=selected_lines();events=[];ledger=[]
 for l in lines:
  ev,_,led=e.extract([l],outcomes)
  for v in ev:
   f=l['tokens'][v['position']+1];av=not f.startswith(('sh','ch','cth','ckh','cph','cfh'))
   v.update(reading=l['reading'],context=l['context'],available=av,strict_available=f.startswith(('q','o','d','y','a')))
   events.append(v)
  for v in led:
   f=v['follower'];v.update(reading=l['reading'],context=l['context'],available=bool(f and not f.startswith(('sh','ch','cth','ckh','cph','cfh'))),follower_class=next((p for p in ('cth','ckh','cph','cfh','qok','ch','sh','qo','q','o','d','y','a') if f and f.startswith(p)),'other' if f else 'unknown_or_absent'))
   ledger.append(v)
 return events,ledger
def cells(events):
 p1=set(json.loads((P/'sh-qok-single-target-attempt-c/PANELS.json').read_text())['declared_folios']['P1']);out={}
 for co in ['H','F']:
  for name in ['A-P1','A-bath','A-starred','B-Q1']:
   out[name+'-'+co]=[v for v in events if v['reading']==co and (v['folio'] in p1 if name=='A-P1' else v['context']==('C1' if name=='A-bath' else 'C4') if name!='B-Q1' else v['context'] in ('C6','C7')) and (v['available'] if name.startswith('A-') else True)]
 return out
def check_seals():
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(line)['hashes'].items():assert sha(R/n)==h,('changed frozen file',n)
def freeze():
 assert not (R/'AMENDMENT-v3.1.json').exists()
 save('AMENDMENT-v3.1.json',dict(authority='User clarification in this chat, 24 October 2026; frozen before any amended-primary support computation',original_sections='ORIGINAL-SPEC.txt sections 3.2 through 3.5 retained byte-for-byte',partA='Primary: unchanged attempt C folio x ending exact engine on available-only events. Drop blocked before strata. Gate V>=80, >=8 pages, share<=.25. Qualify all six original A.4 scenarios at actual support; positive .20/.35. Holm3 per reading. Surviving share=available MH RD / aggregate MH RD with paired folio bootstrap. Existing W engine remains unchanged unsupported sensitivity outside Holm.',partB='B-Q1 unchanged attempt C engine on C6+C7; B-Q2 remains original spec.',metadata_correction='Davis scribe4 astronomy Section is literally Astronomy/Astrology, not Astronomy. C8 keeps only P units and excludes reserved folios explicitly before tokenization. f73r/v have no H/F P units, so C5 unchanged. No new context added.',qualification=dict(trials_per_cell_scenario=200,alpha_A=.05/3,alpha_BQ1=.05/2,alpha_BQ2=.05/2,seeds='A/Q1 3100000+cellindex*100000+scenarioindex*1000+trial; BQ2 5100000+readingindex*100000+scenarioindex*1000+trial',null_gates='Wilson95 upper<=.05',positive_gate='Wilson95 lower>=.80; failed power retained as UNDERPOWERED',availability_only='Actual prefix and blocked geometry fixed; equal .20 qok probability among available followers and structural zero among blocked. Thus any aggregate availability confounding is retained. Primary A tests only available events.',junction_only='Attempt C unchanged final-y .10/.60 rates; blocked followers remain zero in A synthetic full layouts.'),heterogeneity=dict(variance='For each context, folio-cluster delta-method MH variance m/(m-1)*sum_p(Np-RD*Dp)^2/(sum Dp)^2, m all covered event pages. Report percentile folio-bootstrap CIs separately. Zero variance/undefined effects => NOT ESTIMABLE, no smoothing.',Q='Cochran Q inverse cluster-variance weights about overall fixed-effect mean. Recompute RD and cluster variance for every shuffle. Whole folio labels shuffled within scribe, fixed context counts. 10000 seeded shuffles with plus-one p. Undefined shuffle invalidates permutation test rather than dropping it.',REML='Restricted normal likelihood, tau2>=0; Q-profile interval solves Q(tau2)=chi-square quantiles df=k-1, truncate at zero. I2=max(0,(Q-df)/Q). Variance in squared probability units; effect/CI points in report.',sensitivities='Scribe2 C1-C3; scribe2 without C1 C2-C3. Selection of C1/C4 retained and labeled.',controls='200 independently generated outcomes per homogeneous null .20, homogeneous positive .20+.08*sh, heterogeneous positive .20+.12*sh in C1 only. Same real geometry and folio permutations. Null and homogeneous-positive Wilson upper<=.05; heterogeneous power descriptive only. No gates retuned.',bootstrap='4999 folio resamples; 2.5/97.5 percentile; pooled H/F prohibited. Ratio uses identical draws for available and aggregate. Zero-denominator replicates retained as invalid count; warn if aggregate CI spans zero.'),interpretation='Retrospective structural association only. A Currier-A pass supports cross-variety association in these samples, not proof of a scribe-independent habit. Selection, sparse contexts and within-scribe test limits remain explicit.'))
 seal('v3.1_frozen',['AMENDMENT-v3.1.json','analysis.py'])
def prepare():
 check_seals();events,_=collect(False);cc=cells(events);support={k:e.support(v) for k,v in cc.items()}
 for co in ['H','F']:
  for c in ['C'+str(i) for i in range(1,8)]+['C8-4','C8-5']:
   vv=[v for v in events if v['reading']==co and v['context']==c];support[c+'-'+co]=e.support(vv)
 save('SUPPORT-v3.1.json',support);save('MASKED-v3.1.json',events)
 seal('v3.1_support_frozen',['SUPPORT-v3.1.json','MASKED-v3.1.json'])
 print(json.dumps({k:{n:v[n] for n in ['V','supported_pages','max_page_share','gate']} for k,v in support.items() if k.startswith(('A-','B-Q1'))},indent=2),flush=True)
def worker(job):
 ci,key,si,scene,t=job
 vv=cells(json.loads((R/'MASKED-v3.1.json').read_text()))[key];seed=3100000+ci*100000+si*1000+t
 y=e.synthetic(vv,'null_low' if scene=='availability_only' else scene,seed)
 if key.startswith('B-') and scene=='availability_only':
  y=y*np.array([v['available'] for v in vv])
 rr=e.exact(vv,y);alpha=.05/(3 if key.startswith('A-') else 2)
 return dict(cell=key,scenario=scene,trial=t,seed=seed,p=rr['p'],degenerate=rr['degenerate'],flag=rr['p'] is not None and rr['p']<=alpha,outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest())
def variance_terms(vv):
 pages=sorted({v['folio'] for v in vv});terms=e.page_effects(vv)
 return pages,np.array([terms.get(pg,[0.,0.]) for pg in pages])
def cluster(a):
 m=len(a);den=a[:,1].sum() if m else 0
 if not den:return None,None
 rd=a[:,0].sum()/den
 var=m/(m-1)*np.square(a[:,0]-rd*a[:,1]).sum()/den**2 if m>1 else 0
 return float(rd),float(var)
def q_summary(effects,variances):
 if len(effects)<2 or any(v is None or v<=0 for v in variances) or any(x is None for x in effects):return None
 y=np.array(effects);v=np.array(variances);w=1/v;mean=(w*y).sum()/w.sum();q=float((w*(y-mean)**2).sum())
 return q
def hetero_data(vv,contexts):
 by=collections.defaultdict(list)
 for v in vv:
  if v['context'] in contexts:by[v['folio']].append(v)
 pages=sorted(by);terms=[];labels=[];hands=[]
 for pg in pages:
  a=e.page_effects(by[pg]).get(pg,[0.,0.]);terms.append(a);labels.append(contexts.index(by[pg][0]['context']));hands.append(by[pg][0]['hand'])
 return np.array(terms),np.array(labels),np.array(hands),pages
def permutation_labels(labels,hands,seed):
 rng=np.random.default_rng(seed);perms=np.tile(labels,(10000,1))
 for h in sorted(set(hands)):
  ix=np.where(hands==h)[0]
  for row in perms:row[ix]=rng.permutation(labels[ix])
 return np.vstack([labels,perms])
def perm_test(terms,labmat,k):
 ys=[];vs=[]
 for j in range(k):
  mask=(labmat==j).astype(float);m=mask.sum(axis=1);den=mask@terms[:,1];num=mask@terms[:,0]
  with np.errstate(divide='ignore',invalid='ignore'):
   rd=num/den;res=(mask@np.square(terms[:,0]))-2*rd*(mask@(terms[:,0]*terms[:,1]))+rd**2*(mask@np.square(terms[:,1]));var=m/(m-1)*np.maximum(0,res)/den**2
  ys.append(rd);vs.append(var)
 y=np.array(ys).T;v=np.array(vs).T;good=np.isfinite(y).all(axis=1)&np.isfinite(v).all(axis=1)&(v>1e-20).all(axis=1)
 if not good.all():return dict(status='NOT ESTIMABLE',p=None,undefined_shuffles=int((~good[1:]).sum()),observed_defined=bool(good[0]))
 w=1/v;mean=(w*y).sum(axis=1)/w.sum(axis=1);q=(w*(y-mean[:,None])**2).sum(axis=1);p=(1+int((q[1:]>=q[0]-1e-12).sum()))/len(q)
 return dict(status='SCORED',p=float(p),Q=float(q[0]),shuffles=len(q)-1,exceedances=int((q[1:]>=q[0]-1e-12).sum()),observed_effects=y[0].tolist(),observed_variances=v[0].tolist(),permutation_Q_sha256=hashlib.sha256(q[1:].tobytes()).hexdigest())
def hetero_worker(job):
 co,si,scene,t=job;events=json.loads((R/'MASKED-v3.1.json').read_text());vv=[v for v in events if v['reading']==co and v['context'] in ['C1','C2','C3','C4','C5']]
 seed=5100000+['H','F'].index(co)*100000+si*1000+t;rng=np.random.default_rng(seed)
 for v in vv:v['y']=int(rng.random()<(.2+(.08*v['x'] if scene=='homogeneous_positive' else .12*v['x']*(v['context']=='C1') if scene=='heterogeneous_positive' else 0)))
 a,labels,hands,pages=hetero_data(vv,['C1','C2','C3','C4','C5']);labmat=permutation_labels(labels,hands,6100000+['H','F'].index(co))
 rr=perm_test(a,labmat,5)
 return dict(reading=co,scenario=scene,trial=t,seed=seed,flag=rr['p'] is not None and rr['p']<=.025,**rr)
def qualify():
 check_seals();supp=json.loads((R/'SUPPORT-v3.1.json').read_text());keys=list(cells(json.loads((R/'MASKED-v3.1.json').read_text())))
 jobs=[(ci,k,si,s,t) for ci,k in enumerate(keys) if supp[k]['gate'] for si,s in enumerate(SCENES) for t in range(200)]
 records=[]
 with ProcessPoolExecutor(max_workers=3) as pool,(R/'SYNTHETIC-TRIALS-v3.1.jsonl').open('w') as f:
  for rr in pool.map(worker,jobs,chunksize=10):
   records.append(rr);f.write(json.dumps(rr)+'\n')
   if len(records)%200==0:print('A/Q1 controls',len(records),'/',len(jobs),flush=True)
 summary={}
 for key in keys:
  controls=[]
  for s in SCENES:
   rr=[r for r in records if r['cell']==key and r['scenario']==s]
   if not rr:continue
   n=len(rr);flags=sum(r['flag'] for r in rr);ci=e.wilson(flags,n);gate=ci[0]>=.8 if s=='positive' else ci[1]<=.05
   controls.append(dict(scenario=s,n=n,flags=flags,wilson95=ci,gate=gate,degenerate=sum(r['degenerate'] for r in rr)))
  null=bool(controls) and all(c['gate'] for c in controls if c['scenario']!='positive');power=bool(controls) and all(c['gate'] for c in controls if c['scenario']=='positive')
  summary[key]=dict(status='NOT ESTIMABLE' if not supp[key]['gate'] else 'FAIL NULL QUALIFICATION' if not null else 'UNDERPOWERED' if not power else 'QUALIFIED',null_pass=null,power_pass=power,controls=controls)
 save('QUALIFICATION-A-Q1.json',summary);seal('A_Q1_qualification_frozen',['QUALIFICATION-A-Q1.json','SYNTHETIC-TRIALS-v3.1.jsonl'])
 print(json.dumps({k:v['status'] for k,v in summary.items()}),flush=True)
def qualify_hetero():
 check_seals();records=[];jobs=[(co,si,s,t) for co in ['H','F'] for si,s in enumerate(['homogeneous_null','homogeneous_positive','heterogeneous_positive']) for t in range(200)]
 with ProcessPoolExecutor(max_workers=3) as pool,(R/'HETEROGENEITY-CONTROLS.jsonl').open('w') as f:
  for rr in pool.map(hetero_worker,jobs,chunksize=10):
   records.append(rr);f.write(json.dumps(rr)+'\n')
   if len(records)%100==0:print('Heterogeneity controls',len(records),'/',len(jobs),flush=True)
 summary={}
 for co in ['H','F']:
  controls=[]
  for scene in ['homogeneous_null','homogeneous_positive','heterogeneous_positive']:
   rr=[r for r in records if r['reading']==co and r['scenario']==scene];k=sum(r['flag'] for r in rr);ci=e.wilson(k,len(rr));ne=sum(r['status']!='SCORED' for r in rr)
   controls.append(dict(scenario=scene,n=len(rr),flags=k,wilson95=ci,not_estimable=ne,gate=(ci[1]<=.05 and ne==0) if scene!='heterogeneous_positive' else None))
  summary[co]=dict(null_pass=all(r['gate'] for r in controls if r['gate'] is not None),controls=controls)
 save('QUALIFICATION-BQ2.json',summary);seal('BQ2_qualification_frozen',['QUALIFICATION-BQ2.json','HETEROGENEITY-CONTROLS.jsonl'])
 print(json.dumps(summary,indent=2),flush=True)
def estimate(vv,seed):
 result=e.effect(vv,seed);pages,a=variance_terms(vv);rd,var=cluster(a)
 return result|dict(cluster_variance=var,events=len(vv),sh=sum(v['x'] for v in vv),qok=sum(v['y'] for v in vv),discordant_events=sum(s['sh']+s['ch'] for s in e.support(vv)['strata'] if s['sh'] and s['ch']),support=e.support(vv))
def share(aggregate,available,seed):
 pages=sorted({v['folio'] for v in aggregate});aa=e.page_effects(aggregate);bb=e.page_effects(available)
 a=np.array([aa.get(pg,[0,0]) for pg in pages]);b=np.array([bb.get(pg,[0,0]) for pg in pages]);rng=np.random.default_rng(seed);ix=rng.integers(len(pages),size=(4999,len(pages)));sa=a[ix].sum(axis=1);sb=b[ix].sum(axis=1)
 good=(sa[:,1]>0)&(sb[:,1]>0)&(np.abs(sa[:,0])>1e-14);rat=(sb[good,0]/sb[good,1])/(sa[good,0]/sa[good,1]);total=(b[:,0].sum()/b[:,1].sum())/(a[:,0].sum()/a[:,1].sum()) if a[:,0].sum() and b[:,1].sum() else None
 return dict(share=float(total) if total is not None else None,CI95=np.quantile(rat,[.025,.975]).tolist() if len(rat) else None,valid_replicates=int(good.sum()),invalid_replicates=int((~good).sum()),note='Ratio is descriptive; can exceed 1 or change sign. Paired folio draws.')
def reml(rr):
 if rr['p'] is None:return dict(status='NOT ESTIMABLE')
 y=np.array(rr['observed_effects']);v=np.array(rr['observed_variances']);k=len(y)
 def q(t):
  w=1/(v+t);mu=(w*y).sum()/w.sum();return float((w*(y-mu)**2).sum())
 def objective(t):return float(np.log(v+t).sum()+np.log((1/(v+t)).sum())+q(t))
 opt=minimize_scalar(objective,bounds=(0,1),method='bounded',options={'xatol':1e-13});tau=float(opt.x) if opt.fun<objective(0) else 0.
 def root(target):
  if q(0)<=target:return 0.
  hi=1.
  while q(hi)>target:hi*=2
  return float(brentq(lambda t:q(t)-target,0,hi))
 lo=root(chi2.ppf(.975,k-1));hi=root(chi2.ppf(.025,k-1));Q=q(0)
 return dict(status='ESTIMATED',tau2=tau,Q_profile_CI95=[lo,hi],I2=max(0.,(Q-(k-1))/Q) if Q else 0.,Q=Q,df=k-1,units='tau2 in squared probability; multiply by 10000 for squared percentage points',boundary_CI_note='Q-profile roots truncated at zero; broad intervals mean unresolved heterogeneity')
def outcomes():
 check_seals();assert not (R/'PART-A.json').exists();events,ledger=collect(True);cc=cells(events);supp=json.loads((R/'SUPPORT-v3.1.json').read_text());qual=json.loads((R/'QUALIFICATION-A-Q1.json').read_text());qh=json.loads((R/'QUALIFICATION-BQ2.json').read_text());A={};B={};ests={}
 with (R/'EVENTS.csv').open('w',newline='',encoding='utf-8') as f:
  fields=sorted(set().union(*(v.keys() for v in ledger)));writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(ledger)
 for i,(key,vv) in enumerate(cc.items()):
  est=estimate(vv,7100000+i);q=qual[key];raw=e.exact(vv) if supp[key]['gate'] and q['null_pass'] else dict(p=None,degenerate=None)
  status='NOT ESTIMABLE' if not supp[key]['gate'] or raw['degenerate'] else 'BLOCKED: NULL QUALIFICATION' if not q['null_pass'] else 'UNDERPOWERED' if not q['power_pass'] else 'SCORED'
  row=dict(status=status,estimate=est,exact=raw,qualification=q['status'])
  if key.startswith('A-'):
   allvv=[v for v in events if v['reading']==key[-1] and (v['folio'] in set(supp['C2-'+key[-1]]['page_support'])|set(supp['C3-'+key[-1]]['page_support']) if key.startswith('A-P1') else v['context']==('C1' if key.startswith('A-bath') else 'C4'))]
   strict=[v for v in allvv if v['strict_available']];row.update(aggregate=estimate(allvv,7200000+i),strict_sensitivity=estimate(strict,7300000+i),surviving_share=share(allvv,vv,7400000+i),A1b_identity=True)
   A[key]=row
  else:B[key]=row
 for co in ['H','F']:
  for ci,c in enumerate(['C'+str(j) for j in range(1,8)]+['C8-4','C8-5']):
   vv=[v for v in events if v['reading']==co and v['context']==c];s=e.support(vv);discord=sum(t['sh']+t['ch'] for t in s['strata'] if t['sh'] and t['ch'])
   ests[c+'-'+co]=dict(context=c,reading=co,role='discovery' if c in ['C1','C4'] else 'exposed/uncertified',aggregate=estimate(vv,7500000+ci+100*['H','F'].index(co)),available=estimate([v for v in vv if v['available']],7600000+ci+100*['H','F'].index(co))) if not c.startswith('C8') or discord>=30 else dict(context=c,reading=co,status='COUNTS ONLY',support=s,discordant_events=discord)
  vv=[v for v in events if v['reading']==co];contexts=['C1','C2','C3','C4','C5'];tests={}
  for si,cs in enumerate([contexts,['C1','C2','C3'],['C2','C3']]):
   a,lab,hands,pg=hetero_data(vv,cs);mat=permutation_labels(lab,hands,6100000+['H','F'].index(co)+si*100)
   rr=perm_test(a,mat,len(cs));tests['primary' if si==0 else 'scribe2_with_C1' if si==1 else 'scribe2_without_C1']=rr|dict(contexts=cs,random_effects=reml(rr),selection_note='C1 and C4 selected for large prior effects; winner selection can inflate heterogeneity.')
  main=tests['primary'];B['B-Q2-'+co]=dict(status='SCORED' if qh[co]['null_pass'] and main['p'] is not None else 'BLOCKED: NULL QUALIFICATION' if not qh[co]['null_pass'] else 'NOT ESTIMABLE',p=main['p'] if qh[co]['null_pass'] else None,descriptive_tests=tests)
  aks=[k for k in A if k.endswith(co)];adjusted=e.holm([A[k]['exact']['p'] for k in aks])
  for k,p in zip(aks,adjusted):
   A[k]['holm_p']=p
   if A[k]['status']=='SCORED':A[k]['status']='PASS' if p is not None and p<=.05 and A[k]['estimate']['effect_points']>0 else 'NO PASS'
  qkeys=['B-Q1-'+co,'B-Q2-'+co];ps=[B[qkeys[0]]['exact']['p'],B[qkeys[1]]['p']];adjusted=e.holm(ps)
  for k,p in zip(qkeys,adjusted):
   B[k]['holm_p']=p
   if B[k]['status']=='SCORED':B[k]['status']='PASS' if p is not None and p<=.05 else 'NO PASS'
 save('PART-A.json',A);save('PART-B-ESTIMATES.json',ests);save('PART-B-TESTS.json',B)
 save('QUALIFICATION.json',dict(A_and_BQ1=qual,BQ2=qh,retrospective=True))
 seal('outcomes_scored',['PART-A.json','PART-B-ESTIMATES.json','PART-B-TESTS.json','EVENTS.csv','QUALIFICATION.json'])
 print(json.dumps({k:dict(status=v['status'],holm_p=v['holm_p']) for k,v in (A|B).items()},indent=2))
if __name__=='__main__':
 {'freeze':freeze,'prepare':prepare,'qualify':qualify,'qualify_hetero':qualify_hetero,'outcomes':outcomes}[sys.argv[1]]()
