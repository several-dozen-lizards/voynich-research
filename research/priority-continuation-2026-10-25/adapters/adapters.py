"""B/C engineering adapters. NOT part of v7.2 qualification.
No corpus loader, vault executor, source-list selection or meaning inference.
"""
from fractions import Fraction
from itertools import permutations,product
from collections import defaultdict
import hashlib,json,re,math
RESERVED={'f72v1','f72v2','f73r','f73v'}
OPEN={'f70v2','f70v1','f71r','f71v','f72r1','f72r2','f72r3','f72v3'}
class NotAdmitted(ValueError):pass

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def tokenize_unique(word,units):
    # Author-declared glyph units; do not resolve multiple parses by greedy preference.
    if word is None:return None
    if not isinstance(word,str) or not word or not units or len(units)!=len(set(units)) or any(not isinstance(u,str) or not u for u in units):raise NotAdmitted('unit inventory/source word')
    paths={len(word):[()]}
    for i in range(len(word)-1,-1,-1):
        ps=[]
        for u in units:
            if word.startswith(u,i):
                ps.extend((u,)+p for p in paths.get(i+len(u),[]))
                if len(ps)>1:ps=ps[:2];break
        paths[i]=ps
    ps=paths[0]
    return list(ps[0]) if len(ps)==1 else None

def validate_records(records):
    if len({r['id'] for r in records})!=len(records):raise NotAdmitted('duplicate record')
    for r in records:
        if r.get('folio') in RESERVED or r.get('vault'):raise NotAdmitted('vault forbidden')
        if r.get('reading') not in ('H','F'):raise NotAdmitted('explicit H/F required')
    if len({r['reading'] for r in records})!=1:raise NotAdmitted('readings may not be pooled')

def decode_span(records,span,key,decode_word):
    validate_records(records)
    index={r['id']:r for r in records}
    # A span is an ordered list of [record ID, original zero-based word slot].
    locs=[tuple(x) for x in span]
    if not locs or len(set(locs))!=len(locs):raise NotAdmitted('empty or repeated span slots')
    vals=[]
    for rid,i in locs:
        if rid not in index or type(i) is not int or not 0<=i<len(index[rid]['words']):raise NotAdmitted('invalid span location')
        r=index[rid];vals.append(decode_word(r['words'][i],key,r.get('section','')))
    # Word boundaries survive; one unknown makes the entire object label undecodable.
    return None if any(v is None for v in vals) else ' '.join(vals)

def e2_spans(records,pairs,key,decode_word):
    validate_records(records);success=unknown=0;ids=set()
    for pair in pairs:
        if pair['id'] in ids:raise NotAdmitted('duplicate pair')
        ids.add(pair['id'])
        a=decode_span(records,pair['a'],key,decode_word);b=decode_span(records,pair['b'],key,decode_word)
        bad=a is None or b is None;unknown+=bad
        success+=not bad and (a==b or [a,b] in pair.get('relations',[]) or [b,a] in pair.get('relations',[]))
    return dict(kind='rate',success=success,n=len(pairs),value=success/len(pairs) if pairs else None,unknown=unknown,qualification='OUTSIDE_V7.2_E2_SCOPE')

def exact_number(x):
    # No float inputs, rounding, coercion of glyphs, or guessed Roman/additive notation.
    if type(x) is int:return Fraction(x)
    if isinstance(x,Fraction):return x
    if isinstance(x,str) and re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]+)?|[0-9]+/[1-9][0-9]*)',x):return Fraction(x)
    raise NotAdmitted('exact declared numeral required')

def numeric_check(values,kind,expected):
    if any(v is None for v in values):return False
    ns=[exact_number(v) for v in values]
    if kind=='sum':return sum(ns,Fraction())==exact_number(expected)
    if kind=='exact_sequence':return ns==[exact_number(v) for v in expected]
    raise NotAdmitted('undeclared numeric constraint')

def geometry_bands(rows):
    # Positions are preassigned from geometry. Missing labels stay at their figure slots.
    if not rows:raise NotAdmitted('empty figure inventory')
    validate_records(rows)
    if any(r['folio'] not in OPEN for r in rows):raise NotAdmitted('not an open zodiac page')
    if len({r['folio'] for r in rows})!=1:raise NotAdmitted('one geometry page per alignment')
    bands=defaultdict(list)
    for r in rows:
        if r.get('order_source')!='geometry-only':raise NotAdmitted('text-conditioned order forbidden')
        if type(r.get('position')) is not int or r['position']<0:raise NotAdmitted('cyclic position required')
        if 'label_span' not in r:raise NotAdmitted('missing label slot must be explicit None')
        if not isinstance(r.get('band'),str) or not r['band']:raise NotAdmitted('band identity')
        bands[r['band']].append(r)
    for b,rs in bands.items():
        if sorted(r['position'] for r in rs)!=list(range(len(rs))):raise NotAdmitted('duplicate/gapped geometry positions; represent missing figures explicitly')
        rs.sort(key=lambda r:r['position'])
    return dict(sorted(bands.items()))

def alignment_count(bands):return math.factorial(len(bands))*math.prod(2*len(v) for v in bands.values())

def alignments(rows,max_candidates):
    bands=geometry_bands(rows);count=alignment_count(bands)
    if type(max_candidates) is not int or count>max_candidates:raise NotAdmitted('full search exceeds declared computational budget; no truncation')
    # Full Cartesian search, independent rotations/directions of each band and every band order.
    # Symmetric aliases remain charged. Caller must freeze this freedom before data use.
    choices={b:[dict(rotation=r,direction=d,ids=[rs[(r+d*i)%len(rs)]['id'] for i in range(len(rs))]) for r in range(len(rs)) for d in (1,-1)] for b,rs in bands.items()}
    for order in permutations(bands):
        for selected in product(*(choices[b] for b in order)):
            yield dict(band_order=list(order),bands=[dict(band=b,**s) for b,s in zip(order,selected)],ids=[i for s in selected for i in s['ids']],charged_candidates=count)

def full_search(rows,score,max_candidates):
    best=None;count=0
    for candidate in alignments(rows,max_candidates):
        value=score(candidate['ids']);count+=1
        if not isinstance(value,(int,float)) or not math.isfinite(value):raise NotAdmitted('undefined candidate; no dropping search members')
        # Enumeration is deterministic; retain first witness on equal score.
        if best is None or value>best['value']:best=dict(value=value,witness=candidate)
    return dict(**best,evaluated=count,geometry_hash=digest(rows),qualification='ENGINEERING_ONLY')

def search_null(real_rows,null_rows,score_factory,max_candidates):
    def geometry_signature(rs):
        return sorted((r['id'],r['folio'],r['reading'],r['band'],r['position'],r['order_source']) for r in rs)
    signature=geometry_signature(real_rows)
    if any(geometry_signature(rs)!=signature for rs in null_rows):raise NotAdmitted('null must preserve exact geometry identities and positions')
    observed=full_search(real_rows,score_factory(real_rows),max_candidates)
    null=[full_search(rs,score_factory(rs),max_candidates) for rs in null_rows]
    if any(n['evaluated']!=observed['evaluated'] for n in null):raise NotAdmitted('null search-space mismatch')
    return dict(observed=observed,null=null,p=(1+sum(n['value']>=observed['value'] for n in null))/(len(null)+1) if null else None,status='ENGINEERING_ONLY_NOT_A_B_OR_C_RESULT')

def list_variant(packet):
    # C1 source audit owns real packets; this validates supplied contract only.
    required={'id','source','source_sha256','date_latest','eligible_by_1440','slots','normalization','variant_id','freeze_sha256'}
    if not required<=packet.keys():raise NotAdmitted('incomplete C1 packet')
    if type(packet['date_latest']) is not int or packet['date_latest']>1440 or packet['eligible_by_1440'] is not True:raise NotAdmitted('undated/late list not admitted')
    if not re.fullmatch('[a-f0-9]{64}',packet['source_sha256']):raise NotAdmitted('source hash')
    body={k:v for k,v in packet.items() if k!='freeze_sha256'}
    if digest(body)!=packet['freeze_sha256']:raise NotAdmitted('list changed after freeze')
    if not packet['slots'] or any(v is not None and (not isinstance(v,str) or not v) for v in packet['slots']):raise NotAdmitted('variant slots; preserve gaps as None')
    return tuple(packet['slots'])

def require_scientific_release(receipt):
    # Deliberately closed in this adapter version. Qualification must be a new owning attempt,
    # not a boolean supplied by a caller and not inherited from v7.2 E1/E3/E4.
    raise NotAdmitted('B/C scientific adapter qualification and budget release not implemented; vault closed')
