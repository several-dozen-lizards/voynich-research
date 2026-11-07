import collections,random
import numpy as np
from scipy.stats import rankdata
FORCED=['prefix:sh','prefix:qok','prefix:d','prefix:a','union:l/s','exact:ol/or']
QUESTIONS=[('prefix:sh','prefix:qok'),('prefix:qok','exact:ol/or'),('prefix:d','prefix:sh'),('union:l/s','prefix:a')]
def belongs(w,label):
 if label.startswith('prefix:'):return w.startswith(label[7:])
 if label=='union:l/s':return w.startswith(('l','s'))
 return w in ('ol','or')
def prepare(rows):
 freq=collections.Counter();folios=collections.defaultdict(set)
 for r in rows:
  for w in r['tokens']:
   if w is None:continue
   for n in range(1,min(3,len(w))+1):lab='prefix:'+w[:n];freq[lab]+=1;folios[lab].add(r['folio'])
 labels=sorted(set(lab for lab,v in freq.items() if v>=20 and len(folios[lab])>=2)|set(FORCED));K=len(labels)
 words=sorted({w for r in rows for w in r['tokens'] if w is not None});wordid={w:i for i,w in enumerate(words)}
 memberships=[[i for i,lab in enumerate(labels) if belongs(w,lab)] for w in words];W=max(map(len,memberships),default=0)
 code=np.full((len(words),W),-1,dtype=np.int32)
 for i,ms in enumerate(memberships):code[i,:len(ms)]=ms
 lines=[];buckets=[];offset=0;li=[];ri=[]
 for r in rows:
  ws=r['tokens'];ids=[wordid[w] if w is not None else -1 for w in ws];lines.extend(ids);start=1
  for j in range(len(ws)-1):
   if ws[j] is not None and ws[j+1] is not None:li.append(offset+j);ri.append(offset+j+1)
  for j in range(1,len(ws)):
   if j<len(ws)-1 and ws[j] is not None:continue
   if j-start>=2:buckets.append(np.arange(offset+start,offset+j))
   start=j+1
  offset+=len(ws)
 ia,ib=np.triu_indices(K,1)
 return dict(labels=labels,words=words,wordid=wordid,code=code,K=K,original=np.array(lines,dtype=np.int32),buckets=buckets,li=np.array(li,dtype=np.int32),ri=np.array(ri,dtype=np.int32),ia=ia,ib=ib,family_marginals={lab:dict(tokens=freq[lab],folios=len(folios[lab]),forced=lab in FORCED) for lab in labels if lab.startswith('prefix:')})
def count(arr,p):
 K=p['K'];left=p['code'][arr[p['li']]];right=p['code'][arr[p['ri']]];c=np.zeros(K*K,dtype=np.int32)
 for j in range(left.shape[1]):
  for k in range(right.shape[1]):
   a=left[:,j];b=right[:,k];mask=(a>=0)&(b>=0)
   c+=np.bincount(a[mask]*K+b[mask],minlength=K*K).astype(np.int32)
 c=c.reshape(K,K);return c,c[p['ia'],p['ib']]-c[p['ib'],p['ia']]
def calibrate(scores):
 N=len(scores);minimum=np.ones(N);tails=[]
 for j in range(scores.shape[1]):
  v=scores[:,j];up=rankdata(-v,method='max')/N;lo=rankdata(v,method='max')/N;t=np.minimum(up,lo);minimum=np.minimum(minimum,t);tails.append((float(up[0]),float(lo[0]),float(t[0])))
 return minimum,tails
def run(rows,B,seed,progress=None):
 p=prepare(rows);rng=np.random.default_rng(seed);scores=np.empty((B+1,len(p['ia'])),dtype=np.int16);observed,scores[0]=count(p['original'],p)
 for b in range(1,B+1):
  a=p['original'].copy()
  for indices in p['buckets']:a[indices]=rng.permutation(a[indices])
  _,v=count(a,p);assert np.max(np.abs(v),initial=0)<=32767;scores[b]=v
  if progress and b%1000==0:progress(b)
 minimum,tails=calibrate(scores);results=[]
 for a,b in QUESTIONS:
  i=p['labels'].index(a);j=p['labels'].index(b);small,big=sorted((i,j));col=int(np.flatnonzero((p['ia']==small)&(p['ib']==big))[0]);sign=1 if i<j else -1
  values=scores[:,col].astype(np.int32)*sign;up,lo,t=tails[col]
  if sign<0:up,lo=lo,up
  results.append(dict(A=a,B=b,forward=int(observed[i,j]),reverse=int(observed[j,i]),observed_D=int(values[0]),null_mean=float(values[1:].mean()),null_95=[float(v) for v in np.quantile(values[1:],[.025,.975])],p_raw_two_sided=min(1,2*t),p_upper=up,p_search_family=float(np.mean(minimum<=t+1e-14)),column=col,sign=sign))
 movable={int(i) for indices in p['buckets'] if len(set(p['original'][indices]))>=2 for i in indices}
 result=dict(labels=p['labels'],class_pairs=len(p['ia']),reported_rules=results,mobility=dict(readable_adjacent_slots=len(p['li']),movable_word_slots=len(movable),shuffle_buckets=len(p['buckets'])),family_marginals=p['family_marginals'])
 return result,scores
