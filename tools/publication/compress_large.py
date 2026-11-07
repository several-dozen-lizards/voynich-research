"""Use streaming XZ for a retained output exceeding GitHub's blob limit."""
import gzip, hashlib, json, lzma
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'github-export/voynich-research'
rows=json.loads((ROOT/'catalog/FILES.json').read_text(encoding='utf-8'))
changed=[]
for row in rows:
    if row.get('published_bytes',0)<90_000_000 or not row['published_path'].endswith('.gz'): continue
    old=ROOT/row['published_path']; rel=row['published_path'][:-3]+'.xz'; new=ROOT/rel
    with gzip.open(old,'rb') as src, lzma.open(new,'wb',preset=3) as dst:
        for chunk in iter(lambda:src.read(1024*1024),b''): dst.write(chunk)
    if new.stat().st_size>=100_000_000: raise RuntimeError('XZ output still exceeds the publication size target')
    digest=hashlib.sha256(); git=hashlib.sha1(b'blob '+str(new.stat().st_size).encode()+b'\0')
    with new.open('rb') as src:
        for chunk in iter(lambda:src.read(1024*1024),b''): digest.update(chunk); git.update(chunk)
    row.update(published_path=rel,published_bytes=new.stat().st_size,published_sha256=digest.hexdigest(),git_blob=git.hexdigest())
    changed.append({'path':rel,'bytes':new.stat().st_size})
    # The old staged gzip is left for the reversible quarantine pass.
(ROOT/'catalog/FILES.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'changed':changed},indent=2))
