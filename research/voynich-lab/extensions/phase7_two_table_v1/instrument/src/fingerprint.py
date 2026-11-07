"""Control-fitted PCA/ranking and source-block-held-out chunk classification.

Classifier probabilities describe membership among these specific controls;
they are not calibrated probabilities of the manuscript's historical generator.
"""
from src.train import *
sys.path.insert(0,str(ROOT/'.analysis-runtime'))
from src.extend_phase3 import read
from src.metrics import measure
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,balanced_accuracy_score,log_loss,confusion_matrix

BASE_FEATURES=['h0','h1','h2','zipf_slope','zipf_r2','word_hapax_ratio','word_length_mean','word_length_variance',
    'word_length_skewness','word_length_excess_kurtosis','mi_glyph_line_word_edge','mi_glyph_word_edge',
    'consecutive_identical_rate','consecutive_edit1_rate']

def numeric(r,k):return float(r[k])

def full_fingerprint():
    master=read(ROOT/'report/master_metrics_extended.csv');models=read(ROOT/'report/model_summary.csv');gains=read(ROOT/'report/line_position_gain.csv')
    names=['ZL_running','LSI_H_running']+[f'C{i}_{v}' for i in range(1,14) for v in ['clean','noise']]
    names+=['ZL_running_A','ZL_running_B','LSI_H_running_A','LSI_H_running_B']
    records=[];vectors=[]
    for name in names:
        t1=next(r for r in master if r['corpus']==name and r['tokenization']=='T1')
        d={k:numeric(t1,k) for k in BASE_FEATURES}
        for scheme in ['T2','T3']:
            r=next(r for r in master if r['corpus']==name and r['tokenization']==scheme)
            for key in ['h0','h1','h2']:d[scheme+'_'+key]=numeric(r,key)
        for scheme in ['T1','T2','T3']:
            for arch in ['lstm','transformer']:
                r=next(r for r in models if r['corpus']==name and r['tokenization']==scheme and r['architecture']==arch and r['with_position']=='False')
                g=next(r for r in gains if r['corpus']==name and r['tokenization']==scheme and r['architecture']==arch)
                d[f'{scheme}_{arch}_baseline_bpc']=numeric(r,'test_bpc_mean')
                d[f'{scheme}_{arch}_position_gain']=numeric(g,'gain_mean')
        records.append(dict(corpus=name,**d));vectors.append(list(d.values()))
    x=np.array(vectors);control=np.array([n.startswith('C') for n in names])
    scaler=StandardScaler().fit(x[control]);z=scaler.transform(x);pca=PCA(2).fit(z[control]);xy=pca.transform(z)
    table(ROOT/'report/fingerprint_features.csv',records)
    coordinates=[dict(corpus=n,PC1=float(a),PC2=float(b)) for n,(a,b) in zip(names,xy)]
    table(ROOT/'report/fingerprint_pca.csv',coordinates)
    rankings=[]
    for i,name in enumerate(names):
        if name.startswith('C'):continue
        distances=[(float(np.linalg.norm(z[i]-z[j])),n) for j,n in enumerate(names) if n.startswith('C')]
        for rank,(distance,other) in enumerate(sorted(distances),1):rankings.append(dict(query=name,rank=rank,control=other,standardized_distance=distance))
    table(ROOT/'report/nearest_controls.csv',rankings)
    dump(ROOT/'report/fingerprint_pca_metadata.json',dict(feature_names=list(records[0])[1:],
        explained_variance_ratio=pca.explained_variance_ratio_.tolist(),scaler_fit='controls_only',PCA_fit='controls_only',
        interpretation='Euclidean similarity of these controls/settings; not mechanism identification'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(15,7),layout='constrained',gridspec_kw={'width_ratios':[1.6,1]})
    for ax in axes:
        for name,(a,b) in zip(names,xy):
            ax.scatter(a,b,c='#15637d' if name.startswith('C') else '#b03b38',marker='o' if name.startswith('C') else '*',s=30 if name.startswith('C') else 95)
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})');ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})');ax.grid(alpha=.15)
    axes[0].margins(x=.15,y=.12);axes[0].set_title('All controls; c=clean, n=noise')
    query=xy[~control];axes[1].set_xlim(query[:,0].min()-.9,query[:,0].max()+.9)
    axes[1].set_ylim(query[:,1].min()-.8,query[:,1].max()+.8);axes[1].set_title('Query-region detail (same coordinates)')
    fig.suptitle('Control-fitted PCA — full-space distances define rankings; proximity is descriptive')
    fig.canvas.draw()
    for ax in axes:clear_labels(ax,names,xy)
    fig.savefig(ROOT/'report/fingerprint_pca.png',dpi=160);plt.close(fig)
    return rankings

def clear_labels(ax,names,xy):
    """Deterministic text-only collision avoidance; point coordinates never move."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.transforms import Bbox
    renderer=ax.figure.canvas.get_renderer();bounds=ax.get_window_extent();used=[]
    for name,(x,y) in zip(names,xy):
        if not (ax.get_xlim()[0]<=x<=ax.get_xlim()[1] and ax.get_ylim()[0]<=y<=ax.get_ylim()[1]):continue
        label=name.replace('_clean','c').replace('_noise','n').replace('ZL_running','ZL').replace('LSI_H_running','H').replace('_','-')
        w,h,_=renderer.get_text_width_height_descent(label,FontProperties(size=8),False)
        origin=ax.transData.transform((x,y));chosen=None
        for radius in range(0,145,12):
            offsets=[(8+radius,8),(8,8+radius),(8,-h-8-radius),(-w-8-radius,8),(-w-8-radius,-h-8),(8+radius,-h-8-radius)]
            for dx,dy in offsets:
                px,py=origin[0]+dx,origin[1]+dy;box=Bbox.from_bounds(px-3,py-3,w+6,h+9)
                if box.x0<bounds.x0+3 or box.x1>bounds.x1-3 or box.y0<bounds.y0+3 or box.y1>bounds.y1-3:continue
                if not any(box.overlaps(other) for other in used):chosen=(px,py,box);break
            if chosen is not None:break
        if chosen is None:chosen=(origin[0]+8,origin[1]+8,Bbox.from_bounds(origin[0]+5,origin[1]+5,w+6,h+9))
        px,py,box=chosen;used.append(box);tx,ty=ax.transData.inverted().transform((px,py))
        ax.annotate('',xy=(x,y),xytext=(tx,ty),arrowprops=dict(arrowstyle='-',color='#aaaaaa',lw=.5),in_layout=False)
        ax.text(tx,ty,label,fontsize=8,va='bottom',in_layout=False)

def chunks(rows,primary_template=None):
    groups=defaultdict(list);position=0
    for i,r in enumerate(rows):
        group=position//2000;groups[group].append(r)
        position+=len(primary_template[i]['text_eva'].split()) if primary_template is not None else len(r['text_eva'].split())
    return [(i,rs) for i,rs in sorted(groups.items()) if sum(len(r['text_eva'].split()) for r in rs)>=1600]

def chunk_features(name,rows,reference,primary_template=None):
    p3=json.loads((ROOT/'configs/phase3.json').read_text());result=[]
    load=lambda v:read(v) if isinstance(v,Path) else v
    baseline={(r['line_id'],int(r['word_index'])):float(r['bits']) for r in load(reference[name,False])}
    positioned={(r['line_id'],int(r['word_index'])):float(r['bits']) for r in load(reference[name,True])}
    for group,rs in chunks(rows,primary_template):
        m,_=measure(rs,'T1',p3['clusters'],None)
        d={k:m[k] for k in BASE_FEATURES};b=p=chars=0
        for r in rs:
            for wi,w in enumerate(r['text_eva'].split()):
                key=r['line_id'],wi;b+=baseline[key];p+=positioned[key];chars+=len(w)
        d['crossfit_lexical_bpc']=b/chars;d['crossfit_position_gain_bpc']=(b-p)/chars
        result.append(dict(corpus=name,source_block=group,words=m['words'],**d))
    return result

def classify(reference):
    allrows=[];queries=[];membership=[];primary=read_rows('ZL_running')
    for i in range(1,14):
        template=primary if i!=13 else read_rows('C13_clean')
        for version in ['clean','noise']:
            name=f'C{i}_{version}';rows=read_rows(name)
            for block,selected in chunks(rows,template):
                membership.extend(dict(corpus=name,line_id=r['line_id'],source_block=block) for r in selected)
            current=chunk_features(name,rows,reference,primary_template=template)
            for r in current:r['class']=f'C{i}'
            allrows.extend(current)
    for name in ['ZL_running','LSI_H_running']:
        rows=read_rows(name)
        queries.extend(chunk_features(name,rows,reference))
        for lang in ['A','B']:
            selected=[r for r in rows if r['currier_lang']==lang]
            features=chunk_features(name,selected,reference)
            for r in features:r['corpus']=name+'_'+lang
            queries.extend(features)
    table(ROOT/'report/classifier_chunks.csv',allrows)
    table(ROOT/'report/classifier_chunk_membership.csv',membership)
    table(ROOT/'report/classifier_query_chunks.csv',queries)
    keys=BASE_FEATURES+['crossfit_lexical_bpc','crossfit_position_gain_bpc']
    x=np.array([[r[k] for k in keys] for r in allrows]);y=np.array([r['class'] for r in allrows]);groups=np.array([r['source_block'] for r in allrows])
    p5=json.loads((ROOT/'configs/phase5.json').read_text());predictions=[];chosen=[]
    unique=sorted(set(groups))
    for index,heldout in enumerate(unique):
        test=groups==heldout;validation=groups==unique[(index+1)%len(unique)];train=~(test|validation)
        scaler=StandardScaler().fit(x[train]);z=scaler.transform(x);options=[]
        for c in p5['classifier_C_candidates']:
            model=LogisticRegression(C=c,max_iter=2000,random_state=1729).fit(z[train],y[train])
            options.append((accuracy_score(y[validation],model.predict(z[validation])),c,model))
        score,c,model=max(options,key=lambda v:(v[0],-v[1]));chosen.append(c)
        probabilities=model.predict_proba(z[test]);pred=model.predict(z[test]);indices=np.flatnonzero(test)
        majority=Counter(y[train]).most_common(1)[0][0]
        for j,original_index in enumerate(indices):
            predictions.append(dict(corpus=allrows[original_index]['corpus'],source_block=int(heldout),truth=y[original_index],
                prediction=pred[j],confidence=float(probabilities[j].max()),correct=pred[j]==y[original_index],
                majority_baseline_correct=majority==y[original_index],selected_C=c,
                probabilities=json.dumps(dict(zip(model.classes_,probabilities[j].tolist())))))
    table(ROOT/'report/classifier_heldout_predictions.csv',predictions)
    final_c=sorted(Counter(chosen),key=lambda c:(-Counter(chosen)[c],c))[0]
    scaler=StandardScaler().fit(x);model=LogisticRegression(C=final_c,max_iter=2000,random_state=1729).fit(scaler.transform(x),y)
    q=np.array([[r[k] for k in keys] for r in queries]);prob=model.predict_proba(scaler.transform(q));outputs=[]
    for r,ps in zip(queries,prob):
        ranked=sorted(zip(model.classes_,ps),key=lambda a:-a[1]);outputs.append(dict(corpus=r['corpus'],source_block=r['source_block'],words=r['words'],
            assigned_control=ranked[0][0],confidence=float(ranked[0][1]),probabilities=json.dumps(dict(zip(model.classes_,ps.tolist())))))
    table(ROOT/'report/classifier_voynich_assignments.csv',outputs)
    result=dict(leave_out_unit='source word block index shared across C1 derivatives, clean/noise, and other corpora',
        classifier_features=keys,model_features='one-seed five-fold leaf-cross-fitted LSTM T1 lexical BPC and causal-position gain',
        accuracy=float(np.mean([r['correct'] for r in predictions])),
        balanced_accuracy=float(balanced_accuracy_score([r['truth'] for r in predictions],[r['prediction'] for r in predictions])),
        majority_baseline=float(np.mean([r['majority_baseline_correct'] for r in predictions])),test_chunks=len(predictions),
        final_C=final_c,classes=model.classes_.tolist(),confidence_warning='uncalibrated conditional control-class probabilities, not historical-generator probabilities')
    dump(ROOT/'report/classifier_result.json',result)
    table(ROOT/'report/classifier_confusion.csv',[dict(truth=a,**{b:int(n) for b,n in zip(model.classes_,row)}) for a,row in zip(model.classes_,confusion_matrix(
        [r['truth'] for r in predictions],[r['prediction'] for r in predictions],labels=model.classes_))])
    return result,outputs
