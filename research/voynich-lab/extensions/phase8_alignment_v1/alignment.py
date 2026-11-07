from common import *
import numpy as np
from scipy.optimize import quadratic_assignment
def vocabulary(rows,label_by_leaf,which):
    counts=Counter(w for r in rows if label_by_leaf[leaf(r['folio'])]==which for w in r['text_eva'].split());v=[w for w,n in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:NODES]]
    return v+[f'__PAD_{which}_{i}' for i in range(NODES-len(v))]
def graph(rows,vocab):
    lookup={v:i for i,v in enumerate(vocab)};p=np.zeros(NODES);g=np.zeros((NODES,NODES));total=0;all_edges=0;retained_edges=0
    for r in rows:
        words=r['text_eva'].split();total+=len(words)
        for word in words:
            if word in lookup:p[lookup[word]]+=1
        for i,a in enumerate(words):
            for b in words[i+1:i+3]:
                all_edges+=1
                if a in lookup and b in lookup:
                    retained_edges+=1
                    if a!=b:g[lookup[a],lookup[b]]+=1;g[lookup[b],lookup[a]]+=1
    mass=float(p.sum());pn=float(np.linalg.norm(p));gn=float(np.linalg.norm(g));valid=total>0 and pn>0 and gn>0
    return dict(p=p/pn if pn else p,G=g/gn if gn else g,coverage=mass/total if total else 0.,tokens=total,edge_coverage=retained_edges/all_edges if all_edges else 0.,valid=valid)
def raw_score(a,b,permutation=None,identity=None):
    if not a['valid'] or not b['valid']:raise ValueError('NOT_ESTIMABLE_EMPTY_CORE_GRAPH')
    if permutation is not None:bp=b['p'][permutation];bg=b['G'][np.ix_(permutation,permutation)]
    else:
        bp=np.zeros(NODES);bg=np.zeros((NODES,NODES));ai,bi=identity;bp[ai]=b['p'][bi];bg[np.ix_(ai,ai)]=b['G'][np.ix_(bi,bi)]
    coverage=math.sqrt(a['coverage']*b['coverage']);gs=float(np.sum(a['G']*bg));fs=float(a['p']@bp)
    return dict(score=coverage*(gs+fs)/2,graph=gs,frequency=fs,coverage=coverage)
def identity_indices(va,vb):
    b={v:i for i,v in enumerate(vb) if not v.startswith('__PAD_')};ai=[];bi=[]
    for i,v in enumerate(va):
        if v in b:ai.append(i);bi.append(b[v])
    return np.array(ai,dtype=int),np.array(bi,dtype=int)
def learn(rows,label_by_leaf,seed):
    va=vocabulary(rows,label_by_leaf,'A');vb=vocabulary(rows,label_by_leaf,'B');a=graph([r for r in rows if label_by_leaf[leaf(r['folio'])]=='A'],va);b=graph([r for r in rows if label_by_leaf[leaf(r['folio'])]=='B'],vb)
    if not a['valid'] or not b['valid']:raise ValueError('NOT_ESTIMABLE_TRAINING_HALF')
    ai,bi=identity_indices(va,vb);native=np.full(NODES,-1,dtype=int);native[ai]=bi;remaining=[j for j in range(NODES) if j not in set(bi)]
    for i,j in zip(np.where(native<0)[0],remaining):native[i]=j
    rank=np.arange(NODES);ma=(a['G']+np.diag(a['p']))/math.sqrt(2);mb=(b['G']+np.diag(b['p']))/math.sqrt(2);candidates=[rank,native];receipts=[]
    for i,start in enumerate([np.eye(NODES),np.eye(NODES)[native],'barycenter','randomized']):
        result=quadratic_assignment(ma,mb,method='faq',options=dict(maximize=True,P0=start,rng=sid(seed,'start',i)%(2**32),maxiter=100,tol=.001));permutation=result.col_ind;candidates.append(permutation);receipts.append(dict(start=i,iterations=int(result.nit),budget_endpoint=bool(result.nit>=100)))
    best=min(candidates,key=lambda p:(-float(np.sum(ma*mb[np.ix_(p,p)])),tuple(int(x) for x in p)))
    return dict(va=va,vb=vb,permutation=best,identity=(ai,bi),train_score=raw_score(a,b,best),optimizer=receipts)
def evaluate(rows,labels,seed,save=None):
    fm=folds();records=[];maps=[]
    for fold in range(5):
        train=[r for r in rows if fm[str(leaf(r['folio']))]!=fold];test=[r for r in rows if fm[str(leaf(r['folio']))]==fold];mapping=learn(train,labels,sid(seed,'fold',fold));a=graph([r for r in test if labels[leaf(r['folio'])]=='A'],mapping['va']);b=graph([r for r in test if labels[leaf(r['folio'])]=='B'],mapping['vb']);score=raw_score(a,b,mapping['permutation']);native=raw_score(a,b,identity=mapping['identity'])
        records.append(dict(fold=fold,Q=score['score'],Q0=native['score'],D=score['score']-native['score'],graph=score['graph'],frequency=score['frequency'],A_coverage=a['coverage'],B_coverage=b['coverage'],A_tokens=a['tokens'],B_tokens=b['tokens'],A_edge_coverage=a['edge_coverage'],B_edge_coverage=b['edge_coverage']))
        maps.append(dict(fold=fold,A_units=mapping['va'],B_units=mapping['vb'],permutation=mapping['permutation'].tolist(),train_score=mapping['train_score'],optimizer=mapping['optimizer']))
    result=dict(Q=statistics.mean(r['Q'] for r in records),D=statistics.mean(r['D'] for r in records),Q0=statistics.mean(r['Q0'] for r in records),folds=records)
    if save:dump(save,dict(**result,mappings=maps))
    return result
def nulls(rows,labels,seed,observed,out):
    fm=folds();by=defaultdict(list);sides=defaultdict(set)
    for r in rows:sides[leaf(r['folio'])].add(side(r['folio']))
    for l in labels:by[fm[str(l)],len(sides[l])].append(l)
    rng=np.random.default_rng(sid(seed,'null')%(2**32));results=[];assignments=[]
    for i in range(99):
        shuffled=labels.copy()
        for group in by.values():
            vals=rng.permutation([labels[l] for l in group])
            for l,v in zip(group,vals):shuffled[l]=str(v)
        value=evaluate(rows,shuffled,seed);results.append(dict(index=i,Q=value['Q'],D=value['D']));assignments.append([shuffled[l] for l in sorted(labels)])
    stats={}
    for key in ['Q','D']:
        vals=[v[key] for v in results];p=(1+sum(v>=observed[key] for v in vals))/100 if min(vals)!=max(vals) else None;stats[key]=dict(p=p,observed=observed[key],null_mean=statistics.mean(vals),null_sd=statistics.stdev(vals),status='SCORED' if p is not None else 'NULL_INVARIANT')
    dump(out,dict(statistics=stats,null_scores=results,leaf_order=sorted(labels),assignments=assignments,unique_assignments=len({tuple(a) for a in assignments}),unchanged_assignments=sum(all(a[j]==labels[l] for j,l in enumerate(sorted(labels))) for a in assignments)))
    return stats
