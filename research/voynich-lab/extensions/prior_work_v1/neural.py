"""Extend the registered neural matrix without editing the accepted trainer.

T4 adapter preserves original source spans for coding denominators and OOV
literal costs. Existing T1–T3 fits are reused byte-for-byte.
"""
from .common import *
from .slots import tokenize as slot_tokens,pieces
from src import train
from src.tokenize import tokenize_line as original_tokenize,train_bpe
import numpy as np

def tokenizer(text,scheme,clusters,merges):
    return slot_tokens(text) if scheme=='T4' else original_tokenize(text,scheme,clusters,merges)

def prepare(name,scheme,cfg):
    train.tokenize_line=tokenizer
    selected=corpus(name);allocation=split(name);meta=registry()[name]
    bpe_file=EXT/'data/control_bpe.json'
    merges=json.loads(bpe_file.read_text()).get(name.rsplit('_',1)[0]) if bpe_file.exists() else None
    if meta['legacy']:
        old=json.loads((ROOT/'configs/control_bpe_extended.json').read_text());merges=old.get(name.split('_')[0])
    prepared=train.prepare(name,scheme,cfg,rows=selected,split=allocation,merges_override=merges)
    if scheme!='T4':return prepared
    spans={}
    for r in selected:
        tokens=[]
        for wi,w in enumerate(r['text_eva'].split()):
            if wi:tokens.append((None,' '))
            tokens.extend((wi,span) for _,span in pieces(w))
        spans[r['line_id']]=iter(tokens)
    prepared['character_counts']={p:0 for p in ['train','validation','test']}
    for block in prepared['metadata']:
        p=block['split'];bi=block['block_index'];updated=[]
        for j,meta_row in enumerate(block['metadata']):
            if meta_row is None:updated.append(None);continue
            line,wi,token,folio,lang=meta_row;expected_wi,span=next(spans[line]);assert expected_wi==wi
            updated.append((line,wi,span,folio,lang));prepared['character_counts'][p]+=len(span.replace(' ',''))
            target=int(prepared['tensors'][p][bi,1,j]);prepared['escape'][p][bi,j]=32+8*len(span.encode('utf-8')) if target==1 else 0
        block['metadata']=updated
    for p in prepared['character_counts']:
        assert prepared['character_counts'][p]==sum(len(r['text_eva'].replace(' ','')) for r in selected if allocation[r['folio']]==p)
    return prepared

def bpe():
    result={};reg=registry()
    for name,m in reg.items():
        if m['legacy'] or not name.endswith('_clean') or m.get('analysis_only'):continue
        selected=corpus(name);allocation=split(name)
        result[name.rsplit('_',1)[0]]=train_bpe([w for r in selected if allocation[r['folio']]=='train' for w in r['text_eva'].split()],13)
    dump(EXT/'data/control_bpe.json',result)

def main():
    if not (EXT/'FREEZE.json').exists():raise RuntimeError('Freeze sources/data/analyses before neural fitting')
    cfg=json.loads((ROOT/'configs/phase4.json').read_text());folder=EXT/'runs/models';folder.mkdir(exist_ok=True)
    reg=registry();jobs=[]
    for name,m in reg.items():
        if m.get('analysis_only'):continue
        for scheme in ['T4'] if m['legacy'] else ['T1','T2','T3','T4']:
            for architecture in ['lstm','transformer']:
                for pos in [False,True]:
                    for seed in cfg['seeds']:jobs.append((name,scheme,architecture,pos,seed))
    prepared=None;last=None
    for index,(name,scheme,architecture,pos,seed) in enumerate(jobs,1):
        path=folder/f'{name}-{scheme}-{architecture}-p{int(pos)}-s{seed}'
        if (path/'metrics.json').exists():continue
        if last!=(name,scheme):prepared=prepare(name,scheme,cfg);last=(name,scheme)
        try:
            model,result=train.fit(prepared,architecture,pos,seed,cfg,path,save_weights=seed==cfg['seeds'][0])
            if name=='C8_published_clean' and scheme=='T3' and not pos:
                np.savez_compressed(path/'embeddings.npz',embedding=model.embedding.weight.detach().cpu().numpy())
            del model
        except Exception as e:dump(path/'FAILED.json',dict(error=repr(e)));raise
        if index%5==0:progress('extended neural matrix',completed=index,total=len(jobs),last=path.name)
    dump(EXT/'report/NEURAL_STATUS.json',dict(status='COMPLETE',new_fits=len(jobs),reused_main_fits=1680))
    summarize()

def summarize():
    import statistics
    results=[]
    for directory in [ROOT/'runs/phase4-de886963575d',EXT/'runs/models']:
        results.extend(json.loads(p.read_text()) for p in directory.glob('*/metrics.json'))
    table(EXT/'report/model_runs.csv',[{k:v for k,v in r.items() if k not in ['curve','currier_test']} for r in results])
    groups={}
    for r in results:
        groups.setdefault((r['corpus'],r['tokenization'],r['architecture'],r['with_position']),[]).append(r)
        for language,values in r.get('currier_test',{}).items():
            alt={**r,'corpus':r['corpus']+'_'+language,'test_bpt':values['bpt'],'test_bpc_with_escape':values['bpc_with_escape'],'test_unknown_rate':values['unknown']/values['tokens']}
            groups.setdefault((alt['corpus'],r['tokenization'],r['architecture'],r['with_position']),[]).append(alt)
    summary=[];gains=[]
    for (name,scheme,arch,pos),rs in groups.items():
        summary.append(dict(corpus=name,tokenization=scheme,architecture=arch,with_position=pos,seeds=len(rs),
            test_bpt_mean=statistics.mean(r['test_bpt'] for r in rs),test_bpt_sd=statistics.stdev(r['test_bpt'] for r in rs),
            test_bpc_mean=statistics.mean(r['test_bpc_with_escape'] for r in rs),validation_bpc_mean=statistics.mean(r['validation_bpc_with_escape'] for r in rs),
            unknown_rate_mean=statistics.mean(r['test_unknown_rate'] for r in rs),endpoint_selected_fraction=statistics.mean(r['still_improving_at_budget'] for r in rs)))
        if pos:continue
        paired=groups[name,scheme,arch,True];values=[r['test_bpt']-next(p['test_bpt'] for p in paired if p['seed']==r['seed']) for r in rs]
        gains.append(dict(corpus=name,tokenization=scheme,architecture=arch,gain_mean=statistics.mean(values),gain_sd=statistics.stdev(values),seeds=len(values)))
    for r in gains:
        z=next(g for g in gains if g['corpus']=='ZL_running' and g['tokenization']==r['tokenization'] and g['architecture']==r['architecture'])
        h=next(g for g in gains if g['corpus']=='LSI_H_running' and g['tokenization']==r['tokenization'] and g['architecture']==r['architecture'])
        sensitivity=abs(z['gain_mean']-h['gain_mean']);r['transcription_gain_sensitivity']=sensitivity
        r['interpretation']='no difference' if abs(r['gain_mean'])<=max(r['gain_sd'],sensitivity) else 'exceeds descriptive band; not significance'
    table(EXT/'report/model_summary.csv',summary);table(EXT/'report/line_position_gain.csv',gains)
    return summary,gains
if __name__=='__main__':main()
