import re,json,hashlib,random,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
RAW=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not (P/'PRE-RUN-FREEZE.json').exists():
 save('PROTOCOL.json',{'scope':'Exploratory audit prompted by observed yk and near-pair; cannot become confirmatory by freezing after seeing these clues. No phonetic fitting.', 'selection':'f67r1.S.1..12 versus f67r2.Y.1..12; complete titles retained, no hand-picked words. Source order provisional until image registration. All readings inventoried; H primary, other complete readings separate. F absence explicit.', 'cleaning':'Remove ! padding, {...} comments become boundaries; split dot/comma/hyphen/equals/whitespace. Tokens with * or % or non a-z retained as unknowns; never repaired.', 'transformations':'raw, and strip exactly one initial ot/ok on f67r1 or yk on f67r2. No other prefix deletion. Exact overlap only. Report known ykeeody/ykeody as observed near-pair, not independently discovered.', 'statistic':'Number of paired sectors sharing at least one exact token (nonempty); each sector at most one point. Search all12 offsets and2 directions, both raw/stripped. Null shuffles whole sectors of second wheel; max over all48 options for each of999 permutations seed82001. Preserve title contents, prefix frequencies and unknown slots. Post-selection/exchangeability limits remain.', 'controls':'Before manuscript scoring: twelve distinct dummy tokens in shifted reversed cycle recover12; no-shared-token cycle recovers0. Engineering sanity only, not historical-system validation.', 'semantic_gate':'No sign/house/month identity inferred from twelve sectors. No planets guessed from stars. No image-based nymph features scored yet; need independently selected dated degree table and numbered feature inventory before comparisons.', 'historical':'Dated written traditions kept separate; no pronunciations, modern translations or arbitrary language switching admitted. Prior v81 has12panels but10signs and0F rows; no H/F replication claim.', 'f9v':'Excluded from fitting; no plant tokens enter analysis.'})
 save('PRE-RUN-FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{'run.py':sha(P/'run.py'),'PROTOCOL.json':sha(P/'PROTOCOL.json')},'source_sha256':sha(RAW)})
 print('Frozen before cycle scoring');raise SystemExit
assert all(sha(P/n)==h for n,h in json.loads((P/'PRE-RUN-FREEZE.json').read_text())['files'].items())
records=[]
for line in RAW.read_text(encoding='utf-8').splitlines():
 m=re.match(r'^<(f67r[12])\.([SY])\.(\d+);([^>]+)>\s*(.*)',line)
 if not m:continue
 page,unit,num,tr,raw=m.groups()
 if (page,unit) not in [('f67r1','S'),('f67r2','Y')]:continue
 txt=re.sub(r'\{[^}]*\}',' ',raw).replace('!','');parts=[x for x in re.split(r'[.,=\s-]+',txt) if x]
 records.append(dict(page=page,unit=unit,number=int(num),reading=tr,raw=raw,tokens=[x if re.fullmatch('[a-z]+',x) else None for x in parts],uncertain=[x for x in parts if not re.fullmatch('[a-z]+',x)]))
def prep(rows,page,mode):
 result=[]
 for r in rows:
  ss=set()
  for w in r['tokens']:
   if w is None:continue
   if mode=='stripped':w=re.sub('^(?:ot|ok)' if page=='f67r1' else '^yk','',w,count=1)
   if w:ss.add(w)
  result.append(ss)
 return result
def scores(a,b):return [dict(direction=d,offset=o,score=sum(bool(a[i]&b[(o+d*i)%12]) for i in range(12))) for d in [1,-1] for o in range(12)]
def scan(a,b):
 out=[]
 for mode in ['raw','stripped']:
  for s in scores(prep(a,'f67r1',mode),prep(b,'f67r2',mode)):out.append(dict(mode=mode,**s))
 return out
dummy=[{str(i)} for i in range(12)];assert max(s['score'] for s in scores(dummy,list(reversed(dummy))))==12
assert max(s['score'] for s in scores(dummy,[{'x'+str(i)} for i in range(12)]))==0
results=[]
for tr in sorted({r['reading'] for r in records}):
 a=sorted([r for r in records if r['reading']==tr and r['page']=='f67r1'],key=lambda r:r['number']);b=sorted([r for r in records if r['reading']==tr and r['page']=='f67r2'],key=lambda r:r['number'])
 if [r['number'] for r in a]!=list(range(1,13)) or [r['number'] for r in b]!=list(range(1,13)):
  results.append(dict(reading=tr,status='incomplete; not scored',counts=[len(a),len(b)]));continue
 ss=scan(a,b);best=max(s['score'] for s in ss);rng=random.Random(82001);null=[]
 for _ in range(999):
  z=b.copy();rng.shuffle(z);null.append(max(s['score'] for s in scan(a,z)))
 results.append(dict(reading=tr,status='scored; exploratory',all_offsets=ss,best=best,permutation_p=(1+sum(x>=best for x in null))/1000,null_maxima=null,known_near_pair='f67r1.S.9 H ykeeody / f67r2.Y.6 H ykeody is not exact; already exposed, not added to score'))
counts=[]
for tr in sorted({r['reading'] for r in records}):
 rr=[r for r in records if r['reading']==tr and r['page']=='f67r2'];words=[w for r in rr for w in r['tokens'] if w]
 counts.append(dict(reading=tr,sectors=len(rr),clear_words=len(words),unknown_tokens=sum(w is None for r in rr for w in r['tokens']),yk_words=sum(w.startswith('yk') for w in words),yk_title_starts=sum(bool(r['tokens']) and r['tokens'][0] is not None and r['tokens'][0].startswith('yk') for r in rr),sectors_with_yk=sum(any(w and w.startswith('yk') for w in r['tokens']) for r in rr)))
save('READINGS.json',records);save('PREFIX-COUNTS.json',counts);save('CYCLE-RESULTS.json',results)
latin='Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricornus Aquarius Pisces'.split()
lex=[]
def add(trad,date,source,locator,items,status):
 for obj,form in items:lex.append(dict(tradition=trad,work_date=date,source=source,locator=locator,referent=obj,form=form,status=status,phonetic_value=None))
add('Middle English Chaucer, Latin technical zodiac names','c1391','https://sourcebooks.web.fordham.edu/source/chaucer-astro.asp','Part I §8',zip(latin,latin),'Edited text; inherited v81. Latin forms in English prose do not independently identify a language.')
fr='Aries Taurus Geminis Cancre Lion Virgene Libre Escorpion Sagittaire Capricorne Aquare Poisson'.split()
add('Old French Brunetto Latini','1267 work; Carmody critical edition1948','https://oeuvres.github.io/html/latini_tresor.html','I.CXIII',zip(latin,fr),'Forms in running text; inflection/variants retained. Same work also lists Latin zodiac forms. Not diplomatic manuscript evidence.')
add('Old French Brunetto Latini','1267 work; Carmody critical edition1948','https://oeuvres.github.io/html/latini_tresor.html','I.CXIX, planetary hour sequence',zip(['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon'],['Saturne','Jupiter','Mars','soleil','Venus','Mercure','lune']),'Edited primary text. Other inflected forms/variants not silently merged.')
add('Italian Dante','early14th century, Convivio','https://dante.princeton.edu/cgi-bin/dante/DispMinorWork.pl?REF=II.iii.7&TITLE=Conv','II.iii.7',zip(['Moon','Mercury','Venus','Sun','Mars','Jupiter','Saturn'],['Luna','Mercurio','Venere','Sole','Marte','Giove','Saturno']),'Edited primary text. Article lo not included in name field; no pronunciation reconstructed.')
save('HISTORICAL-NAMES.json',lex)
save('OPEN-GATES.json',{'languages':'Verified starter traditions only; German, Iberian vernaculars, Arabic, Hebrew, Greek and additional Latin witnesses still require dated source passages. Do not fill gaps using modern translated lists.', 'phonetic_search':'Not performed. Suspected anomalous text needs same-hand/format selection controls; whole-manuscript fishing and language switching would multiply opportunities.', 'nymph_tables':'Not performed. Need dated original degree table (including transmission variants), independently registered image features with ambiguous cases, full sign coverage, and rotation/direction/multiple-table correction. Light/dark Aries/Taurus names do not prove degree categories.', 'coverage':'v81: twelve panels, ten distinct signs, no F rows. Keep reading codes and hand metadata conflict explicit. Cycle source order unverified against images; current test conditional on source ordering.', 'scope':'No new semantic anchor. A repeated prefix can mark category, spelling convention, positional context or copying.'})
e=lambda x:html.escape(str(x))
out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Astrological names and cycles v82</title><style>body{font:16px/1.55 system-ui;max-width:1100px;margin:32px auto;padding:0 22px;background:#11251f;color:#edf1e9}a{color:#a5e5bc}td,th{padding:8px;border-bottom:1px solid #456654;text-align:left}table{border-collapse:collapse;width:100%}aside{padding:18px;background:#314532}</style><h1>Astrological names & twelve-part cycles</h1><p>v82 · Exploratory audit · No sounds fitted</p><aside>Twelve sectors are not twelve words. Complete titles retained; unknown tokens remain unknown. No wheel assigned to signs, houses or months.</aside><h2>Prefix denominator audit</h2><table><tr><th>Reading</th><th>Sectors</th><th>Clear words</th><th>Unknown</th><th>yk words</th><th>yk title starts</th><th>Sectors containing yk</th></tr>']
for c in counts:out.append('<tr>'+''.join('<td>'+e(c[k])+'</td>' for k in ['reading','sectors','clear_words','unknown_tokens','yk_words','yk_title_starts','sectors_with_yk'])+'</tr>')
out.append('</table><h2>Cycle comparisons</h2><p>Maximum exact shared-token sector matches over24 rotations/directions and2 preprocessing choices.999 whole-sector shuffles use the same48-way maximum. This is post-clue exploratory evidence, not independent confirmation. No fuzzy match added for the already noticed near-pair.</p><ul>')
for r in results:out.append('<li>'+e(r['reading'])+': '+e(r.get('best','unscored'))+' matches; '+e(r.get('permutation_p',r['status']))+'</li>')
out.append('</ul><h2>Dated written-name starter list</h2><table><tr><th>Tradition</th><th>Referent</th><th>Written form</th><th>Source</th></tr>')
for r in lex:out.append('<tr><td>'+e(r['tradition'])+'</td><td>'+e(r['referent'])+'</td><td>'+e(r['form'])+'</td><td><a href="'+html.escape(r['source'],quote=True)+'">'+e(r['work_date']+' · '+r['locator'])+'</a></td></tr>')
out.append('</table><h2>Still unqualified</h2><p>No sound mapping, no nymph-degree table match and no broad anomaly search. Source order needs image registration. v81 found no F rows on the zodiac panels: other readings are not replacements for F or independent samples. A recognisable zodiac animal does not identify an adjacent token as its name. Later month notes are not Voynich phonetic ground truth.</p><p><a href="READINGS.json">Every original title and reading</a> · <a href="CYCLE-RESULTS.json">All offsets and null results</a> · <a href="HISTORICAL-NAMES.json">Name provenance and limits</a> · <a href="OPEN-GATES.json">Outstanding gates</a> · <a href="PRE-RUN-FREEZE.json">Frozen method</a> · <a href="../astrology-name-audit-v81/report.html">Prior zodiac inventory</a></p></html>')
(P/'report.html').write_text('\n'.join(out),encoding='utf-8')
save('FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='FREEZE.json'}})
print(json.dumps(counts));print(json.dumps([{k:v for k,v in r.items() if k not in ['all_offsets','null_maxima']} for r in results]))
