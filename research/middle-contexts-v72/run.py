from pathlib import Path
import collections,hashlib,itertools,json,re
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
paths=[P/'frequency-atlas-v48/rows.json',P/'category-extension-v61/RESULTS.json',P/'shared-frame-null-v69/RESULTS.json']
protocol={
 'scope':'Primary same bath section/hand2/CurrierB/rawP stratum; exclude original numbered folio f75, and restrict to H/F shared eligible source loci. No pooling readings, hands, varieties or formats.',
 'exclusion':'For each target occurrence ol/qokedy/qol, exclude it if its immediately adjacent readable source tokens are shedy on BOTH sides. Do not delete tokens, join gaps or exclude the rest of its line. Unknowns and source-line edges remain explicit.',
 'profiles':'Every retained target occurrence: first/interior/last/single position, exact ordinal, left/right exact word with counts and numbered-folio support. Separate all-position and interior-only profiles, so endpoints do not drive neighbour comparisons. Show counts, not semantic scores or significance.',
 'comparisons':'By each side, enumerate every neighbour shared by each target pair or all three; flag if each involved target has that neighbour across>=2 numbered folios. Enumerate every other exact flank frame shared by >=2 targets; flag if each involved target recurs across>=2folios. Preserve weak/singleton/single-folio frames and nonoverlapping neighbours. Full event passages saved.',
 'positions':'Compare target position proportions and all eligible readable token baseline, including the same frame-center exclusion for the baseline. Also show per-folio profiles, not just pooled-token counts. Source-line positions are not independently established grammatical or record positions.',
 'cross_stratum_inventory':'Separate descriptive appendix of every original section/hand/variety/raw-format stratum on shared H/F source loci containing any target outside the excluded frame. Global f75 exclusion retained. Show zero/absent targets; do not aggregate or rank roles across strata. Primary event analyses remain bath only.',
 'limits':'Already inspected material, no untouched validation. Fixed targets, no newly assigned meanings. Shared contexts do not establish interchangeability or parts of speech; different counts/contexts do not establish different semantic roles. Frequencies, word length and spelling may explain differences. No new null or significance test.'}
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};freeze['run.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
rows=load(paths[0]);prior=next(g for g in load(paths[1])['groups'] if g['id']=='bath');targets=['ol','qokedy','qol']
def fol(r):return re.match(r'f\d+',r[1])[0]
def pos(i,n):return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def counter(xs):return dict(collections.Counter(xs).most_common())
def valid(x):return x not in ('#EDGE','#UNKNOWN')
def rec(es):return dict(count=len(es),folios=len({e['folio'] for e in es}),locators=sorted({e['locator'] for e in es}))
allbase=[r for r in rows if fol(r) not in prior['excluded_folios']]
def sharedrows(base):
 loci={tr:{r[6] for r in base if r[0]==tr} for tr in ['H','F']};common=loci['H']&loci['F'];return [r for r in base if r[6] in common]
primary=sharedrows([r for r in allbase if tuple(r[2:6])==('Balneological','2','B','P')])

def occurrence(r,i):
 ws=r[7];return dict(page=r[1],folio=fol(r),locator=r[6],ordinal=i+1,position=pos(i,len(ws)),line_length=len(ws),left=(ws[i-1] or '#UNKNOWN') if i else '#EDGE',right=(ws[i+1] or '#UNKNOWN') if i+1<len(ws) else '#EDGE',tokens=ws)

readings={}
for tr in ['H','F']:
 rs=[r for r in primary if r[0]==tr];profiles={};baseline=[]
 for r in rs:
  for i,w in enumerate(r[7]):
   if w is None:continue
   e=occurrence(r,i)
   if not(e['left']==e['right']=='shedy'):baseline.append(e)
 for w in targets:
  kept=[];removed=[]
  for r in rs:
   for i,v in enumerate(r[7]):
    if v!=w:continue
    e=occurrence(r,i);(removed if e['left']==e['right']=='shedy' else kept).append(e)
  profiles[w]=dict(total_before_exclusion=len(kept)+len(removed),excluded_frame_centers=removed,retained=len(kept),folios=len({e['folio'] for e in kept}),positions=counter(e['position'] for e in kept),ordinals=counter(e['ordinal'] for e in kept),events=kept,
   folio_profiles={f:dict(count=len(es),positions=counter(e['position'] for e in es)) for f in sorted({e['folio'] for e in kept}) for es in [[e for e in kept if e['folio']==f]]})
  for scope in ['all_positions','interior_only']:
   ev=[e for e in kept if scope=='all_positions' or e['position']=='interior'];side_profiles={}
   for side in ['left','right']:
    by=collections.defaultdict(list)
    for e in ev:by[e[side]].append(e)
    side_profiles[side]=dict(known=[dict(word=n,**rec(es)) for n,es in sorted(by.items(),key=lambda kv:(-len(kv[1]),kv[0])) if valid(n)],unknown_or_edge={n:len(es) for n,es in by.items() if not valid(n)})
   profiles[w][scope]=dict(events=len(ev),sides=side_profiles)
 comparisons={}
 for scope in ['all_positions','interior_only']:
  comparisons[scope]={}
  for side in ['left','right']:
   maps={w:{x['word']:x for x in profiles[w][scope]['sides'][side]['known']} for w in targets}
   shared=[]
   for word in sorted(set().union(*(set(m) for m in maps.values()))):
    members={w:maps[w][word] for w in targets if word in maps[w]}
    if len(members)>=2:shared.append(dict(word=word,members=members,all_three=len(members)==3,strict_crossfolio=all(x['folios']>=2 for x in members.values())))
   shared.sort(key=lambda x:(-x['all_three'],-x['strict_crossfolio'],-sum(v['count'] for v in x['members'].values()),x['word']))
   comparisons[scope][side]=shared
 frames=collections.defaultdict(lambda:collections.defaultdict(list))
 for w in targets:
  for e in profiles[w]['events']:
   if valid(e['left']) and valid(e['right']):frames[(e['left'],e['right'])][w].append(e)
 frame_records=[]
 for (l,r),by in frames.items():
  if len(by)>=2:frame_records.append(dict(left=l,right=r,members={w:rec(es) for w,es in sorted(by.items())},all_three=len(by)==3,strict_crossfolio=all(len({e['folio'] for e in es})>=2 for es in by.values())))
 frame_records.sort(key=lambda x:(-x['all_three'],-x['strict_crossfolio'],-sum(p['count'] for p in x['members'].values()),x['left'],x['right']))
 adjacency={}
 for a,b in itertools.product(targets,repeat=2):
  es=[e for e in profiles[a]['events'] if e['right']==b]
  adjacency[a+' '+b]=rec(es)
 readings[tr]=dict(eligible_lines=len(rs),eligible_folios=len({fol(r) for r in rs}),baseline_positions=counter(e['position'] for e in baseline),profiles=profiles,shared_neighbors=comparisons,shared_frames=frame_records,directed_target_pairs=adjacency)

strata=collections.defaultdict(list)
for r in allbase:strata[tuple(r[2:6])].append(r)
inventory=[]
for key,rs0 in sorted(strata.items()):
 rs=sharedrows(rs0)
 if not any(w in targets for r in rs for w in r[7]):continue
 counts={}
 for tr in ['H','F']:
  counts[tr]={}
  for w in targets:
   ev=[occurrence(r,i) for r in rs if r[0]==tr for i,v in enumerate(r[7]) if v==w];removed=[e for e in ev if e['left']==e['right']=='shedy'];ev=[e for e in ev if not(e['left']==e['right']=='shedy')]
   counts[tr][w]=dict(count=len(ev),folios=len({e['folio'] for e in ev}),excluded_frame_centers=len(removed),positions=counter(e['position'] for e in ev))
 inventory.append(dict(section=key[0],hand=key[1],variety=key[2],format=key[3],readings=counts))
result=dict(protocol=protocol,targets=targets,readings=readings,cross_stratum_inventory=inventory)
save('RESULTS.json',result);(R/'data.js').write_text('const DATA = '+json.dumps(result,ensure_ascii=False)+';',encoding='utf-8')
summary={tr:dict(profiles={w:{k:p[k] for k in ['total_before_exclusion','retained','folios','positions']} for w,p in d['profiles'].items()},other_shared_frames=d['shared_frames'],strict_shared_neighbors={scope:{side:[x for x in d['shared_neighbors'][scope][side] if x['strict_crossfolio']] for side in ['left','right']} for scope in ['all_positions','interior_only']}) for tr,d in readings.items()}
save('SUMMARY.json',summary);save('VERIFICATION.json',dict(source_hash_and_method_freeze='pass',semantic_assignments='none',browser_visual_review='not performed'))
print(json.dumps(summary))
