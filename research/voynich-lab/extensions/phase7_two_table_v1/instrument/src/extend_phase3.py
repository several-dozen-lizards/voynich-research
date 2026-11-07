"""C12 expansive shorthand and CC0 C13 authentic manuscript-line control."""
import csv,hashlib,io,json,re,unicodedata,zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from src.phase3 import ROOT,dump,table,rng_for,load_words,layout,relabel
from src.encoders import expansive
from src.noise import inject
from src.metrics import measure
from src.tokenize import train_bpe

def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def typed(rows):
    return [{**r,'is_para_start':None if r.get('is_para_start','')=='' else r['is_para_start']=='True'} for r in rows]

def visible(node):
    tag=node.tag.split('}')[-1]
    if tag=='choice':
        branch=node.find('{*}abbr')
        if branch is None:branch=node.find('{*}orig')
        if branch is None:branch=next(iter(node),None)
        return visible(branch) if branch is not None else ''
    if tag in ['note','del','expan','ex']:return ''
    if tag=='gap':return '\ufffd'
    return (node.text or '')+''.join(visible(c)+(c.tail or '') for c in node)

def line_words(node):
    tag=node.tag.split('}')[-1]
    if tag in ['note','del','expan','ex']:return []
    if tag=='w':return [visible(node)]
    return [w for child in node for w in line_words(child)]

def manuscript():
    archive=ROOT/'data/raw/faithful_transcriptions_5582483.zip'
    outer=zipfile.ZipFile(archive)
    inner=zipfile.ZipFile(io.BytesIO(outer.read('SBB_PK_Mgf516.zip')))
    rows=[];receipts=[]
    # The archive also has an aggregated XML. Never count that duplicate copy.
    files=sorted(n for n in inner.namelist() if n.endswith('.xml') and '_all_transcriptions' not in n)
    for name in files:
        raw=inner.read(name);root=ET.fromstring(raw)
        licence=''.join(root.find('.//{*}licence').itertext())
        assert 'CC0' in licence
        folio=Path(name).stem
        receipts.append(dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),licence=licence.strip()))
        for index,line in enumerate(root.findall('.//{*}line')):
            raw_words=line_words(line)
            words=[]
            for w in raw_words:
                # Preserve abbreviations and diacritics; do not expand or join across lines.
                w=unicodedata.normalize('NFC',w.casefold().replace('\u017f','s'))
                w=''.join(c for c in w if not c.isspace())
                if w:words.append(w)
            if not words:continue
            rows.append(dict(corpus='C13',folio=folio,line_id=line.get('{http://www.w3.org/XML/1998/namespace}id') or f'{folio}.{index}',
                transcriber='Faithful_Transcriptions',text_raw=' '.join(raw_words),text_eva=' '.join(words),
                is_para_start=None,is_para_end=None,line_index_in_paragraph=None,section=None,currier_lang=None,
                hand_scribe=None,is_label=False,locus_code='authentic_line',
                source_xml=name,source_line_n=line.get('n'),image_coordinates=json.dumps({k:line.get(k) for k in ['ulx','uly','lrx','lry']}),
                metadata_origin='authentic_manuscript_line_coordinates'))
    assert len(rows)==2252
    return rows,dict(source='Faithful Transcriptions, SBB-PK Ms. germ. fol. 516, c.1457–1460, Middle High German historical Bible',
        url='https://zenodo.org/records/5582483',license='CC0 1.0',archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        source_files=receipts,normalization='diplomatic abbr/orig branch; omit del/note; NFC casefold long-s to s; retain marks; no line or word-fragment joining',
        size_exception='All 36 available manuscript pages retained; shorter than primary; no duplicated or synthetic filling.')

def main():
    config=json.loads((ROOT/'configs/phase3.json').read_text())
    primary=typed(read(ROOT/'data/voynich/ZL_running.csv'))
    n=sum(len(r['text_eva'].split()) for r in primary)
    source,_=load_words(config['source_slices']['C1'],n)
    words,metadata=expansive(source,rng_for(1729,'C12'),config,3,.5)
    c12=layout(words,primary,'C12');c12,mapping=relabel(c12);metadata['symbol_mapping']=mapping
    c13,meta13=manuscript();c13,mapping13=relabel(c13);meta13['symbol_mapping']=mapping13
    additions={'C12':(c12,metadata),'C13':(c13,meta13)}
    split=json.loads((ROOT/'configs/page_split.json').read_text())
    c13_pages=sorted({r['folio'] for r in c13});rng_for(1729,'C13:page_split').shuffle(c13_pages)
    a,b=int(.8*len(c13_pages)),int(.9*len(c13_pages))
    split13={p:'train' if i<a else 'validation' if i<b else 'test' for i,p in enumerate(c13_pages)}
    # Group leaf sides; override paired side assignments consistently.
    leaves=sorted({p[:-1] for p in c13_pages});rng_for(1729,'C13:leaf_split').shuffle(leaves)
    la,lb=int(.8*len(leaves)),int(.9*len(leaves))
    leafsplit={p:'train' if i<la else 'validation' if i<lb else 'test' for i,p in enumerate(leaves)}
    split13={p:leafsplit[p[:-1]] for p in c13_pages}
    dump(ROOT/'configs/C13_page_split.json',split13)
    rates=json.loads((ROOT/'report/noise_model.json').read_text())['rates']
    bpe=json.loads((ROOT/'configs/control_bpe.json').read_text())
    metrics=read(ROOT/'report/master_metrics.csv');shapes=json.loads((ROOT/'report/growth_and_lengths.json').read_text())
    matches=read(ROOT/'report/size_matching.csv');noise_receipts={}
    for c,(rows,meta) in additions.items():
        folder=ROOT/f'data/controls/{c}';folder.mkdir(exist_ok=True)
        current_split=split13 if c=='C13' else split
        merges=train_bpe([w for r in rows if current_split[r['folio']]=='train' for w in r['text_eva'].split()],13)
        bpe[c]=merges
        alphabet=set(''.join(r['text_eva'].replace(' ','') for r in rows))
        rng=rng_for(1729,c+':noise');noisy=[];ops=Counter();length=0
        for r in rows:
            text,events,raw=inject(r['text_eva'],rates,alphabet,rng)
            ops.update(events);length+=len(r['text_eva'])
            noisy.append({**r,'text_eva':text,'pre_whitespace_normalization':raw})
        noise_receipts[c]=dict(operations=dict(ops),input_characters=length,realized_operation_rate=sum(ops.values())/length)
        for version,selected in [('clean',rows),('noise',noisy)]:
            table(folder/f'{version}.csv',selected)
            name=c+'_'+version
            wc=sum(len(r['text_eva'].split()) for r in selected);cc=sum(len(r['text_eva'].replace(' ','')) for r in selected)
            matches.append(dict(corpus=c,version=version,words=wc,target_words=n,word_ratio=wc/n,characters=cc,target_EVA_characters=172280,
                EVA_character_ratio=cc/172280,alphabet_size=len(alphabet),word_match_within_5pct=abs(wc/n-1)<=.05,
                size_exception='authentic manuscript excerpt shorter than primary' if c=='C13' else ''))
            for scheme in ['T1','T2','T3']:
                result,detail=measure(selected,scheme,config['clusters'],merges)
                metrics.append(dict(corpus=name,tokenization=scheme,**result));shapes[name+':'+scheme]=detail
        dump(folder/'metadata.json',meta)
    dump(ROOT/'configs/control_bpe_extended.json',bpe)
    table(ROOT/'report/master_metrics_extended.csv',metrics)
    table(ROOT/'report/size_matching_extended.csv',matches)
    dump(ROOT/'report/growth_and_lengths_extended.json',shapes)
    dump(ROOT/'report/noise_realized_extensions.json',noise_receipts)
    focus=['ZL_running']+['C'+str(i)+'_clean' for i in range(4,10)]+['C12_clean']
    comparison=[r for r in metrics if r['corpus'] in focus and r['tokenization'] in ['T1','T2']]
    table(ROOT/'report/T1_T2_entropy_comparison.csv',comparison)
    report=['# Phase 3 additions for Phase 4','',
        'C12 decomposes every atomic C5 shorthand sign into a fixed three-stroke sequence; slot rigidity 0.5. Both parameters are frozen for the main run and registered for the Phase 5 sweep. C13 retains all 2,252 image-coordinate manuscript lines on 36 available pages of SBB-PK Ms. germ. fol. 516 (CC0).','',
        'C13 is an authentic-layout excerpt, not word-count matched: its available 36 pages are retained without repeating text, mixing manuscripts or inventing lines. This size/genre/orthography limitation must accompany its line-edge MI. Clean and noise variants retain exactly the same line records.','',
        '| Corpus | Scheme | h0 | h1 | h2 |','|---|---|---:|---:|---:|']
    for r in comparison:report.append(f"| {r['corpus']} | {r['tokenization']} | {float(r['h0']):.5f} | {float(r['h1']):.5f} | {float(r['h2']):.5f} |")
    report+=['','All h values are bits/token within that scheme. T2 values cannot be interpreted as bits per EVA character.','',
        '| Corpus | Line-edge MI (bits) | Words | Characters |','|---|---:|---:|---:|']
    for r in metrics:
        if r['tokenization']=='T1' and r['corpus'] in ['ZL_running','C1_clean','C13_clean','C13_noise']:
            report.append(f"| {r['corpus']} | {float(r['mi_glyph_line_word_edge']):.6f} | {r['words']} | {r['characters']} |")
    report+=['','No model result or historical generator inference is established by these additions.']
    (ROOT/'report/PHASE3_EXTENDED_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='C12_C13_READY',C13_lines=len(c13),C13_words=sum(len(r['text_eva'].split()) for r in c13),metric_rows=len(metrics)),indent=2))

if __name__=='__main__':main()
