"""Read-only independent check of the prepared blind packet."""
from pathlib import Path
import collections,csv,hashlib,json,zipfile
D=Path(__file__).resolve().parent/'adjudication-prep'
def sha(b):return hashlib.sha256(b).hexdigest()
seal=json.loads((D/'PREPARATION-SEAL.json').read_text(encoding='utf-8'))
assert all(sha((D/p).read_bytes())==h for p,h in seal.items())
with (D/'PRIVATE-TARGET-LINES.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==len({r['shared_line_id'] for r in rows})==427
assert collections.Counter(r['reason'] for r in rows)=={'DISAGREEMENT':194,'MISSING_A':222,'MISSING_B':11}
tasks=json.loads((D/'rater-only/TASKS.json').read_text())
key=json.loads((D/'PRIVATE-CROSSWALK.json').read_text())['pages']
assert len(tasks)==len(key)==49
assert {t['task_id'] for t in tasks}=={k['third_task_id'] for k in key}
assert {r['original_task_id'] for r in rows}=={k['original_task_id'] for k in key}
with zipfile.ZipFile(D/'rater-only.zip') as z:
    expected={p.relative_to(D/'rater-only').as_posix():p for p in (D/'rater-only').rglob('*') if p.is_file()}
    assert set(z.namelist())==set(expected)
    assert all(z.read(name)==p.read_bytes() for name,p in expected.items())
assert all(sha((D/'rater-only/images'/f"{k['third_task_id']}.jpg").read_bytes())==k['image_sha256'] for k in key)
print('PASS: seal, 427-line union, 49-page crosswalk, byte-identical ZIP and source-image hashes.')
