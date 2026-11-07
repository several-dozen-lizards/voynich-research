from pathlib import Path
import json,re,random,collections,hashlib,importlib.util,html
R=Path(__file__).resolve().parent;P=R.parent
sp=importlib.util.spec_from_file_location('old',P/'combination-null-v59/run.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
def sample(blocks,n,width):
 lines=[];used=0;labels=[]
 for label,ws in blocks:
  take=ws[:max(0,n-used)];used+=len(take);labels.append(label)
  lines.extend(take[i:i+width] for i in range(0,len(take),width))
  if used>=n:break
 return lines,labels,used
def test(lines,seed,targets=None,B=999):
 rng=random.Random(seed);obs=old.counts(lines,'interior','bigrams');targets=set(targets) if targets is not None else {p for p,c in obs.items() if c>=2};sums=collections.Counter();tails=collections.Counter();maxima=[]
 for b in range(B):
  c=old.counts([old.shuffle(w,rng) for w in lines],'interior','bigrams');maxima.append(max(c.values(),default=0))
  for p in targets:sums[p]+=c[p];tails[p]+=c[p]>=obs[p]
 out=[]
 for p in targets:
  mean=sums[p]/B;raw=(1+tails[p])/(B+1);mx=(1+sum(v>=obs[p] for v in maxima))/(B+1)
  out.append({'phrase':' '.join(p),'observed':obs[p],'expected':mean,'excess':obs[p]-mean,'p_phrase':raw,'p_max':mx,'p_max48':min(1,mx*48),'p_fixed_candidates':min(1,raw*len(targets))})
 return sorted(out,key=lambda x:(-(x['excess']/(x['expected']+1)**.5),x['phrase']))
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 rows=json.loads((P/'herbal-slots-v53/LATER-EXTRACTIONS.json').read_text());lookup={f"{x['herb']}:{x['paragraph']}":(x['herb'],re.findall('[a-z]+',x['text'].lower())) for x in rows if x['recipe_candidate']};prior=json.loads((P/'phrase-power-v60/SAMPLES.json').read_text());seen=set()
 for s in prior:
  if not s['source'].startswith('Later'):continue
  budget=sum(w is not None for ws in s['lines'] for w in ws);n=0
  for label in s['source_blocks_order']:
   herb,words=lookup[label];seen.add(herb);n+=len(words)+1
   if n>=budget:break
 pools=[[],[],[]]
 for label,(herb,words) in lookup.items():
  if herb in seen:continue
  fold=int(hashlib.sha256(('v61:'+herb).encode()).hexdigest()[:8],16)%3;pools[fold].append((label,words))
 for i,pool in enumerate(pools):random.Random(6100+i).shuffle(pool)
 allocation={'excluded_v60_herbs':sorted(seen),'pool_token_counts':[sum(len(w) for _,w in ps) for ps in pools],'blocks':[[l for l,w in ps] for ps in pools]};(R/'ALLOCATION.json').write_text(json.dumps(allocation,indent=2))
 if min(allocation['pool_token_counts'])<2000 or allocation['pool_token_counts'][0]<4000:
  (R/'STATUS.txt').write_text('Insufficient source for frozen allocation; no adaptive resplit.');print(allocation['pool_token_counts']);return
 diagnostics=[];dev_results=None
 for n in (2000,4000):
  for width in (6,12):
   lines,labels,actual=sample(pools[0],n,width);res=test(lines,6200+n+width);diagnostics.append({'words':actual,'width':width,'results':res,'uncorrected_flags':sum(x['p_phrase']<=.05 and x['excess']>0 for x in res),'max_only_flags':sum(x['p_max']<=.05 and x['excess']>0 for x in res),'max48_flags':sum(x['p_max48']<=.05 and x['excess']>0 for x in res)})
   if n==2000 and width==6:dev_results=res
   print('diagnostic',n,width,diagnostics[-1]['max48_flags'],flush=True)
 (R/'DIAGNOSTICS.json').write_text(json.dumps(diagnostics,indent=2))
 # Revision fixed before fresh scoring: only five phrases selected on development; local-frequency p and Bonferroni5.
 phrases=[tuple(x['phrase'].split()) for x in dev_results[:5]];(R/'FROZEN-CANDIDATES.json').write_text(json.dumps({'phrases':phrases,'selection':'top5development excess/sqrt(expected+1), independent herb-disjoint tests; no max rawcount correction needed for fixed independent candidates'},indent=2))
 fresh=[]
 for i in (1,2):
  lines,labels,actual=sample(pools[i],2000,6);res=test(lines,6300+i,phrases);fresh.append({'fold':i,'words':actual,'blocks':labels,'results':res,'detected':sum(x['p_fixed_candidates']<=.05 and x['excess']>0 for x in res)})
  print('fresh',i,fresh[-1]['detected'],flush=True)
 # Frequency-preserving sham datasets; same five development candidates remain fixed.
 shams=[];base,_,_=sample(pools[1],2000,6)
 for i in range(20):
  rng=random.Random(6400+i);fake=[old.shuffle(w,rng) for w in base];res=test(fake,6500+i,phrases,199);shams.append({'seed':6400+i,'flag':any(x['p_fixed_candidates']<=.05 and x['excess']>0 for x in res),'results':res})
 (R/'FRESH-RESULTS.json').write_text(json.dumps(fresh,indent=2));(R/'SHAM-FAILURES.json').write_text(json.dumps(shams,indent=2));result={'diagnostics':[{k:v for k,v in x.items() if k!='results'} for x in diagnostics],'fixed_phrases':[' '.join(p) for p in phrases],'fresh_detections':[x['detected'] for x in fresh],'sham_flags':sum(x['flag'] for x in shams),'shams':20,'narrow_gate':'pass' if all(x['detected']>=1 for x in fresh) and sum(x['flag'] for x in shams)<=1 else 'FAIL','limits':'Only later herbal candidate prose; edited artificial lines; fresh to phrase testing, previously processed in slot work. 20shams and2fresh samples are finite engineering evidence, not broad qualification. No manuscript-transcription transfer. Voynich test unchanged.'};(R/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 body='<h1>Phrase-test diagnosis — v61</h1><p>Size and layout crossed on development text; correction variants computed from the same permutations. Raw p flags are diagnostic only. Revision selects five phrases on development, freezes them, then uses phrase-specific permutation tails with Bonferroni5 on herb-disjoint fresh samples. All failures retained.</p><pre>'+html.escape(json.dumps(result,indent=2))+'</pre>'
 for f in ['DIAGNOSTICS.json','FROZEN-CANDIDATES.json','FRESH-RESULTS.json','SHAM-FAILURES.json','ALLOCATION.json','PROTOCOL.json']:body+='<p><a href="'+f+'">'+f+'</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Phrase diagnosis v61</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}p{line-height:1.6}</style>'+body,encoding='utf8')
if __name__=='__main__':main()
