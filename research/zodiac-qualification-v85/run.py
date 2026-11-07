import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import numpy as np, json, hashlib, itertools, time
from pathlib import Path
P=Path(__file__).resolve().parent
SIGNS='Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces'.split()
SEX=['M7 F2 M6 F7 M8','M7 F8 M15','F6 M11 F6 M4 F3','M2 F5 M3 F2 M11 F4 M3','M5 F2 M6 F10 M7','F7 M5 F8 M10','M5 F5 M11 F7 F2','M6 F7 M4 F5 M8','M2 F3 M7 F12 M6','M11 F8 M11','M5 F7 M6 F7 M5','M10 F2 M3 F5 M10']
LIGHT=['d3 s5 d8 b4 s4 b5 s1','d3 L7 d2 b8 v5 b3 b2','v5 b2 d3 b5 v2 b6 d7','d7 b5 d2 L4 s2 b8 s2','b7 d3 s6 v5 b9','d5 L4 v2 b6 v4 s7 v2','b5 d5 b8 d3 b7 L2','d3 L5 v6 L6 s2 L5 d3','b9 d3 b7 s4 d7','d7 b3 s5 b4 d2 L4 b5','s4 b5 d5 b8 v3 L5','d7 b4 v6 L3 d10']
def expand(s):
    a=[v[0] for v in s.split() for _ in range(int(v[1:]))]
    assert len(a)==30
    return a
TABLES={sign:{'457_runs':a,'458_runs':b,'457_degrees':expand(a),'458_degrees':expand(b)} for sign,a,b in zip(SIGNS,SEX,LIGHT)}
# Synthetic slots only; no actual figure features or label readings are loaded.
SHAPES=[[[10,5],[10,5]],[[10,5],[10,5]],[[16,9,5]],[[12,11,7]]]
BLOCKS=[]; PANELS=[]; signpanels=[]; cursor=0
for shape in SHAPES:
    sp=[]
    for panel in shape:
        pb=[]
        for n in panel:
            ix=np.arange(cursor,cursor+n); cursor+=n; BLOCKS.append(ix); pb.append(ix)
        sp.append(pb); PANELS.append(pb)
    signpanels.append(sp)
assert cursor==120
def templates():
    out=[]; keys=[]
    for inward,cw,extra_first,extra_reverse,aries_reverse,taurus_reverse in itertools.product([0,1],repeat=6):
        orders=[]
        for si,panels in enumerate(signpanels):
            panels=panels[::-1] if (si==0 and aries_reverse) or (si==1 and taurus_reverse) else panels
            seq=[]
            for pb in panels:
                bands=pb[:2] if si==2 else pb
                bands=bands if inward else bands[::-1]
                q=np.concatenate([b if cw else b[::-1] for b in bands])
                if si==2:
                    e=pb[2][::-1] if extra_reverse else pb[2]
                    q=np.r_[e,q] if extra_first else np.r_[q,e]
                seq.extend(q)
            orders.append(np.array(seq))
        for phase in range(30):
            for table,subset in [('457','F')]+[('458',''.join(c for j,c in enumerate('L d s v'.split()) if bits>>j&1)) for bits in range(1,16)]:
                # b excluded to choose one of each complementary binary pair.
                x=np.zeros(120,dtype=np.int8)
                for si,order in enumerate(orders):
                    cats=TABLES[SIGNS[si]][table+'_degrees']
                    x[order]=[int(cats[(i+phase)%30] in subset) for i in range(30)]
                out.append(x); keys.append([inward,cw,extra_first,extra_reverse,aries_reverse,taurus_reverse,phase,table,subset])
    a=np.array(out); unique,idx=np.unique(a,axis=0,return_index=True)
    return unique,[keys[i] for i in idx]
def center(a):
    a=a.astype(np.float32).copy()
    for b in BLOCKS: a[...,b]-=a[...,b].mean(axis=-1,keepdims=True)
    return a
def score_engine(X,y,rng):
    # Rotate complete value+missingness sequences together; unknown is not zero.
    Y=np.tile(y,(200,1))
    for j in range(1,200):
        for b in BLOCKS: Y[j,b]=np.roll(y[b],rng.integers(len(b)))
    scores=np.zeros(200); winners=np.zeros(200,dtype=int)
    if np.all(np.isfinite(y)):
        xx=center(X); yy=center(Y)
        den=np.sqrt((xx*xx).sum(axis=1)[:,None]*(yy*yy).sum(axis=1)[None,:])
        s=np.divide(np.abs(xx@yy.T),den,out=np.zeros_like(den),where=den>0)
        winners=np.argmax(s,axis=0); scores=s[winners,np.arange(200)]
        p=(1+int(np.count_nonzero(scores[1:]>=scores[0]-1e-7)))/200
        return dict(score=float(scores[0]),p_raw=p,p_two_features=min(1,2*p),winner=int(winners[0]))
    # Mask-specific template centering is required for each permutation.
    for j,v in enumerate(Y):
        mask=np.isfinite(v); xx=X.astype(np.float32).copy(); yy=np.nan_to_num(v).astype(np.float32)
        for b in BLOCKS:
            obs=b[mask[b]]
            if len(obs):
                xx[:,obs]-=xx[:,obs].mean(axis=1,keepdims=True); yy[obs]-=yy[obs].mean()
        xx[:,~mask]=0; yy[~mask]=0
        den=np.sqrt((xx*xx).sum(axis=1)*(yy*yy).sum())
        s=np.divide(np.abs(xx@yy),den,out=np.zeros(len(xx),dtype=np.float32),where=den>0)
        winners[j]=np.argmax(s); scores[j]=s[winners[j]]
    p=(1+int(np.count_nonzero(scores[1:]>=scores[0]-1e-7)))/200
    return dict(score=float(scores[0]),p_raw=p,p_two_features=min(1,2*p),winner=int(winners[0]))
REGIMES=['iid','ring_rates','clustered','common_layout','structured_missing','clean_signal','noisy_masked_signal']
def make_y(regime,rng,X):
    y=np.zeros(120,dtype=float)
    if regime in ['clean_signal','noisy_masked_signal']:
        k=int(rng.integers(len(X))); y=X[k].astype(float)
        if regime=='noisy_masked_signal':
            flip=rng.random(120)<.10; y[flip]=1-y[flip]; y[rng.random(120)<.15]=np.nan
        return y,k
    for b in BLOCKS:
        n=len(b)
        if regime=='iid': vals=rng.binomial(1,.5,n)
        elif regime=='ring_rates': vals=rng.binomial(1,rng.choice([.1,.3,.7,.9]),n)
        elif regime in ['clustered','structured_missing']:
            vals=np.zeros(n); vals[0]=rng.integers(2)
            for i in range(1,n): vals[i]=1-vals[i-1] if rng.random()<.15 else vals[i-1]
            vals=np.roll(vals,int(rng.integers(n)))
        elif regime=='common_layout':
            # Aligned image-top nuisance unrelated to historical table.
            vals=(np.arange(n)<n/2).astype(float); flip=rng.random(n)<.1; vals[flip]=1-vals[flip]
        y[b]=vals
        if regime=='structured_missing': y[b[:max(1,n//4)]]=np.nan
    return y,None
def dump(name,obj): (P/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
if __name__=='__main__':
    import sys
    if sys.argv[1]=='freeze':
        dump('TABLES.json',TABLES)
        dump('PROTOCOL.json',{'scope':'Synthetic qualification only. No Voynich feature values or held-out sign scores.', 'source':'Wright 1934 English extract, PDF63-64 / printed62-63, sections457-458; one textual witness, two visual readbacks by same agent.', 'transcription':'Consecutive run lengths. Star=F in457; unstarred=M. In458 normalize dark/shadowed glyph to s and luminous to L. Adjacent identical runs preserved; Aries third458 run d8 confirmed enlarged. All24 rows sum30.', 'geometry':'Aries/Taurus10+5 per panel; Gemini16+9+5 extra; Cancer12+11+7. Pisces29 and uncertain Leo excluded. Six binary traversal alternatives and common30 phases; no per-sign fitting.', 'search':'All1920 traversals/phases x16 templates (457 binary;458 fifteen nontrivial binary partitions up to complement). Absolute within-panel/ring centered correlation. Exact duplicate template rows deduplicated. Search maximum recomputed in every null.', 'null':'199 independent within-ring cyclic shifts; rotate missingness with values. Block means and norms recomputed on observed slots. Monte Carlo p=(1+#null>=observed)/200; conservative tie tolerance1e-7. Bonferroni2 reserves garment/enclosure feature family. Pigment unavailable; labels not scored.', 'qualification':'40 replicates per regime; each negative <=4/40 flags at adjustedp<=.05; clean >=36/40; noisy10%flip15%missing >=32/40. ALL gates required. Report Wilson intervals; no tuning/retries within v85.', 'regimes':REGIMES, 'seed':'850000+1000*regime_index+replicate; independent permutation seed seed+500000', 'confirmation':'Qualification alone does not authorize manuscript scoring. Future development selects one global rule, freezes it, and predicts whole held-out signs without refitting. Current held-out signs untouched. No mapping of table sex to figure sex asserted.', 'limitations':'Same-agent source transcription, not independent witness; synthetic sample geometry only, not empirical ambiguity masks. Two features Bonferroni protected. Null assumes within-ring rotational exchangeability; shared layout nuisance explicitly challenges it.'})
        dump('SEEDS.json',{r:[850000+1000*i+j for j in range(40)] for i,r in enumerate(REGIMES)})
        dump('FREEZE.json',{'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['run.py','TABLES.json','PROTOCOL.json','SEEDS.json']}})
        print('Frozen; no simulation executed.')
    elif sys.argv[1]=='run':
        f=json.loads((P/'FREEZE.json').read_text())
        assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in f['sha256'].items())
        X,keys=templates(); dump('SEARCH.json',{'raw':30720,'unique':len(X),'key_fields':['inward','cw','extra_first','extra_reverse','aries_reverse','taurus_reverse','phase','table','subset'],'keys':keys})
        print('templates',len(X),flush=True)
        with (P/'replicates.jsonl').open('x',encoding='utf-8') as out:
            for ri,r in enumerate(REGIMES):
                for j in range(40):
                    seed=850000+1000*ri+j; y,k=make_y(r,np.random.default_rng(seed),X)
                    result=score_engine(X,y,np.random.default_rng(seed+500000))
                    result.update(regime=r,replicate=j,seed=seed,true_template=k,observed=int(np.isfinite(y).sum()),values=[None if not np.isfinite(v) else int(v) for v in y])
                    out.write(json.dumps(result)+'\n'); out.flush()
                print(r,'complete',flush=True)
