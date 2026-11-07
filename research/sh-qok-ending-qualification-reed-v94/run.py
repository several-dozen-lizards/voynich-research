from pathlib import Path
import json,hashlib,collections,itertools,sys,math
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json';B=4999;FACTOR=16
ENDINGS=['edy','eey','ey','y']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def family(w):return next((s for s in ENDINGS if w.endswith(s)),None)
def encode(rows):
 words=sorted({w for r in rows for w in r['tokens'] if w});wid={w:i for i,w in enumerate(words)};pages=sorted({r['page'] for r in rows});pid={v:i for i,v in enumerate(pages)};arr=[];page=[];buckets={m:[] for m in ['whole_line','fixed_endpoints']};li=[];ri=[];offset=0
 for r in rows:
  ws=r['tokens'];arr.extend(wid[w] if w else -1 for w in ws);page.extend([pid[r['page']]]*len(ws))
  for j in range(len(ws)-1):
   if ws[j] and ws[j+1]:li.append(offset+j);ri.append(offset+j+1)
  start=0
  for j in range(len(ws)+1):
   if j<len(ws) and ws[j]:continue
   if j-start>1:buckets['whole_line'].append(np.arange(offset+start,offset+j))
   start=j+1
  # Same source-first/source-last and unknown-barrier bucket policy as v75/v78.
  start=1
  for j in range(1,len(ws)):
   if j<len(ws)-1 and ws[j]:continue
   if j-start>=2:buckets['fixed_endpoints'].append(np.arange(offset+start,offset+j))
   start=j+1
  offset+=len(ws)
 cls=np.array([0 if w.startswith('sh') else 1 if w.startswith('ch') else -1 for w in words]);fam=[family(w) for w in words];bodies=sorted({w[2:] for w,f,c in zip(words,fam,cls) if f and c>=0});bid={s:i for i,s in enumerate(bodies)}
 return dict(rows=rows,words=words,pages=pages,original=np.array(arr,dtype=np.int32),slot_page=np.array(page),li=np.array(li,dtype=int),ri=np.array(ri,dtype=int),buckets=buckets,cls=cls,qok=np.array([w.startswith('qok') for w in words]),valid=np.array([f is not None and c>=0 for f,c in zip(fam,cls)]),keys={'ending_family':np.array([ENDINGS.index(f) if f else -1 for f in fam]),'exact_body':np.array([bid.get(w[2:],-1) if f and c>=0 else -1 for w,f,c in zip(words,fam,cls)])},K={'ending_family':4,'exact_body':max(1,len(bodies))},body_labels=bodies)
def score(arr,p,view,detail=False):
 a=arr[p['li']];b=arr[p['ri']];keep=p['valid'][a];a=a[keep];b=b[keep];pg=p['slot_page'][p['li'][keep]];K=p['K'][view];groups=pg*K+p['keys'][view][a];ix=groups*2+p['cls'][a];size=len(p['pages'])*K*2
 n=np.bincount(ix,minlength=size).reshape(-1,2);success=np.bincount(ix,weights=p['qok'][b].astype(int),minlength=size).reshape(-1,2);ok=(n[:,0]>0)&(n[:,1]>0);delta=np.zeros(len(n));delta[ok]=success[ok,0]/n[ok,0]-success[ok,1]/n[ok,1];weight=np.zeros(len(n));weight[ok]=n[ok,0]*n[ok,1]/n[ok].sum(axis=1);den=weight.reshape(-1,K).sum(axis=1);num=(weight*delta).reshape(-1,K).sum(axis=1);eligible=den>0;pd=np.divide(num,den,out=np.zeros(len(den)),where=eligible);T=float(pd[eligible].mean()) if eligible.any() else 0.
 if not detail:return T,int(eligible.sum())
 cells=[]
 for i,page in enumerate(p['pages']):
  for k in range(K):
   j=i*K+k
   if n[j].sum():cells.append(dict(page=page,key=ENDINGS[k] if view=='ending_family' else p['body_labels'][k],sh_n=int(n[j,0]),ch_n=int(n[j,1]),sh_qok=int(success[j,0]),ch_qok=int(success[j,1]),comparable=bool(ok[j]),delta=float(delta[j]) if ok[j] else None,weight=float(weight[j])))
 return dict(T=T,eligible_pages=int(eligible.sum()),positive_pages=int(((pd>1e-12)&eligible).sum()),negative_pages=int(((pd< -1e-12)&eligible).sum()),tie_pages=int(((abs(pd)<=1e-12)&eligible).sum()),pages=[dict(page=page,eligible=bool(eligible[i]),gap=float(pd[i]) if eligible[i] else None,sh_share=prefix_share(p['rows'],page)) for i,page in enumerate(p['pages'])],cells=cells)
def prefix_share(rows,page):
 ws=[w for r in rows if r['page']==page for w in r['tokens'] if w and w.startswith(('ch','sh'))];return sum(w.startswith('sh') for w in ws)/len(ws) if ws else None
def direct(arr,p,view):
 ds=collections.defaultdict(lambda:[0,0,0,0]);off=0
 for r in p['rows']:
  for j in range(len(r['tokens'])-1):
   ia,ib=arr[off+j],arr[off+j+1]
   if ia<0 or ib<0:continue
   w=p['words'][ia];f=family(w)
   if f is None or not w.startswith(('sh','ch')):continue
   c=0 if w.startswith('sh') else 1;key=f if view=='ending_family' else w[2:];z=ds[(r['page'],key)];z[c]+=1;z[c+2]+=p['words'][ib].startswith('qok')
  off+=len(r['tokens'])
 page=collections.defaultdict(lambda:[0.,0.])
 for (pg,k),(ns,nc,ss,sc) in ds.items():
  if ns and nc:
   wt=ns*nc/(ns+nc);page[pg][0]+=wt*(ss/ns-sc/nc);page[pg][1]+=wt
 return sum(a/b for a,b in page.values())/len(page) if page else 0.
def simulate(p,mode,N,seed,views):
 rng=np.random.default_rng(seed);scores={v:np.empty(N) for v in views};coverage={v:np.empty(N,dtype=np.int16) for v in views};batch=100
 for start in range(0,N,batch):
  size=min(batch,N-start);aa=np.tile(p['original'],(size,1))
  for ix in p['buckets'][mode]:
   order=np.argsort(rng.random((size,len(ix))),axis=1);aa[:,ix]=p['original'][ix][order]
  for j,arr in enumerate(aa):
   for v in views:scores[v][start+j],coverage[v][start+j]=score(arr,p,v)
  if N>=4000 and (start+size)%1000==0:print(mode,start+size,'/',N,flush=True)
 return scores,coverage
def frozen():
 for pp,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(pp))==h
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Retrospective structural qualification of exposed sh/ch and qok claims. Original Claude gap.py unavailable here; not an exact reproduction of its inline tests. No semantics assigned.',panels='Balneological hand2/B/P and Starred paragraphs hand3/B/P, H/F separate on shared eligible source loci, all original pages incl f75. Match v75/v78 panels. Page means physical source page; numbered-folio counts also retained.',endings=ENDINGS,ending_rule='Literal longest matching suffix among edy,eey,ey,y, disjoint with listed priority. Exact initial sh or ch; no glyph regrouping, prefix stripping beyond these characters, spelling repair or e-run normalization. Keep unknown slots as barriers.',outcome='Immediate next readable source token starts qok. Origins at line end or followed by unknown excluded. No source-line or unknown crossing. Paragraphs not established sentences.',primary_statistic='Within each physical page and suffix family, compute next-qok probability difference sh minus ch where both have >=1eligible origin. Weight these family differences by harmonic exposure ns*nc/(ns+nc). Compute equal-weight mean across eligible pages. Recompute strata/eligibility/weights in every permutation; no eligible page => statistic0. Save every excluded cell/page and permutation eligible-page counts.',exact_body='Predeclared stricter diagnostic matches page and exact rest of word after initial ch/sh, e.g. shedy vs chedy, rather than broad ending family. Same statistic. It may have low support; a failure is not absence.',nulls='Primary whole_line permutes complete word tokens within every contiguous readable run in each source line, including endpoints. Sensitivity fixed_endpoints uses unchanged v75/v78 source-first/source-last/unknown-barrier bucket policy. Both preserve each line multiset and unknown slots, never join gaps; exact interior ordinals and transitions not fixed.',permutations=B,seeds='94000+panel index*100+mode index, fixed order bathH,bathF,starredH,starredF; whole_line then fixed_endpoints.',correction='One-sided sh>ch Monte Carlo p=(1+#null T>=observed T)/(B+1). Bonferroni16 across4panels x2matching views x2nulls. This accounts only for declared audit comparisons, NOT the historical exploratory selection of endings, prefixes, panels or hypotheses. No fresh confirmatory p-values claimed. H/F are alternate readings of same manuscript, not independent replications.',qualification='Before manuscript scoring, independently check optimized statistic against direct counting over all720 permutations of authored6word line, both views; exact-orbit upper-tail false-flag fraction at alpha.05 and alpha.05/16 must obey rank bound. Check line multisets, unknown slots and pinned endpoints for both nulls on authored damaged and multi-line fixtures. A24line authored positive matched-body fixture must have T>=.9 and correctedp<=.05 under both nulls, same4999permutations. A no-qok fixture must haveT0/p1. These qualify arithmetic/invariants and one planted effect only, not grammar or all alternatives. Any failure stops manuscript run.',interpretation='Page-level use rates and within-page conditional differences can coexist. Broad suffix matching does not isolate sh itself from vocabulary/rest-of-word confounds. Exact-body test is stronger but still cannot distinguish grammar, collocation, spelling conditioned on context, sandhi/junction processes, copying or notation. Grammar can be adjacent; first-order local chains can produce gap effects. No thing/action assignments. Use existing v78 gap qualification/results; do not rerun or reinterpret corrected negatives as no effect.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]});print('Frozen audit rules.')
elif sys.argv[1]=='qualify':
 frozen();ws=['a','shedy','qokam','chedy','dar','x'];p=encode([dict(page='toy',tokens=ws)]);vals=[];checks=0
 for perm in itertools.permutations(p['original']):
  arr=np.array(perm);z=[]
  for view in ['ending_family','exact_body']:
   v,_=score(arr,p,view);assert abs(v-direct(arr,p,view))<1e-12;z.append(v);checks+=1
  vals.append(z)
 vals=np.array(vals);bounds=[]
 for j in range(2):
  tail=np.array([(vals[:,j]>=x-1e-12).mean() for x in vals[:,j]])
  for alpha in [.05,.05/FACTOR]:assert (tail<=alpha).mean()<=alpha+1e-12;bounds.append(dict(view=j,alpha=alpha,flag_fraction=float((tail<=alpha).mean())))
 fixture=encode([dict(page='x',tokens=['a','shedy',None,'chedy','qokam','x']),dict(page='y',tokens=['a','shedy','qokam','chedy','x'])]);rng=np.random.default_rng(941)
 for mode in fixture['buckets']:
  for _ in range(100):
   arr=fixture['original'].copy()
   for ix in fixture['buckets'][mode]:arr[ix]=rng.permutation(arr[ix])
   off=0
   for r in fixture['rows']:
    n=len(r['tokens']);assert sorted(arr[off:off+n])==sorted(fixture['original'][off:off+n]);assert np.array_equal(arr[off:off+n]<0,fixture['original'][off:off+n]<0)
    if mode=='fixed_endpoints':assert arr[off]==fixture['original'][off] and arr[off+n-1]==fixture['original'][off+n-1]
    off+=n
   for view in ['ending_family','exact_body']:assert abs(score(arr,fixture,view)[0]-direct(arr,fixture,view))<1e-12
 positive=encode([dict(page='p'+str(i//4),tokens=ws) for i in range(24)]);controls=[]
 for k,mode in enumerate(['whole_line','fixed_endpoints']):
  null,_=simulate(positive,mode,B,9420+k,['ending_family','exact_body'])
  for view in null:
   T=score(positive['original'],positive,view)[0];pv=(1+sum(null[view]>=T-1e-12))/(B+1);assert T>=.9 and pv*FACTOR<=.05;controls.append(dict(mode=mode,view=view,T=T,p=float(pv),adjusted=float(min(1,pv*FACTOR))))
 negative=encode([dict(page='p',tokens=['a','shedy','dar','chedy','x'])]);assert score(negative['original'],negative,'ending_family')[0]==0
 save('QUALIFICATION.json',dict(status='PASS',direct_orbit_checks=checks,orbit_rank_bounds=bounds,multiset_barrier_endpoint_checks=200,positive_controls=controls,no_qok_T=0,no_qok_p=1,limits='Arithmetic/invariants plus one strong planted adjacency family. No semantic or general-power qualification.'));print('Qualification PASS.')
else:
 frozen();assert json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS';raw=json.loads(S.read_text());results=[];all_rows={};events=[]
 for pi,(sec,hand,code) in enumerate([('Balneological','2','H'),('Balneological','2','F'),('Starred paragraphs','3','H'),('Starred paragraphs','3','F')]):
  eligible={co:{x[8] for x in raw if x[0]==co and x[2]==sec and x[3]==hand and x[4]=='B' and x[5]=='P'} for co in ['H','F']};shared=eligible['H']&eligible['F'];rr=[dict(page=x[1],locator=x[8],tokens=x[9],raw=x[10]) for x in raw if x[0]==code and x[8] in shared];all_rows[str(pi)]=rr;p=encode(rr);observed={v:score(p['original'],p,v,True) for v in ['ending_family','exact_body']}
  for r in rr:
   for i in range(len(r['tokens'])-1):
    w,n=r['tokens'][i:i+2]
    if w and n and w.startswith(('sh','ch')) and family(w):events.append(dict(panel=pi,reading=code,section=sec,page=r['page'],locator=r['locator'],index=i,word=w,next=n,ending=family(w),qok=n.startswith('qok'),raw=r['raw']))
  for mi,mode in enumerate(['whole_line','fixed_endpoints']):
   null,cov=simulate(p,mode,B,94000+pi*100+mi,list(observed));np.savez_compressed(R/f'panel{pi}-{mode}-null.npz',**null,**{v+'_coverage':c for v,c in cov.items()})
   for view,ob in observed.items():
    pv=(1+sum(null[view]>=ob['T']-1e-12))/(B+1);results.append(dict(panel=pi,reading=code,section=sec,hand=hand,variety='B',format='P',lines=len(rr),physical_pages=len(p['pages']),view=view,null=mode,observed=ob,null_mean=float(null[view].mean()),null_95=[float(x) for x in np.quantile(null[view],[.025,.975])],eligible_pages_null_range=[int(cov[view].min()),int(cov[view].max())],p_upper=float(pv),p_adjusted=float(min(1,pv*FACTOR)),permutations=B))
  print('Finished',code,sec,flush=True)
 save('RESULTS.json',results);save('ROWS.json',all_rows);save('EVENTS.json',events);save('SUMMARY.json',[{k:v for k,v in z.items() if k!='observed'}|dict(T=z['observed']['T'],eligible_pages=z['observed']['eligible_pages'],positive_pages=z['observed']['positive_pages']) for z in results]);print(json.dumps(read_summary if False else [{k:z[k] for k in ['reading','section','view','null','p_adjusted']}|dict(T=z['observed']['T'],eligible=z['observed']['eligible_pages'],positive=z['observed']['positive_pages']) for z in results],indent=2))
