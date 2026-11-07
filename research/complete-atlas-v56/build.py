from pathlib import Path
import json,re,csv,hashlib,collections
R=Path(__file__).resolve().parent;P=R.parent
D=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data')
source=D/'text16e6.original.evt';meta=D/'Davis-hands.original.csv'
hands={r['Folio']:r for r in csv.DictReader(meta.open(encoding='utf-8-sig'))};mapping=json.loads((P/'wheel-parts-v51/LOCATION-MAP.json').read_text());rows=[]
for raw in source.read_text(encoding='latin1').splitlines():
 m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',raw)
 if not m:continue
 pg,place,num,tr,txt=m.groups();h=hands.get(pg,{});loc=f'{pg}.{place}.{num}';unit=f'{pg}.{place}';mp=mapping.get(unit,{})
 t=re.sub(r'\{[^}]*\}','~',txt.split('#')[0]);t=re.sub(r'[!\s]','',t);t=re.sub(r'([=\-.,])~+$',r'\1',t).rstrip('=-.,');parts=re.split(r'([.,\-=])',t);ws=[]
 for i in range(0,len(parts),2):
  w=parts[i]
  if not w:continue
  comma=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
  ws.append(w if re.fullmatch('[a-z]+',w) and not comma else None)
 section='Rosettes diagram' if pg=='f85v2' else h.get('Section','Unknown')
 rows.append([tr,pg,section,h.get('Scribe','Unknown'),h.get('Language','Unknown'),'P' if place.startswith('P') else place,mp.get('zone','unmapped'),mp.get('rosette') or 'not assigned',loc,ws,txt])
manifest={'rows':len(rows),'readable_tokens':sum(bool(w) for r in rows for w in r[9]),'uncertain_slots':sum(w is None for r in rows for w in r[9]),'transcriptions':dict(collections.Counter(r[0] for r in rows)),'scope':'All parsed transcriber codes in source; every observed fully readable EVA unit, with no frequency or length cutoff. Uncertain/non-EVA token slots retained and excluded from feature counts, not decoded. Raw readings included for audit. Spatial map is partial v51 source-description map, not new geometry.','hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,meta,P/'wheel-parts-v51/LOCATION-MAP.json']}}
(R/'data.js').write_text('const ROWS='+json.dumps(rows,separators=(',',':'))+';const MANIFEST='+json.dumps(manifest)+';',encoding='utf8');(R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2));(R/'ROWS.json').write_text(json.dumps(rows,separators=(',',':')),encoding='utf8');print(json.dumps({k:v for k,v in manifest.items() if k!='hashes'}))
