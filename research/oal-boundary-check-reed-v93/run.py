from pathlib import Path
import collections as C,json,hashlib,sys
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json'
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Exposed descriptive queries, no confirmatory p-values, normalization, sound or name fit.',oal='Count exact token, proper initial (longer than oal), noninitial (any start index>0 including word-final), anywhere union. Preserve every reading separately and all source alternatives. Section metadata already combines Astronomy/Astrology.',seam='Split first alch into pre+al | ch+tail. Record standalone component frequencies without adopting boundaries. Compare tail token frequency distributions against ordinary initial-ch word tails, including empty tails.',metric='Explicit descriptive distribution overlap=sum min(p,q)=1-total variation. Quoted0.68 definition unavailable, so this cannot be called an exact replication of that metric. Also reweight ordinary-ch pools to alch section+hand+format strata; report missing strata.',boundary='Record adjacent complete words left ending al and right starting ch within each original row, no cross-unknown or cross-row joining. At joined-alch source loci look for exact candidate left,right in alternate source rows; retain full contexts because position alignment is not guaranteed.',limits='A common component does not disprove a restricted combination; shared endings do not establish a word boundary or root. Counts cannot select Pleiades or a lunar mansion. All g,m,y remain separate. No old frozen experiment changed.',provenance='A concurrently written oal-seam-audit-v92 folder was encountered; this isolated audit has its own script, frozen rules, input hash and records. No further edits to that folder.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]});print('Isolated audit frozen.')
else:
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
 rows=json.loads(S.read_text());codes=sorted({x[0] for x in rows});events=[];seams=[];pairs=[];byloc=C.defaultdict(list)
 def base(x,j,w):return dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],index=j,word=w,raw=x[10])
 for x in rows:
  byloc[x[8]].append(x)
  for j,w in enumerate(x[9]):
   if not w:continue
   if 'oal' in w:
    ix=[k for k in range(len(w)-2) if w[k:k+3]=='oal'];events.append(dict(**base(x,j,w),exact=w=='oal',proper_initial=w.startswith('oal') and len(w)>3,noninitial=any(k>0 for k in ix),anywhere=True,initial_oalch=w.startswith('oalch'),indices=ix))
   if 'alch' in w:
    k=w.index('alch');seams.append(dict(**base(x,j,w),before=w[:k],tail=w[k+4:],left=w[:k]+'al',right='ch'+w[k+4:]))
   if j+1<len(x[9]) and x[9][j+1] and w.endswith('al') and x[9][j+1].startswith('ch'):pairs.append(dict(**base(x,j,w),right=x[9][j+1]))
 counts=[];summary=[];splits=[]
 for code in codes:
  rr=[x for x in rows if x[0]==code];v=C.Counter(w for x in rr for w in x[9] if w);ee=[x for x in events if x['reading']==code];ss=[x for x in seams if x['reading']==code];tails=C.Counter(x['tail'] for x in ss);ordinary=C.Counter(w[2:] for x in rr for w in x[9] if w and w.startswith('ch'));n=sum(tails.values());m=sum(ordinary.values());strata=C.Counter((z['section'],z['hand'],z['format']) for z in ss);weighted=C.defaultdict(float);missing=[]
  for stratum,num in strata.items():
   pool=C.Counter(w[2:] for x in rr if (x[2],x[3],x[5])==stratum for w in x[9] if w and w.startswith('ch'));den=sum(pool.values())
   if not den:missing.append(dict(stratum=stratum,candidates=num));continue
   for t,val in pool.items():weighted[t]+=num/n*val/den
  for z in ss:
   z['left_frequency']=v[z['left']];z['right_frequency']=v[z['right']]
   for x in byloc[z['locator']]:
    if x[0]==code:continue
    ix=[j for j in range(len(x[9])-1) if x[9][j]==z['left'] and x[9][j+1]==z['right']]
    if ix:splits.append(dict(joined_reading=code,joined_word=z['word'],locator=z['locator'],split_reading=x[0],left=z['left'],right=z['right'],positions=ix,raw=x[10]))
  for section in sorted({x[2] for x in rr}):
   a=[x for x in ee if x['section']==section];counts.append(dict(reading=code,section=section,tokens=sum(bool(w) for x in rr if x[2]==section for w in x[9]),**{k:sum(x[k] for x in a) for k in ['exact','proper_initial','noninitial','anywhere','initial_oalch']},alch=sum(z['section']==section for z in ss)))
  summary.append(dict(reading=code,tokens=sum(v.values()),**{k:sum(x[k] for x in ee) for k in ['exact','proper_initial','noninitial','anywhere','initial_oalch']},alch=n,before=dict(C.Counter(z['before'] for z in ss).most_common()),tails=dict(tails.most_common()),ordinary_ch=m,overlap=sum(min(tails[t]/n,ordinary[t]/m) for t in tails) if n and m else None,matched_overlap=sum(min(tails[t]/n,weighted[t]) for t in tails) if n and not missing else None,missing_strata=missing,both_parts_attested=sum(z['left_frequency']>0 and z['right_frequency']>0 for z in ss),adjacent_pairs=sum(z['reading']==code for z in pairs),oal_standalone_frequency=v['oal']))
 locs={z['locator'] for z in events+seams+pairs};alts={l:[dict(reading=x[0],tokens=x[9],raw=x[10],page=x[1],section=x[2],hand=x[3],format=x[5]) for x in byloc[l]] for l in sorted(locs)}
 for name,data in [('COUNTS.json',counts),('SUMMARY.json',summary),('OAL-EVENTS.json',events),('SEAMS.json',seams),('ADJACENT-PAIRS.json',pairs),('ALTERNATE-SPLITS.json',splits),('ALTERNATES.json',alts)]:save(name,data)
 for z in seams:assert z['left']+z['right']==z['word']
 for code in codes:assert sum(x['anywhere'] for x in counts if x['reading']==code)==sum(x['reading']==code for x in events)
 save('VERIFICATION.json',dict(reading_codes=len(codes),splits_reconstruct=True,counts_reconcile=True,normalizations=0,sounds_fitted=0))
 print(json.dumps(dict(main=[s for s in summary if s['reading'] in ['H','F','U','V']],H_sections=[x for x in counts if x['reading']=='H'],H_exact_or_initial=[x for x in events if x['reading']=='H' and (x['exact'] or x['proper_initial'])],split_loci=sorted({z['locator'] for z in splits})),indent=2))
