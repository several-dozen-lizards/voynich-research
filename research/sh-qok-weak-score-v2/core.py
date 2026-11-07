"""Nuisance-only repair; the frozen v1 interaction score is unchanged."""
from pathlib import Path
import hashlib,math
import numpy as np
import importlib.util

R=Path(__file__).resolve().parent
ROOT=R.parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

old=module('frozen_weak_v1',ROOT/'sh-qok-weak-score-v1/core.py')
a,b=old.a,old.b
null_features=old.null_features
raw_model=old.raw_model
CANDIDATES=('P','J','L','F')

def baseline(events,tr,te):
    """All selection uses leave-one-learning-folio-out predictions, never te."""
    yy=np.array([e['y'] for e in events]);folios=sorted({events[i]['folio'] for i in tr})
    assert {events[i]['folio'] for i in tr}.isdisjoint({events[i]['folio'] for i in te})
    oof={m:np.zeros(len(tr)) for m in ('constant',)+CANDIDATES};pos={i:j for j,i in enumerate(tr)};assignments=[]
    for folio in folios:
        it=[i for i in tr if events[i]['folio']!=folio];iv=[i for i in tr if events[i]['folio']==folio]
        assert iv and it and len(set(yy[it]))==2
        rate=(yy[it].sum()+.5)/(len(it)+1);jj=[pos[i] for i in iv];oof['constant'][jj]=rate
        for m in CANDIDATES:oof[m][jj]=raw_model(events,it,iv,m)
        assignments.append(dict(validation_folio=folio,fit_folios=[f for f in folios if f!=folio],fit_events=len(it),validation_events=len(iv),constant=float(rate)))
    def logloss(p):return float(np.mean(-(yy[tr]*np.log(p)+(1-yy[tr])*np.log(1-p))))
    base_loss=logloss(oof['constant']);penalty=(.5*math.log(len(tr))+math.log(len(CANDIDATES)))/len(tr)
    candidates=[]
    for m in CANDIDATES:
        weight,gain=b.mixture_weight(oof[m],oof['constant'],yy[tr])
        candidates.append(dict(model=m,weight=float(weight),gain_nats=float(gain),penalized_gain=float(gain-penalty)))
    winner=max(candidates,key=lambda x:x['penalized_gain'])
    selected=winner['model'] if winner['penalized_gain']>0 else 'constant';weight=winner['weight'] if selected!='constant' else 0.
    rate=(yy[tr].sum()+.5)/(len(tr)+1);both=tr+te
    raw=raw_model(events,tr,both,selected) if selected!='constant' else np.full(len(both),rate)
    pred=(1-weight)*rate+weight*raw
    calibration=dict(method='learning-folio-OOF single-candidate constant backoff',learning_folios=folios,assignments=assignments,
                     learning_events=tr,learning_y=yy[tr].astype(int).tolist(),oof={m:p.tolist() for m,p in oof.items()},candidates=candidates,
                     baseline_cv_loss_nats=base_loss,penalty_nats=penalty,selected=selected,weight=float(weight),full_learning_constant=float(rate),
                     selected_raw_probabilities=raw.tolist())
    return pred[:len(tr)],pred[len(tr):],calibration

# Only replace the nuisance estimator in the imported frozen score's namespace.
# Split, vocabulary, projection, direction, support, adequacy and p-values stay v1.
old.baseline=baseline
score=old.score

