"""Read-only delivery verification; optional append-only project research index update."""
from pathlib import Path
import json,sys
from source_cut2 import ROOT,CUT
from core import sha
manifest=json.loads((ROOT/'DELIVERY-HASHES.json').read_text())
bad=[name for name,digest in manifest.items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
assert not bad,bad
assert not (ROOT/'FREEZE.json').exists() and not (CUT/'FREEZE.json').exists()
print(json.dumps(dict(delivery_files=len(manifest),mismatches=bad,H3='UNRESOLVED',held_scoring=False,fresh_reserve_bodies_parsed=0)))
if '--update-current' in sys.argv:
    path=ROOT.parent/'CURRENT-RESEARCH.txt';text=path.read_text(encoding='utf-8-sig')
    marker='2026-10-25 — Voynich v5 independent development source cut 2'
    print('Current index tail before append:\n'+text[-1300:])
    if marker not in text:
        entry='\n\n'+marker+'\n'+(
            'Built system-types-v5/source-cut-2/REPORT.md: all seven prior size cases supported with source/register limits; all exposed literal units attested in new development. '
            '60/60 codebook capacity and22/22 source-entrypoint checks pass;50/50 engineering tests pass with process-scoped64MB Java heap. '
            '48 fresh-reserve files separately byte-sealed; zero bodies parsed or scored. Old503-file delivery verified/preserved, old failures retained. '
            'Italian ä remains new-Dante-section only (Petrarch supplies independent x but no ä); broad Latin glyph coverage is not medical-only qualification. '
            'H3 unresolved; no claim FREEZE, held scores, manuscript fit or full recovery.\n')
        with path.open('a',encoding='utf-8') as handle:handle.write(entry)
        print('Appended source-cut2 status without rewriting other research entries.')
