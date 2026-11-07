"""C2 descriptive runner. Unit arrays and ring geometry must be registered upstream.
No data acquisition, no reserved-file loader, no sound fitting. Gates fail closed.
"""
import collections,json,math
from pathlib import Path
OPEN={'f70v2','f70v1','f71r','f71v','f72r1','f72r2','f72r3','f72v3'}
RESERVED={'f72v2','f72v1','f73r','f73v'}

def opener(units):
    s=''.join(units)
    return next((p for p in ('ot','ok','qo','ch','sh','d') if s.startswith(p)),'other')

def feature(units,kind,width=1):
    if kind=='opener':return opener(units)
    if kind=='ending':return ''.join(units[-width:]) if len(units)>=width else None
    raise ValueError('unfrozen feature kind')

def share(rows,f,value):
    # Ordered pairs; denominator excludes no unknowns silently: missing listed in coverage.
    groups=collections.defaultdict(list)
    for r in rows:groups[(r['section'],r['folio'],r['ring'])].append(f(r['units']))
    n=sum(len(v)*(len(v)-1) for v in groups.values())
    hit=sum(sum(x==value for x in v)*(sum(x==value for x in v)-1) for v in groups.values())
    return {'numerator':hit,'denominator':n,'probability':hit/n if n else None}

def cross_ring(rows,f,value):
    # Same section, different registered rings. Exact formula avoids materialising pairs.
    section=collections.defaultdict(list)
    for r in rows:section[r['section']].append(r)
    numerator=denominator=0
    for rr in section.values():
        n=len(rr);c=sum(f(r['units'])==value for r in rr)
        within=share(rr,f,value);denominator+=n*(n-1)-within['denominator'];numerator+=c*(c-1)-within['numerator']
    return {'numerator':numerator,'denominator':denominator,'probability':numerator/denominator if denominator else None}

def baseline(rows,f,value):
    n=len(rows);c=sum(f(r['units'])==value for r in rows)
    return {'numerator':c*(c-1),'denominator':n*(n-1),'probability':c*(c-1)/(n*(n-1)) if n>=2 else None}

def compute(rows,feature_plan):
    ids=[(r['id'],r['reading']) for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate physical label/reading')
    if any(r.get('folio') in RESERVED for r in rows):raise ValueError('reserved material forbidden')
    if any(r['set']=='zodiac' and r['folio'] not in OPEN for r in rows):raise ValueError('unregistered open sign')
    result={}
    for reading in ('H','F'):
        raw=[r for r in rows if r['reading']==reading]
        valid=[r for r in raw if r.get('units') and all(isinstance(x,str) and x for x in r['units'])]
        z=[r for r in valid if r['set']=='zodiac'];o=[r for r in valid if r['set'] in ('star','plant-jar','rosette')];para=[r for r in valid if r['set']=='paragraph']
        metrics=[]
        for p in feature_plan:
            f=lambda u,p=p:feature(u,p['kind'],p.get('width',1))
            values=sorted({f(r['units']) for r in valid}-{None})
            for value in values:
                within=share(z,f,value);other=baseline(o,f,value)
                a=within['probability'];b=other['probability'];ratio=a/b if a is not None and b is not None and b>0 else None
                metrics.append({'feature':p,'value':value,'within_ring':within,'different_ring_same_section':cross_ring(z,f,value),'nonzodiac_pair_baseline':other,'constancy_ratio':ratio,'shares':{name:{'n':len(rr),'count':sum(f(r['units'])==value for r in rr)} for name,rr in [('zodiac',z),('other_labels',o),('paragraph',para)]+[(s,[r for r in o if r['set']==s]) for s in ('star','plant-jar','rosette')]}})
        # Candidates require an actual fixed string. Other is a residual class, never a removable marker.
        def select(kind):
            q=[m for m in metrics if m['feature']['kind']==kind and m['constancy_ratio'] is not None and m['value']!='other']
            q.sort(key=lambda m:(-m['constancy_ratio'],m['value'],m['feature'].get('width',0)))
            return q[0] if q and q[0]['constancy_ratio']>2 else None
        result[reading]={'coverage':{'raw':len(raw),'readable':len(valid),'excluded_unknown_or_empty':len(raw)-len(valid),'zodiac':len(z),'other':len(o)},'metrics':metrics,'S_star':select('ending'),'M_star':select('opener')}
    return {'status':'DESCRIPTIVE_ONLY','readings':result,'marker_admission':'requires both readings, same frozen removal operation; no cross-reading pooling or replacement reading allowed'}

def run(root,input_path,plan_path):
    root=Path(root)
    # Examine gates BEFORE opening input data.
    lists=json.loads((root/'LISTS.json').read_text())
    qual=json.loads((root/'HARNESS/QUALIFICATION.json').read_text())
    budget=json.loads((root/'BUDGET.json').read_text())
    if lists['status']!='FROZEN' or not lists.get('assembly_complete'):raise RuntimeError('C1 not frozen; data remain unopened')
    if qual['status']!='QUALIFIED_FOR_REAL_KEYS':raise RuntimeError('Part A not qualified; data remain unopened')
    if budget['status']!='ALLOCATED':raise RuntimeError('joint budget not allocated; data remain unopened')
    rows=json.loads(Path(input_path).read_text());plan=json.loads(Path(plan_path).read_text())
    return compute(rows,plan)
