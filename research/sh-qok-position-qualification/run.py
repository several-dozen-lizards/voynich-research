from pathlib import Path
import json,hashlib,sys
import numpy as np
R=Path(__file__).resolve().parent
def save(n,x): (R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
REGIMES=['page_only','position_only','body_mix','line_environment','local_positive','no_overlap']
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh synthetic qualification only. No Voynich reads permitted by this script.',revision='Permute sh/ch labels among eligible origins within exact page, source-line token length, zero-based origin index, and exact remaining word body. Keep qok outcomes fixed. Secondary ending-family matching reported separately.',eligibility='Literal sh/ch initial with longest disjoint suffix edy,eey,ey,y. Next token must be readable within same line. Unknown slots retained in length and index, never bridged. Only strata containing both prefixes contribute. No smoothing or pooling sparse strata.',statistic='Within each page sum observed sh-qok successes minus conditional expectation; divide by sum ns*nc/n; equal mean across eligible pages. Conditional null draws hypergeometric successes independently per stratum, preserving sh/ch and qok margins. One-sided; 1999 draws, Bonferroni8 for future 2 panels x H/F x 2 views. No manuscript run here.',seeds='Fresh 961000+1000*regime+trial; null seed +100000',trials=200,regimes=REGIMES,generators='12 pages x 30 lines x 10 tokens. Eligible origins slots1,3,5,7; three exact bodies edy/eey/ey. Page-only correlates prefix and outcome rates across pages. Position-only correlates rates across interior slots. Body-mix correlates rates across bodies. Line-environment correlates both through a random per-line state. All four have independent prefix and outcome given the generator state, with probabilities .15/.85. Local-positive adds outcome probability .45 for sh (baseline .2) atop page prefix preference. No-overlap fixes sh at slot1/3 and ch at5/7 with matching position-specific outcomes.',gates='Primary exact-body only: each of four nuisance regimes Wilson95 upper false-flag bound <=.05 over200 trials; local-positive Wilson95 lower detection bound >=.80; no-overlap all200 not estimable. Arithmetic must agree with independent direct weighted differences. Every failure stops manuscript scoring. Ending-family secondary failures retained, not used to repair primary after outcomes.',limits='Conditional exchangeability across lines is an assumption. Line-environment adversary tests it explicitly. Qualification is finite, not evidence of grammar. No-overlap is missing support, not evidence against association. H/F must remain separate on shared readable loci in any later authorized retrospective manuscript run; previously exposed pages cannot be called fresh holdouts.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']});print('Frozen.');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items(): assert sha(Path(p))==h
def generate(reg,rng):
 events=[]
 for pg in range(12):
  pr=.15+.7*(pg%2)
  for line in range(30):
   state=rng.integers(2)
   for ix in [1,3,5,7]:
    body=str(rng.choice(['edy','eey','ey']))
    a=b=.5
    if reg=='page_only': a=b=pr
    elif reg=='position_only': a=b=.15+.7*(ix<4)
    elif reg=='body_mix': a=b=.85 if body=='edy' else .15
    elif reg=='line_environment': a=b=.15+.7*state
    elif reg=='local_positive': a=pr
    sh=int(rng.random()<a)
    if reg=='local_positive': b=.2+.45*sh
    q=int(rng.random()<b)
    if reg=='no_overlap': sh=q=int(ix<4)
    events.append((pg,10,ix,body,sh,q))
 return events
def test(events,view,rng):
 groups={}
 for pg,L,ix,body,sh,q in events:
  key=(pg,L,ix,body if view=='exact_body' else 'ey' if body.endswith('ey') else 'edy')
  z=groups.setdefault(key,[0,0,0,0]);z[0]+=1;z[1]+=sh;z[2]+=q;z[3]+=sh*q
 cells=[(key[0],*z) for key,z in groups.items() if 0<z[1]<z[0]]
 if not cells:return dict(T=None,p_adjusted=None,eligible_pages=0,eligible_strata=0,flag=False)
 a=np.array(cells);pg,n,ns,q,x=a.T;w=ns*(n-ns)/n;den=np.bincount(pg,weights=w,minlength=12);active=den>0
 obs=np.bincount(pg,weights=x-ns*q/n,minlength=12)[active]/den[active];T=float(obs.mean())
 direct=np.zeros(12)
 for page,nn,ss,qq,xx in cells: direct[page]+=(ss*(nn-ss)/nn)*(xx/ss-(qq-xx)/(nn-ss))
 assert abs(T-float((direct[active]/den[active]).mean()))<1e-12
 nullx=rng.hypergeometric(q,n-q,ns,size=(1999,len(cells)));coeff=1/den[pg]/active.sum()
 null=((nullx-ns*q/n)*coeff).sum(axis=1);p=min(1.,8*(1+int((null>=T-1e-12).sum()))/2000)
 return dict(T=T,p_adjusted=p,eligible_pages=int(active.sum()),eligible_strata=len(cells),flag=p<=.05)
def wilson(k,n):
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*np.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [max(0.,float(c-h)),min(1.,float(c+h))]
records=[]
for ri,reg in enumerate(REGIMES):
 for trial in range(200):
  seed=961000+1000*ri+trial;events=generate(reg,np.random.default_rng(seed))
  for vi,view in enumerate(['exact_body','ending_family']):
   records.append(dict(regime=reg,trial=trial,seed=seed,view=view,**test(events,view,np.random.default_rng(seed+100000+vi*10000))))
 save('TRIALS.json',records);print(reg,'complete',flush=True)
summary=[]
for reg in REGIMES:
 for view in ['exact_body','ending_family']:
  rr=[r for r in records if r['regime']==reg and r['view']==view];k=sum(r['flag'] for r in rr);ne=sum(r['T'] is None for r in rr);ci=wilson(k,len(rr))
  passed=ne==200 if reg=='no_overlap' else ci[0]>=.80 if reg=='local_positive' else ci[1]<=.05
  summary.append(dict(regime=reg,view=view,flags=k,total=200,not_estimable=ne,wilson95=ci,criterion_pass=passed))
passed=all(x['criterion_pass'] for x in summary if x['view']=='exact_body')
save('SUMMARY.json',dict(status='PASS' if passed else 'FAIL',manuscript_rescored=False,results=summary))
save('VERIFICATION.json',dict(freeze_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),independent_statistic_checks=sum(r['T'] is not None for r in records),trials_preserved=len(records),manuscript_read=False))
print('Primary qualification:', 'PASS' if passed else 'FAIL')
