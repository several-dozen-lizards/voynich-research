"""Engineering checks only; no rule changes or manuscript scores."""
import run, numpy as np, json
rng=np.random.default_rng(850901)
X=rng.integers(0,2,(8,120),dtype=np.int8)
y=X[0].astype(float)
perfect=run.score_engine(X,y,np.random.default_rng(1))
assert abs(perfect['score']-1)<1e-6
constant=run.score_engine(X,np.ones(120),np.random.default_rng(2))
assert constant['score']==0 and constant['p_two_features']==1
missing=y.copy(); missing[::5]=np.nan
masked=run.score_engine(X,missing,np.random.default_rng(3))
assert abs(masked['score']-1)<1e-6
inv=run.score_engine(1-X,missing,np.random.default_rng(3))
assert abs(inv['score']-masked['score'])<1e-6 and inv['p_raw']==masked['p_raw']
assert all(len(run.expand(s))==30 for s in run.SEX+run.LIGHT)
result={'exact_planted_score_one':True,'constant_response_not_significant':True,'missing_values_not_treated_as_zero':True,'category_complement_invariant':True,'all_table_rows_length30':True,'scope':'Small engineering fixtures only; not additional qualification replicates'}
(run.P/'ENGINE-CHECKS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(result)
