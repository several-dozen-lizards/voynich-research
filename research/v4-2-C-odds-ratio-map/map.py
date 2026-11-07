"""Frozen retrospective descriptive v4.2-C. Never imports/runs earlier analyses."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from fractions import Fraction
import csv
import hashlib
import json
import math
import sys
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.stats import chi2

R = Path(__file__).resolve().parent
P = R.parent
os.environ['MPLCONFIGDIR'] = str(R/'runtime-matplotlib')
CONTEXTS = ['C1','C2','C3','C4','C5','C6','C7','C8-4','C8-5','C6+C7']
LABELS = {'C1':'Scribe 2 · bath', 'C2':'Scribe 2 · botanical', 'C3':'Scribe 2 · Rosettes',
    'C4':'Scribe 3 · starred', 'C5':'Scribe 3 · botanical',
    'C6':'Scribe 1 · botanical', 'C7':'Scribe 1 · recipes',
    'C8-4':'Scribe 4 · astronomy/astrology', 'C8-5':'Scribe 5 · botanical',
    'C6+C7':'Scribe 1 · pooled A reference'}
RESERVED = {'f72v1','f72v2','f73r','f73v'}
B = 4999


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def save(name, value):
    (R/name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
def check(ok, why):
    if not ok: raise RuntimeError(why)
def seal(phase, names):
    path = R/'PHASES.jsonl'
    previous = sha(path) if path.exists() else None
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(dict(phase=phase, utc=now(), previous_log_sha256=previous,
                               hashes={n:sha(R/n) for n in names}))+'\n')
def check_seals():
    for line in (R/'PHASES.jsonl').read_text(encoding='utf-8').splitlines():
        for name, h in json.loads(line)['hashes'].items():
            check(sha(R/name)==h, 'Frozen artifact changed: '+name)
    for path,h in json.loads((R/'SOURCE-MANIFEST.json').read_text(encoding='utf-8'))['files'].items():
        check(sha(path)==h, 'Original input changed: '+path)
def finite_json(x):
    if isinstance(x, dict): return {k:finite_json(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [finite_json(v) for v in x]
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (float,np.floating)):
        check(not math.isnan(float(x)), 'Unexpected NaN')
        return 'Infinity' if x==math.inf else '-Infinity' if x==-math.inf else float(x)
    return x


def terms(tables):
    """Rows are a,b,c,d: sh-qok, sh-other, ch-qok, ch-other."""
    a = np.asarray(tables,dtype=float).reshape((-1,4))
    if not len(a): return np.zeros(5)
    aa,bb,cc,dd = a.T; n=a.sum(axis=1)
    keep=n>0; aa,bb,cc,dd,n=[x[keep] for x in (aa,bb,cc,dd,n)]
    return np.array([np.sum(aa*dd/n), np.sum(bb*cc/n),
        np.sum((aa*(cc+dd)-cc*(aa+bb))/n), np.sum((aa+bb)*(cc+dd)/n),
        np.sum(((aa+bb)>0)&((cc+dd)>0)&((aa+cc)>0)&((bb+dd)>0))])


def point(rs):
    rr,ss=float(rs[0]),float(rs[1])
    if rr==0 and ss==0: return None,None
    if ss==0: return math.inf,math.inf
    if rr==0: return 0.,-math.inf
    return rr/ss, math.log(rr)-math.log(ss)


def empirical_bounds(values):
    # Nearest-rank inverse empirical CDF preserves zero/infinite boundary draws.
    values=np.sort(np.asarray(values))
    return [float(values[max(0, math.ceil(p*len(values))-1)]) for p in (.025,.975)]


def bootstrap(page_terms, seed):
    if not len(page_terms): return dict(status='NOT ESTIMABLE',draws=0,seed=seed,OR_CI95=None,RD_CI95_points=None)
    rng=np.random.default_rng(seed)
    ix=rng.integers(len(page_terms),size=(B,len(page_terms)))
    total=page_terms[ix].sum(axis=1)
    rr,ss,nn,dd=total[:,:4].T
    valid=(rr>0)|(ss>0)
    vals=np.empty(B);vals.fill(np.nan)
    finite=(rr>0)&(ss>0)
    vals[finite]=np.log(rr[finite])-np.log(ss[finite])
    vals[(rr==0)&(ss>0)]=-math.inf;vals[(rr>0)&(ss==0)]=math.inf
    ci=empirical_bounds(vals) if valid.all() else None
    orci=[math.exp(v) if math.isfinite(v) else (0. if v<0 else math.inf) for v in ci] if ci else None
    rdgood=dd>0
    rdci=empirical_bounds(100*nn/dd) if rdgood.all() else None
    return dict(status='ESTIMATED' if valid.all() else 'CI WITHHELD: undefined 0/0 bootstrap draws',
        draws=B,seed=seed,finite_OR_draws=int(finite.sum()),zero_OR_draws=int(((rr==0)&(ss>0)).sum()),
        infinite_OR_draws=int(((rr>0)&(ss==0)).sum()),undefined_OR_draws=int((~valid).sum()),
        OR_CI95=orci,logOR_CI95=ci,RD_CI95_points=rdci,undefined_RD_draws=int((~rdgood).sum()),
        draw_indices_sha256=hashlib.sha256(ix.tobytes()).hexdigest())


def reml(y,v):
    y=np.asarray(y,dtype=float);v=np.asarray(v,dtype=float);k=len(y)
    check(k>=2 and np.isfinite(y).all() and np.isfinite(v).all() and (v>0).all(), 'Undefined REML input')
    def q(t):
        w=1/(v+t);mu=np.sum(w*y)/w.sum();return float(np.sum(w*(y-mu)**2))
    def obj(t): return float(.5*(np.log(v+t).sum()+np.log((1/(v+t)).sum())+q(t)))
    hi=max(float(np.ptp(y)**2),float(v.max()))*4
    for _ in range(60):
        if obj(hi)>obj(hi*.9): break
        hi*=2
    else: raise RuntimeError('REML bracket failed')
    # Search logarithmically plus all local minima, including the exact boundary.
    grid=np.r_[0.,np.geomspace(hi*1e-10,hi,301)]
    vals=np.array([obj(t) for t in grid]);candidates=[(0.,obj(0.))]
    for j in range(1,len(grid)-1):
        if vals[j]<=vals[j-1] and vals[j]<=vals[j+1]:
            opt=minimize_scalar(obj,bounds=(grid[j-1],grid[j+1]),method='bounded',options={'xatol':1e-13})
            check(opt.success,'REML optimization failed');candidates.append((float(opt.x),float(opt.fun)))
    tau,_=min(candidates,key=lambda z:z[1])
    def root(target):
        if q(0)<=target:return 0.
        upper=hi
        for _ in range(60):
            if q(upper)<=target:break
            upper*=2
        else:raise RuntimeError('Q-profile bracket failed')
        return float(brentq(lambda t:q(t)-target,0,upper))
    w=1/(v+tau);mu=float(np.sum(w*y)/w.sum());Q=q(0)
    return dict(status='DESCRIPTIVE ESTIMATE',k=k,pooled_logOR=mu,pooled_OR=math.exp(mu),tau2_logOR=tau,
        tau_logOR=math.sqrt(tau),Q_profile_CI95_tau2=[root(chi2.ppf(.975,k-1)),root(chi2.ppf(.025,k-1))],
        Q_descriptive=Q,I2_descriptive=max(0.,(Q-(k-1))/Q) if Q else 0.,df=k-1,
        inferential_p=None,note='Normal working model; selected retrospective contexts; cluster delta variances. Not a qualified heterogeneity/equality test; B-Q2 remains unqualified.')


def qualify():
    check_seals();check(not (R/'QUALIFICATION.json').exists(),'One-shot qualification already exists')
    tests=[];rng=np.random.default_rng(425260)
    for i in range(600):
        a=rng.integers(0,8,size=(1+i%7,4))
        r=Fraction(0);s=Fraction(0);rdn=Fraction(0);rdd=Fraction(0)
        for aa,bb,cc,dd in a.tolist():
            n=aa+bb+cc+dd
            if n:
                r+=Fraction(aa*dd,n);s+=Fraction(bb*cc,n)
                rdn+=Fraction(aa*(cc+dd)-cc*(aa+bb),n);rdd+=Fraction((aa+bb)*(cc+dd),n)
        got=terms(a);check(np.allclose(got[:4],[float(r),float(s),float(rdn),float(rdd)],rtol=1e-12,atol=1e-12),'Rational table oracle failed')
        tests.append(i)
    check(point([0,0])==(None,None),'0/0 handling')
    check(point([1,0])==(math.inf,math.inf),'Infinite OR handling')
    check(point([0,1])==(0.,-math.inf),'Zero OR handling')
    base=np.array([[10,20,5,25],[7,13,6,24],[2,8,4,16]],float)
    check(math.isclose(point(terms(base))[0]*point(terms(base[:,[2,3,0,1]]))[0],1.,rel_tol=1e-12),'Arm reversal failed')
    a=np.array([terms(row[None,:]) for row in base]);tot=a.sum(axis=0)
    inf=a[:,0]/tot[0]-a[:,1]/tot[1]
    for j in range(3):
        eps=1e-5;plus=tot+eps*a[j];minus=tot-eps*a[j]
        derivative=(point(plus)[1]-point(minus)[1])/(2*eps)
        check(abs(derivative-inf[j])<1e-9,'Cluster derivative oracle failed')
    for _ in range(50):
        ix=rng.integers(3,size=3)
        # Expanded independent strata vs repeated page contributions.
        check(np.allclose(terms(base[ix]),a[ix].sum(axis=0)),'Folio bootstrap expansion oracle failed')
    for y,var in [([0,0,0,0,0],.2),([-2,-1,0,1,2],.2),([.2,.3,.4,.5,.6],.2)]:
        got=reml(y,[var]*5)['tau2_logOR'];expected=max(0.,float(np.var(y,ddof=1))-var)
        check(abs(got-expected)<1e-6,'Equal-variance analytic REML oracle failed')
    check(empirical_bounds([-math.inf,0,math.inf])==[-math.inf,math.inf],'Boundary percentile oracle')
    bad=bootstrap(np.array([[0,0,0,1,0]],float),1)
    check(bad['OR_CI95'] is None and bad['undefined_OR_draws']==B,'Undefined bootstrap must not be silently dropped')
    save('QUALIFICATION.json',dict(status='PASS_ENGINEERING_ONLY',utc=now(),rational_table_fixtures=len(tests),
        arm_reversal=True,cluster_derivative_checks=3,expanded_folio_bootstrap_checks=50,
        analytic_equal_variance_REML_cases=3,boundary_and_invalid_draw_checks=True,
        scope='Arithmetic and implementation checks only. No manuscript significance, coverage, mechanism or heterogeneity qualification.'))
    seal('engineering_qualified_before_outcome_join',['QUALIFICATION.json'])


def masked_support(vv):
    groups=defaultdict(list)
    for e in vv:groups[e['folio'],e['family']].append(e)
    pages=defaultdict(float);discord=0
    for (pg,_),events in groups.items():
        sh=sum(e['x'] for e in events);ch=len(events)-sh
        pages[pg]+=sh*ch/len(events)
        if sh and ch:discord+=len(events)
    total=sum(pages.values());supported=sum(x>0 for x in pages.values())
    share=max(pages.values(),default=0)/total if total else None
    return dict(events=len(vv),folio_panel_units=len(pages),supported_folio_panel_units=supported,
        V=total,max_unit_support_share=share,discordant_origin_events=discord,
        original_support_gate=bool(total>=80 and supported>=8 and share<=.25))


def select(events,co,context,view):
    return [e for e in events if e['reading']==co and
            (e['context'] in ('C6','C7') if context=='C6+C7' else e['context']==context) and
            (e['available'] if view=='available' else True)]


def estimate(vv,seed,support,counts_only):
    groups=defaultdict(lambda:[0,0,0,0]);pages=sorted({e['folio'] for e in vv})
    for e in vv:groups[e['folio'],e['family']][(0 if e['x'] else 2)+(0 if e['y'] else 1)]+=1
    sh=sum(e['x'] for e in vv);ch=len(vv)-sh
    a=sum(e['x']*e['y'] for e in vv);c=sum((1-e['x'])*e['y'] for e in vv)
    base=dict(support=support,pooled_counts=dict(sh=sh,ch=ch,sh_qok=a,ch_qok=c),
        pooled_qok_rate_after_sh=a/sh if sh else None,pooled_qok_rate_after_ch=c/ch if ch else None,
        pooled_risk_ratio=(a/sh)/(c/ch) if sh and ch and c else ('Infinity' if sh and a and ch else None))
    if counts_only:return base|dict(status='COUNTS ONLY: inherited C8 <30 discordant origins',OR=None,bootstrap=None,cluster_logOR_variance=None)
    array=np.array([terms(np.array([row for (p,_),row in groups.items() if p==pg])) for pg in pages]) if pages else np.zeros((0,5))
    total=array.sum(axis=0);OR,logOR=point(total)
    variance=None
    if logOR is not None and math.isfinite(logOR) and len(pages)>1:
        influence=array[:,0]/total[0]-array[:,1]/total[1]
        variance=float(len(pages)/(len(pages)-1)*np.square(influence).sum())
    boot=bootstrap(array,seed)
    return base|dict(status='NOT ESTIMABLE: zero/zero MH contributions' if OR is None else 'DESCRIPTIVE' if support['original_support_gate'] else 'DESCRIPTIVE: support limited',
        OR=OR,logOR=logOR,MH_crossproducts=total[:2].tolist(),outcome_informative_strata=int(total[4]),
        MH_RD_points=100*float(total[2]/total[3]) if total[3]>0 else None,bootstrap=boot,cluster_logOR_variance=variance,
        folio_panel_terms={pg:array[i].tolist() for i,pg in enumerate(pages)})


def run():
    check_seals();check(not (R/'RESULTS.json').exists(),'One-shot run already exists; retain it')
    check(json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS_ENGINEERING_ONLY','Qualify arithmetic first')
    masked=json.loads((R/'inputs/MASKED-v3.1.json').read_text(encoding='utf-8'))
    check(all('y' not in e and 'outcome' not in e and 'follower' not in e for e in masked),'Masked source contains outcomes')
    check(not any(e['folio'] in RESERVED for e in masked),'Reserved zodiac in existing event population')
    keys=[(e['reading'],e['line'],e['position']) for e in masked];check(len(keys)==len(set(keys)),'Duplicate masked key')
    support={}
    for ri,co in enumerate(('H','F')):
        for vi,view in enumerate(('available','aggregate')):
            for ci,context in enumerate(CONTEXTS):
                key=f'{context}-{co}-{view}';support[key]=masked_support(select(masked,co,context,view))
    save('SUPPORT.json',support);seal('outcome_blind_support_preserved',['SUPPORT.json'])
    ledger={}
    with (R/'inputs/EVENTS.csv').open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            if row['exclusion_reason']:continue
            key=(row['reading'],row['line'],int(row['position']))
            check(key not in ledger,'Duplicate eligible event key');ledger[key]=row
    check(set(ledger)==set(keys),'Eligible event ledger and masked inventory differ')
    events=[]
    for m,key in zip(masked,keys):
        row=ledger[key]
        for field in ('folio','family','origin','context','reading','hand','section'):
            check(str(m[field])==row[field], 'Event metadata drift: '+field)
        check(int(row['x'])==m['x'] and (row['available']=='True')==m['available'],'Prefix/availability drift')
        y=int(row['y']);check(y in (0,1) and y==int(row['outcome']) and y==int(row['follower'].startswith('qok')),'Outcome reconciliation failed')
        events.append(m|dict(y=y))
    results={};tables=[]
    for ri,co in enumerate(('H','F')):
        for vi,view in enumerate(('available','aggregate')):
            for ci,context in enumerate(CONTEXTS):
                key=f'{context}-{co}-{view}';vv=select(events,co,context,view);s=support[key]
                row=estimate(vv,4252600+ri*1000+vi*100+ci,s,context.startswith('C8') and s['discordant_origin_events']<30)
                results[key]=dict(context=context,reading=co,view=view,label=LABELS[context],**row)
                groups=defaultdict(lambda:[0,0,0,0])
                for e in vv:groups[e['folio'],e['family']][(0 if e['x'] else 2)+(0 if e['y'] else 1)]+=1
                for (pg,family),cells in groups.items():tables.append(dict(context=context,reading=co,view=view,folio=pg,family=family,**dict(zip(('a','b','c','d'),cells))))
    with (R/'STRATUM-TABLES.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['context','reading','view','folio','family','a','b','c','d']);w.writeheader();w.writerows(tables)
    # Independent comparison of new RD points against untouched old receipts.
    original=json.loads((P/'sh-qok-context-map-v3/PART-B-ESTIMATES.json').read_text())
    checks=[]
    for key,row in results.items():
        old=original.get(row['context']+'-'+row['reading'],{}).get(row['view'])
        if old and row.get('MH_RD_points') is not None:
            err=abs(row['MH_RD_points']-old['effect_points']);check(err<1e-10,'Old risk-difference point changed');checks.append(dict(key=key,error=err))
    ca=json.loads((P/'currier-a-available-only-v1/RESULTS.json').read_text())
    for co in ('H','F'):
        err=abs(results[f'C6+C7-{co}-available']['MH_RD_points']-ca['readings'][co]['estimate']['effect_points'])
        check(err<1e-10,'Available-only Currier A RD did not replay');checks.append(dict(key='Currier-A-'+co,error=err))
    hetero={}
    for co in ('H','F'):
        for view in ('available','aggregate'):
            rr=[results[f'C{i}-{co}-{view}'] for i in range(1,6)]
            bad=[r['context'] for r in rr if r.get('logOR') is None or not math.isfinite(r['logOR']) or not r.get('cluster_logOR_variance') or r['cluster_logOR_variance']<=0]
            hetero[co+'-'+view]=dict(status='NOT ESTIMABLE',missing_or_zero_variance_contexts=bad,contexts=['C1','C2','C3','C4','C5'],inferential_p=None) if bad else reml([r['logOR'] for r in rr],[r['cluster_logOR_variance'] for r in rr])|dict(contexts=['C1','C2','C3','C4','C5'])
    save('RESULTS.json',finite_json(dict(retrospective=True,descriptive_only=True,readings_pooled=False,results=results,REML_C1_C5=hetero)))
    save('RECONCILIATION.json',dict(status='PASS',masked_events=len(masked),eligible_ledger_events=len(ledger),all_events_matched=True,RD_point_replay_checks=checks))
    seal('one_shot_descriptive_map_complete',['RESULTS.json','STRATUM-TABLES.csv','RECONCILIATION.json'])
    render()


def fmt(x, digits=2):
    if x is None:return '—'
    if x in ('Infinity','-Infinity'):return '∞' if x=='Infinity' else '−∞'
    return f'{x:.{digits}f}'
def interval(ci):return '['+', '.join(fmt(x) for x in ci)+']' if ci else 'not estimable'


def render():
    check_seals();d=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'));rr=d['results']
    lines=['# v4.2-C odds-ratio context map','', '**RETROSPECTIVE AND DESCRIPTIVE — all material exposed or uncertified. H/F are alternate readings and remain separate.**','',
        'The available-only map is primary here. It preserves the v3 event population and folio × ending strata, removing the previously defined blocked followers before stratification. C6+C7 is a fixed pooled reference, not an additional independent context. No new significance test or global-alpha claim is made.','',
        '![Available-only forest plot](available-only-forest.png)','']
    for view,title in [('available','Available-only comparison'),('aggregate','Aggregate companion (secondary)')]:
        lines+=['## '+title,'','| Context | H OR [folio-bootstrap 95% CI] | F OR [folio-bootstrap 95% CI] | H/F risk difference, pp | H/F supported units |','|---|---|---|---|---|']
        for context in CONTEXTS:
            h,f=[rr[f'{context}-{co}-{view}'] for co in ('H','F')]
            def cell(r):return 'counts only' if r['status'].startswith('COUNTS') else fmt(r.get('OR'))+' '+interval((r.get('bootstrap') or {}).get('OR_CI95'))
            lines.append(f"| {context}: {LABELS[context]} | {cell(h)} | {cell(f)} | {fmt(h.get('MH_RD_points'))} / {fmt(f.get('MH_RD_points'))} | {h['support']['supported_folio_panel_units']} / {f['support']['supported_folio_panel_units']} |")
    lines+=['','## Available-only base rates and support','','Rates below pool eligible origins within each context; they are not the adjusted MH estimand. RRs, ORs and RDs are distinct summaries.','',
        '| Context | Reading | sh qok/n | ch qok/n | sh rate | ch rate | V | Maximum unit share | Status |','|---|---|---|---|---|---|---|---|---|']
    for context in CONTEXTS:
        for co in ('H','F'):
            r=rr[f'{context}-{co}-available'];c=r['pooled_counts'];s=r['support']
            rate=lambda x:fmt(100*x)+'%' if x is not None else '—'
            lines.append(f"| {context} | {co} | {c['sh_qok']}/{c['sh']} | {c['ch_qok']}/{c['ch']} | {rate(r['pooled_qok_rate_after_sh'])} | {rate(r['pooled_qok_rate_after_ch'])} | {fmt(s['V'])} | {rate(s['max_unit_support_share'])} | {r['status']} |")
    lines+=['','## Requested descriptive REML summary across C1–C5','',
        'Each fixed five-context fit requires finite log-ORs and positive folio-cluster delta variances in every context. Missing/zero-variance contexts are retained and block the fit; no subset rescue or continuity correction is used.','']
    for key,r in d['REML_C1_C5'].items():
        lines.append(f"- **{key}:** "+(f"NOT ESTIMABLE; undefined/zero-variance contexts: {', '.join(r['missing_or_zero_variance_contexts'])}." if r['status']=='NOT ESTIMABLE' else f"descriptive pooled OR {fmt(r['pooled_OR'])}; τ²(log OR) {fmt(r['tau2_logOR'],4)}, Q-profile interval {interval(r['Q_profile_CI95_tau2'])}; Q={fmt(r['Q_descriptive'])}, I²={fmt(100*r['I2_descriptive'])}% (no inferential p)."))
    lines+=['','## Interpretation and limits','',
        '- This map estimates associations, not sound values, semantics, a mechanism, or a common underlying language. A same-sound sh/ch proposal is not excluded merely by assigning the same sound; it must explain the contextual distinction.',
        '- Similar point estimates or overlapping intervals do not establish equal strength. No equivalence margin, equivalence test or common-versus-variable predictive model comparison was specified here. C6/C7 should not be treated as independent of the pooled C6+C7 reference.',
        '- C1/C4 were selected in earlier work; all text and earlier RD outcomes were exposed. H/F agreement is reading robustness, not independent replication. REML and Q/I² are descriptive and do not repair unqualified B-Q2.',
        '- 4,999 seeded folio/panel-cluster bootstrap draws per row; zero/infinite OR draws retained. Any undefined 0/0 draw withholds the OR interval rather than silently removing draws. No half-cell correction, smoothing or replacement seed.',
        '- Clusters use the inherited source folio/panel identifiers. Several Rosettes panels may share a physical foldout; this bootstrap does not certify their physical independence. Sparse rows remain visible.',
        '- No raw EVT, images or reserved zodiac data were read. The analysis used only the already-exposed frozen v3 masked event inventory and its saved outcome ledger. Existing primaries, image-work holds and the inactive autonomous loop were preserved.','']
    (R/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    plot(d)
    seal('report_rendered',['REPORT.md','available-only-forest.png','available-only-forest.svg'])


def plot(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(13,7.5),sharey=True)
    def numeric(x):return math.inf if x=='Infinity' else -math.inf if x=='-Infinity' else x
    for ax,co,color in zip(axs,('H','F'),('#176b87','#ad5c27')):
        for i,context in enumerate(CONTEXTS):
            row=d['results'][f'{context}-{co}-available'];point_or=numeric(row.get('OR'))
            ci=(row.get('bootstrap') or {}).get('OR_CI95')
            if point_or is None:
                ax.text(.98,i,'counts only' if row['status'].startswith('COUNTS') else 'not estimable',transform=ax.get_yaxis_transform(),ha='right',fontsize=8,color='#555');continue
            if ci:
                lo,hi=map(numeric,ci);ax.plot([max(.1,lo),min(32,hi)],[i,i],color=color,lw=1.3)
                if lo<.1:ax.plot(.1,i,marker='<',color=color)
                if hi>32:ax.plot(32,i,marker='>',color=color)
            marker='<' if point_or<.1 else '>' if point_or>32 else 'o' if row['support']['original_support_gate'] else 's'
            ax.plot(min(32,max(.1,point_or)),i,marker=marker,color=color,ms=5)
        ax.set_xscale('log');ax.set_xlim(.1,32);ax.axvline(1,color='#777',lw=1,ls='--')
        ax.set_xticks([.125,.25,.5,1,2,4,8,16,32]);ax.set_xticklabels(['⅛','¼','½','1','2','4','8','16','32'])
        ax.set_title(co+' reading — available followers');ax.set_xlabel('Mantel–Haenszel odds ratio (log axis)');ax.grid(axis='x',alpha=.15)
        ax.spines[['top','right']].set_visible(False)
    axs[0].set_yticks(range(len(CONTEXTS)));axs[0].set_yticklabels([f'{c}: {LABELS[c]}' for c in CONTEXTS],fontsize=9)
    axs[0].invert_yaxis()
    fig.suptitle('v4.2-C · retrospective descriptive context map',fontsize=15)
    fig.text(.02,.015,'Bars: folio/panel bootstrap 95% intervals. Arrows: outside display range. Squares: original support gate not met.\nH/F are alternate readings; no equality or heterogeneity significance claim. Full values and undefined-draw counts are in RESULTS.json.',fontsize=8,color='#444')
    fig.tight_layout(rect=(0,.075,1,.95));fig.savefig(R/'available-only-forest.png',dpi=180);fig.savefig(R/'available-only-forest.svg');plt.close(fig)


if __name__=='__main__':
    {'qualify':qualify,'run':run}[sys.argv[1]]()
