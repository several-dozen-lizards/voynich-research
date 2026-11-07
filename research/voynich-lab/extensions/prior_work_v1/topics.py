"""Topic/section probes within a single hand×Currier cell, with fake-label floors."""
from collections import Counter,defaultdict
from .common import *
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,balanced_accuracy_score,adjusted_mutual_info_score
from threadpoolctl import threadpool_limits

def template():
    selected=corpus('ZL_running');allocation=split('ZL_running');pages={}
    for r in selected:
        if r.get('hand_scribe') and r.get('currier_lang') in ['A','B']:
            pages[r['folio']]=dict(cell=r['hand_scribe']+'_'+r['currier_lang'],section=r['section'],split=allocation[r['folio']])
    distribution=Counter(p['cell'] for p in pages.values() if p['split']=='train')
    sections=defaultdict(Counter)
    for p in pages.values():
        if p['split']=='train':sections[p['cell']][p['section']]+=1
    return pages,distribution,sections

def cell_rows(name):
    pages,distribution,sections=template();selected=corpus(name);control=name.startswith('C');result=[]
    for r in selected:
        if not control:
            if r.get('currier_lang') not in ['A','B'] or not r.get('hand_scribe'):continue
            cell=r['hand_scribe']+'_'+r['currier_lang'];kind='real ZL hand x Currier'
        elif r['folio'] in pages:cell=pages[r['folio']]['cell'];kind='borrowed layout cell, not real hand/language'
        else:
            keys=sorted(distribution);cell=rng_for(1729,'fake_cell:'+name+':'+r['folio']).choices(keys,weights=[distribution[k] for k in keys],k=1)[0];kind='independent fake source-page cell'
        result.append({**r,'analysis_cell':cell,'cell_kind':kind})
    return result,sections

def fit_probe(features,labels,parts,candidates):
    train=parts=='train';valid=parts=='validation';test=parts=='test';labels=np.array(labels)
    if min(train.sum(),valid.sum(),test.sum())==0 or len(set(labels[train]))<2:
        return dict(status='NOT_ESTIMABLE',train_lines=int(train.sum()),validation_lines=int(valid.sum()),test_lines=int(test.sum()),train_classes=json.dumps(dict(Counter(labels[train]))),test_classes=json.dumps(dict(Counter(labels[test]))))
    models=[]
    for c in candidates:
        model=LogisticRegression(C=c,max_iter=1000,random_state=1729).fit(features[train],labels[train])
        models.append((accuracy_score(labels[valid],model.predict(features[valid])),c,model))
    _,c,model=max(models,key=lambda r:(r[0],-r[1]));prediction=model.predict(features[test]);majority=Counter(labels[train]).most_common(1)[0][0]
    return dict(status='SCORED',accuracy=float(accuracy_score(labels[test],prediction)),balanced_accuracy=float(balanced_accuracy_score(labels[test],prediction)),
        majority_baseline=float(np.mean(labels[test]==majority)),selected_C=c,train_lines=int(train.sum()),validation_lines=int(valid.sum()),test_lines=int(test.sum()),
        train_classes=json.dumps(dict(Counter(labels[train]))),test_classes=json.dumps(dict(Counter(labels[test]))))

def topic_association(current,parts,features,labels,seed,permutations):
    groups=defaultdict(list)
    for i,r in enumerate(current):
        if parts[i]!='test':continue
        match=re.match(r'f\d+',r['folio']);leaf=match[0] if match else r.get('source_group') or re.sub(r'[rv]$','',r['folio'])
        groups[leaf].append(i)
    truth=[];pred=[]
    for indices in groups.values():
        values={labels[i] for i in indices}
        if len(values)==1:truth.append(next(iter(values)));pred.append(int(features[indices].mean(axis=0).argmax()))
    if len(set(truth))<2:return dict(topic_leaf_AMI=None,topic_leaf_permutation_p=None,topic_pure_leaves=len(truth))
    observed=float(adjusted_mutual_info_score(truth,pred));rng=np.random.default_rng(seed)
    null=[adjusted_mutual_info_score(rng.permutation(truth),pred) for _ in range(permutations)]
    return dict(topic_leaf_AMI=observed,topic_leaf_permutation_p=(1+sum(v>=observed for v in null))/(1+len(null)),topic_pure_leaves=len(truth))

def run():
    settings=config()['topics'];names=['ZL_running']+[n for n,m in registry().items() if n.startswith('C') and not m.get('analysis_only')]
    folder=EXT/'runs/topics';folder.mkdir(exist_ok=True)
    registration=dict(config_sha256=sha(EXT/'config.json'),code_sha256=sha(Path(__file__)),fake_replicates=20,replicate_seed_rule='cycle through five registered seeds;20 total independent fake assignments, not100')
    dump(folder/'REGISTRATION.json',registration);output=[];words=[]
    with threadpool_limits(limits=2):
      for index,name in enumerate(names):
        selected,distributions=cell_rows(name);allocation=split(name);control=name.startswith('C')
        for cell in sorted({r['analysis_cell'] for r in selected}):
            current=[r for r in selected if r['analysis_cell']==cell];parts=np.array([allocation[r['folio']] for r in current]);texts=[r['text_eva'] for r in current]
            train=parts=='train';counts=Counter(parts);seed_features={}
            if not train.any() or not (parts=='test').any() or not (parts=='validation').any():
                output.append(dict(corpus=name,cell=cell,label_kind='fake' if control else 'real',status='NOT_ESTIMABLE',reason='missing split',support=json.dumps(counts)));continue
            try:
                cv=CountVectorizer(token_pattern=r'\S+',lowercase=False,min_df=2,max_features=settings['vocabulary_cap'])
                cv.fit([t for t,m in zip(texts,train) if m]);count_features=cv.transform(texts)
                tf=TfidfVectorizer(analyzer='char',ngram_range=(1,3),lowercase=False,min_df=2,max_features=settings['vocabulary_cap'])
                tf.fit([t for t,m in zip(texts,train) if m]);char_features=tf.transform(texts)
            except ValueError as error:
                output.append(dict(corpus=name,cell=cell,status='NOT_ESTIMABLE',reason=str(error),label_kind='fake' if control else 'real'));continue
            repeats=range(settings['fake_label_replicates']) if control else range(len(config()['seeds']))
            for replicate in repeats:
                seed=config()['seeds'][replicate%len(config()['seeds'])]
                cache=folder/f'{name}-{cell}-s{seed}.npz'
                if seed not in seed_features:
                    if cache.exists():
                        topic_features=np.load(cache)['features']
                        words.extend(json.loads(cache.with_suffix('.json').read_text()))
                    else:
                        lda=LatentDirichletAllocation(n_components=settings['topics'],max_iter=settings['iterations'],learning_method='batch',random_state=seed)
                        lda.fit(count_features[train]);topic_features=lda.transform(count_features)
                        np.savez_compressed(cache,features=topic_features)
                        vocabulary=cv.get_feature_names_out()
                        descriptions=[]
                        for topic,weights in enumerate(lda.components_):
                            terms=[vocabulary[i] for i in np.argsort(-weights)[:15]]
                            descriptions.append(dict(corpus=name,cell=cell,seed=seed,topic=topic,top_strings=json.dumps(terms),meaning='uninterpreted token strings'))
                        dump(cache.with_suffix('.json'),descriptions);words.extend(descriptions)
                    seed_features[seed]=topic_features
                topic_features=seed_features[seed]
                if control:
                    distribution=distributions.get(cell) or Counter(r['section'] for r in corpus('ZL_running') if r.get('section'))
                    classes=sorted(distribution);by_page={p:rng_for(1729,f'fake_section:{cell}:{replicate}:{p}').choices(classes,weights=[distribution[c] for c in classes],k=1)[0] for p in {r['folio'] for r in current}}
                    labels=[by_page[r['folio']] for r in current]
                else:labels=[r.get('section') or 'unknown' for r in current]
                association=topic_association(current,parts,topic_features,labels,seed+replicate,settings['permutations'])
                for method,features in [('LDA_topics',topic_features),('character_TFIDF',char_features)]:
                    result=fit_probe(features,labels,parts,settings['probe_C'])
                    output.append(dict(corpus=name,cell=cell,cell_kind=current[0]['cell_kind'],method=method,seed=seed,replicate=replicate,
                        label_kind='independent_fake_page_section' if control else 'source_section',size_mismatch=name.startswith(('C13','C17')),**association,**result))
        table(EXT/'report/within_cell_section_probes.csv',output);table(EXT/'report/within_cell_topic_strings.csv',words)
        progress('within-cell topics and section probes',completed=index+1,total=len(names),corpus=name)
    summary=[]
    for name,cell,method in sorted({(r['corpus'],r.get('cell'),r.get('method')) for r in output if r.get('status')=='SCORED'}):
        rs=[r for r in output if r.get('status')=='SCORED' and (r['corpus'],r['cell'],r['method'])==(name,cell,method)]
        summary.append(dict(corpus=name,cell=cell,method=method,replicates=len(rs),label_kind=rs[0]['label_kind'],
            mean_accuracy=float(np.mean([r['accuracy'] for r in rs])),sd_accuracy=float(np.std([r['accuracy'] for r in rs],ddof=1)) if len(rs)>1 else None,
            mean_majority=float(np.mean([r['majority_baseline'] for r in rs])),mean_balanced_accuracy=float(np.mean([r['balanced_accuracy'] for r in rs]))))
    table(EXT/'report/within_cell_probe_summary.csv',summary)
if __name__=='__main__':run()
