from pathlib import Path
import sys,json,csv,hashlib,ast,collections,functools,math,re
from datetime import datetime,timezone
import numpy as np
R=Path(__file__).resolve().parent; P=R.parent
sys.path.insert(0,str(P/'sh-qok-single-target-attempt-c'))
import engine as e
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def seal(phase,names):
 with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),hashes={n:sha(R/n) for n in names}))+'\n')
def load(p,names,env):
 exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),env)
def context(m,pg):
 h,s=m['Scribe'],m['Section']
 if (h,s)==('2','Balneological'):return 'C1'
 if (h,s)==('2','Botanical'):return 'C2'
 if h=='2' and s.startswith('Rose'):return 'C3'
 if (h,s)==('3','Starred paragraphs'):return 'C4'
 if h=='3' and (s=='Botanical' or pg in ('f73r','f73v')):return 'C5'
 if (h,s)==('1','Botanical'):return 'C6'
 if (h,s)==('1','Recipes'):return 'C7'
 if (h,s) in [('4','Astronomy'),('5','Botanical')]:return 'C8-'+h
 return None
def main():
 assert not (R/'PROTOCOL.json').exists()
 original=Path(r'C:\Users\lewis\.codex\attachments\1281d8eb-159f-423a-bc11-6a0ea07f17bf\Pasted text.txt')
 (R/'ORIGINAL-SPEC.txt').write_bytes(original.read_bytes())
 prior=json.loads((P/'sh-qok-single-target-attempt-c/PROTOCOL.json').read_text())
 sources=prior['sources'];assert all(sha(p)==h for p,h in sources.items())
 save('PROTOCOL.json',dict(status='FROZEN ORIGINAL; ENGINE DISTINCTION PENDING CLARIFICATION',spec=original.read_text(encoding='utf-8'),original_sha256=sha(original),sources=sources,implementation_note='Coverage replay and masked support only. No outcome inference. Existing paired W engine uses its unchanged first-position and ending restrictions; attempt C coverage includes first positions and other endings. These populations must not be conflated.'))
 seal('original_preserved',['PROTOCOL.json','ORIGINAL-SPEC.txt','preflight.py'])
 source=next(Path(p) for p in sources if 'text16e6' in p);meta=next(Path(p) for p in sources if 'Davis-hands' in p)
 metadata={r['Folio']:r for r in csv.DictReader(meta.open(encoding='utf-8-sig'))}
 lines=list(e.parse(source,metadata));masked,ex,_=e.extract(lines,False)
 old=json.loads((P/'sh-qok-single-target-attempt-c/SUPPORT.json').read_text());checks={}
 for co in ['H','F']:
  cell='P1-'+co;got=e.support([v for v in masked if v['cell']==cell]);got['exclusions']=dict(ex.get(cell,{}))
  keys=['eligible_origins','sh','ch','supported_strata','supported_pages','V','max_page_share','page_support','strata','exclusions']
  differences={k:dict(expected=old[cell][k],actual=got[k]) for k in keys if old[cell][k]!=got[k]}
  checks[cell]=dict(match=not differences,counts={k:got[k] for k in ['eligible_origins','sh','ch','exclusions']},differences=differences)
 save('COVERAGE-REPLAY.json',dict(status='PASS' if all(x['match'] for x in checks.values()) else 'STOP',checks=checks,tokenizer_sha256=sha(P/'sh-qok-single-target-attempt-c/engine.py')))
 seal('coverage_replayed',['COVERAGE-REPLAY.json'])
 assert all(x['match'] for x in checks.values()),checks
 # Only selected P units are tokenized. Zodiac contexts are filtered by metadata before tokenization.
 selected=[];seen=set()
 for raw in source.read_text(encoding='latin1').splitlines():
  m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',raw)
  if not m:continue
  pg,place,num,co,text=m.groups()
  if co not in ('H','F') or not place.startswith('P') or pg not in metadata:continue
  c=context(metadata[pg],pg)
  if not c:continue
  key=(co,pg,place,num);assert key not in seen;seen.add(key)
  selected.append(dict(panel=c,context=c,reading=co,folio=pg,line=f'{pg}.{place}.{num}',hand=metadata[pg]['Scribe'],section=metadata[pg]['Section'],tokens=e.tokens(text)))
 # Import unchanged selection/matching functions, with outcome reads removed from event extraction.
 env=dict(collections=collections,functools=functools)
 load(P/'sh-qok-all-interior/run.py',['matching'],env)
 def blind_events(ws):
  return {i:(w[2:],int(w.startswith('sh')),None) for i,w in enumerate(ws) if 0<i<len(ws)-1 and w and ws[i+1] and w.startswith(('sh','ch')) and any(w.endswith(s) for s in ['edy','eey','ey','y'])}
 env['events']=blind_events
 matched=dict(collections=collections,env=env)
 load(P/'sh-qok-matched-effect/run.py',['extract'],matched)
 p1=set(json.loads((P/'sh-qok-single-target-attempt-c/PANELS.json').read_text())['declared_folios']['P1'])
 support={};designs={};availability=[]
 for co in ['H','F']:
  for cell,cs in [('A-P1',None),('A-bath',['C1']),('A-starred',['C4'])]:
   ll=[l for l in selected if l['reading']==co and (l['folio'] in p1 if cs is None else l['context'] in cs)]
   rows=[(l['folio'],l['tokens']) for l in ll];gg=matched['extract'](rows);groups=[];pages=collections.defaultdict(float)
   for _,entries in gg:
    patterns=collections.defaultdict(list)
    for ri,j,k,left in entries:
     pattern=tuple(int(not rows[ri][1][pos+1].startswith(('ch','sh','cth','ckh','cph','cfh'))) for pos in (j,k))
     patterns[pattern].append(dict(line=ll[ri]['line'],positions=[j,k],left=left))
    for pat,items in patterns.items():
     n=len(items);k=sum(i['left'] for i in items);pg=ll[next(ri for ri,j,pos,left in entries)]['folio'];w=k*(n-k)/n*sum(pat);pages[pg]+=w
     groups.append(dict(page=pg,pattern=pat,items=items,W=w))
   W=sum(pages.values());n=sum(v>0 for v in pages.values());share=max(pages.values(),default=0)/W if W else None
   support[cell+'-'+co]=dict(W=W,pages=n,max_page_share=share,gate=bool(W>=160 and n>=8 and share<=.25),page_support=dict(pages),selected_exact_body_groups=len(gg),availability_pattern_groups=len(groups),event_population='Unchanged paired engine scoring subset; not all attempt-C origins')
   designs[cell+'-'+co]=groups
  for c in ['C'+str(i) for i in range(1,8)]+['C8-4','C8-5']:
   ll=[l for l in selected if l['reading']==co and l['context']==c];ev,xx,_=e.extract(ll,False)
   support[c+'-'+co]=e.support(ev)|dict(exclusions={k:dict(v) for k,v in xx.items()},covered_pages=sorted({l['folio'] for l in ll}))
  ll=[l for l in selected if l['reading']==co and l['context'] in ['C6','C7']];ev,xx,_=e.extract(ll,False)
  support['B-Q1-'+co]=e.support(ev)
 for l in selected:
  ev,_,_=e.extract([l],False)
  for v in ev:
   follower=l['tokens'][v['position']+1];av=not follower.startswith(('ch','sh','cth','ckh','cph','cfh'))
   availability.append(dict(reading=l['reading'],context=l['context'],folio=l['folio'],line=l['line'],position=v['position'],available=av,strict_available=follower.startswith(('q','o','d','y','a'))))
 save('SUPPORT.json',support);save('MASKED-PAIRS.json',designs);save('AVAILABILITY.json',dict(outcomes_used=False,rule='not ch/sh/cth/ckh/cph/cfh',events=availability))
 seal('support_frozen',['SUPPORT.json','MASKED-PAIRS.json','AVAILABILITY.json'])
 print(json.dumps({k:{f:v[f] for f in ['W','V','pages','supported_pages','max_page_share','gate'] if f in v} for k,v in support.items()},indent=2))
if __name__=='__main__':main()
