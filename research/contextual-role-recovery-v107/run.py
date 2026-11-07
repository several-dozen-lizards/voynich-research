import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,random,collections,math,types,time,re,warnings
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import cdist
P=Path(__file__).resolve().parent
H=Path(r'C:/Users/lewis/.codex/visualizations/2026/10/21/01a160c2-56f0-7303-b3bf-ed8594c6ec40')
SOURCE=H/'voynich-grammar-v36/sources'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def engine(forced=False):
 s=(P/'engine-frozen.py').read_text(encoding='utf8')
 if forced:s=s.replace('for k in [2,3,4]:','for k in [2]:').replace("best['silhouette']<.2","best['silhouette']< -1")
 m=types.ModuleType('engine');m.__file__=str(P/'engine-frozen.py');exec(compile(s,m.__file__,'exec'),m.__dict__);return m
E=engine();F=engine(True)
def shuffle(rows,seed):
 out=[dict(r,context=r['context'].copy()) for r in rows];rng=random.Random(seed)
 for page in sorted({r['page'] for r in out}):
  ix=[i for i,r in enumerate(out) if r['page']==page]
  for j in range(4):
   vals=[out[i]['context'][j] for i in ix];rng.shuffle(vals)
   for i,v in zip(ix,vals):out[i]['context'][j]=v
 return out
def vectors(rows,vocab=None):
 if vocab is None:vocab={f:i for i,f in enumerate(sorted({f for r in rows for f in E.fs(r)}))}
 x=np.zeros((len(rows),len(vocab)))
 for i,r in enumerate(rows):
  for f in E.fs(r):
   if f in vocab:x[i,vocab[f]]=1
 return x/np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1e-12),vocab
def fitks(x):
 out=[]
 for k in range(1,6):
  if k==1:
   cent=x.mean(axis=0,keepdims=True);lab=np.zeros(len(x),dtype=int);best=(float(((x-cent)**2).sum()),cent,lab)
  else:
   best=None
   for seed in range(1074601,1074604):
    with warnings.catch_warnings():
     warnings.simplefilter('ignore');cent,lab=kmeans2(x,k,iter=60,minit='++',seed=seed)
    if len(set(lab))<k:continue
    loss=float(((x-cent[lab])**2).sum())
    if best is None or loss<best[0]:best=(loss,cent,lab)
  out.append(best)
 return out
def gap(rows,seed):
 tr=[r for r in rows if r['split']=='train'];te=[r for r in rows if r['split']=='test']
 if len(tr)<10:return {'k':None,'reason':'insufficient training','assignments':[],'choices':[]}
 a,vocab=vectors(tr);b,_=vectors(te,vocab);actual=fitks(a);refs=[]
 for j in range(19):
  x,_=vectors(shuffle(tr,seed+j),vocab);refs.append([math.log(max(z[0],1e-12)) if z else None for z in fitks(x)])
 choices=[]
 for i,z in enumerate(actual):
  vals=[r[i] for r in refs if r[i] is not None]
  choices.append({'k':i+1,'loss':z[0] if z else None,'gap':float(np.mean(vals)-math.log(max(z[0],1e-12))) if z and len(vals)==19 else None,'s':float(np.std(vals,ddof=1)*math.sqrt(1+1/19)) if len(vals)==19 else None})
 selected=None
 for i in range(4):
  c,d=choices[i:i+2]
  if c['gap'] is not None and d['gap'] is not None and c['gap']>=d['gap']-d['s']:selected=i+1;break
 if selected is None:return {'k':None,'reason':'no one-standard-error stopping point below search ceiling','choices':choices,'assignments':[]}
 _,cent,lab=actual[selected-1];test=np.argmin(cdist(b,cent),axis=1) if len(te) else []
 return {'k':selected,'choices':choices,'assignments':[{'id':r['id'],'split':r['split'],'cluster':int(z)} for rs,zs in [(tr,lab),(te,test)] for r,z in zip(rs,zs)]}
def wilson(x,n):
 z=1.959963984540054;p=x/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [c-rad,c+rad]
def synthetic(regime,j):
 rng=random.Random(1070000+1000*['iid','page_nuisance','clean2','clean3','clean4','noisy2'].index(regime)+j)
 k={'clean2':2,'clean3':3,'clean4':4,'noisy2':2}.get(regime,1);rows=[];truth={}
 for block in range(20):
  roles=[i%k for i in range(12)];rng.shuffle(roles)
  for i,role in enumerate(roles):
   ctx=[]
   for col in range(4):
    if regime=='iid':val='w'+str(rng.randrange(16))
    elif regime=='page_nuisance':val='page'+str(block%4)+'w'+str(rng.randrange(4)) if rng.random()<.95 else 'w'+str(rng.randrange(16))
    else:val='r'+str(role)+'w'+str(rng.randrange(4)) if rng.random()<(0.85 if regime=='noisy2' else .95) else 'noise'+str(rng.randrange(16))
    ctx.append(val)
   ident=f'{block}:{i}';rows.append({'id':ident,'page':str(block),'split':'train' if block<12 else 'test','context':ctx});truth[ident]=role
 return rows,truth,k

def qualification():
 verify();assert not (P/'QUALIFICATION.json').exists();summary=[]
 with (P/'synthetic-trials.jsonl').open('x',encoding='utf8') as log:
  for ri,regime in enumerate(['iid','page_nuisance','clean2','clean3','clean4','noisy2']):
   successes=0
   for j in range(40):
    rows,key,truek=synthetic(regime,j);fit=gap(rows,107100000+ri*10000+j*100)
    te=[a for a in fit['assignments'] if a['split']=='test'];ar=E.ari([key[a['id']] for a in te],[a['cluster'] for a in te]) if truek>1 else None
    ok=fit['k']==truek;successes+=ok
    log.write(json.dumps({'regime':regime,'trial':j,'true_k':truek,'selected_k':fit['k'],'exact':ok,'test_ARI':ar,'choices':fit['choices']})+'\n');log.flush()
   required=38 if truek==1 else 32;summary.append({'regime':regime,'exact':successes,'n':40,'required':required,'wilson95':wilson(successes,40),'pass':successes>=required});print(json.dumps(summary[-1]),flush=True)
 dump('QUALIFICATION.json',{'status':'PASS' if all(s['pass'] for s in summary) else 'FAIL','regimes':summary,'limits':'Project-specific categorical-reference gap variant; strong toy signals, no broad discovery qualification. No retuning.'})

def prepare():
 verify();assert not (P/'BLIND-INPUT.json').exists();cfg=load(P/'PROTOCOL.json')['historical'];rows=[];key={};seen=set();audit=collections.Counter();barriers=[]
 for partition in ['train','dev','test']:
  text=(SOURCE/f'la_proiel-ud-{partition}.conllu').read_text(encoding='utf8')
  for block in text.strip().split('\n\n'):
   comments=[l for l in block.splitlines() if l.startswith('#')];tokens=[l.split('\t') for l in block.splitlines() if l and not l.startswith('#') and l.split('\t')[0].isdigit()]
   sour=next((l.split(' = ',1)[1] for l in comments if l.startswith('# source = ')),None)
   if not sour or sour.split(',')[0] not in cfg['works']:continue
   sentid=next((l.split(' = ',1)[1] for l in comments if l.startswith('# sent_id = ')),None)
   assert sentid and all(len(t)==10 for t in tokens)
   identity=tuple(t[1].lower() for t in tokens)
   if identity in seen:audit['duplicate_sentences_removed']+=1;continue
   seen.add(identity)
   ref=next((m.group(1) for t in tokens if (m:=re.search(r'(?:^|\|)Ref=([^|]+)',t[9]))),None)
   if ref is None:raise ValueError('Missing source reference')
   # Book+chapter (or letter) kept together; source prefix separates works.
   parts=ref.split('.');unit=sour.split(',')[0]+':'+'.'.join(parts[:2]);split='test' if int(hashlib.sha256(('v107:'+unit).encode()).hexdigest()[:8],16)%5<2 else 'train'
   audit['admitted_sentences']+=1
   for i,t in enumerate(tokens):
    target=t[1].lower()
    if target not in cfg['targets']:continue
    def context_at(j):
     if not 0<=j<len(tokens):return '#edge'
     step=1 if j>i else -1
     if any(tokens[k][3]=='PUNCT' for k in range(i+step,j+step,step)):return '#barrier'
     return tokens[j][1].lower()
    ident=partition+':'+sentid+':'+t[0];rows.append({'id':ident,'page':unit,'stratum':sour.split(',')[0]+'|'+target,'split':split,'context':[context_at(i-2),context_at(i-1),context_at(i+1),context_at(i+2)],'source_ref':ref,'sentence_id':sentid,'target':target});key[ident]={'upos':t[3],'source_partition':partition,'source':sour,'reference':ref}
 assert len({r['id'] for r in rows})==len(rows)
 assert {r['page'] for r in rows if r['split']=='train'}.isdisjoint({r['page'] for r in rows if r['split']=='test'})
 dump('BLIND-INPUT.json',rows);dump('ANSWER-KEY.json',key);dump('PREPARATION-AUDIT.json',dict(audit));dump('INPUT-FREEZE.json',{n:sha(P/n) for n in ['BLIND-INPUT.json','ANSWER-KEY.json','PREPARATION-AUDIT.json']});print('Prepared',len(rows),'occurrences; no label scoring.',flush=True)

def evaluate(fit,rows,key,roles):
 meta={r['id']:r for r in rows};tr=[a for a in fit['assignments'] if a['split']=='train' and key[a['id']]['upos'] in roles];te=[a for a in fit['assignments'] if a['split']=='test' and key[a['id']]['upos'] in roles]
 counts=collections.defaultdict(collections.Counter)
 for a in tr:counts[a['cluster']][key[a['id']]['upos']]+=1
 mapping={k:sorted(c,key=lambda x:(-c[x],x))[0] for k,c in counts.items()};y=[key[a['id']]['upos'] for a in te];z=[a['cluster'] for a in te];pred=[mapping.get(v,'UNKNOWN') for v in z];n=collections.Counter(y);traincounts=collections.Counter(key[a['id']]['upos'] for a in tr)
 recall=sum(sum(a==role and b==role for a,b in zip(y,pred))/n[role] for role in n)/len(n) if n else None;ar=E.ari(y,z);rng=random.Random(1074602);perms=[]
 for _ in range(199):
  yy=y.copy();rng.shuffle(yy);perms.append(E.ari(yy,z))
 p=(1+sum(v>=ar for v in perms if v is not None))/200 if ar is not None else None
 allcounts={split:dict(collections.Counter(key[r['id']]['upos'] for r in rows if r['split']==split)) for split in ['train','test']}
 support=all(traincounts[r]>=20 and n[r]>=20 for r in roles) and len({meta[a['id']]['page'] for a in te})>=5
 return {'train_counts':dict(traincounts),'test_counts':dict(n),'all_gold_counts':allcounts,'test_blocks':len({meta[a['id']]['page'] for a in te}),'support':support,'balanced_recall':recall,'ARI':ar,'p_raw':p,'p_bonferroni8':min(1,8*p) if p else None,'mapping':mapping,'predictions':[{'id':a['id'],'gold':yy,'cluster':zz,'prediction':pp} for a,yy,zz,pp in zip(te,y,z,pred)]}

def historical():
 verify();assert not (P/'RESULTS.json').exists()
 for n,h in load(P/'INPUT-FREEZE.json').items():assert sha(P/n)==h,n
 rows=load(P/'BLIND-INPUT.json');qual=load(P/'QUALIFICATION.json');fits=[]
 for st in sorted({r['stratum'] for r in rows}):
  rs=[r for r in rows if r['stratum']==st];null=shuffle(rs,1074701);fits.append({'stratum':st,'arm':'fixed2','actual':F.fit(rs),'null':F.fit(null)})
  if qual['status']=='PASS':fits.append({'stratum':st,'arm':'automatic_gap','actual':gap(rs,1078800),'null':gap(null,1079900)})
 dump('ASSIGNMENTS.json',fits);dump('ASSIGNMENT-FREEZE.json',{'sha256':sha(P/'ASSIGNMENTS.json'),'before_answer_key_read':True})
 key=load(P/'ANSWER-KEY.json');results=[];cfg=load(P/'PROTOCOL.json')['historical']
 for f in fits:
  rs=[r for r in rows if r['stratum']==f['stratum']];roles=cfg['targets'][rs[0]['target']];a=evaluate(f['actual'],rs,key,roles);b=evaluate(f['null'],rs,key,roles)
  ok=a['support'] and f['actual']['k']==2 and a['balanced_recall']>=.8 and a['ARI']>=.5 and a['p_bonferroni8']<=.05 and b['balanced_recall'] is not None and a['balanced_recall']-b['balanced_recall']>=.1
  results.append({'stratum':f['stratum'],'arm':f['arm'],'k':f['actual']['k'],'status':'PASS' if ok else 'FAIL' if a['support'] else 'NOT_ESTIMABLE','actual':a,'context_null':b});print(f['stratum'],f['arm'],results[-1]['status'],'recall',a['balanced_recall'],'null',b['balanced_recall'],flush=True)
 dump('RESULTS.json',{'automatic_selector_qualification':qual['status'],'automatic_historical_run':qual['status']=='PASS','results':results,'Voynich':'CLOSED; no manuscript role or meaning claim','scope':'Fixed2 transfer evaluates separate annotated Latin homographs; binary choice supplied, not discovered.'})

def verify():
 for n,h in load(P/'FREEZE.json')['local'].items():assert sha(P/n)==h,n
 for n,h in load(P/'FREEZE.json')['external'].items():assert sha(Path(n))==h,n
if __name__=='__main__':
 import sys
 command=sys.argv[1]
 if command=='freeze':
  assert not (P/'FREEZE.json').exists();names=['run.py','PROTOCOL.json','engine-frozen.py','parser-frozen.py','SOURCE-PROVENANCE.json'];paths=[SOURCE/f'la_proiel-ud-{s}.conllu' for s in ['train','dev','test']]
  dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'local':{n:sha(P/n) for n in names},'external':{str(p):sha(p) for p in paths}});print('Frozen before new target extraction, synthetic tests or scoring.')
 elif command=='qualify':qualification()
 elif command=='prepare':prepare()
 elif command=='historical':historical()
 elif command=='verify':verify();print('Freeze intact.')
