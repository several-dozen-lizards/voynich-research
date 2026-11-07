"""Compare the committed Git tree against the archive's byte manifest."""
import json, subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]/'github-export/voynich-research'
rows=json.loads((root/'catalog/FILES.json').read_text(encoding='utf-8'))
result=subprocess.run(['git','ls-tree','-rz','--full-tree','HEAD'],cwd=root,capture_output=True,check=True).stdout
tree={}
for entry in result.split(b'\0'):
    if not entry: continue
    metadata,name=entry.split(b'\t',1); tree[name.decode('utf-8')]=metadata.split()[2].decode('ascii')
errors=[]; expected={r['published_path']:r['git_blob'] for r in rows if r['published_path']}
editorial_path=root/'catalog/EDITORIAL-FILES.json'
editorial=json.loads(editorial_path.read_text(encoding='utf-8'))['files'] if editorial_path.exists() else []
editorial_expected={r['path']:r['git_blob'] for r in editorial}
for path,digest in expected.items():
    if tree.get(path)!=digest: errors.append(path+': committed blob differs from the copied-byte manifest')
for path in tree:
    if path.startswith('research/') and path not in expected and path not in editorial_expected: errors.append(path+': undeclared research file')
for path,digest in editorial_expected.items():
    if tree.get(path)!=digest: errors.append(path+': committed editorial guide differs from manifest')
receipt={'passed':not errors,'committed_files':len(tree),'research_blob_identities_checked':len(expected),'editorial_blob_identities_checked':len(editorial_expected),'errors':errors}
(root.parent/'VOYNICH-RESEARCH-GIT-VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2)); raise SystemExit(0 if not errors else 1)
