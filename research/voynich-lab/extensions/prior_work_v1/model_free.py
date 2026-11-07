"""Bounded, resumable Phase 3 extension and source-size sensitivity."""
import unicodedata,math,statistics
from collections import Counter
from .common import *
from .slots import decompose,tokenize as slot_tokens
from src import metrics
from src.metrics import entropy,conditional
from src.tokenize import tokenize_line,train_bpe

def tokens(text,scheme,clusters,merges):return slot_tokens(text) if scheme=='T4' else tokenize_line(text,scheme,clusters,merges)
def fast_measure(selected,scheme,clusters,merges,base=None):
    if base is None:
        m,d=metrics.measure(selected,'T1',clusters,merges)
        if scheme=='T1':return m,d
        base=(m,d)
    m,d=base;m=dict(m);d=dict(d)
    seqs=[tokens(r['text_eva'],scheme,clusters,merges) for r in selected];counts=Counter(t for s in seqs for t in s);n=sum(counts.values());v=len(counts)
    h0=entropy(counts);h1,s1=conditional(seqs,1);h2,s2=conditional(seqs,2)
    if v>1:
        x=[math.log(i) for i in range(1,v+1)];y=[math.log(c) for c in sorted(counts.values(),reverse=True)];xm=sum(x)/v;ym=sum(y)/v
        slope=sum((a-xm)*(b-ym) for a,b in zip(x,y))/sum((a-xm)**2 for a in x);total=sum((b-ym)**2 for b in y)
        r2=1-sum((b-(ym+slope*(a-xm)))**2 for a,b in zip(x,y))/total if total else None
    else:slope=r2=None
    points={max(1,round(n**(i/19))) for i in range(20)}|{n};growth=[];seen=set();i=0
    for sequence in seqs:
        for token in sequence:
            i+=1;seen.add(token)
            if i in points:growth.append(dict(tokens=i,types=len(seen)))
    m.update(tokens=n,types=v,h0=h0,h1=h1,h2=h2,h1_support=s1,h2_support=s2,
        alphabet_hartley=math.log2(v) if v else None,h2_normalized=h2/math.log2(v) if v>1 else None,
        zipf_slope=slope,zipf_r2=r2,hapax_ratio=sum(c==1 for c in counts.values())/v if v else None)
    d['growth']=growth;return m,d

def coverage(name,selected,view):
    counts=Counter(w for r in selected for w in r['text_eva'].split());classes=Counter();types=Counter()
    for word,n in counts.items():kind,_=decompose(word);classes[kind]+=n;types[kind]+=1
    return dict(corpus=name,view=view,words=sum(counts.values()),types=len(counts),
        **{kind+'_token_rate':classes[kind]/max(1,sum(counts.values())) for kind in ['REGULAR','SEPARABLE','UNSTRUCTURED','UNREADABLE']},
        **{kind+'_type_rate':types[kind]/max(1,len(counts)) for kind in ['REGULAR','SEPARABLE','UNSTRUCTURED','UNREADABLE']})

def matched_rows(words,name,template):
    result=[];position=0
    for row in template:
        n=min(len(row['text_eva'].split()),len(words)-position)
        if n<=0:break
        result.append({**row,'text_eva':' '.join(words[position:position+n]),'section':None,'currier_lang':None,'hand_scribe':None})
        position+=n
    assert position==len(words);return result

def work_family(name):
    for prefix in ['Casebook_','Codex_Wormianus_','Hebrew_Bereshit','Necrologium_','Secreta_Secretorum_']:
        if name.startswith(prefix):return prefix.rstrip('_')
    return name

def compute_one(name,selected,merges,folder,metadata):
    path=folder/(hashlib.sha256(name.encode()).hexdigest()[:20]+'.json')
    if path.exists():return json.loads(path.read_text())
    clusters=json.loads((ROOT/'configs/phase3.json').read_text())['clusters'];base=None;out=[]
    for scheme in ['T1','T2','T3','T4']:
        m,d=fast_measure(selected,scheme,clusters,merges,base)
        if scheme=='T1':base=(m,d)
        out.append(dict(corpus=name,tokenization=scheme,**metadata,**m))
    result=dict(metrics=out,coverage=coverage(name,selected,'pipeline'),details=base[1]);dump(path,result);return result

def controls():
    cfg=json.loads((ROOT/'configs/phase3.json').read_text());reg=registry();folder=EXT/'runs/model_free';folder.mkdir(exist_ok=True)
    bpes=json.loads((EXT/'data/control_bpe.json').read_text());old_bpes=json.loads((ROOT/'configs/control_bpe_extended.json').read_text())
    master=[];covers=[]
    names=list(reg)
    extras=['ZL_running_A','ZL_running_B','LSI_H_running_A','LSI_H_running_B','ZL_labels','LSI_H_labels','ZL_free_floating_Pb']
    for index,name in enumerate(names+extras):
        if name in reg:selected=corpus(name)
        elif name.endswith(('_A','_B')):selected=[r for r in corpus(name[:-2]) if r.get('currier_lang')==name[-1]]
        else:selected=rows(ROOT/f'data/voynich/{name}.csv')
        merges=old_bpes.get(name.split('_')[0]) if name not in reg or reg[name]['legacy'] else bpes.get(name.rsplit('_',1)[0])
        result=compute_one(name,selected,merges,folder,dict(family=reg[name]['family'] if name in reg else name.split('_')[0],source='pipeline control/manuscript'))
        master.extend(result['metrics']);covers.append(result['coverage'])
        if name in reg and reg[name].get('native_path') and name.endswith('_clean'):
            covers.append(coverage(name,rows(ROOT/reg[name]['native_path']),'native spelling'))
        elif name.startswith('C') and name in reg and reg[name]['legacy'] and name.endswith('_clean'):
            meta=json.loads((ROOT/f'data/controls/{name.split("_")[0]}/metadata.json').read_text());mapping=meta.get('symbol_mapping',{})
            if mapping:
                inverse={v:k for k,v in mapping.items()};native=[{**r,'text_eva':''.join(inverse.get(c,c) for c in r['text_eva'])} for r in selected]
                covers.append(coverage(name,native,'native spelling'))
        if index%5==0:progress('extended model-free controls',completed=index+1,total=len(names)+len(extras))
    table(EXT/'report/master_metrics.csv',master);table(EXT/'report/T4_coverage.csv',covers)
    # Independent human samples remain separate, with their original size.
    human=corpus('C17_human_clean');participant=[]
    for p in sorted({r['participant'] for r in human}):
        current=[r for r in human if r['participant']==p];base=None
        for scheme in ['T1','T2','T3','T4']:
            m,d=fast_measure(current,scheme,cfg['clusters'],bpes['C17_human'],base)
            if scheme=='T1':base=(m,d)
            participant.append(dict(source_document=p,tokenization=scheme,**m))
    table(EXT/'report/C17_per_document_metrics.csv',participant)

def baseline_one(job):
    family,path_str=job;path=Path(path_str);name=family+':'+path.name;folder=EXT/'runs/natural_baseline';folder.mkdir(exist_ok=True)
    cache=folder/(hashlib.sha256(name.encode()).hexdigest()[:20]+'.json')
    if cache.exists():
        cached=json.loads(cache.read_text())
        if 'blocks' in cached:return cached
    text=unicodedata.normalize('NFC',path.read_text(encoding='utf-8-sig')).casefold();all_words=text.split();selected_words=all_words[:34509]
    template=rows(ROOT/'data/voynich/ZL_running.csv');selected=matched_rows(selected_words,name,template)
    allocation=json.loads((ROOT/'configs/page_split.json').read_text());merges=train_bpe([w for r in selected if allocation[r['folio']]=='train' for w in r['text_eva'].split()],13)
    result=compute_one(name,selected,merges,folder,dict(family=family,work_family=work_family(path.name),available_words=len(all_words),source_sha256=sha(path),borrowed_ZL_layout=True))
    block_rows=[];clusters=json.loads((ROOT/'configs/phase3.json').read_text())['clusters']
    for block in range(min(30,len(selected_words)//200)):
        words=selected_words[block*200:(block+1)*200];current=matched_rows(words,name,template)
        # Size-matched entropy sensitivity. No source padding or resampling.
        for scheme in ['T1','T2','T3','T4']:
            sequences=[tokens(r['text_eva'],scheme,clusters,merges) for r in current]
            counts=Counter(t for s in sequences for t in s);h1,_=conditional(sequences,1);h2,_=conditional(sequences,2)
            block_rows.append(dict(corpus=name,block=block,words=200,tokenization=scheme,h0=entropy(counts),h1=h1,h2=h2))
    result['blocks']=block_rows;dump(cache,result);return result

def baselines():
    import concurrent.futures
    root=EXT/'raw/chirila/Corpora';wiki=sorted((root/'Wikipedia_texts/full').glob('*'));historical=sorted((root/'Historical_texts').glob('*'))
    wiki=[p for p in wiki if p.is_file() and p.name!='.DS_Store'];historical=[p for p in historical if p.is_file() and p.name!='.DS_Store']
    assert len(wiki)==294 and len(historical)==24
    jobs=[('Wikipedia',str(p)) for p in wiki]+[('Historical',str(p)) for p in historical]
    master=[];covers=[];blocks=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        for i,result in enumerate(pool.map(baseline_one,jobs),1):
            master.extend(result['metrics']);covers.append(result['coverage']);blocks.extend(result.get('blocks',[]))
            if i%10==0:progress('294-language and historical baseline metrics',completed=i,total=len(jobs))
    table(EXT/'report/natural_baseline_metrics.csv',master);table(EXT/'report/natural_baseline_T4_coverage.csv',covers);table(EXT/'report/natural_baseline_200word_blocks.csv',blocks)
    inventory=[dict(work=work_family(p.name),view=p.name,source_sha256=sha(p)) for p in historical]
    table(EXT/'report/historical_inventory.csv',inventory)
    dump(EXT/'report/BASELINE_STATUS.json',dict(status='COMPLETE',Wikipedia_languages=len(wiki),historical_views=len(historical),historical_work_families=len({r['work'] for r in inventory})))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--baselines-only',action='store_true');args=p.parse_args()
    if args.baselines_only:baselines()
    else:controls();baselines()
