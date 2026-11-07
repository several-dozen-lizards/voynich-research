"""Held-out-leaf linear probes; representations never receive target metadata."""
from src.train import *
sys.path.insert(0,str(ROOT/'.analysis-runtime'))
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,balanced_accuracy_score

@torch.no_grad()
def representations(model,rows,spec,config):
    if model.with_position:raise ValueError('Probe target leakage: position-conditioned model forbidden')
    width=config['context_length'];lookup={t:i for i,t in enumerate(spec['vocabulary'])}
    clusters=json.loads((ROOT/'configs/phase3.json').read_text())['clusters']
    blocks=[];owners=[]
    for i,r in enumerate(rows):
        tokens=tokenize_line(r['text_eva'],spec['tokenization'],clusters,spec['bpe_merges'])
        ids=[lookup.get(t,1) for t in tokens];x=[2]+ids
        for start in range(0,len(x),width):
            part=x[start:start+width];blocks.append(part+[0]*(width-len(part)));owners.append((i,len(part)))
    features=np.zeros((len(rows),config['embedding_dim']),dtype=np.float64);support=np.zeros(len(rows))
    device=next(model.parameters()).device
    for start in range(0,len(blocks),config['batch_size']):
        batch=torch.tensor(blocks[start:start+config['batch_size']],device=device)
        with autocast():_,hidden=model(batch,torch.zeros_like(batch),return_hidden=True)
        hidden=hidden.float().cpu().numpy()
        for j,(owner,length) in enumerate(owners[start:start+len(batch)]):
            features[owner]+=hidden[j,:length].sum(axis=0);support[owner]+=length
    return features/np.maximum(support[:,None],1)

def fit_probe(features,labels,groups,candidates):
    eligible=np.array([label is not None and label!='' for label in labels])
    labels=np.array([str(x) for x in labels]);groups=np.array(groups)
    train=eligible&(groups=='train');valid=eligible&(groups=='validation');test=eligible&(groups=='test')
    if min(train.sum(),valid.sum(),test.sum())==0 or len(set(labels[train]))<2:
        return dict(status='NOT_ESTIMABLE',train=int(train.sum()),validation=int(valid.sum()),test=int(test.sum()))
    scaler=StandardScaler().fit(features[train]);x=scaler.transform(features)
    choices=[]
    for c in candidates:
        model=LogisticRegression(C=c,max_iter=2000,solver='lbfgs',random_state=1729).fit(x[train],labels[train])
        choices.append((accuracy_score(labels[valid],model.predict(x[valid])),c,model))
    best=max(choices,key=lambda v:(v[0],-v[1]));prediction=best[2].predict(x[test])
    majority=Counter(labels[train]).most_common(1)[0][0]
    return dict(status='PASS',train=int(train.sum()),validation=int(valid.sum()),test=int(test.sum()),
        accuracy=float(accuracy_score(labels[test],prediction)),balanced_accuracy=float(balanced_accuracy_score(labels[test],prediction)),
        majority_baseline=float(np.mean(labels[test]==majority)),selected_C=best[1],
        train_classes=json.dumps(dict(Counter(labels[train]))),test_classes=json.dumps(dict(Counter(labels[test]))))

def run(experiment,config):
    runs=read_model_runs();targets=[]
    p5=json.loads((ROOT/'configs/phase5.json').read_text())
    # Select baseline architecture/scheme by mean validation BPC, never probe test accuracy.
    names=['ZL_running','LSI_H_running']+[f'C{i}_{v}' for i in range(1,14) for v in ['clean','noise']]
    zl_rows=read_rows('ZL_running');zl_split=split_for('ZL_running');fake_distributions={}
    for target in ['section','currier_lang']:
        page_labels={r['folio']:r.get(target) for r in zl_rows if zl_split[r['folio']]=='train' and r.get(target)}
        fake_distributions[target]=Counter(page_labels.values())
    for name in names:
        group=defaultdict(list)
        for r in runs:
            if r['corpus']==name and not r['with_position']:group[r['architecture'],r['tokenization']].append(r)
        key=min(group,key=lambda k:np.mean([r['validation_bpc_with_escape'] for r in group[k]]))
        selected=next(r for r in group[key] if r['seed']==config['seeds'][0])
        model,spec=load_model(ROOT/selected['run_dir']/'model.pt',config)
        rows=read_rows(name);split=split_for(name);features=representations(model,rows,spec,config)
        np.savez_compressed(experiment/f'probe_features_{name}.npz',features=features)
        groups=[split[r['folio']] for r in rows]
        for target in ['section','currier_lang']+(['hand_scribe','is_para_start'] if name=='ZL_running' else []):
            if name.startswith('C'):
                # Independent random PAGE labels; page-held-out scoring prevents page lookup.
                distribution=fake_distributions[target];classes=sorted(distribution)
                labels_by_page={p:random.Random(int.from_bytes(hashlib.sha256(f'1729:{name}:{target}:{p}'.encode()).digest()[:8],'big')).choices(
                    classes,weights=[distribution[c] for c in classes],k=1)[0] for p in split}
                labels=[labels_by_page[r['folio']] for r in rows];kind='independent_fake_page_labels'
            else:
                labels=[r.get(target) for r in rows]
                if target=='currier_lang':labels=[v if v in ['A','B'] else None for v in labels]
                kind='source_metadata'
            result=fit_probe(features,labels,groups,p5['probe_C_candidates'])
            targets.append(dict(corpus=name,target=target,label_kind=kind,representation_architecture=spec['architecture'],
                representation_tokenization=spec['tokenization'],model_seed=config['seeds'][0],**result))
        del model
    table(ROOT/'report/probes.csv',targets)
    return targets

def read_model_runs():
    progress=json.loads((ROOT/'report/phase4_progress.json').read_text())
    return [json.loads(p.read_text()) for p in Path(progress['experiment']).glob('*/metrics.json')]

def geometry(config):
    from src.parse_ivtff import edit_distance
    outputs=[];examples=[]
    p5=json.loads((ROOT/'configs/phase5.json').read_text())
    for result in read_model_runs():
        if result['corpus'] not in p5['geometry_corpora'] or result['tokenization']!='T3' or result['with_position']:continue
        job=ROOT/result['run_dir'];spec=json.loads((job/'config.json').read_text())
        embedding=np.load(job/'embeddings.npz')['embedding']
        rows=read_rows(result['corpus']);split=split_for(result['corpus'])
        counts=Counter(w for r in rows if split[r['folio']]=='train' for w in r['text_eva'].split())
        ids=[i for i,w in enumerate(spec['vocabulary']) if i>=3 and counts[w]>=3]
        ids.sort(key=lambda i:(-counts[spec['vocabulary'][i]],spec['vocabulary'][i]))
        matrix=embedding[ids];matrix=matrix/np.maximum(np.linalg.norm(matrix,axis=1,keepdims=True),1e-12)
        queries=min(p5['geometry_top_words'],len(ids));cosine=matrix[:queries]@matrix.T
        for i in range(queries):cosine[i,i]=-np.inf
        nearest=np.argsort(-cosine,axis=1)[:,:p5['geometry_neighbors']]
        count=edit=stem=intersection=randedit=randstem=0;rng=random.Random(result['seed'])
        for i in range(queries):
            w=spec['vocabulary'][ids[i]]
            for j in nearest[i]:
                v=spec['vocabulary'][ids[int(j)]];prefix=len(os.path.commonprefix([w,v]))
                isedit=edit_distance(w,v)==1;isstem=prefix>=3 and prefix>=min(len(w),len(v))/2
                count+=1;edit+=isedit;stem+=isstem;intersection+=isedit and isstem
                candidates=[k for k in range(len(ids)) if k!=i and abs(len(spec['vocabulary'][ids[k]])-len(v))<=1]
                k=rng.choice(candidates or [k for k in range(len(ids)) if k!=i]);u=spec['vocabulary'][ids[k]]
                randedit+=edit_distance(w,u)==1;p=len(os.path.commonprefix([w,u]));randstem+=p>=3 and p>=min(len(w),len(u))/2
                if result['seed']==config['seeds'][0] and i<20:
                    examples.append(dict(corpus=result['corpus'],architecture=result['architecture'],word=w,neighbor=v,
                        cosine=float(cosine[i,j]),edit1=isedit,prefix_family=isstem))
        outputs.append(dict(corpus=result['corpus'],architecture=result['architecture'],seed=result['seed'],pairs=count,
            edit1_fraction=edit/count,prefix_family_fraction=stem/count,both_fraction=intersection/count,
            length_matched_random_edit1_fraction=randedit/count,length_matched_random_prefix_fraction=randstem/count))
    table(ROOT/'report/embedding_geometry.csv',outputs);table(ROOT/'report/embedding_neighbor_examples.csv',examples)
    return outputs
