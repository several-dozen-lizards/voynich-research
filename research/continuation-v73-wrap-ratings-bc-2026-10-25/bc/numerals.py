import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json,math,hashlib
from fractions import Fraction
import numpy as np
P=Path(__file__).parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'));import harness as h
s=importlib.util.spec_from_file_location('old_control',ROOT/'bc-adapter-qualification-2026-10-25/attempt-2/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.a
book={str(i):'a'+chr(97+i) for i in range(10)};key=dict(map={v:k for k,v in book.items()},rules=[],units=list(book.values()))
def seed(*p):return int.from_bytes(hashlib.sha256(':'.join(map(str,p)).encode()).digest()[:8],'big')
def source(v):return None if v<0 else [str(v)] if v<10 else [str(10*(v//10)),str(v%10)]
def decode(raw,reading):
 records=[]
 for i,label in enumerate(raw):records.append(dict(id=str(i),folio='synthetic-numeral',reading=reading,words=[None] if label is None else [a.tokenize_unique(''.join(book[c] for c in w),key['units']) for w in label]))
 out=[]
 for i,label in enumerate(raw):
  locs=[[str(i),j] for j in range(len(records[i]['words']))];whole=a.decode_span(records,locs,key,h.decode_word)
  if label is None:
   assert whole is None;assert not a.numeric_check([whole],'sum','0');out.append(-1)
  else:
   assert whole==' '.join(label)
   values=[h.decode_word(w,key) for w in records[i]['words']];n=sum((a.exact_number(v) for v in values),Fraction());assert n.denominator==1;assert a.numeric_check(values,'sum',str(n));out.append(int(n))
 return np.array(out)

def main():
 plan=json.loads((P/'NUMERAL-FREEZE.json').read_text());details=[];summary={};checks=0
 for lengths in plan['geometries']:
  g=m.Geometry(lengths);N=g.n;target=np.arange(1,N+1)
  for scenario in ('positive','source-permutation-null'):
   for reading,noise in [('H',.1),('F',.2)]:
    rows=[]
    for trial in range(200):
     rng=np.random.default_rng(seed(plan['seed'],lengths,scenario,trial));values=np.empty(N,dtype=int);values[g.A[int(rng.integers(len(g.A)))]]=target
     if scenario!='positive':
      for band in g.bands:values[band]=values[band][rng.permutation(len(band))]
     mask=np.random.default_rng(seed(plan['seed'],'mask',lengths,scenario,reading,trial)).random(N)<noise;values[mask]=-1
     raw=[source(int(v)) for v in values];observed_values=decode(raw,reading);assert np.array_equal(values,observed_values);checks+=1
     rr=np.random.default_rng(seed(plan['seed'],'null',lengths,scenario,reading,trial));indices=np.broadcast_to(np.arange(N),(1000,N)).copy()
     for band in g.bands:indices[:,band]=band[np.argsort(rr.random((1000,len(band))),axis=1)]
     # Explicit source-label permutations. Exact cached decode commutes with moving whole labels.
     null_values=values[indices]
     for b in (0,999):assert np.array_equal(decode([raw[i] for i in indices[b]],reading),null_values[b]);checks+=1
     obs=g.oracle(observed_values,target);null=g.score(null_values,target);p=m.pvalue(obs,null);row=dict(geometry=lengths,reading=reading,scenario=scenario,trial=trial,correct=obs,n=N,p=p,flag=p<=.01);rows.append(row);details.append(row)
    name=f'{lengths}:{reading}:{scenario}';summary[name]=m.summarize(rows,positive=scenario=='positive');print(name,summary[name],flush=True)
 out=dict(status='NUMERAL_SOURCE_FIRST_BRIDGE_QUALIFIED_ON_DECLARED_SCOPE' if all(v['gate'] for v in summary.values()) else 'NUMERAL_SOURCE_FIRST_BRIDGE_NOT_QUALIFIED',cells=summary,trials=len(details),source_panel_replays=checks,declined_geometry=plan['declined_geometry'],vault='CLOSED',full_B_C_admission=False)
 (P/'NUMERAL-TRIALS.json').write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8');(P/'NUMERAL-QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
