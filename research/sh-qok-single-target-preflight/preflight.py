from pathlib import Path
import csv, hashlib, json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
ATTACHMENT = Path(r'C:\Users\lewis\.codex\attachments\77a0efce-c4f8-4837-b4dd-1f6dd279e7ba\Pasted text.txt')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')

assert not (OUT / 'FREEZE.json').exists(), 'Preserve existing preflight; do not overwrite.'
original = ATTACHMENT.read_bytes()
(OUT / 'ORIGINAL-SPEC.txt').write_bytes(original)
manifest = json.loads((ROOT / 'complete-atlas-v56/SOURCE-MANIFEST.json').read_text())
metadata = next(Path(p) for p in manifest['hashes'] if 'Davis-hands' in p)
assert digest(metadata) == manifest['hashes'][str(metadata)]
rows = list(csv.DictReader(metadata.open(encoding='utf-8-sig')))
panels = {
    'P1': [r for r in rows if r['Scribe'] == '2' and r['Section'] != 'Balneological'],
    'P2': [r for r in rows if r['Scribe'] == '3' and r['Section'] != 'Starred paragraphs'],
    'P0': [r for r in rows if (r['Scribe'], r['Section']) in [('2', 'Balneological'), ('3', 'Starred paragraphs')]],
}
save('PANELS-METADATA-ONLY.json', {
    'status': 'METADATA_ONLY; freshness audit not completed; no token or outcome extraction',
    'source': str(metadata), 'sha256': digest(metadata),
    'panels': {p: {'folios': [r['Folio'] for r in rr], 'metadata': rr} for p, rr in panels.items()},
})
issues = [
    {
        'id': 'EXACT_ENGINE_AND_STRATA_CONFLICT',
        'spec': 'Sections 3, 5, 6 require folio x ending-family label exchangeability, and unchanged V>=80-qualified exact engine.',
        'source': ['sh-qok-support-boundary/PROTOCOL.json', 'sh-qok-four-body-boundary/run.py', 'sh-qok-all-interior/run.py'],
        'finding': 'Qualified engine selects disjoint position pairs within page/exact line length using exact bodies, then permutes discordant-row orientations within exact-body groups. Its V=sum k(n-k)/n is support for those assignment groups. It is not a folio x ending-family label-shuffle engine. Its event rule also excludes first-position origins and other endings. Four-body boundary qualification uses Bonferroni8.',
        'required_resolution': 'Choose the requested family-stratified question and qualify a new engine/support rule, or explicitly revise the estimand and event population to the existing engine. Neither is unchanged execution of this spec.',
    },
    {
        'id': 'H2_TARGET_LEAKAGE',
        'spec': 'Section 7 asks for qok-outcome prediction with attempt-B P/J unchanged.',
        'source': ['sh-qok-context-transfer-v1/run.py', 'sh-qok-context-transfer-v2/PROTOCOL.md'],
        'finding': 'Attempt B inherits y=int(origin.startswith(sh)). J includes qok, right-start widths 1..3, body-right-start and ending-right-start features of the next token. With y changed to next-qok, these are direct target leakage. Retaining original y instead answers a different predictive question.',
        'required_resolution': 'Explicitly retain sh/ch as target, or define and qualify new leakage-free qok-target feature maps. Do not interpret unchanged J as prediction of an unseen qok outcome.',
    },
    {
        'id': 'EXTRACTOR_POLICY_CONFLICT',
        'spec': 'Section 2 calls for qualified existing extractor but describes commas as separators and dropping comments.',
        'source': ['complete-atlas-v56/build.py', 'sh-qok-context-transfer-v1/run.py'],
        'finding': 'Existing atlas extractor masks words touching commas, replaces comments with an uncertainty marker, and rejects non-lowercase tokens. Context-transfer additionally restricts to shared H/F loci, Currier B and four ending families. The proposed panel/event population removes several of those restrictions.',
        'required_resolution': 'Freeze explicit parsing and population choices, with fixtures proving intended differences before extraction.',
    },
]
save('PROTOCOL.json', {
    'status': 'PREFLIGHT_BLOCKED_DESIGN_CONFLICT; not a scored attempt',
    'original_spec_file': 'ORIGINAL-SPEC.txt', 'original_spec_sha256': hashlib.sha256(original).hexdigest(),
    'original_spec_text': original.decode('utf-8-sig'),
    'changes_to_design': [], 'manuscript_outcomes_computed': False,
    'support_computed': False, 'issues': issues,
})
report = '''P1-H: NOT RUN — design conflict; effect, CI and Holm p unavailable.
P1-F: NOT RUN — design conflict; effect, CI and Holm p unavailable.
P2-H: NOT RUN — design conflict; effect, CI and Holm p unavailable.
P2-F: NOT RUN — design conflict; effect, CI and Holm p unavailable.

The frozen specification cannot be executed unchanged against the referenced engines. NOT RUN is a preflight state, not NOT ESTIMABLE, UNDERPOWERED or a negative result. No support gate has been evaluated.

'''
for issue in issues:
    report += f"## {issue['id']}\n\n{issue['finding']}\n\n{issue['required_resolution']}\n\nSources: " + ', '.join(issue['source']) + '\n\n'
report += '''## Preserved work and boundaries

The original attachment is preserved byte for byte and hashed. Panel folio lists were derived only from the hash-verified Davis metadata; see PANELS-METADATA-ONLY.json. No P1/P2 outcomes, support counts, effects or p-values were computed. No reserved zodiac signs were opened. No discovery-panel inferential scoring was performed. The full freshness audit, qualification, events and independent result verification remain unperformed and are not represented by placeholder success files.

Earlier source code and protocols were inspected to establish engine definitions. CURRENT-RESEARCH.txt was initially opened as an orientation index before its breadth was recognized; it contains historical outcome summaries. This is recorded as incidental exposure, not a completed membership-only freshness audit. No earlier P1/P2 numerical outcome tables were deliberately opened. Four-body SUMMARY.json was read for its synthetic qualification status and controls only.

The recommended revision is to preserve the requested H1 estimand, freeze a new ending-family conditional engine, and qualify it at actual outcome-blind panel geometry before any manuscript score. H2 needs a separately frozen target/feature decision; the current J inputs cannot predict next-qok without target leakage. Freshness must still be established: v77 explicitly reuses all v75 panels, whose source rules include Botanical material. Do not call those panels untouched without a folio audit. Even a successful retest would not by itself justify the original spec's claim of non-circular confirmation.
'''
(OUT / 'REPORT.md').write_text(report, encoding='utf-8')
sources = sorted({s for i in issues for s in i['source']} | {'sh-qok-support-rule/PROTOCOL.json', 'opening-order-audit-v75/run.py', 'opening-maxT-qualification-v77/rescore.py'})
save('FREEZE.json', {
    'utc': datetime.now(timezone.utc).isoformat(),
    'files': {str(p): digest(p) for p in [OUT / 'ORIGINAL-SPEC.txt', OUT / 'PROTOCOL.json', OUT / 'PANELS-METADATA-ONLY.json', OUT / 'REPORT.md', Path(__file__), metadata] + [ROOT / s for s in sources]},
})
print(json.dumps({'status': 'PREFLIGHT_BLOCKED_DESIGN_CONFLICT', 'panel_folios': {p: len(rr) for p, rr in panels.items()}, 'outcomes_computed': False}))
