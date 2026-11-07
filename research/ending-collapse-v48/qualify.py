from pathlib import Path
import json,re,hashlib,random,math,collections
R=Path(__file__).resolve().parent
B=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40')
def sources():
 p=B/'voynich-encoding-v27/sources/Secreta_Secretorum_LAT';w=re.findall('[a-z]+',p.read_text(encoding='utf8').lower());lines=[w[i:i+50] for i in range(0,len(w),50)];cut=int(.6*len(lines))
 out={'Latin':[(('train' if i<cut else 'test'),l) for i,l in enumerate(lines)]}
 p2=B/'voynich-casebooks-v46/RECORDS.json';rows=json.loads(p2.read_text(encoding='utf8'))
 for r in rows:
  for line in r['lines']:
   segment=[]
   for x in line+['|']:
    if x=='|':
     if len(segment)>1:out.setdefault(r['stratum'],[]).append((r['split'],segment))
     segment=[]
    else:segment.append(x)
 return out,{str(p):hashlib.sha256(p.read_bytes()).hexdigest(),str(p2):hashlib.sha256(p2.read_bytes()).hexdigest()}
def events(lines,arm,seed):
 rng=random.Random(seed);out=[]
 for split,l in lines:
  for i in range(len(l)-1):
   bit=rng.randrange(2) if arm=='redundant' else int(hashlib.sha256(l[i+1].encode()).hexdigest()[-1],16)%2 if arm=='informative' else int(i==len(l)-2)
   out.append((split,(l[i],bit),l[i+1]))
 return out
def score(ev,mapping):
 tr=[e for e in ev if e[0]=='train'];te=[e for e in ev if e[0]=='test'];tc=collections.Counter(y for _,x,y in tr);vocab={y for y,n in tc.items() if n>=3};canon=lambda y:y if y in vocab else '<UNK>'
 prior=collections.Counter(canon(y) for _,x,y in tr);V=len(vocab)+1;N=sum(prior.values());counts=collections.defaultdict(collections.Counter)
 for _,x,y in tr:counts[mapping(x)][canon(y)]+=1
 loss=0
 for _,x,y in te:
  y=canon(y);c=counts.get(mapping(x),{});p=(prior[y]+1)/(N+V);loss-=math.log2((c.get(y,0)+10*p)/(sum(c.values())+10))
 return loss/max(1,len(te))
def main():
 f=json.loads((R/'FREEZE.json').read_text(encoding='utf-8-sig'))
 for n,h in f.items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 data,hashes=sources();results=[]
 for name,lines in data.items():
  for seed in range(4801,4806):
   for arm in ['redundant','informative','layout']:
    ev=events(lines,arm,seed);raw=score(ev,lambda x:x);merged=score(ev,lambda x:x[0]);counts=collections.Counter(x for sp,x,y in ev if sp=='train');types=sorted(counts,key=lambda x:(counts[x],x));null=[]
    for j in range(19):
     rng=random.Random(seed*100+j);mapping={}
     for start in range(0,len(types),40):
      block=types[start:start+40].copy();rng.shuffle(block)
      for i,x in enumerate(block):mapping[x]=('null',start+i//2)
     null.append(raw-score(ev,lambda x:mapping.get(x,('unseen',x))))
    gain=raw-merged;threshold=sorted(null)[-1];accept=gain>0 and gain>threshold
    results.append(dict(source=name,seed=seed,arm=arm,test_transitions=sum(e[0]=='test' for e in ev),raw_loss=raw,collapse_loss=merged,gain_bits=gain,arbitrary_gains=null,accepted=accept))
 summary={name:{arm:sum(r['accepted'] for r in results if r['source']==name and r['arm']==arm) for arm in ['redundant','informative','layout']} for name in data}
 passed=all(v['redundant']>=4 and v['informative']==0 for v in summary.values())
 (R/'RESULTS.json').write_text(json.dumps(dict(source_hashes=hashes,results=results,summary=summary,initial_gate_pass=passed,manuscript_collapse='NOT RUN'),indent=2),encoding='utf8');print(json.dumps(summary,indent=2));print('initial_gate_pass',passed)
if __name__=='__main__':main()
