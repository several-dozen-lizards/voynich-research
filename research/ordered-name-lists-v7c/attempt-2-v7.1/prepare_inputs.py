import sys,json,re,hashlib,math,random
from pathlib import Path
P=Path(__file__).parent;ROOT=P.parent.parent;V5=ROOT/'system-types-v5'
sys.path.insert(0,str(V5));sys.path.insert(0,str(P.parent/'HARNESS/vendor'))
from core import load_evt,EXPECTED_EVT,EXPECTED_HANDS
from sandbox import DATA
from rapidfuzz.distance import Levenshtein

def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows,manifest=load_evt(DATA/'text16e6.original.evt',DATA/'Davis-hands.original.csv')
rows=[r for r in rows if not 67<=int(re.match(r'f(\d+)',r['folio'])[1])<=73]
assert not any(r['folio'] in ('f72v1','f72v2','f73r','f73v') for r in rows)
by={}
for r in rows:by.setdefault(r['locus'],{})[r['reading']]=r
edits=den=paired=unequal=unknown=0
for loc,rr in by.items():
 if set(rr)!=set(('H','F')):continue
 h,f=rr['H']['tokens'],rr['F']['tokens']
 if len(h)!=len(f):unequal+=1;continue
 for x,y in zip(h,f):
  if x is None or y is None:unknown+=1;continue
  paired+=1;edits+=Levenshtein.distance(x,y);den+=max(len(x),len(y))
assert den and 0<edits/den<1
receipt={'status':'OBSERVED_NONZODIAC_PARAGRAPH_DISAGREEMENT','source_manifest':manifest,'policy':'only equal original slot counts at shared H/F paragraph loci; paired readable tokens; no zodiac folios67–73','paired_tokens':paired,'edit_count':edits,'max_length_denominator':den,'rate':edits/den,'unequal_slot_count_lines_excluded':unequal,'unknown_pairs_excluded':unknown,'caveat':'disagreement is not a measured error probability; no boundary-error channel inferred'}
save('HF-DISAGREEMENT.json',receipt)
# Persist only the preregistered actual-trap slices; no reserved source forms retained.
folios=sorted(set(r['folio'] for r in rows),key=lambda x:(int(re.match(r'f(\d+)',x)[1]),x))[:16]
slices={}
for reading in ('H','F'):
 slices[reading]={part:[r for r in rows if r['reading']==reading and r['folio'] in ff][:40] for part,ff in [('train',folios[:8]),('held',folios[8:])]}
save('TRAP-SLICES.json',{'folios':{'train':folios[:8],'held':folios[8:]},'readings':slices,'source_manifest':manifest})
print(json.dumps({'HF_rate':edits/den,'paired_tokens':paired,'trap_sizes':{r:{p:len(x) for p,x in z.items()} for r,z in slices.items()}}))
