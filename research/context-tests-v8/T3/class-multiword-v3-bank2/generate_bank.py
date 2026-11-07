from pathlib import Path
import json,sys,subprocess,hashlib,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
def main():
 seal=load(R/'PRE-GENERATION-SEAL.json');assert all(sha(p)==h for p,h in seal['files'].items());spec=importlib.util.spec_from_file_location('native_worker',R/'generate_one.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref);ref.verify_source();rows=[]
 for plan in load(R/'TRIAL-PLAN.json'):
  folder=R/'controls'/plan['name'];assert not folder.exists();rr=subprocess.run([sys.executable,'-B',str(R/'generate_one.py'),plan['family'],plan['geometry'],str(plan['trial'])],cwd=R,capture_output=True,text=True);folder.mkdir(parents=True,exist_ok=True);(folder/'worker-stdout.txt').write_text(rr.stdout,encoding='utf-8');(folder/'worker-stderr.txt').write_text(rr.stderr,encoding='utf-8')
  if (folder/'GENERATION.json').exists():row=load(folder/'GENERATION.json')
  else:row=dict(plan,status='FAILED',error='ISOLATED WORKER EXIT WITHOUT RECEIPT',returncode=rr.returncode);save(folder/'GENERATION.json',row)
  assert all(row[k]==v for k,v in plan.items());rows.append(row);save(R/'GENERATION-LEDGER.json',rows)
  if len(rows)%10==0:print('generated',len(rows),row['status'],flush=True)
 assert len(rows)==1200;bad=[r for r in rows if r['status']!='GENERATED'];save(R/'GENERATION-SUMMARY.json',dict(status='COMPLETE' if not bad else 'COMPLETE WITH INVALID TRIALS',datasets=1200,valid=1200-len(bad),failures=bad,retries=0,isolated_workers=1200));print('BANK COMPLETE',flush=True)
if __name__=='__main__':main()
