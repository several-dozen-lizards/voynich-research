import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib,math,collections
import numpy as np
from scipy.stats import binom,beta
R=Path(__file__).resolve().parent;OLD=R.parent/'sh-qok-context-map-v3'
sys.path.insert(0,str(OLD));import analysis as a
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def manifest():return {str(p.relative_to(OLD)):sha(p) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
def oracle(events,y):
 groups=collections.defaultdict(list)
 for i,v in enumerate(events):groups[v['folio'],v['family']].append(i)
 dist=np.array([1.]);offset=obs=0
 for ix in groups.values():
  ns=sum(events[i]['x'] for i in ix);nc=len(ix)-ns;t=sum(int(y[i]) for i in ix);lo=max(0,t-nc);hi=min(ns,t)
  den=math.comb(ns+nc,t)
  local=np.array([math.comb(ns,j)*math.comb(nc,t-j)/den for j in range(lo,hi+1)])
  dist=np.convolve(dist,local);offset+=lo;obs+=sum(int(y[i])*events[i]['x'] for i in ix)
 return None if len(dist)==1 else float(dist[max(0,obs-offset):].sum()/dist.sum())
def main():
 assert not (R/'DIAGNOSIS.json').exists();before=manifest();save('PRESERVED-ATTEMPT.json',dict(directory=str(OLD),hashes=before));a.check_seals()
 q=json.loads((OLD/'QUALIFICATION-A-Q1.json').read_text());trials=[json.loads(s) for s in (OLD/'SYNTHETIC-TRIALS-v3.1.jsonl').read_text().splitlines()];events=json.loads((OLD/'MASKED-v3.1.json').read_text());cc=a.cells(events)
 maxk=max(k for k in range(201) if a.e.wilson(k,200)[1]<=.05);bounds=[];audit=[]
 for key,row in q.items():
  nominal=.05/(3 if key.startswith('A-') else 2)
  for r in row['controls']:
   k,n=r['flags'],r['n'];lo=0. if not k else float(beta.ppf(.025,k,n-k+1));hi=1. if k==n else float(beta.ppf(.975,k+1,n-k))
   bounds.append(dict(cell=key,scenario=r['scenario'],role=r['role'],flags=k,n=n,rate=k/n,wilson95=r['wilson95'],exact95=[lo,hi],old_gate=r['gate'],nominal_alpha=nominal,binomial_upper_tail_at_nominal=float(binom.sf(k-1,n,nominal)) if r['role']!='power' else None))
   if r['role']=='power':continue
   rr=[v for v in trials if v['cell']==key and v['scenario']==r['scenario']]
   chosen=[v for v in rr if v['flag']]+[next(v for v in rr if not v['flag'])]
   for rec in chosen:
    vv=cc[key];y=a.e.synthetic(vv,'null_low' if rec['scenario']=='availability_only' else rec['scenario'],rec['seed'])
    if key.startswith('B-') and rec['scenario']=='availability_only':y=y*np.array([v['available'] for v in vv])
    assert hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()==rec['outcome_sha256']
    p=oracle(vv,y);error=abs(p-rec['p']) if p is not None and rec['p'] is not None else 0.
    assert error<1e-11 and (p is not None and p<=nominal)==rec['flag']
    audit.append(dict(cell=key,scenario=rec['scenario'],trial=rec['trial'],absolute_p_error=error,flag=rec['flag']))
 gate_benchmarks={}
 for alpha,ngates,label in [(.05/3,5,'Part_A'),(.025,4,'BQ1'),(.025,2,'BQ2')]:
  p=float(binom.cdf(maxk,200,alpha));gate_benchmarks[label]=dict(nominal=alpha,per_gate_pass_probability=p,per_gate_miss_probability=1-p,all_gates_pass_if_independent_at_nominal=p**ngates,caveat='Boundary benchmark only: exact discrete tests can be conservative; dependence changes joint probability.')
 # Expected aggregate RD under equal available qok rate: structural-availability association is not a null for the unconditioned estimand.
 expected={}
 p1=set(json.loads((R.parent/'sh-qok-single-target-attempt-c/PANELS.json').read_text())['declared_folios']['P1'])
 for co in ['H','F']:
  for name,contexts in [('P1',None),('bath',['C1']),('starred',['C4']),('BQ1',['C6','C7'])]:
   vv=[v for v in events if v['reading']==co and (v['folio'] in p1 if contexts is None else v['context'] in contexts)];num=den=0.
   for ix in a.e.grouping(vv).values():
    ns=sum(vv[i]['x'] for i in ix);nc=len(ix)-ns
    if not ns or not nc:continue
    avs=sum(vv[i]['available']*vv[i]['x'] for i in ix)/ns;avc=sum(vv[i]['available']*(1-vv[i]['x']) for i in ix)/nc;w=ns*nc/(ns+nc);num+=w*.2*(avs-avc);den+=w
   expected[name+'-'+co]=100*num/den if den else None
 hetero=[json.loads(s) for s in (OLD/'HETEROGENEITY-CONTROLS.jsonl').read_text().splitlines()];inner=[]
 for co in ['H','F']:
  for scenario in ['homogeneous_null','homogeneous_positive','heterogeneous_positive']:
   rr=[r for r in hetero if r['reading']==co and r['scenario']==scenario];near=robust=0;undefined=[]
   for r in rr:
    if r['p'] is None:undefined.append(dict(trial=r['trial'],undefined_shuffles=r.get('undefined_shuffles'),observed_defined=r.get('observed_defined')));continue
    k=r['exceedances'];n=r['shuffles'];lo=0 if k==0 else beta.ppf(.025,k,n-k+1);hi=1 if k==n else beta.ppf(.975,k+1,n-k)
    near+=lo<=.025<=hi;robust+=hi<.025
   inner.append(dict(reading=co,scenario=scenario,flags=sum(r['flag'] for r in rr),inner_tail_CI_straddles_alpha=int(near),inner_tail_CI_wholly_below_alpha=int(robust),undefined_trials=undefined,caveat='Pointwise diagnostic for finite permutation sampling, not a simultaneous inference or a reclassification of saved flags. Same frozen permutation bank reused across outer trials.'))
 result=dict(old_attempt_unchanged=before==manifest(),old_gate_accepts_at_most=maxk,gate_design_benchmarks=gate_benchmarks,controls=bounds,oracle_audit=dict(cases=len(audit),max_absolute_error=max(r['absolute_p_error'] for r in audit),records=audit),expected_aggregate_RD_points_under_availability_only=expected,heterogeneity_inner_MC=inner,important_distinctions=['A/Q1 p-values use exact convolution; no inner permutation Monte Carlo. Outer 200 synthetic outcome draws estimate the rejection rate.','A null_low and availability_only have identical marginal law after blocked events are removed. They are independent seeded repetitions, not two different availability mechanisms.','junction_only .1/.6 is constant within each ending family, so it is exchangeable under the exact engine. Additive page/line/position can violate within-stratum exchangeability; it is a robustness stress.','BQ1 original synthetic nulls/positive allow qok on structurally blocked followers. They test an abstract outcome model. The extra availability-only scenario instead induces a nonzero aggregate association and is not a sharp null for unconditioned Q1.','BQ2 has outer simulation uncertainty, finite inner permutation sampling, observed zero variance, and context/folio nonexchangeability issues; more simulations alone do not remove those issues.'])
 assert result['old_attempt_unchanged'];save('DIAGNOSIS.json',result);print(json.dumps(dict(maxk=maxk,benchmarks=gate_benchmarks,oracle_cases=len(audit),expected_availability_RD=expected,heterogeneity_inner_MC=inner),indent=2))
if __name__=='__main__':main()
