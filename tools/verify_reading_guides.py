"""Audit editorial coverage, checksums, and links without running research."""
import hashlib, json, os, re
from pathlib import Path
from urllib.parse import unquote

root=Path(__file__).resolve().parents[1]
registry=json.loads((root/'catalog/PLAIN-ENGLISH-GUIDES.json').read_text(encoding='utf-8'))
editorial=json.loads((root/'catalog/EDITORIAL-FILES.json').read_text(encoding='utf-8'))['files']
archive=json.loads((root/'catalog/FILES.json').read_text(encoding='utf-8'))
original={r['published_path'] for r in archive if r['published_path']}
known=original|{r['path'] for r in editorial}
known.update(p.relative_to(root).as_posix() for p in root.glob('*.md'))
known.update(p.relative_to(root).as_posix() for p in (root/'catalog').glob('*') if p.is_file())
known.update(p.relative_to(root).as_posix() for p in (root/'catalog/studies').glob('*.md'))
directories={'.'}
for rel in known:
    directories.update(p.as_posix() for p in Path(rel).parents)
errors=[]; links=0
if len({r['study'] for r in registry['guides']})!=len(registry['guides']): errors.append('duplicate study guide')
for level,expected in [('study',registry['top_level_guides']),('nested-study',registry['nested_guides'])]:
    if sum(r['level']==level for r in registry['guides'])!=expected: errors.append('coverage mismatch: '+level)
for r in registry['guides']:
    for field in ['tested','found','unresolved','evidence']:
        if not r.get(field): errors.append(r['study']+': missing '+field)
    if not set(r['evidence'])<=original: errors.append(r['study']+': evidence outside archived artifact list')
    for field in ['guide','folder_guide']:
        p=root/r[field]
        if r[field] in original: errors.append(r['study']+': guide overlaps an original artifact')
        body=p.read_text(encoding='utf-8')
        for heading in ['## What we tested','## What we found','## What remains unresolved','## What is in this folder','## Read the evidence']:
            if heading not in body: errors.append(r[field]+': missing '+heading)
for r in editorial:
    data=(root/r['path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=r['sha256']: errors.append(r['path']+': editorial hash mismatch')
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=r['git_blob']: errors.append(r['path']+': editorial Git identity mismatch')
docs=[root/r['path'] for r in editorial if r['path'].endswith('.md')]+[root/'README.md',root/'GLOSSARY.md']
for p in docs:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target.startswith(('http:','https:','#','mailto:')): continue
        rel=Path(os.path.normpath(p.parent/unquote(target.split('#')[0]))).relative_to(root).as_posix()
        if rel not in known and rel not in directories: errors.append(p.relative_to(root).as_posix()+': missing link '+target)
        links+=1
receipt={'passed':not errors,'top_level_study_guides':registry['top_level_guides'],'major_nested_guides':registry['nested_guides'],'editorial_files_verified':len(editorial),'links_checked':links,'original_artifacts_replaced':0,'errors':errors,'scope':'Editorial coverage, evidence paths, content sections, hashes, and links. Historical studies were not rerun.'}
(root/'catalog/READING-GUIDES-VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2)); raise SystemExit(0 if not errors else 1)
