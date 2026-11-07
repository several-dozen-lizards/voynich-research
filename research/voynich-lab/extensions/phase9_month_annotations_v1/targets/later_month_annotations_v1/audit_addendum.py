"""Post-outcome saved-witness support audit. No matcher imports or fitting."""
from pathlib import Path
from datetime import datetime, timezone
import collections, gzip, hashlib, json

T = Path(__file__).resolve().parent
R = T.parents[1]
def load(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value): (T/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf8')

assert not (T/'AUDIT_ADDENDUM.md').exists()
before = {str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file()}
earlier = load(R/'PRESERVATION_BEFORE.json')
assert all(sha(Path(p))==h for p,h in earlier.items())
assert all(sha(R/p)==h for p,h in load(T/'PREEXISTING_FILES.json').items())
assert all(sha(R/p)==h for p,h in load(R/'TARGET_MANIFEST.json')['files'].items())
assert all(sha(T/p)==h for p,h in load(T/'OUTPUT_HASHES.json').items())
reg = load(R/'REGISTRATION.json')
assert [p for p,h in reg['files'].items() if sha(R/p)!=h] == ['RUN_STATE.json']
assert load(R/'RUN_STATE.json')['native_gate']=='CLOSED'
assert load(R.parent/'phase8_alignment_v1'/'QUALIFICATION.json')['status']=='FAIL'
items = load(T/'TARGET_INPUT.json')['items']
names = load(R/'NORMALIZED_NAMES.json')['Occitan']
result = load(T/'RESULT.json')
observed = load(T/'OBSERVED.json')
month_names = {3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

def support(tag, model):
    usage = collections.defaultdict(set)
    used_by_month = collections.defaultdict(set)
    mapping = {(g,p):c for g,p,c in model['mapping']}
    for match in model['matched']:
        month = items[match['item']]['month_number']
        word = names[str(month)]
        assert len(word)==len(match['label'])
        for j,(p,c) in enumerate(zip(word, match['label'])):
            g = 'A' if model['family']=='mono' else 'B' if j==0 else 'E' if j==len(word)-1 else 'M'
            assert mapping[g,p]==c
            assignment = (g,p,c)
            usage[assignment].add(month)
            used_by_month[month].add(assignment)
    assert set(usage)=={tuple(x) for x in model['mapping']}
    assignments = [dict(group=g,plain=p,cipher=c,months=sorted(ms),distinct_month_support=len(ms)) for (g,p,c),ms in sorted(usage.items())]
    fully = [month for month,entries in used_by_month.items() if all(len(usage[a])>1 for a in entries)]
    may = sum(items[x['item']]['month_number']==5 for x in model['matched'])
    return dict(witness=tag,language=model['language'],family=model['family'],saved_score=model['score'],
        matched=model['matched'],distinct_matched_months=sorted(used_by_month),may_panel_points=may,
        extra_duplicate_may_points=max(0,may-1),assignments=assignments,
        shared_assignment_count=sum(len(ms)>1 for ms in usage.values()),
        single_month_assignment_count=sum(len(ms)==1 for ms in usage.values()),
        fully_cross_supported_months=sorted(fully),
        month_unique_assignments={str(month):[list(a) for a in sorted(entries) if len(usage[a])==1] for month,entries in sorted(used_by_month.items())})

witnesses = [support('Observed',m) for m in observed['models'] if m['language']=='Occitan' and m['family']!='naibbe']
tops = []
for seed in [9011,9013,9019,9029,9041]:
    with gzip.open(T/f'NULLS_s{seed}.jsonl.gz','rt',encoding='utf8') as f:
        for line in f:
            record = json.loads(line)
            if record['score']==4:
                tops.append((seed,record['index']))
                witnesses += [support(f'{seed}/{record["index"]}',m) for m in record['models'] if m['score']==4]
assert tops==[(9013,98),(9019,3),(9019,71),(9041,2),(9041,97)]
assert len(witnesses)==9 and all(not w['fully_cross_supported_months'] for w in witnesses)
assert all(a['plain']==a['cipher'] for w in witnesses for a in w['assignments'] if a['distinct_month_support']>1)
write('AUDIT_ADDENDUM_DATA.json', dict(status='DESCRIPTIVE_SAVED_WITNESS_AUDIT',new_fits=0,
    month_definition='Candidate month at destination panel; repeated May counted once for support',
    support_definition='Same saved assignment used in at least two distinct matched candidate months; position group is part of assignment',
    fully_supported_definition='Every assignment used by a matched month is also used by at least one other distinct matched month',
    top_null_assignments=[list(x) for x in tops],witnesses=witnesses))

lines = ['# Phase 9 audit addendum: duplicate labels and mapping support', '',
 'This is a post-outcome descriptive audit of saved witnesses only. No fitting, optimizer calls, new shuffle draws, rule changes, registration, or revised significance tests were performed. It supplements the sealed target report and does not replace any result or receipt.', '',
 '## Shuffle result and its scope', '',
 'The registered panel statistic remains 5/12 for the observed Occitan positional fit (4/12 for observed Occitan monoalphabetic). Each of the five frozen banks contains 99 shuffles; none reaches 5, giving p=.01 separately in each bank for the full maximum over languages, families, and fixed Naibbe tables. These are repeated Monte Carlo banks on one target, not independent manuscript replications; .01 is each bank\'s resolution floor. No banks are pooled or selected here.', '',
 'The null preserves the label multiset, including both May labels, and refits every shuffled assignment by the same search rule. Duplicate May is therefore present on both sides of the registered comparison. Its presence is not an unaccounted difference in label counts, but the panel statistic weights a repeated identical month-label constraint twice. The shuffled result is evidence of association between the assigned month candidates and annotations under this finite matching procedure; it is not evidence of out-of-sample mapping generalization, an annotator language, a historical cipher, or native-script decipherment.', '',
 '## Duplicate-May contributions and distinct-month support', '',
 'Month means the candidate month at the destination panel, even if its assigned shuffled annotation originated from another month. Assignment identity includes the position group: B=beginning, M=interior, E=end; A=global monoalphabetic. A shared assignment must occur in at least two distinct matched candidate months. May\'s two panels count once for support. Repetition within one word or month also counts once. A fully cross-supported month would require every one of its used assignments to occur in another distinct matched month.', '',
 '| Witness | Family | Saved score | May points | Extra duplicate May point | Distinct matched months | Shared / single-month assignments | Fully cross-supported months |',
 '|---|---|---:|---:|---:|---:|---|---:|']
for w in witnesses:
    lines.append(f"| {w['witness']} | {w['family']} | {w['saved_score']} | {w['may_panel_points']} | {w['extra_duplicate_may_points']} | {len(w['distinct_matched_months'])} | {w['shared_assignment_count']} / {w['single_month_assignment_count']} | 0 |")
lines += ['', 'The selected top-null witness is monoalphabetic for 9019/3 and 9041/97; each also has the saved tied positional witness shown above. The five assignments shown are all saved null assignments attaining the global null maximum of four. The other banks peak at three.', '',
 'Both observed fits receive two points from the identical `mai -> may` match, with the second contributing no new mapping constraint. Four of five top null assignments do likewise; 9013/98 matches only one May panel. These counts describe the saved witnesses. They do not constitute deduplicated reoptimization or recalibrated p-values.', '',
 '## Mapping generalization boundary', '',
 '**No matched month is fully cross-supported in any of the nine saved witnesses**, counting both observed fits and all tied top-null models. Every matched month requires at least one assignment used by no other distinct matched month. All shared assignments are identity substitutions; every nonidentity substitution has support from just one distinct candidate month.', '',
 'For the observed monoalphabetic witness, March uniquely supplies `r -> r`, May `i -> y`, and August `g -> u`, `o -> g`, and `t -> t`. For the observed positional witness, the added June match uniquely supplies B:`i -> j`, M:`u -> o`, M:`n -> n`, and E:`h -> g`. Thus June does not follow entirely from assignments supplied by the other matched months.', '',
 'This support audit is conditional on each stored optimal witness. It does not enumerate all equally optimal mappings, refit after withholding a month, or test predictions on held-out names. Zero fully supported months limits what can be claimed from these witnesses; it does not establish that every alternative optimum or encoding family lacks predictive ability. Calibration recovery on synthetic controls and the target shuffle association do not fill this generalization gap.', '',
 '## Per-month assignments lacking support elsewhere', '',
 'Each entry below lists all assignments unique to that month within that saved witness. Machine-readable support sets for every assignment are retained in AUDIT_ADDENDUM_DATA.json.', '',
 '| Witness / family | Month | Assignments unique to this month |', '|---|---|---|']
for w in witnesses:
    for month, assignments in w['month_unique_assignments'].items():
        text=', '.join(f'{g}:{p}->{c}' for g,p,c in assignments)
        lines.append(f"| {w['witness']} / {w['family']} | {month_names[int(month)]} | `{text}` |")
lines += ['', '## Preserved status and receipts', '',
 '**Native tracks remain CLOSED. Phase 8 remains FAIL.** No target track is opened by this audit. All pre-existing artifacts, including the target manifest, results, original report, filename erratum, calibration records, output seals, and completion receipts, are retained byte-for-byte.', '',
 'The original calibration strict registration check still fails solely for the previously documented mutable RUN_STATE.json entry. That defect is not repaired or relabeled PASS. The addendum has its own preservation receipt; this is a saved-witness arithmetic and documentation audit, not a new scientific gate or registration.', '']
(T/'AUDIT_ADDENDUM.md').write_text('\n'.join(lines),encoding='utf8')
assert all(sha(R/p)==h for p,h in before.items())
assert all(sha(Path(p))==h for p,h in earlier.items())
write('AUDIT_ADDENDUM_RECEIPT.json',dict(status='COMPLETE_SAVED_WITNESS_ADDENDUM',created_at_utc=datetime.now(timezone.utc).isoformat(),
    new_fits=0,new_nulls=0,new_registration=False,existing_artifacts_changed=0,
    preexisting_phase9_files=len(before),earlier_preserved_files=len(earlier),
    prior_file_hashes=before,addendum_files={p:sha(T/p) for p in ['audit_addendum.py','AUDIT_ADDENDUM.md','AUDIT_ADDENDUM_DATA.json']},
    native_tracks='CLOSED',Phase8='FAIL_PRESERVED',original_receipt_defect='PRESERVED_MUTABLE_RUN_STATE_ONLY',
    fully_cross_supported_months_all_witnesses=0))
print(json.dumps(dict(status='COMPLETE',witnesses=len(witnesses),top_null_assignments=len(tops),changed_existing_files=0,new_fits=0,native_tracks='CLOSED')))
