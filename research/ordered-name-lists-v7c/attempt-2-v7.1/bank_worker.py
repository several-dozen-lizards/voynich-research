"""Process-local evaluator with read-only inputs; original score definitions."""
import json,random,sys,functools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'HARNESS'))
import harness as h
# Equivalent memoization only: repeated decoded word/lexicon queries reuse exact NED result.
class CachedProcess:
 @staticmethod
 @functools.lru_cache(maxsize=100000)
 def find(w,lex):return h_original.extractOne(w,lex,scorer=h.Levenshtein.normalized_distance,score_cutoff=.25)
 @staticmethod
 def extractOne(w,lex,**kwargs):return CachedProcess.find(w,tuple(lex))
h_original=h.process
h.process=CachedProcess
CTX=None

def init(context):
 global CTX
 CTX=context

def score_one(item):
 i,key=item
 s=h.raw_scores(key,CTX['train'],CTX['held'],CTX['target'],CTX['lexicons'])
 return {'index':i,'key_sha256':h.digest(key),'scores':s}
