"""Frozen retrospective Currier-B rare-word section-prediction retest."""
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
import json,hashlib,math,sys,re,gzip
import numpy as np
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'ab-insertion-v4'))
import analysis as old
CLASSES=['Astronomy/Astrology','Balneological','Botanical','Rose obverse','Starred paragraphs']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,x):
    data=json.dumps(x,ensure_ascii=False,indent=None if n.endswith('.gz') else 2,default=lambda v:v.item() if isinstance(v,np.generic) else str(v))+'\n'
    if n.endswith('.gz'):
        with gzip.open(ROOT/n,'wt',encoding='utf-8') as f:f.write(data)
    else:(ROOT/n).write_text(data,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fold(o):return int(hashlib.sha256(('voynich-topic-v8:'+str(o['folio'])).encode()).hexdigest(),16)%5
def units(w,group):return tuple(w) if group=='raw' else tuple(re.findall(r'c[kptf]h|ch|sh|.',w))
def replace(seq,pair):
    out=[];i=0
    while i<len(seq):
        if i+1<len(seq) and (seq[i],seq[i+1])==pair:out.append(seq[i]+seq[i+1]);i+=2
        else:out.append(seq[i]);i+=1
    return tuple(out)
def learn_bpe(common,group):
    words={w:units(w,group) for w in common};merges=[]
    for _ in range(30):
        cc=Counter()
        for w,seq in words.items():
            for pair in zip(seq,seq[1:]):cc[pair]+=common[w]
        if not cc:break
        best=min(cc,key=lambda p:(-cc[p],p));merges.append(best);words={w:replace(s,best) for w,s in words.items()}
    return merges,words
def segment(w,group,merges):
    seq=units(w,group)
    for pair in merges:seq=replace(seq,tuple(pair))
    return seq
@lru_cache(maxsize=500000)
def distance(a,b):
    # Myers bit-vector Levenshtein; used only for spelling, never topic labels.
    if not a:return len(b)
    masks={}
    for i,c in enumerate(a):masks[c]=masks.get(c,0)|(1<<i)
    pv=~0;mv=0;score=len(a);top=1<<(len(a)-1)
    for c in b:
        eq=masks.get(c,0);xv=eq|mv;xh=(((eq&pv)+pv)^pv)|eq;ph=mv|~(xh|pv);mh=pv&xh
        score+=bool(ph&top);score-=bool(mh&top);ph=(ph<<1)|1;mh<<=1;pv=mh|~(xv|ph);mv=ph&xv
    return score
class Topic:
    def __init__(self,rows,group,foldid):
        self.group=group;self.count=Counter(o['word'] for o in rows);self.common={w:n for w,n in self.count.items() if n>=5}
        self.merges,self.segments=learn_bpe(self.common,group);self.W=defaultdict(lambda:np.zeros(5));self.P=defaultdict(lambda:np.zeros(5));self.S=defaultdict(lambda:np.zeros(5));self.M=defaultdict(lambda:np.zeros(5));bg=np.ones(5)*.5
        for o in rows:
            c=CLASSES.index(o['section']);bg[c]+=1;self.S[o['scribe']][c]+=1;self.M[self.meta(o)][c]+=1
            if o['word'] in self.common:self.W[o['word']][c]+=1
        self.G=bg/bg.sum()
        for w,counts in self.W.items():
            for piece in self.segments[w]:self.P[piece]+=counts
        self.common_units={w:units(w,group) for w in self.common};self.pieces=sorted(self.P);self.pi={p:i for i,p in enumerate(self.pieces)}
        self.pc=np.array([self.P[p] for p in self.pieces]);bins=defaultdict(list)
        for i,p in enumerate(self.pieces):bins[(int(math.log2(self.pc[i].sum())),len(units(p,group)))].append(i)
        rng=np.random.default_rng(20261021+foldid);maps=[]
        for _ in range(199):
            arr=np.arange(len(self.pieces))
            for ix in bins.values():arr[ix]=rng.permutation(ix)
            maps.append(arr)
        self.maps=np.array(maps);self.movable=sum(len(ix) for ix in bins.values() if len(ix)>1)/len(self.pieces)
    def meta(self,o):return (o['scribe'],o['edge_start'],o['pfirst'],o['plast'])
    def prior(self,o):
        v=self.S.get(o['scribe'],np.zeros(5));p=(v+10*self.G)/(v.sum()+10)
        v=self.M.get(self.meta(o),np.zeros(5));return (v+100*p)/(v.sum()+100)
    def predict(self,o):
        w=o['word'];u=units(w,self.group);dists={x:distance(u,xx) for x,xx in self.common_units.items()};best=min(dists.values());neighbors=sorted(x for x,d in dists.items() if d==best)
        bg=self.prior(o);priors=np.array([self.G,bg]);den=sum(self.common[x] for x in neighbors)
        nn=sum(self.common[x]*(self.W[x][None,:]+10*priors)/(self.common[x]+10) for x in neighbors)/den
        seg=segment(w,self.group,self.merges);piece_predictions=[];null=[]
        for p in seg:
            if p in self.P:
                counts=self.P[p];piece_predictions.append((counts[None,:]+10*priors)/(counts.sum()+10))
                cc=self.pc[self.maps[:,self.pi[p]]];null.append((cc[:,None,:]+10*priors[None,:,:])/(cc.sum(axis=1)[:,None,None]+10))
            else:piece_predictions.append(priors);null.append(np.broadcast_to(priors,(199,2,5)))
        pp=np.mean(piece_predictions,axis=0);rr=np.mean(null,axis=0)
        probs={'G':self.G,'M':bg,'NG':nn[0],'N':nn[1],'PG':pp[0],'P':pp[1],'HG':.5*(nn[0]+pp[0]),'H':.5*(nn[1]+pp[1])}
        assert all(abs(p.sum()-1)<1e-10 and min(p)>0 for p in probs.values())
        return probs,rr,{'nearest_distance':best,'nearest_ties':neighbors,'pieces':seg}
    def receipt(self):
        return {'merges':self.merges,'common_training_words':self.common,'piece_class_counts':{p:self.P[p].tolist() for p in self.pieces},'word_class_counts':{w:self.W[w].tolist() for w in self.W},'global_prior':self.G.tolist(),'null_movable_piece_fraction':self.movable,'null_profile_mappings':self.maps.tolist()}
def summarize(rows):
    out={};comparisons={'PG_over_G':('G','PG'),'NG_over_G':('G','NG'),'P_over_M':('M','P'),'N_over_M':('M','N'),'P_over_N':('N','P'),'H_over_N':('N','H'),'HG_over_NG':('NG','HG')}
    masks={'primary_global_frequency_1_2':[o for o in rows if o['global_frequency']<=2],'training_frequency_below5':rows,'never_seen_training':[o for o in rows if o['training_frequency']==0]}
    for k,rr in masks.items():
        out[k]={'n':len(rr),'types':len({o['word'] for o in rr}),'folios':len({o['folio'] for o in rr}),'loss_bits':{m:float(np.mean([o['losses'][m] for o in rr])) for m in ('G','M','NG','N','PG','P','HG','H')},'gains':{}}
        for key,(a,b) in comparisons.items():out[k]['gains'][key]=old.bootstrap(rr,[o['losses'][a]-o['losses'][b] for o in rr])
        out[k]['sections']=dict(Counter(o['section'] for o in rr));out[k]['scribes']={s:{'n':len(ss),'H_over_N':old.bootstrap(ss,[o['losses']['N']-o['losses']['H'] for o in ss])} for s in sorted({o['scribe'] for o in rr}) if (ss:=[o for o in rr if o['scribe']==s])}
    return out
def main():
    assert distance(tuple('kitten'),tuple('sitting'))==3 and distance(tuple('ab'),tuple('ba'))==2
    prior={str(p.relative_to(BASE)):sha(p) for p in [BASE/'results.json']+list(BASE.glob('*-v[234567]/results.json'))}
    dump('topic-frozen-inputs.json',{'protocol_sha256':sha(ROOT/'PROTOCOL.txt'),'script_sha256':sha(Path(__file__)),'tokens_sha256':sha(BASE/'tokens.json'),'prior_numeric_sha256':prior,'classes':CLASSES,'mode':'Retrospective grouped retest of already examined archive; not exact Claude estimator reproduction.'})
    rows=[o for o in read(BASE/'tokens.json') if o['language']=='B'];freq=Counter(o['word'] for o in rows);results={}
    for grouping in ('raw','atomic'):
        pred=[];null_total=np.zeros((199,2));nprimary=0;foldinfo=[]
        for f in range(5):
            tr=[o for o in rows if fold(o)!=f];test=[o for o in rows if fold(o)==f];m=Topic(tr,grouping,f)
            assert not {o['folio'] for o in tr}&{o['folio'] for o in test}
            dump(f'topic-{grouping}-fold{f}.json.gz',m.receipt())
            ff={'fold':f,'train_tokens':len(tr),'test_tokens':len(test),'train_folios':sorted({o['folio'] for o in tr}),'test_folios':sorted({o['folio'] for o in test}),'common_types':len(m.common),'pieces':len(m.P),'null_movable_piece_fraction':m.movable}
            foldinfo.append(ff)
            cache={}
            for o in test:
                if m.count[o['word']]>=5:continue
                ck=(o['word'],m.meta(o))
                if ck not in cache:cache[ck]=m.predict(o)
                pp,rr,extra=cache[ck];y=CLASSES.index(o['section']);z={**o,'fold':f,'global_frequency':freq[o['word']],'training_frequency':m.count[o['word']],**extra,'probabilities':{k:p.tolist() for k,p in pp.items()},'losses':{k:float(-math.log2(p[y])) for k,p in pp.items()}}
                pred.append(z)
                if freq[o['word']]<=2:null_total+=-np.log2(rr[:,:,y]);nprimary+=1
            print('FOLD '+grouping+' '+json.dumps(ff),flush=True)
        summary=summarize(pred);null_mean=null_total/nprimary;nulls={}
        for j,model in enumerate(('PG','P')):
            truth=summary['primary_global_frequency_1_2']['loss_bits'][model];nulls[model]={'true_loss_bits':truth,'null_mean_loss_bits':null_mean[:,j].tolist(),'p':(1+sum(x<=truth+1e-12 for x in null_mean[:,j]))/200,'limit':'Profile permutation conditional on coarse frequency/unit-length bins; not a complete generator null.'}
        dump(f'topic-{grouping}-predictions.json.gz',pred);results[grouping]={'folds':foldinfo,'metrics':summary,'random_piece_diagnostic':nulls}
        print('RESULT '+grouping+' '+json.dumps(summary['primary_global_frequency_1_2']),flush=True)
    gates={g:{'incremental_mixture_gain':results[g]['metrics']['primary_global_frequency_1_2']['gains']['H_over_N']['bootstrap95_bits'][0]>0,'piece_specificity':results[g]['random_piece_diagnostic']['P']['p']<=.05} for g in ('raw','atomic')}
    dump('topic-results.json',{'date':'2026-10-21','results':results,'gates':gates,'incremental_piece_utility_established':all(all(x.values()) for x in gates.values()),'prior_numeric_unchanged':all(sha(BASE/p)==h for p,h in prior.items()),'scope':'Retrospective, same exposed archive; raw/atomic sensitivity, no independently reproduced Latin comparison.'})
if __name__=='__main__':main()
