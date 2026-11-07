"""Post-outcome reporting and output seal only. No fits, scoring, or new nulls."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

T = Path(__file__).resolve().parent
R = T.parents[1]
def load(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, obj): (T/name).write_text(json.dumps(obj, indent=2)+'\n', encoding='utf8')

assert not (T/'COMPLETION_RECEIPT.json').exists()
manifest = load(R/'TARGET_MANIFEST.json')
assert all(sha(R/p)==h for p,h in manifest['files'].items())
prior = load(T/'PREEXISTING_FILES.json')
assert all(sha(R/p)==h for p,h in prior.items())
result = load(T/'RESULT.json')
audit = load(T/'AUDIT.json')
observed = load(T/'OBSERVED.json')
assert result['status']=='COMPLETE' and audit['changed_preexisting_files']==0
assert audit['status']=='PASS_SAVED_TARGET_WITNESSES_ARITHMETIC_AND_PRESERVATION'
rows = ['# Later month annotation target: frozen-rule result', '',
 'The maximum is **5/12 exact item matches (41.7%)**, using the Occitan candidate list and positional substitution. Each of the five frozen 99-shuffle banks gives **p = .01** for the full language/family/table maximum. This is a result for the later Latin-script annotations only; it does not identify the annotator\'s language or interpret native-script text.', '',
 'The target manifest was sealed before target optimization at '+manifest['sealed_at_utc']+'. Its SHA256 is `'+sha(R/'TARGET_MANIFEST.json')+'`. Original rules, period names, normalization, annotation alternatives, codebooks, and shuffle assignments were unchanged. The observed target was fitted once with all 32 frozen models; each shuffle was refitted with the same full search.', '',
 '## All language by family scores', '',
 'Scores count whole exact matched items out of 12. Naibbe is the maximum over the six frozen published tables.', '',
 '| Candidate language | Monoalphabetic | Naibbe verbose | Positional substitution |',
 '|---|---:|---:|---:|']
for lang in ['Latin','Italian','German','Occitan']:
    cells={x['family']:x['score'] for x in result['language_family_scores'] if x['language']==lang}
    rows.append(f"| {lang} | {cells['mono']}/12 | {cells['naibbe']}/12 | {cells['position']}/12 |")
rows += ['', 'Every Naibbe submodel is retained below (exact item counts):', '',
 '| Candidate language | alpha | beta1 | beta2 | beta3 | gamma1 | gamma2 |', '|---|---:|---:|---:|---:|---:|---:|']
for lang in ['Latin','Italian','German','Occitan']:
    cells={x['table']:x['score'] for x in observed['models'] if x['language']==lang and x['family']=='naibbe'}
    rows.append('| '+lang+' | '+' | '.join(str(cells[k]) for k in ['alpha','beta1','beta2','beta3','gamma1','gamma2'])+' |')
rows += ['', '## Max-statistic shuffle null', '',
 'For every shuffled assignment, the statistic is the maximum over all four languages and all three families, including all six Naibbe tables. Labels are shuffled among the twelve zodiac panels within section. Each bank uses its original 99 frozen assignments. The p-value is `(1 + count(null >= observed)) / 100`.', '',
 '| Frozen seed | Draws | Null range | Mean | Null >= 5 | p | Histogram (score: count) |', '|---|---:|---|---:|---:|---:|---|']
for bank in result['null_banks']:
    hist=', '.join(f'{k}: {v}' for k,v in bank['null_histogram'].items())
    rows.append(f"| {bank['seed']} | {bank['null_draws']} | {bank['null_min']}–{bank['null_max']} | {bank['null_mean']:.4f} | {bank['null_at_least_observed']} | {bank['p']:.2f} | {hist} |")
rows += ['', 'All five banks are reported separately, without selecting a seed, pooling p-values, or adding a decision gate. They measure Monte Carlo variation on the same target and are not independent manuscript replications. The value .01 is the resolution floor of each 99-shuffle test.', '',
 '## Saved optimal witness', '',
 'The selected model uses separate injective beginning/interior/end maps, each consistent across all items. Its five matched items are March (`Mars` -> `mars`, f70v2), May (`Mai` -> `may`, f71v and f72r1), June (`Junh` -> `jong`, f72r2), and August (`Agost` -> `augst`, f72v3), with the frozen automatic normalization applied. The two May panels count twice under the registered item statistic; these are five panel matches spanning four distinct months. The twelve-panel target spans ten distinct month identities.', '',
 'The Occitan positional model is the only language/family/table submodel attaining five; this does not establish a unique optimal character mapping. The full saved mapping is in OBSERVED.json and RESULT.json. This fit demonstrates compatibility with the frozen exact-match rule, not a historical cipher reconstruction.', '',
 '## Scope, provenance, and preserved failures', '',
 'Annotation readings and panel assignments come from the frozen source table at [Voynich.nu, Writing](https://www.voynich.nu/writing.html). Parenthesized source letters are included or omitted automatically by the frozen rule; no manual spelling corrections or newly restored letters were added. Candidate spellings and their period citations remain in the original PERIOD_NAMES.json and SOURCES.md. Historical forms span different witnesses, dates, and regions; French is outside the registered candidate set. Length, repeated-character constraints, spelling choices, abbreviation alternatives, and the duplicated panels all affect this exact-match statistic. Zero scores do not exclude a language or all verbose cipher systems. The six tested Naibbe tables are a fixed published subfamily and are not blind to Voynich statistics.', '',
 'The saved-witness audit checked 15,872 model witnesses and 495 null records, with no new fitting. It verified the mappings/segmentation witnesses, score arithmetic, full maxima, shuffle assignments, p-values, and preservation hashes. All 1,353 pre-existing calibration files and 1,837 earlier preserved files remain byte-identical.', '',
 '**Native tracks remain CLOSED. Phase 8 remains FAIL.** The original calibration registration still fails its strict full-manifest check solely because mutable RUN_STATE.json was included in it and later changed during calibration. That receipt defect and its documented initial-state reconstruction remain preserved; the target audit does not relabel the original strict receipt as PASS. The original calibration RUN_STATE.json is unchanged by this target run; TARGET_RUN_STATE.json records the separate authorized target completion.', '',
 'Machine-readable evidence: TARGET_MANIFEST.json in the parent calibration directory; local RESULT.json, OBSERVED.json, LANGUAGE_FAMILY_SCORES.json, NULLS_s*.jsonl.gz, AUDIT.json, OUTPUT_HASHES.json, and COMPLETION_RECEIPT.json. No translation claims are made. Work stops here.', '']
(T/'REPORT.md').write_text('\n'.join(rows), encoding='utf8')
outputs={p.name:sha(p) for p in sorted(T.iterdir()) if p.is_file() and p.name not in ['OUTPUT_HASHES.json','COMPLETION_RECEIPT.json']}
write('OUTPUT_HASHES.json', outputs)
write('COMPLETION_RECEIPT.json', dict(status='COMPLETE_TARGET_WITH_DOCUMENTED_ORIGINAL_RECEIPT_DEFECT',
    completed_at_utc=datetime.now(timezone.utc).isoformat(), target_manifest_sha256=sha(R/'TARGET_MANIFEST.json'),
    output_hashes_sha256=sha(T/'OUTPUT_HASHES.json'), observed_maximum=result['observed_maximum'], denominator=12,
    bank_p_values={str(b['seed']):b['p'] for b in result['null_banks']}, native_tracks='CLOSED',
    Phase8_status='FAIL_PRESERVED', original_strict_receipt='FAIL_MUTABLE_RUN_STATE_ONLY_PRESERVED',
    audit_status=audit['status'], reporting_only=True, stop=True))
assert all(sha(T/p)==h for p,h in load(T/'OUTPUT_HASHES.json').items())
assert all(sha(R/p)==h for p,h in manifest['files'].items())
assert all(sha(R/p)==h for p,h in prior.items())
print(json.dumps(load(T/'COMPLETION_RECEIPT.json'), indent=2))
