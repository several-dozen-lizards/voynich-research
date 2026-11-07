from common import *
from datetime import datetime,timezone
import shutil

if any(read_csv(ROOT/f'RATER-{r}.csv') for r in ['A','B','C']) or (ROOT/'OUTCOME-JOIN.json').exists():
    raise RuntimeError('Cannot pre-rating freeze after observations')
if any(r['status']=='REGISTERED' for r in load(ROOT/'LABEL-REGISTRATION.json')['rows']):
    raise RuntimeError('Cannot claim pre-geometry freeze')
archive=ROOT/'history/infrastructure-v6.0'
# The feature helper changed just before archiving; preserve that copy and reconstruct
# the exact previous helper against its already-issued hash, not an invented history.
oldseal=load(archive/'FREEZE.json');target=archive/'common.py'
if sha(target)!=oldseal['hashes']['common.py']:
    current=target.read_text(encoding='utf-8')
    if not (archive/'COMMON-FEATURE-CHANGE-BEFORE-SNAPSHOT.txt').exists():shutil.copy2(target,archive/'COMMON-FEATURE-CHANGE-BEFORE-SNAPSHOT.txt')
    prefix=current.split('\ndef shape(word):')[0]
    prefix=prefix.replace("    d['shape:'+shape(word)]=1\n    for glyph in set(re.findall(r'cth|ckh|cph|cfh|ch|sh|[a-z]',word)):\n        d['grouped-glyph:'+glyph]=1\n",'').rstrip()+'\n'
    target.write_bytes(prefix.encode('utf-8'))
    save(archive/'SNAPSHOT-CORRECTION.json',dict(reason='Feature helper changed before snapshot; original reconstructed and checked against prior issued hash. Changed copy retained.',
         expected_sha256=oldseal['hashes']['common.py'],actual_sha256=sha(target),exact_hash_recovery=sha(target)==oldseal['hashes']['common.py']))
    assert sha(target)==oldseal['hashes']['common.py']
files=['PROTOCOL.json','CONTROL-PLAN.json','MANUAL.md','UNIT-TYPE-AUDIT.csv','TYPE-COUNTS.csv','LABEL-INVENTORY.csv','FEATURES.csv',
       'T2-MATCHED-PAIRS.csv','PREVIOUS-NINE.json','T2-EXPOSURE-EXCLUSIONS.json','SPEC-original.md',
       'common.py','t1.py','batch_cv.py','qualify.py','prepare_v61.py','seal_v61.py']
save(ROOT/'FREEZE.json',dict(tier='CLAIM_PROTOCOL_V6_1',utc=datetime.now(timezone.utc).isoformat(),
    hashes={p:sha(ROOT/p) for p in files},before=dict(accepted_label_geometry=0,object_votes=0,object_join=False,manuscript_inference=False),
    prior_checkpoint='history/infrastructure-v6.0',note='This freezes the protocol, not a successful scientific qualification.'))
print('v6.1 claim protocol sealed before geometry, ratings, join and controls')
