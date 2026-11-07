"""Faithful v4j SlotAlphabet conversion/decomposition adapter (GPL-3.0).

Copyright 2021–2026 Massimiliano Zattera; Python adaptation 2026.
Original pinned Java source and GPL license are retained under raw/mzattera/.
No grammar fitting. Unknown/unstructured words fall back losslessly to raw
characters; coverage denominators include EVERY word, never only valid ones.
"""
import functools,json,re
from common import R as EXT
JAVA=next((EXT/'raw/mzattera').rglob('SlotAlphabet.java'))
SOURCE=JAVA.read_text(encoding='utf-8')
BLOCK=SOURCE.split('public static String fromEva(String txt)')[1].split('public static Set<String> fromEva')[0]
REPLACEMENTS=[(json.loads(a),json.loads(b)) for a,b in re.findall(r'txt = txt\.replace\(("[^"\n]*"), ("[^"\n]*")\);',BLOCK)]
SLOTS=[re.findall(r'p.add\("([^"]+)"\)',block) for block in SOURCE.split('////')[2::2]][:12]
# Parse the actual static initializer rather than silently borrowing a later grammar.
INIT=SOURCE.split('static {',1)[1].split('protected SlotAlphabet',1)[0]
SLOTS=[re.findall(r'p.add\("([^"]+)"\)',b) for b in INIT.split('SLOTS.add(p);')[:-1]]
REGULAR=set(''.join(''.join(s) for s in SLOTS))
REVERSE={'K':'ckh','F':'cfh','T':'cth','P':'cph','C':'ch','S':'sh','B':'eee','E':'ee','U':'iii','J':'ii'}
def from_eva(word):
    for a,b in REPLACEMENTS:word=word.replace(a,b)
    return word
def internal(term):
    rest=term;slots=['']*12;part=''
    for i,choices in enumerate(SLOTS):
        for choice in choices:
            if rest.startswith(choice):slots[i]=choice;part+=choice;rest=rest[len(choice):];break
    for char,start,end in [('y',1,11),('d',0,10),('d',7,10),('r',2,10),('l',2,10),('o',1,8),('d',0,7),('s',0,7)]:
        if slots[start]==char and not any(slots[start+1:end+1]):slots[start]='';slots[end]=char
    return part,rest,slots
@functools.lru_cache(maxsize=300000)
def decompose(word):
    converted=from_eva(word)
    if not converted or any(c not in REGULAR for c in converted):return 'UNREADABLE',[]
    part,rest,slots=internal(converted)
    if not rest:return 'REGULAR',[slots]
    if len(part)>1 and len(rest)>1:
        _,remainder,second=internal(rest)
        if not remainder:return 'SEPARABLE',[slots,second]
    return 'UNSTRUCTURED',[]
@functools.lru_cache(maxsize=300000)
def pieces(word):
    kind,parts=decompose(word)
    if parts:
        items=[(f'S{i}:{c}',REVERSE.get(c,c)) for slots in parts for i,c in enumerate(slots) if c]
        if ''.join(span for _,span in items)==word:return items
    return [('RAW:'+c,c) for c in word]
def tokenize(text):
    result=[]
    for i,w in enumerate(text.split()):
        if i:result.append(' ')
        result.extend(token for token,span in pieces(w))
    return result
