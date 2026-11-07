"""Record the human's explicit quality-direction answer; leave frozen rules intact."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path(__file__).resolve().parent;V=R.parent
def main():
 p=R/'AUTHORIZATION.json';old=json.loads(p.read_text());assert old['collection_status']=='PREPARED_NOT_RELEASED'
 assert hashlib.sha256((R/'RATING-FREEZE.json').read_bytes()).hexdigest()==old['rating_freeze_sha256']
 shutil.copy2(p,R/'prior-permissions/AUTHORIZATION-before-user-quality-answer.json')
 old.update(collection_status='AUTHORIZED_COLLECTION',released_utc=datetime.now(timezone.utc).isoformat(),explicit_quality_direction='User: Proceed; retain the synthetic failures and limitation.',scientific_rules='Unchanged from RATING-FREEZE.json; historical release_status in that immutable preparation freeze remains PREPARED_NOT_RELEASED. This sidecar records the later explicit release.',adjudication='NOT AUTHORIZED; G6/G2 first',v103='PARKED')
 for dest in [p,V/'HOLD.json']:
  dest.write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(collection_status=old['collection_status'],quality_direction=old['explicit_quality_direction']),indent=2))
if __name__=='__main__':main()
