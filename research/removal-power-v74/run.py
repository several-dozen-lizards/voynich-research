from pathlib import Path
import json,hashlib,random,itertools,sys,html,collections
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pvalue(vals):
 a=np.array(vals);signs=np.array(list(itertools.product((-1,1),repeat=len(a))));return float(np.mean(signs@a>=a.sum()-1e-12))
def score(panels):
 result={}
 for unit in ['character','group']:
  details=[]
  for tr in ['H','F']:
   folios=collections.defaultdict(list)
   for cell in panels[(unit,tr)]:
    a=cell['opening_first_rate']-cell['control_first_rate'];b=a-cell['opening_final_rate']+cell['control_final_rate'];folios[cell['folio']].append((a,b))
   vals=[[sum(v[j] for v in vv)/len(vv) for vv in folios.values()] for j in [0,1]]
   details.append({'transcription':tr,'effects':[sum(v)/len(v) for v in vals],'p':[pvalue(v) for v in vals],'folios':len(folios)})
  joint=max(p for x in details for p in x['p']);result[unit]={'details':details,'joint_p':joint,'adjusted_p':min(1,2*joint),'passes':2*joint<=.05 and all(e>0 for x in details for e in x['effects'])}
 return result
def geometry():
 tests=load(P/'opening-removal-v73/TESTS.json');return {(x['unit'],x['stratum'][0]):x['cells'] for x in tests if '|2|B|Botanical|P' in x['stratum'] and x.get('control')=='continuation_first'}
def simulate(geom,regime,trial):
 panels={};receipts=[]
 for (unit,tr),cells in geom.items():
  out=[]
  for ci,cell in enumerate(cells):
   # Shared seed for H/F and unit definitions; preserve actual sample counts in each.
   seed=int(hashlib.sha256(f'v74:{trial}:{cell["folio"]}:{ci}'.encode()).hexdigest()[:12],16);rng=random.Random(seed)
   nuisance=random.Random(seed//100).uniform(-.06,.06);base=.12+nuisance;effect={'null':0,'moderate':.4,'strong':.7,'small':.2,'line_start':0,'suffix':0,'H_only':.7 if tr=='H' else 0}.get(regime,0)
   if regime=='line_start':base=.6+nuisance
   rates={}
   for category,N in [('opening',len(cell['openers'])),('control',len(cell['controls']))]:
    first=base+(effect if category=='opening' else 0);last=.08+(.55 if regime=='suffix' and category=='opening' else 0);first=min(first,1-last);hits=[]
    for k in range(N):
     z=rng.random();state='prefix' if z<first else 'suffix' if z<first+last else 'neither'
     if cell['length']<2:state='neither'
     # A known finite lexicon: same-length ordinary stems, held apart from prefixed forms.
     stem='a'*(max(1,cell['length']-2))+'d';marker='p' if unit=='character' else 'cth';vocab={stem};word=marker+stem if state=='prefix' else stem+marker if state=='suffix' else 'z'*len(stem)+marker
     groups=lambda w:list(w) if unit=='character' else __import__('re').findall('cth|ckh|cph|cfh|ch|sh|[a-z]',w)
     parts=groups(word);fh=''.join(parts[1:]) in vocab;lh=''.join(parts[:-1]) in vocab
     if cell['length']<2:fh=lh=False
     hits.append((fh,lh))
     if trial==0:receipts.append({'unit':unit,'transcription':tr,'folio':cell['folio'],'category':category,'word':word,'vocabulary':list(vocab),'first_hit':fh,'final_hit':lh,'state':state})
    rates[category+'_first_rate']=sum(a for a,b in hits)/N;rates[category+'_final_rate']=sum(b for a,b in hits)/N
   out.append(dict(cell,**rates))
  panels[(unit,tr)]=out
 return score(panels),receipts
stage=sys.argv[1]
if stage=='freeze':
 protocol={'primary_scope':'Hand2/CurrierB/Botanical/P only, ordinary continuation-line starts primary control. v73 folio allocation, training vocabularies, source flags and exact matching unchanged. Other strata/interior controls remain v73 exploratory results. Scope chosen after v73; retrospective revision, not new independent confirmation.', 'revision':'Two unit definitions as two hypotheses. For each unit require positive effects and all four one-sided folio tests (H/F x first-removal excess and first-vs-final interaction). Intersection-union p=max(four p values), then Bonferroni2. H/F not independent replication; no independence assumption in this conjunction. Exact sign-flip over7folios. Minimum adjustedp=.015625; old family48 remains recorded.', 'qualification':'100 fixed-seed trials per regime using actual v73 matched-cell opener/control counts and folio clusters, but no manuscript success outcomes. Explicit planted-prefix/suffix finite lexicons. Shared folio nuisance±.06; base firsthit .12, finalhit .08; syntheticH/F coupled seeds. Effects+.20,+.40,+.70; negatives no effect,commonline-start enhancement,suffixonly,Honly. Known synthetic prefix mechanism, not independently labelled natural-language morphology.', 'gate':'Each unit detects>=80/100 at+.40 and>=90/100 at+.70. At most5/100 trials with any unit flag in each negative regime. If any gate fails, no rescoring manuscript. All trials retained. Small-effect power reported without a passing requirement.', 'limits':'Only simulated controls with known planted prefixes; lexical geometry simplified. Does not establish power against all manuscript nuisances. No raw-token pseudo-replication; folios remain test units. No tuning to a successful result.'}
 save('PROTOCOL.json',protocol);save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',P/'opening-removal-v73/TESTS.json',P/'opening-removal-v73/FREEZE.json',P/'opening-removal-v73/VOCABULARY-FREEZE.json']});print('Frozen revision')
elif stage=='qualify':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 geom=geometry();trials=[];examples={};summary=[]
 for regime in ['null','line_start','suffix','H_only','small','moderate','strong']:
  results=[]
  for trial in range(100):
   res,receipt=simulate(geom,regime,trial);results.append(res);trials.append({'regime':regime,'trial':trial,'results':res})
   if trial==0:examples[regime]=receipt
  summary.append({'regime':regime,'trials':100,'any_flags':sum(any(v['passes'] for v in res.values()) for res in results),'character_flags':sum(res['character']['passes'] for res in results),'group_flags':sum(res['group']['passes'] for res in results)});print(summary[-1],flush=True)
 gate=all(x['any_flags']<=5 for x in summary[:4]) and all(x[u+'_flags']>=limit for x,limit in [(summary[5],80),(summary[6],90)] for u in ['character','group']);save('TRIALS.json',trials);save('PREFIX-EXAMPLES.json',examples);save('QUALIFICATION.json',{'passes':gate,'summary':summary,'manuscript_rescored':False});print('Gate',gate)
elif stage=='score':
 for p,h in load(R/'FREEZE.json').items():assert sha(Path(p))==h
 q=load(R/'QUALIFICATION.json');res=score(geometry()) if q['passes'] else {'status':'Qualification failed. Manuscript not rescored.'};save('RESULTS.json',res)
 body='<h1>Removal-test power qualification — v74</h1><p>Two unit hypotheses; require H/F agreement and both first-removal excess and first-versus-final specificity. Ordinary line starts retained. Whole folios remain inferential units. v73 remains unchanged.</p><pre>'+html.escape(json.dumps(q,indent=2))+'</pre><h2>Manuscript status</h2><pre>'+html.escape(json.dumps(res,indent=2))+'</pre>'
 for n in ['PROTOCOL.json','FREEZE.json','QUALIFICATION.json','TRIALS.json','PREFIX-EXAMPLES.json','RESULTS.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 body+='<p><a href="../opening-removal-v73/report.html">Original H/F examples, failures and full48-outcome correction</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Removal power v74</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f5f2e9;color:#193c39}pre{white-space:pre-wrap}</style>'+body,encoding='utf-8');print(json.dumps(res))
