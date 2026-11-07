from pathlib import Path
import json,hashlib,collections,sys,html
R=Path(__file__).resolve().parent; P=R.parent; S=P/'complete-atlas-v56/ROWS.json'
def save(n,x): (R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
patterns=['alch','oalch','doar','daro']
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Descriptive replication of exposed Claude claims. No confirmatory significance, sound fitting, morphology or plant identification.',patterns=patterns,modes=['whole token','initial string','anywhere substring'],rules='Use every fully readable atlas token; preserve all 18 reading codes separately, with readable token section denominators. alch and oalch searches are nested, not independent. Retain unknowns in source alternates, do not repair or join words. Final g is literal EVA transcription, not an adjudicated glyph. No pooling readings as independent witnesses.',retrieval='Save every matched event and all source rows at its locus. Search doar/daro without fuzzy spelling or prefix stripping; absences are limited to these queries and available coverage.',astronomy='Use atlas Astronomy section verbatim; separately show Astrology rather than silently combine. Also output combined values if section names differ. Do not infer labels from astronomical page membership.',qualification='Already exposed forms and counts make this a replication/exploratory audit, even though execution rules are frozen. Do not infer distributional equality from small counts or infer a functional prefix from concentration. Source coverage and hand/layout confounds remain.'))
 save('PRE-SEARCH-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]})
 print('Frozen descriptive query rules and input hashes.')
else:
 for p,h in json.loads((R/'PRE-SEARCH-FREEZE.json').read_text()).items(): assert sha(Path(p))==h
 rows=json.loads(S.read_text()); codes=sorted({x[0] for x in rows}); sections=sorted({x[2] for x in rows}); counts=[]; events=[]; loci=set()
 for code in codes:
  rr=[x for x in rows if x[0]==code]
  for section in sections:
   xx=[x for x in rr if x[2]==section]; words=[w for x in xx for w in x[9] if w]
   if not words: continue
   c=dict(reading=code,section=section,tokens=len(words),rows=len(xx),pages=len({x[1] for x in xx}),final_g=sum(w.endswith('g') for w in words))
   for pat in patterns:
    c[pat+'_whole']=sum(w==pat for w in words);c[pat+'_initial']=sum(w.startswith(pat) for w in words);c[pat+'_substring']=sum(pat in w for w in words)
   c['alch_substring_excluding_oalch']=sum('alch' in w and 'oalch' not in w for w in words)
   counts.append(c)
 for x in rows:
  for j,w in enumerate(x[9]):
   if not w:continue
   matches={pat:dict(whole=w==pat,initial=w.startswith(pat),substring=pat in w) for pat in patterns if pat in w}
   if matches or w.endswith('g'):
    events.append(dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],token_index=j,word=w,matches=matches,final_g=w.endswith('g'),raw=x[10]));loci.add(x[8])
 alts={l:[dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],tokens=x[9],raw=x[10]) for x in rows if x[8]==l] for l in sorted(loci)}
 save('COUNTS.json',counts);save('EVENTS.json',events);save('ALTERNATES.json',alts)
 summary=[]
 for code in codes:
  cc=[c for c in counts if c['reading']==code]; total=sum(c['tokens'] for c in cc)
  summary.append(dict(reading=code,tokens=total,sections={c['section']:c['tokens'] for c in cc},oalch=[{k:e[k] for k in ['word','page','section','locator']} for e in events if e['reading']==code and 'oalch' in e['matches']],alch_substring=sum(c['alch_substring'] for c in cc),alch_initial=sum(c['alch_initial'] for c in cc),alch_whole=sum(c['alch_whole'] for c in cc),final_g=sum(c['final_g'] for c in cc)))
 save('SUMMARY.json',summary)
 assert sum(c['tokens'] for c in counts)==sum(bool(w) for x in rows for w in x[9])
 for code in codes:
  for pat in patterns:
   assert sum(c[pat+'_substring'] for c in counts if c['reading']==code)==sum(e['reading']==code and pat in e['matches'] for e in events)
 save('VERIFICATION.json',dict(token_reconciliation=True,substring_event_reconciliation=True,reading_codes=len(codes),alternate_loci=len(alts),sounds_fitted=0,plant_ids_assigned=0))
 print(json.dumps(dict(sections=sections,summary=[s for s in summary if s['reading'] in ['H','F','U','V']],H_counts=[c for c in counts if c['reading']=='H']),indent=2))
