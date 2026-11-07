import json,hashlib,re,sys
from pathlib import Path
r=Path(__file__).parent
sys.path.insert(0,str(r.parent/'attempt-2-v7.1/vendor'))
from bs4 import BeautifulSoup
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(check=name,pass_check=bool(ok),detail=detail))
def read(n):return json.loads((r/n).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read('LISTS.json');audit=read('SOURCE-AUDIT.json');profiles=s['profiles']
check('exactly nine enumerated profiles',len(profiles)==9)
check('five source families',len({p['family'] for p in profiles})==5)
check('source profile multiplicity is charged',s['search_size']['explicit_list_variant_profiles']==len(profiles))
check('179 source positions',sum(len(p['entries']) for p in profiles)==179)
check('all IDs unique',len({p['id'] for p in profiles})==len(profiles))
check('14 explicit audit decisions',len(audit['candidates'])==14 and all('PENDING' not in a['status'] for a in audit['candidates']))
sources={x['id'] for x in s['sources']}
for p in profiles:
 check(p['id']+': date cutoff',p['date_upper_year']<=1440 and bool(p['date_basis']))
 check(p['id']+': source exists',p['source_id'] in sources)
 check(p['id']+': length matches',len(p['entries'])==p['length'])
 check(p['id']+': ordered complete positions',[e['position'] for e in p['entries']]==list(range(1,p['length']+1)))
 for e in p['entries']:
  label=p['id']+': '+str(e['position'])
  check(label+': fixed nonempty spelling and coordinate',bool(e['name']) and bool(e['source_coordinate']))
  m=e['morphology']; suffix=m['suffix_surface_candidate']
  check(label+': reversible suffix split',m['stem_for_C_STEM']+(e['name'][-len(suffix):] if suffix else '')==e['name'])
  if p['source_id']=='boudet2002':
   pages=['0876','0877'] if 'seal' in p['id'] else ['0884'] if 'invocation' in p['id'] else ['0882','0883','0884']
   source=' '.join(x['text'] for x in read('sources/boudet-all-pages.json') if x['page'] in pages)
   check(label+': attested in critical passage/apparatus',e['name'] in source)
for fam in {p['family'] for p in profiles}:
 pp=[p for p in profiles if p['family']==fam]
 for i in range(pp[0]['length']):
  actual={p['entries'][i]['name'] for p in pp}
  recorded=next(x for x in s['variant_registry'] if x['family']==fam and x['position']==i+1)
  check(fam+': registry '+str(i+1),actual=={x['form'] for x in recorded['forms']})
for p in profiles:
 if p['family']=='juratus-planets':check(p['id']+': unequal planet groups retained',p['group_sizes']==[4,4,4,4,3,3,4] and p['length']==26)
 if p['family']=='juratus-invocation':check(p['id']+': 25 names, not 24hours',p['length']==25 and p['unit']=='planetary_invocation_position')
amb=next(p for p in profiles if p['id']=='picatrix-I4-ambrosiana')
check('Ambrosiana exceptional spellings preserved',amb['entries'][10]['name']=='Mobra' and amb['entries'][25]['name']=='Aliniquecdea')
check('Ambrosiana repeated ordinal retained','XXVI (repeated)'==amb['entries'][26]['source_ordinal_as_printed'])
h=BeautifulSoup((r/'sources/heptameron-peterson.html').read_text(encoding='cp1252'),'html.parser')
t=h.find('table',id='table2')
raz=[]
for row in t.find_all('tr'):
 cells=row.find_all(['th','td'],recursive=False)
 if len(cells)>2 and cells[0].get_text(strip=True) in ['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon']:raz.append(cells[2].get_text(' ',strip=True))
rz=next(p for p in profiles if p['family']=='raziel-seven')
check('Raziel exact editorial column',raz==[e['name'] for e in rz['entries']],raz)
late=read('LISTS-LATE.json');check('late set barred from claims',late['claim_eligible'] is False)
exc=read('EXCLUDED-DRAFT-LISTS.json');check('IV9 gaps not repaired',all(p['entries'][21]['name'] is None for p in exc['lists']))
for f,oldhash in read('PRESERVATION-BASELINE.json').items():check('preserved original '+f,sha(r.parent/f)==oldhash)
check('C2 not run',s['C2']==dict(run=False,looks_used=0))
check('vault closed',s['vault']['open'] is False and s['vault']['tests_run_in_this_phase']==0)
result=dict(status='PASS' if all(c['pass_check'] for c in checks) else 'FAIL',checks_run=len(checks),failed=[c for c in checks if not c['pass_check']],checks=checks,scope='Structural, source-attestation and preservation checks; historical date/spelling image decisions separately documented. No Voynich scores or vault calls.')
(r/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['status','checks_run','failed']},ensure_ascii=False))
if result['status']!='PASS':sys.exit(1)
