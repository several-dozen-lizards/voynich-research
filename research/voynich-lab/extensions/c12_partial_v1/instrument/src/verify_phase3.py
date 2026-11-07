"""Independent saved-artifact invariants, including paired control preservation."""
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    primary=read(ROOT/'data/voynich/ZL_running.csv')
    assert len(primary)==3996
    assert sum(len(r['text_eva'].split()) for r in primary)==34509
    assert all(r['line_index_in_paragraph']!='' for r in primary)
    metrics=read(ROOT/'report/master_metrics.csv')
    assert len(metrics)==93
    assert len({(r['corpus'],r['tokenization']) for r in metrics})==93
    matches=read(ROOT/'report/size_matching.csv')
    assert len(matches)==22 and all(r['word_match_within_5pct']=='True' for r in matches)
    for r in matches:
        if r['version']=='clean':assert int(r['words'])==34509
    controls={c:read(ROOT/f'data/controls/{c}/clean.csv') for c in ['C'+str(i) for i in range(1,12)]}
    def page_bags(rows):
        bags=defaultdict(Counter)
        for r in rows:bags[r['folio']].update(r['text_eva'].split())
        return dict(bags)
    assert page_bags(primary)==page_bags(controls['C10'])
    for a,b in zip(primary,controls['C11']):
        assert [Counter(w) for w in a['text_eva'].split()]==[Counter(w) for w in b['text_eva'].split()]
    for rows in controls.values():
        assert [len(r['text_eva'].split()) for r in rows]==[len(r['text_eva'].split()) for r in primary]
        assert all(not r['currier_lang'] and not r['hand_scribe'] for r in rows)
    m={(r['corpus'],r['tokenization']):r for r in metrics}
    for scheme in ['T1','T2','T3']:
        for c in ['C10_clean','C11_clean']:
            for k in ['word_length_mean','word_length_variance','word_length_skewness','word_length_excess_kurtosis']:
                assert abs(float(m[c,scheme][k])-float(m['ZL_running',scheme][k]))<1e-12
    assert abs(float(m['C11_clean','T1']['h0'])-float(m['ZL_running','T1']['h0']))<1e-12
    for k in ['h0','types','hapax_ratio']:
        assert abs(float(m['C10_clean','T3'][k])-float(m['ZL_running','T3'][k]))<1e-12
    audit=json.loads((ROOT/'report/paragraph_audit.json').read_text())
    assert sum(r['count'] for r in audit['breakdown'])==1329
    assert audit['dispositions']==dict(nonparagraph_not_applicable=1255,recovered_intervening_label_reset=61,unmarked_free_floating_Pb_separate=13)
    operations=read(ROOT/'report/agreement_edit_operations.csv')
    assert sum(int(r.get('substitution') or 0)+int(r.get('insertion') or 0)+int(r.get('deletion') or 0) for r in operations)==33785
    for name in ['ZL_running','LSI_H_running']:
        allrows=read(ROOT/f'data/voynich/{name}.csv')
        assert sum(int(m[name+'_'+lang,'T1']['loci']) for lang in ['A','B'])==sum(r['currier_lang'] in ['A','B'] for r in allrows)
    merges=json.loads((ROOT/'configs/control_bpe.json').read_text())
    assert all(len(v)==13 for v in merges.values())
    result=dict(status='PASS',checks=['primary selection and paragraph completeness',
        '93 unique corpus/tokenization rows','22 controls within word-count tolerance',
        'C10 page vocabulary preservation','C11 per-word character preservation',
        'clean-control layout preservation','no control Currier/hand metadata leakage',
        'shuffle metric invariants','all 1329 original null positions accounted',
        'edit operation totals reproduce Phase 0','unknown language not imputed','13 BPE merges per control'])
    (ROOT/'report/VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
