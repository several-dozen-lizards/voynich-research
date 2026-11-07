from pathlib import Path
import collections,hashlib,json,re
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
src=[P/'category-extension-v61/RESULTS.json',P/'frequency-atlas-v48/rows.json']
protocol={'scope':'Descriptive examination of qol bath hand2/B/P and cheol botanical hand1/A/P, using unchanged v61 original-folio exclusions and shared H/F loci. No cross-stratum semantic comparison.',
 'definitions':'Exact word neighbour inventory, both sides. Recurs across folios means >=2 numbered folios, a descriptive threshold not a significance test. Preserve singleton and single-folio neighbours. Original target remains as reference; other neighbours explicitly flagged.',
 'groups':'Classify neighbours by cross-folio recurrence before, after, both or neither. Shared external frames use exact readable left and right words around candidate neighbours, with anchor-adjacent occurrences excluded. Loose frames require >=2 member types and >=2 pooled folios; strict frames require each retained member on >=2 folios, with >=2 such members. Never join unknowns or source-line edges.',
 'positions':'Report neighbour positions at anchor adjacency, and independent eligible-stratum occurrences excluding adjacency to anchor. First/interior/last/single use source-line slots, including unknown slots in ordinals. Source-line positions are not sentence or record positions.',
 'frames':'Report all left-anchor-right triples, with cross-folio recurrence flagged, including identical left/right neighbour words. External shared frames are possible substitution environments, not semantic classes.',
 'form_profiles':'Suffix last two EVA characters inventoried among neighbour events, separately by side; these are spelling profiles, not morphological or semantic families. Show every ending and all member words.',
 'limits':'No new semantic labels, statistical tests, category discovery or role validation. Already inspected corpus. High frequency and spelling similarity can generate recurring groups. Contexts containing unknowns/edges cannot enter complete-frame analysis. No operation, attribute or timing conclusion follows solely from these counts.'}
hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in src}
freeze={'source_hashes':hashes,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
old,rows=[load(p) for p in src]
def fol(r):return re.match(r'f\d+',r[1])[0]
def pos(i,n):return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def clean(w):return w is not None and w not in ('#EDGE','#UNKNOWN')
def count(xs):return dict(collections.Counter(xs).most_common())
def record(items):return {'count':len(items),'folios':len({x['folio'] for x in items}),'locators':sorted({x['locator'] for x in items})}
groups=[]
for prior in old['groups']:
 if prior['id'] not in ('bath','botanical'):continue
 a=prior['anchor'];meta=prior['metadata'];stratum=tuple(meta[k] for k in ('section','hand','variety','format'))
 base=[r for r in rows if tuple(r[2:6])==stratum and fol(r) not in prior['excluded_folios']]
 ls={tr:{r[6] for r in base if r[0]==tr} for tr in ('H','F')};shared=ls['H']&ls['F']
 group={'id':prior['id'],'anchor':a,'original_target':prior['target'],'metadata':meta,'excluded_folios':prior['excluded_folios'],'readings':{}}
 for tr in ('H','F'):
  rs=[r for r in base if r[0]==tr and r[6] in shared];ev=prior['readings'][tr]['events']
  nbrs=collections.defaultdict(lambda:collections.defaultdict(list));triples=collections.defaultdict(list)
  for e in ev:
   if clean(e['left']) and clean(e['right']):triples[(e['left'],e['right'])].append(e)
   for side,offset in [('left',-1),('right',1)]:
    w=e[side]
    if clean(w):nbrs[w][side].append(dict(e,neighbor_position=pos(e['ordinal']-1+offset,len(e['tokens']))))
  candidates=set(nbrs);elsewhere=collections.defaultdict(list);frames=collections.defaultdict(lambda:collections.defaultdict(list));den=collections.Counter()
  for r in rs:
   for i,w in enumerate(r[7]):
    if w is None:continue
    left=r[7][i-1] if i else '#EDGE';right=r[7][i+1] if i+1<len(r[7]) else '#EDGE'
    if a in (left,right):continue
    den[pos(i,len(r[7]))]+=1
    if w not in candidates:continue
    e={'locator':r[6],'folio':fol(r),'ordinal':i+1,'position':pos(i,len(r[7]))}
    elsewhere[w].append(e)
    if clean(left) and clean(right):frames[(left,right)][w].append(e)
  inventory=[]
  for w,sides in nbrs.items():
   l=record(sides['left']);r=record(sides['right']);both=[k for k,v in [('before',l),('after',r)] if v['folios']>=2]
   inventory.append({'word':w,'reference':w==prior['target'],'self_neighbor':w==a,'left':l,'right':r,'recurrence_group':'both sides' if len(both)==2 else both[0]+' only' if both else 'no cross-folio recurrence',
    'adjacent_positions':{s:count(e['neighbor_position'] for e in sides[s]) for s in ('left','right')},'elsewhere':dict(record(elsewhere[w]),positions=count(e['position'] for e in elsewhere[w]))})
  inventory.sort(key=lambda x:(-(x['left']['count']+x['right']['count']),x['word']))
  frame_records=[]
  for (l,r),members in frames.items():
   pooled=[e for es in members.values() for e in es];strict={w:es for w,es in members.items() if len({e['folio'] for e in es})>=2}
   if len(members)>=2 and len({e['folio'] for e in pooled})>=2:
    frame_records.append({'left':l,'right':r,'members':{w:record(es) for w,es in sorted(members.items())},'strict_members':sorted(strict),'strict':len(strict)>=2,**record(pooled)})
  frame_records.sort(key=lambda x:(-x['strict'],-len(x['strict_members']),-x['count'],x['left'],x['right']))
  endingprofiles={}
  for side in ('left','right'):
   ending=collections.defaultdict(list)
   for w,sides in nbrs.items():
    for e in sides[side]:ending[w[-2:]].append((w,e))
   endingprofiles[side]=[dict(ending=k,count=len(v),folios=len({e['folio'] for _,e in v}),members=count(w for w,_ in v)) for k,v in sorted(ending.items(),key=lambda kv:(-len(kv[1]),kv[0]))]
  triple_records=[dict(left=l,right=r,**record(es)) for (l,r),es in triples.items()];triple_records.sort(key=lambda x:(-x['folios'],-x['count'],x['left'],x['right']))
  d={'anchor_events':len(ev),'inventory':inventory,'recurrence_counts':count(x['recurrence_group'] for x in inventory),'triples':triple_records,'complete_triples':sum(t['count'] for t in triple_records),'crossfolio_triples':sum(t['folios']>=2 for t in triple_records),
   'external_shared_frames':frame_records,'strict_external_frames':sum(f['strict'] for f in frame_records),'ending_profiles':endingprofiles,'elsewhere_position_baseline':dict(den),'events':ev,
   'unknown_or_edge':{s:count(e[s] for e in ev if not clean(e[s])) for s in ('left','right')}}
  assert sum(x['left']['count'] for x in inventory)+sum(d['unknown_or_edge']['left'].values())==len(ev)
  assert sum(x['right']['count'] for x in inventory)+sum(d['unknown_or_edge']['right'].values())==len(ev)
  assert all(x['word'] in candidates for x in inventory)
  group['readings'][tr]=d
 # Exact-spelling H/F neighbour comparison is bookkeeping, not independent replication.
 by={tr:{x['word']:x for x in d['inventory']} for tr,d in group['readings'].items()}
 group['exact_reading_comparison']=[{'word':w,'H':by['H'].get(w),'F':by['F'].get(w)} for w in sorted(set(by['H'])|set(by['F']))]
 groups.append(group)
result={'protocol':protocol,'groups':groups}
save('RESULTS.json',result);(R/'data.js').write_text('const DATA = '+json.dumps(result,ensure_ascii=False)+';',encoding='utf-8')
summary=[]
for g in groups:
 for tr,d in g['readings'].items():
  summary.append({'anchor':g['anchor'],'reading':tr,'events':d['anchor_events'],'word_types':len(d['inventory']),'recurrence_groups':d['recurrence_counts'],'crossfolio_triples':d['crossfolio_triples'],'strict_external_frames':d['strict_external_frames'],'loose_external_frames':len(d['external_shared_frames']),
   'other_recurrent':[{'word':x['word'],'left':x['left']['count'],'left_folios':x['left']['folios'],'right':x['right']['count'],'right_folios':x['right']['folios'],'elsewhere_positions':x['elsewhere']['positions']} for x in d['inventory'] if not x['reference'] and x['recurrence_group']!='no cross-folio recurrence']})
save('SUMMARY.json',summary);save('VERIFICATION.json',{'frozen_sources_and_script':'pass','left_right_event_conservation':'pass','original_group_controls':'unchanged from v61','no_new_semantic_assignments':True,'visual_review':'not performed'})
print(json.dumps(summary))
