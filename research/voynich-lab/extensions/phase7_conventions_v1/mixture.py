from common import *
from features import fit_basis,transform
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits
def model(k,seed):return GaussianMixture(n_components=k,covariance_type='tied',n_init=3,max_iter=500,tol=1e-4,reg_covar=.001,random_state=seed)
def analyze(raws,seed,out):
    out.mkdir(parents=True,exist_ok=True);folds=json.loads((R/'FOLDS.json').read_text());scores=[];failures=[]
    with threadpool_limits(limits=1):
        for fold in range(5):
            train=[r for r in raws if folds[str(r['leaf'])]!=fold];test=[r for r in raws if folds[str(r['leaf'])]==fold];basis=fit_basis(train);x,_=transform(train,basis);y,tail=transform(test,basis);support=Counter(r['leaf'] for r in test);weights=np.array([1/support[r['leaf']] for r in test])
            for k in range(1,13):
                try:
                    m=model(k,seed);m.fit(x);ll=m.score_samples(y)+tail;valid=bool(m.converged_);value=float(np.sum(ll*weights))
                    scores.append(dict(fold=fold,k=k,seed=seed,log_likelihood=value,held_leaves=len(support),held_pages=len(test),converged=valid,iterations=int(m.n_iter_),q=basis['q'],features=basis['dimension'],retained_variance=basis['retained_variance']))
                    if not valid:failures.append(dict(fold=fold,k=k,error='NONCONVERGED'))
                except Exception as e:failures.append(dict(fold=fold,k=k,error=repr(e)))
            print('fold',out.name,fold,'complete',flush=True)
        table(out/'likelihoods.csv',scores)
        if failures:dump(out/'SEARCH_FAILURES.json',failures);return dict(status='INCOMPLETE_SEARCH',failures=failures)
        curve={k:math.fsum(x['log_likelihood'] for x in scores if x['k']==k) for k in range(1,13)};best=max(curve,key=lambda k:(curve[k],-k));basis=fit_basis(raws);x,_=transform(raws,basis);m=model(best,seed);m.fit(x)
        if not m.converged_:return dict(status='INCOMPLETE_SEARCH',failures=[dict(full_fit=True,k=best,error='NONCONVERGED')])
        labels=m.predict(x);post=m.predict_proba(x);table(out/'page_labels.csv',[dict(page=r['page'],leaf=r['leaf'],cluster=int(c),posterior=json.dumps(p.tolist())) for r,c,p in zip(raws,labels,post)])
        with (out/'full_model.pkl').open('wb') as f:pickle.dump(dict(model=m,basis=basis),f)
        result=dict(status='COMPLETE',best_k=best,curve=curve,full_fit_iterations=int(m.n_iter_),q=basis['q'],retained_variance=basis['retained_variance']);dump(out/'MIXTURE_RESULT.json',result);return result
