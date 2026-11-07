import sys,json,hashlib,math,random,subprocess,importlib.util
from pathlib import Path
P=Path(__file__).parent;B=P.parent;OLD=B/'HARNESS';sys.path.insert(0,str(P));sys.path.insert(0,str(OLD))
from verdict_v71 import *
from run_attempt2 import keys,loadold
from stage5 import loadcase,owner_check
checks=[]
def check(n,ok):
 checks.append({'name':n,'pass':bool(ok)})
 if not ok:raise AssertionError(n)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'DELIVERY-HASHES.json')
admin=read(P/'CONCURRENT-ADMINISTRATION.json')
for f in old['files']:
 if f['path'] in admin['administrative']:
  backup=Path(admin['administrative'][f['path']]['attempt1_backup']);check('attempt1 administrative bytes preserved:'+f['path'],h(backup)==f['sha256'])
 else:check('attempt1 unchanged:'+f['path'],h(B/f['path'])==f['sha256'])
check('amendment seal',h(P/'AMENDMENT-v7.1.md')==read(P/'AMENDMENT-FREEZE.json')['amendment_sha256'])
freeze=read(P/'CODE-FREEZE.json')
for f,d in freeze['files'].items():check('code seal:'+f,h(P/f)==d)
check('stage5 seal',h(P/'stage5.py')==read(P/'STAGE5-CODE-SEAL.json')['sha256'])
noise=read(P/'HF-DISAGREEMENT.json');check('observed noise arithmetic',noise['rate']==noise['edit_count']/noise['max_length_denominator'])
mask=read(P/'NOISY-MASK.json');hd=read(P/'NOISY-H-DATA.json');fd=read(P/'NOISY-F-DATA.json');original=loadold('KNOWN-CIPHER-DATA.json')
ns=nd=0
for hr,fr,oldr in zip(hd['held'],fd['held'],original['held']):
 check('same noise geometry:'+hr['id'],[len(x) for x in hr['words']]==[len(x) for x in fr['words']]==[len(x) for x in oldr['words']])
 for hw,fw in zip(hr['words'],fr['words']):
  ns+=len(hw);nd+=sum(a!=b for a,b in zip(hw,fw))
check('realized disagreement mask',nd==mask['disagreeing_sites']==round(noise['rate']*ns) and ns==mask['sites'])
results=read(P/'QUALIFICATION.json')
for case in ('CLEAN','CORRUPT','NOISY-H','NOISY-F'):
 q,data,k,ks,real,controls=loadcase(case)
 for kind in ('C1-word','C1-glyph','C2'):
  br=read(P/'banks'/f'{case}-{kind}.json');check(case+' '+kind+'1000 keys',len(br['scores'])==1000 and br['key_hashes']==[digest(x) for x in ks])
 realreceipt=read(P/'banks'/f'{case}-real.json');check(case+' real1000keys',len(real)==1000 and realreceipt['key_hashes']==[digest(x) for x in ks])
 final=read(P/(case+'-FINAL.json'))
 for e,metric in final['metrics'].items():
  if 'mc_p' not in metric:continue
  vals=[z[e]['value'] for z in real];check(case+' '+e+' tail',(1+sum(x>=metric['value'] for x in vals))/1001==metric['mc_p'])
 for name,z in final['matched_controls'].items():
  e,control=name.split(':',1)
  category='CORRUPT' if case=='CORRUPT' else 'CLEAN'
  bp=P/'banks'/(f'{category}-'+control.replace(':','-')+'.json') if control.startswith('C2:') else P/'banks'/(case+'-'+control+'.json')
  bank0=read(bp)['scores'];threshold=sorted(x[e]['value'] for x in bank0)[949]
  check(case+' matched95:'+name,z['control_C3_p95']==threshold and z['exceeds']==(z['real_value']>threshold))
neg=read(P/'NEGATIVE-PROPOSALS-FINAL.json');n=len(neg);passes=sum(x['result']['verdict']=='PASS' for x in neg)
check('200 proposals',n==200);check('negative tally',dict(Counter(x['result']['verdict'] for x in neg))==results['negative']['tally'])
check('negative rate arithmetic',results['negative']['PASS_rate']==passes/n)
upper=results['negative']['CP_one_sided95_upper']
if passes==0:check('CP zero-event closed form',abs(upper-(1-.05**(1/n)))<1e-12)
else:
 tail=sum(math.comb(n,j)*upper**j*(1-upper)**(n-j) for j in range(passes+1));check('CP independent finite-binomial inversion',abs(tail-.05)<1e-10)
# Compare cached worker against an independently imported untouched original module.
spec=importlib.util.spec_from_file_location('independent_original',OLD/'harness.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
import bank_worker
base=loadold('KNOWN-CIPHER-DATA.json');key=loadold('KNOWN-KEY.json');context={x:base[x] for x in ('train','held','target','lexicons')};bank_worker.init(context)
check('cached worker equals untouched original',bank_worker.score_one((0,key))['scores']==ref.raw_scores(key,**context))
g=read(P/'V5-C2-DATA.json');check('v5 qualified owners unchanged after execution',owner_check()['owners']==g['owner_qualification']['owners'])
check('all6 qualified entrypoint families',set(g['generated'])==set(('G1','G2','G3','G4','G5','G6')))
check('publishedG5 seed exclusion',g['generated']['G5']['mechanism_receipt']['published_source'] and g['generated']['G5']['mechanism_receipt']['seed_line_excluded'])
for fam,item in g['generated'].items():
 r=item['mechanism_receipt']
 if fam in ('G1','G2','G3','G4'):check(fam+' source custody',r['source_receipt']['partition']=='development' and r['source_receipt']['source_wraps']==0)
for reading in ('H','F'):
 trap=read(P/('TRAP-'+reading+'-DATA.json'));tk=read(P/('TRAP-'+reading+'-KEY.json'));custody_check(tk,trap['train'],trap['held'])
 check(reading+' actual trap disjoint pages',not ({r['folio'] for r in trap['train']}&{r['folio'] for r in trap['held']}))
 check(reading+' no zodiac trap folios',not any(67<=int(__import__('re').match(r'f(\d+)',r['folio'])[1])<=73 for r in trap['train']+trap['held']))
check('external reservation remains closed',read(B/'BUDGET.json')['vault_tests_run']==0 and read(B/'ALPHA-V-AMENDMENT.json')['vault_execution_authorised'] is False)
check('no vault result',(B/'VAULT-RESULT.json').exists() is False and (P/'VAULT-RESULT.json').exists() is False)
r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(P),'-p','test_v71.py','-v'],capture_output=True,text=True);(P/'TEST-LOG.txt').write_text(r.stdout+r.stderr);check('11 focused tests',r.returncode==0 and 'Ran 11 tests' in r.stderr)
out={'status':'PASS_ARTIFACT_AND_METHOD_VERIFICATION','checks':checks,'check_count':len(checks),'tests':11,'qualification_status':results['status'],'attempt1_files_preserved':len(old['files']),'same_path_unchanged':128,'administrative_supersessions':2,'vault_tests_run_here':0,'external_alpha_reservation':read(B/'BUDGET.json')['alpha_V']}
(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
