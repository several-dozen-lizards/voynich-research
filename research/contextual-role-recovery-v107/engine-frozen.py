from pathlib import Path
import json,hashlib,collections,random,warnings
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import cdist
R=Path(__file__).resolve().parent
def fs(e):
    c=e['context'];return [str(i)+':'+t for i,t in enumerate(c)]+['L:'+c[0]+'|'+c[1],'R:'+c[2]+'|'+c[3]]
def fit(rows):
    tr=[e for e in rows if e['split']=='train'];te=[e for e in rows if e['split']=='test']
    vocab={x:i for i,x in enumerate(sorted({f for e in tr for f in fs(e)}))}
    def vec(rs):
        x=np.zeros((len(rs),len(vocab)))
        for i,e in enumerate(rs):
            for f in fs(e):
                if f in vocab:x[i,vocab[f]]=1
        return x/np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1e-12)
    a,b=vec(tr),vec(te);choices=[]
    if len(a)<5 or not vocab:return dict(k=1,choices=[],assignments=[dict(id=e['id'],cluster=0,split=e['split']) for e in rows])
    dist=cdist(a,a)
    for k in [2,3,4]:
        best=None
        for seed in range(4601,4611):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');cent,lab=kmeans2(a,k,iter=60,minit='++',seed=seed)
            loss=float(np.sum((a-cent[lab])**2))
            if len(set(lab))<k:continue
            if best is None or loss<best[0]:best=(loss,cent,lab)
        if best is None:continue
        loss,cent,lab=best;sil=[]
        for i in range(len(a)):
            own=np.where(lab==lab[i])[0];own=own[own!=i]
            if not len(own):sil.append(0);continue
            aa=float(np.mean(dist[i,own]));bb=min(float(np.mean(dist[i,lab==j])) for j in range(k) if j!=lab[i]);sil.append((bb-aa)/max(aa,bb,1e-12))
        choices.append(dict(k=k,silhouette=float(np.mean(sil)),loss=loss,cent=cent,lab=lab))
    best=max(choices,key=lambda c:(c['silhouette'],-c['k'])) if choices else None
    if best is None or best['silhouette']<.2:labs=np.zeros(len(tr),int);test=np.zeros(len(te),int);k=1
    else:k=best['k'];labs=best['lab'];test=np.argmin(cdist(b,best['cent']),axis=1) if len(b) else []
    return dict(k=k,choices=[{k:v for k,v in c.items() if k not in ['cent','lab']} for c in choices],assignments=[dict(id=e['id'],cluster=int(z),split=e['split']) for rs,ls in [(tr,labs),(te,test)] for e,z in zip(rs,ls)])
def ari(y,z):
    def pairs(c):return sum(v*(v-1)/2 for v in c.values())
    n=len(y);total=n*(n-1)/2
    if not total:return None
    a=pairs(collections.Counter(y));b=pairs(collections.Counter(z));ab=pairs(collections.Counter(zip(y,z)));expected=a*b/total;den=(a+b)/2-expected
    return (ab-expected)/den if den else 0.
def evaluate(fit,key,meta):
    tr=[a for a in fit['assignments'] if a['split']=='train' and key[a['id']]['role'] in ['day_period','temporal_relation']]
    te=[a for a in fit['assignments'] if a['split']=='test' and key[a['id']]['role'] in ['day_period','temporal_relation']]
    counts=collections.defaultdict(collections.Counter)
    for a in tr:counts[a['cluster']][key[a['id']]['role']]+=1
    mapping={k:c.most_common(1)[0][0] for k,c in counts.items()}
    y=[key[a['id']]['role'] for a in te];z=[a['cluster'] for a in te];pred=[mapping.get(i,'unknown') for i in z]
    n=collections.Counter(y);recall=sum(sum(a==v and b==v for a,b in zip(y,pred))/n[v] for v in n)/len(n) if n else None
    ar=ari(y,z);rng=random.Random(4602);null=[]
    for _ in range(199):yy=y.copy();rng.shuffle(yy);null.append(ari(yy,z))
    p=(1+sum(v>=ar for v in null if v is not None))/200 if ar is not None else None
    return dict(test_counts=dict(n),test_folios=len(set(meta[a['id']]['page'] for a in te)),macro_recall=recall,ARI=ar,label_permutation_p=p,label_permutation_ARI=null,mapping=mapping)
def main():
    freeze=json.loads((R/'FREEZE.json').read_text())
    for name,h in freeze.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
    rows=json.loads((R/'BLIND-INPUT.json').read_text());fits=[]
    for s in sorted(set(e['stratum'] for e in rows)):
        rs=[e for e in rows if e['stratum']==s];null=[dict(e,context=e['context'].copy()) for e in rs];rng=random.Random(4603)
        for p in set(e['page'] for e in null):
            ix=[i for i,e in enumerate(null) if e['page']==p]
            for j in range(4):
                vals=[null[i]['context'][j] for i in ix];rng.shuffle(vals)
                for i,v in zip(ix,vals):null[i]['context'][j]=v
        fits.append(dict(stratum=s,actual=fit(rs),context_null=fit(null)))
    p=R/'BLIND-ASSIGNMENTS.json';p.write_text(json.dumps(fits,indent=2),encoding='utf8')
    (R/'ASSIGNMENT-FREEZE.json').write_text(json.dumps({'BLIND-ASSIGNMENTS.json':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2),encoding='utf8')
    # First answer-key load occurs only after assignments are saved and hashed.
    key=json.loads((R/'ANSWER-KEY.json').read_text());meta={e['id']:e for e in rows};out=[]
    for f in fits:
        a=evaluate(f['actual'],key,meta);b=evaluate(f['context_null'],key,meta)
        support=len(a['test_counts'])==2 and min(a['test_counts'].values())>=20 and a['test_folios']>=5
        passed=support and f['actual']['k']==2 and a['macro_recall']>=.8 and a['ARI']>=.5 and a['label_permutation_p']<=.05 and b['macro_recall'] is not None and a['macro_recall']-b['macro_recall']>=.1
        out.append(dict(stratum=f['stratum'],k=f['actual']['k'],selection=f['actual']['choices'],status='pass' if passed else 'failed' if support else 'not_estimable',actual=a,context_null=b))
    result=dict(results=out,overall_pass=sum(x['status']=='pass' for x in out)>=2,Voynich='CLOSED pending qualification')
    (R/'BLIND-RESULTS.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps([{k:v for k,v in x.items() if k not in ['actual','context_null']}|{'actual':{k:v for k,v in x['actual'].items() if k!='label_permutation_ARI'},'null_recall':x['context_null']['macro_recall']} for x in out],indent=2))
if __name__=='__main__':main()
