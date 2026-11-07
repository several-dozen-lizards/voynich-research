from common import *
import numpy as np
TESTS=['conjugacy_within_quire','conjugacy_book','coherence_leaf_shuffle','coherence_bifolio_shuffle']
def holm(values):
    good=sorted([(v,k) for k,v in values.items() if v is not None]);out={k:None for k in values};last=0.
    for i,(p,key) in enumerate(good):last=max(last,min(1.,(len(good)-i)*p));out[key]=last
    return out
def leaf_labels(rows):
    by=defaultdict(list)
    for r in rows:by[int(r['leaf'])].append(np.array(json.loads(r['posterior']),dtype=float))
    return {key:int(np.mean(values,axis=0).argmax()) for key,values in by.items()}
def run(labels,seed,out=None):
    phy=physical();leaves=sorted(labels);index={v:i for i,v in enumerate(leaves)};z=np.array([labels[x] for x in leaves]);qs=defaultdict(list);blocks=defaultdict(list)
    for l in leaves:
        p=phy[str(l)];qs[p['quire']].append(index[l]);blocks[p['sheet']].append(index[l])
    pairs=[b for b in blocks.values() if len(b)==2];edges=np.array(pairs,dtype=int).reshape(-1,2);qgroups=[np.array(v,dtype=int) for v in qs.values()];blockgroups=defaultdict(list)
    for b in blocks.values():blockgroups[len(b)].append(np.array(b,dtype=int))
    denom=sum(len(g)*(len(g)-1)//2 for g in qgroups)
    def conj(x):return float(np.mean(x[edges[:,0]]==x[edges[:,1]])) if len(edges) else None
    def coh(x):return sum(sum(v*(v-1)//2 for v in Counter(x[g]).values()) for g in qgroups)/denom if denom else None
    observed={'conjugacy_within_quire':conj(z),'conjugacy_book':conj(z),'coherence_leaf_shuffle':coh(z),'coherence_bifolio_shuffle':coh(z)};null={k:[] for k in TESTS};rng=np.random.default_rng(seed)
    for _ in range(1999):
        within=z.copy()
        for g in qgroups:within[g]=rng.permutation(z[g])
        book=rng.permutation(z);block=z.copy()
        for bs in blockgroups.values():
            order=rng.permutation(len(bs))
            for host,source in zip(bs,order):block[host]=z[bs[source]]
        values=[conj(within),conj(book),coh(book),coh(block)]
        for k,v in zip(TESTS,values):null[k].append(v)
    result={}
    for key in TESTS:
        ns=null[key];obs=observed[key]
        if obs is None:status='NOT_ESTIMABLE';p=None
        elif min(ns)==max(ns):status='NULL_INVARIANT';p=None
        else:status='SCORED';p=(1+sum(v>=obs for v in ns))/2000
        result[key]=dict(status=status,statistic=obs,p=p,null_mean=statistics.mean(ns) if obs is not None else None,null_sd=statistics.stdev(ns) if obs is not None else None)
    adj=holm({key:r['p'] for key,r in result.items()})
    for key,r in result.items():r['Holm_p']=adj[key]
    summary=dict(tests=result,observed_leaves=len(leaves),complete_observed_bifolia=len(edges),orphan_observed_leaves=sum(len(b)==1 for b in blocks.values()),quire_pair_denominator=denom)
    if out:dump(out,dict(**summary,nulls=null))
    return summary
