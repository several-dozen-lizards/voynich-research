import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('app',P/'run.py');app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
app.verify();data=app.load(P/'INPUT.json');results=app.load(P/'RESULTS.json');X=np.load(P.parent/'zodiac-457-v86/templates.npy').astype(np.float64);blocks=[b['indices'] for b in data['blocks']]
checks={};out=[]
obs=app.load(P.parent/'zodiac-image-audit-v88/OBSERVATIONS.json');lookup={r['id']:r for r in obs}
checks['120_unique_original_slots']=len(data['records'])==len({r['figure_id'] for r in data['records']})==120
checks['exact_revised_observation_join']=all(r['source']['audit_evidence']==lookup[r['figure_id']] for r in data['records'])
checks['reserved_signs_absent']=not any(r['sign'] in ['Virgo','Libra','Scorpio','Sagittarius'] for r in data['records'])
for feature,result in zip(['body','enclosure'],results):
 y=np.array([np.nan if r[feature] is None else r[feature] for r in data['records']]);rng=np.random.default_rng(app.load(P/'APPLICATION.json')['seeds'][feature]);Y=np.tile(y,(200,1))
 for j in range(1,200):
  for b in blocks:Y[j,b]=np.roll(y[b],rng.integers(len(b)))
 allmax=[];observed=None
 for j,v in enumerate(Y):
  mask=np.isfinite(v);v0=np.nan_to_num(v);cross=X@v0;xvar=(X[:,mask]**2).sum(axis=1);yvar=float((v0*v0).sum())
  for b in blocks:
   ix=[i for i in b if mask[i]]
   if not ix:continue
   xs=X[:,ix].sum(axis=1);ys=v0[ix].sum();cross-=xs*ys/len(ix);xvar-=xs*xs/len(ix);yvar-=ys*ys/len(ix)
  xvar=np.maximum(xvar,0);yvar=max(yvar,0);den=np.sqrt(xvar*yvar);signed=np.divide(cross,den,out=np.zeros(len(X)),where=den>1e-12)
  if j==0:observed=signed
  allmax.append(float(max(abs(signed))))
 exceed=sum(v>=allmax[0]-1e-7 for v in allmax[1:]);p=(1+exceed)/200
 checks[feature+'_score_matches']=abs(allmax[0]-result['score'])<1e-6
 checks[feature+'_null_p_matches']=abs(p-result['p_raw'])<1e-12
 saved=app.load(P/(feature+'-all-scores.json'));delta=max(abs(observed[i]-r['signed_score']) for i,r in enumerate(saved))
 checks[feature+'_all18424_signed_scores_match']=delta<1e-6
 checks[feature+'_multisets_and_missingness_preserved']=all(all(sorted([-1 if not np.isfinite(v) else int(v) for v in Y[j,b]])==sorted([-1 if not np.isfinite(v) else int(v) for v in y[b]]) for b in blocks) for j in range(200))
 out.append({'feature':feature,'independent_score':allmax[0],'null_exceedances':exceed,'null_draws':199,'p_raw':p,'max_signed_score_error':delta,'full_search_maxima':allmax})
checks={k:bool(v) for k,v in checks.items()}
assert all(checks.values()),checks
app.dump('INDEPENDENT-AUDIT.json',{'method':'Independent float64 cross-product and block-sum centering formulation, compared with float32 frozen scorer. Identical frozen RNG for permutation reconstruction. Not independent source annotation.','checks':checks,'results':out})
print(json.dumps(checks,indent=2))
