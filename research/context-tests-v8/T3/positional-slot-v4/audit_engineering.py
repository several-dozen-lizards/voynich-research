from pathlib import Path
import sys,importlib.util,json
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('audit',R/'independent_audit.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);f=a.load('ENGINEERING-REFERENCE-FIXTURES.json');pp=f['paragraphs'];c=f['candidate'];d=a.ref.discover(a.classified(pp));assert all(d['candidate'][k]==c[k] for k in ['start','width','variants']);rng=a.ref.rand(f['seed'])
for fixture in f['fixtures']:
 qq=[]
 for p in pp:
  x=p['tokens'][:]
  for i in range(len(x)-1,1,-1):
   j=1+int(next(rng)*i);x[i],x[j]=x[j],x[i]
  qq.append(dict(p,tokens=x))
 assert a.digesttokens(qq)==fixture['raw_tokens_sha256'];assert a.digesttokens(a.classified(qq))==fixture['class_tokens_sha256'];a.ref.check_metric(a.ref.measure(a.classified(qq),c),fixture['metrics'])
rng=a.ref.rand(f['RNG_seed']);check={c['draw']:c['value'] for c in f['RNG_checkpoints']}
for i in range(1,max(check)+1):
 value=next(rng)
 if i in check:assert value==check[i]
a.save('INDEPENDENT-ENGINEERING-AUDIT.json',dict(status='PASS',authored_draws=len(f['fixtures']),RNG_draws_checked_through=max(check),RNG_checkpoints=len(check),scope='SeparatePythonwordclassification,positionmetrics,shufflehashesanduint32RNG;notpower'))
print('ENGINEERING REFERENCE PASS')
