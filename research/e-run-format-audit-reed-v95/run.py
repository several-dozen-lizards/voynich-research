from pathlib import Path
import json,hashlib,re,collections,itertools,sys,math
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json'
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def feature(w):
 runs=re.findall('e+',w)
 return (re.sub('e+','E',w),tuple(map(len,runs))) if runs else None
def role(x):
 if x[5]=='P':return 'paragraph'
 if re.fullmatch(r'[LS]\d*',x[5]) and x[1]!='f49v':return 'label'
 return None
def diversity(c):
 n=sum(c.values());return 1-sum(v*(v-1) for v in c.values())/(n*(n-1)) if n>=2 else None
def signflip(ds):
 if not ds:return dict(status='not estimable',n=0,p=None)
 a=np.array(ds,float);n=len(a);obs=float(a.mean())
 if n<=20:
  null=np.array([sum(x*y for x,y in zip(a,sg))/n for sg in itertools.product([-1,1],repeat=n)]);p=float(np.mean(null>=obs-1e-12));method='exact leaf sign-flip'
 else:
  rng=np.random.default_rng(9510);null=(rng.choice([-1,1],(9999,n))*a).mean(axis=1);p=float((1+sum(null>=obs-1e-12))/10000);method='9999 leaf sign-flips'
 return dict(status='estimated',n=n,T=obs,p=p,p_adjusted=min(1,4*p),method=method,assumption='Independent leaf clusters and symmetric distribution of paired differences under the null; does not preserve all vocabulary or textual dependence.')
def freezecheck():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(question='Do words in Recipes paragraph rows show more e-run-length variation than label words, after controlling word pattern, scribe, section and page where possible?',status='New execution rules on previously exposed corpus; no claim of untouched confirmatory material. No numeric, phonetic or semantic assignment.',reading='H and F separately. Natural coverage primary; an additional common-source-locus inventory is descriptive only. No substitution of U/V for missing F labels. Retain all reading codes at focal chEol locations.',formats='Paragraph=P only. Label=source codes L or S optionally followed by digits. Exclude f49v L alphabet-like series. Source label status does not establish a name or referent. T/Q/R/X/circular text excluded; no relabelling to improve support.',cohorts='Recipes hand1/A is primary in H/F. Starred paragraphs remains a distinct section, not relabelled Recipes. All other known1..5 hand/section/variety strata reported as separate descriptive structural controls, never pooled as recipe evidence. Ambiguous hands excluded from contrasts.',feature='Replace each maximal nonempty literal EVA e-run with E, preserving all other characters and every run position. Variant is vector of lengths of all runs. No-run words excluded. Thus cheol/cheeol/cheeeol share chEol, but chol is separate and not added after inspection. Main all_runs view plus predeclared single_run sensitivity. No ch/sh collapse, no prefix deletion, no unknown repair.',variation='Unbiased pairwise diversity D=1-sum n_v(n_v-1)/(N(N-1)), the chance that two distinct observed tokens differ in e-run vector. Require at least2 tokens per format within the same skeleton. This removes simple sample-size bias of distinct-type counts, not all dependence or measurement error.',matching='Strict same-page+skeleton contrasts: compute Dparagraph-Dlabel for each supported skeleton; equal-weight mean skeleton gaps withinpage, then average page gaps within numbered leaf (recto/verso and panels of same numberedleaf grouped), then equal leaf means per cohort. Always preserve unsupported families and pages. No threshold chosen from outcome.',inference='Only primary Recipes H/F xall_runs/single_run get one-sided leaf sign-flip p, Bonferroni4. Exact all2^n if n<=20; else9999 fixedseed9510. Assume independent leaves and symmetric paired differences under null. If fewer than2leaves report descriptive only, no claim of adequate power even if a p is calculable. All other cohort and cross-page same-stratum contrasts descriptive only. No all-token exchangeability test or semantics from a pass.',secondary='Same-section+hand+variety skeleton contrasts pooled acrosspages descriptive only, as a fallback that cannot control page spelling setting. Fixed focal chEol counts acrossall sections/readings/formats, with missing/zero forms and alternatives explicit. No search for a better-looking skeleton.',qualification='Before manuscript feature counts: known word examples and multiple-run/zero-run/unknown definitions; D versus direct unordered-pair enumeration; exact null expectation for binary equal-distribution samples of sizes3 and2, all32outcomes, must be0. Positive12leaf authored contrast must have signflipT>0 and correctedp<.05; reversed must notpass; allzero controlp1. Exact sign-flip orbit upper-tail rank bound checked on12leaf authored differences. This qualifies counting/sample-size correction and a synthetic signal only.',limits='Recipe labels mostly absent in F is known metadata limitation. Multiple glyph e readings may be transcription conventions. A paragraph-label difference cannot establish counting, numeral values or a writing mechanism. Failure to estimate is not evidence of equality. No new herbal/zodiac links or sounds.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]});print('Frozen e-run definitions, matching and primary contrasts.')
elif sys.argv[1]=='qualify':
 freezecheck();assert feature('cheol')==('chEol',(1,));assert feature('cheeol')==('chEol',(2,));assert feature('cheeeol')==('chEol',(3,));assert feature('chol') is None;assert feature('cheeedeeol')==('chEdEol',(3,2));assert feature('e')==('E',(1,))
 checks=0
 for n in range(2,7):
  for vals in itertools.product([1,2],repeat=n):
   c=collections.Counter(vals);direct=sum(a!=b for a,b in itertools.combinations(vals,2))/math.comb(n,2);assert abs(diversity(c)-direct)<1e-12;checks+=1
 diffs=[diversity(collections.Counter(v[:3]))-diversity(collections.Counter(v[3:])) for v in itertools.product([1,2],repeat=5)];assert abs(sum(diffs)/32)<1e-12
 ds=[.5]*12;pos=signflip(ds);neg=signflip([-x for x in ds]);zero=signflip([0.]*12);assert pos['p_adjusted']<.05 and neg['p_adjusted']>.05 and zero['p']==1
 orbit=np.array([sum(sg)/12 for sg in itertools.product([-1,1],repeat=12)]);tail=np.array([np.mean(orbit>=x-1e-12) for x in orbit]);assert np.mean(tail<=.05)<=.05
 save('QUALIFICATION.json',dict(status='PASS',pair_count_checks=checks,unequal_sample_null_expected_gap=float(sum(diffs)/32),positive=pos,reversed=neg,zero=zero,exact_rank_flag_fraction=float(np.mean(tail<=.05)),limits='Arithmetic, exact same-distribution expectation and12leaf planted signal only. No real token independence/power or glyph interpretation established.'));print('Qualification PASS.')
else:
 freezecheck();assert json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS';rows=json.loads(S.read_text());meta=[];events=[];focal=[];cohort=collections.defaultdict(lambda:collections.defaultdict(collections.Counter));byloc=collections.defaultdict(list)
 for x in rows:
  byloc[x[8]].append(x);rr=role(x)
  if rr and x[0] in ['H','F'] and x[3] in ['1','2','3','4','5']:
   meta.append(dict(reading=x[0],section=x[2],hand=x[3],variety=x[4],page=x[1],locator=x[8],role=rr,readable=sum(bool(w) for w in x[9]),unknown=sum(w is None for w in x[9])))
  for j,w in enumerate(x[9]):
   if not w:continue
   f=feature(w)
   if f and f[0]=='chEol':focal.append(dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],index=j,word=w,lengths=f[1],role=rr,raw=x[10]))
   if f and rr and x[0] in ['H','F'] and x[3] in ['1','2','3','4','5']:
    z=dict(reading=x[0],section=x[2],hand=x[3],variety=x[4],page=x[1],locator=x[8],index=j,role=rr,word=w,skeleton=f[0],lengths=f[1],runs=len(f[1]),raw=x[10]);events.append(z);key=(x[0],x[2],x[3],x[4]);cohort[key][(x[1],f[0],rr)].update([f[1]])
 counts=[];contrasts=[];primary=[]
 keys=sorted({(x['reading'],x['section'],x['hand'],x['variety']) for x in meta})
 for key in keys:
  mm=[m for m in meta if (m['reading'],m['section'],m['hand'],m['variety'])==key];ee=[z for z in events if (z['reading'],z['section'],z['hand'],z['variety'])==key];base=dict(zip(['reading','section','hand','variety'],key));counts.append(dict(**base,coverage={r:dict(rows=sum(m['role']==r for m in mm),readable=sum(m['readable'] for m in mm if m['role']==r),e_tokens=sum(z['role']==r for z in ee),pages=len({m['page'] for m in mm if m['role']==r})) for r in ['paragraph','label']}))
  for view in ['all_runs','single_run']:
   a=[z for z in ee if view=='all_runs' or z['runs']==1];d=collections.defaultdict(lambda:collections.Counter());pooled=collections.defaultdict(lambda:collections.Counter())
   for z in a:d[(z['page'],z['skeleton'],z['role'])].update([tuple(z['lengths'])]);pooled[(z['skeleton'],z['role'])].update([tuple(z['lengths'])])
   pagegaps=collections.defaultdict(list);cells=[]
   for pg,sk in sorted({(p,s) for p,s,r in d}):
    cp=d[(pg,sk,'paragraph')];cl=d[(pg,sk,'label')];dp=diversity(cp);dl=diversity(cl);ok=dp is not None and dl is not None
    if ok:pagegaps[pg].append(dp-dl)
    cells.append(dict(page=pg,skeleton=sk,paragraph_n=sum(cp.values()),label_n=sum(cl.values()),paragraph_variants={str(k):v for k,v in cp.items()},label_variants={str(k):v for k,v in cl.items()},D_paragraph=dp,D_label=dl,comparable=ok,gap=dp-dl if ok else None))
   leaves=collections.defaultdict(list)
   for pg,gaps in pagegaps.items():leaves[re.match(r'f\d+',pg)[0]].append(sum(gaps)/len(gaps))
   leafgaps={leaf:sum(ds)/len(ds) for leaf,ds in leaves.items()};cross=[]
   for sk in sorted({k[0] for k in pooled}):
    cp=pooled[(sk,'paragraph')];cl=pooled[(sk,'label')];dp=diversity(cp);dl=diversity(cl)
    if dp is not None and dl is not None:cross.append(dict(skeleton=sk,paragraph_n=sum(cp.values()),label_n=sum(cl.values()),D_paragraph=dp,D_label=dl,gap=dp-dl))
   record=dict(**base,view=view,samepage_cells=cells,eligible_cells=sum(x['comparable'] for x in cells),eligible_pages=len(pagegaps),page_gaps={pg:sum(gs)/len(gs) for pg,gs in pagegaps.items()},leaf_gaps=leafgaps,eligible_leaves=len(leafgaps),mean_leaf_gap=sum(leafgaps.values())/len(leafgaps) if leafgaps else None,crosspage_same_stratum=cross,crosspage_mean_gap=sum(z['gap'] for z in cross)/len(cross) if cross else None)
   contrasts.append(record)
   if key[1:] == ('Recipes','1','A'):
    primary.append(dict(**base,view=view,eligible_cells=record['eligible_cells'],eligible_pages=record['eligible_pages'],leaf_gaps=leafgaps,inference=signflip(list(leafgaps.values())),power_qualification='Not demonstrated at this manuscript sample size; fewer than2leaves is descriptive only.'))
 # Recipes F could have no feature-bearing rows but remains included by metadata cohort keys.
 focloc={z['locator'] for z in focal};alts={l:[dict(reading=x[0],tokens=x[9],raw=x[10],page=x[1],section=x[2],hand=x[3],format=x[5]) for x in byloc[l]] for l in sorted(focloc)}
 shared={l for l,rr in byloc.items() if {'H','F'}<={x[0] for x in rr}};sharedmeta=[m for m in meta if m['locator'] in shared]
 for n,v in [('COVERAGE.json',counts),('PRIMARY.json',primary),('CONTRASTS.json',contrasts),('EVENTS.json',events),('SOURCE-ROWS-METADATA.json',meta),('SHARED-LOCUS-METADATA.json',sharedmeta),('FOCAL-chEol.json',focal),('FOCAL-ALTERNATES.json',alts)]:save(n,v)
 print(json.dumps(dict(primary=primary,controlled=[{k:z[k] for k in ['reading','section','hand','variety','view','eligible_cells','eligible_pages','eligible_leaves','mean_leaf_gap','crosspage_mean_gap']} for z in contrasts if z['view']=='all_runs' and (z['eligible_cells'] or z['crosspage_same_stratum'])],focalHF=[z for z in focal if z['reading'] in ['H','F'] and z['section']=='Recipes']),indent=2))
