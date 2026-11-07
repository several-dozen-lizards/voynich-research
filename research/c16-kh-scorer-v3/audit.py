"""Verify fresh source positions and gold-only ranking geometry. No new fitting."""
from preserve import R,dump
from register import read
from corrected import LM,VARIANTS,variant_id,UNK
from qualify import transform,table
from collections import Counter
import json,math,statistics
def units(rows,v):
    # Independent order traversal, retaining gold-surface slot identities.
    char,word,line,mode=v;rs=list(rows) if line=='TB' else list(reversed(rows));us=[]
    for j,r in enumerate(rs):
        ws=r.get('gold_words',r['text_eva'].split());tokens=[(r['line_id'],i,w) for i,w in enumerate(ws)]
        if word=='RTL':tokens=list(reversed(tokens))
        if mode=='boustro' and j%2:tokens=list(reversed(tokens))
        us.append(tokens)
    if mode=='column':us=[[u[k] for u in us if k<len(u)] for k in range(max(map(len,us),default=0))]
    return [u for u in us if u]
def main():
    banks=json.loads((R/'inputs/banks.json').read_text());old=json.loads((R/'inputs/v2-banks.json').read_text());checks=[];lengths=[]
    for arm,docs in banks['hebrew'].items():
        data=json.loads((R/'inputs'/f'{arm}.json').read_text());train={tuple(s) for s in data['train']};oldparents={i for d in old['hebrew'][arm] for i in d['test_segment_ids']};oldstrings={tuple(r['text_eva'].split()) for d in old['hebrew'][arm] for r in d['rows']};strings=[];parents=[]
        for d in docs:
            for r,p in zip(d['rows'],d['parents']):
                parent=p['parent'];ws=r['text_eva'].split();assert ws==data['test'][parent][p['offset']:p['end']];assert parent not in oldparents and tuple(ws) not in train and tuple(ws) not in oldstrings;assert p['end']-p['offset']==len(ws) and p['parent_words']==len(data['test'][parent]);parents.append(parent);strings.append(tuple(ws))
        assert len(parents)==len(set(parents))==640 and len(strings)==len(set(strings))==640
        checks.append(dict(arm=arm,check='independent_source_position_and_string_audit',parents=640,v2_parent_overlap=0,duplicate_windows=0,status='PASS'))
        lm=LM(data['train']);recorded={(r['document'],r['family']):float(r['score']) for r in read(R/'results'/arm/'raw-scorer-maxima.csv')};compared=0
        for d in docs:
            for family in ['Hebrew','word_shuffle','wrong_key','quarter_UNKNOWN','all_UNKNOWN','within_word']:
                rows=d['rows'] if family=='Hebrew' else transform(d['rows'],family,f"{arm}:{d['document']}:{family}");vs=[];envelope={}
                for v in VARIANTS:
                    records=[]
                    for u in units(rows,v):
                        ws=[t[2] for t in u];identity=tuple(sorted((t[0],t[1]) for t in u));score=lm.score(ws);r=dict(score=score,identity=identity,words=len(ws),unknowns=sum(lm.canonical(w)==UNK for w in ws),variant=variant_id(v));records.append(r)
                        if identity not in envelope or score>envelope[identity]['score']:envelope[identity]=r
                    top=sorted(records,key=lambda r:(-r['score'],r['identity']))[:3];score=sum(r['score'] for r in top)/len(top);vs.append(dict(score=score,variant=variant_id(v),top=top))
                best=max(vs,key=lambda r:r['score']);assert math.isclose(best['score'],recorded[d['document'],family],rel_tol=0,abs_tol=1e-12);compared+=1;top=best['top'];env=sorted(envelope.values(),key=lambda r:(-r['score'],r['identity']))[:3]
                lengths.append(dict(arm=arm,bank=d['bank'],document=d['document'],family=family,best_variant=best['variant'],score=best['score'],top_lines=len(top),mean_top_line_words=statistics.mean(r['words'] for r in top),min_top_line_words=min(r['words'] for r in top),max_top_line_words=max(r['words'] for r in top),singleton_top_lines=sum(r['words']==1 for r in top),envelope_mean_words=statistics.mean(r['words'] for r in env),envelope_singleton_lines=sum(r['words']==1 for r in env)))
            if len(lm.cache)>200000:lm.cache.clear()
        checks.append(dict(arm=arm,check='independent_gold_surface_traversal_and_maximum_selection',document_family_comparisons=compared,decoder_calls=0,fitter_calls=0,status='PASS'))
        for i in range(6):
            case=json.loads((R/'results'/arm/f'cipher-{i}.json').read_text());key=case['fitted_key'];n=ok=0;assert len(key)==len(set(key.values()))
            for ps,cs in zip(case['plaintext'],case['ciphertext']):
                for w,cw in zip(ps,cs):n+=1;ok+=Counter(w)==Counter(key.get(c,'?') for c in cw)
            assert ok/n==case['result']['alphagram_recovery']
        checks.append(dict(arm=arm,check='cipher_recovery_from_independent_count_vectors',cases=6,status='PASS'))
    oldC1={d['document'] for d in old['nulls'] if d['family']=='C1'};assert not (oldC1&{d['document'] for d in banks['external'] if d['family']=='C1'})
    for d in banks['external']:
        assert d['family'] in ['C1','C9']
        if d['family']=='C9':
            meta=d['generation'];actual=[w for r in d['clean'] for w in r['text_eva'].split()];expected=[''.join(d['symbol_mapping'][c] for c in meta['cell_order'][(meta['offset']+i*meta['stride'])%meta['period']]) for i in range(len(actual))];assert actual==expected
    checks.append(dict(check='C1_page_disjointness_C9_draw_reconstruction_and_no_C17_reuse',C1_pages=40,C9_draws=80,C17_scored=0,status='PASS'))
    table(R/'raw-selected-length-audit.csv',lengths);dump(R/'INDEPENDENT_AUDIT.json',dict(checks=checks,passed=True,decoder_or_fitter_called_in_scorer_audit=False,ZL_scores=0,qualification_decisions_changed=False))
    summary=[]
    for arm in ['tanakh','medieval']:
        for f in ['Hebrew','word_shuffle']:
            rs=[r for r in lengths if r['arm']==arm and r['bank']=='confirmation' and r['family']==f];summary.append(dict(arm=arm,family=f,mean_selected_line_words=statistics.mean(r['mean_top_line_words'] for r in rs),singleton_selected_lines=sum(r['singleton_top_lines'] for r in rs),selected_lines=sum(r['top_lines'] for r in rs)))
    dump(R/'LENGTH_DIAGNOSTIC.json',dict(confirmation=summary,no_threshold_or_filter_changed=True))
    lines=['','## Independent source/selection audit','',
    'The independent audit reconstructed every selected Hebrew window from its original parent/offset, excluded all v2 parents, checked exact duplicate exclusions, and independently traversed and selected all 960 document-family maxima. This scorer audit instantiated only the word LM and called neither a decoder nor a fitter. It also reconstructed fresh C9 draws from frozen cell orders and independently recomputed all 12 cipher recoveries with count vectors. All checks passed.','',
    '| Arm | Gold scorer family | Mean selected line words | Singleton selected lines |','|---|---|---:|---:|']
    for r in summary:lines.append(f"| {r['arm']} | {r['family']} | {r['mean_selected_line_words']:.2f} | {r['singleton_selected_lines']}/{r['selected_lines']} |")
    lines+=['','The full length table is raw-selected-length-audit.csv. These are diagnostics, not a post-hoc coverage filter or revised threshold. V2 and v3 use different qualification windows and geometry: changes in recovery rates cannot be attributed to the EOS repair, whose valid-sentence scores were proven unchanged. No added retry, larger search, new source or manuscript score was introduced.']
    p=R/'REPORT.md';text=p.read_text(encoding='utf8');assert '## Independent source/selection audit' not in text;p.write_text(text+'\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(checks=len(checks),passed=True,scorer_maxima_verified=960,summary=summary),indent=2))
if __name__=='__main__':main()
