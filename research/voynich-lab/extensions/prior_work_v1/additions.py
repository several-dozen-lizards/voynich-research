"""Separately registered full-best C12 and exploratory partial decomposition."""
from collections import Counter
from .common import *
from src.encoders import encode,expansive
from src.noise import inject
from src.tokenize import train_bpe
from src import train
from src.metrics import measure
import numpy as np

def data():
    folder=EXT/'runs/additions';cfg=json.loads((ROOT/'configs/phase3.json').read_text())
    selected=json.loads((folder/'C12_SELECTION.json').read_text())['selected'];settings=json.loads((EXT/'phase6_additions.json').read_text())
    template=rows(ROOT/'data/voynich/ZL_running.csv');allocation=json.loads((ROOT/'configs/page_split.json').read_text())
    source,_=load_words(cfg['source_slices']['C1'],34509);atomic,_=encode(source,'C5',rng_for(1729,'C12'),cfg)
    signs=sorted(set(''.join(atomic)));order=signs[:];rng_for(1729,'C12:partial:types').shuffle(order)
    noise_rates=json.loads((ROOT/'report/noise_model.json').read_text())['rates'];reg={}
    for i,setting in enumerate(selected):
        L=setting['sequence_length'];R=setting['slot_rigidity'];_,meta=expansive(source,rng_for(1729,'C12'),cfg,L,R)
        fractions=[1.0]+settings['C12_partial']['fractions'] if i==0 else settings['C12_partial']['fractions']
        for fraction in fractions:
            code='C12_fullbest' if fraction==1 else f'C12_partial_L{L}_R{R:g}_F{fraction:g}'
            directory=folder/'data'/code;directory.mkdir(parents=True,exist_ok=True)
            count=min(len(signs),max(1,round(fraction*len(signs))));expanded=set(order[:count])
            book={c:meta['codebook'][c] if c in expanded else c for c in signs}
            output=[''.join(book[c] for c in w) for w in atomic];native=layout(output,template,'C12');clean,mapping=relabel(native)
            alphabet=set(mapping.values());rng=rng_for(1729,('C12' if fraction==1 else code)+':noise');noisy=[]
            for r in clean:
                text,_,_=inject(r['text_eva'],noise_rates,alphabet,rng);noisy.append({**r,'text_eva':text})
            bpe=train_bpe([w for r in clean if allocation[r['folio']]=='train' for w in r['text_eva'].split()],13)
            inverse=Counter();vocab={}
            for original,encoded in zip(atomic,output):vocab.setdefault(encoded,set()).add(original)
            metadata=dict(fraction_requested=fraction,decomposed_types=count,atomic_types=len(signs),type_fraction=count/len(signs),
                occurrence_fraction=sum(c in expanded for w in atomic for c in w)/sum(map(len,atomic)),sequence_length=L,slot_rigidity=R,
                selected_atomic_signs=sorted(expanded),mixed_codebook=book,collision_output_word_types=sum(len(values)>1 for values in vocab.values()),
                total_output_types=len(vocab),alphabet_size=len(alphabet),exploratory_post_null=fraction!=1)
            dump(directory/'metadata.json',metadata)
            for version,current in [('clean',clean),('noise',noisy)]:
                if fraction==1:
                    original=rows(ROOT/f'runs/phase5-c2f38fa45d6b/sweep/{setting["setting"]}/{version}.csv')
                    assert [r['text_eva'] for r in current]==[r['text_eva'] for r in original]
                path=directory/(version+'.csv');table(path,current);name=code+'_'+version
                reg[name]=dict(path=str(path.relative_to(ROOT)),split=allocation,bpe=bpe,fraction=fraction,metadata=str((directory/'metadata.json').relative_to(ROOT)))
    dump(folder/'registry.json',reg)
    # This receipt precedes partial metric/model scoring.
    dump(folder/'PARTIAL_DATA_FREEZE.json',{str(p.relative_to(ROOT)):sha(p) for p in (folder/'data').rglob('*') if p.is_file()})
    return reg

def prepared(name,scheme,cfg,extra=None):
    if extra is not None and name in extra:
        m=extra[name];selected=rows(ROOT/m['path']);allocation=m['split'];bpe=m['bpe']
    else:
        m=registry()[name];selected=corpus(name);allocation=m['split']
        old=json.loads((ROOT/'configs/control_bpe_extended.json').read_text());new=json.loads((EXT/'data/control_bpe.json').read_text())
        bpe=old.get(name.split('_')[0]) if m['legacy'] else new.get(name.rsplit('_',1)[0])
    return train.prepare(name,scheme,cfg,rows=selected,split=allocation,merges_override=bpe)

def partial_sweep():
    folder=EXT/'runs/additions';extra=json.loads((folder/'registry.json').read_text()) if (folder/'registry.json').exists() else data()
    cfg=json.loads((ROOT/'configs/phase4.json').read_text());results=[];free=[]
    for name,m in extra.items():
        if m['fraction']==1:continue
        selected=rows(ROOT/m['path']);metric,_=measure(selected,'T1',[],None);free.append(dict(corpus=name,**metric))
        p=prepared(name,'T1',cfg,extra)
        for pos in [False,True]:
            for seed in cfg['seeds']:
                job=folder/'partial_models'/f'{name}-p{int(pos)}-s{seed}'
                if (job/'metrics.json').exists():r=json.loads((job/'metrics.json').read_text())
                else:
                    model,r=train.fit(p,'lstm',pos,seed,cfg,job);del model
                results.append(r)
        progress('registered partial-decomposition sweep',corpus=name,completed=len(results),total=240)
    table(EXT/'report/C12_partial_model_free.csv',free);table(EXT/'report/C12_partial_model_runs.csv',[{k:v for k,v in r.items() if k!='curve'} for r in results])
    from scipy.stats import wasserstein_distance
    primary=corpus('ZL_running');alternate=corpus('LSI_H_running');lengths=lambda rs:[len(w) for r in rs for w in r['text_eva'].split()]
    zlength=lengths(primary);hlength=lengths(alternate);old=read(ROOT/'report/master_metrics_extended.csv');gains=read(ROOT/'report/line_position_gain.csv')
    z=next(r for r in old if r['corpus']=='ZL_running' and r['tokenization']=='T1');h=next(r for r in old if r['corpus']=='LSI_H_running' and r['tokenization']=='T1')
    zg=next(r for r in gains if r['corpus']=='ZL_running' and r['tokenization']=='T1' and r['architecture']=='lstm');hg=next(r for r in gains if r['corpus']=='LSI_H_running' and r['tokenization']=='T1' and r['architecture']=='lstm')
    output=[]
    for f in free:
        name=f['corpus'];rs=[r for r in results if r['corpus']==name];pairs=[next(r['test_bpt'] for r in rs if r['seed']==s and not r['with_position'])-next(r['test_bpt'] for r in rs if r['seed']==s and r['with_position']) for s in cfg['seeds']]
        hdist=abs(float(f['h2'])-float(z['h2']));hband=abs(float(z['h2'])-float(h['h2']));w1=wasserstein_distance(zlength,lengths(rows(ROOT/extra[name]['path'])));wband=wasserstein_distance(zlength,hlength)
        gain=float(np.mean(pairs));sd=float(np.std(pairs,ddof=1));gband=max(sd,float(zg['gain_sd']),abs(float(zg['gain_mean'])-float(hg['gain_mean'])))
        output.append(dict(corpus=name,**json.loads((ROOT/extra[name]['metadata']).read_text()),h2=f['h2'],h2_distance=hdist,h2_band=hband,
            word_length_W1=w1,word_length_band=wband,position_gain_mean=gain,position_gain_sd=sd,gain_band=gband,
            matches_all_three=hdist<=hband and w1<=wband and abs(gain-float(zg['gain_mean']))<=gband))
    table(EXT/'report/C12_partial_sweep.csv',output)
if __name__=='__main__':partial_sweep()
