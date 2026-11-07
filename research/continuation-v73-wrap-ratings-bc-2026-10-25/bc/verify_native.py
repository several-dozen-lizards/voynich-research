import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,random,hashlib,time
P=Path(__file__).parent;ROOT=P.parents[1];sys.path.insert(0,str(P/'native-rapidfuzz-3.14.1'))
import rapidfuzz
from rapidfuzz import process as native_process,process_py as pure_process
from rapidfuzz.distance import Levenshtein as native_lev,Levenshtein_py as pure_lev
assert rapidfuzz.__version__=='3.14.1' and 'cpp' in native_process.extractOne.__module__ and 'cpp' in native_lev.normalized_distance.__module__
checks=0;rng=random.Random(90263);cases=[('',''),('a',''),('abcd','abce'),('abcd','abxy'),('a'*64,'a'*63+'b')]
for i in range(2000):cases.append((''.join(rng.choices('abcdefghijklmnopqrstuvwxyz',k=rng.randrange(81))),''.join(rng.choices('abcdefghijklmnopqrstuvwxyz',k=rng.randrange(81)))))
for a,b in cases:
 for cutoff in (None,.25,.5,1):assert native_lev.normalized_distance(a,b,score_cutoff=cutoff)==pure_lev.normalized_distance(a,b,score_cutoff=cutoff);checks+=1
for i in range(100):
 choices=[''.join(rng.choices('abcde',k=rng.randrange(1,14))) for _ in range(32)];word=choices[0] if i%3==0 else ''.join(rng.choices('abcde',k=8));assert native_process.extractOne(word,choices,scorer=native_lev.normalized_distance,score_cutoff=.25)==pure_process.extractOne(word,choices,scorer=pure_lev.normalized_distance,score_cutoff=.25);checks+=1
A=ROOT/'ordered-name-lists-v7c/attempt-3-v7.2';sys.path.insert(0,str(A));sys.path.insert(0,str(A.parent/'HARNESS'))
import harness as h,worker_v72 as w
from source_first_controls import tokenize
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
data=read(A/'KNOWN-DATA.json');key=read(A/'KNOWN-KEY.json');keys=[key,h.random_key(key,random.Random(714))];contexts=[('real',data['held']),('C1-glyph',read(A/'CLEAN-C1-glyph-INPUT.json')['records'])]
for fam in ('G1','G5'):
 native=read(A/('controls/CLEAN-'+fam+'.json'));flat=[word for r in native for word in r['raw_words']];offset=0;rows=[]
 for base in data['held']:
  raw=[flat[(offset+i)%len(flat)] for i in range(len(base['words']))];offset+=len(raw);rows.append(dict(base,raw_words=raw,words=[tokenize(word,key,'known_initial_a') for word in raw]))
 contexts.append((fam,rows))
replays=[];begin=time.time()
for name,held in contexts:
 ctx=dict(train=data['train'],held=held,target=data['target'],lexicons=data['lexicons'],alphabet=key['target']['alphabet'])
 for i,k in enumerate(keys):
  w.OriginalProcess=pure_process;h.Levenshtein=pure_lev;w.init(ctx);pure=w.score_one((i,k))['scores']
  w.OriginalProcess=native_process;h.Levenshtein=native_lev;w.init(ctx);native=w.score_one((i,k))['scores']
  assert pure==native,(name,i);replays.append(dict(context=name,key=i,exact_equal=True))
receipt=read(P/'NATIVE-ACQUISITION.json');assert all(v['same'] for v in receipt['pure_source_comparison'].values())
out=dict(status='EXACT_ACCELERATOR_VERIFIED',version=rapidfuzz.__version__,atomic_checks=checks,raw_score_replays=replays,pure_source_files_identical_to_baseline=True,backend=native_lev.normalized_distance.__module__,seconds=time.time()-begin,method_change=False)
(P/'NATIVE-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
