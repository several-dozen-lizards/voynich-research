import json,re,csv,collections,hashlib,datetime
from pathlib import Path
R=Path(__file__).parent;P=R.parent.parent
plan=json.loads((R/'COVERAGE-PLAN.json').read_text())
assert hashlib.sha256(Path(plan['source_evt']).read_bytes()).hexdigest()==plan['source_evt_sha256']
units={x['unit']:x for x in plan['partC_units']}
with (P/'label-objects-v6/UNIT-TYPE-AUDIT.csv').open(encoding='utf-8-sig',newline='') as f:
 v6={x['unit'] for x in csv.DictReader(f) if x['status']=='INCLUDE' and x['section'] in ('Recipes','Pharmaceutical') and x['reserved'].lower()=='false'}

def flag(b):
 # Syntax-only boolean: never turn EVA bytes into text or count letters by identity.
 b=re.sub(rb'\{[^}]*\}',b'~',b.split(b'#')[0]);b=re.sub(rb'[!%\s]',b'',b)
 b=re.sub(rb'([=\-.,])~+$',rb'\1',b).rstrip(b'=-.')
 parts=re.split(rb'([.,=\-])',b);any_word=False
 for i in range(0,len(parts),2):
  if not parts[i]:continue
  any_word=True
  if (i>0 and parts[i-1]==b',') or (i+1<len(parts) and parts[i+1]==b','):return False
  if not re.fullmatch(rb'[a-z]+',parts[i]):return False
 return any_word
flags=[];skip=collections.Counter();provenance=[];current=None
with Path(plan['source_evt']).open('rb') as inp:
 for lineno,b in enumerate(inp,1):
  u=re.match(rb'^## <(f[0-9]+[rv][0-9]*)[.]([^>]+)>',b)
  if u:
   folio=u[1].decode('ascii');unit=folio+'.'+u[2].decode('ascii')
   current=unit if folio not in plan['reserved'] and (unit in units or unit in v6) else None
  elif b.startswith(b'## '):current=None
  elif current and b.startswith(b'#') and re.search(rb'transcrip|Grove|Takahashi|derived|copied|scanned|photocop|from H',b,re.I):
   provenance.append(dict(unit=current,line=lineno,comment=b.decode('latin1').strip()))
  m=re.match(rb'^<(f[0-9]+[rv][0-9]*)[.]([^.]+)[.]([^;]+);([A-Z])>',b)
  if not m:continue
  folio,code,num,reading=[x.decode('ascii') for x in m.groups()]
  if folio in plan['reserved']:skip['reserved_before_flagging']+=1;continue
  unit=folio+'.'+code
  if unit not in units and unit not in v6:continue
  flags.append(dict(id=unit+'.'+num,unit=unit,folio=folio,reading=reading,source_line=lineno,readable=flag(b[m.end():]),C2_stratum=units.get(unit,{}).get('set'),v6_pharma=unit in v6))
(R/'READABILITY-FLAGS.json').write_text(json.dumps(flags,indent=2)+'\n',encoding='utf8')
(R/'UNIT-PROVENANCE-COMMENTS.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf8')
(R/'COVERAGE-EXTRACTION.json').write_text(json.dumps(dict(status='BOOLEAN_FLAGS_ONLY',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=len(flags),decoded_label_strings=0,emitted_label_strings=0,reserved_flags_computed=0,skips=dict(skip),v6_units=sorted(v6)),indent=2)+'\n')
print(json.dumps(dict(status='BOOLEAN_FLAGS_ONLY',records=len(flags),reserved_flags_computed=0)))
