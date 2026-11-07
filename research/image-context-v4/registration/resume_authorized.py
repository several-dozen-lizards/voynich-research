"""Record explicit registration-only release without exposing analyst content to registrar."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path(__file__).resolve().parent;V=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 now=datetime.now(timezone.utc);dest=R/'resume-snapshots'/now.strftime('%Y%m%dT%H%M%SZ');dest.mkdir(parents=True,exist_ok=False)
 baseline=json.loads((R/'GEOMETRY-RETENTION-DECISION.json').read_text());assert sha(R/'SHARED-LINE-GEOMETRY.json')==baseline['retained']['sha256']
 for name in ['HOLD.json','STATUS.json','REGISTRATION.json','SHARED-LINE-GEOMETRY.json','DROPPED-BLOCKS.csv','BLOCK-AUDIT.json','REGISTRATION-SNAPSHOT.json','registrar-only/REVIEW.json','register.py','verify.py']:
  p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,p)
 shutil.copy2(V/'HOLD.json',dest/'root-HOLD.json')
 release=dict(status='REGISTRATION_ONLY_RELEASED_BY_USER',utc=now.isoformat(),authority='User: resume blind registration under v4.1/v4.2, retaining 45 shared lines and timing exception; continue full queue; preserve every dropped block; keep raters blind and v103 parked.',allowed=['source-only independent geometry review','source-only registration','coverage and engineering validation','preserve versioned outputs and every drop'],still_held=['picture rating','picture-box application','image-context derivation','agreement','support','synthetic controls','outcome joining','statistical analysis'],timing_exception='v4.2 was not frozen before initial registration; retained explicitly. No backdating or clean pre-registration claim.',retained_geometry_sha256=baseline['retained']['sha256'],retained_physical_lines=45,retention_decision_sha256=sha(R/'GEOMETRY-RETENTION-DECISION.json'),snapshot=str(dest),v103='PARKED',blindness='Registrar receives neutral source-only continuation instruction, no amendment rationale, effect scales, event outcomes or picture-rater data.')
 for p in [R/'RESUME-AUTHORIZATION.json',R/'HOLD.json',V/'HOLD.json']:p.write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8')
 (R/'BASELINE-45-LINES.json').write_bytes((dest/'SHARED-LINE-GEOMETRY.json').read_bytes())
 (R/'BASELINE-REVIEW.json').write_bytes((dest/'registrar-only/REVIEW.json').read_bytes())
 print(json.dumps(release,indent=2))
if __name__=='__main__':main()
