from source_cut2 import ROOT,CUT,dump
from core import sha
import json,shutil,hashlib
old=json.loads((ROOT/'DELIVERY-HASHES.json').read_text());p=CUT/'previous-cut';p.mkdir(exist_ok=True)
current=ROOT/'G5-RUNS/registry-d207581800f371df8088/stderr.txt'
name=str(current.relative_to(ROOT));expected=old.get(name)
if expected==hashlib.sha256(b'').hexdigest() and current.read_bytes():
    (CUT/'G5-TEST-STDERR.txt').write_bytes(current.read_bytes())
    current.write_bytes(b'') # restore exact pre-existing bytes verified by the old delivery hash
    dump(CUT/'G5-LOG-RESTORATION.json',dict(path=name,restored_sha256=sha(current),new_run_stderr='G5-TEST-STDERR.txt',reason='Keep old delivered empty stderr receipt unchanged; new process-scoped heap option log preserved in cut2.'))
differences=[name for name,digest in old.items() if not (ROOT/name).exists() or sha(ROOT/name)!=digest]
dump(CUT/'PREVIOUS-DELIVERY-AUDIT.json',dict(files=len(old),mismatches=differences,old_reserves_used_for_new_fitting=False))
if differences:raise ValueError(('unexpected prior delivery changes',differences))
for name in ('REPORT.md','STATUS.json','PROTOCOL.json','VERIFICATION.json','TEST-RESULTS.json','DELIVERY-HASHES.json','RETAINED-FAILURES.json','prepare.py'):
    if not (p/name).exists():shutil.copyfile(ROOT/name,p/name)
print('Previous delivery verified and preserved:',len(old),'files')
