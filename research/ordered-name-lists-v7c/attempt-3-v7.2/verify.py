import sys,json,hashlib,math,random,statistics,subprocess,copy
from pathlib import Path
from collections import Counter
P=Path(__file__).parent;B=P.parent;A2=B/'attempt-2-v7.1';sys.path.insert(0,str(B/'HARNESS'));sys.path.insert(0,str(A2))
from harness import digest,complexity,custody_check
from run import keybank,project,context,loadbank
from role_preserving_keys import invariants
from source_first_controls import validate_source
checks=[];cache={}
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
def bankread(p):
 p=Path(p).resolve();seen=set()
 while True:
  if p in seen:raise AssertionError('cyclic bank reference')
  seen.add(p)
  if p not in cache:cache[p]=read(p)
  obj=cache[p]
  if 'ref' not in obj:return obj
  if 'reference_sha256' in obj:check('external reused bank hash:'+p.name,h(obj['ref'])==obj['reference_sha256'])
  p=Path(obj['ref']).resolve()
q=read(P/'QUALIFICATION.json');freeze=read(P/'CODE-FREEZE.json')
for f,s in freeze['files'].items():check('frozen code:'+f,h(P/f)==s)
check('approved amendment',h(P/'AMENDMENT-v7.2.md')==read(P/'APPROVAL-AND-FREEZE.json')['amendment_sha256'])
check('plan seal',h(P/'PLAN.json')==read(P/'PLAN-SEAL.json')['sha256'])
for f,s in read(P/'INPUT-SEAL.json')['files'].items():check('input before fitting:'+f,h(P/f)==s)
old=read(A2/'DELIVERY-HASHES.json')
for f in old['files']:check('attempt2 unchanged:'+f['path'],h(A2/f['path'])==f['sha256'])
cohort=read(P/'TRAP-COHORT.json');coverage=read(P/'TRAP-COVERAGE.json')
for part in ('train','held'):
 hh=cohort['readings']['H'][part];ff=cohort['readings']['F'][part]
 check(part+'40 native-readable pairedlines',len(hh)==len(ff)==40 and [r['locus'] for r in hh]==[r['locus'] for r in ff] and all(all(w is not None for w in r['tokens']) for r in hh+ff))
 check(part+' first40 eligible sourcelines',[x['locus'] for x in coverage if x.get('partition')==part and x.get('native_eligible')][:40]==[r['locus'] for r in hh])
check('native exclusion ledger retained',sum('native unreadable slot or empty line' in x['reason'] for x in coverage)==18)
for name in ('CLEAN','CORRUPT','NOISY-H','NOISY-F','TRAP-H','TRAP-F'):
 c=read(P/(name+'-C1-ONLY.json'));k=c['key'];obs=c['observed'];final=q['cases'][name]
 data=read(P/('KNOWN-DATA.json' if name in ('CLEAN','CORRUPT') else name+'-DATA.json'))
 mode='training_whole_word' if name.startswith('TRAP') else 'known_initial_a';validate_source(data['train'],k,mode);validate_source(data['held'],k,mode);custody_check(k,data['train'],data['held'])
 check(name+' raw source/tokenizer andcustody',True)
 for kind,seed in [('original',c['original_seed']),('role',c['role_seed'])]:
  ks=keybank(k,kind,seed);expected=[digest(z) for z in ks];br=bankread(P/'banks'/(name+'-'+kind+'-real.json'));check(name+kind+'1000 realbankkeys',len(br['scores'])==1000 and br['key_hashes']==expected)
  if kind=='role':check(name+' all1000roleK invariants',all(invariants(k,z) and complexity(z)==complexity(k) for z in ks))
  fin=final[kind];gains=0
  for e,m in fin['metrics'].items():
   if 'mc_p' not in m:continue
   vals=[z[e]['value'] for z in br['scores']];tail=(1+sum(x>=m['value'] for x in vals))/1001
   check(name+kind+e+' upper tail',tail==m['mc_p']);check(name+kind+e+' median',statistics.median(vals)==m['C3_median']);gains+=m['gain_bits']
  check(name+kind+' coherence arithmetic',math.isclose(gains-complexity(k),fin['coherence_bits'],abs_tol=1e-8))
  for label,z in fin['matched_controls'].items():
   e,control=label.split(':',1);filename=name+'-'+kind+'-'+control.replace(':','-')+'.json';cb=bankread(P/'banks'/filename);check(name+kind+label+'same1000keys',cb['key_hashes']==expected)
   threshold=sorted(x[e]['value'] for x in cb['scores'])[949];check(name+kind+label+' exact95comparison',threshold==z['control_C3_p95'] and z['exceeds']==(z['real_value']>threshold))
  check(name+kind+' six C2families complete',all(any(label.endswith('C2:'+fam) for label in fin['matched_controls']) for fam in ('G1','G2','G3','G4','G5','G6')))
 a=final['original'];b=final['role'];same99=set(a['above_99'])&set(b['above_99']);same998=set(a['above_998'])&set(b['above_998']);pass0=a['verdict']==b['verdict']=='PASS' and len(same99)>=2;expected_label='PASS' if pass0 else 'PARTIAL' if same998 else 'FAIL';check(name+' independentcombinedverdict',final['combined']['verdict']==expected_label)
 if name.startswith('TRAP'):check(name+' finiteE3E4 withno ambiguousslots',all(obs[e]['value'] is not None for e in ('E3','E4')) and obs['E6']['ambiguous_or_unknown']==0)
negative=read(P/'NEGATIVE-FINAL.json')
for kind in ('original','role'):
 rr=[x for x in negative if x['cohort']==kind];n=len(rr);tally=dict(Counter(x['result']['combined']['verdict'] for x in rr));p=tally.get('PASS',0);record=q['negative'][kind]
 check(kind+'200 freshproposals',n==200 and tally==record['tally']);upper=record['CP95_upper']
 if p==0:check(kind+' independentCPclosedform',abs(upper-(1-.05**(1/n)))<1e-12)
 else:check(kind+' independentfinitebinomialCP',abs(sum(math.comb(n,j)*upper**j*(1-upper)**(n-j) for j in range(p+1))-.05)<1e-10)
 check(kind+' negativegate',record['gate']==(1-p/n>=.99 and upper<=.03))
check('overall status reflects allgates',(q['status']=='QUALIFIED_V7.2_ON_DECLARED_SCOPE')==all(q['gates'].values()))
check('no vault result',(P/'VAULT-RESULT.json').exists() is False and (B/'VAULT-RESULT.json').exists() is False)
r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(P),'-p','test_v72.py','-v'],capture_output=True,text=True);(P/'TEST-LOG.txt').write_text(r.stdout+r.stderr);check('6 exactscore/input/control regressiontests',r.returncode==0 and 'Ran 6 tests' in r.stderr)
out={'status':'VERIFIED','check_count':len(checks),'checks':checks,'tests':6,'qualification_status':q['status'],'old_attempt2_files_preserved':len(old['files']),'vault_tests':0};(P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
