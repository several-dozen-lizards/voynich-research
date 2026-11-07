"""Frozen retrospective conditional predictive comparison; no vault or models."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
from fractions import Fraction
import csv,json,hashlib,math,re,sys
import numpy as np
from scipy.special import gammaln,logsumexp
from scipy.optimize import minimize,minimize_scalar
from scipy.stats import hypergeom
R=Path(__file__).resolve().parent
CONTEXTS=['C1','C2','C3','C4','C5','C6','C7','C8-4','C8-5']
FOLD_SEEDS=['v4.2-C2-primary','v4.2-C2-partition-1','v4.2-C2-partition-2','v4.2-C2-partition-3','v4.2-C2-partition-4']
SCENARIOS=['common_OR1','common_OR2','modest_heterogeneous','strong_heterogeneous']
SIM_N=20
BOOT_N=4999
SD_COMMON=2.5
SD_DEVIATION=1.

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def check(ok,why):
    if not ok:raise RuntimeError(why)
def seal(phase,names):
    path=R/'PHASES.jsonl';previous=sha(path) if path.exists() else None
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),previous_log_sha256=previous,hashes={n:sha(R/n) for n in names}))+'\n')
def seals():
    for line in (R/'PHASES.jsonl').read_text(encoding='utf-8').splitlines():
        for n,h in json.loads(line)['hashes'].items():check(sha(R/n)==h,'Frozen artifact drift: '+n)
    manifest=json.loads((R/'SOURCE-MANIFEST.json').read_text())
    for p,h in manifest['files'].items():check(sha(p)==h,'Source drift: '+p)

def physical_group(folio):
    m=re.fullmatch(r'f(\d+)[rv]\d*',folio);check(m is not None,'Unknown folio id')
    return 'rosettes-foldout' if int(m[1]) in (85,86) else 'f'+m[1]

def load():
    rows=[]
    with (R/'inputs/STRATUM-TABLES.csv').open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            if row['view']!='available' or row['context'] not in CONTEXTS:continue
            a,b,c,d=[int(row[x]) for x in ('a','b','c','d')]
            check(not row['folio'] in {'f72v1','f72v2','f73r','f73v'},'Reserved zodiac in input')
            rows.append(dict(reading=row['reading'],context=row['context'],ci=CONTEXTS.index(row['context']),
                folio=row['folio'],family=row['family'],group=physical_group(row['folio']),
                ns=a+b,nc=c+d,k=a+c,a=a,n=a+b+c+d))
    check(len({(x['reading'],x['folio'],x['family']) for x in rows})==len(rows),'Duplicate/nonexclusive source strata')
    return rows

def logcomb(n,k):return gammaln(n+1)-gammaln(k+1)-gammaln(n-k+1)

class Data:
    def __init__(self,rows):
        self.rows=rows;self.ci=np.array([r['ci'] for r in rows],dtype=int)
        self.a=np.array([r['a'] for r in rows],float)
        self.aa=[];self.base=[];self.start=[];cursor=0
        for r in rows:
            aa=np.arange(max(0,r['k']-r['nc']),min(r['ns'],r['k'])+1,dtype=float)
            check(len(aa)>0 and r['a'] in aa,'Impossible conditional table')
            self.start.append(cursor);cursor+=len(aa)
            self.aa.extend(aa);self.base.extend(logcomb(r['ns'],aa)+logcomb(r['nc'],r['k']-aa))
        self.start=np.asarray(self.start,dtype=int);self.aa=np.asarray(self.aa,float);self.base=np.asarray(self.base,float)
        self.sid=np.repeat(np.arange(len(rows)),np.diff(np.r_[self.start,cursor]))
        self.obsbase=np.array([logcomb(r['ns'],r['a'])+logcomb(r['nc'],r['k']-r['a']) for r in rows])

    def likelihood(self,beta):
        z=self.base+self.aa*beta[self.ci[self.sid]]
        maxima=np.maximum.reduceat(z,self.start)
        scaled=np.exp(z-maxima[self.sid]);sums=np.add.reduceat(scaled,self.start)
        norm=maxima+np.log(sums)
        means=np.add.reduceat(scaled*self.aa,self.start)/sums
        ll=self.obsbase+self.a*beta[self.ci]-norm
        return ll,means-self.a

def objective(parameters,data,varying):
    beta=np.repeat(parameters[0],len(CONTEXTS))+(parameters[1:] if varying else 0)
    ll,residual=data.likelihood(beta)
    value=-float(ll.sum())+.5*(parameters[0]/SD_COMMON)**2
    gradient=[float(residual.sum())+parameters[0]/SD_COMMON**2]
    if varying:
        value+=.5*float(np.square(parameters[1:]/SD_DEVIATION).sum())
        gradient.extend(np.bincount(data.ci,weights=residual,minlength=len(CONTEXTS))+parameters[1:]/SD_DEVIATION**2)
    return value,np.array(gradient)

def fit(rows,varying):
    check(rows,'Empty training fold')
    data=Data(rows)
    result=minimize(lambda p:objective(p,data,varying),np.zeros(1+len(CONTEXTS) if varying else 1),jac=True,
        method='L-BFGS-B',options=dict(maxiter=1000,ftol=1e-13,gtol=1e-7,maxls=50))
    value,gradient=objective(result.x,data,varying)
    check(np.isfinite(result.x).all() and (result.success or np.max(abs(gradient))<=1e-5),'Conditional fit failed')
    beta=np.repeat(result.x[0],len(CONTEXTS))+(result.x[1:] if varying else 0)
    unseen=sorted(set(range(len(CONTEXTS)))-set(data.ci))
    if varying:check(all(abs(result.x[1+i])<1e-12 for i in unseen),'Unseen context did not fall back to training shared effect')
    return dict(beta=beta.tolist(),shared_beta=float(result.x[0]),parameters=result.x.tolist(),
        iterations=int(result.nit),gradient_max=float(np.max(abs(gradient))),unseen_contexts=[CONTEXTS[i] for i in unseen])

def assignments(rows,seed):
    groups=sorted({r['group'] for r in rows},key=lambda g:hashlib.sha256((seed+':'+g).encode()).hexdigest())
    return {group:i%5 for i,group in enumerate(groups)}

def cv(rows,folds):
    scored=[];fits=[]
    for fold in range(5):
        train=[r for r in rows if folds[r['group']]!=fold];test=[r for r in rows if folds[r['group']]==fold]
        check(train and test,'Empty CV fold')
        check(not {r['group'] for r in train}&{r['group'] for r in test},'Group leakage')
        common=fit(train,False);varying=fit(train,True);data=Data(test)
        common_ll,_=data.likelihood(np.array(common['beta']));varying_ll,_=data.likelihood(np.array(varying['beta']))
        for r,lc,lv in zip(test,common_ll,varying_ll):
            informative=bool(r['ns'] and r['nc'] and 0<r['k']<r['n'])
            scored.append(dict(reading=r['reading'],context=r['context'],folio=r['folio'],family=r['family'],group=r['group'],fold=fold,
                origins=r['n'],informative_origins=r['n'] if informative else 0,common_LL=float(lc),varying_LL=float(lv),delta_LL=float(lv-lc)))
        fits.append(dict(fold=fold,train_groups=len({r['group'] for r in train}),test_groups=len({r['group'] for r in test}),common=common,varying=varying))
    check(len(scored)==len(rows),'CV rows missing or duplicated')
    total=sum(r['origins'] for r in scored);delta=sum(r['delta_LL'] for r in scored)
    return dict(delta_LL_nats=delta,origins=total,delta_nats_per_origin=delta/total,
        common_LL=sum(r['common_LL'] for r in scored),varying_LL=sum(r['varying_LL'] for r in scored),
        informative_origins=sum(r['informative_origins'] for r in scored),rows=scored,fits=fits)

def bootstrap_scores(scores,seed):
    groups=sorted({r['group'] for r in scores});totals=np.zeros((len(groups),2));lookup={g:i for i,g in enumerate(groups)}
    for row in scores:totals[lookup[row['group']]]+=[row['delta_LL'],row['origins']]
    rng=np.random.default_rng(seed);ix=rng.integers(len(groups),size=(BOOT_N,len(groups)))
    sampled=totals[ix].sum(axis=1);values=sampled[:,0]/sampled[:,1]
    return dict(draws=BOOT_N,seed=seed,groups=len(groups),CI95_nats_per_origin=np.quantile(values,[.025,.975]).tolist(),
        note='Paired group bootstrap of saved OOF scores, conditional on fitted training sets and fixed partition. Does not include training-refit uncertainty or establish nominal selection-test error control.')

def synthetic(rows,scenario,seed):
    rng=np.random.default_rng(seed);out=[]
    for row in rows:
        botanical=row['context'] in ('C2','C5','C6','C8-5')
        odds=1. if scenario=='common_OR1' else 2. if scenario=='common_OR2' else (1.5 if botanical else 2.5) if scenario=='modest_heterogeneous' else (1. if botanical else 4.)
        aa=np.arange(max(0,row['k']-row['nc']),min(row['ns'],row['k'])+1)
        logs=logcomb(row['ns'],aa)+logcomb(row['nc'],row['k']-aa)+aa*math.log(odds)
        probs=np.exp(logs-logsumexp(logs));chosen=int(rng.choice(aa,p=probs))
        out.append(row|dict(a=chosen))
    return out

def qualify():
    seals();check(not (R/'QUALIFICATION.json').exists(),'Qualification already recorded')
    checked=0
    for ns in range(1,7):
        for nc in range(1,7):
            for k in range(ns+nc+1):
                aa=list(range(max(0,k-nc),min(ns,k)+1));base=np.array([math.comb(ns,a)*math.comb(nc,k-a) for a in aa],float)
                row=dict(ci=0,ns=ns,nc=nc,k=k,a=aa[0]);d=Data([row])
                z=d.base-d.base.max();pmf=np.exp(z)/np.exp(z).sum()
                expected=hypergeom.pmf(aa,ns+nc,ns,k)
                check(np.allclose(pmf,expected,atol=1e-12),'Central hypergeometric oracle mismatch')
                weights=[Fraction(math.comb(ns,a)*math.comb(nc,k-a)*2**a) for a in aa];den=sum(weights)
                pmf2=np.exp(d.base+d.aa*math.log(2)-logsumexp(d.base+d.aa*math.log(2)))
                check(np.allclose(pmf2,[float(w/den) for w in weights],atol=1e-12),'Rational noncentral oracle mismatch')
                checked+=1
    toy=[dict(ci=i%3,ns=10,nc=12,k=8,a=3+i%4) for i in range(12)]
    d=Data(toy);gradient_checks=0
    for varying in (False,True):
        parameters=np.linspace(-.2,.2,10 if varying else 1);value,gradient=objective(parameters,d,varying)
        for i in range(len(parameters)):
            step=np.zeros(len(parameters));step[i]=1e-5
            numerical=(objective(parameters+step,d,varying)[0]-objective(parameters-step,d,varying)[0])/(2e-5)
            check(abs(numerical-gradient[i])<1e-7,'Gradient oracle mismatch');gradient_checks+=1
    expected=minimize_scalar(lambda b:objective(np.array([b]),d,False)[0],bounds=(-5,5),method='bounded',options={'xatol':1e-12})
    toy_rows=[r|dict(group='f'+str(i),context=CONTEXTS[r['ci']],reading='H',folio='f1r',family='y',n=r['ns']+r['nc']) for i,r in enumerate(toy)]
    got=fit(toy_rows,False);check(abs(got['shared_beta']-expected.x)<1e-6,'Independent scalar fit oracle mismatch')
    check(physical_group('f1r')==physical_group('f1v'),'Leaf-side grouping failed')
    check(len({physical_group(x) for x in ['f85r1','f85r2','f85v2','f86v3','f86v6']})==1,'Foldout grouping failed')
    unseen=fit([r for r in toy_rows if r['ci']!=2],True);check('C3' in unseen['unseen_contexts'],'Unseen context check absent')
    save('QUALIFICATION.json',dict(status='PASS_ENGINEERING_ONLY',conditional_distribution_cases=checked,
        gradient_checks=gradient_checks,independent_scalar_fit=True,grouping_and_unseen_fallback=True,
        no_manuscript_predictive_score_yet=True))
    seal('arithmetic_and_grouping_qualified',['QUALIFICATION.json'])

def controls():
    seals();check(not (R/'CONTROLS.json').exists(),'Controls already recorded')
    rows=load();folds=assignments(rows,FOLD_SEEDS[0]);records=[]
    for ri,co in enumerate(('H','F')):
        rr=[r for r in rows if r['reading']==co]
        for si,scenario in enumerate(SCENARIOS):
            for trial in range(SIM_N):
                seed=4262600+ri*100000+si*1000+trial
                sample=synthetic(rr,scenario,seed);result=cv(sample,folds)
                records.append(dict(reading=co,scenario=scenario,trial=trial,seed=seed,delta_nats_per_origin=result['delta_nats_per_origin'],delta_LL_nats=result['delta_LL_nats']))
                if (trial+1)%5==0:print('controls',co,scenario,trial+1,'/',SIM_N,flush=True)
    summary=[]
    for co in ('H','F'):
        for scenario in SCENARIOS:
            rr=[r for r in records if r['reading']==co and r['scenario']==scenario];values=[r['delta_nats_per_origin'] for r in rr]
            summary.append(dict(reading=co,scenario=scenario,n=len(rr),varying_wins=sum(x>0 for x in values),
                mean_delta_nats_per_origin=float(np.mean(values)),range_delta=[min(values),max(values)]))
    save('CONTROLS.json',dict(status='COMPLETED_ALL_FIXED_TRIALS',records=records,summary=summary,
        interpretation='Controls retain observed stratum totals/qok margins and use known conditional ORs. Sign wins are diagnostic, not a calibrated significance test or generic power estimate. No retuning or dropped trials.'))
    seal('fixed_synthetic_controls_complete_before_manuscript_CV',['CONTROLS.json'])

def run():
    seals();check(not (R/'RESULTS.json').exists(),'One-shot manuscript run already exists')
    check(json.loads((R/'CONTROLS.json').read_text())['status']=='COMPLETED_ALL_FIXED_TRIALS','Finish all fixed controls first')
    rows=load();foldings={seed:assignments(rows,seed) for seed in FOLD_SEEDS};results={}
    for ri,co in enumerate(('H','F')):
        rr=[r for r in rows if r['reading']==co];repeats=[]
        for seed in FOLD_SEEDS:
            result=cv(rr,foldings[seed]);result['partition_seed']=seed
            repeats.append(result);print('manuscript',co,seed,result['delta_nats_per_origin'],flush=True)
        primary=repeats[0];primary['score_bootstrap']=bootstrap_scores(primary['rows'],4263600+ri)
        by_context={}
        for context in CONTEXTS:
            scores=[r for r in primary['rows'] if r['context']==context];n=sum(r['origins'] for r in scores);gain=sum(r['delta_LL'] for r in scores)
            by_context[context]=dict(origins=n,groups=len({r['group'] for r in scores}),delta_LL_nats=gain,delta_nats_per_origin=gain/n if n else None)
        results[co]=dict(primary=primary,partition_sensitivities=repeats[1:],context_contributions=by_context)
    save('FOLDS.json',foldings);save('RESULTS.json',dict(retrospective=True,descriptive=True,H_F_pooled=False,results=results,
        sign_definition='positive delta = context-varying predicts better; negative = common predicts better',
        no_equivalence_margin=True,no_common_strength_declaration=True))
    seal('one_shot_manuscript_predictive_comparison_complete',['FOLDS.json','RESULTS.json'])
    render()

def render():
    seals();data=json.loads((R/'RESULTS.json').read_text());controls=json.loads((R/'CONTROLS.json').read_text())
    lines=['# v4.2-C2 common versus context-varying odds ratio','',
        '**RETROSPECTIVE / DESCRIPTIVE. H/F kept separate; no vault access or autonomous-loop activation.**','',
        'The comparison conditions on each held-out folio × ending stratum’s fixed sh/ch counts and total qok count. It predicts the allocation of qok across sh/ch, not the unconditional frequency of qok. No held-out folio baseline is fitted.','',
        'Both models use the same normal-prior penalty on a shared log OR (SD 2.5). The varying model adds context deviations (SD 1), learned only on training folds. An unseen context uses the training shared effect. Recto/verso and all panels of a numbered folio stay together; all f85/f86 material is one Rosettes foldout group.','',
        'Positive Δ means the varying model predicted better. Primary score is held-out conditional log-likelihood, normalized by eligible origins. All models are scored without their training penalty.','',
        '| Reading | Common LL | Varying LL | Δ LL, nats | Δ nats/origin [conditional score-bootstrap interval] |','|---|---:|---:|---:|---|']
    for co in ('H','F'):
        p=data['results'][co]['primary'];lo,hi=p['score_bootstrap']['CI95_nats_per_origin']
        lines.append(f"| {co} | {p['common_LL']:.4f} | {p['varying_LL']:.4f} | {p['delta_LL_nats']:+.4f} | {p['delta_nats_per_origin']:+.7f} [{lo:+.7f}, {hi:+.7f}] |")
    lines+=['','The 4,999-draw paired physical-group bootstrap conditions on the fitted training sets and chosen primary partition. It omits training-refit variability; it is not an inferential model-selection test.','',
        '## Fixed partition sensitivities','','| Reading | Partition | Δ nats/origin |','|---|---|---:|']
    for co in ('H','F'):
        for row in data['results'][co]['partition_sensitivities']:lines.append(f"| {co} | {row['partition_seed']} | {row['delta_nats_per_origin']:+.7f} |")
    lines+=['','## Fixed simulation controls at observed margins','','| Reading | Scenario | Varying wins/N | Mean Δ nats/origin |','|---|---|---:|---:|']
    for row in controls['summary']:lines.append(f"| {row['reading']} | {row['scenario']} | {row['varying_wins']}/{row['n']} | {row['mean_delta_nats_per_origin']:+.7f} |")
    lines+=['','## Context contributions in the primary partition','','| Context | H Δ nats/origin | F Δ nats/origin |','|---|---:|---:|']
    for context in CONTEXTS:
        h,f=[data['results'][co]['context_contributions'][context]['delta_nats_per_origin'] for co in ('H','F')]
        lines.append(f"| {context} | {h:+.7f} | {f:+.7f} |")
    lines+=['','## Limits and provenance','',
        '- This is a comparison of these two fixed penalized predictors, not proof of constant strength, a single mechanism, grammar or sound values. No equivalence margin or “scale artifact likely” classification rule was supplied/frozen.',
        '- The main 5-fold partition was fixed before fitting. Four additional fixed partitions are sensitivities, not extra independent replications; none replaces the primary.',
        '- Sparse contexts may provide little information, and an entirely held-out context cannot teach its own deviation. In particular Rosettes has only one conservative physical foldout group.',
        '- Controls preserve the observed qok totals. They test this conditional prediction problem and do not validate an unconditional generator of section frequencies.',
        '- All saved strata, failed controls and partition outcomes are retained. H/F are alternate readings, not independent datasets.',
        '- Original v4.2-C results and source text were not changed. This run uses only saved count tables; no raw EVT, images, ratings or vault subsets were read.','']
    (R/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    seal('report_written',['REPORT.md'])

if __name__=='__main__':{'qualify':qualify,'controls':controls,'run':run}[sys.argv[1]]()
