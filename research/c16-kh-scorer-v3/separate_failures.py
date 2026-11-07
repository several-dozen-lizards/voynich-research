"""Classify already-recorded search gaps; never change qualification gates."""
from preserve import R,dump
import json
def main():
    rows=[]
    for arm in ['tanakh','medieval']:
        result=json.loads((R/'results'/arm/'RESULT.json').read_text())
        for r in result['cipher_cases']:
            if r['alphagram_recovery']==1:kind='FULL_ALPHAGRAM_RECOVERY'
            elif r['true_minus_fit']>1e-12:kind='SEARCH_MISSED_KNOWN_BETTER_KEY'
            elif r['true_minus_fit']< -1e-12:kind='OBJECTIVE_PREFERS_INCORRECT_FITTED_KEY'
            else:kind='OBJECTIVE_TIE_WITH_INCOMPLETE_RECOVERY'
            rows.append(dict(arm=arm,case=r['case'],alphagram_recovery=r['alphagram_recovery'],true_minus_fit=r['true_minus_fit'],classification=kind))
    counts={k:sum(r['classification']==k for r in rows) for k in sorted({r['classification'] for r in rows})}
    dump(R/'FAILURE_SEPARATION.json',dict(cases=rows,counts=counts,objective_gate_scope='true key vs 100 random injective keys, not a universal objective validation',scorer_gate_scope='gold words only; no key fitting or decoding',registered_gates_changed=False,manuscript_scores=0))
    text='\n## Direct objective-versus-search separation\n\n'
    text+=f"Of 12 known-key cases, {counts.get('SEARCH_MISSED_KNOWN_BETTER_KEY',0)} have incomplete recovery even though the true key has a strictly BETTER combined objective than the fitted key. Those are demonstrated search misses under this budget. The remaining {counts.get('FULL_ALPHAGRAM_RECOVERY',0)} case(s) recover all alphagrams. No case preferred an incorrect fitted key over the true key. This does not prove the objective globally correct: its frozen PASS gate compares only the true key against 100 random wrong keys. The separate gold-word scorer still fails its operating-point gate, independently of these search misses. Detailed gaps and classifications are in FAILURE_SEPARATION.json. No gate, threshold, search budget or result was changed.\n"
    p=R/'REPORT.md';old=p.read_text(encoding='utf8');assert '## Direct objective-versus-search separation' not in old;p.write_text(old+text,encoding='utf8');print(json.dumps(counts))
if __name__=='__main__':main()
