from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parent
SRC=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
s=SRC.read_text(encoding='latin1');mapping={}
for m in re.finditer(r'^## <([^>]+)>[^\n]*\n(.*?)(?=^## <|\Z)',s,re.M|re.S):
 unit,chunk=m.groups();page=unit.split('.')[0]
 if not re.fullmatch(r'f(?:57v|6[789][rv]\d*|7[0123][rv]\d*|85v2)',page) or '.' not in unit:continue
 comments=[]
 for line in chunk.splitlines():
  if line.startswith('<'):break
  if line.startswith('#') and line.strip('# ').strip():comments.append(line.strip('# ').strip())
 desc=comments[0] if comments else '';d=desc.lower();zone='ambiguous';reason='source description insufficient for spatial assignment'
 # Circumferential writing is ON, including inner bands. Discrete labels remain INSIDE if explicitly in sectors/bands.
 if any(t in d for t in ['outside circle','outside the diagram','not in circle','text above diagram','text below diagram','paragraph at top','text, ne side','paragraph west']):zone='outside';reason='explicit external placement'
 elif any(t in d for t in ['circular text','circles of text','circle of text','ring of text','text ring','circular lines','second ring','third ring','inner ring of text','outer band of text']):zone='on';reason='explicit circumferential text band'
 elif any(t in d for t in ['inside','in circle sectors','in sectors','on sectors inside','on central disk sectors','central circle','radial','on spokes','central star','in central rosette','inner band','outer band of nymphs','inner ring of names','labels under the moons','labels around central']):zone='inside';reason='source places text within diagram envelope'
 fmt='paragraph' if any(t in d for t in ['paragraph','plain text','text above','text below','text, ne']) else 'band' if zone=='on' else 'label' if any(t in d for t in ['label','title','names']) else 'other'
 rosette=None
 if page=='f85v2':
  code=unit.split('.')[1];rosette={'V1':'NW','U1':'NW','W1':'NW','V2':'N','U2':'N','V3':'NE','U3':'NE','N1':'W','M1':'W','N2':'centre','M2':'centre','N3':'E','M3':'E','C1':'SW','B1':'SW','D1':'SW-dial','C2':'S','B2':'S','C3':'SE','B3':'SE'}.get(code,'unknown')
  if 'connections' in d:zone='ambiguous';reason='unit mixes rosette labels and connecting passages; not pooled into inside'
 mapping[unit]={'page':page,'description':desc,'zone':zone,'format':fmt,'reason':reason,'rosette':rosette,'source_comments':comments,'status':'missing transcription' if not re.search(r'^<[^>]+;[A-Z]>',chunk,re.M) else 'records present'}
(R/'LOCATION-MAP.json').write_text(json.dumps(mapping,indent=2),encoding='utf8')
protocol={'scope':'f57v and f67-f73 wheel pages; f85v2 Rosettes separately. Inventory from source unit descriptions, not glyph content. Not a new blinded image annotation. Missing/ambiguous units retained. on means circumferential band, even an inner band; inside means non-band text within envelope.','method':'All observed contiguous EVA prefixes/suffixes/internal sequences and words. Strict v48 cleaning. H/F/U/V separate. Rosettes U/V only. Shared-locus U/V and H/U paired descriptive profiles. Same-page differences split by source format; do not call band-v-label contrasts spatial effects independent of format. No p-values or validation claim for sparse one-foldout comparisons. Circular transcription endpoints not interpreted as physical line edges.','features':'All features output; focal qo,od,ke,eol plus top differences shown descriptively. No outcome-based changes to map.'}
(R/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2))
freeze={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'LOCATION-MAP.json',R/'PROTOCOL.json',R/'prepare.py',R/'compare.py']};freeze[str(SRC)]=hashlib.sha256(SRC.read_bytes()).hexdigest()
(R/'FREEZE.json').write_text(json.dumps(freeze,indent=2))
print('Mapped',len(mapping),'units before scoring')
