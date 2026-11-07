"""Create an allowlisted registrar workspace; never export transcription bodies."""
from pathlib import Path
import json,re,hashlib,shutil
R=Path(__file__).resolve().parent;V=R.parent;P=V.parent
SOURCE=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 workspace=R/'registrar-only';(workspace/'images').mkdir(parents=True,exist_ok=True)
 public=json.loads((V/'rater-only/TASKS.json').read_text());key=json.loads((V/'research-only/TASK-KEY.json').read_text());tasks=key['tasks'];pages={x['folio'] for x in tasks}|{x['folio'] for x in key['withheld']}
 reserved={'f72v1','f72v2','f73r','f73v'};assert not pages.intersection(reserved)
 units={}
 # Inspect only locator headers, never text bodies, token classes or qok outcomes.
 for raw in SOURCE.read_text(encoding='latin1').splitlines():
  header=raw.partition('>')[0]
  m=re.fullmatch(r'<(f\d+[rv]\d*)\.(P[^.]*)\.([^;]+);([HF])',header)
  if not m:continue
  folio,unit,num,reading=m.groups()
  if folio not in pages:continue
  k=(folio,unit,reading);units.setdefault(k,[]).append(dict(locus=f'{folio}.{unit}.{num}',source_line_number=num))
 output=[]
 for (folio,unit,reading),lines in sorted(units.items()):
  nums=[x['source_line_number'] for x in lines];assert len(nums)==len(set(nums)),(folio,unit,reading)
  output.append(dict(folio=folio,unit=unit,reading=reading,line_count=len(lines),lines=lines))
 save(workspace/'EVT-STRUCTURE.json',output)
 manifest=[]
 for t in tasks:
  pt=next(x for x in public if x['task_id']==t['task_id']);assert all(pt[k]==t[k] for k in pt)
  dest=workspace/t['image'];src=V/'rater-only'/t['image']
  if not dest.exists():shutil.copy2(src,dest)
  assert sha(dest)==sha(src)
  manifest.append({k:t[k] for k in ('task_id','folio','image','native_width','native_height')})
 save(workspace/'PAGES.json',manifest);save(workspace/'WITHHELD-PAGES.json',key['withheld'])
 protocol=dict(status='REGISTRAR_INPUTS_FROZEN_BEFORE_GEOMETRY',authority='v4.1 + user request to build shared geometry and blind registration',cohort='All frozen 168 exact-canvas source pages; all EVT P-unit locators on cohort folios, not selected event lines.',inputs='Native page images, page dimensions, folio identifiers, P-unit header locators/counts only. No transcription bodies, tokenized words, origins, follower classes, outcomes, effects, rater picture boxes or category labels.',independence='Deterministic registrar subprocess uses only this allowlisted workspace; no model or human exposed to outcome summaries is certified as a blind visual registrar.',geometry='Image-only candidate extraction; output cannot be accepted solely because counts agree. Independent visual review is required to verify writing vs drawing, completeness, block order and segmentation.',registration='Exact within-block line count separately for H/F. Count mismatch, missing reading, ambiguous block identity, unregistered folio and unreviewed geometry retained explicitly. No nearest-line guessed assignment. No reading pooling.',acceptance='An independent reviewer declares outcome_blind=true and picture_boxes_unseen=true, checks native boxes, and explicitly maps each block to one EVT P unit. Count equality required per reading; failures drop the whole block for that reading. No default acceptance.',measurement='Line rectangle height is its native y extent; width is native x extent. No image-context category/distance/OT merge or outcome analysis performed here.',preservation='Prior packet remains fixed. No changes to v103, no Rosettes leave-out grids.',sources=dict(evt_sha256=sha(SOURCE),v41_protocol_sha256=sha(V/'PROTOCOL-v4.1.json')),input_hashes={str(p.relative_to(workspace)):sha(p) for p in sorted(workspace.rglob('*')) if p.is_file()})
 save(R/'PROTOCOL.json',protocol)
 print(json.dumps(dict(pages=len(manifest),withheld=len(key['withheld']),reading_units=len(output),reading_loci=sum(u['line_count'] for u in output)),indent=2))
if __name__=='__main__':main()
