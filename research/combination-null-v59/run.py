from pathlib import Path
import json,re,random,collections,hashlib,html
R=Path(__file__).resolve().parent;P=R.parent
def pos(i,n):return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def shuffle(ws,rng):
 out=ws[:];block=[]
 for i in range(1,len(ws)):
  if i<len(ws)-1 and ws[i] is not None:block.append(i);continue
  vals=[ws[j] for j in block];rng.shuffle(vals)
  for j,v in zip(block,vals):out[j]=v
  block=[]
 return out
def counts(lines,position,kind):
 c=collections.Counter()
 for ws in lines:
  for i,w in enumerate(ws):
   if w is None or pos(i,len(ws))!=position:continue
   a,b=(i-1,i+1) if kind=='left_bigrams' else (i,i+2) if kind=='bigrams' else (i-1,i+2)
   if a<0 or b>len(ws):continue
   part=ws[a:b]
   if None not in part:c[tuple(part)]+=1
 return c
def qualification():
 rng=random.Random(5900);false=0;positives=0
 for trial in range(40):
  lines=[['EDGE']+[rng.choice('abcdefgh') for _ in range(10)]+['END'] for _ in range(16)]
  for planted in (False,True):
   ls=[w[:] for w in lines]
   if planted:
    for w in ls:w[3:6]=['x','y','z']
   obs=max(counts(ls,'interior','trigrams').values(),default=0)
   null=[max(counts([shuffle(w,rng) for w in ls],'interior','trigrams').values(),default=0) for _ in range(199)]
   p=(1+sum(v>=obs for v in null))/200
   if p<=.05:
    if planted:positives+=1
    else:false+=1
 q={'exchangeable_false_flags':false,'trials':40,'planted_detections':positives,'gate':'pass' if false<=5 and positives>=32 else 'FAIL','scope':'Engineering qualification of whole-family maximum-count permutation under this generator only; not layout/nonlinear realism.'};(R/'QUALIFICATION.json').write_text(json.dumps(q,indent=2));return q
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 q=qualification();print(q,flush=True)
 if q['gate']!='pass':return
 source=json.loads((P/'frequency-atlas-v48/rows.json').read_text());context=json.loads((P/'contrast-context-v58/RESULTS.json').read_text());loci=collections.defaultdict(set)
 for r in source:loci[r[6]].add(r[0])
 targets=collections.defaultdict(lambda:collections.defaultdict(set))
 for c in context['contrasts']:
  for g in c['groups']:
   key=(g['transcription'],c['hand'],c['language'],c['format'],c['position'],g['section'])
   for kind in ('left_bigrams','bigrams','trigrams'):
    for p in g[kind]:
     if p['folios']>=2:targets[(key,kind)][tuple(p['text'].split())].add(c['feature'])
 M=len(targets);results=[]
 for j,((key,kind),phrases) in enumerate(sorted(targets.items())):
  tr,h,var,fmt,position,section=key
  rr=[r for r in source if r[0]==tr and r[3]==h and r[4]==var and r[5]==fmt and r[2]==section and loci[r[6]]=={'H','F'}]
  # Preserve mixed-section exclusions used by selected contrasts.
  other={r[1] for r in rr};lines=[r[7] for r in rr]
  observed=counts(lines,position,kind);rng=random.Random(5901+j);maxima=[];sums=collections.Counter();tail=collections.Counter()
  for b in range(999):
   c=counts([shuffle(w,rng) for w in lines],position,kind);maxima.append(max(c.values(),default=0))
   for p in phrases:sums[p]+=c[p];tail[p]+=c[p]>=observed[p]
  vals=[]
  for p,features in phrases.items():
   maxp=(1+sum(m>=observed[p] for m in maxima))/1000
   vals.append({'phrase':' '.join(p),'selected_by':sorted(features),'observed':observed[p],'null_mean':sums[p]/999,'excess':observed[p]-sums[p]/999,'p_unadjusted_exploratory':(1+tail[p])/1000,'p_all_patterns_max':maxp,'p_across_panels':min(1,maxp*M)})
  results.append({'tr':tr,'hand':h,'variety':var,'format':fmt,'position':position,'section':section,'kind':kind,'lines':len(lines),'patterns':vals});print(j+1,'/',M,key,kind,flush=True)
 paired=[];lookup={(r['tr'],r['hand'],r['variety'],r['format'],r['position'],r['section'],r['kind']):r for r in results}
 for k,r in lookup.items():
  if k[0]!='H' or ('F',)+k[1:] not in lookup:continue
  fs={p['phrase']:p for p in lookup[('F',)+k[1:]]['patterns']}
  for p in r['patterns']:
   if p['phrase'] in fs:paired.append({'context':k[1:],'phrase':p['phrase'],'H':p,'F':fs[p['phrase']],'passes_both':p['excess']>0 and fs[p['phrase']]['excess']>0 and max(p['p_across_panels'],fs[p['phrase']]['p_across_panels'])<=.05})
 data={'panels':M,'results':results,'paired':paired,'qualification':q,'method':'Within-line interior permutation, first/last fixed, unknowns fixed barriers; page/hand/section/format and line-word multisets preserved. Positions first/interior/last controlled, not exact interior ordinal. Max raw count over ALL possible realized phrases of same orientation/position each permutation protects selection of recurring phrases. Bonferroni over panels. Conservative and low-powered for rare combinations. No new independent replication.'}
 (R/'RESULTS.json').write_text(json.dumps(data,indent=2));summary={'panels':M,'tested_selected_patterns':sum(len(r['patterns']) for r in results),'paired_patterns':len(paired),'passes_both':sum(p['passes_both'] for p in paired)};(R/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(summary)
 body='<h1>Recurring combinations versus frequency — v59</h1><p>'+html.escape(data['method'])+'</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><table><tr><th>Context</th><th>Phrase</th><th>H observed / expected</th><th>F observed / expected</th><th>Adjusted p H / F</th><th>Pass both</th></tr>'
 for p in sorted(paired,key=lambda p:(not p['passes_both'],-min(p['H']['excess'],p['F']['excess']))):
  body+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in [' / '.join(p['context']),p['phrase'],f"{p['H']['observed']} / {p['H']['null_mean']:.2f}",f"{p['F']['observed']} / {p['F']['null_mean']:.2f}",f"{p['H']['p_across_panels']:.3f} / {p['F']['p_across_panels']:.3f}",p['passes_both']])+'</tr>'
 body+='</table><p><a href="RESULTS.json">All readings, failures and unpaired patterns</a> · <a href="QUALIFICATION.json">Synthetic engineering checks</a> · <a href="PROTOCOL.json">Frozen rules</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Combination null v59</title><style>body{font:16px system-ui;max-width:1300px;margin:35px auto;background:#f5f2e9;color:#193c39}td,th{padding:8px;border-bottom:1px solid #bdcec4;text-align:left}p{line-height:1.6}</style>'+body,encoding='utf8')
if __name__=='__main__':main()
