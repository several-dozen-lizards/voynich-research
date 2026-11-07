import json,hashlib,random,statistics,math,sys,subprocess
from pathlib import Path
from collections import Counter
P=Path(__file__).parent;A2=P.parent/'attempt-2-v7.1';sys.path.insert(0,str(P.parent/'HARNESS'))
from harness import digest,random_key
from role_preserving_keys import random_role_key,invariants,role_signature
from source_controls import build_control
checks=[]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def check(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
seal=read(P/'CODE-SEAL.json');check('diagnostic code seal',sha(P/'diagnose.py')==seal['files']['diagnose.py']);check('plan seal',sha(P/'PLAN.json')==read(P/'PLAN-SEAL.json')['sha256'])
old=read(A2/'DELIVERY-HASHES.json')
for f in old['files']:check('attempt2 preserved:'+f['path'],sha(A2/f['path'])==f['sha256'])
structure={}
for r in ('H','F'):
 k=read(A2/('TRAP-'+r+'-KEY.json'));summary=read(P/('SUMMARY-'+r+'.json'));events=read(P/('TOKEN-RECEIPTS-'+r+'.json'));bank=read(P/('ORIGINAL-C3-DECOMPOSITION-'+r+'.json'));sensitivity=read(P/('STRATIFIED-SENSITIVITY-'+r+'.json'));oldbank=read(A2/('banks/TRAP-'+r+'-real.json'))
 check(r+' event denominators',len(events)==summary['slots'] and sum(e['real_hit'] for e in events)==summary['observed_hits'])
 check(r+' all1000 old E1totals',len(bank)==1000 and all(x['total']==y['E1']['success'] for x,y in zip(bank,oldbank['scores'])))
 check(r+' group totals allkeys',all(sum(z['groups'].values())==z['total'] for z in bank))
 check(r+' native rather than key uncertainty',sum(e['decode_unknown_origin']=='native' for e in events)==2 and not any(e['decode_unknown_origin']=='key' for e in events))
 check(r+' no memorized mapping excess',all(z['groups']['known_WORD']==summary['groups']['known_WORD']['real_hits'] for z in bank))
 check(r+' exactly5 fallbackhits',sum(e['real_hit'] for e in events if e['group']=='character_fallback')==5)
 p=(1+sum(z['total']>=summary['observed_hits'] for z in sensitivity))/1001;check(r+' independent sensitivity tail',p==summary['sensitivity_not_operational_C3']['p'])
 rng=random.Random(2719)
 for i,x in enumerate(sensitivity):
  z=random_role_key(k,rng)
  if digest(z)!=x['key_sha256'] or not invariants(k,z):raise AssertionError('structural role null mismatch')
 check(r+' role method equalsall1000 prespecified sensitivity draws',True)
 # Null-structure audit uses only declared KEY entries, not decoded semantics.
 active=[u for u in k['units'] if not role_signature(k,u)];value_counts=Counter(k['map'].values());dominant,nmax=value_counts.most_common(1)[0]
 rng=random.Random(719);emp=[]
 for _ in range(1000):
  z=random_key(k,rng);emp.append(sum(z['map'][u]==dominant for u in active))
 structure[r]={'default_active_no_context_units':len(active),'all_units':len(k['units']),'most_common_base_value':dominant,'base_value_count':nmax,'real_active_count':sum(k['map'][u]==dominant for u in active),'original_null_expected_active_count':len(active)*nmax/len(k['units']),'original_null_empirical_mean':statistics.mean(emp),'interpretation':'global value-frequency permutation follows v7; active-role value distribution is not preserved'}
 c1=read(P/('C1-SOURCE-FIRST-'+r+'.json'));raw=[];slices=read(A2/'TRAP-SLICES.json')['readings'][r]['held'];data=read(A2/('TRAP-'+r+'-DATA.json'))
 for row,s in zip(data['held'],slices):rr=dict(row,raw_words=s['tokens']);raw.append(rr)
 fixed,receipt=build_control(raw,k,'training_whole_word','C1-glyph',802);check(r+' validated control matchesdiagnostic',fixed==c1['rows']);check(r+' source spelling changes reconcile',receipt['changed_raw_words']==summary['source_C1b']['raw_words_changed'])
 c2=read(P/('C2-E1-'+r+'.json'))['families'];check(r+' complete6 C2diagnostics',len(c2)==6 and all(len(z['C3_hit_totals'])==1000 for z in c2.values()))
 for family,z in c2.items():check(r+' C2percentile:'+family,sorted(z['C3_hit_totals'])[949]/z['slots']==z['C3_p95_rate'])
(P/'NULL-STRUCTURE.json').write_text(json.dumps(structure,indent=2)+'\n')
test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(P),'-p','test*.py','-v'],capture_output=True,text=True);(P/'TEST-LOG.txt').write_text(test.stdout+test.stderr);check('20 diagnostic infrastructure tests',test.returncode==0 and 'Ran 20 tests' in test.stderr)
result={'status':'VERIFIED_DIAGNOSTIC_ONLY','checks':checks,'check_count':len(checks),'tests':20,'previous_attempt2_files_preserved':len(old['files']),'prior_verdict_changed':False,'vault_tests':0}
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
