from pathlib import Path
import json,re,collections,hashlib,random,statistics,math,html
R=Path(__file__).resolve().parent;P=R.parent
def features(w):
 s={'word:'+w}
 for n in range(1,len(w)+1):
  s.update(['prefix:'+w[:n],'suffix:'+w[-n:]])
  for i in range(1,len(w)-n):s.add('internal:'+w[i:i+n])
 return s
def chunks(ws,n=50):return [ws[i:i+n] for i in range(0,len(ws)-n+1,n)]
def metrics(ws):
 n=len(ws);c=collections.Counter(ws);pair=lambda fun:sum(fun(a)==fun(b) for a,b in zip(ws,ws[1:]))/(n-1)
 # Exact random-permutation expectation within this window (without replacement).
 coll=lambda f:sum(v*(v-1) for v in collections.Counter(map(f,ws)).values())/(n*(n-1))
 out={'types_per_50':len(c),'repeat_token_pct':100*(n-len(c))/n,'same_word_excess_pp':100*(pair(lambda w:w)-coll(lambda w:w)),'length':sum(map(len,ws))/n}
 for k in (1,2,3):
  for name,fn in [('prefix',lambda w:w[:k]),('suffix',lambda w:w[-k:])]:
   eligible=[w for w in ws if len(w)>=k];ct=collections.Counter(fn(w) for w in eligible)
   out[f'{name}{k}_top5_pct']=100*sum(v for _,v in ct.most_common(5))/len(eligible) if eligible else None
  # Short words are their whole string here, explicitly not padded.
  out[f'prefix{k}_neighbor_excess_pp']=100*(pair(lambda w:w[:k])-coll(lambda w:w[:k]))
  out[f'suffix{k}_neighbor_excess_pp']=100*(pair(lambda w:w[-k:])-coll(lambda w:w[-k:]))
 mids=collections.Counter(w[1:-1] for w in ws if len(w)>2);out['internal_core_types']=len(mids)
 return out
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 s=(P/'wheel-parts-v51/historical/chaucer-astrolabe-edited.txt').read_text(encoding='utf8');one,two=s.split('PART I',1)[1].split('PART II',1);units=[]
 for role,text in [('description',one),('instruction',two)]:
  # Conservative dehyphenation only explicit hyphen followed by whitespace; preserves spelling otherwise.
  text=re.sub(r'([a-zA-Z])-\s+([a-zA-Z])',r'\1\2',text);text=re.sub(r'\[[^]]*\]',' ',text)
  sections=re.split(r'(?m)^\s*(\d+)\.\s+',text)
  for i in range(1,len(sections)-1,2):
   words=re.findall(r"[a-z]+",sections[i+1].lower());units.append({'corpus':'Chaucer','group':'Chaucer '+role,'unit':role+'-'+sections[i],'words':words,'order':True})
 rows=json.loads((P/'frequency-atlas-v48/rows.json').read_text());groups=collections.defaultdict(list)
 for tr,page,sec,hand,var,fmt,loc,ws in rows:
  if fmt=='P':groups[(tr,page,sec,hand,var)].extend(ws)
 for (tr,page,sec,hand,var),ws in groups.items():units.append({'corpus':'Voynich','group':f'{sec} / hand{hand} / {var} / P / {tr}','unit':page,'words':ws,'order':True})
 wheel=json.loads((P/'wheel-parts-v51/ROWS.json').read_text());groups=collections.defaultdict(list)
 for r in wheel:
  if r['zone']=='ambiguous':continue
  groups[(r['page'],r['zone'],r['format'],r['tr'])].extend(r['words'])
 for (page,zone,fmt,tr),ws in groups.items():units.append({'corpus':'Voynich-wheel','group':f'wheel {page} / {zone} / {fmt} / {tr}','unit':page,'words':ws,'order':False})
 (R/'UNITS.json').write_text(json.dumps(units),encoding='utf8')
 inventory=collections.defaultdict(collections.Counter);samples=collections.defaultdict(list);support=collections.Counter();short=collections.Counter()
 for u in units:
  support[u['group']]+=sum(w is not None for w in u['words'])
  for w in u['words']:
   if w:inventory[u['group']].update(features(w))
  # Unknown tokens break windows; never silently concatenate around them.
  segments=[];cur=[]
  for w in u['words']+[None]:
   if w:cur.append(w)
   else:segments.append(cur);cur=[]
  for seg in segments:
   for ws in chunks(seg):
    m=metrics(ws)
    if not u['order']:m={k:v for k,v in m.items() if 'excess' not in k}
    samples[u['group']].append({'unit':u['unit'],'metrics':m})
   short[u['group']]+=len(seg)%50
 results={}
 for g in inventory:
  ss=samples[g];keys=ss[0]['metrics'] if ss else []
  results[g]={'readable_tokens':support[g],'windows':len(ss),'units_with_windows':len({v['unit'] for v in ss}),'unused_tokens_for_windows':short[g],'metrics':{k:{'mean':statistics.mean(v['metrics'][k] for v in ss),'min':min(v['metrics'][k] for v in ss),'max':max(v['metrics'][k] for v in ss)} for k in keys},'status':'descriptive' if len(ss)>=5 else 'sparse/not comparable'}
 (R/'ALL-WORD-PARTS.json').write_text(json.dumps(inventory),encoding='utf8');(R/'WINDOWS.json').write_text(json.dumps(samples),encoding='utf8');(R/'RESULTS.json').write_text(json.dumps(results,indent=2))
 # Book part split is textual architecture, not independently labelled pure sentence roles.
 body='<h1>Astrolabe descriptions and instructions — v52</h1><p>Part I instrument description; Part II operational conclusions (including worked examples and explanations). Prologue excluded. These are source-defined mixed sections, not independently labelled pure sentence roles. Edited Middle English, not manuscript shorthand. Hyphen plus whitespace joined; bracketed editorial material removed. No manuscript line-position test.</p><p>Equal 50-word windows within chapters or Voynich page/region. Unknowns break windows. Short remainders retained in inventories but excluded from window metrics. Neighbor excess is actual adjacent agreement minus exact random-permutation expectation in the same window. Voynich paragraph lines concatenated in source order; wheel adjacency not scored because label order may be artificial. No similarity optimisation or p-values. Orthographic lengths and alphabet differences remain confounds.</p><table><tr><th>Group</th><th>Windows / source units</th><th>Types /50</th><th>Repeat %</th><th>Start-2 excess pp</th><th>End-2 excess pp</th><th>Same-word excess pp</th></tr>'
 for g,v in results.items():
  if not v['windows']:continue
  vals=[g,f"{v['windows']} / {v['units_with_windows']}"]+[f"{v['metrics'][k]['mean']:.2f}" if k in v['metrics'] else 'not scored' for k in ['types_per_50','repeat_token_pct','prefix2_neighbor_excess_pp','suffix2_neighbor_excess_pp','same_word_excess_pp']]
  body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in vals)+'</tr>'
 body+='</table><p><a href="RESULTS.json">All metrics and sparse groups</a> · <a href="ALL-WORD-PARTS.json">Every observed word part and whole word</a> · <a href="WINDOWS.json">Every retained window</a> · <a href="PROTOCOL.json">Frozen protocol</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Astrolabe comparison</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;background:#f7f4ed;color:#173b39}td,th{padding:8px;border-bottom:1px solid #ccc}p{line-height:1.6}</style>'+body,encoding='utf8')
 print(json.dumps({g:v for g,v in results.items() if g.startswith('Chaucer')},indent=2))
if __name__=='__main__':main()
