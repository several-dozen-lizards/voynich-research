"""Independent stdlib-only verification of saved control banks; no random draws."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from itertools import permutations
import ast,bisect,hashlib,json,math,struct,sys,zipfile
from array import array
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   b=f.read(65536)
   if not b:break
   h.update(b)
 return h.hexdigest()
bankpaths=sorted(R.glob('panel-*-calibration.npz'))
inputs=[R/'verify_stream.py',R/'QUALIFICATION.json',R/'SUPPORT-PLAN.json',R/'FIXTURES.json',R/'FAMILY.json']+bankpaths+sorted(R.glob('panel-*-minima.json'))
vf={str(p):sha(p) for p in inputs}
if (R/'STREAM-VERIFY-FREEZE.json').exists():assert load(R/'STREAM-VERIFY-FREEZE.json')==vf
else:save('STREAM-VERIFY-FREEZE.json',vf)
f=load(R/'FREEZE.json')
for n,h in f['local_sha256'].items():assert sha(R/n)==h
for n,h in f['historical_sha256'].items():assert sha(P/n)==h
def state(w):return 0 if w.startswith('sh') else 1 if w.startswith('qok') else 2
def belongs(w,l):return w.startswith(l[7:]) if l.startswith('prefix:') else w.startswith(('l','s')) if l=='union:l/s' else w in ('ol','or')
def edges(s):return Counter((state(a),state(b)) for a,b in zip(s,s[1:]))
def direct(s,A,B,neutral):return sum(int(belongs(a,A) and belongs(c,B))-int(belongs(a,B) and belongs(c,A)) for a,b,c in zip(s,s[1:],s[2:]) if not neutral or state(b)==2)
def conv(a,b):
 o=Counter()
 for x,n in a.items():
  for y,m in b.items():o[x+y]+=n*m
 return dict(o)
def tail(h):
 T=sum(h.values());M=sum(d*n for d,n in h.items());dis={d:abs(d*T-M) for d in h}
 return {d:Fraction(sum(n for x,n in h.items() if dis[x]>=dis[d]),T) for d in h}
def header(fh):
 assert fh.read(6)==b'\x93NUMPY';version=fh.read(2);assert version==b'\x01\x00';n=struct.unpack('<H',fh.read(2))[0];return ast.literal_eval(fh.read(n).decode('latin1').strip())
q=load(R/'QUALIFICATION.json');panels=load(R/'FAMILY.json');fixture=next(x for x in load(R/'FIXTURES.json') if x['name']=='positive32');row=fixture['rows'][0];assert fixture['rows']==[row]*32
orbit=tuple((row[0],)+s+(row[-1],) for s in sorted(set(permutations(row[1:-1]))) if edges((row[0],)+s+(row[-1],))==edges(row));assert len(orbit)==12
words=sorted(set(row));columns=0;bankcount=0;diagnosticmasschecks=0
for panel in panels:
 pairs=[(a,b) for i,a in enumerate(panel['labels']) for b in panel['labels'][i+1:]];assert len(pairs)==panel['class_pairs']
 keys={};reps=[];mapping=[];group_pairs=[]
 for j,(A,B) in enumerate(pairs):
  key=tuple(int(belongs(w,A))+2*int(belongs(w,B)) for w in words)
  if key not in keys:keys[key]=len(reps);reps.append(j);group_pairs.append((A,B))
  mapping.append(keys[key])
 for neutral in (False,True):
  tails=[];histograms=[]
  for A,B in group_pairs:
   one=Counter(direct(s,A,B,neutral) for s in orbit);h={0:1}
   for _ in range(32):h=conv(h,one)
   histograms.append(h);tails.append(tail(h))
  name=f'panel-{panel["panel_index"]:02d}-{int(neutral)}';expectedmin=[Fraction(*v) for v in load(R/(name+'-minima.json'))]
  with zipfile.ZipFile(R/(name+'-calibration.npz')) as z:
   with z.open('column_group.npy') as fh:
    h=header(fh);assert h['descr'] in ('<i4','=i4');a=array('i');a.frombytes(fh.read());assert list(a)==mapping
   with z.open('scores.npy') as fh:
    h=header(fh);assert h['shape']==(4096,len(pairs)) and h['descr'] in ('<i4','=i4') and not h['fortran_order'];assert sys.byteorder=='little' and array('i').itemsize==4
    for i in range(4096):
     a=array('i');a.frombytes(fh.read(4*len(pairs)));assert len(a)==len(pairs);g=[a[j] for j in reps];assert all(value==g[k] for value,k in zip(a,mapping));assert min(t[d] for t,d in zip(tails,g))==expectedmin[i]
    assert fh.read()==b''
  A,B=sorted(('prefix:sh','prefix:qok'));j=mapping[pairs.index((A,B))];D=32*direct(row,A,B,neutral);ordered=sorted(expectedmin);pv=min(Fraction(1),28*Fraction(1+bisect.bisect_right(ordered,tails[j][D]),4097));rec=next(x for x in q['records'] if x.get('panel_index')==panel['panel_index'] and x.get('fixture')=='positive32' and x.get('view')==('non_target_middle' if neutral else 'any_middle'));assert rec['positive_adjusted_p']==[pv.numerator,pv.denominator]
  for d in rec['scope_diagnostics']:
   one=Counter()
   for s in orbit:
    if d['regime']=='position_weights':w=4**(int(s[1].startswith('sh'))+int(s[3].startswith('qok')))
    elif d['regime']=='repeated_template':w=16**sum((a,b,c)==('shedy','ol','qokedy') for a,b,c in zip(s,s[1:],s[2:]))
    else:w=4**sum((a,b) in [('shedy','ol'),('ol','qokedy')] for a,b in zip(s,s[1:]))
    one[direct(s,A,B,neutral)]+=w
   h={0:1}
   for _ in range(32):h=conv(h,one)
   mass=Fraction(sum(n for value,n in h.items() if min(Fraction(1),28*Fraction(1+bisect.bisect_right(ordered,tails[j][value]),4097))<=Fraction(1,20)),sum(h.values()));assert d['exact_target_rejection_mass']==[mass.numerator,mass.denominator];assert d['target_flags']==sum(Fraction(*p)<=Fraction(1,20) for p in d['target_p']);assert d['family_flags']==sum(Fraction(*p)<=Fraction(1,20) for p in d['family_p']);diagnosticmasschecks+=1
  columns+=len(pairs);bankcount+=1;print('VERIFIED',name,flush=True)
assert len([x for x in q['records'] if 'panel_index' in x])==56
assert q['status']==('PASS_STAGE1_CONTROLS_ONLY' if all(x['pass_gate'] for x in q['records']) else 'FAIL_STAGE1')
for x in q['records']:
 if 'cdf_pass' in x:assert x['cdf_pass']==(max(x['max_marginal_CDF_error'],x['literal_orbit_CDF_error'])<=x['CDF_limit'])
plan=load(R/'SUPPORT-PLAN.json');assert plan['absolute_CDF_error_limit']==math.sqrt(math.log(2*max(1,plan['full_family_support_points'])/.001)/(2*4096))
old=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert old['status']=='FAIL' and old['robustness_banks_not_run']==[2,3]
save('VERIFICATION.json',dict(method='Independent stdlib-only row-wise verifier; direct literal-permutation histograms, not the tested signature DP',frozen_files='PASS',full_family_columns_replayed=columns,calibration_rows=4096,calibration_banks_replayed=bankcount,all_minima_and_positive_p='PASS',scope_diagnostic_exact_masses_replayed=diagnosticmasschecks,control_records=56,gate_status_replay='PASS',actual_layout_power='NOT RUN',manuscript_score='NOT COMPUTED',original_execution_and_replay_resource_failures='preserved',v98='FAIL unchanged; banks2/3 unrun'))
print(q['status'])
