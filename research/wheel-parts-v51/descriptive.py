from pathlib import Path
import json,collections,itertools,html
R=Path(__file__).resolve().parent
rows=json.loads((R/'ROWS.json').read_text())
def feats(w):
 s={'word:'+w}
 for n in range(1,len(w)+1):
  s.update(['prefix:'+w[:n],'suffix:'+w[-n:]])
  for i in range(1,len(w)-n):s.add('internal:'+w[i:i+n])
 return s
out=[]
for page in sorted({r['page'] for r in rows}):
 pair=('U','V') if page=='f85v2' else ('H','U')
 shared=set.intersection(*[{r['locator'] for r in rows if r['page']==page and r['tr']==t} for t in pair])
 rs=[r for r in rows if r['page']==page and r['locator'] in shared and r['tr'] in pair]
 field='rosette' if page=='f85v2' else 'zone'
 for a,b in itertools.combinations(sorted({r[field] for r in rs if r[field] and r[field]!='ambiguous'}),2):
  per={};counts={};den={}
  for tr in pair:
   counts[tr]={};den[tr]={}
   for zone in (a,b):
    ws=[w for r in rs if r['tr']==tr and r[field]==zone for w in r['words'] if w];den[tr][zone]=len(ws);counts[tr][zone]=collections.Counter(f for w in ws for f in feats(w))
  eligible=min(n for d in den.values() for n in d.values())>=5
  if eligible:
   universe=set().union(*(set(c) for d in counts.values() for c in d.values()))
   for f in universe:
    ds={t:100*(counts[t][a][f]/den[t][a]-counts[t][b][f]/den[t][b]) for t in pair}
    per[f]=ds
  out.append(dict(page=page,dimension=field,a=a,b=b,denominators=den,status='descriptive only; format confounded' if eligible else 'too sparse even for display',differences_pp=per))
(R/'DESCRIPTIVE-DIFFERENCES.json').write_text(json.dumps(out),encoding='utf8')
body='<h2>Descriptive differences, shared locations in both readings</h2><p>Wheel comparison H/U; Rosettes U/V. Five readable words per side is only a display threshold, not statistical qualification. Wheel comparisons mix formats; Rosettes comparisons are mostly labels with unresolved interior/connection placement. All differences saved, including disagreements. Listed below: largest same-direction differences with at least three occurrences in each reading across the two groups. No significance or generalisation claim.</p><table><tr><th>Page / contrast</th><th>Words, first / second reading</th><th>Largest differences (percentage points)</th></tr>'
shown=0
for x in out:
 if not x['differences_pp']:continue
 ts=list(x['denominators']);ranked=[]
 for f,d in x['differences_pp'].items():
  if d[ts[0]]*d[ts[1]]<=0:continue
  # Frequency floor recomputed from source rows for each displayed feature.
  if min(sum(f in feats(w) for r in rows if r['page']==x['page'] and r['tr']==t and r[x['dimension']] in (x['a'],x['b']) for w in r['words'] if w) for t in ts)<3:continue
  ranked.append((min(abs(v) for v in d.values()),f,d))
 ranked.sort(reverse=True)
 txt='; '.join(f"{f}: "+'/'.join(f'{d[t]:+.1f}' for t in ts) for _,f,d in ranked[:5])
 body+='<tr><td>'+html.escape(x['page']+' '+x['a']+' minus '+x['b'])+'</td><td>'+html.escape(str(x['denominators']))+'</td><td>'+html.escape(txt)+'</td></tr>';shown+=1
body+='</table><p><a href="DESCRIPTIVE-DIFFERENCES.json">Full descriptive differences and sparse comparisons</a></p>'
with (R/'report.html').open('a',encoding='utf8') as f:f.write(body)
print('Descriptive comparisons displayed:',shown)
