"""Finite-prototype synthetic CV; preserves the original L2 objective exactly.
Each assignment gets every inner/outer fit. Only label-invariant matrices are reused.
Not used to score manuscript data. Numerical parity is required before controls.
"""
from common import *
import numpy as np
from scipy.special import softmax, logsumexp
from sklearn.feature_extraction import DictVectorizer
from t1 import folds, GRID

class BatchCV:
    def __init__(self,prototypes,types,groups,pages,classes):
        self.types=np.asarray(types);self.groups=np.asarray(groups);self.pages=np.asarray(pages)
        self.K=classes;self.D=len(prototypes);self.n=len(types);self.cache={}
        self.vectors=DictVectorizer().fit_transform(prototypes).toarray()
        self.outer=list(folds(self.groups,5))
        self.inner=[list(folds(self.groups[tr],4)) for tr,te in self.outer]

    def design(self,train):
        counts=np.bincount(self.types[train],minlength=self.D);key=tuple(counts)
        if key not in self.cache:
            weights=counts/counts.sum();mean=weights@self.vectors
            var=weights@((self.vectors-mean)**2);scale=np.where(var>1e-14,np.sqrt(var),1.)
            v=self.vectors/scale;v-=v.mean(axis=0)
            u,s,vh=np.linalg.svd(v,full_matrices=False)
            z=np.column_stack([v@vh[s>1e-10].T,np.ones(self.D)])
            self.cache[key]=(z,counts)
        return self.cache[key]

    def counts(self,Y,index):
        out=np.zeros((len(Y),self.D,self.K))
        for d in range(self.D):
            use=index[self.types[index]==d]
            for k in range(self.K):out[:,d,k]=(Y[:,use]==k).sum(axis=1)
        return out

    def fit(self,Y,train,C):
        z,n=self.design(train);target=self.counts(Y,train);B=len(Y);p=z.shape[1];k=self.K-1
        if np.any(target.sum(axis=1)==0):raise ValueError('Missing training class')
        w=np.zeros((B,p,k));M=np.eye(k) if self.K==2 else np.eye(k)-np.ones((k,k))/self.K
        penalty=np.zeros((p,k,p,k))
        for j in range(p-1):penalty[j,:,j,:]=M/C
        penalty=penalty.reshape(p*k,p*k)
        def probs(value):
            logits=np.concatenate([np.einsum('dp,bpk->bdk',z,value),np.zeros((B,self.D,1))],axis=2)
            return softmax(logits,axis=2),logits
        def objective(value):
            pr,logits=probs(value);flat=value.reshape(B,-1)
            return np.sum(n[None,:]*logsumexp(logits,axis=2)-np.sum(target*logits,axis=2),axis=1)+.5*np.einsum('bi,ij,bj->b',flat,penalty,flat)
        for iteration in range(60):
            pr,_=probs(w);q=pr[:,:,:k]
            grad=np.einsum('dp,bdk->bpk',z,n[None,:,None]*q-target[:,:,:k]).reshape(B,-1)
            grad+=w.reshape(B,-1)@penalty
            cov=-q[:,:,:,None]*q[:,:,None,:]
            for j in range(k):cov[:,:,j,j]+=q[:,:,j]
            hess=np.einsum('di,dj,bdkl,d->bikjl',z,z,cov,n).reshape(B,p*k,p*k)+penalty
            step=np.linalg.solve(hess,grad[...,None])[...,0].reshape(B,p,k)
            old=objective(w);rate=np.ones(B)
            for backtrack in range(25):
                bad=objective(w-rate[:,None,None]*step)>old+1e-10
                if not np.any(bad):break
                rate[bad]*=.5
            delta=rate[:,None,None]*step;w-=delta
            if np.max(np.abs(delta))<1e-8:return probs(w)[0]
        raise ValueError('Batch Newton did not converge')

    def losses(self,Y,index,pr):
        return -np.sum(self.counts(Y,index)*np.log(np.clip(pr,1e-15,1)),axis=(1,2))

    def evaluate(self,Y,return_trace=False):
        Y=np.asarray(Y,dtype=np.int8)
        if Y.ndim==1:Y=Y[None,:]
        loss=np.zeros(len(Y));trace=[];prediction=np.zeros((len(Y),self.n),dtype=np.int8)
        for oi,(train,test) in enumerate(self.outer):
            tuning=np.zeros((len(Y),len(GRID)))
            for ci,C in enumerate(GRID):
                for itr,ite in self.inner[oi]:
                    tr,te=train[itr],train[ite]
                    tuning[:,ci]+=self.losses(Y,te,self.fit(Y,tr,C))
            chosen=np.argmin(tuning,axis=1);pr=np.zeros((len(Y),self.D,self.K))
            for ci,C in enumerate(GRID):
                ix=np.flatnonzero(chosen==ci)
                if len(ix):pr[ix]=self.fit(Y[ix],train,C)
            loss+=self.losses(Y,test,pr)
            prediction[:,test]=np.argmax(pr[:,self.types[test],:],axis=2)
            if return_trace:trace.append(dict(chosen_C=[GRID[i] for i in chosen],inner_loss=(tuning/len(train)).tolist()))
        base=np.zeros(len(Y))
        for page in sorted(set(self.pages)):
            ix=np.flatnonzero(self.pages==page);yy=Y[:,ix]
            counts=np.stack([(yy==k).sum(axis=1) for k in range(self.K)],axis=1)
            numer=np.take_along_axis(counts,yy,axis=1)-1+.5
            base-=np.log(numer/(len(ix)-1+.5*self.K)).sum(axis=1)
        ba=np.mean([np.sum((prediction==k)&(Y==k),axis=1)/np.sum(Y==k,axis=1) for k in range(self.K)],axis=0)
        out=dict(gain=(base-loss)/self.n,log_loss=loss/self.n,page_prior_log_loss=base/self.n,balanced_accuracy=ba)
        if return_trace:out['trace']=trace
        return out

def assignments(y,pages,nperm,seed):
    from t1 import permute
    rng=np.random.default_rng(seed)
    return np.stack([np.asarray(y)]+[permute(y,pages,rng) for _ in range(nperm)])
