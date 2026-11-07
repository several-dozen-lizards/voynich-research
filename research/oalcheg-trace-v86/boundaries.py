from pathlib import Path
import json, hashlib, re, sys
R=Path(__file__).resolve().parent;S=R.parent/'complete-atlas-v56/ROWS.json'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def groups(w):return re.findall('cth|ckh|cph|cfh|ch|sh|.',w)
def d(a,b):
 v=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  q=[i]
  for j,y in enumerate(b,1):q.append(min(q[-1]+1,v[j]+1,v[j-1]+(x!=y)))
  v=q
 return v[-1]
if sys.argv[1]=='freeze':
 save('BOUNDARY-PROTOCOL.json',dict(reason='Supplement after f39r C okal.cheg was observed; not part of original whole-token search.',rule='Every contiguous sequence of at least2 fully readable tokens within one source row, stopping at null barriers. Join without changing characters, search exact/one-edit in either same EVA/group view. No cross-row joins. Length limited only by necessary edit-distance bounds (<=8 characters OR <=7 groups); longer sequences stop because neither length can shrink. This is a diagnostic of source segmentation, not evidence spaces should be removed.',limits='Broad two-edit token net unchanged. Split/multiword matches remain separate and never counted as single-word attestations. No historical fitting.'))
 save('BOUNDARY-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'BOUNDARY-PROTOCOL.json',S]});print('Boundary diagnostic frozen.')
else:
 for p,h in json.loads((R/'BOUNDARY-FREEZE.json').read_text()).items():assert sha(Path(p))==h
 target='oalcheg';tg=groups(target);out=[]
 for x in json.loads(S.read_text()):
  for i,w in enumerate(x[9]):
   if w is None:continue
   joined=w
   for j in range(i+1,len(x[9])):
    if x[9][j] is None:break
    joined+=x[9][j];g=groups(joined)
    if len(joined)>8 and len(g)>7:break
    cd=d(target,joined) if abs(7-len(joined))<=1 else 99
    gd=d(tg,g) if abs(6-len(g))<=1 else 99
    if min(cd,gd)<=1:out.append(dict(reading=x[0],page=x[1],section=x[2],locator=x[8],token_indices=[i,j],tokens=x[9][i:j+1],joined=joined,character_distance=cd if cd!=99 else None,group_distance=gd if gd!=99 else None,raw=x[10]))
 save('MULTIWORD-NEAR-HITS.json',out);print(json.dumps(out,indent=2))
