from pathlib import Path
import json, re, hashlib, collections, sys
R=Path(__file__).resolve().parent;P=R.parent;SOURCE=P/'complete-atlas-v56/ROWS.json'
RAW=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def units(w):return re.findall('cth|ckh|cph|cfh|ch|sh|.',w)
def distance(a,b):
 prev=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  nxt=[i]
  for j,y in enumerate(b,1):nxt.append(min(prev[j]+1,nxt[-1]+1,prev[j-1]+(x!=y)))
  prev=nxt
 return prev[-1]
if sys.argv[1]=='freeze':
 protocol=dict(date='2026-10-23',anchor='oalcheg',scope='All 18 reading codes and all corpus sections in unchanged v56 strict readable-token atlas. Missing/uncertain slots and raw source retained at every selected locus.',selection='Exact anchor plus all complete tokens of Levenshtein edit distance <=1 (primary near variants), <=2 (secondary wider net), in EITHER EVA character or fixed longest cth/ckh/cph/cfh/ch/sh group view. Standard insertion/deletion/substitution only, no transpositions, phonetic weights, consonant skeletons or suffix peeling. No historical names consulted to select variants.',order='Freeze definition and code before search. Preserve every qualifying type, count separately by reading, distinguish source loci from alternate-reading row counts. Nearness does not establish same word/name.',raw_audit='Also list every raw source line containing literal oalcheg, including forms excluded by strict cleaning. Selected loci get every alternative source reading, full raw lines and surrounding source comments. No harmonization.',associations='Extract section/hand/format and actual label-unit comments before inference. Zodiac star/figure labels are not equivalent to named fixed stars. Read enough images to identify any independent repeated referent; transcription order and clock position alone do not establish celestial coordinates.',historical='Seek historically attested candidates only when an independent referent or ordered series supports them. EVA spelling is not pronunciation; no matching al- star names to EVA oal- as evidence. If no discriminating referent exists, retain an empty admissible name list. No sounds fitted.',limits='Source and anchor previously exposed. Exhaustive frozen string search is descriptive, not an enrichment significance test. Alternate readings are not independent attestations. Existing arbitrary unit grouping has no phonetic standing.')
 save('PROTOCOL.json',protocol);save('PRE-SEARCH-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SOURCE,RAW]});print('Trace protocol frozen.')
else:
 for p,h in load(R/'PRE-SEARCH-FREEZE.json').items():assert sha(Path(p))==h
 assert distance('abc','abc')==0 and distance('abc','ac')==1 and distance('abc','adc')==1 and distance('ab','ba')==2
 assert units('oalcheg')==['o','a','l','ch','e','g']
 rows=load(SOURCE);vocab=sorted({w for x in rows for w in x[9] if w});target='oalcheg';tg=units(target);variants={}
 for w in vocab:
  ch=distance(target,w) if abs(len(w)-len(target))<=2 else 99
  gu=units(w);gr=distance(tg,gu) if abs(len(gu)-len(tg))<=2 else 99
  if min(ch,gr)<=2:variants[w]=dict(word=w,character_distance=ch if ch!=99 else None,group_distance=gr if gr!=99 else None,tier='exact' if w==target else 'primary one-edit' if min(ch,gr)<=1 else 'secondary two-edit')
 events=[];selected=set();allbyloc=collections.defaultdict(list)
 for x in rows:
  d=dict(reading=x[0],page=x[1],section=x[2],hand=x[3],variety=x[4],source_unit=x[5],zone=x[6],locator=x[8],tokens=x[9],raw=x[10]);allbyloc[x[8]].append(d)
  for j,w in enumerate(x[9]):
   if w in variants:
    events.append(dict(**variants[w],**d,token_index=j));selected.add(x[8])
 lines=RAW.read_text(encoding='latin1').splitlines();literal=[];context={}
 for i,line in enumerate(lines):
  if line.startswith('<') and 'oalcheg' in line:literal.append(dict(line_number=i+1,line=line))
  m=re.match(r'^<(f\d+[rv]\d*\.[^.]+\.[^;]+);([A-Z])>',line)
  if m and m[1] in selected:
   context.setdefault(m[1],[]).append(dict(line_number=i+1,context='\n'.join(lines[max(0,i-3):i+2])))
 comments={};current=None
 for line in lines:
  m=re.match(r'^## <([^>]+)>',line)
  if m:current=m[1];comments[current]=[]
  elif current and line.startswith('#'):comments[current].append(line)
  elif not line.startswith('#'):current=None
 summary=[]
 for w,v in variants.items():
  es=[e for e in events if e['word']==w];summary.append(dict(**v,rows_by_reading=dict(collections.Counter(e['reading'] for e in es)),loci=len({e['locator'] for e in es}),pages=sorted({e['page'] for e in es}),sections=sorted({e['section'] for e in es})))
 summary.sort(key=lambda x:({'exact':0,'primary one-edit':1,'secondary two-edit':2}[x['tier']],x['word']))
 save('VARIANTS.json',summary);save('ALL-EVENTS.json',events);save('LOCUS-ALTERNATES.json',{k:allbyloc[k] for k in sorted(selected)});save('RAW-LITERAL-HITS.json',literal);save('RAW-CONTEXT.json',context);save('UNIT-COMMENTS.json',{u:comments.get(u,[]) for u in sorted({e['page']+'.'+e['source_unit'] for e in events})})
 save('SEARCH-SUMMARY.json',dict(vocabulary_types=len(vocab),variant_types=len(variants),selected_loci=len(selected),reading_events=len(events),types_by_tier=dict(collections.Counter(x['tier'] for x in summary)),sounds_fitted=0))
 print(json.dumps(load(R/'SEARCH-SUMMARY.json')))
 print(json.dumps([x for x in summary if x['tier']!='secondary two-edit'],indent=2))
