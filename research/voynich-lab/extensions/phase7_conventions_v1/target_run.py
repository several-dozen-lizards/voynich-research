"""Guarded target analysis. This module is never invoked on failed calibration."""
from common import *
from features import raw_features,fit_basis,transform
from mixture import analyze,model
from physical_tests import run as physical_run,leaf_labels,holm
from sklearn.metrics import adjusted_rand_score,adjusted_mutual_info_score
from threadpoolctl import threadpool_limits
import numpy as np,itertools
def conditional_entropy(a,b):
    joint=Counter(zip(a,b));ctx=Counter(b);n=len(a)
    return -sum(v/n*math.log(v/ctx[y],2) for (x,y),v in joint.items()) if n else None
def external_metadata():
    meta=json.loads((OLD/'LAYOUT.json').read_text());by=defaultdict(list)
    for r in meta:by[page(r['folio'])].append(r)
    result={}
    for p,rs in by.items():
        row={}
        for field in ['currier_lang','hand_scribe','section']:
            values=sorted({str(r.get(field)) for r in rs if r.get(field)})
            row[field]=values[0] if len(values)==1 else 'MIXED' if values else 'UNKNOWN'
        row['quire']=str(physical()[str(leaf(p))]['quire']);result[p]=row
    return result
def association(labels,meta):
    out=[]
    for field in ['currier_lang','hand_scribe','section','quire']:
        pairs=[(int(r['cluster']),meta[r['page']][field]) for r in labels if meta[r['page']][field] not in ['UNKNOWN','MIXED'] and (field!='currier_lang' or meta[r['page']][field] in ['A','B'])];a=[x[0] for x in pairs];b=[x[1] for x in pairs]
        out.append(dict(metadata=field,pages=len(pairs),excluded=len(labels)-len(pairs),AMI=float(adjusted_mutual_info_score(a,b)) if pairs else None,H_metadata_given_cluster=conditional_entropy(b,a),H_cluster_given_metadata=conditional_entropy(a,b),contingency={str(c):dict(Counter(y for x,y in pairs if x==c)) for c in sorted(set(a))}))
    ab=[(int(r['cluster']),meta[r['page']]['currier_lang']) for r in labels if meta[r['page']]['currier_lang'] in ['A','B']]
    nesting={}
    for language in ['A','B']:
        vals=[x for x,y in ab if y==language];h=conditional_entropy(vals,[language]*len(vals));nesting[language]=dict(pages=len(vals),cluster_counts=dict(Counter(vals)),effective_cluster_count=2**h if h is not None else None)
    return dict(associations=out,AB_nesting=nesting)
def sequence(labels,seed):
    lookup={r['page']:int(r['cluster']) for r in labels};orders=json.loads((R/'ORDER_REGISTRY.json').read_text());phy=physical();out=[]
    for order in orders:
        if not order['status'].startswith('ADMITTED'):
            out.append(dict(order=order['id'],status='NOT_ESTIMABLE',reason=order['status'],citation=order['citation']));continue
        if order.get('kind')=='current_binding':
            groups=defaultdict(list)
            for p in sorted(lookup,key=lambda p:(leaf(p),p)):groups[phy[str(leaf(p))]['quire']].append(p)
            segments=list(groups.values())
        else:segments=[order['pages']]
        vals=[np.array([lookup[p] for p in s if p in lookup]) for s in segments];rng=np.random.default_rng(seed);records=[]
        for lag in range(1,13):
            n=sum(max(0,len(v)-lag) for v in vals)
            if n<10:records.append(dict(lag=lag,status='NOT_ESTIMABLE',pairs=n,p=None));continue
            def score(vs):return sum(int(np.sum(v[lag:]!=v[:-lag])) if lag==1 else int(np.sum(v[lag:]==v[:-lag])) for v in vs)/n
            observed=score(vals);null=[score([rng.permutation(v) for v in vals]) for _ in range(1999)];p=(1+sum(x>=observed for x in null))/2000 if min(null)!=max(null) else None;records.append(dict(lag=lag,status='SCORED' if p is not None else 'NULL_INVARIANT',pairs=n,statistic=observed,p=p,null_mean=statistics.mean(null)))
        adj=holm({str(x['lag']):x['p'] for x in records})
        for x in records:x['Holm_p']=adj[str(x['lag'])]
        out.append(dict(order=order['id'],status='DEPENDENT_SENSITIVITY',citation=order['citation'],statistics=records))
    return out
def main():
    verify();qualification=json.loads((R/'QUALIFICATION.json').read_text());assert qualification['status']=='PASS','CONTROL GATE CLOSED: no Voynich feature extraction'
    assert not (R/'TARGET_RUN_MANIFEST.json').exists(),'Target already started; preserve state before any rerun'
    dump(R/'TARGET_RUN_MANIFEST.json',dict(status='FROZEN_BEFORE_TARGET_TEXT_ACCESS',qualification_sha256=sha(R/'QUALIFICATION.json'),registration_sha256=sha(R/'REGISTRATION.json'),code_sha256=sha(Path(__file__)),orders_sha256=sha(R/'ORDER_REGISTRY.json'),target_fit_rule='unchanged calibrated instrument'))
    common=set(json.loads((R/'COMMON_PAGES.json').read_text()));raw={};selected={};union=set()
    with threadpool_limits(limits=1):
        for name,filename in [('ZL','ZL_running.csv'),('H','LSI_H_running.csv')]:
            rows=read(LAB/'data/voynich'/filename);raw[name]=[raw_features(p) for p in pages(rows) if p['page'] in common];gzwrite(R/'targets'/name/'raw.json.gz',raw[name]);selected[name]={}
            for seed in SEEDS:
                result=analyze(raw[name],seed,R/'targets'/name/f's{seed}');assert result['status']=='COMPLETE',result;selected[name][seed]=result['best_k'];union.add(result['best_k'])
        meta=external_metadata();assign={};physical_results=[]
        for name,raws in raw.items():
            basis=fit_basis(raws);x,_=transform(raws,basis)
            for seed in SEEDS:
                allp={};cache={}
                for k in sorted(union):
                    m=model(k,seed);m.fit(x);assert m.converged_;post=m.predict_proba(x);labels=[dict(page=r['page'],leaf=r['leaf'],cluster=int(p.argmax()),posterior=json.dumps(p.tolist())) for r,p in zip(raws,post)];assign[name,seed,k]=labels
                    out=R/'targets'/name/f's{seed}'/f'K{k}';table(out/'labels.csv',labels);dump(out/'metadata.json',association(labels,meta));dump(out/'sequence_sensitivities.json',sequence(labels,seed));ph=physical_run(leaf_labels(labels),seed,out/'physical_nulls.json');cache[k]=ph
                    allp.update({str(k)+':'+test:value['p'] for test,value in ph['tests'].items()})
                adjusted=holm(allp)
                for k,ph in cache.items():
                    for test,value in ph['tests'].items():physical_results.append(dict(transcription=name,seed=seed,k=k,test=test,**value,Holm_across_selected_k=adjusted[str(k)+':'+test]))
        stability=[]
        for name in ['ZL','H']:
            for a,b in itertools.combinations(SEEDS,2):
                aa=assign[name,a,selected[name][a]];bb=assign[name,b,selected[name][b]];stability.append(dict(comparison='seed',transcription=name,seed_a=a,seed_b=b,k_a=selected[name][a],k_b=selected[name][b],ARI=float(adjusted_rand_score([r['cluster'] for r in aa],[r['cluster'] for r in bb]))))
        for seed in SEEDS:
            aa=assign['ZL',seed,selected['ZL'][seed]];bb=assign['H',seed,selected['H'][seed]];stability.append(dict(comparison='transcription',seed_a=seed,seed_b=seed,k_a=selected['ZL'][seed],k_b=selected['H'][seed],ARI=float(adjusted_rand_score([r['cluster'] for r in aa],[r['cluster'] for r in bb]))))
        dump(R/'TARGET_SELECTIONS.json',dict(selected=selected,all_selected_k=sorted(union),criterion='leaf-weighted held-out likelihood'));table(R/'TARGET_PHYSICAL_TESTS.csv',physical_results);table(R/'TARGET_STABILITY.csv',stability)
        dump(R/'RUN_STATE.json',dict(status='COMPLETE',Voynich_gate='QUALIFIED_ANALYSIS_COMPLETE',target_features_read=True,selected=selected,order_primary=False,translation_claims=False))
if __name__=='__main__':main()
