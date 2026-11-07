from pathlib import Path
import importlib.util
import numpy as np
P=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('opening_encoder',P/'opening-order-audit-v75/engine.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def prepare(rows):
 p=base.prepare(rows);left=[];right=[];middle=[];offset=0
 for r in rows:
  ws=r['tokens']
  for i in range(len(ws)-2):
   if all(w is not None for w in ws[i:i+3]):left.append(offset+i);middle.append(offset+i+1);right.append(offset+i+2)
  offset+=len(ws)
 p['li']=np.array(left,dtype=np.int32);p['ri']=np.array(right,dtype=np.int32);p['mi']=np.array(middle,dtype=np.int32)
 p['target_middle']=np.array([w.startswith(('sh','qok')) for w in p['words']],dtype=bool)
 return p
def count(arr,p,neutral=False):
 if not neutral:return base.count(arr,p)
 keep=~p['target_middle'][arr[p['mi']]];q=dict(p,li=p['li'][keep],ri=p['ri'][keep]);return base.count(arr,q)
def run(rows,B,seed,progress=None):
 p=prepare(rows);rng=np.random.default_rng(seed);scores={mode:np.empty((B+1,len(p['ia'])),dtype=np.int16) for mode in ['any_middle','non_target_middle']};cells={}
 for mode in scores:cells[mode],scores[mode][0]=count(p['original'],p,mode=='non_target_middle')
 for b in range(1,B+1):
  arr=p['original'].copy()
  for indices in p['buckets']:arr[indices]=rng.permutation(arr[indices])
  for mode in scores:
   _,v=count(arr,p,mode=='non_target_middle');assert np.max(np.abs(v),initial=0)<=32767;scores[mode][b]=v
  if progress and b%1000==0:progress(b)
 a=p['labels'].index('prefix:sh');z=p['labels'].index('prefix:qok');lo,hi=sorted((a,z));column=int(np.flatnonzero((p['ia']==lo)&(p['ib']==hi))[0]);sign=1 if a<z else -1
 return p,scores,{mode:dict(forward=int(c[a,z]),reverse=int(c[z,a])) for mode,c in cells.items()},column,sign
