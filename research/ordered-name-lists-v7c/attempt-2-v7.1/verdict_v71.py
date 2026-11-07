"""Attempt2 verdict rules; no changes to original raw evaluations or K."""
import sys,math,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'HARNESS'))
from harness import *
MATCH={'E1':('C1-glyph','C2'),'E2':('C1-glyph','C2'),'E3':('C1-word','C2'),'E4':('C1-glyph','C2'),'E5':('within-band',)}
def percentile(values,q):
 if not values or any(x is None for x in values):return None
 return sorted(values)[math.ceil(q*len(values))-1]
def clopper_upper(k,n,confidence=.95):
 if n<=0 or k<0 or k>n:raise ValueError('invalid binomial counts')
 if k==n:return 1.
 alpha=1-confidence;lo,hi=0.,1.
 # Invert P_p(X<=k)=alpha using log binomial terms; exact finite binomial, no normal approximation.
 def cdf(p):
  if p==0:return 1.
  if p==1:return float(k==n)
  logs=[math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1)+j*math.log(p)+(n-j)*math.log1p(-p) for j in range(k+1)]
  m=max(logs);return math.exp(m)*sum(math.exp(x-m) for x in logs)
 for _ in range(100):
  mid=(lo+hi)/2
  if cdf(mid)>alpha:lo=mid
  else:hi=mid
 return (lo+hi)/2

def verdict(k,obs,real_bank,control_banks,require_C2=True):
 if len(real_bank)<1000 or any(len(b)<1000 for b in control_banks.values()):raise NotTestable('1000 C3 keys required for every real/control distribution')
 gain=0.;above99=[];above998=[];metrics={};control_tests={};missing=[];failed=[]
 for e in EIDS:
  v=obs[e]['value'];vals=[z[e]['value'] for z in real_bank]
  if v is None or any(x is None for x in vals):
   metrics[e]={'status':'NOT_ESTIMABLE'}
   if e in ('E3','E4'):missing.append(e)
   continue
  med=statistics.median(vals);tail=(1+sum(x>=v for x in vals))/(len(vals)+1)
  if obs[e]['kind']=='rate':
   n=obs[e]['n'];bits=signed_binomial_bits(obs[e]['success'],n,(med*n+.5)/(n+1))
  else:bits=(v-med)*obs[e]['n']
  gain+=bits
  if tail<=.01:above99.append(e)
  if tail<=.002:above998.append(e)
  metrics[e]={'value':v,'C3_median':med,'mc_p':tail,'gain_bits':bits}
  for control in MATCH[e]:
   names=[x for x in control_banks if x==control or x.startswith(control+':')]
   if control=='C2' and not require_C2:continue
   if not names:missing.append(e+':'+control);continue
   for name in names:
    cut=percentile([z[e]['value'] for z in control_banks[name]],.95)
    ok=v>cut if cut is not None else None
    control_tests[e+':'+name]={'real_value':v,'control_C3_p95':cut,'exceeds':ok,'keys':len(control_banks[name])}
    if ok is None:missing.append(e+':'+name)
    elif not ok:failed.append(e+':'+name)
 coh=gain-complexity(k)
 necessary=coh>0 and len(above99)>=2
 passes=necessary and not failed and not missing
 label='PASS' if passes else 'PARTIAL' if above998 else 'FAIL'
 return {'verdict':label,'K_bits':complexity(k),'coherence_bits':coh,'above_99':above99,'above_998':above998,'metrics':metrics,'matched_controls':control_tests,'failed_controls':failed,'missing_controls':missing,'all_required_controls_pass':not failed and not missing,'necessary_coherence_and_rank':necessary,'applicability':'nonzero supported evaluations; E3/E4 always required','complete_evaluation':not missing}
