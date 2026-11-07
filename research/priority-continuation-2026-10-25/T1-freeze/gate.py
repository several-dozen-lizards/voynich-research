"""Status-only preflight; deliberately contains no ratings/text join route."""
import hashlib,json
from pathlib import Path
P=Path(__file__).parent
ROOT=P.parents[1]
def status():
    seal=json.loads((P/'SEAL.json').read_text(encoding='utf-8'))
    changed=[name for name,sha in seal['files'].items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha]
    return dict(status='CLOSED',join_permitted=False,vault_permitted=False,seal_intact=not changed,changed=changed,blockers=['Full-population v4 G6 not passed in frozen receipt','Wrap input provenance unresolved','Real-support T1 qualification not run','No production ratings/text loader in this version'])
if __name__=='__main__':print(json.dumps(status(),indent=2))
