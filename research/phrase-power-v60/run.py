from pathlib import Path
import json,re,random,collections,hashlib,importlib.util,html
R=Path(__file__).resolve().parent;P=R.parent
sp=importlib.util.spec_from_file_location('v59',P/'combination-null-v59/run.py');v59=importlib.util.module_from_spec(sp);sp.loader.exec_module(v59)
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 units=json.loads((P/'astrolabe-comparison-v52/UNITS.json').read_text());sources={}
 for role in ['description','instruction']:
  sources['Chaucer '+role]=[(u['unit'],u['words']) for u in units if u['group']=='Chaucer '+role]
 herbs=json.loads((P/'herbal-slots-v53/LATER-EXTRACTIONS.json').read_text());sources['Later herbal treatment candidates']=[(f"{x['herb']}:{x['paragraph']}",re.findall('[a-z]+',x['text'].lower())) for x in herbs if x['recipe_candidate']]
 rows=json.loads((P/'frequency-atlas-v48/rows.json').read_text());locs=collections.defaultdict(set)
 for r in rows:locs[r[6]].add(r[0])
 results=[];samples=[];rng=random.Random(6001)
 for source,blocks in sources.items():
  # Deterministic randomized block order; no outcome-based sample choice; within-block order intact.
  blocks=blocks[:];rng.shuffle(blocks);stream=[]
  for label,words in blocks:stream.extend(words);stream.append(None)
  for tr in ('H','F'):
   template=[r for r in rows if r[0]==tr and r[2]=='Recipes' and r[3]=='1' and r[4]=='A' and r[5]=='P' and locs[r[6]]=={'H','F'}]
   need=sum(w is not None for r in template for w in r[7])
   if len(stream)<need:results.append({'source':source,'geometry':tr,'status':'insufficient source','needed':need,'available':len(stream)});continue
   it=iter(stream);lines=[[next(it) if w is not None else None for w in r[7]] for r in template];folios=[re.match(r'f\d+',r[1])[0] for r in template]
   samples.append({'source':source,'geometry':tr,'template':'hand1 A Recipes P sharedH/F','lines':lines,'pseudo_folios':folios,'known_words':sum(w is not None for ws in lines for w in ws),'source_blocks_order':[b[0] for b in blocks]})
   for kind in ('bigrams','trigrams'):
    observed=v59.counts(lines,'interior',kind);pages=collections.defaultdict(set)
    for ws,fol in zip(lines,folios):
     for p in v59.counts([ws],'interior',kind):pages[p].add(fol)
    candidates={p for p in observed if len(pages[p])>=2};nulls=[];sums=collections.Counter();rngp=random.Random(6100+len(results))
    for b in range(999):
     c=v59.counts([v59.shuffle(ws,rngp) for ws in lines],'interior',kind);nulls.append(max(c.values(),default=0))
     for p in candidates:sums[p]+=c[p]
    vals=[]
    for p in candidates:
     pv=(1+sum(m>=observed[p] for m in nulls))/1000;mean=sums[p]/999
     vals.append({'phrase':' '.join(p),'observed':observed[p],'expected':mean,'pseudo_folios':len(pages[p]),'p_max':pv,'p_corrected':min(1,pv*48),'passes':pv*48<=.05 and observed[p]>mean})
    vals.sort(key=lambda x:(not x['passes'],-x['observed'],x['phrase']));results.append({'source':source,'geometry':tr,'kind':kind,'known_words':samples[-1]['known_words'],'lines':len(lines),'pseudo_folios':len(set(folios)),'candidate_phrases':len(vals),'passing':sum(v['passes'] for v in vals),'phrases':vals});print(source,tr,kind,'passing',results[-1]['passing'],flush=True)
 (R/'SAMPLES.json').write_text(json.dumps(samples),encoding='utf8');(R/'RESULTS.json').write_text(json.dumps(results,indent=2));summary=[{k:v for k,v in r.items() if k!='phrases'} for r in results];(R/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
 body='<h1>Known-text phrase detection — v60</h1><p>Unchanged v59 shuffle/count code;999 permutations and fixed48-family correction. Known text placed into actual hand1 Recipes H/F line-length and uncertainty templates; source chapter/paragraph boundaries become unknown barriers. These are artificial layouts and pseudo-folios, not recovered manuscript pages. H/F here denotes two geometry templates, NOT alternate transcriptions of Chaucer or Culpeper. Descriptive sensitivity test, not independent dual-transcription qualification. One sample per source/geometry, not a power estimate.</p><p>Herbal candidate paragraphs were selected by v53 lexical action cues; this is not independent recipe gold. Later expanded edition is separate from Chaucer. Medieval herbal material insufficient for this sample size. Prior Voynich results unchanged.</p><table><tr><th>Source / geometry / kind</th><th>Words</th><th>Passing / candidates</th><th>Strongest observed examples</th></tr>'
 for r in results:
  if 'phrases' not in r:continue
  text='; '.join(f"{v['phrase']}: {v['observed']} vs {v['expected']:.2f}, adjusted p={v['p_corrected']:.3f}" for v in r['phrases'][:5]);body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [r['source']+' / '+r['geometry']+' / '+r['kind'],r['known_words'],f"{r['passing']} / {r['candidate_phrases']}",text])+'</tr>'
 body+='</table><p><a href="RESULTS.json">Every phrase, including failures</a> · <a href="SAMPLES.json">Exact synthetic layouts and source order</a> · <a href="PROTOCOL.json">Frozen protocol</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Phrase power v60</title><style>body{font:16px system-ui;max-width:1300px;margin:35px auto;background:#f5f2e9;color:#193c39}td,th{padding:10px;border-bottom:1px solid #b8cbbf;text-align:left}p{line-height:1.6}</style>'+body,encoding='utf8')
if __name__=='__main__':main()
