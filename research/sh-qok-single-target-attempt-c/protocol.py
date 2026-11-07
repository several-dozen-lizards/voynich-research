from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

R=Path(__file__).resolve().parent
P=R.parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x): (R/name).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def freeze():
    assert not (R/'FREEZE.json').exists()
    manifest=json.loads((P/'complete-atlas-v56/SOURCE-MANIFEST.json').read_text())
    sources={p:h for p,h in manifest['hashes'].items() if 'text16e6.original.evt' in p or 'Davis-hands' in p}
    assert all(sha(p)==h for p,h in sources.items())
    original=P/'sh-qok-single-target-preflight/ORIGINAL-SPEC.txt'
    (R/'ORIGINAL-SPEC.txt').write_bytes(original.read_bytes())
    protocol=dict(
        attempt='C: new family-stratified conditional engine and leakage-free H2; authorized after blocked preflight',
        frozen_utc=datetime.now(timezone.utc).isoformat(),original_spec_sha256=sha(original),
        scope='Frozen single-target retest. Previously searched material is NOT untouched confirmation. H/F are alternate readings; never pool.',
        sources=sources,
        panels='P1 Davis Scribe exactly 2, Section != Balneological; P2 exactly 3, Section != Starred paragraphs; P0 the two excluded discovery groups DESCRIPTIVE ONLY. Folio means exact CSV Folio/physical page, not numbered leaf. P0 additionally reported separately by hand/section.',
        tokenizer='New explicitly qualified literal-spec tokenizer: strip inline # remainder, remove {non-nested comments} and ! and whitespace; split on .,-=; omit empty boundary pieces. Only full [a-z]+ tokens known; *,%,?,other signs => None slot. Commas separate rather than poisoning adjacent words; no joins across unknowns. No shared-H/F-locus or Currier-B restriction; all paragraph P-unit source rows, each reading separately. Duplicate source locators abort.',
        origins='All sh/ch starts, including first word; not line-final; following known on same line. cth/ckh/cph/cfh cannot match. Ending eey,edy,ey,y longest first, else other retained.',
        h1=dict(question='P(next qok | sh) > P(next qok | ch) conditional physical folio x ending family',
            engine='Independent uniform sh/ch-label permutations within each stratum fixing origin counts and qok successes. Total sh successes has convolution of hypergeometric distributions. One-sided >= observed; degenerate distribution => p=null, not evidence.',
            effect='Mantel-Haenszel risk difference: sum_s [ns*nc/(ns+nc)]*(a/ns-b/nc) / sum_s ns*nc/(ns+nc). Unsupported strata contribute zero. Bootstrap physical folios with replacement 4999 times, recomputing this ratio; percentile 2.5/97.5, seed240100+cell index.',
            support='New engine assignment-support V=sum ns*nc/(ns+nc), NOT inherited calibration from body-position engine. Freeze blind. Gate V>=80, >=8supported physical pages, maxpageV/V<=.25; failed cells NOT ESTIMABLE; no inferential score.',
            correction='Holm fixed family4 P1-H,P1-F,P2-H,P2-F; untested cells occupy conservative p=1 internally but reported p=null. Primary requires both P1 readings effect>0 and adjustedp<.05. No inferential P0 tests.',
            qualification='200 independent seeded outcome realizations per actual cell x null_low(.2),null_high(.6),additive,junction_only,positive(.2+.15*sh). Exact observed origin/position/body/stratum geometry, no observed qok labels. additive logit=-1+page±.7+line±.7+.7*normalizedposition, independent draws; junction rate .1+.5*(final sign==y), no direct prefix effect. Fixed sh allocation means these test exchangeability robustness, not only a sharp exchangeable null. Record any induced confounding as qualification failure, not engine arithmetic failure. alpha=.05/4 conservative planned Holm boundary. Each null Wilson95upper<=.05. Positive Wilson95lower>=.80. Null failure blocks H1 manuscript inferential score; positive failure UNDERPOWERED, still score if null pass. Do not tune/fix after qualification.'),
        h2=dict(question='Leakage-free prediction of next-qok; J-P held-out logloss gain',
            target='next-qok, separate from sh/ch origin prefix',
            P='Categorical origin body after prefix, ending family, prefix sh/ch, position, reverse position, line length, body-position,body-reverse,ending-length-position; no follower or any future context.',
            J='P plus origin final1/final2, preceding known word final1/final2 (EDGE/UNKNOWN preserved), and prefix x origin final1/final2 and prefix x previous final1/final2. These are available before follower. P includes prefix main effect to avoid mistaking simple sh effect for junction gain. No right-start, qok, body-right, ending-right or future token features.',
            fitting='Attempt-B C=.25 liblinear logistic, max_iter2000,tol1e-7, five physical-folio folds assigned SHA256 context-transfer-v1|folio. Training-only DictVectorizer. Inner training folios split SHA256 inner|folio; sequential convex constant->P->J backoff from attempt B with 1/n validation gain cutoff. Refit on outertrain. Single-class training rawmodel falls back to add-half constant, documented; convergence errors block.',
            inference='Equal-folio mean logloss(P)-logloss(J) in bits; one-sided exact sign-flip on folio mean gains if <=18folios, otherwise 65535 seeded signs plus-one. This is a model-comparison diagnostic relying on sign symmetry; CV dependence is assessed only in limited controls. Holm separate fixed4. Adequacy P loss<=constant+.01bits and >=200events,>=8folios,>=30each outcome; failures inadequate baseline/support, not negative.',
            qualification='Supported cells only; 100trials per actual cell x independent low/high, additive, junction_only,positive. Same H1 generators except H2 positive logit=-1+2.5*(2sh-1)*(2(final==y)-1); this is a prespecified strong interaction, not +15 point H1 effect. H2 junction-only is a recovery/power diagnostic not a false-positive null: it belongs to the alternative predictive question. low/high/additive false-positive upperWilson<=.05 at .05/4; interaction positive lowerWilson>=.80. Null failure blocks H2 inference; positive failure UNDERPOWERED. Qualification does not establish equivalence to old attempt-B pattern.'),
        sensitivity='Apply original weak-score-v2 unchanged to original-target sh/ch events from new eligible cells; its qok input is valid for that original target, not H2. Preserve its own support/adequacy gates. Label transported exploratory sensitivity because new population is outside old qualification; cannot rescue H1/H2. P0 not sensitivity-scored.',
        ordering='Freeze code/protocol/source hashes; metadata-only freshness audit and blinded support; freeze SUPPORT/PANELS/MASKED; synthetic controls and qualification hashes; ONLY THEN reparse source outcomes for effects/descriptives and qualified tests. No reserved zodiac sign files.',
        failures='Keep all controls, support failures, blocked inference and numerical exceptions. No post-outcome changes. Descriptive effects/CI reported even unsupported, as requested, without treating them as tests.',
        exposure='Preflight opened historical research index with summaries; no outcome-blind historical-unexposed claim. Audit only metadata source rows and source code; no old P1/P2 outcome tables.'
    )
    save('PROTOCOL.json',protocol)
    files=[R/n for n in ['protocol.py','engine.py','run.py','verify.py','PROTOCOL.json','ORIGINAL-SPEC.txt']]
    files += [P/'complete-atlas-v56/SOURCE-MANIFEST.json',P/'frequency-atlas-v48/rows.json',P/'opening-order-audit-v75/run.py',P/'opening-maxT-qualification-v77/rescore.py',P/'sh-qok-context-transfer-v1/run.py',P/'sh-qok-context-transfer-v2/run.py',P/'sh-qok-weak-score-v1/core.py',P/'sh-qok-weak-score-v2/core.py']
    save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in files}|sources))

if __name__=='__main__': freeze()
