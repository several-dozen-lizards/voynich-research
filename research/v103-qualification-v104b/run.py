from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from itertools import product
import ast,functools,gc,hashlib,json,math,traceback,zipfile
import numpy as np
from core import dp,paths,edgecounts,spans,oracle_layout,draw,invariant,build,scores,minima,target,convolve,seed,belongs,state,direct,rational
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,d):(R/n).write_text(json.dumps(d,indent=2),encoding='utf-8')
def hashes():
 f=load(R/'FREEZE.json')
 for n,h in f['local_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 for n,h in f['historical_sha256'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
def rowscores(layouts,p):
 out=[];K=len(p['labels']);idx=np.triu_indices(K,1)
 for layout in layouts:
  c=np.zeros((K,K),dtype=np.int32)
  for s in layout:
   for a,b,z in zip(s,s[1:],s[2:]):
    if p['neutral'] and state(b)!=2:continue
    A=np.array([belongs(a,l) for l in p['labels']],dtype=np.int32);Z=np.array([belongs(z,l) for l in p['labels']],dtype=np.int32);c+=np.outer(A,Z)
  out.append((c-c.T)[idx])
 return np.array(out)
def exact_law(hist):
 t=sum(hist.values());return {d:Fraction(n,t) for d,n in hist.items()}
def cdf_error(vals,hist):
 n=len(vals);err=0.;cum=0;total=sum(hist.values())
 for d,v in sorted(hist.items())[:-1]:cum+=v;err=max(err,abs(float(np.mean(vals<=d))-float(Fraction(cum,total))))
 return err
def weighted_target_law(orbit,regime,p,repetitions):
 _,j,_=target(p);single=scores(orbit,p)[:,j];h=Counter();weights=[]
 for layout,d in zip(orbit,single):
  s=layout[0]
  if regime=='position_weights':w=4**(int(s[1].startswith('sh'))+int(s[3].startswith('qok')))
  elif regime=='repeated_template':w=16**sum((a,b,c)==('shedy','ol','qokedy') for a,b,c in zip(s,s[1:],s[2:]))
  else:w=4**sum((a,b) in [('shedy','ol'),('ol','qokedy')] for a,b in zip(s,s[1:]))
  h[int(d)]+=w;weights.append(w)
 out={0:1}
 for _ in range(repetitions):out=convolve(out,h)
 return out,weights
def main():
 hashes();assert not (R/'QUALIFICATION.json').exists(),'Do not rerun a frozen completed attempt'
 plan=load(R/'CONTROL-PLAN.json');panels=load(R/'FAMILY.json');fixtures=load(R/'FIXTURES.json');records=[];support=0
 # Exhaustive path oracle and independent replay of the frozen v98 path function.
 ns={'np':np,'functools':functools};node=next(n for n in ast.parse((P/'transition-maxT-qual-v98/engine.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='paths');exec(compile(ast.Module(body=[node],type_ignores=[]),'v98-paths-only','exec'),ns)
 fibers=defaultdict(set)
 for n in range(1,8):
  for seq in product(range(3),repeat=n):fibers[(seq[0],seq[-1],edgecounts(seq))].add(seq)
 for (start,end,ec),ss in fibers.items():assert set(paths(start,end,ec))==ss=={tuple(map(int,x)) for x in ns['paths'](start,end,ec)}
 for initial in [(0,1),(0,1,2),(0,1,2,3),(0,0,1)]:
  tally=Counter()
  for swaps in product(*(range(j+1) for j in range(len(initial)-1,0,-1))):
   a=list(initial)
   for j,k in zip(range(len(a)-1,0,-1),swaps):a[j],a[k]=a[k],a[j]
   tally[tuple(a)]+=1
  assert len(set(tally.values()))==1
 records.append(dict(check='exact_path_and_Fisher_Yates_oracles',pass_gate=True,fibers=len(fibers)))
 # All null tables and support-count audit plan are fixed before random controls.
 for panel in panels:
  for fixture in fixtures:
   rr=fixture['rows'];orbit=None if fixture['name']=='positive32' else oracle_layout(rr)
   if orbit is not None:support+=len(orbit)-1
   for neutral in (False,True):
    p=build(rr,panel['labels'],neutral);assert len(p['pairs'])==panel['class_pairs'];key=(panel['panel_index'],fixture['name'],neutral)
    support+=sum(len(p['groups'][int(g)]['hist'])-1 for g in p['column_group'])
    print('TABLES',key,'columns',len(p['pairs']),'complete_signature_groups',len(p['groups']),flush=True)
    del p;gc.collect()
 threshold=math.sqrt(math.log(2*max(1,support)/.001)/(2*4096))
 save('SUPPORT-PLAN.json',dict(full_family_support_points=support,alpha=.001,draws=4096,absolute_CDF_error_limit=threshold,frozen_before_any_random_draw=True))
 for panel in panels:
  pi=panel['panel_index']
  for fixture in fixtures:
   name=fixture['name'];rr=fixture['rows'];sample=draw(rr,4096,np.random.default_rng(seed(f'v104/controls/null/{pi}/{name}')))
   for a in sample:invariant(a,rr)
   literal_error=0.
   orbit=None if name=='positive32' else oracle_layout(rr)
   if orbit is not None:
    index={a:i for i,a in enumerate(orbit)};ids=np.array([index[a] for a in sample]);literal_error=max((abs(float(np.mean(ids<=i))-(i+1)/len(orbit)) for i in range(len(orbit)-1)),default=0.)
   for neutral in (False,True):
    p=build(rr,panel['labels'],neutral);gs=scores(sample,p);errors=[cdf_error(gs[:,j],g['hist']) for j,g in enumerate(p['groups'])];rec=dict(panel_index=pi,section=panel['section'],hand=panel['hand'],reading=panel['reading'],fixture=name,view='non_target_middle' if neutral else 'any_middle',columns=len(p['pairs']),signature_groups=len(p['groups']),max_marginal_CDF_error=max(errors,default=0.),literal_orbit_CDF_error=literal_error,CDF_limit=threshold,invariants=True)
    rec['cdf_pass']=max(rec['max_marginal_CDF_error'],literal_error)<=threshold
    if orbit is not None:
     og=scores(orbit,p);expanded=og[:,p['column_group']];assert np.array_equal(expanded,rowscores(orbit,p))
     for j,g in enumerate(p['groups']):assert exact_law(Counter(map(int,og[:,j])))==exact_law(g['hist'])
     ms=minima(og,p);exact_adj=[Fraction(sum(x<=m for x in ms),len(ms)) for m in ms]
     for alpha in (Fraction(1,560),Fraction(1,20),Fraction(1,10),Fraction(1,2),Fraction(1)):
      assert Fraction(sum(x<=alpha for x in exact_adj),len(exact_adj))<=alpha
     # Weight within each fixed span's fiber under concrete first-order nuisance laws.
     nuisance=[]
     for regime in plan['nuisance_regimes']:
      ww=[]
      for layout in orbit:
       prob=Fraction(1)
       for si,s in enumerate(layout):
        mi=1 if regime=='independent_words' else (si//2)%5 if regime=='page_specific' else si%5 if regime=='line_span_specific' else (2 if panel['hand']=='2' else 3)
        M=plan['matrices'][mi]
        for a,b in zip(s,s[1:]):prob*=Fraction(M[state(a)][state(b)],sum(M[state(a)]))
       ww.append(prob)
      assert len(set(ww))==1
      mass=sum(w for w,pv in zip(ww,exact_adj) if pv<=Fraction(1,560))/sum(ww)
      assert mass<=Fraction(1,560);nuisance.append(dict(regime=regime,conditional_family_null_size=rational(mass)))
     rec.update(exact_marginals_and_all_column_scores=True,exact_rank=True,nuisance=nuisance,oracle_layouts=len(orbit),estimability='nonconstant' if any(len(g['hist'])>1 for g in p['groups']) else 'not_estimable_constant')
    else:
     # Frozen positive is AUTHORED, not an original manuscript arrangement.
     ps=scores((spans(rr),),p);_,tj,sign=target(p);pv=dp.calibrated(p['groups'][tj]['tails'][int(ps[0,tj])],minima(gs,p));h=p['groups'][tj]['hist'];mean=Fraction(sum(d*n for d,n in h.items()),sum(h.values()));forward=sign*(Fraction(int(ps[0,tj]))-mean)>0
     rec.update(positive_adjusted_p=rational(pv),positive_forward=forward,positive_pass=forward and pv<=Fraction(1,20))
     # Store every family column, not just representatives or target.
     with zipfile.ZipFile(R/f'panel-{pi:02d}-{int(neutral)}-calibration.npz','w',compression=zipfile.ZIP_DEFLATED) as z:
      with z.open('scores.npy','w',force_zip64=True) as fh:
       np.lib.format.write_array_header_1_0(fh,dict(descr=np.lib.format.dtype_to_descr(gs.dtype),fortran_order=False,shape=(4096,len(p['pairs']))))
       for lo in range(0,4096,32):fh.write(gs[lo:lo+32,p['column_group']].tobytes(order='C'))
      with z.open('column_group.npy','w') as fh:np.lib.format.write_array(fh,p['column_group'],allow_pickle=False)
     save(f'panel-{pi:02d}-{int(neutral)}-minima.json',[rational(x) for x in minima(gs,p)])
     base=next(x for x in fixtures if x['name']=='variable');small=oracle_layout(base['rows']);bank=minima(gs,p);diagnostics=[]
     for regime in plan['diagnostics']:
      ph,pweights=weighted_target_law(small,regime,p,32);rng=np.random.default_rng(seed(f'v104/controls/{regime}/{pi}/positive32'));chosen=rng.choice(len(small),size=(200,32),p=np.array(pweights,dtype=float)/sum(pweights));layouts=tuple(tuple(small[k][0] for k in row) for row in chosen);dg=scores(layouts,p);dm=minima(dg,p);target_ps=[dp.calibrated(p['groups'][tj]['tails'][int(d)],bank) for d in dg[:,tj]];family_ps=[dp.calibrated(m,bank) for m in dm]
      exactmass=Fraction(sum(n for d,n in ph.items() if dp.calibrated(p['groups'][tj]['tails'][d],bank)<=Fraction(1,20)),sum(ph.values()))
      entry=dict(regime=regime,trials=200,target_flags=sum(x<=Fraction(1,20) for x in target_ps),family_flags=sum(x<=Fraction(1,20) for x in family_ps),exact_target_rejection_mass=rational(exactmass),meaning='Outside-uniform-null residual dependence; no false-positive or grammar interpretation',target_p=[rational(x) for x in target_ps],family_p=[rational(x) for x in family_ps]);diagnostics.append(entry)
     rec['scope_diagnostics']=diagnostics
    rec['pass_gate']=rec['cdf_pass'] and rec.get('positive_pass',True);records.append(rec);save('PROGRESS.json',dict(records=records,scoring='CLOSED'))
    print('CONTROL',pi,name,neutral,'PASS' if rec['pass_gate'] else 'FAIL',flush=True)
    del p,gs;gc.collect()
 # Exact plus-one rank bound including ties; no empirical zero-tail substitution.
 for vals in ([0,1,2],[0,0,1]):
  for alpha in (Fraction(1,3),Fraction(2,3),Fraction(1)):
   tuples=list(product(vals,repeat=3));assert Fraction(sum(Fraction(1+sum(c<=t[0] for c in t[1:]),3)<=alpha for t in tuples),len(tuples))<=alpha
 assert dp.calibrated(Fraction(0),[Fraction(1)]*4096)==Fraction(28,4097)
 records.append(dict(check='Monte_Carlo_plus_one_exact_rank_ties',pass_gate=True))
 hashes();old=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert old['status']=='FAIL' and old['robustness_banks_not_run']==[2,3]
 save('QUALIFICATION.json',dict(status='PASS_STAGE1_CONTROLS_ONLY' if all(x['pass_gate'] for x in records) else 'FAIL_STAGE1',records=records,failed_required=[{k:v for k,v in x.items() if k!='scope_diagnostics'} for x in records if not x['pass_gate']],actual_layout_power='NOT RUN',manuscript_scoring='CLOSED',old_v98='FAIL unchanged; banks2/3 unrun',limitations='Finite authored controls; calibration conditional-null scope only. No actual-layout 80/90 power qualification or semantic inference.'))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  save('EXECUTION-FAILURE.json',dict(status='FAIL_STAGE1_EXECUTION',type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),scoring='CLOSED',repair='Requires a separately named frozen attempt; original failure retained.'))
  raise
