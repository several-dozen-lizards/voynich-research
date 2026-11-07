import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,re,collections,itertools
import numpy as np
R=Path(__file__).resolve().parent
SOURCE=R.parent/'frequency-atlas-v48/rows.json'
def feats(w):
 out=set()
 for n in [1,2,3]:
  if len(w)>=n:out.add('prefix:'+w[:n]);out.add('suffix:'+w[-n:])
  for i in range(1,len(w)-n):out.add('internal:'+w[i:i+n])
 return out
def fol(pg):return re.match(r'f\d+',pg).group()
def pos(i,n):return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def build():
 rows=json.loads(SOURCE.read_text());locs=collections.defaultdict(set)
 for r in rows:locs[r[6]].add(r[0])
 shared={l for l,ts in locs.items() if len(ts)==2};ev=[];counts=collections.Counter();pages=collections.defaultdict(set)
 for tr,pg,sec,h,lang,fmt,loc,ws in rows:
  if loc not in shared:continue
  for i,w in enumerate(ws):
   if not w:continue
   fs=feats(w);ev.append(dict(tr=tr,folio=fol(pg),page=pg,section=sec,hand=h,language=lang,format=fmt,pos=pos(i,len(ws)),ordinal=i+1,w=w,features=fs))
   counts.update(fs)
   for f in fs:pages[f].add(fol(pg))
 features=sorted(f for f,n in counts.items() if n>=20 and len(pages[f])>=5)
 return rows,ev,features,shared
def matrices(events,features,a,b):
 by=collections.defaultdict(list);sections=collections.defaultdict(set)
 for e in events:
  if e['section'] not in [a,b]:continue
  sections[e['folio']].add(e['section']);by[(e['section'],e['folio'])].append(e)
 excluded=sorted(f for f,ss in sections.items() if len(ss)>1)
 keys=sorted(k for k in by if k[1] not in excluded);ix={f:i for i,f in enumerate(features)};x=np.zeros((len(keys),len(features)),np.float32);den=[]
 for j,k in enumerate(keys):
  es=by[k];den.append(len(es))
  for e in es:
   for f in e['features']:
    if f in ix:x[j,ix[f]]+=1
  x[j]/=len(es)
 mask=np.array([k[0]==a for k in keys]);return x,mask,keys,den,excluded
def support(mask,den,minfolios=5,minwords=100):
 return min(sum(mask),sum(~mask))>=minfolios and min(sum(n for n,m in zip(den,mask) if m),sum(n for n,m in zip(den,mask) if not m))>=minwords
def main():
 frozen=json.loads((R/'FREEZE.json').read_text(encoding='utf-8-sig'))
 for name,h in frozen.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
 rows,ev,features,shared=build();groups=collections.defaultdict(list)
 for e in ev:groups[(e['tr'],e['hand'],e['language'],e['format'],e['pos'])].append(e)
 panels=[];excluded=[]
 for key,es in sorted(groups.items()):
  for a,b in itertools.combinations(sorted(set(e['section'] for e in es)),2):
   x,m,ks,den,mixed=matrices(es,features,a,b)
   info=dict(transcription=key[0],hand=key[1],language=key[2],format=key[3],position=key[4],section_a=a,section_b=b,folios_a=int(sum(m)),folios_b=int(sum(~m)),words_a=sum(n for n,t in zip(den,m) if t),words_b=sum(n for n,t in zip(den,m) if not t),mixed_folios_excluded=mixed)
   if not support(m,den):excluded.append(info|{'reason':'insufficient support'});continue
   panels.append((info,es,x,m,ks,den))
 M=len(panels);results=[];rng=np.random.default_rng(4901)
 for pi,(info,es,x,m,ks,den) in enumerate(panels):
  n=len(m);na=int(sum(m));nb=n-na;diff=x[m].mean(0)-x[~m].mean(0);se=np.sqrt(x.var(0,ddof=1)*(1/na+1/nb));se=np.maximum(se,1e-8);stat=np.abs(diff/se)
  weights=np.full((1999,n),-1/nb,dtype=np.float32)
  for row in weights:row[rng.choice(n,na,replace=False)]=1/na
  perm=(weights@x)/se;maxima=np.max(np.abs(perm),axis=1);p=(1+(maxima[:,None]>=stat[None,:]-1e-6).sum(0))/2000;adjust=np.minimum(1,p*M)
  ra=x[m].mean(0);rb=x[~m].mean(0)
  vals=[dict(feature=f,rate_a=float(ra[j]),rate_b=float(rb[j]),difference_pp=float(100*diff[j]),p_maxT=float(p[j]),p_family=float(adjust[j])) for j,f in enumerate(features)]
  results.append(info|dict(features=vals,folio_denominators=[dict(section=k[0],folio=k[1],words=d) for k,d in zip(ks,den)]))
  print('panel',pi+1,'/',M,info['transcription'],info['hand'],info['position'],info['section_a'],info['section_b'],flush=True)
 lookup={tuple(p[k] for k in ['transcription','hand','language','format','position','section_a','section_b']):p for p in results};candidates=[];disagreements=[]
 for key,hp in lookup.items():
  if key[0]!='H' or ('F',)+key[1:] not in lookup:continue
  fp=lookup[('F',)+key[1:]]
  for h,f in zip(hp['features'],fp['features']):
   same=h['difference_pp']*f['difference_pp']>0;large=min(abs(h['difference_pp']),abs(f['difference_pp']))>=2
   ok=same and large and max(h['p_family'],f['p_family'])<=.05
   record={k:hp[k] for k in ['hand','language','format','position','section_a','section_b']}|dict(feature=h['feature'],H=h,F=f)
   if ok:candidates.append(record)
   elif max(abs(h['difference_pp']),abs(f['difference_pp']))>=2 and (not same or min(h['p_family'],f['p_family'])<=.05):disagreements.append(record|dict(reason='direction disagreement' if not same else 'only one reading passes or effect below threshold'))
 for c in candidates:
  sensitivities=[]
  for tr in ['H','F']:
   base=[e for e in ev if e['tr']==tr and e['hand']==c['hand'] and e['language']==c['language'] and e['format']==c['format'] and e['pos']==c['position']]
   arms={'length5-8':[e for e in base if 5<=len(e['w'])<=8]}
   if c['position']=='interior':arms.update({f'ordinal{j}':[e for e in base if e['ordinal']==j] for j in [2,3,4]})
   for arm,es in arms.items():
    x,m,ks,den,_=matrices(es,[c['feature']],c['section_a'],c['section_b']);valid=support(m,den,3,30)
    d=float(100*(x[m].mean()-x[~m].mean())) if valid else None
    sensitivities.append(dict(tr=tr,arm=arm,status='not estimable' if not valid else 'reversal' if d*c[tr]['difference_pp']<0 else 'same direction',difference_pp=d,folios_a=int(sum(m)),folios_b=int(sum(~m))))
  c['sensitivity']=sensitivities
 result=dict(protocol='PROTOCOL.json',panel_tests=M,features=len(features),shared_loci=len(shared),events=len(ev),results=results,candidates=candidates,exceptions=disagreements,unestimable=excluded,interpretation='Conditional associations; section-label exchangeability is unverified. No semantic conclusion.')
 (R/'RESULTS.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(panels=M,features=len(features),candidates=len(candidates),exceptions=len(disagreements),unestimable=len(excluded))))
if __name__=='__main__':main()
