from pathlib import Path
import collections,hashlib,json,random,re
import numpy as np
from engine import buckets,shuffled,frames,test
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
inputs=[P/'frequency-atlas-v48/rows.json',P/'category-extension-v61/RESULTS.json',P/'neighbor-patterns-v66/RESULTS.json']
protocol={
 'scope':'Same bath hand2, Currier B, raw P stratum and numbered-folio exclusions as v61/v66. Shared eligible H/F loci, each reading scored separately. No cross-reading independence claim.',
 'target':'shedy ___ shedy, every readable middle word in eligible lines. Statistics T=total exact flank-frame occurrences and R=number of distinct middle words each occurring in that exact frame across >=2 numbered folios. Two-folio recurrence is inherited from v66. No fixed semantic middle-word class.',
 'nulls':'Primary exact_slot: permute all readable words within page, line length, exact ordinal and identical unknown-slot mask. Sensitivity within_line: permute each contiguous readable interior span, fixing endpoints and unknown barriers. NO shedy or other word positions are locked except by slot constraints or within-line endpoints: fixing shedy positions would condition away frame recurrence.',
 'selection':'For every shuffle compute maximum T and maximum R over ALL ordered exact left/right flank-word pairs, including unequal flanks and any middle words, not only noticed candidate neighbours. This broadens the earlier inspected-frame family and conservatively adjusts frame selection. It is not frequency-normalized max scoring: common frames can set the threshold.',
 'calibration':'1999 shuffles per reading/null. Seeds H exact6901/within6902, F exact6903/within6904. Plus-one upper-tail raw and all-frame maximum p-values. Bonferroni x8 across H/F, both nulls and both statistics. Positive excess and eight-panel p<=.05 required for supported enrichment. Do not tune after outcomes.',
 'engineering':'Before manuscript outcomes: exact counts checked against hand-worked example; both schemes preserve bucket multisets, unknowns and declared position/frequency controls. 20 exchangeable/20 planted synthetic samples per scheme with199shuffles, target-T all-frame-max p screen <=.05. Frozen diagnostic gate <=4null flags and>=12plant detections. R power not qualified by this planted-T gate; report that limit.',
 'preservation':'Save target scores, all-frame maxima, every observed frame T/R, target middle counts/folios/source lines, one-folio members, H/F differences and background one-shedy-flank/unknown-middle cases. Keep zero and failed results.',
 'limits':'Retrospective exposed corpus, conservative all-frame raw-max correction, two conditional nulls rather than a full model of ordinary text. No semantic roles, morphological inference or independent confirmation. Failure is not absence of shared slots or language.'}
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['run.py','engine.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)

def invariant(rs,mode):
 bs=buckets(rs,mode);out=shuffled(rs,bs,random.Random(69))
 for r,ws in zip(rs,out):
  assert len(r['tokens'])==len(ws)
  assert [i for i,w in enumerate(r['tokens']) if w is None]==[i for i,w in enumerate(ws) if w is None]
  if mode=='within_line':assert collections.Counter(r['tokens'])==collections.Counter(ws) and r['tokens'][0]==ws[0] and r['tokens'][-1]==ws[-1]
 for b in bs:assert collections.Counter(rs[ri]['tokens'][i] for ri,i in b)==collections.Counter(out[ri][i] for ri,i in b)
toy=[['shedy','a','shedy'],['shedy','a','shedy'],['shedy','b','shedy'],['shedy',None,'shedy']]
t,r=frames(toy,['f1','f2','f1','f2']);assert t[('shedy','shedy')]==3 and r[('shedy','shedy')]==1
qualification=[]
for mi,mode in enumerate(['exact_slot','within_line']):
 flags=hits=0
 for trial in range(20):
  rng=random.Random(69000+trial);null=[];planted=[]
  for i in range(64):
   ws=['s']+[rng.choice(['a','b','c','d','e','f','shedy']) for _ in range(10)]+['t']
   p=ws[:]
   if i%2==0:
    j=4 if i%4==0 else 8;p[j-1]='shedy';p[j]=['a','b','c'][(i//2)%3];p[j+1]='shedy'
   meta={'page':'toy','folio':'f'+str(i%4)}
   null.append(dict(meta,tokens=ws));planted.append(dict(meta,tokens=p))
  for isplant,rs in [(False,null),(True,planted)]:
   invariant(rs,mode);o,_,_=test(rs,mode,199,69500+trial+100*mi)
   positive=o['results'][0]['observed']>o['results'][0]['null_mean'] and o['results'][0]['p_all_frames_max']<=.05
   if isplant:hits+=positive
   else:flags+=positive
  if (trial+1)%5==0:print('engineering',mode,trial+1,flush=True)
 qualification.append(dict(mode=mode,null_flags=flags,null_trials=20,planted_T_detections=hits,planted_trials=20,pass_gate=flags<=4 and hits>=12))
save('QUALIFICATION.json',{'results':qualification,'limits':'Engineering checks under one generator. Planted gate targets T only; no R power or historical validity claim.'})
if not all(x['pass_gate'] for x in qualification):raise SystemExit('Engineering gate failed; manuscript scoring not run; no tuning.')

raw=load(inputs[0]);old=load(inputs[1]);prior=next(g for g in old['groups'] if g['id']=='bath')
eligible=[r for r in raw if tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0] not in prior['excluded_folios']]
locs={tr:{r[6] for r in eligible if r[0]==tr} for tr in ['H','F']};shared=locs['H']&locs['F'];panels=[];observed={}
for ti,tr in enumerate(['H','F']):
 rs=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in eligible if r[0]==tr and r[6] in shared]
 totals,recur=frames([r['tokens'] for r in rs],[r['folio'] for r in rs]);members=collections.defaultdict(list);background=[];unknown=[]
 for row in rs:
  ws=row['tokens']
  for i in range(1,len(ws)-1):
   left,mid,right=ws[i-1:i+2]
   if left=='shedy' and right=='shedy':
    ev=dict(row,ordinal=i+1,middle=mid)
    if mid is not None:members[mid].append(ev)
    else:unknown.append(ev)
   elif left=='shedy' or right=='shedy':background.append(dict(row,ordinal=i+1,left=left,middle=mid,right=right))
 observed[tr]=dict(lines=len(rs),folios=len({r['folio'] for r in rs}),members={w:dict(count=len(es),folios=len({e['folio'] for e in es}),events=es) for w,es in sorted(members.items())},unknown_middle=unknown,one_flank_background=background,
  all_frames=[dict(left=l,right=r,T=n,R=recur[(l,r)]) for (l,r),n in sorted(totals.items(),key=lambda x:(-x[1],x[0]))])
 for mi,mode in enumerate(['exact_slot','within_line']):
  invariant(rs,mode);out,scores,maxima=test(rs,mode,1999,6901+2*ti+mi)
  for x in out['results']:x['p_eight_panels']=min(1,x['p_all_frames_max']*8)
  out.update(reading=tr,lines=len(rs),folios=len({r['folio'] for r in rs}));panels.append(out)
  np.savez_compressed(R/(tr+'-'+mode+'-null.npz'),scores=scores,maxima=maxima)
  print(tr,mode,out['results'],out['mobility'],flush=True)
save('RESULTS.json',dict(protocol=protocol,qualification=qualification,panels=panels,observed=observed))
save('SUMMARY.json',panels)
save('VERIFICATION.json',dict(frozen_inputs_and_methods='pass',shuffle_invariants='pass',hand_worked_frame_example='pass',semantic_inference='none',browser_visual_review='not performed'))
