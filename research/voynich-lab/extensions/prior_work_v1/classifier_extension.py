"""Phase 6 classifier, preserving the accepted Phase 5 classifier and features.

All new control lexical scores are five-fold leaf cross-fits. Source ancestry
purges shared plaintext blocks across differently respaced encodings. No query
manuscript data selects scaler, class weights, or regularization.
"""
from collections import Counter,defaultdict
from .common import *
import numpy as np
from src import surprise
from src.fingerprint import BASE_FEATURES,chunks,chunk_features
from src.metrics import measure
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,balanced_accuracy_score
from threadpoolctl import threadpool_limits

FOLDER=EXT/'runs/classifier';FOLDER.mkdir(exist_ok=True)
OLD=ROOT/'runs/phase5-c2f38fa45d6b'

def names():
    return [n for n,m in registry().items() if not m.get('analysis_only') and n.startswith('C') and n not in ['C8_clean','C8_noise']]

def references():
    cfg=json.loads((ROOT/'configs/phase4.json').read_text());out={};surprise.read_rows=corpus
    for name in ['ZL_running','LSI_H_running']+names():
        for pos in [False,True]:
            target=OLD/f'reference_{name}_p{int(pos)}_words.csv'
            if not target.exists():
                target=FOLDER/f'reference_{name}_p{int(pos)}_words.csv'
                if not target.exists():
                    ws,ls,labs=surprise.crossfit(name,'lstm','T1',pos,cfg,FOLDER/'crossfit',f'{name}-p{int(pos)}')
                    table(target,ws);table(target.with_name(target.name.replace('_words','_lines')),ls)
            out[name,pos]=target
        progress('Phase 6 classifier cross-fits',corpus=name)
    dump(FOLDER/'REFERENCE_RECEIPT.json',{f'{n}:p{int(p)}':dict(path=str(v.relative_to(ROOT)),sha256=sha(v)) for (n,p),v in out.items()})
    return out

def ancestry(name):
    """Conservative line-level origins; noise cannot move text between lines."""
    clean_name=name.rsplit('_',1)[0]+'_clean';rs=corpus(clean_name);family=registry()[name]['family'];word_origins=[]
    if family=='C14' and not name.startswith('C14_labeltext_'):
        truth=json.loads((ROOT/registry()[clean_name]['truth_path']).read_text());p=[0,0]
        for r in truth:
            for s in r['word_sources']:
                word_origins.append({f'C{1 if s==0 else 3}:{p[s]//2000}'});p[s]+=1
    elif family=='C15':
        from .controls import naibbe_module
        language='C1' if '_Latin_' in name else 'C2';cfg=json.loads((ROOT/'configs/phase3.json').read_text())
        words,_=load_words(cfg['source_slices'][language],34509);mod=naibbe_module(1729);units=[];original=mod.respace_plaintext
        def capture(*a,**kw):
            v=original(*a,**kw);units.extend(v);return v
        mod.respace_plaintext=capture
        encrypted=mod.encrypt_naibbe(mod.clean_line(' '.join(words)),mod.naibbe_tables,mod.placeholder_to_glyph,use_78='_78_' in name)
        native=rows(ROOT/registry()[clean_name]['native_path']);expected=[w for r in native for w in r['text_eva'].split()]
        assert encrypted[:len(expected)]==expected
        chars=[f'{language}:{i//2000}' for i,w in enumerate(words) for _ in mod.clean_line(w)]
        offset=0
        for unit in units[:len(expected)]:
            word_origins.append(set(chars[offset:offset+len(unit)]));offset+=len(unit)
    else:
        source='C1' if family in ['C1','C4','C5','C6','C7','C12','C18'] or name.startswith(('C16_Latin_','C14_labeltext_')) else 'C2' if family=='C2' else 'C3' if family=='C3' else 'WLC' if name.startswith('C16_Hebrew_') else family
        word_origins=[{f'{source}:{i//2000}'} for i in range(sum(len(r['text_eva'].split()) for r in rs))]
    result={};offset=0
    for r in rs:
        n=len(r['text_eva'].split())
        result[r['line_id']]={f'C17:writer:{r["folio"]}'} if family=='C17' else set().union(*word_origins[offset:offset+n])
        offset+=n
    assert offset==len(word_origins)
    return result

def selected_chunks(name,rs):
    clean=corpus(name.rsplit('_',1)[0]+'_clean')
    if not name.startswith('C17_'):return chunks(rs,clean)
    # Whole writers are indivisible; pool adjacent complete writers until >=1600.
    writers=defaultdict(list)
    for r in rs:writers[r['folio']].append(r)
    output=[];batch=[];n=0
    for selected in writers.values():
        batch.extend(selected);n+=sum(len(r['text_eva'].split()) for r in selected)
        if n>=1600:output.append((len(output),batch));batch=[];n=0
    if batch and output:output[-1]=(output[-1][0],output[-1][1]+batch)
    return output

def features(name,refs):
    cache=FOLDER/(name+'_features.json')
    if cache.exists():return json.loads(cache.read_text())
    rs=corpus(name);origins=ancestry(name);p3=json.loads((ROOT/'configs/phase3.json').read_text());scores=[]
    for pos in [False,True]:scores.append({(r['line_id'],int(r['word_index'])):float(r['bits']) for r in read(refs[name,pos])})
    result=[]
    for block,selected in selected_chunks(name,rs):
        m,_=measure(selected,'T1',p3['clusters'],None);d={k:m[k] for k in BASE_FEATURES};bits=[0.,0.];chars=0
        for r in selected:
            for wi,w in enumerate(r['text_eva'].split()):
                for p in range(2):bits[p]+=scores[p][r['line_id'],wi]
                chars+=len(w)
        result.append(dict(corpus=name,source_block=block,words=m['words'],**d,crossfit_lexical_bpc=bits[0]/chars,
            crossfit_position_gain_bpc=(bits[0]-bits[1])/chars,ancestry=sorted(set().union(*(origins[r['line_id']] for r in selected))),
            **{'class':registry()[name]['family']}))
    dump(cache,result);return result

def classify(refs):
    records=[r for name in names() for r in features(name,refs)];queries=[]
    for name in ['ZL_running','LSI_H_running']:
        rs=corpus(name);queries.extend(chunk_features(name,rs,refs))
        for lang in ['A','B']:
            current=chunk_features(name,[r for r in rs if r.get('currier_lang')==lang],refs)
            for r in current:r['corpus']=name+'_'+lang
            queries.extend(current)
    keys=BASE_FEATURES+['crossfit_lexical_bpc','crossfit_position_gain_bpc']
    for excluded in [False,True]:
        current=[r for r in records if not excluded or r['class'] not in ['C10','C11']];tag='exclude_C10_C11' if excluded else 'all_families'
        x=np.array([[r[k] for k in keys] for r in current]);y=np.array([r['class'] for r in current]);groups=sorted({r['source_block'] for r in current})
        p5=json.loads((ROOT/'configs/phase5.json').read_text());predictions=[];choices=[];receipts=[]
        for i,block in enumerate(groups):
            test=[j for j,r in enumerate(current) if r['source_block']==block];val0=[j for j,r in enumerate(current) if r['source_block']==groups[(i+1)%len(groups)]]
            ta=set().union(*(set(current[j]['ancestry']) for j in test));val=[j for j in val0 if not ta.intersection(current[j]['ancestry'])]
            va=set().union(*(set(current[j]['ancestry']) for j in val));train=[j for j,r in enumerate(current) if j not in test+val0 and not (ta|va).intersection(r['ancestry'])]
            train_classes=set(y[train]);valid=bool(train and val and test and train_classes==set(y))
            receipts.append(dict(block=block,train_chunks=len(train),validation_chunks=len(val),test_chunks=len(test),estimable=valid,
                missing_train_classes=sorted(set(y)-train_classes),train_ancestry=sorted(set().union(*(set(current[j]['ancestry']) for j in train))),test_ancestry=sorted(ta),validation_ancestry=sorted(va)))
            if not valid:continue
            scaler=StandardScaler().fit(x[train]);z=scaler.transform(x);options=[]
            for c in p5['classifier_C_candidates']:
                model=LogisticRegression(C=c,max_iter=2000,random_state=1729).fit(z[train],y[train]);options.append((accuracy_score(y[val],model.predict(z[val])),c,model))
            _,c,model=max(options,key=lambda v:(v[0],-v[1]));choices.append(c)
            for j,pred in zip(test,model.predict(z[test])):predictions.append(dict(corpus=current[j]['corpus'],source_block=block,truth=y[j],prediction=pred,correct=pred==y[j],selected_C=c))
        # If purging leaves no estimable fold, retain the previously frozen C and
        # label validation NOT ESTIMABLE rather than use manuscript assignments.
        c=sorted(Counter(choices),key=lambda v:(-Counter(choices)[v],v))[0] if choices else float(json.loads((ROOT/'report/classifier_result.json').read_text())['final_C'])
        table(EXT/f'report/classifier_{tag}_chunks.csv',[{**r,'ancestry':json.dumps(r['ancestry'])} for r in current]);dump(EXT/f'report/classifier_{tag}_purge_receipts.json',receipts)
        if predictions:table(EXT/f'report/classifier_{tag}_heldout.csv',predictions)
        output=[]
        for weighting in [None,'balanced']:
            scaler=StandardScaler().fit(x);model=LogisticRegression(C=c,class_weight=weighting,max_iter=2000,random_state=1729).fit(scaler.transform(x),y)
            q=np.array([[r[k] for k in keys] for r in queries]);ps=model.predict_proba(scaler.transform(q))
            for r,p in zip(queries,ps):output.append(dict(corpus=r['corpus'],source_block=r['source_block'],words=r['words'],class_weight=weighting or 'original_frequency',assigned_control=model.classes_[p.argmax()],confidence=float(p.max()),probabilities=json.dumps(dict(zip(model.classes_,p.tolist())))))
        table(EXT/f'report/classifier_{tag}_assignments.csv',output)
        dump(EXT/f'report/classifier_{tag}_result.json',dict(classes=sorted(set(y)),features=keys,final_C=c,estimable_folds=len(choices),folds=len(groups),test_chunks=len(predictions),accuracy=float(np.mean([r['correct'] for r in predictions])) if predictions else None,balanced_accuracy=float(balanced_accuracy_score([r['truth'] for r in predictions],[r['prediction'] for r in predictions])) if predictions else None,query_selection=False,warning='uncalibrated conditional control-family membership; ancestry-purged validation; original Phase5 classifier preserved; published C8 uses manuscript-derived seed'))
    dump(EXT/'report/CLASSIFIER_STATUS.json',dict(status='COMPLETE',original_preserved=True,excluded=['C10','C11'],queries=sorted({r['corpus'] for r in queries})))

def run():
    with threadpool_limits(2):classify(references())
if __name__=='__main__':run()
