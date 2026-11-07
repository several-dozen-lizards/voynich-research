"""Language-free categorical HMM; compiled CPU inference, no oracle inputs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.analysis-runtime'))
sys.path.insert(0,str(Path(__file__).resolve().parent/'.runtime'))
import numpy as np
from numba import njit, prange

@njit(cache=True)
def forward(x,start,pi,A,B):
    N=len(x); K=len(pi); f=np.zeros((N,K)); scales=np.zeros(N); ll=0.
    for t in range(N):
        for j in range(K):
            v=pi[j] if start[t] else 0.
            if not start[t]:
                for i in range(K): v+=f[t-1,i]*A[i,j]
            f[t,j]=v*B[j,x[t]]; scales[t]+=f[t,j]
        if scales[t]<=0: return f,scales,-np.inf
        ll+=np.log(scales[t])
        for j in range(K): f[t,j]/=scales[t]
    return f,scales,ll

@njit(cache=True)
def normalize(v):
    total=0.
    for i in range(len(v)):
        v[i]=max(v[i],1.e-12); total+=v[i]
    for i in range(len(v)): v[i]/=total

@njit(cache=True)
def init(K,V,seed):
    np.random.seed(seed)
    pi=np.random.gamma(1.,1.,K); normalize(pi)
    A=np.empty((K,K)); B=np.empty((K,V))
    for i in range(K):
        A[i]=np.random.gamma(1.,1.,K); normalize(A[i])
        B[i]=np.random.gamma(1./V,1.,V); normalize(B[i])
    return pi,A,B

@njit(cache=True)
def em(x,start,K,V,seed,maxiter=100,tol=1.e-6):
    pi,A,B=init(K,V,seed); trace=np.full(maxiter+1,np.nan)
    f,s,ll=forward(x,start,pi,A,B); trace[0]=ll; steps=0
    for it in range(maxiter):
        cp=np.zeros(K); ca=np.zeros((K,K)); cb=np.zeros((K,V)); beta=np.ones(K)
        for t in range(len(x)-1,-1,-1):
            if t==len(x)-1 or start[t+1]: beta=np.ones(K)
            gamma=f[t]*beta; gamma/=gamma.sum()
            for i in range(K): cb[i,x[t]]+=gamma[i]
            if start[t]:
                for i in range(K): cp[i]+=gamma[i]
            if t>0 and not start[t]:
                previous=np.zeros(K)
                for i in range(K):
                    for j in range(K):
                        v=A[i,j]*B[j,x[t]]*beta[j]/s[t]
                        ca[i,j]+=f[t-1,i]*v; previous[i]+=v
                beta=previous
        normalize(cp); pi=cp
        for i in range(K): normalize(ca[i]); normalize(cb[i])
        A=ca; B=cb
        f,s,newll=forward(x,start,pi,A,B); trace[it+1]=newll; steps=it+1
        if not np.isfinite(newll): ll=newll; break
        gain=(newll-ll)/max(1,len(x)); ll=newll
        if it>=4 and abs(gain)<=tol: break
    return pi,A,B,ll,steps,trace

@njit(cache=True)
def counts(x,start,z,K,V):
    cp=np.zeros(K); ca=np.zeros((K,K)); cb=np.zeros((K,V))
    for t in range(len(x)):
        cb[z[t],x[t]]+=1
        if start[t]: cp[z[t]]+=1
        else: ca[z[t-1],z[t]]+=1
    return cp,ca,cb

@njit(cache=True)
def conditional(t,x,start,z,cp,ca,cb):
    # Counts must have this site's emission, initial and both edges removed.
    return conditional_fast(t,x,start,z,cp,ca,cb,ca.sum(axis=1),cb.sum(axis=1))

@njit(cache=True)
def conditional_fast(t,x,start,z,cp,ca,cb,atot,btot):
    K=len(cp); V=cb.shape[1]; weights=np.empty(K)
    prev=-1 if start[t] else z[t-1]
    nxt=-1 if t==len(x)-1 or start[t+1] else z[t+1]
    alpha=1./K; beta=1./V
    for k in range(K):
        prob=(cb[k,x[t]]+beta)/(btot[k]+1.)
        if prev<0: prob*=(cp[k]+alpha)/(cp.sum()+1.)
        else: prob*=(ca[prev,k]+alpha)/(atot[prev]+1.)
        if nxt>=0:
            # Sequential Dirichlet predictive for adding both adjacent edges.
            prob*=(ca[k,nxt]+alpha+(1. if prev==k and nxt==k else 0.))/(atot[k]+1.+(1. if prev==k else 0.))
        weights[k]=prob
    return weights/weights.sum()

@njit(cache=True)
def posterior(cp,ca,cb):
    K=len(cp); V=cb.shape[1]
    pi=cp+1./K; pi/=pi.sum()
    A=ca+1./K; B=cb+1./V
    for k in range(K): A[k]/=A[k].sum(); B[k]/=B[k].sum()
    return pi,A,B

@njit(cache=True)
def gibbs(x,start,K,V,seed,sweeps=100,burn=50,thin=10):
    np.random.seed(seed); z=np.random.randint(0,K,len(x)); cp,ca,cb=counts(x,start,z,K,V)
    atot=ca.sum(axis=1); btot=cb.sum(axis=1)
    best=-np.inf; bpi,bA,bB=posterior(cp,ca,cb); trace=np.full(sweeps//thin,np.nan)
    for sweep in range(sweeps):
        # Systematic full sweep is a valid Gibbs kernel; no red/black approximation.
        for t in range(len(x)):
            old=z[t]; cb[old,x[t]]-=1; btot[old]-=1
            if start[t]: cp[old]-=1
            else: ca[z[t-1],old]-=1; atot[z[t-1]]-=1
            hasnext=t+1<len(x) and not start[t+1]
            if hasnext: ca[old,z[t+1]]-=1; atot[old]-=1
            probs=conditional_fast(t,x,start,z,cp,ca,cb,atot,btot)
            u=np.random.random(); acc=0.; new=K-1
            for k in range(K):
                acc+=probs[k]
                if u<acc: new=k; break
            z[t]=new; cb[new,x[t]]+=1; btot[new]+=1
            if start[t]: cp[new]+=1
            else: ca[z[t-1],new]+=1; atot[z[t-1]]+=1
            if hasnext: ca[new,z[t+1]]+=1; atot[new]+=1
        if (sweep+1)%thin==0:
            pi,A,B=posterior(cp,ca,cb); _,_,ll=forward(x,start,pi,A,B); trace[sweep//thin]=ll
            if sweep+1>burn and ll>best: best=ll; bpi=pi.copy(); bA=A.copy(); bB=B.copy()
    return bpi,bA,bB,best,sweeps,trace

@njit(cache=True,parallel=True)
def restarts(x,start,K,V,seeds,algorithm,maxiter=100):
    R=len(seeds); pis=np.zeros((R,K)); As=np.zeros((R,K,K)); Bs=np.zeros((R,K,V))
    lls=np.zeros(R); steps=np.zeros(R,np.int64); traces=np.full((R,maxiter+1),np.nan)
    for r in prange(R):
        if algorithm==0: pi,A,B,ll,n,tr=em(x,start,K,V,seeds[r],maxiter)
        else: pi,A,B,ll,n,tr=gibbs(x,start,K,V,seeds[r],maxiter,maxiter//2,10)
        pis[r]=pi; As[r]=A; Bs[r]=B; lls[r]=ll; steps[r]=n
        for i in range(len(tr)): traces[r,i]=tr[i]
    return pis,As,Bs,lls,steps,traces

@njit(cache=True)
def viterbi(x,start,pi,A,B):
    K=len(pi); N=len(x); back=np.zeros((N,K),np.int32); scores=np.empty((N,K)); z=np.zeros(N,np.int32)
    lp=np.log(pi); la=np.log(A); lb=np.log(B)
    for t in range(N):
        for j in range(K):
            if start[t]: scores[t,j]=lp[j]+lb[j,x[t]]
            else:
                best=-np.inf; arg=0
                for i in range(K):
                    value=scores[t-1,i]+la[i,j]
                    if value>best: best=value; arg=i
                scores[t,j]=best+lb[j,x[t]]; back[t,j]=arg
        if t==N-1 or start[t+1]:
            z[t]=np.argmax(scores[t]); s=t
            while s>0 and not start[s]: z[s-1]=back[s,z[s]]; s-=1
    return z
