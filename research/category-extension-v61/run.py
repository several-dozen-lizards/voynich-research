from pathlib import Path
import collections, hashlib, json, re

R=Path(__file__).resolve().parent; P=R.parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(name,x): (R/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
sources=[P/'category-worksheet-v60/WORKSHEET.json',P/'frequency-atlas-v48/rows.json']
hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
protocol={
 'status':'Operational tests fixed before this extension is run. Existing full corpus was previously inventoried: additional examples, not untouched validation.',
 'assignment_policy':'Copy every category mapping unchanged from worksheet. Group-local whole-word proposals only. No affix meanings or new assigned words.',
 'selection':'Exclude entire numbered folios used in each original group, including page parts and contexts. Match group section, hand, variety and raw format. Primary shared H/F source loci; show unavailable/single-reading support separately. Include all broad line positions, preserving unknown slots.',
 'anchors':{'bath':['qol','chedy'],'recipe':['qokeey','daiin'],'botanical':['cheol','chol'],'celestial':['sar',None]},
 'tests':['Count exact forward and reverse pair without bridging unknowns or line boundaries; report right/left neighbours, unknowns and edges separately.',
          'Show original and additional anchor broad-position and ordinal distributions separately by H/F, plus all readable-token position baseline.',
          'For each anchor occurrence, show full source line and unchanged substitutions for all three models. No winner or semantic score.'],
 'interpretation':'Recurrence, direction and position are form observations shared by relabelled models. Recurrence supports availability of a pattern, not the assigned meaning. Missing target neighbour is an exception to an obligatory adjacency reading, not disproof of a flexible category interpretation. Celestial model predicts no particular neighbour in the original worksheet: test not specified, no invented planet or condition label.',
 'comparison':'No hypothesis test or p values. Source selected features and corpus already inspected; descriptive rates, target ranks and folio support only. No semantic qualification claim.',
 'positions':'single for one slot, first/last at physical source-line token slots, otherwise interior. Unknown slots count toward ordinal and line length. Source lines are not assumed sentences or records.'}
if (R/'FREEZE.json').exists():
 assert read(R/'FREEZE.json')['source_hashes']==hashes, 'Inputs changed since freeze'
 assert read(R/'PROTOCOL.json')==protocol, 'Protocol changed'
else:
 save('PROTOCOL.json',protocol)
 save('FREEZE.json',{'source_hashes':hashes,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
assert read(R/'FREEZE.json')['script_sha256']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

ws,rows=[read(p) for p in sources]
def fol(r): return re.match(r'f\d+',r[1])[0]
def pos(i,n): return 'single' if n==1 else 'first' if i==0 else 'last' if i==n-1 else 'interior'
def counter(xs): return dict(collections.Counter(xs).most_common())
def events(rs,a,b):
 out=[]
 for r in rs:
  for i,w in enumerate(r[7]):
   if w!=a: continue
   left=r[7][i-1] if i else '#EDGE'; right=r[7][i+1] if i+1<len(r[7]) else '#EDGE'
   out.append(dict(locator=r[6],folio=fol(r),ordinal=i+1,position=pos(i,len(r[7])),line_length=len(r[7]),left=left if left is not None else '#UNKNOWN',right=right if right is not None else '#UNKNOWN',tokens=r[7],forward=right==b if b else None,reverse=left==b if b else None))
 return out
groups=[]
for c in ws['cohorts']:
 a,b=protocol['anchors'][c['id']]
 originals=[c['passages'][0]['readings'][tr] for tr in ('H','F')]
 meta=originals[0]; strata=(meta['section'],meta['hand'],meta['variety'],meta['format'])
 assert all((q['section'],q['hand'],q['variety'],q['format'])==strata for q in originals)
 excluded={re.match(r'f\d+',loc)[0] for loc in c['loci']}
 pool=[r for r in rows if tuple(r[2:6])==strata and fol(r) not in excluded]
 loci={tr:{r[6] for r in pool if r[0]==tr} for tr in ('H','F')}
 shared=loci['H']&loci['F']; group=dict(id=c['id'],title=c['title'],anchor=a,target=b,metadata=dict(zip(['section','hand','variety','format'],strata)),excluded_folios=sorted(excluded),models=c['models'],readings={})
 for tr in ('H','F'):
  selected=[r for r in pool if r[0]==tr and r[6] in shared]; ev=events(selected,a,b)
  originalrows=[r for r in rows if r[0]==tr and r[6] in c['loci']]
  orig=events(originalrows,a,b)
  right=collections.Counter(e['right'] for e in ev if e['right'] not in ('#UNKNOWN','#EDGE'))
  left=collections.Counter(e['left'] for e in ev if e['left'] not in ('#UNKNOWN','#EDGE'))
  readable_right=sum(right.values()); readable_left=sum(left.values())
  # Dense rank is descriptive, with ties made explicit by counts.
  targetrank=1+sum(v>right[b] for v in right.values()) if b and right[b] else None
  allpos=counter(pos(i,len(r[7])) for r in selected for i,w in enumerate(r[7]) if w is not None)
  group['readings'][tr]=dict(eligible_lines=len(selected),eligible_folios=len({fol(r) for r in selected}),readable_words=sum(w is not None for r in selected for w in r[7]),single_reading_loci=len(loci[tr]-shared),
   anchor_events=len(ev),anchor_folios=len({e['folio'] for e in ev}),original_positions=counter(e['position'] for e in orig),original_ordinals=counter(e['ordinal'] for e in orig),positions=counter(e['position'] for e in ev),ordinals=counter(e['ordinal'] for e in ev),all_readable_positions=allpos,
   right_neighbors=dict(right.most_common()),left_neighbors=dict(left.most_common()),known_right_opportunities=readable_right,known_left_opportunities=readable_left,
   unknown_right=sum(e['right']=='#UNKNOWN' for e in ev),edge_right=sum(e['right']=='#EDGE' for e in ev),unknown_left=sum(e['left']=='#UNKNOWN' for e in ev),edge_left=sum(e['left']=='#EDGE' for e in ev),
   forward_count=sum(e['forward'] is True for e in ev) if b else None,reverse_count=sum(e['reverse'] is True for e in ev) if b else None,
   forward_folios=len({e['folio'] for e in ev if e['forward'] is True}) if b else None,target_right_rank=targetrank,
   known_right_exceptions=[e['locator'] for e in ev if b and e['right'] not in (b,'#UNKNOWN','#EDGE')],events=ev,
   target_profile=({'events':len(events(selected,b,a)),'positions':counter(e['position'] for e in events(selected,b,a))} if b else None))
 groups.append(group)
result=dict(protocol=protocol,groups=groups,scope='Fixed word assignments extended to additional source folios. Structural tests only. Competing category meanings remain unidentifiable from identical token mappings and positional predictions.')
save('RESULTS.json',result)
(R/'data.js').write_text('const DATA = '+json.dumps(result,ensure_ascii=False)+';',encoding='utf-8')
summary=[dict(group=g['id'],transcription=tr,anchor=d['anchor_events'],folios=d['anchor_folios'],forward=d['forward_count'],forward_folios=d['forward_folios'],known_right=d['known_right_opportunities'],reverse=d['reverse_count'],right_rank=d['target_right_rank'],positions=d['positions'],top_right=list(d['right_neighbors'].items())[:5]) for g in groups for tr,d in g['readings'].items()]
save('SUMMARY.json',summary)
for g in groups:
 for tr,d in g['readings'].items():
  assert d['anchor_events']==sum(d['positions'].values())==d['known_right_opportunities']+d['unknown_right']+d['edge_right']
  assert not any(e['folio'] in g['excluded_folios'] for e in d['events'])
  assert all(e['tokens'][e['ordinal']-1]==g['anchor'] for e in d['events'])
  assert g['models']==next(c['models'] for c in ws['cohorts'] if c['id']==g['id'])
save('VERIFICATION.json',dict(source_hashes='pass',script_freeze='pass',original_folio_exclusion='pass',source_token_anchor_indices='pass',counts_conserved='pass',mappings_unchanged='pass',semantic_validation='not performed',browser_visual_review='not performed'))
print(json.dumps(summary))
