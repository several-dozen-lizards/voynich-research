"""Verify delivery hashes without parsing source/reserve bodies; append-only research index."""
from pathlib import Path
import json,sys
from core import sha
ROOT=Path(__file__).resolve().parent;HERE=ROOT/'held-definition-development'
for base in (ROOT,HERE):
    manifest=json.loads((base/'DELIVERY-HASHES.json').read_text())
    bad=[name for name,digest in manifest.items() if not (base/name).is_file() or sha(base/name)!=digest]
    assert not bad,bad
    print(json.dumps(dict(manifest=str(base/'DELIVERY-HASHES.json'),files=len(manifest),mismatches=bad)))
assert not (ROOT/'FREEZE.json').exists()
if '--update-current' in sys.argv:
    path=ROOT.parent/'CURRENT-RESEARCH.txt';text=path.read_text(encoding='utf-8-sig')
    marker='2026-10-25 — Voynich v5 synthetic log-odds arithmetic qualification'
    print('Index tail before append:\n'+text[-1000:])
    if marker not in text:
        with path.open('a',encoding='utf-8') as handle:handle.write('\n\n'+marker+'\n'+
            'held-definition-development/REPORT.md:16synthetic engineering tests and250independent80-digit Decimal comparisons pass. '
            'MH pooled log-OR reference preserves unsupported/infinite states without pseudocounts; candidate H2 ratio of log effects is undefined at an exact-null aggregate effect. '
            'User-approved log-odds scale retained; no scientific event builder, uncertainty coverage or targets adopted. '
            'No manuscript, source or G1-G6-output counts used. H3 unresolved; fresh reserves unparsed; held/recovery locks retained. '
            'Source-cut2 delivery verified/preserved before publication.\n')
        print('Appended arithmetic qualification status.')
