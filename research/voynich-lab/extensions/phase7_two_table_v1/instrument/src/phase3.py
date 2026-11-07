"""Offline, frozen Phase 1–3 pipeline. Stops before any model training.

Run from voynich-lab as python -m src.phase3 (avoids stdlib tokenize shadowing).
"""
import csv
import hashlib
import json
import random
import re
import sys
import unicodedata
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT_RUN=None
# Also support direct script execution without shadowing stdlib tokenize.
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=ROOT/'src']
sys.path.insert(0,str(ROOT))
from src.parse_ivtff import parse
from src.encoders import encode,self_citation,grille
from src.metrics import measure
from src.noise import estimate,inject
from src.tokenize import train_bpe

SOURCE_HASHES={
 'hildegard_1903_ocr.txt':'fd4c50319594f9819e8ebe099d4d399e2015f17272b23d8685b2b2be68e7bc44',
 'mattioli_1568_ocr.txt':'f011d86894d0635a30eab9f97d98e51fafb7d82fd85f28c627e5282c4f161880',
 'bock_1595_ocr.txt':'6ad45002293f2174149a7743a24fcfb488b65ae6d951102ff178fadcdb2c34fa'}

def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=True,allow_nan=False)+'\n',encoding='utf-8')

def table(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def rng_for(seed,name):
    return random.Random(int.from_bytes(hashlib.sha256(f'{seed}:{name}'.encode()).digest()[:8],'big'))

def ordinary(r,config):
    return r['locus_code'][1:] in config['running_types'] and not r['is_spurious']

def load_words(spec,n):
    path=ROOT/'data/raw'/spec['filename']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==SOURCE_HASHES[path.name]
    raw=path.read_text(encoding='utf-8-sig')
    start=raw.index(spec['start_marker'])
    end=raw.index(spec['end_marker'],start) if spec['end_marker'] else len(raw)
    text=raw[start:end].lower().replace('\u017f','s').replace('\u00df','ss').replace('\u00e6','ae').replace('\u0153','oe')
    text=re.sub(r'([a-z])[-\u00ad]\s*\n\s*([a-z])',r'\1\2',text)
    text=''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c))
    words=re.findall(r'[a-z]+',text)
    if len(words)<n:
        raise ValueError(f'{path}: only {len(words)} words; no repetition/substitution permitted')
    return words[:n],dict(filename=path.name,raw_start_codepoint=start,raw_end_codepoint=end,
        available_normalized_words=len(words),selected_word_start=0,selected_word_end=n,
        first_words=words[:12],last_words=words[n-12:n],sha256=SOURCE_HASHES[path.name])

def layout(words,template,corpus):
    out=[];pos=0
    for r in template:
        n=len(r['text_eva'].split());row=dict(r)
        row.update(corpus=corpus,text_eva=' '.join(words[pos:pos+n]),transcriber='',
            text_raw='',hand_scribe=None,currier_lang=None,currier_hand=None,
            source_word_start=pos,source_word_end=pos+n,
            section=None,section_code=None,metadata_origin='borrowed_ZL_layout_only')
        out.append(row);pos+=n
    assert pos==len(words)
    return out

def relabel(rows):
    native=sorted(set(''.join(r['text_eva'].replace(' ','') for r in rows)))
    shared=list('abcdefghijklmnopqrstuvxyz')+['\ufffd']+[chr(0xe200+i) for i in range(256)]
    mapping=dict(zip(native,shared))
    return [{**r,'text_eva':''.join(mapping.get(c,c) for c in r['text_eva'])} for r in rows],mapping

def splits(template,seed):
    # All sides/panels of a leaf stay together: stricter than random-page splitting.
    leaves=sorted({re.match(r'f\d+',r['folio'])[0] for r in template})
    rng_for(seed,'page-splits').shuffle(leaves)
    a,b=int(.8*len(leaves)),int(.9*len(leaves))
    assignment={leaf:'train' if i<a else 'validation' if i<b else 'test' for i,leaf in enumerate(leaves)}
    return {r['folio']:assignment[re.match(r'f\d+',r['folio'])[0]] for r in template}

def audit(zl,config):
    # Reconstruct exactly the old reset-on-any-non-P behavior without editing bytes.
    active=None;old_missing=[]
    for r in zl:
        if r['folio']!=active:
            active=r['folio'];idx=None
        isp=r['locus_code'][1]=='P'
        if isp and '<%>' in r['text_raw']:idx=0
        elif isp and idx is not None:idx+=1
        if not isp or idx is None:old_missing.append(r)
        if not isp or '<$>' in r['text_raw']:idx=None
    assert len(old_missing)==1329
    grouped=Counter((r['is_label'],r['section'],r['locus_code'][1:]) for r in old_missing)
    table(ROOT/'report/paragraph_missing_before.csv',[
        dict(is_label=a,section=b,locus_type=c,count=n) for (a,b,c),n in sorted(grouped.items())])
    detail=[dict(line_id=r['line_id'],is_label=r['is_label'],section=r['section'],locus_type=r['locus_code'][1:],
        old_position=None,new_position=r['line_index_in_paragraph'],
        disposition='recovered_intervening_label_reset' if r['line_index_in_paragraph'] is not None else
                    'unmarked_free_floating_Pb_separate' if r['locus_code'][1:]=='Pb' else 'nonparagraph_not_applicable') for r in old_missing]
    table(ROOT/'report/paragraph_missing_loci.csv',detail)
    counts=Counter(r['disposition'] for r in detail)
    assert not any(ordinary(r,config) and r['line_index_in_paragraph'] is None for r in zl)
    table(ROOT/'data/voynich/ZL_lines_corrected.csv',zl)
    return dict(original_missing=1329,dispositions=dict(counts),primary_missing_positions=0,
                breakdown=[dict(is_label=a,section=b,count=n) for (a,b),n in sorted(Counter((r['is_label'],r['section']) for r in old_missing).items())])

def write_sources():
    path=ROOT/'SOURCES.md';old=path.read_text(encoding='utf-8').split('\n## Phase 1 sources')[0]
    lines=['', '## Phase 1 sources — public-domain underlying editions', '',
        '- C1: Hildegard, *Causae et curae*, medieval Latin medical prose, Paul Kaiser edition, Leipzig 1903. [Archive metadata](https://archive.org/metadata/hildegardiscaus00hildgoog) records NOT_IN_COPYRIGHT, US. [OCR](https://archive.org/download/hildegardiscaus00hildgoog/hildegardiscaus00hildgoog_djvu.txt).',
        '- C2: Mattioli, *I discorsi ... della materia medicinale*, Venice 1568, Italian herbal/medical prose. Getty/Archive metadata records NOT_IN_COPYRIGHT. [Catalog](https://archive.org/details/gri_33125014246561), [OCR](https://archive.org/download/gri_33125014246561/gri_33125014246561_djvu.txt).',
        '- C3: Bock, *Kreutterbuch*, Strasbourg 1595, ETH-Bibliothek Zürich, Rar 10995. [Catalog and Public Domain Mark](https://www.e-rara.ch/zut/content/titleinfo/32316756), [OCR](https://www.e-rara.ch/zut/download/ftpack/plain/32316756), DOI 10.3931/e-rara-151544.', '',
        'Underlying historical texts/editions are public domain. OCR is not corrected transcription: scan headers, glosses, cross-column ordering and recognition errors can remain. “Clean” means without added simulated noise. Never interpret OCR effects as inherent properties of Latin/Italian/German.', '',
        'Source selection uses the first N words after frozen body-text markers, with N=ZL ordinary running-text word count. Source_slices.json records ranges and samples; normalization is in config. No selection by measured resemblance. C1 includes the medical work’s cosmological exposition, not just remedy entries.', '']
    for name,h in SOURCE_HASHES.items():lines.append(f'- `{name}` SHA-256 `{h}`.')
    lines+=['', 'Other raw lookup/download receipts retained:',
        '- `mattioli_metadata.json`, `hildegard_metadata.json`: Archive metadata URLs above.',
        '- `bock_1595_catalog.html`: e-rara catalog above.',
        '- `bock_catalog.html`: attempted https://digital.ulb.hhu.de/vester/content/titleinfo/5277713 returned a JavaScript challenge; not used as corpus text. Attempted /download/fulltext/5277713 returned 404; no text file substituted.',
        '- `bock_archive_search.json`: https://archive.org/advancedsearch.php?q=creator%3A%22Bock%2C+Hieronymus%22&output=json&rows=20 ; lookup only.',
        '- `physica_catalog.html`: https://www.medievalbestiary.info/biblios/biblio113744.htm ; considered Physica before selecting the accessible Causae et curae medical prose edition; lookup only.',
        '- C4–C7 derive from the exact selected C1 word sequence; C8/C9 are local deterministic synthetic generators. C10/C11 derive from the primary ZL running text. Their Voynich-source redistribution status remains as in Phase 0.', '']
    path.write_text(old+'\n'.join(lines),encoding='utf-8')

def main():
    global CURRENT_RUN
    if sys.version_info<(3,11):raise RuntimeError('Python 3.11+ required')
    config=json.loads((ROOT/'configs/phase3.json').read_text())
    phase0=json.loads((ROOT/'configs/phase0.json').read_text())
    for s in phase0['sources']:
        assert hashlib.sha256((ROOT/'data/raw'/s['filename']).read_bytes()).hexdigest()==s['sha256']
    run=ROOT/'runs'/datetime.now(timezone.utc).strftime('phase3-%Y%m%dT%H%M%S%fZ');run.mkdir()
    CURRENT_RUN=run
    dump(run/'config.json',config);dump(run/'source_hashes.json',SOURCE_HASHES)
    dump(run/'environment.json',dict(python=sys.version,executable=sys.executable,seed=config['seed']))
    zl=parse(ROOT/'data/raw/ZL3b-n.txt','ZL');lsi=parse(ROOT/'data/raw/LSI_ivtff_0d.txt','LSI')
    audit_result=audit(zl,config);dump(ROOT/'report/paragraph_audit.json',audit_result)
    primary=[r for r in zl if ordinary(r,config)]
    alternate=[r for r in lsi if r['transcriber']=='H' and ordinary(r,config)]
    corpora={'ZL_running':primary,'LSI_H_running':alternate,
             'ZL_labels':[r for r in zl if r['is_label']],
             'LSI_H_labels':[r for r in lsi if r['transcriber']=='H' and r['is_label']],
             'ZL_free_floating_Pb':[r for r in zl if r['locus_code'][1:]=='Pb']}
    for name,rows in list(corpora.items()):
        table(ROOT/'data/voynich'/f'{name}.csv',rows)
        if name.endswith('_running'):
            for lang in ['A','B']:
                corpora[name+'_'+lang]=[r for r in rows if r['currier_lang']==lang]
    missing_AB={name:sum(r['currier_lang'] not in ['A','B'] for r in rows) for name,rows in [('ZL_running',primary),('LSI_H_running',alternate)]}
    n=sum(len(r['text_eva'].split()) for r in primary)
    sources={};source_receipts={}
    for c,spec in config['source_slices'].items():
        sources[c],source_receipts[c]=load_words(spec,n)
    dump(ROOT/'report/source_slices.json',source_receipts)
    with (ROOT/'report/agreement_lines.csv').open(encoding='utf-8',newline='') as f:pairs=list(csv.DictReader(f))
    noise,ops_table=estimate(lsi,pairs)
    table(ROOT/'report/agreement_edit_operations.csv',ops_table)
    assert sum(noise['counts'].get(k,0) for k in ['substitution','insertion','deletion'])==33785
    dump(ROOT/'report/noise_model.json',noise)
    control_meta={};raw_controls={}
    for c in ['C1','C2','C3']:
        raw_controls[c]=layout(sources[c],primary,c);control_meta[c]=dict(source=c)
    for c in ['C4','C5','C6','C7']:
        words,meta=encode(sources['C1'],c,rng_for(config['seed'],c),config)
        raw_controls[c]=layout(words,primary,c);control_meta[c]=meta
    for c,fn in [('C8',self_citation),('C9',grille)]:
        words,meta=fn(n,rng_for(config['seed'],c),config)
        raw_controls[c]=layout(words,primary,c);control_meta[c]=meta
    page_words=defaultdict(list)
    for r in primary:page_words[r['folio']].extend(r['text_eva'].split())
    shuffled={p:list(ws) for p,ws in page_words.items()}
    for p,ws in shuffled.items():rng_for(config['seed'],'C10:'+p).shuffle(ws)
    offsets=Counter();rows=[]
    for r in primary:
        p=r['folio'];count=len(r['text_eva'].split());start=offsets[p]
        rows.append({**r,'corpus':'C10','text_eva':' '.join(shuffled[p][start:start+count])});offsets[p]+=count
    raw_controls['C10']=rows;control_meta['C10']=dict(method='word shuffle within primary page, same word slots')
    rows=[];rng=rng_for(config['seed'],'C11')
    for r in primary:
        ws=[]
        for w in r['text_eva'].split():
            chars=list(w);rng.shuffle(chars);ws.append(''.join(chars))
        rows.append({**r,'corpus':'C11','text_eva':' '.join(ws)})
    raw_controls['C11']=rows;control_meta['C11']=dict(method='characters shuffled independently within word')
    split=splits(primary,config['seed']);dump(ROOT/'configs/page_split.json',split)
    noise_receipts={};bpe_models={};match=[]
    target_chars=sum(len(r['text_eva'].replace(' ','')) for r in primary)
    for c,rows in raw_controls.items():
        folder=ROOT/'data/controls'/c;folder.mkdir(exist_ok=True)
        rows=[{**r,'hand_scribe':None,'currier_hand':None,'currier_lang':None,
               'section':None,'section_code':None,'metadata_origin':'borrowed_ZL_layout_only'} for r in rows]
        # Voynich-derived shuffles keep their original glyph identities exactly.
        if c not in ['C10','C11']:rows,mapping=relabel(rows)
        else:mapping={s:s for s in sorted(set(''.join(r['text_eva'].replace(' ','') for r in rows)))}
        control_meta[c]['symbol_mapping']=mapping
        train_words=[w for r in rows if split[r['folio']]=='train' for w in r['text_eva'].split()]
        merges=train_bpe(train_words,config['control_bpe_merges'])
        bpe_models[c]=merges
        noisy=[];counts=Counter();length=0;whitespace_changed=0
        rng=rng_for(config['seed'],c+':noise')
        alphabet=set(''.join(r['text_eva'].replace(' ','') for r in rows))
        for r in rows:
            text,ops,raw=inject(r['text_eva'],noise['rates'],alphabet,rng)
            counts.update(ops);length+=len(r['text_eva']);whitespace_changed+=raw!=text
            noisy.append({**r,'text_eva':text,'pre_whitespace_normalization':raw})
        noise_receipts[c]=dict(operations=dict(counts),input_characters_including_spaces=length,
            realized_operation_rate=sum(counts.values())/length,whitespace_normalized_loci=whitespace_changed)
        for version,selected in [('clean',rows),('noise',noisy)]:
            name=c+'_'+version;corpora[name]=selected
            table(folder/f'{version}.csv',selected)
            wc=sum(len(r['text_eva'].split()) for r in selected);cc=sum(len(r['text_eva'].replace(' ','')) for r in selected)
            match.append(dict(corpus=c,version=version,words=wc,target_words=n,word_ratio=wc/n,
                characters=cc,target_EVA_characters=target_chars,EVA_character_ratio=cc/target_chars,
                alphabet_size=len(set(''.join(r['text_eva'].replace(' ','') for r in selected))),
                word_match_within_5pct=abs(wc/n-1)<=.05))
        dump(folder/'metadata.json',control_meta[c])
    table(ROOT/'report/size_matching.csv',match);dump(ROOT/'report/noise_realized.json',noise_receipts)
    dump(ROOT/'configs/control_bpe.json',bpe_models)
    # Freeze every input before calculating any Phase 3 metric.
    frozen=[*ROOT.glob('configs/*.json'),*ROOT.glob('data/raw/*'),*ROOT.glob('src/*.py'),*ROOT.glob('src/encoders/*.py'),
            *ROOT.glob('tests/*.py'),ROOT/'DECISIONS.md',ROOT/'requirements-phase3.txt',
            *ROOT.glob('data/controls/*/*.csv'),*ROOT.glob('data/voynich/*running*.csv')]
    dump(run/'freeze_before_metrics.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen if p.is_file()})
    print('Inputs frozen. Measuring Phase 3.',flush=True)
    results=[];shapes={}
    for name,rows in corpora.items():
        base=name.split('_')[0];merges=bpe_models.get(base)
        for scheme in ['T1','T2','T3']:
            result,detail=measure(rows,scheme,config['clusters'],merges)
            results.append(dict(corpus=name,tokenization=scheme,**result));shapes[name+':'+scheme]=detail
    table(ROOT/'report/master_metrics.csv',results);dump(ROOT/'report/growth_and_lengths.json',shapes)
    run_metrics=dict(status='PHASE_3_COMPLETE_STOP',seed=config['seed'],primary_words=n,
        primary_characters=target_chars,audit=audit_result,noise=noise,AB_excluded=missing_AB,metrics=results)
    write_sources()
    write_report(run.name,results,match,audit_result,noise,missing_AB)
    from src.plot_phase3 import plot
    plot(ROOT)
    from src.verify_phase3 import main as verify
    verify()
    dump(run/'metrics.json',run_metrics)
    dump(run/'status.json',dict(status='PHASE_3_COMPLETE_STOP'))
    # Per-run copies preserve older checkpoints when shared report files are rebuilt.
    for p in (ROOT/'report').glob('*'):
        if p.is_file() and p.suffix in ['.json','.csv','.md','.png','.svg']:(run/p.name).write_bytes(p.read_bytes())
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [*ROOT.glob('report/*'),*ROOT.glob('data/controls/*/*.csv'),*ROOT.glob('data/voynich/*running*.csv')] if p.is_file()}
    dump(run/'output_hashes.json',hashes)
    print(json.dumps(dict(run_id=run.name,primary_words=n,primary_characters=target_chars,noise=noise,rows=len(results)),indent=2))

def write_report(run_id,results,match,audit_result,noise,missing_AB):
    report=['# Voynich pattern-model lab — Phase 3 checkpoint','',
      '**STOP: Phases 1, 2 and 3 complete. No model training, probes, fingerprint classification or Phase 5 analyses have run.**','',
      f'Run `{run_id}`; seed 1729. Primary ZL ordinary running paragraphs; LSI-H robustness corpus remains separate. Labels and free-floating Pb text have separate files.','',
      '## Paragraph-position repair','',
      'The old parser erased a running paragraph’s state whenever it encountered a label. The repair preserves explicit paragraph state across intervening non-paragraph loci. No source text changed.','',
      f"Original missing positions: {audit_result['original_missing']:,}. Dispositions: {audit_result['dispositions']}. Primary missing positions after repair: **0**.",'',
      '| is_label | Section | Originally missing loci |','|---|---|---:|']
    report += [f"| {r['is_label']} | {r['section']} | {r['count']} |" for r in audit_result['breakdown']]
    report += ['', 'The 13 still-unmarked paragraph-type loci are Pb (free-floating blocks), not ordinary running paragraphs. All 134 Pb loci are retained separately, including marked ones; none are silently reclassified as labels. Primary running types are P0/P1/Pc/Pr/Pt. C/R diagram text also remains outside the primary corpus. Full original 1,329-locus audit is in paragraph_missing_loci.csv.','',
      '## Corpora and matching','',
      'All clean controls match the primary **word count exactly**; source words are never repeated to fill a short corpus. Noise variants use the paired clean corpus without resampling. EVA-character ratios are disclosed, not forced to match. Layout uses the same word slots, pages and paragraph flags as ZL; original language lines/paragraphs are not preserved. This tests lexical/order structure under matched layout, not natural manuscript line-breaking behavior.','',
      '| Control | Version | Words | Word ratio | Characters | EVA-character ratio | Alphabet |','|---|---|---:|---:|---:|---:|---:|']
    for r in match:report.append(f"| {r['corpus']} | {r['version']} | {r['words']} | {r['word_ratio']:.4f} | {r['characters']} | {r['EVA_character_ratio']:.4f} | {r['alphabet_size']} |")
    report += ['', 'C1=Hildegard Latin medical prose (1903 edition); C2=Mattioli Italian herbal (1568); C3=Bock German herbal (1595). C4–C6 are parameterized schematic scribal/shorthand/astro encoders of C1. C7=fixed verbose cipher of C1. C8=simplified recent-word copying/mutation; C9=simplified table/grille. C10=page-local word shuffle; C11=within-word character shuffle. C8/C9 are style controls, not replications of published implementations. SOURCES.md records provenance, byte hashes and failed retrievals.','',
      'Clean historical controls contain uncorrected OCR. Alphabet relabeling is injective and preserves counts/structure; actual alphabet sizes are reported. Cardinalities are comparable, not identical: there is residual alphabet-size confounding, so raw entropy alone cannot identify a generator. The normalized entropy column is descriptive and does not eliminate this confound.','',
      '## Noise calibration','',
      f"Eligible historical line-pairs reproduce Phase 0’s 33,785 edit operations / 790,720 denominator = **{sum(noise['rates'].values()):.4%}**. Fixed symmetric rates: substitution **{noise['rates']['substitution']:.4%}**, insertion **{noise['rates']['insertion']:.4%}**, deletion **{noise['rates']['deletion']:.4%}**.",'',
      'Traceback ties choose diagonal, deletion, insertion. Insertion/deletion orientation is averaged because neither transcriber is truth. The IID sensitivity channel edits existing characters including spaces; no newline edits. Inserted/substituted symbols are uniform over that control’s alphabet plus one space; substitutions cannot equal the input. Single-pass mutually exclusive operations; output whitespace is canonicalized, with raw pre-normalization strings saved. Attempted operation rates and normalization counts are in noise_realized.json. This is not a fitted historical corruption process or a literal per-transcription error rate.','',
      '## Frozen tokenizations and metric definitions','',
      'T1=EVA code point/normalized control symbol, including spaces. T2=longest configured EVA cluster for ZL/LSI; controls use 13 greedy BPE pair merges learned only from clean control training pages, then reused on its noisy version. T3=space-delimited word. BPE stays inside words. Splits group all manuscript sides/panels of a leaf into the same 80/10/10 partition; models have not run. Every merge/codebook/config is saved.','',
      'h0=H(X), h1=H(next|previous), h2=H(next|previous two), empirical plug-in bits per token. No transitions cross loci. The headline character h2 is T1; T2/T3 are cluster/word entropies, not character entropies. Entropies use UNK as a symbol. Space/no-space conventions matter. No bias correction: sparse contexts, especially T3, can depress conditional entropy. Support counts accompany estimates.','',
      'Zipf uses all token types in log-rank/log-frequency regression. Hapax ratio is singleton types / all types. Word-length mean/variance/skewness/excess kurtosis and growth curves are supplied. Glyph MI uses first/interior/last/both word positions within lines, first/interior/last/single glyph positions within words, and explicit paragraph-start vs continuation; null starts are excluded. Identical and edit-distance-exactly-1 repetition rates use adjacent words within a locus. The glyph/word metrics repeat across tokenizations by design.','',
      '## Master measurements: every corpus beside the controls','',
      'The full one-table output is master_metrics.csv (all metrics, tokenizations, primary, LSI-H, separate labels/Pb, A/B subsets, clean/noisy controls). This display highlights character entropy and shared structural measurements; it is not a significance test.','',
      '![Paired control comparisons](phase3_comparisons.png)','',
      '![Token-growth curves alongside controls](phase3_growth.png)','',
      '| Corpus | T1 h0 | T1 h1 | **T1 h2** | Word length mean | Line-edge MI | Paragraph-start MI | Edit-1 repetition |','|---|---:|---:|---:|---:|---:|---:|---:|']
    def fmt(v):return 'NA' if v is None else f'{v:.4f}'
    for r in results:
        if r['tokenization']=='T1':report.append('| '+r['corpus']+' | '+' | '.join(fmt(r[k]) for k in ['h0','h1','h2','word_length_mean','mi_glyph_line_word_edge','mi_glyph_paragraph_start','consecutive_edit1_rate'])+' |')
    report += ['', '## Eligibility and interpretation','',
      f"Unknown Currier-language exclusions from A/B: {missing_AB}. Never imputed. Overall corpora retain those loci. Control A/B comparisons at this checkpoint use the same full control baselines; controls have no authentic Currier assignment. No A/B-specific generator inference is made.",'',
      'Scribe/hand and paragraph-position probes are registered as ZL-only. LSI-H has no explicit paragraph-start markers here; its paragraph-start MI is NA, not zero. Labels/Pb have different lengths/coverage from the running controls: those rows are inventories, not matched label-effect evidence.','',
      '## What this does NOT show','',
      'These measurements do not translate or decipher Voynich, identify its language or generator, establish medieval shorthand authenticity, or distinguish a broad historical generator class from one schematic control. No nearest-control ranking, significance claim or “dramatic” finding is asserted. Noise is a sensitivity channel and historical OCR is an uncontrolled additional source of variation. Matching word counts cannot simultaneously equalize character budgets when word lengths differ.','',
      'Model-free measures alone do not test line-position embedding gain. Model comparisons, five-seed variance, alternate-transcription confirmation of any proposed dramatic finding, shorthand sweeps, classifier validation, surprise maps and probes remain for later phases. Further inference requires those checks and matched controls.','',
      'Verification and run receipts are in runs/. DECISIONS.md freezes all judgment calls. Proceed no further until this Phase 3 checkpoint is accepted.','']
    (ROOT/'report/REPORT.md').write_text('\n'.join(report),encoding='utf-8')

if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if CURRENT_RUN is not None:dump(CURRENT_RUN/'status.json',dict(status='FAILED',error=repr(error)))
        raise
