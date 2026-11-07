from pathlib import Path
import json,hashlib,math,sys
from fractions import Fraction
from gate import retain_geometry_slots,literal_count_compatibility,role_pair,scientific_release,NotAdmitted
R=Path(__file__).parent;B=R.parent;P=B.parent
checks=[]
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(n,v):checks.append(dict(check=n,pass_check=bool(v)))
plan=load(R/'PLAN.json');r=load(R/'COMPATIBILITY.json')
for name,v in plan['inputs'].items():check('pinned input unchanged '+name,sha(v['path'])==v['sha256'])
check('complete nine profiles inventoried',len(r['source_profiles'])==9)
check('39 natural metadata scopes',len(r['targets'])==39)
check('all351profile-target pairs present',r['pair_count']==351 and len(r['compatibility_matrix'])==351)
check('five count matches only',len(r['count_matches'])==5)
check('onlyCancer7orGemini25match',{x['target'] for x in r['count_matches']}=={'band:f72r3:inner','panel_circular_bands:f72r2'})
check('no full-sign list length fits',all(not x['count_compatible'] for x in r['compatibility_matrix'] if x['target'].startswith('sign:')))
check('no admission by count alone',all(x['admitted_for_real_fitting'] is False for x in r['compatibility_matrix']))
check('Cancer7noKcoverage',next(x for x in r['targets'] if x['id']=='band:f72r3:inner')['R2_readable']==0)
check('Gemini25noexactlengthwrongunitlist',all(not x['same_length_other_list_units'] for x in r['count_matches'] if x['target']=='panel_circular_bands:f72r2'))
check('readable-onlyPiscesandLeotrapsretained',{x['folio'] for x in r['readable_compression_traps']}=={'f70v2','f72v3'})
# Compare independently with geometry inventory counts, never with readable word counts.
geo=load(plan['inputs']['geometry_inventory']['path'])
for p in geo:
 b={}
 for x in p['rows']:b[x['group']]=b.get(x['group'],0)+1
 for band,n in b.items():
  rr=next(x for x in r['bands'] if x['folio']==p['folio'] and x['band']==band)
  check('actual band count '+rr['id'],rr['positions']==n)
rows=[dict(slot_id='s'+str(i),folio='f70v2',labels={'H':None if i==3 else 'label-'+str(i),'R2':None}) for i in range(29)]
check('missing labels not compressed',len(retain_geometry_slots(rows,'H'))==29 and retain_geometry_slots(rows,'H')[3][1] is None)
for n in [7,25,26,28,30]:
 try:literal_count_compatibility(n,rows);ok=False
 except NotAdmitted:ok=True
 check('refuse length '+str(n)+'onto29',ok)
check('actual29slotlistcountpassesstructuralonly',literal_count_compatibility(29,rows))
for codes in [{'H':'H','R2':'V'},{'H':'H','R2':'F'}]:
 try:role_pair(codes);ok=False
 except NotAdmitted:ok=True
 check('reject role substitution '+codes['R2'],ok)
check('correct frozen roles structurally accepted',role_pair({'H':'H','R2':'K'}))
try:retain_geometry_slots([dict(slot_id='reserved',folio='f73r',labels={})],'H');ok=False
except NotAdmitted:ok=True
check('reserved input rejected',ok)
try:scientific_release(qualified=True,approved=True);ok=False
except NotAdmitted:ok=True
check('booleans cannot activate scientific/vault route',ok)
# Both prior delivery freezes remain unchanged.
for folder in [B/'amendment-v7.3',B/'C2-open-v1']:
 seal=load(folder/'DELIVERY-FREEZE.json')
 for f in seal['files']:check('prior delivery '+folder.name+'/'+f['path'],sha(folder/f['path'])==f['sha256'])
 for f in seal.get('external_policy_outputs',[]):check('prior policy output '+f['path'],sha(f['path'])==f['sha256'])
check('C2looksremain6',load(B/'amendment-v7.3/COMBINED-C2-LOOK-LOG.json')['looks_used']==6)
check('no hypothesis FAIL from infeasibility',r['scientific_verdict']=='NOT_ESTIMABLE_NOT_A_HYPOTHESIS_FAIL')
check('no scoring or vault',r['no_alignment_or_sound_fitting'] and r['vault_open'] is False)
# Exact MC resolution at frozen alpha; this is arithmetic, not qualification.
alpha=Fraction(1,1200)
check('1199nullsnotstrictlybelowalpha',Fraction(1,1200)==alpha)
check('1200nullsfirstpossiblepositivep',Fraction(1,1201)<alpha)
out=dict(status='PASS' if all(c['pass_check'] for c in checks) else 'FAIL',checks_run=len(checks),failed=[c for c in checks if not c['pass_check']],checks=checks,scope='Metadata and engineering guards only; no scientific C3 qualification or new C2 look.')
(R/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['status','checks_run','failed']}))
if out['status']!='PASS':raise SystemExit(1)
