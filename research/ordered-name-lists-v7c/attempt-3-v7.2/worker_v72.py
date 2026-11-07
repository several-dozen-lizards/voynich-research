"""Exact-score acceleration only; original raw E1–E6 definitions retained."""
import sys,math
from pathlib import Path
from collections import defaultdict
from functools import lru_cache
sys.path.insert(0,str(Path(__file__).parent.parent/'HARNESS'))
import harness as h
OriginalLM=h.LM
OriginalProcess=h.process
CTX=None;TARGET_LM=None;CURRENT_KEY=None;RULES=None;LEX={}

class FastLM(OriginalLM):
 def __init__(self,records,alphabet,order=2,smoothing=.5):
  super().__init__(records,alphabet,order,smoothing);self.den={ctx:sum(row.values())+self.a*len(self.alphabet) for ctx,row in self.c.items()};self.logs={}
 def loss(self,records):
  total=0.;n=0;invalid=False
  for words in records:
   if any(w is None for w in words):invalid=True
   for text in h.segments(words):
    ctx='^'*self.order
    for ch in text:
     if ch not in self.alphabet:return None,n,'out-of-target-alphabet'
     token=(ctx,ch)
     if token not in self.logs:
      row=self.c[ctx];p=(row[ch]+self.a)/self.den.get(ctx,self.a*len(self.alphabet));self.logs[token]=-math.log2(p)
     total+=self.logs[token];n+=1;ctx=(ctx+ch)[-self.order:]
  if invalid:return None,n,'ambiguous-or-unknown-token'
  return (total/n if n else None),n,None if n else 'no-characters'

def lm_factory(records,alphabet,order=2,smoothing=.5):
 if records is CTX['target']:return TARGET_LM
 return FastLM(records,alphabet,order,smoothing)

@lru_cache(maxsize=10000)
def decoded(word,section):
 if not word:return None
 out=[]
 for i,u in enumerate(word):
  if u not in CURRENT_KEY['map']:return None
  pos='single' if len(word)==1 else 'first' if i==0 else 'last' if i==len(word)-1 else 'interior'
  ctx={'position':pos,'left':word[i-1] if i else '^','right':word[i+1] if i+1<len(word) else '$','section':section}
  values={r['value'] for r in RULES[u] if all(ctx.get(a)==b for a,b in r['when'].items())}
  if len(values)>1:return None
  out.append(next(iter(values)) if values else CURRENT_KEY['map'][u])
 return ''.join(out)

def decode_record(record,key):
 global CURRENT_KEY,RULES
 if key is not CURRENT_KEY:
  CURRENT_KEY=key;RULES=defaultdict(list)
  for r in key['rules']:RULES[r['unit']].append(r)
  decoded.cache_clear()
 return [decoded(tuple(w) if w is not None else None,record.get('section','')) for w in record['words']]

@lru_cache(maxsize=250000)
def lookup(word,lexid):return OriginalProcess.extractOne(word,LEX[lexid],scorer=h.Levenshtein.normalized_distance,score_cutoff=.25)
class CachedProcess:
 @staticmethod
 def extractOne(word,lex,**kwargs):
  LEX[id(lex)]=lex;return lookup(word,id(lex))

def init(context):
 global CTX,TARGET_LM,CURRENT_KEY
 CTX=context;CURRENT_KEY=None;lookup.cache_clear();decoded.cache_clear();LEX.clear();TARGET_LM=FastLM(context['target'],context['alphabet'])
 h.LM=lm_factory;h.decode_record=decode_record;h.process=CachedProcess

def score_one(item):
 index,key=item
 return {'index':index,'key_sha256':h.digest(key),'scores':h.raw_scores(key,CTX['train'],CTX['held'],CTX['target'],CTX['lexicons'])}
