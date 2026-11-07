from pathlib import Path
import csv,json,re,hashlib,collections
R=Path(__file__).resolve().parent
D=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data')
src=D/'text16e6.original.evt';meta=D/'Davis-hands.original.csv'
hands={x['Folio']:x for x in csv.DictReader(meta.open(encoding='utf-8-sig'))}
rows=[];bad=collections.Counter()
for raw in src.read_text(encoding='latin-1').splitlines():
 m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',raw)
 if not m or m[4] not in ['H','F']:continue
 pg,place,num,tr,txt=m.groups();h=hands.get(pg,{})
 t=re.sub(r'\{[^}]*\}','~',txt.split('#')[0]);t=re.sub(r'[!\s]','',t)
 t=re.sub(r'([=\-.,])~+$',r'\1',t).rstrip('=-.,');parts=re.split(r'([.,\-=])',t);ws=[]
 for i in range(0,len(parts),2):
  w=parts[i]
  if not w:continue
  comma=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
  good=bool(re.fullmatch('[a-z]+',w)) and not comma
  ws.append(w if good else None)
  if not good:bad[tr]+=1
 # Raw non-P locus tag retained: no guessed circular/label classification.
 rows.append([tr,pg,h.get('Section','Unknown'),h.get('Scribe','?'),h.get('Language','?'),'P' if place.startswith('P') else place,f'{pg}.{place}.{num}',ws])
manifest={'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,meta]},'rows':len(rows),'known_words':dict(collections.Counter(r[0] for r in rows for w in r[7] if w)),'uncertain_word_slots':dict(bad),'transcribers':{'H':'Takahashi','F':'First Study Group'},'status':'Descriptive atlas only. Section tags are manuscript categories, not verified word meanings. No ending merges or semantic role scoring.'}
(R/'data.js').write_text('const ROWS='+json.dumps(rows,separators=(',',':'))+';\nconst MANIFEST='+json.dumps(manifest)+';',encoding='utf8')
(R/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(R/'rows.json').write_text(json.dumps(rows,separators=(',',':')),encoding='utf8')
print(json.dumps(manifest,indent=2))
