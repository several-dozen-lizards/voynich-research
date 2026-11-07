"""Restore archived research paths into a new directory without running code."""
import argparse, gzip, hashlib, json, lzma
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination',type=Path,help='new or empty directory; existing files are never overwritten')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
destination=args.destination.resolve()
if destination.is_relative_to(root) or root.is_relative_to(destination): parser.error('choose a separate destination outside the repository and its parents')
if destination.exists() and any(destination.iterdir()): parser.error('destination must be new or empty')
destination.mkdir(parents=True,exist_ok=True)
rows=json.loads((root/'catalog/FILES.json').read_text(encoding='utf-8'))
count=0
for row in rows:
    if not row['published_path']: continue
    target=(destination/row['original_path']).resolve()
    if not target.is_relative_to(destination): raise RuntimeError('unsafe original path')
    source=(root/row['published_path']).resolve()
    if not source.is_relative_to(root): raise RuntimeError('unsafe published path')
    target.parent.mkdir(parents=True,exist_ok=True)
    opener=gzip.open if source.suffix=='.gz' else lzma.open if source.suffix=='.xz' else open
    digest=hashlib.sha256(); size=0
    with opener(source,'rb') as incoming, target.open('xb') as outgoing:
        for chunk in iter(lambda:incoming.read(1024*1024),b''):
            digest.update(chunk); size+=len(chunk); outgoing.write(chunk)
    if size!=row['bytes'] or digest.hexdigest()!=row['sha256']: raise RuntimeError('restored bytes fail verification: '+row['original_path'])
    count+=1
print(json.dumps({'restored_files':count,'destination':str(destination),'research_code_executed':False},indent=2))
