"""Strict final receipts: full matrix, held-out leaves, source coverage, probes."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def verify(experiment):
    from src.phase4 import all_names
    from src.extend_phase3 import manuscript
    freeze5=json.loads((experiment/'FREEZE.json').read_text())
    revisions=json.loads((experiment/'ANALYSIS_CORRECTIONS.json').read_text())
    changed={}
    for name,old in freeze5.items():
        current=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if current!=old:changed[name]=dict(frozen_sha256=old,current_sha256=current)
    assert changed==revisions['changes']
    reproduction=json.loads((experiment/'BASELINE_SWEEP_REPRODUCTION.json').read_text())
    assert reproduction['comparisons']==80 and reproduction['max_test_bpt_difference']==0 and reproduction['status']=='PASS'
    progress=json.loads((ROOT/'report/phase4_progress.json').read_text())
    assert progress['status']=='PHASE_4_COMPLETE' and progress['completed']==1680
    modelpaths=list(Path(progress['experiment']).glob('*/metrics.json'))
    freeze=json.loads((Path(progress['experiment'])/'FREEZE.json').read_text())
    normalized_freeze={k.replace('\\','/'):v for k,v in freeze.items()}
    for name in ['src/train.py','src/phase4.py','src/tokenize.py','configs/phase4.json','configs/page_split.json']:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==normalized_freeze[name]
    results=[json.loads(p.read_text()) for p in modelpaths]
    expected={(name,scheme,arch,pos,seed) for name in all_names() for scheme in ['T1','T2','T3']
              for arch in ['lstm','transformer'] for pos in [False,True] for seed in [1729,1733,1741,1753,1777]}
    actual={(r['corpus'],r['tokenization'],r['architecture'],r['with_position'],r['seed']) for r in results}
    assert actual==expected and len(actual)==len(results)==1680
    for path,r in zip(modelpaths,results):
        assert r['parameter_count']<=5_000_000
        assert all(math.isfinite(r[k]) for k in ['test_bpt','validation_bpt','test_bpc_with_escape','validation_bpc_with_escape'])
        assert r['device']=='cuda'
        if r['seed']==1729:assert (path.parent/'model.pt').exists()
    corrections=json.loads((Path(progress['experiment'])/'C12_CORRECTION.json').read_text())
    assert corrections['completed_non_C12']<1440
    c12merges=json.loads((ROOT/'configs/control_bpe_extended.json').read_text())['C12']
    for path,r in zip(modelpaths,results):
        if r['corpus'].startswith('C12_'):
            assert json.loads((path.parent/'config.json').read_text())['bpe_merges']==c12merges
    cv_receipts=list(experiment.glob('crossfit/*/LEAKAGE_RECEIPT.json'))+list(experiment.glob('surprise/*/LEAKAGE_RECEIPT.json'))
    assert len(cv_receipts)==285
    for path in cv_receipts:
        r=json.loads(path.read_text())
        assert not set(r['test_leaves'])&set(r['train_leaves'])
        assert not set(r['test_leaves'])&set(r['validation_leaves'])
        assert r['labels_in_training'] is False
    for name in all_names():
        if name in ['ZL_running','LSI_H_running']:source=ROOT/f'data/voynich/{name}.csv'
        else:
            code,version=name.rsplit('_',1);source=ROOT/f'data/controls/{code}/{version}.csv'
        expected_words=sum(len(r['text_eva'].split()) for r in read(source))
        for pos in [0,1]:
            values=read(experiment/f'reference_{name}_p{pos}_words.csv')
            assert len(values)==expected_words
            assert len({(r['line_id'],int(r['word_index'])) for r in values})==len(values)
    source=read(ROOT/'data/voynich/ZL_lines_corrected.csv')
    eligible={r['line_id'] for r in source if r['text_eva'].split()}
    words=read(ROOT/'report/surprise_words.csv');observed={r['line_id'] for r in words}
    assert observed==eligible
    assert len({(r['line_id'],int(r['word_index'])) for r in words})==len(words)
    assert len(words)==sum(len(r['text_eva'].split()) for r in source)
    token_scores=read(ROOT/'report/best_model_token_surprise.csv')
    token_word_bits=sum(float(r['total_bits']) for r in token_scores if r['word_index']!='')
    assert abs(token_word_bits-sum(float(r['bits']) for r in words))<1e-4
    assert len(read(ROOT/'report/top50_surprising_words.csv'))==50
    probes=read(ROOT/'report/probes.csv')
    assert len(probes)==58
    assert all(r['corpus']=='ZL_running' for r in probes if r['target'] in ['hand_scribe','is_para_start'])
    assert all(r['label_kind']=='independent_fake_page_labels' for r in probes if r['corpus'].startswith('C'))
    assert len(read(ROOT/'report/embedding_geometry.csv'))==40
    assert len(read(ROOT/'report/shorthand_sweep.csv'))==36
    assert len(read(ROOT/'report/shorthand_sweep_model_runs.csv'))==360
    assert len(read(ROOT/'report/confirmation_runs.csv'))==280
    membership=read(ROOT/'report/classifier_chunk_membership.csv')
    for i in range(1,14):
        a={r['line_id']:r['source_block'] for r in membership if r['corpus']==f'C{i}_clean'}
        b={r['line_id']:r['source_block'] for r in membership if r['corpus']==f'C{i}_noise'}
        assert all(a[k]==b[k] for k in a.keys()&b.keys())
    assert len(read(ROOT/'report/master_metrics_extended.csv'))==105
    assert len(read(ROOT/'report/master_metrics_final.csv'))==105
    assert len(read(ROOT/'report/labels_model_free.csv'))==84
    assert len(read(ROOT/'report/labels_model_scores.csv'))==56
    rows,meta=manuscript();assert len(rows)==2252 and len({r['folio'] for r in rows})==36
    assert sum(len(r['text_eva'].split()) for r in rows)==11056
    assert hashlib.sha256((ROOT/'data/raw/faithful_transcriptions_5582483.zip').read_bytes()).hexdigest()=='051ae4e6bbd984d967fdacea6de75b7e39da9b7259503479e232f16124040642'
    for name in ['fingerprint_pca.png','surprise_map.png','shorthand_sweep.png','C12_sweep_grid.png','model_position_gain.png']:
        assert (ROOT/'report'/name).stat().st_size>1000
    for path in modelpaths:
        spec=json.loads((path.parent/'config.json').read_text());split=spec['page_split'];leaves={}
        from src.surprise import leaf_key
        for page,part in split.items():
            key=leaf_key(page)
            if key in leaves:assert leaves[key]==part
            leaves[key]=part
    output=dict(status='PASS',main_model_runs=1680,crossfit_models=285,sweep_models=360,confirmation_models=280,
        total_neural_fits=2605,source_loci_covered=len(observed),source_words_scored=len(words),
        model_parameter_cap=5_000_000,checks=[
            'complete unique five-seed matrix','all CUDA and <=5M parameters','seed-1729 checkpoints present',
            'C12 corrected before its training and BPE receipts consistent','all cross-fit test leaves disjoint from training/validation',
            'reference word scores cover every source word exactly once','all nonempty ZL loci covered, no duplicate word scores',
            'per-token losses reconcile with per-word losses','top50 list complete','ZL-only restricted probes',
            'control probe labels explicitly fake','40 geometry seed/architecture rows','36 sweep points, 360 fits',
            '280 changed-seed control/transcription confirmation fits','all clean/noise classifier chunks share source-line boundaries','C13 authentic line/page/word coverage and raw hash',
            'required figures present','leaf sides never split across main partitions','all post-freeze analysis revisions explicitly hashed','80 original-setting sweep/main scores reproduce exactly'])
    (ROOT/'report/PHASE5_VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))
    return output

if __name__=='__main__':
    import sys
    verify(Path(sys.argv[1]))
