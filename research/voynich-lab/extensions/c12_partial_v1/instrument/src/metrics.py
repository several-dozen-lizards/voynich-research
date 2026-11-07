"""Descriptive plug-in measurements; no hypothesis test or learned model.

Token entropies never cross locus boundaries. Glyph MI excludes spaces; within-line
first/interior/last/both word and within-word first/interior/last/single positions.
Null paragraph starts are excluded, never recoded as false. All logs are base 2
except Zipf's natural-log regression (slope is base invariant).
"""
import math
from collections import Counter
from src.parse_ivtff import edit_distance
from src.tokenize import tokenize_line

def entropy(counts):
    total=sum(counts.values())
    return -sum((n/total)*math.log2(n/total) for n in counts.values()) if total else None

def conditional(sequences,order):
    joint,contexts=Counter(),Counter()
    for seq in sequences:
        for i in range(order,len(seq)):
            context=tuple(seq[i-order:i]);joint[context+(seq[i],)]+=1;contexts[context]+=1
    if not joint:
        return None,0
    return entropy(joint)-entropy(contexts),sum(joint.values())

def mi(counts):
    if not counts:
        return None
    a,b=Counter(),Counter()
    for (x,y),n in counts.items():
        a[x]+=n;b[y]+=n
    return entropy(a)+entropy(b)-entropy(counts)

def glyph_mi(rows):
    line,paragraph,wordpos=Counter(),Counter(),Counter()
    for r in rows:
        words=r['text_eva'].split()
        for j,w in enumerate(words):
            edge='both' if len(words)==1 else 'first' if j==0 else 'last' if j==len(words)-1 else 'interior'
            for i,c in enumerate(w):
                pos='single' if len(w)==1 else 'first' if i==0 else 'last' if i==len(w)-1 else 'interior'
                line[c,edge]+=1;wordpos[c,pos]+=1
                if r.get('is_para_start') is not None:
                    paragraph[c,bool(r['is_para_start'])]+=1
    return dict(mi_glyph_line_word_edge=mi(line),mi_glyph_paragraph_start=mi(paragraph),
                mi_glyph_word_edge=mi(wordpos),paragraph_MI_glyph_support=sum(paragraph.values()))

def measure(rows,scheme,clusters,merges):
    seqs=[tokenize_line(r['text_eva'],scheme,clusters,merges) for r in rows]
    counts=Counter(t for s in seqs for t in s)
    n=sum(counts.values());v=len(counts)
    h0=entropy(counts);h1,s1=conditional(seqs,1);h2,s2=conditional(seqs,2)
    ranks=list(range(1,v+1));freqs=sorted(counts.values(),reverse=True)
    if v>1:
        x=[math.log(i) for i in ranks];y=[math.log(f) for f in freqs]
        xm=sum(x)/v;ym=sum(y)/v
        slope=sum((a-xm)*(b-ym) for a,b in zip(x,y))/sum((a-xm)**2 for a in x)
        residual=sum((b-(ym+slope*(a-xm)))**2 for a,b in zip(x,y))
        tss=sum((b-ym)**2 for b in y)
        r2=1-residual/tss if tss else None
    else:
        slope=r2=None
    words=[w for r in rows for w in r['text_eva'].split()]
    lens=[len(w) for w in words];mean=sum(lens)/len(lens)
    variance=sum((x-mean)**2 for x in lens)/len(lens)
    skew=sum((x-mean)**3 for x in lens)/len(lens)/variance**1.5 if variance else None
    kurt=sum((x-mean)**4 for x in lens)/len(lens)/variance**2-3 if variance else None
    identical=near=transitions=0
    for r in rows:
        ws=r['text_eva'].split()
        for a,b in zip(ws,ws[1:]):
            transitions+=1
            identical+=a==b
            near+=abs(len(a)-len(b))<=1 and edit_distance(a,b)==1
    growth=[];seen=set();total=0
    points={max(1,round(n**(i/19))) for i in range(20)}|{n}
    for s in seqs:
        for t in s:
            seen.add(t);total+=1
            if total in points:
                growth.append(dict(tokens=total,types=len(seen)))
    types=Counter(words)
    result=dict(loci=len(rows),pages=len({r['folio'] for r in rows}),words=len(words),
        characters=sum(lens),alphabet_size=len(set(''.join(words))),tokens=n,types=v,
        h0=h0,h1=h1,h2=h2,h1_support=s1,h2_support=s2,
        alphabet_hartley=math.log2(v) if v else None,
        h2_normalized=h2/math.log2(v) if v>1 and h2 is not None else None,
        zipf_slope=slope,zipf_r2=r2,hapax_ratio=sum(c==1 for c in counts.values())/v if v else None,
        word_hapax_ratio=sum(c==1 for c in types.values())/len(types),
        word_length_mean=mean,word_length_variance=variance,word_length_skewness=skew,
        word_length_excess_kurtosis=kurt,word_transition_support=transitions,
        consecutive_identical_rate=identical/transitions if transitions else None,
        consecutive_edit1_rate=near/transitions if transitions else None,
        **glyph_mi(rows))
    return result,dict(growth=growth,word_length_distribution=dict(sorted(Counter(lens).items())))
