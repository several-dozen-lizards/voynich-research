import sys,os,json,copy,random,math,time,statistics,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
P=Path(__file__).parent;OLD=P.parent/'HARNESS';sys.path.insert(0,str(OLD))
from harness import *
from verdict_v71 import verdict,clopper_upper
import bank_worker

def save(n,v):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(p)
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def loadold(n):return json.loads((OLD/n).read_text(encoding='utf8'))
def keys(k,seed):
 rng=random.Random(seed);return [random_key(k,rng) for _ in range(1000)]
def bank(name,k,ks,train,held,target,lexicons,reuse=None):
 path='banks/'+name+'.json';identity=digest({'key_hashes':[digest(x) for x in ks],'train':train,'held':held,'target':target,'lexicons':lexicons})
 if (P/path).exists():
  b=read(path)
  if b['input_sha256']!=identity:raise RuntimeError('bank identity changed')
  return b['scores']
 if reuse:
  old=loadold(reuse)
  assert old['C3_key_hashes']==[digest(x) for x in ks]
  out=old['C3_raw'];save(path,{'input_sha256':identity,'scores':out,'key_hashes':old['C3_key_hashes'],'reused_from':reuse});return out
 checkpoint=P/('banks/'+name+'.jsonl');checkpoint.parent.mkdir(exist_ok=True)
 done=[]
 if checkpoint.exists():done=[json.loads(x) for x in checkpoint.read_text().splitlines()]
 if any(z['index']!=i or z['key_sha256']!=digest(ks[i]) for i,z in enumerate(done)):raise RuntimeError('checkpoint identity mismatch')
 context={'train':train,'held':held,'target':target,'lexicons':lexicons}
 if len(done)<len(ks):
  with ProcessPoolExecutor(max_workers=4,initializer=bank_worker.init,initargs=(context,)) as pool,checkpoint.open('a',encoding='utf8') as f:
   for z in pool.map(bank_worker.score_one,enumerate(ks[len(done):],start=len(done)),chunksize=10):
    f.write(json.dumps(z,ensure_ascii=False)+'\n');f.flush();done.append(z)
    if len(done)%250==0:print(name,len(done),flush=True)
 out=[x['scores'] for x in done];save(path,{'input_sha256':identity,'scores':out,'key_hashes':[digest(x) for x in ks]});return out

def observed(k,train,held,target,lexicons):return raw_scores(k,train,held,target,lexicons)

def case(name,k,seed,data,reuse=None):
 ks=keys(k,seed);train=data['train'];held=data['held'];target=data['target'];lex=data['lexicons']
 custody_check(k,train,held);validate_key(k)
 real=bank(name+'-real',k,ks,train,held,target,lex,reuse)
 controls=data.get('controls') or {'C1-word':shuffle_lines(held,random.Random(801)),'C1-glyph':shuffle_glyphs(held,random.Random(802)),'C2':shuffle_lines(held,random.Random(803))}
 cb={}
 for control in ('C1-word','C1-glyph','C2'):
  cb[control]=bank(name+'-'+control,k,ks,train,controls[control],target,lex)
 obs=observed(k,train,held,target,lex);result=verdict(k,obs,real,cb)
 save(name+'-PROVISIONAL.json',{'status':'PROVISIONAL_C2_SURROGATE','result':result,'key':k,'observed':obs,'seed':seed,'data_sha256':digest(data)})
 print(name,result['verdict'],'provisional',flush=True)
 return {'key':k,'ks':ks,'train':train,'held':held,'target':target,'lexicons':lex,'real_bank':real,'controls':cb,'obs':obs,'result':result}

def noisy_data(data,k,rate):
 d=copy.deepcopy(data);h=copy.deepcopy(d['held']);f=copy.deepcopy(d['held']);sites=[(ri,wi,ui) for ri,r in enumerate(h) for wi,w in enumerate(r['words']) if w for ui in range(len(w))]
 rng=random.Random(1712);chosen=rng.sample(sites,round(rate*len(sites)));mask=[]
 for j,(ri,wi,ui) in enumerate(chosen):
  dest=h if j%2==0 else f;w=dest[ri]['words'][wi];old=w[ui];orig=k['map'][old] if old!='INIT_A' else 'a'
  alternatives=['u'+x for x in k['target']['alphabet'] if x!=orig];w[ui]=rng.choice(alternatives)
  mask.append({'reading':'H' if j%2==0 else 'F','line':ri,'word':wi,'unit':ui,'old':old,'new':w[ui]})
 def output(held):
  z=copy.deepcopy(data);z['held']=held;z['controls']={'C1-word':shuffle_lines(held,random.Random(801)),'C1-glyph':shuffle_glyphs(held,random.Random(802)),'C2':shuffle_lines(held,random.Random(803))};return z
 save('NOISY-MASK.json',{'source_rate':rate,'sites':len(sites),'disagreeing_sites':len(chosen),'realized_disagreement':len(chosen)/len(sites),'seed':1712,'edits':mask,'noise_model':'synthetic substitutions, disjoint H/F sites, unchanged token boundaries'})
 return output(h),output(f)

def build_trap(reading,base):
 slices=read('TRAP-SLICES.json')['readings'][reading];tr=slices['train'];he=slices['held'];vocab=sorted({w for r in tr for w in r['tokens'] if w})
 alphabet=list('abcdefghijklmnopqrstuvwxyz');lex=base['lexicons']['HERBAL'];mapping={c:c for c in alphabet};units=list(alphabet);rules=[];conds=[];prov={c:'fixed character fallback' for c in alphabet}
 for word in vocab:
  u='WORD:'+word;units.append(u);mapping[u]='x';prov[u]='training-only whole-word tokenizer inventory'
  val=min(lex,key=lambda x:(abs(len(x)-len(word)),x))
  for section in sorted({r['section'] for r in tr if word in r['tokens']}):
   condition={'section':section}
   if condition not in conds:conds.append(condition)
   rules.append({'unit':u,'when':condition,'value':val,'source':'maximal dictionary-hit training objective, all values from training reference lexicon'})
 def convert(rr,part):
  out=[]
  for r in rr:
   out.append({'id':reading+':'+r['locus'],'folio':r['folio'],'custody':'built' if part=='train' else 'demonstrated_unbuilt','section':r['section'],'class':'HERBAL','words':[None if w is None else ['WORD:'+w] if w in vocab else list(w) for w in r['tokens']]})
  return out
 train=convert(tr,'train');held=convert(he,'held')
 k={'id':'actual-flexible-dictionary-trap-'+reading,'units':units,'map':mapping,'rules':rules,'target':{'alphabet':alphabet,'resources':['same frozen Macer reference lexicon/LM'],'system':'Latin dictionary-overfit negative, no claimed reading'},'built_on':[r['id'] for r in train]+sorted({r['folio'] for r in train}),'provenance':prov,'value_inventory':sorted(set(mapping.values())|{r['value'] for r in rules}),'condition_inventory':conds,'process_evidence':'whole-word inventory and dictionary-match context values fitted only to predetermined first8 nonzodiac folios; held next8 folios not used to fit key; other prior exposure retained'}
 data={'train':train,'held':held,'target':base['target'],'lexicons':base['lexicons']}
 save('TRAP-'+reading+'-KEY.json',k);save('TRAP-'+reading+'-DATA.json',data)
 save('TRAP-'+reading+'-TRAINING.json',{'dictionary_objective':raw_scores(k,train,train,base['target'],base['lexicons'])['E1'],'word_inventory':len(vocab),'context_slots':len(rules),'K_bits':complexity(k),'tokenizer':'exact training whole-word match else character fallback; no held inventory learning'})
 return k,data

def main():
 start=time.time();data=loadold('KNOWN-CIPHER-DATA.json');k=loadold('KNOWN-KEY.json');save('RUN-STATE.json',{'phase':'true-key','status':'RUNNING','utc':time.time()})
 clean=case('CLEAN',k,714,data,'KNOWN-POSITIVE-FULL.json')
 save('RUN-STATE.json',{'phase':'corrupt-and-dual','status':'RUNNING'})
 corrupt=loadold('NEAR-MISS-KEY.json');near=case('CORRUPT',corrupt,715,data,'NEAR-MISS-FULL.json')
 rate=read('HF-DISAGREEMENT.json')['rate'];hd,fd=noisy_data(data,k,rate);save('NOISY-H-DATA.json',hd);save('NOISY-F-DATA.json',fd)
 H=case('NOISY-H',k,714,hd);F=case('NOISY-F',k,714,fd)
 save('RUN-STATE.json',{'phase':'random-proposals','status':'RUNNING'})
 rng=random.Random(1711);proposals=[]
 for i in range(200):
  rk=random_key(k,rng);obs=observed(rk,clean['train'],clean['held'],clean['target'],clean['lexicons']);res=verdict(rk,obs,clean['real_bank'],clean['controls']);proposals.append({'index':i,'key_sha256':digest(rk),'observed':obs,'result':res})
 save('NEGATIVE-PROPOSALS-PROVISIONAL.json',proposals);print('200 negative proposals complete',flush=True)
 save('RUN-STATE.json',{'phase':'actual-flexible-key-trap','status':'RUNNING'})
 traps={}
 for reading in ('H','F'):
  tk,td=build_trap(reading,data);traps[reading]=case('TRAP-'+reading,tk,719,td)
 save('STAGES1-4.json',{'status':'COMPLETED_WITH_PROVISIONAL_SURROGATE_C2','clean':clean['result'],'corrupt':near['result'],'noisy_H':H['result'],'noisy_F':F['result'],'negative_tally':dict(Counter(x['result']['verdict'] for x in proposals)),'traps':{r:z['result'] for r,z in traps.items()},'seconds':time.time()-start})
 save('RUN-STATE.json',{'phase':'qualified-v5-C2-required','status':'AWAITING_STAGE5','seconds':time.time()-start})
 print('Stages1–4 complete; stage5 required',flush=True)

if __name__=='__main__':main()
