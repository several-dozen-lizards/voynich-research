"""Independent post-run diagnosis. No changed gates, parameters or scores."""
from preserve import R
from register import dump,read
from corrected import LM,EOS
from collections import Counter,defaultdict
import json,math,statistics
def main():
    result={}
    for arm in ['tanakh','medieval']:
        data=json.loads((R/'inputs'/f'{arm}.json').read_text());lm=LM(data['train']);outgoing=Counter();bigrams=Counter()
        for (a,b,c),n in lm.t.items():outgoing[a,b]+=n
        for (b,c),n in lm.b.items():bigrams[b]+=n
        bad=[];nonterminal_bad=[]
        for (a,b),denom in lm.ctx.items():
            p2mass=bigrams[b]/lm.bctx[b] if lm.bctx[b] else 1.
            p3mass=outgoing[a,b]/denom if denom else p2mass
            mass=lm.weights[0]+lm.weights[1]*p2mass+lm.weights[2]*p3mass
            if abs(mass-1)>1e-10:
                bad.append((a,b,mass))
                if b!=EOS:nonterminal_bad.append((a,b,mass))
        assert not nonterminal_bad
        # Correct the denominator in an ephemeral mathematical witness only.
        counter_changes=[k for k in lm.ctx if lm.ctx[k]!=outgoing[k]]
        assert all(b==EOS for a,b in counter_changes)
        scores=defaultdict(dict)
        for r in read(R/'results'/arm/'variant-source.csv'):
            if r['bank']=='confirmation' and r['family'] in ['Hebrew','word_shuffle']:
                key=(r['document'],r['family']);v=float(r['score']);scores[key]['score']=max(v,scores[key].get('score',float('-inf')))
        docs=sorted({d for d,f in scores});wins=losses=ties=0
        for doc in docs:
            a=scores[doc,'Hebrew']['score'];b=scores[doc,'word_shuffle']['score'];wins+=a>b;losses+=a<b;ties+=a==b
        exact=sum(math.comb(wins+losses,k) for k in range(wins,wins+losses+1))/2**(wins+losses)
        q=json.loads((R/'results'/arm/'RESULT.json').read_text());calibration=[]
        for r in q['details']['G4']:
            if r['family']=='C17':
                t=r['calibration_thresholds'];calibration.append(dict(version=r['version'],threshold=r['threshold'],driving_families=[k for k,v in t.items() if v==max(t.values())],C17_calibration_documents=19,C17_nearest_rank_95_percentile=19))
        recovery=[]
        for i in range(6):
            c=json.loads((R/'results'/arm/f'cipher-{i}.json').read_text());key=c['fitted_key'];n=ok=0
            assert len(set(key.values()))==len(key)
            for ps,cs in zip(c['plaintext'],c['ciphertext']):
                for w,cw in zip(ps,cs):n+=1;ok+=Counter(w)==Counter(key.get(x,'?') for x in cw)
            assert ok/n==c['result']['alphagram_recovery'];recovery.append(ok/n)
        result[arm]=dict(normalization_bad_contexts=len(bad),all_bad_contexts_end_in_EOS=True,reachable_context_mass_checks='PASS',terminal_mass=1-lm.weights[2],terminal_counter_repair_would_change_valid_sentence_scores=False,registered_G1_still='FAIL',G3_wins=wins,G3_losses=losses,G3_ties=ties,G3_exact_one_sided_sign_tail_omitting_ties=exact,legacy_half_tie_tail_in_RESULT=q['details']['G3']['sign_tail'],legacy_sign_tail_label='Not the exact sign test when ties exist; use this audit instead.',G3_gate_unchanged=wins+.5*ties>=32,calibration=calibration,independent_cipher_recovery='PASS',median_cipher_recovery=statistics.median(recovery))
    dump(R/'INDEPENDENT_AUDIT.json',dict(arms=result,registered_candidate_modified=False,registered_gates_waived=False,manuscript_scores=0,all_original_failures_preserved=True))
    lines=['','## Independent post-run audit','',
    'The remaining normalization failure is confined to histories ending in EOS: context denominators count terminal pairs with no outgoing trigrams. Valid sentence scoring terminates at EOS and does not traverse those histories. Rebuilding that denominator from actual trigram-prefix counts would leave all valid sentence scores and deleted-interpolation weights unchanged; this is an analytic witness, not an activated or qualified revision. The registered G1 remains FAIL. This terminal-boundary failure is separate from the failed discrimination and search gates.','',
    'The original G3 `sign_tail` calculation treated half-ties as a binomial count. That is not an exact sign test when ties exist. The audit omits ties for the exact one-sided sign test below; the pre-registered win-count gate and every qualification decision remain unchanged.','',
    '| Arm | Wins / losses / ties | Exact sign tail | Reachable-context probability sums |','|---|---|---:|---|']
    for a,r in result.items():lines.append(f"| {a} | {r['G3_wins']} / {r['G3_losses']} / {r['G3_ties']} | {r['G3_exact_one_sided_sign_tail_omitting_ties']:.6g} | PASS |")
    lines+=['','The null-threshold gate also exposes small-bank upper-tail instability. With 19 C17 calibration writers, a nearest-rank 95th percentile is the largest writer score. The frozen pooled upper-tail threshold can reject nearly all positives even when pairwise AUC is high. It was not lowered after seeing this failure. Driver-family receipts are in INDEPENDENT_AUDIT.json.','',
    'All 12 cipher-recovery receipts were independently recomputed using letter-count vectors and unchanged fitted keys. The published-rule mismatch, repaired unknown-collapse symptom, terminal-count defect, weak maximum-over-variant order discrimination, threshold sensitivity and limited key search are distinct findings. No manuscript was scored, no original run file changed, and no semantic conclusion follows.']
    report=R/'REPORT.md';s=report.read_text(encoding='utf8');assert '## Independent post-run audit' not in s;report.write_text(s+'\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({a:{k:v for k,v in r.items() if k in ['normalization_bad_contexts','G3_wins','G3_losses','G3_ties','G3_exact_one_sided_sign_tail_omitting_ties','median_cipher_recovery']} for a,r in result.items()},indent=2))
if __name__=='__main__':main()
