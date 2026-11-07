from pathlib import Path
import json,re,collections,hashlib,html,itertools
R=Path(__file__).resolve().parent
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
mapping=json.loads((R/'LOCATION-MAP.json').read_text());src=next(p for p in json.loads((R/'FREEZE.json').read_text()) if p.endswith('.evt'))
def clean(txt):
 t=re.sub(r'\{[^}]*\}','~',txt.split('#')[0]);t=re.sub(r'[!\s]','',t);t=re.sub(r'([=\-.,])~+$',r'\1',t).rstrip('=-.,');parts=re.split(r'([.,\-=])',t);ws=[]
 for i in range(0,len(parts),2):
  w=parts[i]
  if not w:continue
  comma=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
  ws.append(w if re.fullmatch('[a-z]+',w) and not comma else None)
 return ws
def feats(w):
 out={'word:'+w}
 for n in range(1,len(w)+1):
  out.update(['prefix:'+w[:n],'suffix:'+w[-n:]])
  for i in range(1,len(w)-n):out.add('internal:'+w[i:i+n])
 return out
rows=[]
for line in Path(src).read_text(encoding='latin1').splitlines():
 m=re.match(r'^<([^;]+);([HFUV])>\s*(.*)',line)
 if not m:continue
 loc,tr,txt=m.groups();unit=loc.rsplit('.',1)[0]
 if unit not in mapping:continue
 if unit.startswith('f85v2') and tr not in 'UV':continue
 rows.append(dict(mapping[unit],unit=unit,locator=loc,tr=tr,words=clean(txt)))
(R/'ROWS.json').write_text(json.dumps(rows),encoding='utf8')
profiles={};counts=collections.defaultdict(collections.Counter);den=collections.Counter();unknown=collections.Counter()
for row in rows:
 key='|'.join([row['page'],row['rosette'] or '-',row['zone'],row['format'],row['tr']])
 for w in row['words']:
  if w:den[key]+=1;counts[key].update(feats(w))
  else:unknown[key]+=1
for key in sorted(set(den)|set(unknown)):
 profiles[key]={'readable_words':den[key],'uncertain_slots':unknown[key],'features':dict(counts[key])}
(R/'ALL-PROFILES.json').write_text(json.dumps(profiles),encoding='utf8')
# Same page, same format, same loci across two readings; no cross-page hand pooling.
comparisons=[]
for page in sorted({r['page'] for r in rows}):
 for pair in ([('U','V')] if page=='f85v2' else [('H','F'),('H','U'),('U','V')]):
  locsets=[{r['locator'] for r in rows if r['page']==page and r['tr']==tr} for tr in pair];shared=set.intersection(*locsets)
  rs=[r for r in rows if r['page']==page and r['tr'] in pair and r['locator'] in shared and r['zone']!='ambiguous']
  for fmt in sorted({r['format'] for r in rs}):
   for a,b in itertools.combinations(sorted({r['zone'] for r in rs if r['format']==fmt}),2):
    vals={}
    for tr in pair:
     cs={};ns={}
     for zone in (a,b):
      words=[w for r in rs if r['tr']==tr and r['format']==fmt and r['zone']==zone for w in r['words'] if w];ns[zone]=len(words);cs[zone]=collections.Counter(f for w in words for f in feats(w))
     eligible=all(ns[z]>=20 for z in (a,b))
     vals[tr]={'words':ns,'status':'descriptive eligible' if eligible else 'sparse','differences_pp':{f:100*(cs[a][f]/ns[a]-cs[b][f]/ns[b]) for f in cs[a].keys()|cs[b].keys()} if eligible else {}}
    comparisons.append({'page':page,'pair':pair,'format':fmt,'a':a,'b':b,'readings':vals})
(R/'MATCHED-COMPARISONS.json').write_text(json.dumps(comparisons),encoding='utf8')
coverage=collections.Counter(r['zone'] for r in mapping.values());body='<h1>Wheel locations and Rosettes — v51</h1><p>Source-description map frozen before word-part scoring. Not a new blinded image registration. Unclear locations remain ambiguous. Inner circular bands count as ON; labels within the envelope as INSIDE. Format is retained separately. All profiles are descriptive; no translation, p-value or held-out confirmation.</p>'
body+='<h2>Location ledger</h2><table><tr><th>Unit</th><th>Zone / format</th><th>Description / uncertainty</th><th>Status</th></tr>'
for k,v in mapping.items():body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [k,v['zone']+' / '+v['format'],v['description']+' — '+v['reason'],v['status']])+'</tr>'
body+='</table><h2>Focal profiles (percent of readable words)</h2><p>Denominators and uncertain slots visible; different regions and transcriptions are not pooled.</p><table><tr><th>Page | rosette | zone | format | reading</th><th>Words / uncertain</th><th>qo-</th><th>internal od</th><th>internal ke</th><th>-eol</th></tr>'
for k,v in profiles.items():
 n=v['readable_words'];body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [k,f"{n} / {v['uncertain_slots']}",*[f"{100*v['features'].get(f,0)/n:.1f}" if n else 'NA' for f in ['prefix:qo','internal:od','internal:ke','suffix:eol']]])+'</tr>'
body+='</table><p><a href="ALL-PROFILES.json">Every word part and whole word</a> · <a href="MATCHED-COMPARISONS.json">Same-page, same-format, shared-reading comparisons (including sparse failures)</a> · <a href="LOCATION-MAP.json">Frozen spatial ledger</a> · <a href="HISTORICAL-SOURCES.json">Historical source receipts</a></p>'
(R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Wheel locations v51</title><style>body{font:16px system-ui;max-width:1300px;margin:35px auto;background:#f7f4ed;color:#193a39}td,th{padding:8px;border-bottom:1px solid #ccc;text-align:left}p{line-height:1.6}</style>'+body,encoding='utf8')
summary={'mapped_units':len(mapping),'zone_units':dict(coverage),'missing_units':[k for k,v in mapping.items() if v['status']=='missing transcription'],'rows':len(rows),'matched_comparisons':len(comparisons),'eligible_pairs':sum(all(v['status']=='descriptive eligible' for v in c['readings'].values()) for c in comparisons)}
(R/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
