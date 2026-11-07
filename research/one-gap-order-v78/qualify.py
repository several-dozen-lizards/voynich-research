from pathlib import Path
import collections,hashlib,importlib.util,itertools,json
import numpy as np
from engine import prepare,count,base
R=Path(__file__).resolve().parent;P=R.parent
spec=importlib.util.spec_from_file_location('maxT_method',P/'opening-maxT-qualification-v77/method.py');method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
protocol={
 'question':'Exactly one readable intervening source token: sh X qok versus qok X sh. One lag only, source positions i andi+2, allthree tokens readable. No line or unknown bridging.',
 'scope':'Unchanged v77 Bath hand2/B/rawP and Starred hand3/B/rawP, H/F separate on shared eligible loci, alloriginaleligiblefolios inclf75. No botanical/ambiguous-hand pooling. Classification and opening search family inherited unchanged fromv75/v77.',
 'views':'Primary any_middle includes every readable middle word. Predeclared sensitivity non_target_middle excludes middle words beginning sh or qok. This fixed target-based filter is applied to all candidate end-class pairs for its search maximum; not claimed as a pair-specific generic filter. Recompute filter each permutation.',
 'null':'4999 within-line permutations per reading/stratum, same endpoints and uncertainty barriers fixed and same per-line word multisets. Both views share each permutation. Seeds7800+original v75 panel index. Exact interior ordinals and local transition counts are not held fixed.',
 'correction':'Unchanged v77 symmetric count-unit-regularized maxT over ALL original end-opening pairs, both signs. Original14panel factor retained, doubled for the two middle definitions: x28 although only4actual reading/stratum panels are run. New lag2 is user-prespecified, not a lag search. Existinglag1findings are reference only.',
 'qualification':'Before manuscript lag scores: exact authored permutation-orbit gap counts/unknown/line barriers and middle filters versus independent enumeration. Reuse v77 PASS numerical banks only after hash checks, recheck their full28-view rank bound/precision and8SDpower/paired controls. Treat two views as correlated; duplicating bank maxima is a numerical worst-union-bound check, not independent controls. Require globalflags<=floor(.05*4096), attainableadjustedp<=.01,>=90%8SDdetections in everybank/panel, pairedfalse<=5%. Any failure stops manuscript run.',
 'boundary_counterexample':'Predefined first-order Markov toy: shaa -> qokbb or m equiprobably; m->qokbb->r->t->shaa. It contains no state beyond the current token. Record adjacent and one-gap directions without assigning it to the manuscript. A surviving one-gap preference cannot logically rule out local transition chaining.',
 'preserve':'All source gap events in both directions, middle words and their classes, excluded target-middle cases, per-folio zeros/negative effects, every qualified/nonpassing view, complete null score matrices and maxima. H/F tokenization remains separate: one source-word gap is not a glyph-aligned distance.',
 'limits':'Gap survival establishes arrangement beyond immediate adjacency under THIS line-shuffle null, not grammar versus boundary as an exhaustive dichotomy. Chained first-order effects can propagate; genuine grammatical dependencies can also be strictly local. Failure may reflect power. Two known hands do not rule out shared conventions, copying or common training; starred text is not the recipe section.'}
sources=[P/'opening-maxT-qualification-v77/method.py',P/'opening-maxT-qualification-v77/QUALIFICATION.json',P/'opening-order-audit-v75/engine.py',P/'opening-order-audit-v75/FREEZE.json']
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','qualify.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
oldq=load(sources[1]);assert oldq['status']=='PASS'
templates=[['EDGE','shaa','m','qokbb','END'],['EDGE','qokcc','shdd','x','END'],['EDGE','shaa',None,'qokbb','x','END']];rows=[dict(page='toy',folio='f'+str(i),locator='toy'+str(i),tokens=ws) for i,ws in enumerate(templates)];p=prepare(rows);variations=[]
for ws in templates:variations.append([ws[:3]+list(v)+['END'] for v in itertools.permutations(ws[3:-1])] if None in ws else [[ws[0]]+list(v)+[ws[-1]] for v in itertools.permutations(ws[1:-1])])
checked=0
for combo in itertools.product(*variations):
 arr=np.array([p['wordid'][w] if w is not None else -1 for ws in combo for w in ws],dtype=np.int32)
 for mode in [False,True]:
  c,_=count(arr,p,mode)
  for i,A in enumerate(p['labels']):
   for j,B in enumerate(p['labels']):
    direct=0
    for ws in combo:
     for a,m,b in zip(ws,ws[1:],ws[2:]):
      if a is None or m is None or b is None or (mode and m.startswith(('sh','qok'))):continue
      direct+=base.belongs(a,A) and base.belongs(b,B)
    assert c[i,j]==direct
  checked+=1
# Preserve word/line/unknown/endpoints through the unchanged shuffled slot lists.
rng=np.random.default_rng(78000);arr=p['original'].copy()
for indices in p['buckets']:arr[indices]=rng.permutation(arr[indices]);assert collections.Counter(arr[indices])==collections.Counter(p['original'][indices])
assert np.array_equal(arr<0,p['original']<0)
banks=[]
for b in oldq['banks']:
 data=np.load(P/'opening-maxT-qualification-v77'/(f'bank-{b["bank"]:02d}-diagnostics.npz'));mx=data['panel_maxima'];other=data['other_maxima'];targets=data['anonymous_target_scores'];selected=data['selected_rows'];ps=np.array([method.rotation_p(x,28) for x in mx]);globalflags=int(np.count_nonzero(np.any(ps<=.05,axis=0)));mins=[float(np.min(method.rotation_p(x,28))) for x in mx];power=[];paired=[]
 for pi in range(14):
  hit=sum(method.inject_target(other[pi],targets[pi],int(r),8,float(np.std(targets[pi])),28)<=.05 for r in selected);power.append(dict(panel_index=pi,hits=int(hit),trials=len(selected)))
 for pi in range(0,14,2):
  wrong=0
  for r in selected:
   ph=method.inject_target(other[pi],targets[pi],int(r),8,float(np.std(targets[pi])),28);target=targets[pi+1];z=abs((target[r]-target.mean())/np.sqrt(target.var()+1));pf=min(1,28*np.mean(mx[pi+1]>=z-1e-12));wrong+=ph<=.05 and pf<=.05
  paired.append(dict(pair=pi//2,false_both=int(wrong),trials=len(selected)))
 q=dict(bank=b['bank'],rows=4096,null_flags=globalflags,minimum_adjusted_p=mins,strong_power=power,H_only_paired=paired);q['passes']=globalflags<=int(.05*4096) and all(x<=.01 for x in mins) and all(x['hits']/x['trials']>=.9 for x in power) and all(x['false_both']/x['trials']<=.05 for x in paired);banks.append(q);print('qualified bank',b['bank'],q['passes'],flush=True)
rng=np.random.default_rng(78001);tokens=[];state='shaa'
for k in range(4096):
 tokens.append(state)
 state=('qokbb' if rng.random()<.5 else 'm') if state=='shaa' else {'m':'qokbb','qokbb':'r','r':'t','t':'shaa'}[state]
lines=[tokens[i:i+16] for i in range(0,len(tokens),16)];counts={}
for lag in [1,2]:
 f=r=0
 for ws in lines:
  for a,b in zip(ws,ws[lag:]):f+=a.startswith('sh') and b.startswith('qok');r+=a.startswith('qok') and b.startswith('sh')
 counts[str(lag)]=dict(forward=f,reverse=r)
save('LOCAL-CHAIN-COUNTEREXAMPLE.json',dict(transition_rule='shaa -> qokbb or m, m->qokbb->r->t->shaa; memory is current state only',seed=78001,tokens=4096,line_length=16,counts=counts,interpretation='A one-gap preference is possible under strictly first-order transitions. This is a logical counterexample, not a fitted manuscript model.'))
status='PASS' if all(x['passes'] for x in banks) else 'FAIL';save('QUALIFICATION.json',dict(status=status,authored_orbit_views_checked=checked,direct_gap_class_count='pass',unknown_line_and_filter_barriers='pass',banks=banks,limits='Numerical/counter verification only, not semantic or complete boundary-model qualification. Reused correlated bank views are not independent.'))
print(status,flush=True)
