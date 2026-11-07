import json,hashlib,re,ast,itertools,collections,datetime,sys,importlib.util
from pathlib import Path
from fractions import Fraction
R=Path(__file__).parent;B=R.parent;C2=B/'C2-open-v1';RC=R/'C2-R2-check'
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(n,v):checks.append(dict(check=n,pass_check=bool(v)))
a=load(R/'AMENDMENT-FREEZE.json');choice=load(R/'R2-CHOICE-FREEZE.json');plan=load(R/'COVERAGE-PLAN.json');count=load(R/'COVERAGE-COUNTS.json');result=load(RC/'RESULT.json');arms=load(R/'ARM-DISPOSITION-FREEZE.json');log=load(R/'COMBINED-C2-LOOK-LOG.json')
check('amendment hash',sha(R/'AMENDMENT.md')==a['amendment_sha256'])
for f,h in load(R/'PRESERVATION-BASELINE.json').items():check('prior preserved '+f,sha(B/f)==h)
for f in load(R/'PUBLISHED-INTAKE-PRESERVATION.json')['files']:check('intake preserved '+f['path'],sha(f['path'])==f['sha256'])
for f in load(C2/'DELIVERY-FREEZE.json')['files']:check('old C2 sealed '+f['path'],sha(C2/f['path'])==f['sha256'])
for f in load(B/'C1-source-freeze-v1/FREEZE.json')['files']:check('old C1 sealed '+f['path'],sha(B/'C1-source-freeze-v1'/f['path'])==f['sha256'])
check('half H gate',choice['PartC_and_B']['code']=='K' and choice['PartC_and_B']['readable_zodiac']==110 and choice['PartC_and_B']['H_readable_zodiac']==170 and choice['PartC_and_B']['half_H_gate'])
check('separate pharma freeze',choice['v6_pharma']['code']=='V' and choice['v6_pharma']['readable_pharma']==204 and choice['v6_pharma']['H_readable_pharma']==216)
flags=load(R/'READABILITY-FLAGS.json');ct={}
check('no strings or features in coverage flags',all(set(x)=={'id','unit','folio','reading','source_line','readable','C2_stratum','v6_pharma'} for x in flags))
check('no reserved flags',all(x['folio'] not in plan['reserved'] for x in flags))
for x in flags:
 c=ct.setdefault(x['reading'],collections.Counter())
 if x['readable'] and x['C2_stratum']:c[x['C2_stratum']]+=1
 if x['readable'] and x['v6_pharma']:c['v6_pharma']+=1
for x in count['counts']:
 for s,v in x['readable'].items():check('recount coverage '+x['code']+s,ct[x['code']][s]==v)
excluded=set(load(R/'PROVENANCE-POLICY.json')['not_separate_transcriber_codes'])|{'H'}
eligible=[x for x in count['counts'] if x['code'] not in excluded]
rank=sorted(eligible,key=lambda x:(-x['readable']['zodiac'],-x['readable']['plant-jar'],x['code']))
pharma=sorted(eligible,key=lambda x:(-x['readable']['v6_pharma'],-x['readable']['zodiac'],x['code']))
check('outcome blind zodiac winner',rank[0]['code']==choice['PartC_and_B']['code'])
check('outcome blind pharma winner',pharma[0]['code']==choice['v6_pharma']['code'])
check('choice frozen before decoding',datetime.datetime.fromisoformat(choice['utc'])<datetime.datetime.fromisoformat(load(RC/'COVERAGE.json')['decode_completed_utc']))
# Match every historically scored mathematical/extraction function by AST, excluding reading-role wrappers.
old=ast.parse((C2/'c2_engine.py').read_text());new=ast.parse((RC/'c2_roles.py').read_text())
def functions(t):return {x.name:ast.dump(x,include_attributes=False) for x in t.body if isinstance(x,ast.FunctionDef)}
o,n=functions(old),functions(new)
for name in ['tokens','glyphs','feature','probability','pair_counts','baseline','prevalence','ratio_of','choose']:check('frozen function unchanged '+name,o[name]==n[name])
rows=load(RC/'ROWS.json');look=load(RC/'LOOK-06.json')
check('only selected K decoded',all(x['reading']=='R2' and x['source_reading']=='K' and x['folio'] not in plan['reserved'] for x in rows))
check('no paragraph switch',all(x['set']!='paragraph' for x in rows) and choice['paragraph_readings']==['H','F'])
# Directly enumerate pairs independently of the optimized frozen function.
z=[x for x in rows if x['set']=='zodiac'];other=[x for x in rows if x['set'] in ['star','plant-jar','rosette']]
def opener(x):return next((p for p in ['ot','ok','qo','ch','sh','d'] if x['words'][0].startswith(p)),'other')
zv=[opener(x) for x in z];ov=[opener(x) for x in other]
wh=collections.Counter();dh=collections.Counter();bh=collections.Counter();wd=dd=bd=0
for i,j in itertools.permutations(range(len(z)),2):
 same=(z[i]['folio'],z[i]['unit'])==(z[j]['folio'],z[j]['unit'])
 if same:wd+=1
 else:dd+=1
 if zv[i]==zv[j]:
  if same:wh[zv[i]]+=1
  else:dh[zv[i]]+=1
for i,j in itertools.permutations(range(len(other)),2):
 bd+=1
 if ov[i]==ov[j]:bh[ov[i]]+=1
for m in look['readings']['R2']['metrics']:
 v=m['value'];check(v+' within pairs',m['within_ring']['numerator']==wh[v] and m['within_ring']['denominator']==wd)
 check(v+' between pairs',m['different_ring_same_section']['numerator']==dh[v] and m['different_ring_same_section']['denominator']==dd)
 check(v+' other pairs',m['nonzodiac_pair_baseline']['numerator']==bh[v] and m['nonzodiac_pair_baseline']['denominator']==bd)
 ratio=None if not wd or not bd or not bh[v] else Fraction(wh[v]*bd,wd*bh[v]);r=m['constancy_ratio']
 check(v+' exact ratio',r is None if ratio is None else r is not None and Fraction(r['numerator'],r['denominator'])==ratio)
q=[m for m in look['readings']['R2']['metrics'] if m['value']!='other' and m['constancy_ratio'] is not None and m['within_ring']['numerator']>0]
q.sort(key=lambda m:(-Fraction(m['constancy_ratio']['numerator'],m['constancy_ratio']['denominator']),m['value']))
check('actual R2 maximum is ok',q[0]['value']==result['M_star']['value']=='ok' and result['M_star']['exceeds_two'])
check('removal matches frozen H',result['M_star']['removal_operation']==result['H_M_star_preserved']['removal_operation'])
check('only one new look',log['looks_used']==6 and len(log['looks'])==6 and [x['look'] for x in log['looks']]==list(range(1,7)) and log['look_cap']==10)
check('prior five logs preserved',log['looks'][:5]==load(C2/'LOOK-LOG.json')['looks'])
check('no replacement suffix',arms['dispositions']['C-SUF']['status']=='DROPPED' and result['suffix_arm']=='DROPPED_NO_REPLACEMENT' and log['looks'][-1]['feature']['kind']=='opener')
check('C pool preserved',arms['alpha_overlay']['C_pool']==load(B/'BUDGET.json')['allocations']['C_pool'])
check('three arms equal split',arms['eligible_arms']==['C-FULL','C-STEM','C-MRK'] and arms['alpha_overlay']['each_C_arm']==arms['alpha_overlay']['C_pool']/3)
check('vault remains closed',not result['vault_open'] and not arms['vault_open'] and not arms['vault_execution_authorized'] and not result['C3_scored'])
check('published tier gates preserved',load(R/'PUBLISHED-TIER-POLICY.json')['banks']==['original_C3','context_role_preserving_C3'] and not load(R/'PUBLISHED-TIER-POLICY.json')['scored_in_this_continuation'])
check('no v6 scoring',not load(R/'V6-LABEL-READING-POLICY.json')['new_v6_scoring_run'])
# Source validity flags are invariant to letter identity; no spelling can influence the coverage rank.
spec=importlib.util.spec_from_file_location('flag_audit',R/'coverage_flags.py');module=ast.parse((R/'coverage_flags.py').read_text());flag_node=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='flag');env={'re':re};exec(compile(ast.Module(body=[flag_node],type_ignores=[]),'<syntax-only-flag>','exec'),env)
for payload in [b'qokeedy=',b'daiin.otal=',b'!ok%ar=',b'ot,edy=',b'ot{gap}edy=',b'%%%%=',b'chedy={old locator}']:
 check('flag letter-identity invariance '+str(payload),env['flag'](payload)==env['flag'](re.sub(rb'[a-z]',b'a',payload)))
summary=dict(status='PASS' if all(x['pass_check'] for x in checks) else 'FAIL',checks_run=len(checks),failed=[x for x in checks if not x['pass_check']],checks=checks,verification_is_new_feature_look=False)
(R/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['status','checks_run','failed']}))
if summary['status']!='PASS':raise SystemExit(1)
