"""Symmetric minimal-edit transcription sensitivity model; no inferred true text.

Reconstruct exact Phase 0 distances by dynamic-program traceback; ties choose
diagonal, then deletion, then insertion. Orientation is arbitrary, so insertion
and deletion counts are averaged over forward/reverse directions. Rates use
Phase 0's sum(max(line lengths)) denominator, not a probability of true error.
"""
from collections import Counter,defaultdict
from src.parse_ivtff import UNK

def alignment_ops(a,b):
    table=[list(range(len(b)+1))]
    for i,x in enumerate(a,1):
        row=[i]
        for j,y in enumerate(b,1):
            row.append(min(row[-1]+1,table[-1][j]+1,table[-1][j-1]+(x!=y)))
        table.append(row)
    i,j=len(a),len(b);ops=Counter()
    while i or j:
        if i and j and table[i][j]==table[i-1][j-1]+(a[i-1]!=b[j-1]):
            if a[i-1]!=b[j-1]:ops['substitution']+=1
            i-=1;j-=1
        elif i and table[i][j]==table[i-1][j]+1:
            ops['deletion']+=1;i-=1
        else:
            ops['insertion']+=1;j-=1
    return ops,table[-1][-1]

def estimate(rows,pairs):
    lookup={(r['line_id'],r['transcriber']):r['text_eva'] for r in rows}
    totals=Counter();by_pair=defaultdict(Counter)
    for p in pairs:
        if p['included']!='True':continue
        a=lookup[p['line_id'],p['transcriber_a']].replace(UNK,'\ue000')
        b=lookup[p['line_id'],p['transcriber_b']].replace(UNK,'\ue001')
        ops,distance=alignment_ops(a,b)
        assert distance==int(p['distance'])
        ops['denominator']=int(p['denominator']);ops['line_pairs']=1
        totals.update(ops);by_pair[p['transcriber_a'],p['transcriber_b']].update(ops)
    def rates(c):
        return dict(substitution=c['substitution']/c['denominator'],
            insertion=(c['insertion']+c['deletion'])/2/c['denominator'],
            deletion=(c['insertion']+c['deletion'])/2/c['denominator'])
    table=[dict(transcriber_a=a,transcriber_b=b,**c,**{'rate_'+k:v for k,v in rates(c).items()}) for (a,b),c in sorted(by_pair.items())]
    return dict(counts=dict(totals),rates=rates(totals)),table

def inject(text,rates,alphabet,rng):
    # Include one space class, mirroring the agreement metric's boundary edits.
    symbols=sorted(set(alphabet)|{' '});out=[];ops=Counter()
    s,i,d=(rates[k] for k in ['substitution','insertion','deletion'])
    for c in text:
        x=rng.random()
        if x<s:
            out.append(rng.choice([a for a in symbols if a!=c]));ops['substitution']+=1
        elif x<s+d:
            ops['deletion']+=1
        elif x<s+d+i:
            out.extend([rng.choice(symbols),c]);ops['insertion']+=1
        else:
            out.append(c)
    # Canonical whitespace is required by every tokenizer; normalization is logged.
    raw=''.join(out)
    return ' '.join(raw.split()),dict(ops),raw
