"""Pure descriptive C2 engine. No file/network acquisition or source-name fitting."""
from collections import Counter,defaultdict
from fractions import Fraction
import re
RESERVED={'f72v2','f72v1','f73r','f73v'}
OPEN={'f70v2','f70v1','f71r','f71v','f72r1','f72r2','f72r3','f72v3'}
SETS=('zodiac','zodiac-extra','star','plant-jar','rosette','paragraph')

def tokens(raw):
 text=re.sub(r'\{[^}]*\}','~',raw.split('#')[0])
 text=re.sub(r'[!%\s]','',text)
 text=re.sub(r'([=\-.,])~+$',r'\1',text).rstrip('=-.')
 parts=re.split(r'([.,=\-])',text)
 out=[]
 for i in range(0,len(parts),2):
  word=parts[i]
  if not word:continue
  uncertain=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
  out.append(word if re.fullmatch('[a-z]+',word) and not uncertain else None)
 return out

def glyphs(word):return re.findall(r'cth|ckh|cph|cfh|ch|sh|[a-z]',word)

def feature(row,feat,plan):
 words=row['words']
 if feat['kind']=='opener':
  return next((p for p in plan['opener_classes'] if p!='other' and words[0].startswith(p)),'other')
 if feat['kind']=='ending_family':
  return next((s for s in plan['ending_families'] if s!='other' and words[-1].endswith(s)),'other')
 if feat['kind']=='ending':
  units=glyphs(words[-1]);w=feat['width']
  return ''.join(units[-w:]) if len(units)>=w else None
 raise ValueError('unfrozen feature')

def probability(hit,n):return {'numerator':hit,'denominator':n,'probability':hit/n if n else None}
def pair_counts(rows,values,value,within=True):
 groups=defaultdict(list)
 for r,x in zip(rows,values):groups[(r['folio'],r['unit'])].append(x)
 wden=sum(len(v)*(len(v)-1) for v in groups.values())
 whit=sum(sum(x==value for x in v)*(sum(x==value for x in v)-1) for v in groups.values())
 if within:return probability(whit,wden)
 n=len(rows);c=sum(x==value for x in values)
 return probability(c*(c-1)-whit,n*(n-1)-wden)

def baseline(values,value):
 n=len(values);c=sum(x==value for x in values)
 return probability(c*(c-1),n*(n-1))

def prevalence(values,value):
 c=sum(x==value for x in values);n=len(values)
 return {'count':c,'n':n,'share':c/n if n else None,'feature_undefined':sum(x is None for x in values)}

def ratio_of(a,b):
 if a['denominator']<=0 or b['denominator']<=0 or b['numerator']<=0:return None
 f=Fraction(a['numerator']*b['denominator'],a['denominator']*b['numerator'])
 return {'numerator':f.numerator,'denominator':f.denominator,'value':float(f)}

def validate(rows,allowed_readings=('H','F')):
 ids=set()
 for r in rows:
  if r['folio'] in RESERVED:raise ValueError('Reserved folio rejected before feature evaluation')
  if r['reading'] not in allowed_readings:raise ValueError('Replacement reading forbidden')
  if r['set'] in ('zodiac','zodiac-extra') and r['folio'] not in OPEN:raise ValueError('Unregistered zodiac panel')
  if r['set'] not in SETS:raise ValueError('Unfrozen set')
  if not r['words'] or not all(isinstance(w,str) and re.fullmatch('[a-z]+',w) for w in r['words']):raise ValueError('Incomplete word slots must be excluded by adapter')
  key=(r['id'],r['reading'])
  if key in ids:raise ValueError('Duplicate label/reading')
  ids.add(key)

def compute_look(rows,feat,plan):
 validate(rows,plan.get('reading_codes',('H','F')));out={}
 for reading in plan.get('reading_codes',('H','F')):
  rr=[r for r in rows if r['reading']==reading]
  groups={s:[r for r in rr if r['set']==s] for s in SETS}
  groups['other_labels']=sum((groups[s] for s in ('star','plant-jar','rosette')),[])
  vals={s:[feature(r,feat,plan) for r in a] for s,a in groups.items()}
  candidates=sorted({x for v in vals.values() for x in v if x is not None})
  ringrows=groups['zodiac'];zvals=vals['zodiac'];metrics=[]
  for value in candidates:
   w=pair_counts(ringrows,zvals,value);d=pair_counts(ringrows,zvals,value,False);b=baseline(vals['other_labels'],value)
   metrics.append({'value':value,'within_ring':w,'different_ring_same_section':d,'nonzodiac_pair_baseline':b,'constancy_ratio':ratio_of(w,b),'shares':{s:prevalence(v,value) for s,v in vals.items()},'per_comparator_pair_baseline':{s:baseline(vals[s],value) for s in ('star','plant-jar','rosette')},'by_panel':{p:prevalence([feature(r,feat,plan) for r in ringrows if r['folio']==p],value) for p in plan['open_signs']},'by_ring':{u:prevalence([feature(r,feat,plan) for r in ringrows if r['unit']==u],value) for u in sorted({r['unit'] for r in ringrows})}})
  out[reading]={'status':'DESCRIPTIVE_AVAILABLE_COVERAGE' if len(ringrows)>1 and len(groups['other_labels'])>1 else 'NOT_ESTIMABLE','reason':None if ringrows else 'No zodiac label rows for this reading; no substitute used','coverage':{s:len(a) for s,a in groups.items()},'ring_count':len({r['unit'] for r in ringrows}),'metrics':metrics}
 return {'feature':feat,'readings':out,'scope':'C2 descriptive only; no significance test or source-name alignment'}

def choose(looks,reading,kind):
 q=[]
 for look in looks:
  feat=look['feature']
  if (feat['kind']=='opener')!=(kind=='opener'):continue
  for m in look['readings'][reading]['metrics']:
   ratio=m['constancy_ratio']
   if m['value']=='other' or ratio is None or m['within_ring']['numerator']<=0:continue
   q.append((Fraction(ratio['numerator'],ratio['denominator']),m['value'],feat.get('width',0),feat['id'],feat,m))
 q.sort(key=lambda x:(-x[0],x[1],x[2],x[3]))
 if not q:return None
 ratio,value,_,_,feat,m=q[0]
 return {'feature':feat,'value':value,'exceeds_two':ratio>2,'ratio':m['constancy_ratio'],'within_ring':m['within_ring'],'nonzodiac_pair_baseline':m['nonzodiac_pair_baseline'],'shares':m['shares'],'removal_operation':{'side':'prefix' if kind=='opener' else 'suffix','literal':value,'condition':{'feature_id':feat['id'],'equals':value},'applied_now':False}}

def summarize(looks,plan):
 result={}
 for reading in plan.get('reading_codes',('H','F')):
  estimable=all(x['readings'][reading]['status']!='NOT_ESTIMABLE' for x in looks)
  suffix=choose(looks,reading,'ending') if estimable else None
  marker=choose(looks,reading,'opener') if estimable else None
  result[reading]={'status':'DESCRIPTIVE_AVAILABLE_COVERAGE' if estimable else 'NOT_ESTIMABLE','coverage':looks[0]['readings'][reading]['coverage'],'ring_count':looks[0]['readings'][reading]['ring_count'],'best_ending':suffix,'best_opener':marker,'S_star':suffix if suffix and suffix['exceeds_two'] else None,'M_star':marker if marker and marker['exceeds_two'] else None,'scope_limit':'Available comparator pool; absent rosette/reading coverage not imputed.'}
 both=all(result[r]['status']!='NOT_ESTIMABLE' for r in ('H','F'))
 admitted={}
 for name in ('S_star','M_star'):
  a,b=result['H'][name],result['F'][name]
  admitted[name]=a['removal_operation'] if both and a and b and a['removal_operation']==b['removal_operation'] else None
 if not both:joint='NOT_ESTIMABLE'
 elif not any(result[r][k] for r in ('H','F') for k in ('S_star','M_star')):joint='NO_MARKER'
 elif not any(admitted.values()):joint='NO_COMMON_MARKER'
 else:joint='COMMON_MARKER_DESCRIPTIVE_ONLY'
 return {'status':'C2_COMPLETED_ON_AVAILABLE_COVERAGE','joint_marker_outcome':joint,'readings':result,'joint_removal_candidates':admitted,'NO_MARKER':joint=='NO_MARKER','arm_eligibility':'UNRESOLVED_MISSING_READING_COVERAGE' if not both else 'C2_DESCRIPTIVE_CANDIDATES_ONLY','C3_alignment_run':False,'vault_open':False,'vault_tests_run':0,'look_cap':plan['look_cap'],'looks_used':len(looks),'limits':plan['limitations']}
