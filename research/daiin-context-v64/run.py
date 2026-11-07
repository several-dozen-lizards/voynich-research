from pathlib import Path
import json,math,collections,random,hashlib,sys,html
R=Path(__file__).resolve().parent;P=R.parent;SOURCE=P/'frequency-atlas-v48/rows.json'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def diversity(vals,m=20):
 n=len(vals);c=collections.Counter(vals)
 return sum(1-(math.comb(n-v,m)/math.comb(n,m) if n-v>=m else 0) for v in c.values())
def ranktest(groups,seed):
 # Conditional permutation of candidate-content counts among lines of same page/length/unknown count.
 blocks=[x for x in groups.values() if len(x)>1];den=0;obs=0;center=[]
 for b in blocks:
  ds=[x['d'] for x in b];cs=[x['c'] for x in b];dm=sum(ds)/len(ds);cm=sum(cs)/len(cs)
  dd=[v-dm for v in ds];cc=[v-cm for v in cs];den+=sum(v*v for v in dd);obs+=sum(a*b for a,b in zip(dd,cc));center.append((dd,cc))
 if not den:return {'status':'not estimable: no within-block daiin variation','movable_lines':sum(map(len,blocks))}
 rng=random.Random(seed);tail=0;low=0
 for _ in range(999):
  stat=0
  for dd,cc in center:
   perm=cc[:];rng.shuffle(perm);stat+=sum(a*b for a,b in zip(dd,perm))
  tail+=stat>=obs-1e-12;low+=stat<=obs+1e-12
 return {'status':'estimated','slope':obs/den,'p_positive':(1+tail)/1000,'p_negative_diagnostic':(1+low)/1000,'movable_lines':sum(map(len,blocks)),'blocks':len(blocks)}
if sys.argv[1]=='freeze':
 protocol={'scope':'Shared H/F loci; separate transcription, hand, section, Currier variety and raw format. No word harmonization. Exploratory written-form test, not semantic role qualification.', 'breadth':'Interior anchor positions only; readable immediate neighbour on each side separately. Expected distinct neighbour types in a uniform sample of exactly20 events (analytic hypergeometric rarefaction). Comparators require >=20 events on same side. Report daiin percentile among all eligible words and sensitivity restricted to event frequencies between half and twice daiin. >=5 peers and >=3 daiin folios needed for supported descriptive comparison. No p value or posthoc role inference from rank.', 'content':'Fixed whole-word set chedy/shedy/chey/cheol from v63, not inferred ingredients. Paragraph P only. Count daiin and candidate content per source line, uncertain slots retained. Residual slope within exact page x total slot length x unknown-slot count blocks. Permute content counts within blocks 999 times, one-sided positive prediction. >=20 movable lines and >=3 contributing folios. Bonferroni over all estimated eligible H/F strata. Preserve negative slopes and unsupported strata.', 'qualification':'Synthetic nuisance and positive-control engineering check before manuscript scoring; not independent known-text semantic qualification. No new role assignment. Existing known-text role gate remains closed.', 'rebus':'Supplied anomaly percentages unverified. Template irregularity, repeated rare groups and initial-sign deletion cannot identify phonetic encoding. Need training-defined templates, held-out controls for length/frequency/hand/format/position and reading ambiguity, plus independently anchored readings to support phonetics.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [R/'PROTOCOL.json',Path(__file__),SOURCE,P/'phrase-reading-v63/FIFTH-READING-PROTOCOL.json']});print('Frozen; no manuscript statistics scored.')
else:
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 # Deterministic positive and no-signal controls; implementation checks only.
 control={('p',i):[{'d':j,'c':2*j} for j in range(4)] for i in range(10)}
 positive=ranktest(control,6401);null=ranktest({k:[{'d':x['d'],'c':2} for x in b] for k,b in control.items()},6402)
 assert positive['slope']==2 and positive['p_positive']<=.01 and null['slope']==0 and null['p_positive']==1
 assert abs(diversity(['a']*20)-1)<1e-10 and abs(diversity(list(range(20)))-20)<1e-10
 save('ENGINEERING-CHECKS.json',{'positive':positive,'constant_null':null,'rarefaction_endpoints':'pass','limit':'Not a calibrated false-positive or known-text role qualification suite.'})
 rows=load(SOURCE);coverage=collections.defaultdict(set)
 for r in rows:coverage[r[6]].add(r[0])
 panels=collections.defaultdict(list)
 for r in rows:
  if coverage[r[6]]=={'H','F'}:panels[tuple(r[:1]+r[2:6])].append(r)
 breadth=[];content=[];exceptions=[]
 for idx,(key,rr) in enumerate(sorted(panels.items())):
  for side,delta in [('left',-1),('right',1)]:
   events=collections.defaultdict(list);folios=collections.defaultdict(set)
   for r in rr:
    ws=r[7]
    for i in range(1,len(ws)-1):
     w=ws[i];v=ws[i+delta]
     if w is not None and v is not None:events[w].append(v);folios[w].add(r[1].split('r')[0].split('v')[0])
   ds=events.get('daiin',[])
   if not ds:continue
   row={'stratum':key,'side':side,'daiin_events':len(ds),'daiin_folios':len(folios['daiin'])}
   if len(ds)<20:row['status']='insufficient daiin events';breadth.append(row);continue
   dv=diversity(ds);peers=[{'word':w,'events':len(v),'diversity':diversity(v)} for w,v in events.items() if w!='daiin' and len(v)>=20];matched=[x for x in peers if len(ds)/2<=x['events']<=len(ds)*2]
   row.update({'daiin_diversity':dv,'all_peers':len(peers),'matched_peers':len(matched),'percentile_all':sum(x['diversity']<dv for x in peers)/len(peers) if peers else None,'percentile_matched':sum(x['diversity']<dv for x in matched)/len(matched) if matched else None,'status':'supported descriptive comparison' if len(matched)>=5 and len(folios['daiin'])>=3 else 'sparse frequency-matched reference','peers':sorted(peers,key=lambda x:-x['diversity'])});breadth.append(row)
  if key[-1]!='P':continue
  blocks=collections.defaultdict(list)
  for r in rr:
   ws=r[7];blocks[(r[1],len(ws),ws.count(None))].append({'locator':r[6],'page':r[1],'d':ws.count('daiin'),'c':sum(w in {'chedy','shedy','chey','cheol'} for w in ws),'words':ws})
  eligible=[x for b in blocks.values() if len(b)>1 and len({a['d'] for a in b})>1 for x in b];nf=len({x['page'].split('r')[0].split('v')[0] for x in eligible})
  result=ranktest(blocks,64100+idx) if len(eligible)>=20 and nf>=3 else {'status':'not estimable: <20 variable-block lines or <3 folios'}
  result.update({'stratum':key,'variable_block_lines':len(eligible),'contributing_folios':nf});content.append(result)
  exceptions.extend(dict(x,stratum=key) for x in eligible if x['d'] and not x['c'])
 M=sum(x['status']=='estimated' for x in content)
 for x in content:
  if x['status']=='estimated':x['p_adjusted']=min(1,x['p_positive']*M);x['passes']=x['slope']>0 and x['p_adjusted']<=.05
 save('BREADTH.json',breadth);save('CONTENT.json',content);save('ZERO-CONTENT-EXCEPTIONS.json',exceptions)
 summary={'breadth_rows':len(breadth),'supported_frequency_matched_rows':sum(x['status']=='supported descriptive comparison' for x in breadth),'content_tests':M,'positive_passes':sum(x.get('passes',False) for x in content),'zero_content_examples':len(exceptions),'interpretation':'Written-form associations only. Ranks are descriptive; no phonetic or glue-word meaning established.'};save('RESULTS.json',summary)
 body='<h1>Daiin: matched neighbourhoods and line-length controls</h1><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><h2>Neighbour breadth</h2><p>Expected different neighbours in 20 sampled events; sides and strata separate. Percentiles are descriptive, not significance tests. Sparse matched references cannot support a stable unusualness claim.</p>'
 for x in breadth:
  if 'daiin_diversity' in x:body+='<pre>'+html.escape(json.dumps({k:v for k,v in x.items() if k!='peers'},indent=2))+'</pre>'
 body+='<h2>Fixed candidate-content prediction</h2><pre>'+html.escape(json.dumps(content,indent=2))+'</pre>'
 for n in ['PROTOCOL.json','FREEZE.json','BREADTH.json','CONTENT.json','ZERO-CONTENT-EXCEPTIONS.json','ENGINEERING-CHECKS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Daiin context v64</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8');print(json.dumps(summary));print(json.dumps(content))
