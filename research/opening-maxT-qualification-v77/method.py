import numpy as np
from scipy.stats import rankdata

def transform(scores):
 # A one-unit D count change has squared scale 1. No candidate is discarded.
 x=np.asarray(scores,dtype=np.float64);mean=x.mean(axis=0);sd=np.sqrt(x.var(axis=0,ddof=0)+1.0)
 z=(x-mean)/sd;return mean,sd,z

def maximums(scores,block=128):
 N,K=scores.shape;maxima=np.zeros(N,dtype=np.float64);mean=np.empty(K);sd=np.empty(K)
 for lo in range(0,K,block):
  hi=min(K,lo+block);m,s,z=transform(scores[:,lo:hi]);mean[lo:hi]=m;sd[lo:hi]=s;maxima=np.maximum(maxima,np.abs(z).max(axis=1))
 return mean,sd,maxima

def target_result(scores,column,sign,maxima,mean,sd,panels=14):
 values=np.asarray(scores[:,column],dtype=np.float64)*sign;z=float((scores[0,column]-mean[column])/sd[column])*sign
 hits=int(np.sum(maxima[1:]>=abs(z)-1e-12));p=(1+hits)/len(scores)
 return dict(observed_D=int(values[0]),null_mean=float(values[1:].mean()),null_95=[float(v) for v in np.quantile(values[1:],[.025,.975])],center=float(mean[column]*sign),scale=float(sd[column]),observed_Z=z,max_tail_exceedances=hits,permutations=len(scores)-1,p_family=p,p_all_panels=min(1,p*panels))

def rotation_p(maxima,panels):
 # Every exchangeable row can serve as the observation; ties count against it.
 return np.minimum(1,panels*rankdata(-maxima,method='max')/len(maxima))

def inject_target(other_max,target,row,delta,scale,panels):
 # Recompute the symmetric studentization after a single planted row changes.
 x=target.copy();x[row]+=delta*scale;m=x.mean();s=np.sqrt(x.var(ddof=0)+1)
 z=np.abs((x-m)/s);mx=np.maximum(other_max,z)
 return min(1,panels*np.mean(mx>=z[row]-1e-12))
