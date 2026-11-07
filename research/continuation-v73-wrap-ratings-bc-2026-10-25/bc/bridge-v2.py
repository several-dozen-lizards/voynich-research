"""Source-first E2 bridge; baseline and prior adapter files are immutable."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import copy,hashlib,importlib.util,json,random,math
from collections import defaultdict
P=Path(__file__).parent;ROOT=P.parents[1];A=ROOT/'ordered-name-lists-v7c/attempt-3-v7.2'
sys.path.insert(0,str(A));sys.path.insert(0,str(A.parent/'attempt-2-v7.1'));sys.path.insert(0,str(A.parent/'HARNESS'))
import harness as h
import worker_v72
from source_first_controls import tokenize,validate_source
from role_preserving_keys import random_role_key,invariants
from verdict_v71 import verdict,clopper_upper
from dual_bank_verdict import combine
s=importlib.util.spec_from_file_location('adapters',ROOT/'priority-continuation-2026-10-25/adapters/adapters.py');ad=importlib.util.module_from_spec(s);s.loader.exec_module(ad)
READS=[]
def read(path):
 path=Path(path);READS.append(str(path.relative_to(ROOT)));return json.loads(path.read_text(encoding='utf-8'))
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def scorebank(path):
 z=read(path);hashes=z['key_hashes']
 while 'ref' in z:z=read(z['ref'])
 return hashes,z['scores']
def choose_pairs(rows):
 found=defaultdict(list)
 for r in rows:
  for i in range(len(r['raw_words'])-1):found[tuple(r['raw_words'][i:i+2])].append([[r['id'],i],[r['id'],i+1]])
 pairs=[];used=set()
 for ws,occ in found.items():
  available=[z for z in occ if not any(tuple(loc) in used for loc in z)]
  if len(available)<2:continue
  a,b=available[:2]
  if set(map(tuple,a))&set(map(tuple,b)):continue
  pairs.append(dict(id='known-pair-'+str(len(pairs)),a=a,b=b))
  used.update(map(tuple,a+b))
  if len(pairs)==24:break
 if len(pairs)<4:raise ValueError('insufficient known repeated multi-word spans')
 return pairs

BASE_INDEX={}
def e2(rows,pairs,key):
 rows=[dict(r,reading='H') for r in rows]
 pairs=[dict(p,a=[[rows[BASE_INDEX[rid]]['id'],slot] for rid,slot in p['a']],b=[[rows[BASE_INDEX[rid]]['id'],slot] for rid,slot in p['b']]) for p in pairs]
 return {k:v for k,v in ad.e2_spans(rows,pairs,key,h.decode_word).items() if k not in ('qualification','unknown')}

def main():
 data=read(A/'KNOWN-DATA.json');BASE_INDEX.update({r['id']:i for i,r in enumerate(data['held'])});key=read(A/'KNOWN-KEY.json');h.validate_key(key);h.custody_check(key,data['train'],data['held']);pairs=choose_pairs(data['held']);save('PAIRS.json',dict(pairs=pairs,selection='fixed source-order repeated two-word spans; exact-match identity is invariant under many maps and is not by itself phonetic evidence'))
 datasets={'real':data['held']}
 for name in ('C1-word','C1-glyph'):datasets[name]=read(A/('CLEAN-'+name+'-INPUT.json'))['records']
 for family in ('G1','G2','G3','G4','G5','G6'):datasets['C2:'+family]=read(A/('controls/CLEAN-'+family+'.json'))
 # Validate and retokenize original source BEFORE any key application.
 for name,rows in datasets.items():
  assert len(rows)==len(data['held'])
  for r,base in zip(rows,data['held']):
   assert len(r['words'])==len(base['words'])
   if 'control_raw_words' in r:r['raw_words']=r['control_raw_words']
  validate_source(rows,key,'known_initial_a')
  for r in rows:assert r['words']==[tokenize(w,key,'known_initial_a') for w in r['raw_words']]
 worker_v72.init(dict(train=data['train'],held=datasets['real'],target=data['target'],lexicons=data['lexicons'],alphabet=key['target']['alphabet']));observed=worker_v72.score_one((0,key))['scores'];observed['E2']=e2(datasets['real'],pairs,key)
 realbanks={};controls={};regressions=0;newbanks={}
 for kind,fn,seed in [('original',h.random_key,714),('role',random_role_key,3714)]:
  rng=random.Random(seed);keys=[fn(key,rng) for _ in range(1000)];controls[kind]={};newbanks[kind]={}
  for name,rows in datasets.items():
   suffix='real' if name=='real' else name.replace(':','-');hashes,old=scorebank(A/('banks/CLEAN-'+kind+'-'+suffix+'.json'))
   assert hashes==[h.digest(k) for k in keys]
   worker_v72.init(dict(train=data['train'],held=rows,target=data['target'],lexicons=data['lexicons'],alphabet=key['target']['alphabet']))
   for i in (0,999):
    direct=worker_v72.score_one((i,keys[i]))['scores']
    for metric in ('E1','E3','E4','E5','E6'):assert direct[metric]==old[i][metric],(kind,name,i,metric)
    regressions+=1
   bank=[]
   for k,prior in zip(keys,old):
    z=copy.deepcopy(prior);z['E2']=e2(rows,pairs,k);bank.append(z)
   newbanks[kind][name]=bank
   if name=='real':realbanks[kind]=bank
   else:controls[kind][name]=bank
   print('bridge bank',kind,name,len(bank),flush=True)
 positive={kind:verdict(key,observed,realbanks[kind],controls[kind],True) for kind in realbanks};joint=combine(positive['original'],positive['role'])
 # Exact-key replay of already sealed fresh-proposal raw projections; no new score fitting.
 previous=read(A/'NEGATIVE-C1-ONLY.json');negative=[]
 rngs={'original':random.Random(4711),'role':random.Random(4712)}
 for row in previous:
  kind=row['cohort'];fn=h.random_key if kind=='original' else random_role_key;k=fn(key,rngs[kind]);assert h.digest(k)==row['key_sha256'];obs=copy.deepcopy(row['observed']);obs['E2']=e2(datasets['real'],pairs,k)
  vv={b:verdict(k,obs,realbanks[b],controls[b],True) for b in realbanks};negative.append(dict(cohort=kind,index=row['index'],key_sha256=h.digest(k),combined=combine(vv['original'],vv['role'])))
 neg={}
 for kind in ('original','role'):
  rs=[z for z in negative if z['cohort']==kind];flags=sum(z['combined']['verdict']=='PASS' for z in rs);upper=clopper_upper(flags,len(rs));neg[kind]=dict(n=len(rs),PASS=flags,CP95upper=upper,gate=(1-flags/len(rs)>=.99 and upper<=.03))
 # Date/spelling/gap-preserving bridge to the final audited C1 source set.
 lists=read(ROOT/'ordered-name-lists-v7c/C1-source-freeze-v1/LISTS.json');source_hash=hashlib.sha256((ROOT/'ordered-name-lists-v7c/C1-source-freeze-v1/LISTS.json').read_bytes()).hexdigest();packets=[]
 for profile in lists['profiles']:
  packet=dict(id=profile['id'],source='frozen C1 LISTS.json#'+profile['id'],source_sha256=source_hash,date_latest=profile['date_upper_year'],eligible_by_1440=profile['date_upper_year']<=1440,slots=[entry.get('name') for entry in profile['entries']],normalization='identity; preserve audited spelling',variant_id=profile['id']);packet['freeze_sha256']=ad.digest(packet);assert ad.list_variant(packet)==tuple(packet['slots']);packets.append(packet)
 gates=dict(known_positive=joint['verdict']=='PASS',negative_original=neg['original']['gate'],negative_role=neg['role']['gate'],raw_projection_regressions=regressions==36,source_first_all_datasets=len(datasets)==9,frozen_list_profiles=len(packets)==9)
 save('POSITIVE.json',dict(observed=observed,result=positive,combined=joint));save('NEGATIVE.json',negative);save('LIST-PACKETS.json',packets)
 save('QUALIFICATION.json',dict(status='SOURCE_FIRST_E2_BRIDGE_QUALIFIED_ON_DECLARED_SCOPE' if all(gates.values()) else 'SOURCE_FIRST_E2_BRIDGE_NOT_QUALIFIED',gates=gates,positive=joint,negative=neg,paired_spans=len(pairs),raw_projection_regressions=regressions,source_datasets=list(datasets),list_profiles=len(packets),list_positions=sum(len(p['slots']) for p in packets),input_reads=READS,vault='CLOSED',baseline_modified=False,full_B_C_admission=False,limits=['E2 identity matching alone is not key evidence','C NED/list-arm/fake-refit qualification not run','No actual B/C manuscript labels or real geometry read']))
 print(json.dumps(dict(gates=gates,positive=joint,negative=neg,pairs=len(pairs))),flush=True)
if __name__=='__main__':main()
