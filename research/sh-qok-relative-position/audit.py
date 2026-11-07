from pathlib import Path
import ast,json,collections,itertools,math,re
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
ns=dict(collections=collections,np=np,math=math,re=re,itertools=itertools)
def load(p,names,env):exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),env)
e=dict(collections=collections,math=math,re=re);load(P/'sh-qok-all-interior/run.py',['events'],e);load(P/'sh-qok-expanded-null/run.py',['subset'],e);ns['e']=e
load(R/'run.py',['groups','score','support'],ns)
rows=[]
for pg in [0,1]:
 for i in range(7):
  left=i<3;rows.append((pg,['dar',('sh' if left else 'ch')+'aedy','qokam' if i<3 else 'dar',('ch' if left else 'sh')+'aedy','qokam' if i>=3 else 'dar','dar']))
g=ns['groups'](rows);poss=[];obs=0
for key,items in g.items():
 w=[int(rows[ri][1][j+1]=='qokam')-int(rows[ri][1][k+1]=='qokam') for ri,j,k,a in items];nsh=sum(x[3] for x in items)
 obs+=sum(a*d for (*_,a),d in zip(items,w));poss.append([sum(w[i] for i in ix) for ix in itertools.combinations(range(len(items)),nsh)])
vals=[sum(x) for x in itertools.product(*poss)];oracle=min(1,8*sum(x>=obs for x in vals)/len(vals));actual=ns['score'](rows,g);assert abs(actual-oracle)<1e-12
out=dict(exhaustive_full_conditional_assignments=len(vals),expected_adjusted_p=oracle,actual_adjusted_p=actual,pass_check=True,scope='Additional implementation audit only; no outcome thresholds or frozen test changed.')
(R/'ORACLE.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(out)


