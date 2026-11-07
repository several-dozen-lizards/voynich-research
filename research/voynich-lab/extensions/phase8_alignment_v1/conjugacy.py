from common import *
from alignment import learn,graph
import numpy as np
def run(rows,labels,seed,out):
    phy=facts();byq=defaultdict(list)
    for r in rows:byq[phy[str(leaf(r['folio']))]['quire']].append(r)
    kernels=[];pair_info=[]
    for q,held in sorted(byq.items()):
        train=[r for r in rows if phy[str(leaf(r['folio']))]['quire']!=q];mapping=learn(train,labels,sid(seed,'outside_quire',q));byl=defaultdict(list)
        for r in held:byl[leaf(r['folio'])].append(r)
        ls=sorted(byl);profiles=[]
        for l in ls:
            g=graph(byl[l],mapping['va'] if labels[l]=='A' else mapping['vb'])
            if not g['valid']:raise ValueError('NOT_ESTIMABLE_LEAF_CORE_GRAPH')
            if labels[l]=='B':p=mapping['permutation'];g={**g,'G':g['G'][np.ix_(p,p)],'p':g['p'][p]}
            profiles.append(g)
        index={l:i for i,l in enumerate(ls)};edges=[(index[l],index[phy[str(l)]['conjugate']]) for l in ls if l<phy[str(l)]['conjugate'] and phy[str(l)]['conjugate'] in index]
        if not edges:continue
        sim=np.zeros((len(ls),len(ls)))
        for i,a in enumerate(profiles):
            for j,b in enumerate(profiles):sim[i,j]=math.sqrt(a['coverage']*b['coverage'])*(.5*float(np.sum(a['G']*b['G']))+.5*float(a['p']@b['p']))
        kernels.append((sim,edges));pair_info.extend(dict(quire=q,leaf1=ls[i],leaf2=ls[j],similarity=float(sim[i,j]),partition_pair=labels[ls[i]]+labels[ls[j]]) for i,j in edges)
    n=sum(len(e) for _,e in kernels)
    if not n:raise ValueError('NOT_ESTIMABLE_NO_COMPLETE_CONJUGATES')
    observed=sum(sum(float(s[i,j]) for i,j in e) for s,e in kernels)/n;rng=np.random.default_rng(sid(seed,'within_quire_conjugacy')%(2**32));ns=[]
    for _ in range(1999):
        value=0.
        for sim,edges in kernels:
            order=rng.permutation(len(sim));value+=sum(float(sim[order[i],order[j]]) for i,j in edges)
        ns.append(value/n)
    p=(1+sum(v>=observed for v in ns))/2000 if min(ns)!=max(ns) else None
    result=dict(status='SCORED' if p is not None else 'NULL_INVARIANT',statistic=observed,p=p,null_mean=statistics.mean(ns),null_sd=statistics.stdev(ns),complete_pairs=n,test='mapped_graph_similarity_within_quire_only',pairs=pair_info)
    dump(out,dict(**result,nulls=ns));return {k:v for k,v in result.items() if k!='pairs'}
