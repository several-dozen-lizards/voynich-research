from pathlib import Path
import collections,hashlib,importlib.util,itertools,json
import numpy as np
from method import transform,maximums,rotation_p,inject_target
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
protocol={
 'purpose':'Resolve v75 finite pooled-tail-rank precision failure without narrowing its search family. Qualify numeric correction before any manuscript score matrix is opened for rescoring.',
 'method':'For every contrast j use pooled observed+permutation mean mu_j and scale sqrt(pooled variance_j + 1 count^2), z=(D-mu)/scale. Each row maximum is max_j abs(z). Selected target family p=(1+#null row maxima>=abs(z_observed))/(B+1). All transforms symmetric in rows; no Gaussian p approximation. Zero-variance columns retained with scale1. One count^2 regularizer fixed to native integer D resolution, not tuned.',
 'family':'Unchanged v75 per-panel candidate openings, pair columns, both signs and 14 separate reading/hand/section/variety/rawP panels. Same saved4999permutations after qualification only; no new candidate selection, no pooling hands/HF, no extra shuffles to force a pass. Bonferroni x14 retained.',
 'qualification_geometry':'Only panel_index and comparison-count metadata read from v75 precision ledger. No manuscript scores or word tokens used in stress banks. Eight independently seeded synthetic joint-score banks; each14panels of4096exchangeable integer rows with the actual family dimensions. Correlated columns, variable count scales, arbitrary position-only mean bias, rare +/-1-count columns and constants included. These are numerical joint-score controls, not independent historical texts or semantic qualification.',
 'null_gate':'Within each bank all4096rows are exhaustively treated as pseudo-observations after a symmetric transform. Global false flags after per-panel maxT and Bonf14 must be<=floor(.05*4096). This checks the finite-row global-null rank bound; rotations are dependent, not4096 independent experiments or an external empirical error-rate estimate.',
 'precision_gate':'Per-panel empirical smallest row-maximum rank p after x14 must be<=.01 in every synthetic panel. The theoretical strict minimum14/4096=.00341796875 is below.01 independent of number of pair columns. Ties may make empirical precision worse; keep them.',
 'power_controls':'For each bank/panel,64 fixed distinct pseudo-observation rows receive a signed positive injection into one designated anonymous contrast of 2,4,6,8 times its unregularized null SD. Other family contrasts unchanged, all means/scales/maxima recomputed symmetrically. Record every dose; do not gate moderate-dose power. Require>=90% detection at8SD in EVERY bank and EVERY panel. Report same-bank reuse/dependence, not independent-trial precision.',
 'paired_reading_control':'On the same64pseudo-observation positions inject8SD in H-shaped panel only, leave corresponding F panel null. Requiring both readings to pass must not exceed5% false paired flags per bank/panel-pair. Shapes/labels here are metadata, not real transcription replicas.',
 'end_to_end_checks':'Import unchanged frozen v75 encoder/counting code on authored toy lines only. Enumerate a small exact within-line permutation orbit with unknown barriers and endpoints, verify every count against direct membership comparison and maxT tail ranks against brute force. Orbit resolution can be too coarse and is not a power gate. No real words loaded. Independently check shift, scale, constant-column and row-permutation invariance of numeric transform as applicable (count-unit regularizer intentionally prevents exact scale invariance).',
 'failure_policy':'Freeze all scripts/protocol before controls. Any failed gate stops without manuscript rescoring. Preserve all banks, failures, dose results and diagnostic limits. No tuning after outcomes.',
 'interpretation':'A passing qualification establishes numerical precision/calibration properties and planted sensitivity under these generators, not validity of all possible linguistic nulls or meanings. Original v75 failures remain. Existing rawP within-line null does not fix every interior ordinal or eliminate all word-boundary mechanisms.'}
sources=[P/'opening-order-audit-v75/FAMILY-PRECISION.json',P/'opening-order-audit-v75/engine.py',P/'opening-order-audit-v75/FREEZE.json']
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['method.py','qualify.py','rescore.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
meta=load(sources[0]);sizes=[int(p['comparisons']) for p in meta];M=len(sizes);assert M==14

# Small complete orbit: this imports old code but never loads old manuscript data.
spec=importlib.util.spec_from_file_location('old_encoder',P/'opening-order-audit-v75/engine.py');enc=importlib.util.module_from_spec(spec);spec.loader.exec_module(enc)
templates=[['EDGE','shaa','qokbb','x','END'],['EDGE','qokcc','shdd','x','END'],['EDGE','shaa',None,'qokbb','x','END']]
rows=[dict(page='toy',folio='f'+str(i+1),locator='toy'+str(i+1),tokens=ws) for i,ws in enumerate(templates)];prep=enc.prepare(rows);variations=[]
for ws in templates:
 if None in ws:
  variations.append([ws[:3]+list(p)+['END'] for p in itertools.permutations(ws[3:-1])])
 else:variations.append([[ws[0]]+list(p)+[ws[-1]] for p in itertools.permutations(ws[1:-1])])
orbit=[]
for combo in itertools.product(*variations):
 flat=np.array([prep['wordid'][w] if w is not None else -1 for ws in combo for w in ws],dtype=np.int32);c,v=enc.count(flat,prep)
 for i,A in enumerate(prep['labels']):
  for j,B in enumerate(prep['labels']):
   direct=sum(enc.belongs(a,A) and enc.belongs(b,B) for ws in combo for a,b in zip(ws,ws[1:]) if a is not None and b is not None);assert c[i,j]==direct
 orbit.append(v)
orbit=np.array(orbit);om,os,ox=maximums(orbit);_,_,oz=transform(orbit)
assert np.allclose(ox,np.abs(oz).max(axis=1))
for j in range(orbit.shape[1]):
 for r in range(len(orbit)):assert np.mean(ox>=abs(oz[r,j])-1e-12)==sum(max(abs(z))>=abs(oz[r,j])-1e-12 for z in oz)/len(oz)
assert np.count_nonzero(rotation_p(ox,1)<=.05)<=int(.05*len(orbit))
rng=np.random.default_rng(77000);a=rng.integers(-12,13,size=(73,11));mu,sd,z=transform(a);m2,s2,z2=transform(a+17);assert np.allclose(z,z2)
order=rng.permutation(len(a));_,_,zp=transform(a[order]);assert np.allclose(zp,z[order]);assert np.all(transform(np.zeros((17,4)))[1]==1)
save('EXACT-ORBIT.json',dict(rows=len(orbit),columns=orbit.shape[1],direct_class_counts='pass',all_orbit_tail_counts='pass',rank_bound='pass',precision_limit='Small authored orbit only; not enough resolution for14-panel .05 screening.',shift_and_row_symmetry='pass'))

banks=[];N=4096;RPTS=64;doses=[2,4,6,8]
for bank in range(8):
 rng=np.random.default_rng(77100+bank);maxima=[];targets=[];othermax=[];scales=[];mins=[]
 # Joint latent factors create overlapping/correlated class-like contrasts.
 for pi,K in enumerate(sizes):
  factors=rng.normal(size=(N,12)).astype(np.float32);mx=np.zeros(N);omx=np.zeros(N);target=None
  for lo in range(0,K,128):
   k=min(128,K-lo);ix=np.arange(lo,lo+k);sigma=rng.choice(np.array([1.,3.,8.,24.]),size=k);mean=rng.integers(-80,81,size=k)
   noise=rng.normal(size=(N,k)).astype(np.float32);x=np.rint(mean+sigma*(.7*factors[:,ix%12]+.714142842854285*noise)).astype(np.float32)
   if bank in [1,3,5,7]:
    rare=(ix%7==0);x[:,rare]=(rng.random((N,int(rare.sum())))<.002)*rng.choice([-1.,1.],size=(N,int(rare.sum())))
   const=(ix%29==0);x[:,const]=mean[const]
   # Designated anonymous contrast is nonconstant, of fixed count scale8.
   if lo==0:
    x[:,0]=np.rint(11+8*(.7*factors[:,0]+.714142842854285*rng.normal(size=N)));target=x[:,0].astype(float)
   _,_,zz=transform(x);absz=np.abs(zz);mx=np.maximum(mx,absz.max(axis=1))
   if lo==0:
    if k>1:omx=np.maximum(omx,absz[:,1:].max(axis=1))
   else:omx=np.maximum(omx,absz.max(axis=1))
  maxima.append(mx);othermax.append(omx);targets.append(target);scales.append(float(np.std(target)));mins.append(float(np.min(rotation_p(mx,M))))
  print('bank',bank+1,'panel',pi+1,flush=True)
 panelps=np.array([rotation_p(mx,M) for mx in maxima]);global_flags=int(np.count_nonzero(np.any(panelps<=.05,axis=0)));selected=rng.choice(N,size=RPTS,replace=False);dose_results=[];strongpass=True
 for pi in range(M):
  hits={dose:0 for dose in doses}
  for r in selected:
   for dose in doses:hits[dose]+=inject_target(othermax[pi],targets[pi],int(r),dose,scales[pi],M)<=.05
  strongpass &= hits[8]/RPTS>=.9;dose_results.append(dict(panel_index=pi,shape_columns=sizes[pi],detections={str(k):int(v) for k,v in hits.items()},trials=RPTS,null_SD=scales[pi]))
 paired=[]
 for pi in range(0,M,2):
  wrong=0
  for r in selected:
   ph=inject_target(othermax[pi],targets[pi],int(r),8,scales[pi],M);base=abs((targets[pi+1][r]-targets[pi+1].mean())/np.sqrt(targets[pi+1].var()+1));pf=min(1,M*np.mean(maxima[pi+1]>=base-1e-12));wrong+=ph<=.05 and pf<=.05
  paired.append(dict(H_shaped_panel=pi,F_shaped_panel=pi+1,false_both_pass=int(wrong),trials=RPTS))
 q=dict(bank=bank+1,seed=77100+bank,null_pseudotrial_rows=N,global_null_flags=global_flags,null_fraction=global_flags/N,minimum_achievable_panel_adjusted_p=mins,dose_results=dose_results,H_only_paired_controls=paired,
  null_gate=global_flags<=int(.05*N),precision_gate=all(v<=.01 for v in mins),strong_power_gate=bool(strongpass),paired_gate=all(x['false_both_pass']/RPTS<=.05 for x in paired))
 q['passes']=all(q[k] for k in ['null_gate','precision_gate','strong_power_gate','paired_gate']);banks.append(q)
 np.savez_compressed(R/(f'bank-{bank+1:02d}-diagnostics.npz'),panel_maxima=np.array(maxima),anonymous_target_scores=np.array(targets),other_maxima=np.array(othermax),selected_rows=selected)
 save('QUALIFICATION-PROGRESS.json',dict(completed_banks=len(banks),banks=banks));print('BANK DONE',bank+1,'passes',q['passes'],'null',global_flags,flush=True)
result=dict(status='PASS' if all(q['passes'] for q in banks) else 'FAIL',banks=banks,exact_orbit='pass',actual_family_dimensions=sizes,limits='Numerical correction qualification only. Rotations share banks; planted controls share null rows. No manuscript score loaded and no semantic/historical null validation claimed.')
save('QUALIFICATION.json',result);print(result['status'],flush=True)
