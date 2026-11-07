from pathlib import Path
import json,re,collections,hashlib
R=Path(__file__).resolve().parent;P=R.parent
rows=json.loads((P/'frequency-atlas-v48/rows.json').read_text());previous=json.loads((P/'word-parts-v50/RESULTS.json').read_text());cs=previous['candidates'];locs=collections.defaultdict(set)
for r in rows:locs[r[6]].add(r[0])
def pos(i,n):return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def hit(w,f):
 kind,s=f.split(':',1)
 return w==s if kind=='word' else w.startswith(s) if kind=='prefix' else w.endswith(s) if kind=='suffix' else s in w[1:-1]
def table(events,key):
 groups=collections.defaultdict(list)
 for e in events:
  v=key(e)
  if v is not None:groups[v].append(e)
 return sorted([{'text':k,'count':len(es),'folios':len({e['folio'] for e in es}),'pages':sorted({e['page'] for e in es}),'locators':sorted({e['locator'] for e in es}),'status':'cross-folio recurrence' if len({e['folio'] for e in es})>=2 else 'single-folio only'} for k,es in groups.items()],key=lambda x:(-x['count'],x['text']))
out=[]
for c in cs:
 f=c['feature'];record={k:c[k] for k in ['hand','language','format','position','section_a','section_b','feature']};record['groups']=[]
 for tr in ('H','F'):
  base=[r for r in rows if r[0]==tr and r[3]==c['hand'] and r[4]==c['language'] and r[5]==c['format'] and locs[r[6]]=={'H','F'} and r[2] in (c['section_a'],c['section_b'])]
  sf=collections.defaultdict(set)
  for r in base:sf[re.match(r'f\d+',r[1])[0]].add(r[2])
  for section in (c['section_a'],c['section_b']):
   ev=[];den=0;eligiblefolios=set()
   for r in base:
    if r[2]!=section:continue
    fol=re.match(r'f\d+',r[1])[0]
    if len(sf[fol])>1:continue
    ws=r[7]
    for i,w in enumerate(ws):
     if not w or pos(i,len(ws))!=c['position']:continue
     den+=1;eligiblefolios.add(fol)
     if not hit(w,f):continue
     left=ws[i-1] if i else '#EDGE';right=ws[i+1] if i+1<len(ws) else '#EDGE'
     ev.append({'page':r[1],'folio':fol,'locator':r[6],'index':i,'ordinal':i+1,'line_length':len(ws),'word':w,'left':left or '#UNKNOWN','right':right or '#UNKNOWN','line':ws})
   clean=lambda x:x not in ('#EDGE','#UNKNOWN')
   record['groups'].append({'transcription':tr,'section':section,'eligible_words':den,'eligible_folios':len(eligiblefolios),'hits':len(ev),'hit_folios':len({e['folio'] for e in ev}),'unknown_neighbor_events':sum('#UNKNOWN' in (e['left'],e['right']) for e in ev),'edge_events':sum('#EDGE' in (e['left'],e['right']) for e in ev),'words':table(ev,lambda e:e['word']),'left_neighbors':table(ev,lambda e:e['left'] if clean(e['left']) else None),'right_neighbors':table(ev,lambda e:e['right'] if clean(e['right']) else None),'bigrams':table(ev,lambda e:e['word']+' '+e['right'] if clean(e['right']) else None),'left_bigrams':table(ev,lambda e:e['left']+' '+e['word'] if clean(e['left']) else None),'trigrams':table(ev,lambda e:e['left']+' '+e['word']+' '+e['right'] if clean(e['left']) and clean(e['right']) else None),'ordinals':dict(collections.Counter(e['ordinal'] for e in ev)),'events':ev})
 out.append(record)
data={'contrasts':out,'method':'Descriptive concordance of21existing selected contrasts. Same shared H/F loci, hand,variety,format,position and mixed-folio exclusion. Neighbors never cross source line boundaries or unknown slots. Cross-folio recurrence means at least2numberedfolios, not a significance test. Counts token-weighted, unlike earlier equal-folio effect sizes. First/last position is selection, not rediscovery. Different tokenization can move word indices across H/F; compare source loci, not indices as exact glyph alignment.'}
(R/'RESULTS.json').write_text(json.dumps(data,indent=2),encoding='utf8');(R/'data.js').write_text('const DATA='+json.dumps(data,separators=(',',':'))+';',encoding='utf8');print(json.dumps({'contrasts':len(out),'occurrences_with_overlap':sum(g['hits'] for c in out for g in c['groups'])}))
checks=[]
for c in out:
 for g in c['groups']:
  assert sum(x['count'] for x in g['words'])==g['hits'];assert all(hit(e['word'],c['feature']) for e in g['events']);assert all(e['line'][e['index']]==e['word'] for e in g['events'])
  checks.append({'feature':c['feature'],'tr':g['transcription'],'section':g['section'],'hits':g['hits'],'crossfolio_bigrams':sum(x['folios']>=2 for x in g['bigrams']),'crossfolio_trigrams':sum(x['folios']>=2 for x in g['trigrams'])})
(R/'SUMMARY.json').write_text(json.dumps(checks,indent=2));(R/'VERIFICATION.json').write_text(json.dumps({'word_count_conservation':'pass','feature_match':'pass','source_index':'pass','visual_review':'not performed','inference':'no new significance claims'},indent=2))
