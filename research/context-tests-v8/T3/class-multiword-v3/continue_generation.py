from pathlib import Path
import json,sys,subprocess,hashlib,importlib.util
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
def worker(gn,trial):
 spec=importlib.util.spec_from_file_location('frozen_generation',R/'generate_controls.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref);gi={'Latin':0,'scribe1':10000,'scribe2':20000}[gn];seed=863600000+gi+trial;name=f'G6-{gn}-{trial:03}';folder=R/'controls'/name;folder.mkdir(exist_ok=False);shapes=ref.geometry(name,load(R/'GEOMETRIES.json')['geometries'][gn]);save(folder/'GEOMETRY.json',shapes);row=dict(name=name,family='G6',geometry=gn,trial=trial,seed=seed,status='PENDING',geometry_sha256=sha(folder/'GEOMETRY.json'),execution='isolated unstarted-trial continuation')
 try:
  sizes=[p['length'] for p in shapes];gg=ref.generate('G6',{},seed,line_lengths=sizes);words=[''.join(w) for ln in gg['lines'] for w in ln];save(folder/'NATIVE-MECHANISM.json',dict(table=gg['table'],grille_offsets=gg['grille_offsets'],fidelity=gg['fidelity'],draws=gg['draws']));row.update(generated_tokens=len(words),unused_tail_tokens=0,published_source=False);assert len(words)==sum(sizes);paras=[];at=0
  for p in shapes:
   a=words[at:at+p['length']];at+=p['length']
   for i in p['unknown']:a[i]=None
   paras.append(dict(folio=p['folio'],paragraph=p['paragraph'],arm=p['arm'],tokens=a))
  save(folder/'PARAGRAPHS.json',paras);row.update(status='GENERATED',paragraphs=len(paras),folios=len({p['folio'] for p in paras}),original_slots=at,unknown_slots=sum(w is None for p in paras for w in p['tokens']),paragraphs_sha256=sha(folder/'PARAGRAPHS.json'))
 except Exception as ex:row.update(status='FAILED',error=repr(ex))
 save(folder/'GENERATION.json',row)
def main():
 freeze=load(R/'CONTINUATION-CODE-SEAL.json');assert all(sha(p)==h for p,h in freeze['files'].items());rows=load(R/'history/GENERATION-LEDGER-interrupted.json');assert len(rows)==693;folder=R/'controls/G6-Latin-093';assert not (folder/'GENERATION.json').exists();row=dict(name='G6-Latin-093',family='G6',geometry='Latin',trial=93,seed=863600093,status='FAILED',error='INTERRUPTED: original worker exited before a generation receipt',geometry_sha256=sha(folder/'GEOMETRY.json'));save(folder/'GENERATION.json',row);rows.append(row);save(R/'GENERATION-LEDGER.json',rows)
 for gn,start in [('Latin',94),('scribe1',0),('scribe2',0)]:
  for trial in range(start,200):
   name=f'G6-{gn}-{trial:03}';folder=R/'controls'/name;assert not folder.exists();rr=subprocess.run([sys.executable,'-B',str(R/'continue_generation.py'),'--worker',gn,str(trial)],cwd=R,capture_output=True,text=True);folder.mkdir(exist_ok=True);(folder/'worker-stdout.txt').write_text(rr.stdout,encoding='utf-8');(folder/'worker-stderr.txt').write_text(rr.stderr,encoding='utf-8')
   if (folder/'GENERATION.json').exists():row=load(folder/'GENERATION.json')
   else:row=dict(name=name,family='G6',geometry=gn,trial=trial,seed=863600000+{'Latin':0,'scribe1':10000,'scribe2':20000}[gn]+trial,status='FAILED',error='ISOLATED WORKER EXIT WITHOUT RECEIPT',returncode=rr.returncode);save(folder/'GENERATION.json',row)
   rows.append(row);save(R/'GENERATION-LEDGER.json',rows)
   if len(rows)%10==0:print('continued',len(rows),row['status'],flush=True)
 assert len(rows)==1200;save(R/'GENERATION-SUMMARY.json',dict(status='COMPLETE WITH INVALID TRIALS; QUALIFICATION BLOCKED',datasets=1200,valid=sum(r['status']=='GENERATED' for r in rows),failures=[r for r in rows if r['status']!='GENERATED'],attempted_all_scheduled_trials=True,retries=0));print('FIXED BANK COMPLETE',flush=True)
if __name__=='__main__':
 if '--worker' in sys.argv:worker(sys.argv[2],int(sys.argv[3]))
 else:main()
