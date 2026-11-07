"""Verify copied research bytes, compression and generated navigation offline."""
import gzip, hashlib, json, re, os, lzma
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'catalog/FILES.json').read_text(encoding='utf-8'))
errors=[]; checked=0; decompressed=0
editorial_path=root/'catalog/EDITORIAL-FILES.json'
editorial=json.loads(editorial_path.read_text(encoding='utf-8'))['files'] if editorial_path.exists() else []
editorial_known={r['path'] for r in editorial}
editorial_checked=0
for r in editorial:
    path=root/r['path']
    try:
        data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=r['sha256']: errors.append(r['path']+': editorial SHA-256 mismatch')
        editorial_checked+=1
    except Exception as e: errors.append(r['path']+': '+str(e))
def verify_one(r):
    failures=[]
    rel=r['published_path']
    if not rel: return 0,0,failures
    p=root/rel
    try:
        published_hash=hashlib.sha256(); git_hash=hashlib.sha1(b'blob '+str(p.stat().st_size).encode()+b'\0')
        with p.open('rb') as saved:
            for chunk in iter(lambda:saved.read(1024*1024),b''): published_hash.update(chunk); git_hash.update(chunk)
        if published_hash.hexdigest()!=r['published_sha256']: failures.append(rel+': published SHA-256 mismatch')
        if git_hash.hexdigest()!=r['git_blob']: failures.append(rel+': Git blob mismatch')
        original_hash=published_hash; original_size=p.stat().st_size
        if rel.endswith(('.gz','.xz')):
            original_hash=hashlib.sha256(); original_size=0
            with (gzip.open(p,'rb') if rel.endswith('.gz') else lzma.open(p,'rb')) as original:
                for chunk in iter(lambda:original.read(1024*1024),b''): original_hash.update(chunk); original_size+=len(chunk)
        if original_size!=r['bytes'] or original_hash.hexdigest()!=r['sha256']: failures.append(rel+': original bytes mismatch')
        return 1,int(rel.endswith(('.gz','.xz'))),failures
    except Exception as e: return 0,0,[rel+': '+str(e)]
with ThreadPoolExecutor(max_workers=8) as executor:
    for offset in range(0,len(rows),256):
        for count,compressed,failures in executor.map(verify_one,rows[offset:offset+256]):
            checked+=count; decompressed+=compressed; errors.extend(failures)
        if offset%4096==0: print(json.dumps({'verified':checked,'indexed':offset}),flush=True)
link_count=0
known={r['published_path'] for r in rows if r['published_path']}
known.update(editorial_known)
known.add('catalog/EXPORT-VERIFICATION.json')
known.update(p.relative_to(root).as_posix() for p in root.glob('*.md'))
known.update(p.relative_to(root).as_posix() for p in (root/'catalog').glob('*') if p.is_file())
known.update(p.relative_to(root).as_posix() for p in (root/'catalog/studies').glob('*.md'))
known_dirs=set()
for rel in known:
    parent=Path(rel).parent
    while str(parent)!='.':
        known_dirs.add(parent.as_posix()); parent=parent.parent
docs=list(dict.fromkeys(list(root.glob('*.md'))+list((root/'catalog/studies').glob('*.md'))+[root/p for p in editorial_known if p.endswith('.md')]))
actual_research=set()
for base,dirs,files in os.walk(root/'research'):
    actual_research.update((Path(base)/name).relative_to(root).as_posix() for name in files)
for unexpected in sorted(actual_research-{r['published_path'] for r in rows if r['published_path']}-editorial_known): errors.append(unexpected+': undeclared research file')
for p in docs:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target.startswith(('https:','http:','#','mailto:')): continue
        target=unquote(target.split('#')[0])
        normalized=Path(os.path.normpath(p.parent/target)).relative_to(root).as_posix()
        if normalized not in known and normalized not in known_dirs: errors.append(p.relative_to(root).as_posix()+': missing link '+target)
        link_count+=1
receipt={'passed':not errors,'research_files_verified':checked,'editorial_files_verified':editorial_checked,'compressed_files_verified':decompressed,'generated_links_checked':link_count,'errors':errors,'scope':'Original archive integrity, declared editorial guides, and generated navigation only; historical research checks were not rerun.'}
(root/'catalog/EXPORT-VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
raise SystemExit(0 if not errors else 1)
