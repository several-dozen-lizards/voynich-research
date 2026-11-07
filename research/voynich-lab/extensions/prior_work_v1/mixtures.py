"""EM mixtures of smoothed character LMs, plus within-line membership companions.

One latent component per whole line is retained as requested. Companions use
word/fixed-five-word units and line-specific membership proportions. No metadata
enters fitting. Component-language mapping is used ONLY for C14 qualification.
"""
import itertools,math
from collections import defaultdict,Counter
from .common import *
import numpy as np
from scipy.sparse import csr_matrix
from scipy.special import logsumexp
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score,adjusted_mutual_info_score,balanced_accuracy_score

class CharFeatures:
    def __init__(self,train_texts,order=2):
        self.order=order;self.alphabet=sorted(set(''.join(train_texts)))+['<EOS>','<UNK>']
        self.symbols={c:i for i,c in enumerate(self.alphabet)};contexts=set()
        for text in train_texts:
            history=['<BOS>']*order
            for c in list(text)+['<EOS>']:
                contexts.add(tuple(history));history=(history+[c])[-order:]
        self.contexts={c:i for i,c in enumerate(sorted(contexts))};self.unknown_context=len(self.contexts)
        self.V=len(self.alphabet);self.C=len(self.contexts)+1
    def transform(self,texts):
        values=[];columns=[];offset=[0];lengths=[]
        for text in texts:
            history=['<BOS>']*self.order;counts=Counter()
            for c in list(text)+['<EOS>']:
                context=self.contexts.get(tuple(history),self.unknown_context);target=self.symbols.get(c,self.symbols['<UNK>'])
                counts[context*self.V+target]+=1
                history=(history+[c if c in self.symbols else '<UNK>'])[-self.order:]
            for index,count in counts.items():columns.append(index);values.append(count)
            offset.append(len(values));lengths.append(len(text)+1)
        return csr_matrix((values,columns,offset),shape=(len(texts),self.C*self.V),dtype=np.float64),np.array(lengths)

def unit_rows(selected,method,truth=None):
    result=[];fraction=[];truth=truth or {}
    size=1 if method=='word_membership' else 5
    for row_index,r in enumerate(selected):
        words=r['text_eva'].split();origins=truth.get(r['line_id'],{}).get('word_sources',[None]*len(words))
        if len(origins)!=len(words):raise ValueError('Source truth no longer aligns to scored word slots')
        cuts=[(0,len(words))] if method=='line' else [(i,min(i+size,len(words))) for i in range(0,len(words),size)]
        for begin,end in cuts:
            result.append(dict(line_id=r['line_id'],folio=r['folio'],row_index=row_index,text=' '.join(words[begin:end]),word_start=begin,word_end=end))
            values=[x for x in origins[begin:end] if x is not None]
            fraction.append(sum(values)/len(values) if values else np.nan)
    return result,np.array(fraction)

def initialize_embeddings(texts):
    x=HashingVectorizer(analyzer='char',ngram_range=(2,3),n_features=8192,alternate_sign=False,norm='l2',lowercase=False).transform(texts)
    dimensions=min(8,x.shape[0]-1,x.shape[1]-1)
    if dimensions<1:return np.ones((len(texts),1))
    return TruncatedSVD(dimensions,random_state=1729).fit_transform(x)

def fit_em(x,groups,embedding,k,seed,V,C,settings,membership):
    n=len(groups);unique,group_ids=np.unique(groups,return_inverse=True);G=len(unique)
    if k==1:initial=np.zeros(n,dtype=int)
    else:initial=KMeans(k,n_init=1,random_state=seed).fit_predict(embedding)
    response=np.full((n,k),.02/max(1,k));response[np.arange(n),initial]+=.98
    a=settings['LM_pseudocount'];b=settings['mixture_pseudocount'];curve=[];last=None;converged=False
    for iteration in range(settings['iterations']):
        counts=np.asarray(x.T@response).T.reshape(k,C,V)+a
        logp=np.log(counts)-np.log(counts.sum(axis=2,keepdims=True))
        if membership:
            proportions=np.zeros((G,k));np.add.at(proportions,group_ids,response);proportions+=b
            proportions/=proportions.sum(axis=1,keepdims=True);prior=proportions[group_ids]
        else:
            proportions=response.sum(axis=0)+b;proportions/=proportions.sum();prior=np.broadcast_to(proportions,(n,k))
        scores=np.asarray(x@logp.reshape(k,-1).T)+np.log(prior)
        norm=logsumexp(scores,axis=1);response=np.exp(scores-norm[:,None])
        objective=float(norm.sum()+a*logp.sum()+b*np.log(proportions).sum())
        if curve and objective<curve[-1]-1e-5:raise AssertionError('EM penalized objective decreased')
        curve.append(objective)
        if last is not None and abs(objective-last)<=settings['relative_tolerance']*max(1,abs(last)):
            converged=True;break
        last=objective
    return dict(logp=logp.reshape(k,-1),proportions=proportions,response=response,curve=curve,converged=converged,iterations=iteration+1)

def score(model,x,groups,membership,settings):
    likelihood=np.asarray(x@model['logp'].T);k=likelihood.shape[1]
    if not membership:
        score=likelihood+np.log(model['proportions']);norm=logsumexp(score,axis=1)
        return np.exp(score-norm[:,None]),norm
    # New lines start from a symmetric prior. A normalized prequential code
    # updates membership from PREVIOUS units only; the current/future word never
    # supplies its own mixture weight. This is soft-count filtering, not an
    # exact integral over the Dirichlet posterior.
    counts={};response=np.empty_like(likelihood);predictive=np.empty(len(groups));b=settings['mixture_pseudocount']
    for index,group in enumerate(groups):
        if group not in counts:counts[group]=np.full(k,b)
        prior=counts[group]/counts[group].sum();logits=likelihood[index]+np.log(prior)
        norm=logsumexp(logits);response[index]=np.exp(logits-norm);predictive[index]=norm
        counts[group]+=response[index]
    return response,predictive

def recovery(train_truth,train_response,test_truth,test_response):
    train_known=np.isfinite(train_truth)&((train_truth<=.1)|(train_truth>=.9))
    test_known=np.isfinite(test_truth)&((test_truth<=.1)|(test_truth>=.9))
    if len(set((test_truth[test_known]>=.5).astype(int)))<2 or len(set((train_truth[train_known]>=.5).astype(int)))<2:
        return dict(status='NOT_IDENTIFIABLE_AT_THIS_UNIT',eligible_test_units=int(test_known.sum()))
    mapping=[]
    for component in range(train_response.shape[1]):
        mass=[train_response[train_known&(train_truth<.5),component].sum(),train_response[train_known&(train_truth>=.5),component].sum()]
        mapping.append(int(np.argmax(mass)))
    prediction=np.array(mapping)[test_response.argmax(axis=1)]
    return dict(status='SCORED',balanced_accuracy=float(balanced_accuracy_score((test_truth[test_known]>=.5).astype(int),prediction[test_known])),
        ARI=float(adjusted_rand_score((test_truth[test_known]>=.5).astype(int),test_response.argmax(axis=1)[test_known])),
        eligible_test_units=int(test_known.sum()),excluded_mixed_or_unknown_units=int((~test_known).sum()),train_component_language_map=mapping)

def associations(selected,units,response,name,seed,permutations):
    # Same-unit line posteriors first; leaf aggregation protects calibration from
    # counting the many lines on one leaf as independent observations.
    by_line=defaultdict(list)
    for unit,prob in zip(units,response):by_line[unit['line_id']].append(prob)
    line_cluster={line:int(np.mean(values,axis=0).argmax()) for line,values in by_line.items()}
    output=[];rng=np.random.default_rng(seed)
    for target in ['section','currier_lang','hand_scribe']:
        if target=='hand_scribe' and name!='ZL_running':continue
        eligible=[r for r in selected if r['line_id'] in line_cluster and r.get(target) and (target!='currier_lang' or r[target] in ['A','B'])]
        if not eligible:continue
        truth=[r[target] for r in eligible];pred=[line_cluster[r['line_id']] for r in eligible]
        blocks=defaultdict(list)
        for r in eligible:
            match=re.match(r'f\d+',r['folio']);leaf=match[0] if match else r.get('source_group',r['folio']);blocks[leaf].append(r)
        leaf_truth=[];leaf_pred=[]
        for rs in blocks.values():
            labels={r[target] for r in rs}
            if len(labels)==1:leaf_truth.append(next(iter(labels)));leaf_pred.append(Counter(line_cluster[r['line_id']] for r in rs).most_common(1)[0][0])
        observed=float(adjusted_mutual_info_score(leaf_truth,leaf_pred)) if len(set(leaf_truth))>1 else None
        null=[float(adjusted_mutual_info_score(rng.permutation(leaf_truth),leaf_pred)) for _ in range(permutations)] if observed is not None else []
        output.append(dict(corpus=name,target=target,line_AMI=float(adjusted_mutual_info_score(truth,pred)),lines=len(eligible),
            pure_metadata_leaves=len(leaf_truth),leaf_AMI=observed,permutation_p=(1+sum(v>=observed for v in null))/(1+len(null)) if null else None,
            excluded_mixed_leaves=len(blocks)-len(leaf_truth),warning='unadjusted covarying metadata; no unique causal attribution'))
    return output

def run_one(name,method,output):
    settings=config()['mixture'];selected=corpus(name);assignment=split(name);meta=registry()[name]
    truth={r['line_id']:r for r in json.loads((ROOT/meta['truth_path']).read_text())} if meta.get('truth_path') else {}
    us,truth_values=unit_rows(selected,method,truth);parts=np.array([assignment[u['folio']] for u in us]);texts=[u['text'] for u in us]
    masks={p:parts==p for p in ['train','validation','test']}
    if any(m.sum()<3 for m in masks.values()):return [dict(corpus=name,method=method,status='NOT_ESTIMABLE',units=len(us))],[],[]
    extractor=CharFeatures([t for t,p in zip(texts,parts) if p=='train'],settings['context_order'])
    x,lengths=extractor.transform(texts);embedding=initialize_embeddings([texts[i] for i in np.flatnonzero(masks['train'])])
    groups=np.array([u['line_id'] for u in us]);results=[];assocs=[];predictions=[]
    for k in settings['components']:
        for seed in config()['seeds']:
            job=output/f'{name}-{method}-k{k}-s{seed}';job.mkdir(parents=True,exist_ok=True)
            if (job/'metrics.json').exists() and (job/'posteriors.npz').exists():
                result=json.loads((job/'metrics.json').read_text());saved=np.load(job/'posteriors.npz');test_response=saved['test'];train_response=saved['train']
            else:
                model=fit_em(x[masks['train']],groups[masks['train']],embedding,k,seed,extractor.V,extractor.C,settings,method!='line')
                test_response,test_ll=score(model,x[masks['test']],groups[masks['test']],method!='line',settings)
                valid_response,valid_ll=score(model,x[masks['validation']],groups[masks['validation']],method!='line',settings)
                train_response=model['response']
                result=dict(corpus=name,method=method,k=k,seed=seed,status='FITTED',converged=model['converged'],iterations=model['iterations'],
                    train_units=int(masks['train'].sum()),test_units=int(masks['test'].sum()),validation_units=int(masks['validation'].sum()),
                    test_bpc=float(-test_ll.sum()/lengths[masks['test']].sum()/math.log(2)),validation_bpc=float(-valid_ll.sum()/lengths[masks['validation']].sum()/math.log(2)),
                    component_occupancy=test_response.mean(axis=0).tolist(),curve=model['curve'],coding='EOS included; companion membership uses prior line units only, soft-count prequential filter')
                if truth:result['recovery']=recovery(truth_values[masks['train']],train_response,truth_values[masks['test']],test_response)
                dump(job/'metrics.json',result);np.savez_compressed(job/'posteriors.npz',test=test_response,train=train_response)
            results.append(result)
            test_units=[u for u,m in zip(us,masks['test']) if m]
            for u,prob in zip(test_units,test_response):predictions.append(dict(corpus=name,method=method,k=k,seed=seed,**u,component=int(prob.argmax()),probabilities=json.dumps(prob.tolist())))
            if k>1:
                current=associations(selected,test_units,test_response,name,seed,settings['permutations'])
                assocs.extend(dict(method=method,k=k,seed=seed,**r) for r in current)
    return results,assocs,predictions

def summarize(results,predictions):
    output=[]
    for name,method in sorted({(r['corpus'],r['method']) for r in results}):
        for k in [2,3]:
            rs=[r for r in results if r['corpus']==name and r['method']==method and r.get('k')==k]
            base=[r for r in results if r['corpus']==name and r['method']==method and r.get('k')==1]
            if not rs or not base:continue
            gains=[next(r['test_bpc'] for r in base if r['seed']==v['seed'])-v['test_bpc'] for v in rs]
            ps=[r for r in predictions if r['corpus']==name and r['method']==method and r['k']==k]
            labels={s:[r['component'] for r in ps if r['seed']==s] for s in config()['seeds']}
            stability=[adjusted_rand_score(labels[a],labels[b]) for a,b in itertools.combinations(config()['seeds'],2)]
            minimum=min(min(r['component_occupancy']) for r in rs);median=float(np.median(stability));mean=float(np.mean(gains));sd=float(np.std(gains,ddof=1))
            rec=[r.get('recovery',{}) for r in rs];qualified=[v for v in rec if v.get('balanced_accuracy',0)>=settings_qualification()['balanced_accuracy']]
            output.append(dict(corpus=name,method=method,k=k,gain_mean=mean,gain_sd=sd,median_seed_ARI=median,minimum_component_occupancy=minimum,
                split_emerges=mean>sd and minimum>=.01 and median>=.5,converged_seeds=sum(r['converged'] for r in rs),
                recovery_status='QUALIFIED' if len(qualified)>=4 and median>=.5 else 'NOT_QUALIFIED' if any('balanced_accuracy' in v for v in rec) else 'NO_APPLICABLE_SOURCE_TRUTH',
                recovery_balanced_accuracy_mean=float(np.mean([v['balanced_accuracy'] for v in rec if 'balanced_accuracy' in v])) if any('balanced_accuracy' in v for v in rec) else None))
    return output
def settings_qualification():return config()['mixture']['qualification']

def run():
    output=EXT/'runs/mixtures';output.mkdir(exist_ok=True);results=[];assocs=[];summary=[];qual=[]
    names=list(registry());first=[n for n in names if n.startswith('C14_') and not n.startswith('C14_labeltext_') or n.startswith('C14_labeltext_withlabels_')]
    names=first+[n for n in names if n not in first]
    sink=(EXT/'report/mixture_assignments.csv').open('w',encoding='utf-8',newline='');writer=None
    for index,name in enumerate(names):
        local_results=[];local_predictions=[]
        for method in config()['mixture']['methods']:
            progress('EM qualification first' if name in first else 'EM control/manuscript analysis',corpus=name,method=method,completed_corpora=index,total_corpora=len(names))
            r,a,p=run_one(name,method,output);results.extend(r);assocs.extend(a);local_results.extend(r);local_predictions.extend(p)
        current=summarize(local_results,local_predictions);summary.extend(current)
        if name in first:qual.extend(current);table(EXT/'report/C14_mixture_qualification.csv',qual)
        if local_predictions:
            if writer is None:writer=csv.DictWriter(sink,fieldnames=list(local_predictions[0]));writer.writeheader()
            writer.writerows(local_predictions);sink.flush()
        table(EXT/'report/mixture_results.csv',[{k:v for k,v in r.items() if k not in ['curve','component_occupancy','recovery']} for r in results])
        table(EXT/'report/mixture_associations.csv',assocs);table(EXT/'report/mixture_summary.csv',summary)
    sink.close()
if __name__=='__main__':run()
