"""Finish publication navigation and quarantine undeclared staging leftovers."""
import collections, json, os, shutil
from pathlib import Path
from urllib.parse import quote

TOOLS=Path(__file__).resolve().parent
ROOT=TOOLS.parents[1]
OUT=ROOT/'github-export/voynich-research'
rows=json.loads((OUT/'catalog/FILES.json').read_text(encoding='utf-8'))
expected={r['published_path'] for r in rows if r['published_path']}
quarantined=[]
for base,dirs,files in os.walk(OUT/'research'):
    for name in files:
        p=Path(base)/name; rel=p.relative_to(OUT).as_posix()
        if rel in expected: continue
        destination=TOOLS/'quarantine'/rel
        if not p.resolve().is_relative_to((OUT/'research').resolve()) or not destination.resolve().is_relative_to(TOOLS.resolve()): raise RuntimeError('unsafe staging path')
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): raise RuntimeError('quarantine destination already exists: '+rel)
        p.rename(destination); quarantined.append(rel)

def theme(name):
    if name.startswith('sh-qok'): return 'sh/qok support, transfer and mechanism controls'
    if name.startswith(('image-','v4-','label-objects','v3-')): return 'Image registration, labels and adjudication'
    if name.startswith(('contextual-role','context-tests','c16','system-types','t1-','bc-adapter','bq2','currier-a','priority-continuation','continuation-v73')): return 'Source controls, semantic-role instruments and qualification'
    if name.startswith(('astro','zodiac','wheel','oal','g-ending','e-run','fp-boundary','gallows')): return 'Astronomical, visual and glyph-context investigations'
    if name.startswith(('herbal','plant','daro','name-','ordered-name')): return 'Herbal, historical-name and referent studies'
    if name.startswith(('phrase','sound','masked','group-decoder','syllable','daiin','neighbor','qol','shared-frame','target-order','middle-context','short-search')): return 'Phrases, decoder controls and context structure'
    if name in {'voynich-lab','voynich-loop'}: return 'Model lab, later extensions and custody infrastructure'
    return 'Structural atlases, nulls, power and exposure accounting'

groups=collections.defaultdict(list)
for study in sorted({r['original_path'].split('/')[0] for r in rows if '/' in r['original_path']}): groups[theme(study)].append(study)
text=['# Browse by research theme','','Themes are navigation aids, not a reclassification of evidence. Each study keeps its own protocols, findings, negative results and qualification limits. See [latest recorded work](LATEST.md) before interpreting the older chronology.','']
for group,names in sorted(groups.items()):
    text += ['## '+group,'']
    text += [f'- [{name}](catalog/studies/{quote(name)}.md)' for name in names]; text.append('')
(OUT/'MAP.md').write_text('\n'.join(text),encoding='utf-8')
(OUT/'tools/publication').mkdir(parents=True,exist_ok=True)
for name in ['prepare.py','inventory.py','finish.py','verify_git.py','refresh_inventory.py','compress_large.py']:
    shutil.copyfile(TOOLS/name,OUT/'tools/publication'/name)
# The publication scripts retain the original workspace layout assumptions;
# they are preserved as build provenance, not a portable research runner.
(OUT/'tools/publication/README.md').write_text('''# Publication build provenance

These are the scripts used to inventory, select, copy and organize this archive. They expect the original workspace layout: `github-export/research-archive-tools/` beside `github-export/voynich-research/`. They are retained for inspection, not as an instruction to rebuild into a live research tree.

`inventory.py` enumerates in-scope files. `prepare.py` applies the documented exclusions, scans copied bytes for credential-shaped patterns, writes resumable copy accounting, compresses large files losslessly, and builds the indexes. `finish.py` adds thematic navigation and moves undeclared staging leftovers to a separate local quarantine. Original experiment files are not moved or edited.

The input inventory is a filesystem listing, not a complete historical provenance ledger. URL extraction considers copied text files up to 10,000,000 bytes; larger files remain fully preserved where publishable and are not automatically treated as bibliographic records. URLs can be examples or failed retrievals. Source records must be read in context.

Run the portable `../verify_archive.py` from this repository to verify export integrity. The export verification receipt is distinct from every historical experiment receipt.
''',encoding='utf-8')
print(json.dumps({'themes':len(groups),'study_folders':sum(map(len,groups.values())),'quarantined_staging_leftovers':len(quarantined),'paths':quarantined[:20]},indent=2))
