"""Approved v7.2 qualification. All prior attempts remain read-only."""
import sys,os,json,copy,random,time,hashlib,math
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
P=Path(__file__).parent;B=P.parent;A2=B/'attempt-2-v7.1';OLD=B/'HARNESS'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(A2))
from harness import *
from verdict_v71 import verdict,clopper_upper
from role_preserving_keys import random_role_key,invariants
from dual_bank_verdict import combine
from source_first_controls import build_control,validate_source,tokenize
import worker_v72

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(n,x):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8');t.replace(p)
def project(rows):return [{k:r.get(k) for k in ('id','folio','section','class','words')} for r in rows]
def context(train,held,target,lex,k):return {'train':train,'held':held,'target':target,'lexicons':lex,'alphabet':k['target']['alphabet']}
def keybank(k,kind,seed):
 rng=random.Random(seed);fn=random_key if kind=='original' else random_role_key;out=[fn(k,rng) for _ in range(1000)]
 if kind=='role':assert all(invariants(k,z) and complexity(z)==complexity(k) for z in out)
 return out

def loadbank(path):
 d=read(path)
 while 'ref' in d:d=read(d['ref'])
 return d['scores']
CACHE={}
def bank(name,k,ks,ctx,old=None,oldctx=None):
 filename='banks/'+name+'.json';p=P/filename
 ident=digest({'keys':[digest(x) for x in ks],'train':project(ctx['train']),'held':project(ctx['held']),'target':ctx['target'],'lexicons':ctx['lexicons'],'score_seed':701})
 if p.exists():
  r=read(p);assert r['input_sha256']==ident;CACHE[ident]=str(p);return loadbank(p)
 if ident in CACHE:
  save(filename,{'input_sha256':ident,'ref':CACHE[ident],'key_hashes':[digest(x) for x in ks],'reuse':'identical scoring projection'});return loadbank(p)
 if old is not None:
  prior=read(old)
  assert prior['key_hashes']==[digest(x) for x in ks]
  assert project(ctx['train'])==project(oldctx['train']) and project(ctx['held'])==project(oldctx['held']) and ctx['target']==oldctx['target'] and ctx['lexicons']==oldctx['lexicons']
  save(filename,{'input_sha256':ident,'ref':str(old),'key_hashes':prior['key_hashes'],'reuse':'attempt2 exact score projection and key bank','reference_sha256':hashlib.sha256(Path(old).read_bytes()).hexdigest()});CACHE[ident]=str(p);return prior['scores']
 checkpoint=P/('banks/'+name+'.jsonl');header=P/('banks/'+name+'.context.json');checkpoint.parent.mkdir(exist_ok=True)
 if header.exists():assert read(header)['input_sha256']==ident
 else:save('banks/'+name+'.context.json',{'input_sha256':ident})
 done=[json.loads(s) for s in checkpoint.read_text(encoding='utf8').splitlines()] if checkpoint.exists() else []
 assert all(z['index']==i and z['key_sha256']==digest(ks[i]) for i,z in enumerate(done))
 if len(done)<len(ks):
  with ProcessPoolExecutor(max_workers=4,initializer=worker_v72.init,initargs=(ctx,)) as pool,checkpoint.open('a',encoding='utf8') as f:
   for z in pool.map(worker_v72.score_one,enumerate(ks[len(done):],start=len(done)),chunksize=10):
    f.write(json.dumps(z,ensure_ascii=False)+'\n');f.flush();done.append(z)
    if len(done)%250==0:print(name,len(done),flush=True)
 out=[z['scores'] for z in done];save(filename,{'input_sha256':ident,'key_hashes':[digest(x) for x in ks],'distinct_keys':len({digest(x) for x in ks}),'scores':out});CACHE[ident]=str(p);return out

def observe(k,ctx):
 worker_v72.init(ctx);return worker_v72.score_one((0,k))['scores']
def summarize(k,obs,banks,controls,require_C2):
 oo={kind:verdict(k,obs,banks[kind],controls[kind],require_C2=require_C2) for kind in ('original','role')}
 return {'combined':combine(oo['original'],oo['role']),'original':oo['original'],'role':oo['role']}

OLDKNOWN=read(OLD/'KNOWN-CIPHER-DATA.json')
def core_case(name,k,data,mode,seed,role_seed,old_prefix=None):
 custody_check(k,data['train'],data['held']);validate_key(k);validate_source(data['train'],k,mode);validate_source(data['held'],k,mode)
 controls={}
 for kind,ss in [('C1-word',801),('C1-glyph',802)]:
  controls[kind],receipt=build_control(data['held'],k,mode,kind,ss);save(name+'-'+kind+'-INPUT.json',{'records':controls[kind],'receipt':receipt})
 kb={kind:keybank(k,kind,ss) for kind,ss in [('original',seed),('role',role_seed)]};br={};bc={kind:{} for kind in kb}
 for kind,ks in kb.items():
  prior=A2/'banks'/(old_prefix+'-real.json') if old_prefix and kind=='original' else None
  br[kind]=bank(name+'-'+kind+'-real',k,ks,context(data['train'],data['held'],data['target'],data['lexicons'],k),prior,OLDKNOWN if prior else None)
  for control,rows in controls.items():
   prior=A2/'banks'/(old_prefix+'-'+control+'.json') if old_prefix and kind=='original' else None
   oldctx=dict(OLDKNOWN,held=OLDKNOWN['controls'][control]) if prior else None
   bc[kind][control]=bank(name+'-'+kind+'-'+control,k,ks,context(data['train'],rows,data['target'],data['lexicons'],k),prior,oldctx)
 obs=observe(k,context(data['train'],data['held'],data['target'],data['lexicons'],k));v=summarize(k,obs,br,bc,False)
 save(name+'-C1-ONLY.json',{'status':'INCOMPLETE_PENDING_FINAL_C2','key':k,'observed':obs,'result':v,'data_sha256':digest(data),'original_seed':seed,'role_seed':role_seed})
 print(name,v['combined']['verdict'],'C1-only',flush=True)
 return {'name':name,'key':k,'data':data,'mode':mode,'keys':kb,'real':br,'controls':bc,'observed':obs,'result':v,'old_prefix':old_prefix}

def trap(reading,base):
 cohort=read(P/'TRAP-COHORT.json')['readings'][reading];tr=cohort['train'];he=cohort['held'];vocab=sorted({w for r in tr for w in r['tokens']});alphabet=list('abcdefghijklmnopqrstuvwxyz');lex=base['lexicons']['HERBAL']
 mapping={c:c for c in alphabet};units=list(alphabet);rules=[];conds=[];prov={c:'fixed character fallback' for c in alphabet}
 for word in vocab:
  u='WORD:'+word;units.append(u);mapping[u]='x';prov[u]='training-only whole-word inventory';val=min(lex,key=lambda x:(abs(len(x)-len(word)),x))
  for section in sorted({r['section'] for r in tr if word in r['tokens']}):
   cond={'section':section}
   if cond not in conds:conds.append(cond)
   rules.append({'unit':u,'when':cond,'value':val,'source':'fixed dictionary objective; training only'})
 def convert(rows,part):return [{'id':reading+':'+r['locus'],'folio':r['folio'],'custody':'built' if part=='train' else 'demonstrated_unbuilt','section':r['section'],'class':'HERBAL','raw_words':r['tokens'],'words':[['WORD:'+w] if w in vocab else list(w) for w in r['tokens']]} for r in rows]
 train=convert(tr,'train');held=convert(he,'held');k={'id':'v72-actual-trap-'+reading,'units':units,'map':mapping,'rules':rules,'target':{'alphabet':alphabet,'resources':['frozen Macer development dictionary and target LM'],'system':'dictionary-overfit negative, no proposed reading'},'built_on':[r['id'] for r in train]+sorted({r['folio'] for r in train}),'provenance':prov,'value_inventory':sorted(set(mapping.values())|{r['value'] for r in rules}),'condition_inventory':conds,'process_evidence':'pre-frozen joint native-readability cohort; training-only whole-word/section dictionary fit; fixed character fallback; held pages not fit'}
 data={'train':train,'held':held,'target':base['target'],'lexicons':base['lexicons']};save('TRAP-'+reading+'-KEY.json',k);save('TRAP-'+reading+'-DATA.json',data)
 return k,data

def generator_rows(case,item,family):
 held=case['data']['held'];out=[]
 for i,line in enumerate(item['mechanism_receipt']['lines']):
  r=copy.deepcopy(item['rows'][i]);r['raw_words']=line
  if case['mode']=='training_whole_word':r['section']=held[i%len(held)]['section']
  r['words']=[tokenize(w,case['key'],case['mode']) for w in line];out.append(r)
 validate_source(out,case['key'],case['mode']);return out

def main():
 started=time.time();base=read(P/'KNOWN-DATA.json');k=read(P/'KNOWN-KEY.json');save('RUN-STATE.json',{'phase':'true-key','status':'RUNNING'})
 cases={};cases['CLEAN']=core_case('CLEAN',k,base,'known_initial_a',714,3714,'CLEAN')
 save('RUN-STATE.json',{'phase':'corrupt-and-noisy','status':'RUNNING'})
 cases['CORRUPT']=core_case('CORRUPT',read(P/'CORRUPT-KEY.json'),base,'known_initial_a',715,3715,'CORRUPT')
 for r in ('H','F'):cases['NOISY-'+r]=core_case('NOISY-'+r,k,read(P/('NOISY-'+r+'-DATA.json')),'known_initial_a',714,3714)
 save('RUN-STATE.json',{'phase':'400-independent-proposals','status':'RUNNING'});neg=[];clean=cases['CLEAN'];ctx=context(base['train'],base['held'],base['target'],base['lexicons'],k)
 for kind,seed in [('original',4711),('role',4712)]:
  rng=random.Random(seed);fn=random_key if kind=='original' else random_role_key
  for i in range(200):
   z=fn(k,rng);obs=observe(z,ctx);res=summarize(z,obs,clean['real'],clean['controls'],False);neg.append({'cohort':kind,'index':i,'key_sha256':digest(z),'observed':obs,'result':res})
 save('NEGATIVE-C1-ONLY.json',neg);print('400 independent proposals complete',flush=True)
 save('RUN-STATE.json',{'phase':'actual-readable-HF-trap','status':'RUNNING'})
 for r in ('H','F'):
  kk,dd=trap(r,base);cases['TRAP-'+r]=core_case('TRAP-'+r,kk,dd,'training_whole_word',719,3719)
 # Final C2 uses the unchanged saved outputs, generated through qualified v5 entrypoint.
 save('RUN-STATE.json',{'phase':'six-family-C2','status':'RUNNING'});g=read(A2/'V5-C2-DATA.json');save('V5-C2-PROVENANCE.json',{'source':str(A2/'V5-C2-DATA.json'),'sha256':hashlib.sha256((A2/'V5-C2-DATA.json').read_bytes()).hexdigest(),'owner_qualification':g['owner_qualification'],'reuse':'same sealed generator outputs; no generation/refit/reserve read'})
 for name,case in cases.items():
  for family,item in g['generated'].items():
   rr=generator_rows(case,item,family);save('controls/'+name+'-'+family+'.json',rr)
   for kind,ks in case['keys'].items():
    prefix=case['old_prefix'] or ('CLEAN' if case['mode']=='known_initial_a' else None)
    prior=A2/'banks'/(prefix+'-C2-'+family+'.json') if prefix and kind=='original' else None
    oldctx=dict(OLDKNOWN,held=item['rows']) if prior else None
    case['controls'][kind]['C2:'+family]=bank(name+'-'+kind+'-C2-'+family,case['key'],ks,context(case['data']['train'],rr,case['data']['target'],case['data']['lexicons'],case['key']),prior,oldctx)
  result=summarize(case['key'],case['observed'],case['real'],case['controls'],True);save(name+'-FINAL.json',result);case['final']=result;print(name,result['combined']['verdict'],'FINAL',flush=True)
 finalneg=[];rngs={'original':random.Random(4711),'role':random.Random(4712)}
 for row in neg:
  fn=random_key if row['cohort']=='original' else random_role_key;z=fn(k,rngs[row['cohort']]);assert digest(z)==row['key_sha256'];res=summarize(z,row['observed'],clean['real'],clean['controls'],True);finalneg.append({'cohort':row['cohort'],'index':row['index'],'key_sha256':row['key_sha256'],'result':res})
 save('NEGATIVE-FINAL.json',finalneg);negative={}
 for kind in ('original','role'):
  vv=[z['result']['combined']['verdict'] for z in finalneg if z['cohort']==kind];n=len(vv);p=vv.count('PASS');negative[kind]={'n':n,'tally':dict(Counter(vv)),'PASS_rate':p/n,'notPASS_rate':1-p/n,'CP95_upper':clopper_upper(p,n),'gate':1-p/n>=.99 and clopper_upper(p,n)<=.03}
 gates={'true_key':cases['CLEAN']['final']['combined']['verdict']=='PASS','noisy_H':cases['NOISY-H']['final']['combined']['verdict']=='PASS','noisy_F':cases['NOISY-F']['final']['combined']['verdict']=='PASS','negative_original':negative['original']['gate'],'negative_role':negative['role']['gate']}
 for r in ('H','F'):
  cc=cases['TRAP-'+r];fin=cc['final'];gates['trap_'+r+'_literalFAIL']=fin['combined']['verdict']=='FAIL';gates['trap_'+r+'_complete_controls']=all(v['complete_evaluation'] for kind,v in fin.items() if kind!='combined');gates['trap_'+r+'_finite_E3E4']=all(cc['observed'][e]['value'] is not None for e in ('E3','E4'))
 result={'version':'v7.2','status':'QUALIFIED_V7.2_ON_DECLARED_SCOPE' if all(gates.values()) else 'NOT_QUALIFIED','gates':gates,'cases':{n:c['final'] for n,c in cases.items()},'negative':negative,'scope':'fixed known Latin/context key; native-readable actual H/F overfittrap;6v5mechanism outputs; no claim of semantic reading or qualification of every source/tokenizer','old_attempts_unchanged':True,'no_vault_execution':True,'seconds':time.time()-started}
 save('QUALIFICATION.json',result);save('RUN-STATE.json',{'phase':'complete','status':result['status']});print(json.dumps({'status':result['status'],'gates':gates,'negative':negative}),flush=True)
if __name__=='__main__':main()
