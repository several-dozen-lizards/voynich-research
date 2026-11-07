from pathlib import Path
import collections,hashlib,json,re
import numpy as np
from engine import belongs,prepare,count,run,QUESTIONS
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
paths=[P/'frequency-atlas-v48/rows.json',P/'frequency-atlas-v48/source-manifest.json']
protocol={'request':'Audit supplied opening-order claims, especially sh- -> qok-, H/F separate and within each known/ambiguous hand, Currier variety, section and raw format.',
 'scope':'Balneological, Botanical and Starred paragraphs, raw P only for inference, including f75 (generalization claim no longer excludes discovery folio). Shared H/F source loci within each exact stratum; no hand/variety pooling. Ambiguous hand2,3 remains a distinct panel and cannot establish another scribe. RawQ starred inventory reported descriptively only.',
 'classes':'Literal EVA startswith sh,qok,d,a; union:l/s means startswith l OR s (therefore includes sh); exact:ol/or is the exact whole-word set ol,or. These classes can overlap. No invented token merging or affix interpretation. Unknown slots are barriers, not words.',
 'search_family':'Every observed prefix of lengths1..3 with >=20 readable tokens and>=2numberedfolios in its fixed stratum, plus all classes needed for the four supplied comparisons regardless of support. Enumerate every unordered class pair, both directions. Support depends only on within-line-shuffle-invariant word/folio frequencies, not observed adjacency. This reconstructs a declared broad family; it does not reproduce the unavailable Claude ~60-pair definitions or all prior analytic choices.',
 'statistic':'Immediate readable source-word adjacency only; for each A/B class pair D=#A->B minus #B->A. If classes overlap, a word-pair can contribute both ways and cancels in D; do not enforce arbitrary exclusive classification. No crossing line or unknown boundaries.',
 'null':'4999 shuffles of every readable contiguous interior span per line; first/last tokens and unknown slots fixed. Each line retains its words, each stratum fixed. Exact interior ordinals not controlled. Seeds7500+fixed sorted panel index. No exact-slot test or reuse of failed v73 qualification claimed.',
 'calibration':'Observed plus4999null rows, single-step minP using symmetric pooled upper/lower ranks with ties. Family includes both directions of all eligible class pairs. Bonferroni across the fixed complete reading/stratum panel count, including zero/sparse target strata. H/F agreement is descriptive correspondence, not independent replication. Point p-values near thresholds not stable without precision assessment.',
 'audit':'Unavailable /tmp/claude-0/s/order.py not executed. Separately tabulate full-H per-section rawP counts to compare supplied pooled numbers; these pooled counts are reproduction diagnostics, never evidence across hands. Supply per-folio counts/reverse examples and target source lines.',
 'verification':'Hand-worked overlapping-class and unknown/line-barrier counts; exact word multiset/endpoints/unknown invariants; saved score matrices and direct independent reported-rule counts. No power/semantic qualification claim.',
 'interpretation':'Retrospective conditional opening-order test. Ordering preference is not an exception-free rule, verified grammar, semantic role or exclusion of all junction/spelling mechanisms. Matching common last character y does not establish identical full boundary conditions.'}
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
toy=[dict(page='toy',folio='f1',locator='toy1',tokens=['shedy','qokedy',None,'shedy']),dict(page='toy',folio='f2',locator='toy2',tokens=['qokedy','shedy','ol'])]
p=prepare(toy);c,_=count(p['original'],p);i=p['labels'].index('prefix:sh');j=p['labels'].index('prefix:qok');assert c[i,j]==c[j,i]==1
raw=load(paths[0]);sections=['Balneological','Botanical','Starred paragraphs'];strata=collections.defaultdict(list)
for r in raw:
 if r[2] in sections and r[5]=='P':strata[tuple(r[2:6])].append(r)
panelspec=[];support=[]
for key,rs in sorted(strata.items()):
 locs={t:{r[6] for r in rs if r[0]==t} for t in ['H','F']};common=locs['H']&locs['F']
 for tr in ['H','F']:
  selected=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in rs if r[0]==tr and r[6] in common]
  if selected:panelspec.append((key,tr,selected));support.append(dict(stratum=key,reading=tr,shared_lines=len(selected),excluded_single_reading_lines=len(locs[tr]-common)))
M=len(panelspec);save('PANEL-LEDGER.json',dict(fixed_panel_count=M,panels=support));results=[];source_events=[]
for pi,(key,tr,rows) in enumerate(panelspec):
 print('START',pi+1,M,key,tr,'classes',len(prepare(rows)['labels']),flush=True)
 out,scores=run(rows,4999,7500+pi,lambda b:print('progress',pi+1,b,flush=True))
 for x in out['reported_rules']:x['p_all_panels']=min(1,x['p_search_family']*M)
 out.update(panel_index=pi,reading=tr,section=key[0],hand=key[1],variety=key[2],format=key[3],lines=len(rows),folios=len({r['folio'] for r in rows}),hand_ambiguous=',' in key[1]);results.append(out);np.savez_compressed(R/(f'panel-{pi:02d}-null.npz'),scores=scores)
 # Preserve both orientations of the principal rule, and zero/negative folios.
 folios={f:dict(forward=0,reverse=0) for f in sorted({r['folio'] for r in rows})};ev=[]
 for r in rows:
  for i in range(len(r['tokens'])-1):
   a,b=r['tokens'][i:i+2]
   if a is None or b is None:continue
   forward=belongs(a,'prefix:sh') and belongs(b,'prefix:qok');reverse=belongs(a,'prefix:qok') and belongs(b,'prefix:sh')
   if forward or reverse:
    orientation='forward' if forward else 'reverse';folios[r['folio']][orientation]+=1;ev.append(dict(r,ordinal=i+1,first=a,second=b,orientation=orientation))
 source_events.append(dict(panel_index=pi,folios=folios,events=ev));save('PROGRESS.json',dict(completed=pi+1,total=M,latest=out['reported_rules'][0]))
 print('DONE',pi+1,out['reported_rules'][0],flush=True)
audit=[]
for section in sections:
 for tr in ['H','F']:
  rr=[r for r in raw if r[0]==tr and r[2]==section and r[5]=='P'];counts=[]
  for A,B in QUESTIONS:
   f=b=0
   for r in rr:
    for a,z in zip(r[7],r[7][1:]):
     if a is None or z is None:continue
     f+=belongs(a,A) and belongs(z,B);b+=belongs(a,B) and belongs(z,A)
   counts.append(dict(A=A,B=B,forward=f,reverse=b))
  audit.append(dict(section=section,reading=tr,scope='All source rawP lines pooled over hands/varieties for reproduction audit ONLY',rules=counts))
save('RESULTS.json',dict(protocol=protocol,panel_count=M,panels=results,source_events=source_events,pooled_reproduction_audit=audit))
save('SUMMARY.json',[dict(section=p['section'],hand=p['hand'],variety=p['variety'],format=p['format'],reading=p['reading'],class_pairs=p['class_pairs'],principal=p['reported_rules'][0]) for p in results]);save('VERIFICATION.json',dict(freeze_integrity='pass',hand_worked_barrier_and_class_overlap_check='pass',historical_and_semantic_qualification='none',browser_visual_review='not performed'))
