from pathlib import Path
import json,hashlib,re,itertools,collections,sys
R=Path(__file__).resolve().parent;P=R.parent;SOURCE=P/'sh-qok-ending-qualification-reed-v94/ROWS.json';ATLAS=P/'complete-atlas-v56/ROWS.json'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Support only. No qok classification, association statistic, permutation p or manuscript effect calculation. H/F separate, bathhand2 and starredhand3 on prior shared source loci.',mapping='Retain qualified eight source zero-based origin positions1,3,5,7,9,11,13,15. Do not pack eligible words or renumber around unknowns. A slot is usable only if literal sh/ch prefix, disjoint ending edy/eey/ey/y, and immediate following token readable in same original source line. Missing/final/unknown slots remain unusable. Following identity never retained or classified.',strata='Physical page and exact original token-slot line length, independently per reading. Variable-length adaptation partitions without pooling; qualification only covered fixed-length synthetic arrays, so this is a support audit not end-to-end qualification.',matching='Enumerate105pairings of8fixedpositions; choose by sum n*(n-1)/2 for identical body in both positions on n lines, ignoring prefix type and following identity. Tie same enumeration as frozen synthetic code. Within each chosen pair/body, discordant sh/ch rows give n,k and V=k*(n-k)/n. Aggregate across length strata to page, then panel.',rule='V>=80, >=8positive-support pages, maxpageV/total<=.25. Zero support notestimable. No alternative position search or pooling of H/F.',verification='Reparse every raw line with atlas cleaning, reconcile rows/metadata/shared-loci, retain tokens null slots and explicit exclusion reasons. Check raw/comment/comma/unknown fixtures and invariance to replacing following readable nonorigin tokens. Save every selected group, page and exclusion.',limits='Eligibility sees following readability only. H/F word boundaries may differ and remain literal. Unknown slots are transcription token slots, not claimed exact glyph-space geometry. Failure applies to this fixed-position exact-body test, not absence of manuscript association.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SOURCE,ATLAS,P/'complete-atlas-v56/build.py',P/'sh-qok-support-boundary/PROTOCOL.json']});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def parse(txt):
 t=re.sub(r'\{[^}]*\}','~',txt.split('#')[0]);t=re.sub(r'[!\s]','',t);t=re.sub(r'([=\-.,])~+$',r'\1',t).rstrip('=-.,');parts=re.split(r'([.,\-=])',t);ws=[]
 for i in range(0,len(parts),2):
  w=parts[i]
  if not w:continue
  comma=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
  ws.append(w if re.fullmatch('[a-z]+',w) and not comma else None)
 return ws
assert parse('sh!edy,chedy.dar-')==[None,None,'dar']
assert parse('shedy.{x}chedy.dar-')==['shedy',None,'dar']
assert parse('shedy.*.chedy= #comment')==['shedy',None,'chedy']
assert parse('shedy.dar-{figure}')==['shedy','dar']
def matches(xs):
 if not xs:yield ();return
 for b in xs[1:]:
  for rest in matches([x for x in xs[1:] if x!=b]):yield ((xs[0],b),)+rest
MATCH=list(matches(list(range(8))));assert len(MATCH)==105
positions=list(range(1,16,2));endings=['edy','eey','ey','y']
def mask(ws):
 out=[];reasons=[]
 for i in positions:
  if i>=len(ws):reason='position_absent'
  elif ws[i] is None:reason='origin_unknown'
  elif i+1>=len(ws):reason='line_final'
  elif ws[i+1] is None:reason='following_unknown'
  elif not ws[i].startswith(('sh','ch')):reason='other_prefix'
  elif not any(ws[i].endswith(e) for e in endings):reason='other_ending'
  else:reason=None
  out.append(None if reason else (ws[i][2:],int(ws[i].startswith('sh'))));reasons.append(reason)
 return out,reasons
assert mask(['a','shedy',None,'chedy','dar'])[0][0] is None
assert mask(['a','shedy','dar'])[0]==mask(['a','shedy','xyz'])[0]
rows=json.loads(SOURCE.read_text());atlas=json.loads(ATLAS.read_text());panels=[('H','Balneological','2'),('F','Balneological','2'),('H','Starred paragraphs','3'),('F','Starred paragraphs','3')];summary=[];groups=[];pages=[];lines=[];verification=[]
for pi,(reading,section,hand) in enumerate(panels):
 rr=rows[str(pi)];lookup={x[8]:x for x in atlas if x[0]==reading and x[2]==section and x[3]==hand and x[4]=='B' and x[5]=='P'}
 assert len({r['locator'] for r in rr})==len(rr)
 strata=collections.defaultdict(list);counts=collections.Counter();outside=0
 for r in rr:
  ws=r['tokens'];assert parse(r['raw'])==ws
  x=lookup[r['locator']];assert (x[1],x[9],x[10])==(r['page'],ws,r['raw'])
  mm,reasons=mask(ws);strata[r['page'],len(ws)].append((r['locator'],mm))
  counts.update(z or 'eligible' for z in reasons)
  outside+=sum(i not in positions and w is not None and w.startswith(('sh','ch')) and any(w.endswith(e) for e in endings) and i+1<len(ws) and ws[i+1] is not None for i,w in enumerate(ws))
  lines.append(dict(panel=pi,reading=reading,locator=r['locator'],page=r['page'],source_length=len(ws),unknown_indices=[i for i,w in enumerate(ws) if w is None],slots=[dict(position=i,body=z[0] if z else None,prefix=('sh' if z[1] else 'ch') if z else None,exclusion=why) for i,z,why in zip(positions,mm,reasons)]))
 pagev={r['page']:0. for r in rr}
 for (page,L),items in sorted(strata.items()):
  scores={}
  for j in range(8):
   for k in range(j+1,8):
    cc=collections.Counter(mm[j][0] for _,mm in items if mm[j] and mm[k] and mm[j][0]==mm[k][0]);scores[j,k]=sum(n*(n-1)//2 for n in cc.values())
  chosen=max(MATCH,key=lambda match:sum(scores[p] for p in match))
  for j,k in chosen:
   dd=collections.defaultdict(list)
   for loc,mm in items:
    if mm[j] and mm[k] and mm[j][0]==mm[k][0] and mm[j][1]!=mm[k][1]:dd[mm[j][0]].append((loc,mm[j][1]))
   for body,entries in dd.items():
    n=len(entries);ns=sum(z[1] for z in entries);v=ns*(n-ns)/n;pagev[page]+=v
    groups.append(dict(panel=pi,reading=reading,page=page,length=L,positions=[positions[j],positions[k]],body=body,n=n,k=ns,V=v,locators=[z[0] for z in entries]))
 total=sum(pagev.values());positive=sum(v>0 for v in pagev.values());share=max(pagev.values())/total if total else None
 summary.append(dict(panel=pi,reading=reading,section=section,hand=hand,lines=len(rr),pages=len(pagev),V=total,supported_pages=positive,max_page_share=share,passes=total>=80 and positive>=8 and share<=.25 if total else False,slot_counts=dict(counts),eligible_origins_outside_frozen_positions=outside))
 pages.extend(dict(panel=pi,reading=reading,page=p,V=v,supported=v>0) for p,v in sorted(pagev.items()))
 verification.append(dict(panel=pi,all_raw_tokens_reparsed=True,all_rows_reconciled_with_atlas=True))
for a,b in [('0','1'),('2','3')]:assert {r['locator'] for r in rows[a]}=={r['locator'] for r in rows[b]}
save('SUMMARY.json',summary);save('GROUPS.json',groups);save('PAGES.json',pages);save('LINE-AUDIT.json',lines)
save('VERIFICATION.json',dict(panels=verification,shared_loci_verified=True,parser_fixtures_pass=True,frozen_hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),outcome_scored=False))
print(json.dumps(summary,indent=2))
