import copy,json,math,random,subprocess,sys,time
from pathlib import Path
from harness import *
P=Path(__file__).parent;ROOT=P.parent
checks=[]
def check(name,ok):
 checks.append({'check':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
q=read(P/'QUALIFICATION.json');pos=read(P/'KNOWN-POSITIVE-FULL.json');near=read(P/'NEAR-MISS-FULL.json');plan=read(P/'QUALIFICATION-PLAN.json');d=read(P/'KNOWN-CIPHER-DATA.json');k=read(P/'KNOWN-KEY.json')
check('known input hash agrees frozen plan',digest({'key':k,**d})==plan['input_sha256'])
for name,r in [('positive',pos),('near-miss',near)]:
 check(name+' has1000 real random-key scores',r['C3_count']==1000 and len(r['C3_raw'])==1000 and len(r['C3_key_hashes'])==1000)
 check(name+' coherence arithmetic',math.isclose(sum(x.get('gain_bits',0) for x in r['C3'].values())-r['K_bits'],r['coherence_bits'],abs_tol=1e-8))
 for e,z in r['C3'].items():
  if 'mc_p' in z:
   vals=[x[e]['value'] for x in r['C3_raw']];tail=(1+sum(v>=z['value'] for v in vals))/1001
   check(name+' '+e+' independent upper tail',tail==z['mc_p'])
corrupt=copy.deepcopy(k)
for u in q['near_miss']['corrupted_entries']:
 a=k['target']['alphabet'];v=corrupt['map'][u];corrupt['map'][u]=a[(a.index(v)+1)%len(a)]
(P/'NEAR-MISS-KEY.json').write_text(json.dumps(corrupt,indent=2)+'\n')
check('near-miss input reconstructed exactly',digest({'key':corrupt,**d,'pairs':(),'number_checks':()})==near['input_sha256'])
check('true-key input reproduces',digest({'key':k,**d,'pairs':(),'number_checks':()})==pos['input_sha256'])
neg=read(P/'NEGATIVE-PROPOSALS.json');tally=dict(Counter(x['verdict'] for x in neg))
check('negative trial tally',tally==q['negative_tally'] and len(neg)==100)
check('literal negative FAIL rate',q['negative_fail_rate']==tally.get('FAIL',0)/100)
rng=random.Random(987)
for z in neg:check('negative key hash '+str(z['index']),digest(random_key(k,rng))==z['key_sha256'])
# Base/random map counts and complexity checked over every baseline key, not a sample.
for seed,r,key in [(714,pos,k),(715,near,corrupt)]:
 rng=random.Random(seed)
 for expected in r['C3_key_hashes']:
  rk=random_key(key,rng)
  if digest(rk)!=expected or complexity(rk)!=complexity(key):raise AssertionError('null bank reconstruction')
check('both1000-key banks reconstructed',True)
check('failed gates not promoted',q['status']=='NOT_QUALIFIED_FOR_REAL_KEYS' and not q['engineering_gates']['positive_pass'] and not q['engineering_gates']['negative_FAIL_rate_at_least_99pct'])
lists=read(ROOT/'LISTS.json');check('list positions retained',len(lists['lists'])==3 and all([e['order'] for e in x['entries']]==list(range(1,29)) for x in lists['lists']))
check('source holes preserved',lists['lists'][1]['entries'][21]['name'] is None and lists['lists'][2]['entries'][21]['name'] is None)
check('two spirit7 forms preserved',{x['form'] for x in lists['lists'][2]['entries'][6]['variants']}=={'Selehe','Siely'})
check('list universe not falsely frozen',lists['status']=='DRAFT_NOT_FROZEN' and not lists['assembly_complete'] and not lists['claim_eligible_lists'])
check('source PDF archived',(ROOT/'sources/picatrix-pingree-1986.pdf').read_bytes()[:4]==b'%PDF')
check('all13 reviewed source renders exist',len(list((ROOT/'sources').glob('page-*.png')))==13)
seal=read(ROOT/'JOINT-DECLARATION-SOURCE-SEAL.json');check('full declaration hash',seal['sha256']==filehash(ROOT/'JOINT-VAULT-DECLARATION-SOURCE.md'))
budget=read(ROOT/'BUDGET.json');check('no unauthorized alpha',budget['alpha_V'] is None and budget['spend']==0 and budget['status']=='UNALLOCATED')
c2=read(ROOT/'C2-PRETEST.json');check('no manuscript pretest or invented NO MARKER',c2['status']=='NOT_RUN' and c2['looks_used']==0 and c2['NO_MARKER'] is False)
check('C3 unfitted',read(ROOT/'C3-FREEZE.json')['status']=='NOT_FROZEN')
check('no vault result artifact',(ROOT/'VAULT-RESULT.json').exists() is False)
run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(P),'-p','test*.py','-v'],capture_output=True,text=True)
(P/'TEST-LOG.txt').write_text(run.stdout+run.stderr,encoding='utf8');check('20 focused engineering tests',run.returncode==0 and 'Ran 20 tests' in run.stderr)
receipt={'status':'PASS_ENGINEERING_AND_ARTIFACT_INTEGRITY_ONLY','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':checks,'tests':20,'scientific_qualification':'NOT_QUALIFIED_FOR_REAL_KEYS','source_review':'13 Picatrix edited pages visually inspected; apparatus not included','manuscript_scoring':False,'vault_spend':0}
(ROOT/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps({'checks':len(checks),'tests':20,'status':receipt['status']}))
