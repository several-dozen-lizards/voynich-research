"""Separate descriptive image qok-rate model. Real-data join stays locked."""
from pathlib import Path
from collections import defaultdict
import ast,hashlib,json,math,re,sys
from fractions import Fraction
import numpy as np
R=Path(__file__).resolve().parent
LABELS=['PL','VE','FG','CE','OT','NO']
def check(ok,why):
    if not ok:raise RuntimeError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tokenizer():
    protocol=json.loads((R/'PROTOCOL.json').read_text())
    path=next(p for p in protocol['sources'] if p.endswith('engine.py'))
    check(sha(path)==protocol['sources'][path],'Tokenizer source changed')
    tree=ast.parse(Path(path).read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='tokens')
    env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),path,'exec'),env)
    return env['tokens']
def count_line(text):
    words=tokenizer()(text)
    return dict(N=sum(w is not None for w in words),Q=sum(bool(w and w.startswith('qok')) for w in words),unknown_slots=sum(w is None for w in words))
def group(folio):
    m=re.fullmatch(r'f(\d+)[rv]\d*',folio);check(m is not None,'Bad folio id')
    return 'rosettes-foldout' if int(m[1]) in (85,86) else 'f'+m[1]
def mh(tables):
    a=np.asarray(tables,float).reshape((-1,4));n=a.sum(axis=1);a=a[n>0];n=n[n>0]
    if not len(a):return None
    r=float(np.sum(a[:,0]*a[:,3]/n));s=float(np.sum(a[:,1]*a[:,2]/n))
    return None if r==0 and s==0 else 'Infinity' if s==0 else r/s
def fit(rows,label,wrap=False,seed=4272600):
    strata=sorted({(r['hand'],r['section'],r['wrap_bin'] if wrap else '') for r in rows})
    groups=sorted({group(r['folio']) for r in rows});si={s:i for i,s in enumerate(strata)};gi={g:i for i,g in enumerate(groups)}
    cells=np.zeros((len(groups),len(strata),4),float)
    rates=defaultdict(lambda:[0,0,0])
    for row in rows:
        key=(row['hand'],row['section'],row['wrap_bin'] if wrap else '');target=row['label']==label
        cells[gi[group(row['folio'])],si[key],0 if target else 2]+=row['Q']
        cells[gi[group(row['folio'])],si[key],1 if target else 3]+=row['N']-row['Q']
        rates[row['label']][0]+=row['Q'];rates[row['label']][1]+=row['N'];rates[row['label']][2]+=row['unknown_slots']
    total=cells.sum(axis=0);OR=mh(total)
    overlap=int(np.sum((total[:,:2].sum(axis=1)>0)&(total[:,2:].sum(axis=1)>0))) if len(total) else 0
    out=dict(OR=OR,overlap_strata=overlap,physical_groups=len(groups),lines=len(rows),
        raw_rates={label:dict(qok=v[0],readable=v[1],unknown_slots=v[2],rate=v[0]/v[1] if v[1] else None) for label,v in rates.items()},
        tables={str(s):total[i].tolist() for i,s in enumerate(strata)},CI95=None,undefined_draws=0)
    if not groups:return out|dict(status='NOT ESTIMABLE: no eligible lines',draws=0)
    rng=np.random.default_rng(seed);indices=rng.integers(len(groups),size=(4999,len(groups)));draws=[]
    # Reaggregate hand x section cells for each resample; this is not a
    # bootstrap of fixed per-folio MH contributions when strata cross folios.
    flat=cells.reshape((len(groups),-1))
    for start in range(0,4999,128):
        weights=np.array([np.bincount(ix,minlength=len(groups)) for ix in indices[start:start+128]])
        aggregated=(weights@flat).reshape((-1,len(strata),4))
        draws.extend(mh(table) for table in aggregated)
    invalid=sum(v is None for v in draws);out.update(draws=4999,seed=seed,undefined_draws=invalid,
        infinite_draws=sum(v=='Infinity' for v in draws),zero_draws=sum(v==0 for v in draws))
    if not invalid:
        ordered=sorted(math.inf if v=='Infinity' else v for v in draws)
        ci=[ordered[math.ceil(p*len(ordered))-1] for p in (.025,.975)]
        out['CI95']=['Infinity' if v==math.inf else v for v in ci]
    return out|dict(status='DESCRIPTIVE' if OR is not None else 'NOT ESTIMABLE: zero/zero adjusted ratio')

def qualify():
    tests=[('shol.qok.foo',dict(N=3,Q=1,unknown_slots=0)),('qok?..?qok.qok',dict(N=1,Q=1,unknown_slots=2)),
        ('qok,chey=qokar-',dict(N=3,Q=2,unknown_slots=0)),('qok!aiin.???',dict(N=1,Q=1,unknown_slots=1))]
    for text,expected in tests:check(count_line(text)==expected,'Tokenizer counter fixture failed')
    rng=np.random.default_rng(427260);nchecks=0
    for _ in range(200):
        tables=rng.integers(0,7,size=(4,4));rr=Fraction(0);ss=Fraction(0)
        for a,b,c,d in tables.tolist():
            n=a+b+c+d
            if n:rr+=Fraction(a*d,n);ss+=Fraction(b*c,n)
        expected=None if not rr and not ss else 'Infinity' if not ss else float(rr/ss);got=mh(tables)
        check(got==expected if expected is None or isinstance(expected,str) else math.isclose(got,expected,rel_tol=1e-12),'Rational label-MH oracle failed');nchecks+=1
    # Strong pooled section imbalance with exactly equal within-section rates.
    confounded=np.array([[1,9,9,81],[90,10,9,1]])
    check(math.isclose(mh(confounded),1.),'Section adjustment failed')
    check(mh([[2,8,0,0],[0,0,3,7]]) is None,'Nonoverlap falsely identified')
    record=dict(status='PASS_SYNTHETIC_ONLY',token_counter_cases=len(tests),rational_MH_cases=nchecks,
        section_confounding_and_nonoverlap_checks=True,real_ratings_read=False)
    (R/'QUALIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

def run():
    # Gate BEFORE opening the joined labels/counts file. No source-owner receipt
    # has been supplied in this session; this branch is intentionally blocked.
    receipt_path=R/'PREJOIN-TIMING-RECEIPT.json'
    check(receipt_path.exists(),'BLOCKED: source-owner pre-join timing receipt absent')
    receipt=json.loads(receipt_path.read_text())
    frozen=json.loads((R/'FREEZE.json').read_text())
    check(all(sha(R/n)==h for n,h in frozen['files'].items()),'Frozen endpoint artifact changed')
    check(receipt['protocol_sha256']==sha(R/'PROTOCOL.json') and receipt['no_relevant_join_before_protocol_freeze'] is True,'Timing/version not certified')
    check(receipt['implementation_sha256']==sha(R/'rate_model.py'),'Implementation version not certified')
    check(json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS_SYNTHETIC_ONLY','Qualify frozen implementation first')
    path=R/'JOINED-LINES.json';check(sha(path)==receipt['joined_lines_sha256'],'Unsealed joined export')
    rows=json.loads(path.read_text());seen=set();accepted=[];excluded=[]
    for row in rows:
        key=(row['reading'],row['line']);check(key not in seen,'Duplicate registered reading/locus');seen.add(key)
        check(row['reading'] in ('H','F'),'Unknown reading')
        check(row['folio'] not in ('f72v1','f72v2','f73r','f73v'),'Reserved zodiac prohibited')
        for field in ('N','Q','unknown_slots'):check(type(row[field]) is int and row[field]>=0,'Invalid word counts')
        check(row['Q']<=row['N'],'Numerator exceeds denominator')
        if not row['registered'] or not row['cohort_eligible']:
            excluded.append(dict(reading=row['reading'],line=row['line'],reason='pre-existing registration/cohort exclusion'));continue
        if row['label'] not in LABELS:
            excluded.append(dict(reading=row['reading'],line=row['line'],reason='unknown/abstained image label, not NO'));continue
        accepted.append(row)
    results={}
    for ri,co in enumerate(('H','F')):
        pl=[r for r in accepted if r['reading']==co and r['G2_pass']]
        six=[r for r in accepted if r['reading']==co and r['G6_pass']]
        results[co]=dict(PL_primary=fit(pl,'PL',False,4272600+1000*ri),
            PL_wrap_sensitivity=fit(pl,'PL',True,4272600+1000*ri+100),
            six_label_descriptive={label:fit(six,label,False,4272600+1000*ri+200+j) for j,label in enumerate(LABELS)})
    check(not (R/'RESULTS.json').exists(),'One-shot endpoint result already exists')
    (R/'RESULTS.json').write_text(json.dumps(dict(descriptive_only=True,readings=results,exclusions=excluded),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':{'qualify':qualify,'run':run}[sys.argv[1]]()
