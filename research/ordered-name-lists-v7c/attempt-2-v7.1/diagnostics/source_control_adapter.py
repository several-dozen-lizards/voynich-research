"""Source-level C1 adapters prepared AFTER attempt2; not used to rescore it.
Shuffle raw characters/words first, then apply the declared tokenizer unchanged.
These adapters cover the two tokenizer modes used in the attempt2 fixtures.
"""
import copy,random

def tokenize(raw,key,mode):
 if raw is None:return None
 if mode=='known_initial_a':
  units=[('INIT_A' if i==0 and c=='a' else 'u'+c) for i,c in enumerate(raw)]
 elif mode=='training_whole_word':
  units=['WORD:'+raw] if 'WORD:'+raw in key['units'] else list(raw)
 else:raise ValueError('tokenizer mode not qualified by this adapter')
 return units if all(u in key['map'] for u in units) else None

def make_control(raw_records,key,mode,kind,seed):
 if kind not in ('C1-word','C1-glyph'):raise ValueError('source control kind')
 rng=random.Random(seed);out=copy.deepcopy(raw_records)
 for record in out:
  if 'raw_words' not in record:raise ValueError('original raw source words required')
  words=list(record['raw_words'])
  if kind=='C1-glyph':
   for i,w in enumerate(words):
    if w is not None and len(w)>2:
     mid=list(w[1:-1]);rng.shuffle(mid);words[i]=w[0]+''.join(mid)+w[-1]
  else:
   start=0
   for stop in range(len(words)+1):
    if stop==len(words) or words[stop] is None:
     chunk=words[start:stop];rng.shuffle(chunk);words[start:stop]=chunk;start=stop+1
  record['control_raw_words']=words
  record['words']=[tokenize(w,key,mode) for w in words]
 return out
