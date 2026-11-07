from common import *
import numpy as np
from src.metrics import measure
from src.tokenize import tokenize_line
from slots_adapter import decompose
BASE=['h0','h1','h2','zipf_slope','zipf_r2','word_hapax_ratio','word_length_mean','word_length_variance','word_length_skewness','word_length_excess_kurtosis','mi_glyph_line_word_edge','mi_glyph_word_edge','consecutive_identical_rate','consecutive_edit1_rate']
def raw_features(pg):
    rows=[{**r,'is_para_start':None} for r in pg['rows']];words=[w for r in rows for w in r['text_eva'].split()];clusters=json.loads((R/'phase3.json').read_text())['clusters']
    if words:
        m,_=measure(rows,'T1',clusters,None);scalar=[m.get(k) for k in BASE]
        for tok in ['T2','T3']:
            mm,_=measure(rows,tok,clusters,None);scalar.extend(mm.get(k) for k in ['h0','h1','h2'])
    else:scalar=[None]*20
    missing=[float(v is None or not math.isfinite(v)) for v in scalar];scalar=[0. if missing[i] else float(v) for i,v in enumerate(scalar)]+missing
    grams=[]
    for n in [1,2,3]:grams.append(dict(Counter(r['text_eva'][i:i+n] for r in rows for i in range(max(0,len(r['text_eva'])-n+1)))))
    aff=[]
    for direction in ['prefix','suffix']:
        for n in [1,2,3]:aff.append(dict(Counter((w[:n] if direction=='prefix' else w[-n:]) for w in words if len(w)>=n)))
    lengths=[0]*25
    for w in words:lengths[min(25,len(w))-1]+=1
    kinds=['REGULAR','SEPARABLE','UNSTRUCTURED','UNREADABLE'];tc=Counter();types=Counter();occ=[0]*12;segments=0
    for w,count in Counter(words).items():
        kind,parts=decompose(w);tc[kind]+=count;types[kind]+=1
        for slots in parts:
            segments+=count
            for i,value in enumerate(slots):occ[i]+=count*bool(value)
    grammar=[tc[k]/max(1,len(words)) for k in kinds]+[types[k]/max(1,len(set(words))) for k in kinds]+[v/max(1,segments) for v in occ]
    return dict(page=pg['page'],leaf=pg['leaf'],scalar=scalar,grams=grams,aff=aff,lengths=lengths,grammar=grammar)
def vocabulary(raws,key):
    count=3 if key=='grams' else 6
    return [sorted({v for r in raws for v in r[key][i]}) for i in range(count)]
def frequency(counts,vocab):
    lookup=set(vocab);xs=np.array([counts.get(x,0) for x in vocab]+[sum(v for k,v in counts.items() if k not in lookup)],dtype=float)+.5
    return np.sqrt(xs/xs.sum())
def matrix(raws,vs):
    blocks=[[],[],[],[],[]]
    for r in raws:
        blocks[0].append(r['scalar']);blocks[1].append(np.concatenate([frequency(r['grams'][i],v) for i,v in enumerate(vs['grams'])]))
        lens=np.array(r['lengths'],dtype=float)+.5;blocks[2].append(np.sqrt(lens/lens.sum()))
        blocks[3].append(np.concatenate([frequency(r['aff'][i],v) for i,v in enumerate(vs['aff'])]));blocks[4].append(r['grammar'])
    return [np.array(b,dtype=float) for b in blocks]
def fit_basis(raws):
    vs={key:vocabulary(raws,key) for key in ['grams','aff']};bs=matrix(raws,vs);means=[b.mean(0) for b in bs];sd=[np.where(b.std(0)==0,1,b.std(0)) for b in bs]
    x=np.concatenate([(b-m)/s/math.sqrt(b.shape[1]) for b,m,s in zip(bs,means,sd)],axis=1);center=x.mean(0);x=x-center
    val,vec=np.linalg.eigh(x@x.T);order=np.argsort(val)[::-1];rank=int(np.sum(val>np.finfo(float).eps*max(x.shape)*max(1.,float(val[order[0]]))));q=min(20,len(raws)-2,x.shape[1],rank);assert q>0,'NO_FEATURE_VARIATION';val=val[order[:q]];axes=x.T@vec[:,order[:q]]/np.sqrt(np.maximum(val,1e-14))
    z=x@axes;d=x.shape[1]-q;res=np.maximum(0,np.sum(x*x,1)-np.sum(z*z,1));variance=max(float(res.sum()/max(1,len(raws)*d)),.001)
    return dict(vocab=vs,means=means,sd=sd,center=center,axes=axes,dimension=x.shape[1],q=q,residual_variance=variance,retained_variance=float(np.sum(z*z)/max(1e-15,np.sum(x*x))))
def transform(raws,basis):
    bs=matrix(raws,basis['vocab']);x=np.concatenate([(b-m)/s/math.sqrt(b.shape[1]) for b,m,s in zip(bs,basis['means'],basis['sd'])],axis=1)-basis['center'];z=x@basis['axes'];res=np.maximum(0,np.sum(x*x,1)-np.sum(z*z,1));d=basis['dimension']-basis['q'];v=basis['residual_variance'];tail=-.5*(d*math.log(2*math.pi*v)+res/v)
    return z,tail
