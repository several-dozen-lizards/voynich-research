"""Metadata-only feasibility audit. Never loads decoded EVA label fields."""
from pathlib import Path
from collections import Counter,defaultdict
from itertools import combinations
import hashlib,json,math
R=Path(__file__).parent

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
def geometric_search_counts(sizes):
 # Candidate conventions only, not an adopted C3 rule.
 return dict(shared_direction=2*math.factorial(len(sizes))*math.prod(sizes),independent_band_directions=math.factorial(len(sizes))*math.prod(2*n for n in sizes))

def audit(plan):
 for item in plan['inputs'].values():
  if sha(item['path'])!=item['sha256']:raise RuntimeError('Pinned input changed: '+item['path'])
 source=read(plan['inputs']['lists']['path']);inventory=read(plan['inputs']['geometry_inventory']['path']);flags=read(plan['inputs']['R2_flags']['path']);status=read(plan['inputs']['geometry_status']['path'])
 profiles=[dict(id=x['id'],family=x['family'],unit=x['unit'],length=x['length']) for x in source['profiles']]
 assert all(x['folio'] not in ('f72v1','f72v2','f73r','f73v') for x in flags)
 # Source-band correspondence for auditing counts only: not unique figure ownership.
 source_band={
 'f70v2':{'outer':'S2','inner':'S1'},'f70v1':{'outer':'S2','inner':'S1'},
 'f71r':{'outer':'S1','inner':'S2'},'f71v':{'outer':'S1','inner':'S2'},
 'f72r1':{'outer':'S1','inner':'S2'},'f72r2':{'outer':'S1','inner':'S2','extra-top':'S0'},
 'f72r3':{'outer':'S1','middle':'S2','inner':'S3'},'f72v3':{'outer':'S1','inner':'S2'}}
 totals=defaultdict(Counter);readable=defaultdict(Counter)
 for x in flags:
  if x['C2_stratum']!='zodiac':continue
  totals[x['unit']][x['reading']]+=1
  if x['readable']:readable[x['unit']][x['reading']]+=1
 bands=[];panels=[];targets=[]
 for p in inventory:
  groups=defaultdict(list)
  for x in p['rows']:groups[x['group']].append(x)
  for band,rows in groups.items():
   unit=p['folio']+'.'+source_band[p['folio']][band]
   item=dict(id=p['folio']+':'+band,folio=p['folio'],sign=p['sign'],band=band,positions=len(rows),uncertain_presence=sum('presence' in x for x in rows),unresolved_adjacent_anchors=sum(x['label_anchor'] is None for x in rows),source_unit=unit,source_band_correspondence='MACRO_COUNTS_ONLY_NOT_OWNERSHIP',unique_registered_label_ownership=False,geometry_only=True,source_headers={a:totals[unit][a] for a in ['H','K']},readable_records={a:readable[unit][a] for a in ['H','K']})
   if band=='extra-top':
    item['source_headers']={'H':5,'K':5};item['readable_records']={'H':None,'K':None};item['coverage_note']='Excluded from frozen ring-ranking flags; not inferred to be a circular band.'
   bands.append(item)
   if band!='extra-top':targets.append(dict(id='band:'+item['id'],scope='individual_circular_band',folio=p['folio'],sign=p['sign'],positions=len(rows),band_sizes=[len(rows)],source_geometry_type='figure_band',uncertain_presence=item['uncertain_presence'],registered_ownership=False,H_readable=item['readable_records']['H'],R2_readable=item['readable_records']['K']))
  circle=[b for b in bands if b['folio']==p['folio'] and b['band']!='extra-top'];allb=[b for b in bands if b['folio']==p['folio']]
  panels.append(dict(folio=p['folio'],sign=p['sign'],circular_positions=sum(b['positions'] for b in circle),all_positions=sum(b['positions'] for b in allb),uncertain_presence=sum(b['uncertain_presence'] for b in allb),H_readable=sum(b['readable_records']['H'] for b in circle),R2_readable=sum(b['readable_records']['K'] for b in circle)))
  for scope,bb in [('panel_circular_bands',circle),('panel_all_groups',allb)]:
   sizes=[b['positions'] for b in bb]
   targets.append(dict(id=scope+':'+p['folio'],scope=scope,folio=p['folio'],sign=p['sign'],positions=sum(sizes),band_sizes=sizes,source_geometry_type='figure_panel',uncertain_presence=sum(b['uncertain_presence'] for b in bb),registered_ownership=False,H_readable=sum(b['readable_records']['H'] for b in circle),R2_readable=sum(b['readable_records']['K'] for b in circle),search_counts=geometric_search_counts(sizes)))
 for sign in sorted({p['sign'] for p in panels}):
  pp=[p for p in panels if p['sign']==sign]
  targets.append(dict(id='sign:'+sign,scope='whole_sign_all_panels',sign=sign,folios=[p['folio'] for p in pp],positions=sum(p['all_positions'] for p in pp),source_geometry_type='whole_sign_figures',uncertain_presence=sum(p['uncertain_presence'] for p in pp),registered_ownership=False,H_readable=sum(p['H_readable'] for p in pp),R2_readable=sum(p['R2_readable'] for p in pp)))
 matrix=[]
 for t in targets:
  for p in profiles:
   compatible=t['positions']==p['length']
   other_units=sorted({q['unit'] for q in profiles if q['length']==p['length'] and q['unit']!=p['unit']})
   issues=[]
   if not compatible:issues.append('LIST_GEOMETRY_LENGTH_MISMATCH')
   if t['uncertain_presence']:issues.append('UNCERTAIN_FIGURE_PRESENCE')
   if t['R2_readable']==0:issues.append('NO_R2_LABEL_COVERAGE')
   if not t['registered_ownership']:issues.append('NO_UNIQUE_LOCUS_TO_FIGURE_REGISTRATION')
   issues+=['SOURCE_UNIT_CORRESPONDENCE_NOT_DECLARED','C3_KEY_AND_MODEL_NOT_FROZEN','C3_SCIENTIFIC_QUALIFICATION_NOT_RUN']
   if not other_units:issues.append('NO_SAME_LENGTH_DIFFERENT_UNIT_LIST_IN_CLOSED_SET')
   matrix.append(dict(target=t['id'],profile=p['id'],target_positions=t['positions'],list_positions=p['length'],count_compatible=compatible,list_unit=p['unit'],target_type=t['source_geometry_type'],same_length_other_list_units=other_units,admitted_for_real_fitting=False,issues=issues))
 matches=[x for x in matrix if x['count_compatible']]
 compression_traps=[]
 for p in panels:
  for q in profiles:
   if p['H_readable']==q['length'] and p['circular_positions']!=q['length']:
    compression_traps.append(dict(folio=p['folio'],profile=q['id'],readable_H=p['H_readable'],physical_circular_positions=p['circular_positions'],reason='Readable-only compression would manufacture count agreement. Never drop geometric slots.'))
 out=dict(status='NO_ADMITTED_C3_FIT_PACKET',source_profiles=profiles,bands=bands,panels=panels,targets=targets,pair_count=len(matrix),compatibility_matrix=matrix,count_matches=matches,readable_compression_traps=compression_traps,independent_registration_status=status['mapping'],no_alignment_or_sound_fitting=True,no_C2_feature_look=True,C2_looks_used=6,C2_look_cap=10,vault_open=False,qualification_status='NOT_ATTEMPTED_NO_ADMITTED_ACTUAL_SUPPORT',scientific_verdict='NOT_ESTIMABLE_NOT_A_HYPOTHESIS_FAIL',limits=['Cardinality checks are necessary metadata checks, not semantic tests.','The listed natural scopes are audited alternatives, not adopted models.','Cancer has a seven-position inner band but no K coverage; Gemini circular bands total25 but labels are not uniquely registered.','Only the invocation family has25entries; no count-compatible different-unit list is available for that C5 control under literal complete-list alignment.','No reserved geometry or label payload was opened. Actual-support C4 qualification is not established.'])
 return out

if __name__=='__main__':
 p=read(R/'PLAN.json');out=audit(p);save('COMPATIBILITY.json',out)
 print(json.dumps(dict(status=out['status'],targets=len(out['targets']),profile_target_pairs=out['pair_count'],count_matches=out['count_matches'],compression_traps=out['readable_compression_traps'])))
