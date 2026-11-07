import re,json,collections,csv,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
P=R.parent.parent
EVT=Path(r'C:/Users/lewis/.codex/visualizations/2026/10/21/01a15c3d-56da-7f02-bc15-2522dc396abd/voynich-layout/data/text16e6.original.evt')
OPEN={'f70v2','f70v1','f71r','f71v','f72r1','f72r2','f72r3','f72v3'}
RES={'f72v2','f72v1','f73r','f73v'}
def scope(f):
 n=int(re.match(r'f([0-9]+)',f)[1])
 return f in OPEN or n in (67,68,85,86) or 88<=n<=102
locators=collections.defaultdict(list)
units={};counts=collections.Counter();current=None;allread=collections.Counter();excluded_reserved=0
with EVT.open('rb') as inp:
 for lineno,b in enumerate(inp,1):
  # Inspect only header metadata. No reading body is decoded in this inventory.
  m=re.match(rb'^## <(f[0-9]+[rv][0-9]*)[.]([^>]+)>',b)
  if m:
   f=m[1].decode('ascii');current=(f+'.'+m[2].decode('ascii')) if f not in RES and scope(f) else None
   if current:units[current]=dict(folio=f,code=m[2].decode('ascii'),comments=[],source_line=lineno)
  elif b.startswith(b'## '):current=None
  elif current and b.startswith(b'# '):units[current]['comments'].append(b[2:].decode('latin1').strip())
  m=re.match(rb'^<(f[0-9]+[rv][0-9]*)[.]([^.]+)[.]([^;]+);([A-Z])>',b)
  if not m:continue
  f,c,num,reading=[s.decode('ascii') for s in m.groups()]
  if f in RES:excluded_reserved+=1;continue
  if scope(f):
   counts[(f,c,reading)]+=1;allread[(f,reading)]+=1
   if reading in ('H','F'):locators[(f+'.'+c,reading)].append(num)
out=dict(status='METADATA_ONLY_NO_FEATURE_LOOK',units=[dict(unit=k,**v,HF_locators={a:locators[(k,a)] for a in ('H','F')},reading_counts={a:n for (f,c,a),n in counts.items() if f+'.'+c==k}) for k,v in units.items()],coverage=[dict(folio=f,readings={a:n for (p,a),n in allread.items() if p==f}) for f in sorted({p for p,a in allread})],reserved_header_rows_skipped=excluded_reserved,payloads_decoded=0,feature_looks_used=0,vault_open=False,container_policy='Monolithic source streamed as bytes. Reserved record bodies never decoded, retained, displayed or scored; only header match was used for exclusion.')
(R/'METADATA-INVENTORY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(out))
