"""Validated source-first controls for the two declared v7.1 fixture tokenizers.
This infrastructure module does not revise a verdict or run a qualification.
"""
import copy,re,sys,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'attempt-2-v7.1/diagnostics'))
from source_control_adapter import make_control,tokenize
RESERVED={'f72v2','f72v1','f73r','f73v'}

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate_source(rows,key,mode):
 ids=[]
 for r in rows:
  if r.get('folio') in RESERVED or r.get('vault'):raise ValueError('reserved source rejected')
  if 'raw_words' not in r or not isinstance(r['raw_words'],list):raise ValueError('registered raw source required')
  ids.append(r['id'])
  for w in r['raw_words']:
   if w is not None and (not isinstance(w,str) or not re.fullmatch('[a-z]+',w)):raise ValueError('unsupported raw glyph representation')
  expected=[tokenize(w,key,mode) for w in r['raw_words']]
  if 'words' in r and r['words']!=expected:raise ValueError('registered source and declared tokenizer disagree')
 if len(ids)!=len(set(ids)):raise ValueError('duplicate source IDs')
 return True

def build_control(rows,key,mode,kind,seed):
 validate_source(rows,key,mode);source_hash=digest(rows);key_hash=digest(key)
 output=make_control(rows,key,mode,kind,seed)
 changes=[];native=0
 for old,new in zip(rows,output):
  if len(old['raw_words'])!=len(new['control_raw_words']):raise AssertionError('word geometry changed')
  for i,(a,b) in enumerate(zip(old['raw_words'],new['control_raw_words'])):
   if a is None:
    native+=1
    if b is not None or new['words'][i] is not None:raise AssertionError('native barrier promoted')
   if kind=='C1-glyph' and a is not None:
    if len(a)!=len(b) or sorted(a)!=sorted(b) or a[0]!=b[0] or a[-1]!=b[-1]:raise AssertionError('position class/multiset changed')
   if a!=b:changes.append({'id':old['id'],'word_index':i,'before':a,'after':b})
 if digest(rows)!=source_hash or digest(key)!=key_hash:raise AssertionError('source/key mutation')
 return output,{'scope':'source-first infrastructure, not a qualification result','mode':mode,'kind':kind,'seed':seed,'key_sha256':key_hash,'source_sha256':source_hash,'control_sha256':digest(output),'native_barriers':native,'changed_raw_words':len(changes),'changes':changes}
