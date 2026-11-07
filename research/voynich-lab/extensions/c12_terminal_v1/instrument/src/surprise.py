"""Leaf-cross-fitted scoring. Every scored leaf is absent from its model's training.

Word surprisal is the sum of its lexical-token losses, excluding separators,
with the registered literal fallback for UNK. Per-character values accompany it.
Labels/pseudo-labels are scored independently from BOS, never trained as running
text and never silently inserted into an assumed manuscript reading order.
"""
from src.train import *
from src.extend_phase3 import read,typed

def leaf_key(page):
    m=re.match(r'f\d+',page)
    return m[0] if m else re.sub(r'[rv]$','',page)

import re

def fold_splits(rows,seed=1729,extra_rows=None):
    pages=sorted({r['folio'] for r in rows+(extra_rows or [])})
    leaves=sorted({leaf_key(p) for p in pages});random.Random(seed).shuffle(leaves)
    folds={p:i%5 for i,p in enumerate(leaves)}
    splits=[]
    for heldout in range(5):
        remaining=[p for p in leaves if folds[p]!=heldout]
        random.Random(seed+100+heldout).shuffle(remaining)
        validation=set(remaining[:max(1,round(.1*len(leaves)))])
        splits.append({p:'test' if folds[leaf_key(p)]==heldout else 'validation' if leaf_key(p) in validation else 'train' for p in pages})
    return splits

def actual_labels():
    return typed(read(ROOT/'data/voynich/ZL_labels.csv'))

def pseudo_labels(name,templates):
    rows=read_rows(name);pages=defaultdict(list)
    for r in rows:pages[r['folio']].extend(r['text_eva'].split())
    order=sorted(pages);random.Random(1729).shuffle(order)
    page_index=0;offset=0;out=[]
    for i,template in enumerate(templates):
        n=len(template['text_eva'].split())
        while page_index<len(order) and len(pages[order[page_index]])-offset<n:
            page_index+=1;offset=0
        if page_index==len(order):raise ValueError(f'{name}: not enough unique source words for pseudo-labels')
        page=order[page_index];words=pages[page][offset:offset+n];offset+=n
        out.append(dict(corpus=name,folio=page,line_id=f'pseudo:{page}:{i}',text_eva=' '.join(words),
            is_para_start=None,currier_lang=None,is_label=True,source_word_end=offset))
    return out

@torch.no_grad()
def score_rows(model,prepared,rows,config,independent_lines=False,token_sink=None):
    if not rows:return [],[]
    original={r['line_id']:r for r in rows}
    selected=[{**r,'folio':r['folio']+'::'+r['line_id']} for r in rows] if independent_lines else rows
    split={r['folio']:'test' for r in selected}
    encoded=prepare(prepared['name'],prepared['scheme'],config,rows=selected,split=split,
        vocabulary_override=prepared['vocabulary'],merges_override=prepared['merges'],allow_empty=True)
    device=next(model.parameters()).device
    scored=evaluate(model,encoded['tensors']['test'].to(device),config['batch_size'],details=True)
    words=defaultdict(lambda:dict(bits=0.,tokens=0,unknown_tokens=0,characters=0))
    lines=defaultdict(lambda:dict(bits=0.,tokens=0,unknown_tokens=0,characters=0))
    target=encoded['tensors']['test'][:,1].numpy()
    for b in encoded['metadata']:
        if b['split']!='test':continue
        bi=b['block_index']
        for j,meta in enumerate(b['metadata']):
            if meta is None:continue
            line_id,wi,token,page,language=meta
            bits=float(scored['losses'][bi,j])+float(encoded['escape']['test'][bi,j])
            unknown=int(target[bi,j]==1);chars=len(token.replace(' ',''))
            role=original[line_id].get('score_role') or ('label' if str(original[line_id].get('is_label',False))=='True' else 'running')
            if token_sink is not None:
                token_sink.append(dict(folio=original[line_id]['folio'],line_id=line_id,word_index=wi,
                    token=token,vocabulary_id=int(target[bi,j]),unknown=unknown,role=role,
                    model_surprisal_bits=float(scored['losses'][bi,j]),literal_escape_bits=float(encoded['escape']['test'][bi,j]),
                    total_bits=bits,is_label=str(original[line_id].get('is_label',False))=='True',context_position=j))
            for entry in [lines[line_id]]+([words[line_id,wi]] if wi is not None else []):
                entry['bits']+=bits;entry['tokens']+=1;entry['unknown_tokens']+=unknown;entry['characters']+=chars
    word_rows=[];line_rows=[]
    for (line_id,wi),d in words.items():
        r=original[line_id];word=r['text_eva'].split()[wi]
        word_rows.append(dict(line_id=line_id,word_index=wi,word=word,folio=r['folio'],
            is_label=str(r.get('is_label',False))=='True',currier_lang=r.get('currier_lang'),
            role=r.get('score_role') or ('label' if str(r.get('is_label',False))=='True' else 'running'),
            contains_transcription_UNK=('\ufffd' in word) if prepared['name'].startswith(('ZL','LSI')) else None,
            **d,bits_per_character=d['bits']/max(1,d['characters'])))
    for line_id,d in lines.items():
        r=original[line_id]
        line_rows.append(dict(line_id=line_id,folio=r['folio'],currier_lang=r.get('currier_lang'),
            **d,bits_per_character=d['bits']/max(1,d['characters'])))
    return word_rows,line_rows

def crossfit(name,architecture,scheme,with_position,config,experiment,tag,labels=None,save_tokens=False):
    rows=read_rows(name);labels=labels or []
    splits=fold_splits(rows,extra_rows=labels)
    all_words=[];all_lines=[];all_labels=[]
    for fold,split in enumerate(splits):
        job=experiment/f'{tag}-fold{fold}'
        outputs=[job/'words.csv',job/'lines.csv',job/'labels.csv']
        token_ready=not save_tokens or all((job/n).exists() for n in ['tokens.csv','label_tokens.csv'])
        if all(p.exists() for p in outputs) and (job/'metrics.json').exists() and (job/'LEAKAGE_RECEIPT.json').exists() and token_ready:
            ws,ls,labs=(read(p) for p in outputs)
        else:
            prepared=prepare(name,scheme,config,rows=rows,split=split,fit_bpe=scheme=='T2')
            model,result=fit(prepared,architecture,with_position,config['seeds'][0],config,job)
            heldout=[r for r in rows if split[r['folio']]=='test']
            token_rows=[]
            ws,ls=score_rows(model,prepared,heldout,config,token_sink=token_rows if save_tokens else None)
            labrows=[r for r in labels if split[r['folio']]=='test']
            label_tokens=[]
            labs,_=score_rows(model,prepared,labrows,config,independent_lines=True,token_sink=label_tokens if save_tokens else None)
            for values in [ws,ls,labs]:
                for value in values:value['fold']=fold
            table(outputs[0],ws);table(outputs[1],ls)
            if labs:table(outputs[2],labs)
            else:outputs[2].write_text('line_id,word_index,word,folio,bits,tokens,unknown_tokens,characters,bits_per_character,fold\n')
            if save_tokens:
                for values,filename in [(token_rows,'tokens.csv'),(label_tokens,'label_tokens.csv')]:
                    for value in values:value['fold']=fold
                    table(job/filename,values)
            del model,prepared
            dump(job/'LEAKAGE_RECEIPT.json',dict(test_leaves=sorted({leaf_key(p) for p,g in split.items() if g=='test'}),
                train_leaves=sorted({leaf_key(p) for p,g in split.items() if g=='train'}),
                validation_leaves=sorted({leaf_key(p) for p,g in split.items() if g=='validation'}),labels_in_training=False))
            print(f'crossfit {tag} fold {fold} complete ({result["seconds"]:.1f}s)',flush=True)
        all_words.extend(ws);all_lines.extend(ls);all_labels.extend(labs)
    for receipt in experiment.glob(f'{tag}-fold*/LEAKAGE_RECEIPT.json'):
        d=json.loads(receipt.read_text());assert not set(d['test_leaves'])&set(d['train_leaves']);assert not set(d['test_leaves'])&set(d['validation_leaves'])
    return all_words,all_lines,all_labels

def render_surprise(words,labels):
    import sys
    sys.path.insert(0,str(ROOT/'.analysis-runtime'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    combined=words+labels
    def numeric(r):
        out=dict(r)
        for k in ['bits','characters','tokens','unknown_tokens','bits_per_character']:
            out[k]=float(out[k])
        return out
    source=read(ROOT/'data/voynich/ZL_lines_corrected.csv')
    source_order={r['line_id']:i for i,r in enumerate(source)}
    order=lambda r:(source_order[r['line_id']],int(r['word_index']))
    words=sorted(words,key=order);labels=sorted(labels,key=order)
    combined=sorted([numeric(r) for r in combined],key=order)
    table(ROOT/'report/surprise_words.csv',combined)
    top=sorted(combined,key=lambda r:(-r['bits'],r['folio'],r['line_id'],int(r['word_index'])))[:50]
    table(ROOT/'report/top50_surprising_words.csv',top)
    folios=defaultdict(lambda:dict(bits=0.,characters=0.,words=0,labels=0))
    for r in combined:
        d=folios[r['folio']];d['bits']+=r['bits'];d['characters']+=r['characters'];d['words']+=1
        d['labels']+=str(r.get('is_label',False))=='True'
    summary=[dict(folio=p,**d,bits_per_character=d['bits']/d['characters']) for p,d in folios.items()]
    table(ROOT/'report/surprise_folios.csv',summary)
    # Heatmap over source-order line/word positions; labels have a separate panel.
    only_labels=[r for r in labels if r.get('role','label')=='label']
    other=[r for r in labels if r.get('role')=='other']
    fig,axes=plt.subplots(3,1,figsize=(15,10),layout='constrained')
    for ax,values,label in zip(axes,[words,only_labels,other],['Running text','Labels (independent BOS context)','Other diagram/free-floating text (independent BOS context)']):
        pages=list(dict.fromkeys(r['folio'] for r in values));lookup={p:i for i,p in enumerate(pages)}
        counts=Counter();points=[]
        for r in values:
            y=counts[r['folio']];counts[r['folio']]+=1;points.append((lookup[r['folio']],y,float(r['bits_per_character'])))
        artist=ax.scatter([p[0] for p in points],[p[1] for p in points],c=[p[2] for p in points],s=3,
            cmap='magma',vmin=0,vmax=8,rasterized=True)
        ticks=list(range(0,len(pages),max(1,len(pages)//18)))
        ax.set_xticks(ticks,[pages[i] for i in ticks],rotation=45,ha='right');ax.set_ylabel('Word index within folio');ax.set_title(label)
        fig.colorbar(artist,ax=ax,label='Bits / lexical character (0–8 display)')
    fig.suptitle('Cross-fitted model surprisal; no scored manuscript leaf in its model training set')
    fig.savefig(ROOT/'report/surprise_map.png',dpi=160);plt.close(fig)
