from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import csv,json,hashlib,sys,importlib.util,itertools,math
from datetime import datetime,timezone
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
import engine as e
from protocol import save,sha,R,P

def log(phase,**data):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**data))+'\n')

def check(name='FREEZE.json'):
    for p,h in json.loads((R/name).read_text())['hashes'].items():assert sha(p)==h,('hash changed',p)

def paths():
    sources=json.loads((R/'PROTOCOL.json').read_text())['sources']
    source=next(Path(p) for p in sources if 'text16e6' in p);meta=next(Path(p) for p in sources if 'Davis-hands' in p)
    metadata={r['Folio']:r for r in csv.DictReader(meta.open(encoding='utf-8-sig'))}
    return source,metadata

def prepare():
    check();assert not (R/'SUPPORT.json').exists()
    source,metadata=paths()
    # No startswith(qok), adjacency outcome, historical result or p-value access in this phase.
    lines=list(e.parse(source,metadata));masked,ex,_=e.extract(lines,False)
    lists={p:sorted({r['folio'] for r in lines if r['panel']==p}) for p in ['P1','P2','P0']}
    declared={p:[] for p in lists}
    for fol,m in metadata.items():
        hand,section=m['Scribe'],m['Section']
        if hand not in ('2','3'):continue
        p='P0' if (hand,section) in [('2','Balneological'),('3','Starred paragraphs')] else 'P1' if hand=='2' else 'P2'
        declared[p].append(fol)
    # Metadata-only reconstruction of earlier inclusion rules. Do not read prior results.
    old=json.loads((P/'frequency-atlas-v48/rows.json').read_text());hf=defaultdict(set)
    for r in old:
        if r[0] in ('H','F'):hf[r[6]].add(r[0])
    oldshared=[r for r in old if r[0] in ('H','F') and hf[r[6]]=={'H','F'}]
    audit=[]
    for panel in ['P1','P2']:
        for fol in sorted(declared[panel]):
            rr=[r for r in oldshared if r[1]==fol]
            v49=bool(rr)
            v75=any(r[2] in ['Balneological','Botanical','Starred paragraphs'] and r[5]=='P' for r in rr)
            records={
                'v49':dict(included=v49,scored_sh_qok=False,role='word-part section contrasts, not adjacency'),
                'v50':dict(included=v49,scored_sh_qok=False,role='expanded word-part section contrasts, not adjacency'),
                'v75':dict(included=v75,scored_sh_qok=v75,role='broad opening-pair search; sh/qok forced comparison'),
                'v77':dict(included=v75,scored_sh_qok=v75,role='recalibration of same v75 matrices'),
            }
            for run in ['v94','v98','v99','context-transfer-A','context-transfer-B','nuisance-repair']:
                records[run]=dict(included=False,scored_sh_qok=False,role='discovery-panel restriction excludes this folio; v98/v99 qualification/diagnostic only, not new manuscript inferential scoring')
            audit.append(dict(panel=panel,folio=fol,section=metadata[fol]['Section'],reading_lines={co:sum(r['reading']==co and r['folio']==fol for r in lines) for co in ['H','F']},prior_runs=records,
                freshness='PREVIOUSLY SEARCHED RETEST; earlier not-passed status supplied in original spec, not re-read' if v75 else 'NOT IN LISTED sh-qok SEARCHES by source-rule audit; no global untouched claim'))
    save('PANELS.json',dict(declared_folios={p:sorted(v) for p,v in declared.items()},P_unit_covered_folios=lists,freshness_audit=audit,
        audit_sources=['section-controls-v49/analyze.py','word-parts-v50/run.py','opening-order-audit-v75/run.py','opening-order-audit-v75/engine.py','opening-maxT-qualification-v77/rescore.py','sh-qok-ending-qualification-reed-v94/run.py','transition-maxT-qual-v98/PROTOCOL.json','transition-cost-diagnostic-v99/PROTOCOL.json','sh-qok-context-transfer-v1/run.py','sh-qok-context-transfer-v2/run.py','sh-qok-weak-score-v2/run.py'],
        limits='Membership reconstructed from source rules and metadata; prior numerical outcomes not opened. Per-folio inclusion is exposure, not an independent per-folio test. No general claim of unseen data.'))
    support={}
    for cell in e.CELLS:
        ev=[v for v in masked if v['cell']==cell]
        support[cell]=e.support(ev)|dict(exclusions=dict(ex.get(cell,{})),declared_folios=len(declared[cell[:2]]),P_unit_folios=len({r['folio'] for r in lines if r['panel']==cell[:2] and r['reading']==cell[-1]}))
    save('MASKED.json',masked);save('SUPPORT.json',support)
    save('SUPPORT-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(R/n):sha(R/n) for n in ['PANELS.json','SUPPORT.json','MASKED.json']}))
    log('support_frozen',outcomes_computed=False)
    print(json.dumps({c:{k:s[k] for k in ['eligible_origins','sh','ch','V','supported_pages','max_page_share','gate']} for c,s in support.items()},indent=2),flush=True)

def engineering():
    assert e.tokens('shedy.qokam,chedy-dar=foo!')==['shedy','qokam','chedy','dar','foo']
    assert e.tokens('sh{note}edy.qokam.%%.ch*y.?.dar')==['shedy','qokam',None,None,None,'dar']
    assert [e.family(w) for w in ['sheey','shedy','shey','shy','shol']]==['eey','edy','ey','y','other']
    fixture=[dict(panel='P1',reading='H',folio='toy',line='toy.P.1',hand='2',section='toy',tokens=['shedy','qokam',None,'chedy','dar','shol'])]
    ev,ex,ledger=e.extract(fixture,True);assert len(ev)==2 and ev[0]['position']==0 and ex['P1-H']['unknown_origin']==1 and ex['P1-H']['origin_at_end']==1
    # Exact permutation oracle on every assignment of six origins; p-values compared directly.
    checks=0
    for n,ns in [(4,2),(5,2),(6,3)]:
        xx=[int(i<ns) for i in range(n)]
        template=[dict(folio='a' if i<n//2 else 'b',family='y',x=xx[i]) for i in range(n)]
        groups=e.grouping(template)
        assignments=list(itertools.product(*[list(itertools.combinations(ix,sum(xx[i] for i in ix))) for ix in groups.values()]))
        for bits in itertools.product([0,1],repeat=n):
            y=np.array(bits);stats=[sum(y[i] for chosen in a for i in chosen) for a in assignments]
            observed=sum(x*y[i] for i,x in enumerate(xx));oracle=sum(s>=observed for s in stats)/len(stats);got=e.exact(template,y)
            if got['p'] is not None:assert abs(got['p']-oracle)<1e-12
            else:assert len(set(stats))==1
            checks+=1
    leak=ev[0];changed={**leak,'y':1-leak['y'],'follower':'qokFAKE','context':{'1':'qokFAKE','2':'FAKE'}}
    for m in ['P','J']:assert e.feature(leak,m)==e.feature(changed,m)
    save('ENGINEERING.json',dict(status='PASS',exact_oracle_cases=checks,tokenizer_comments_commas_unknowns=True,ending_order=True,first_position_line_barriers=True,H2_future_field_invariance=True))

def worker(job):
    cell,kind,scenario,trial=job
    events=[v for v in json.loads((R/'MASKED.json').read_text()) if v['cell']==cell]
    ci=e.CELLS.index(cell);si=['null_low','null_high','additive','junction_only','positive'].index(scenario)
    seed=2500000+ci*100000+si*1000+trial+(500000 if kind=='H2' else 0)
    y=e.synthetic(events,scenario,seed,kind=='H2')
    result=e.exact(events,y) if kind=='H1' else e.h2(events,y)
    flag=result['p'] is not None and result['p']<.05/4
    if kind=='H2':flag=flag and result['gain_bits']>0
    return dict(cell=cell,kind=kind,scenario=scenario,trial=trial,seed=seed,synthetic_outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest(),flag=bool(flag),result=result)

def qualify():
    check();check('SUPPORT-FREEZE.json');engineering();assert not (R/'QUALIFICATION.json').exists()
    log('qualification_start');support=json.loads((R/'SUPPORT.json').read_text());scenes=['null_low','null_high','additive','junction_only','positive']
    jobs=[(c,'H1',s,t) for c in e.CELLS for s in scenes for t in range(200)]
    jobs += [(c,'H2',s,t) for c in e.CELLS if support[c]['gate'] for s in scenes for t in range(100)]
    records=[];path=R/'SYNTHETIC-TRIALS.jsonl';assert not path.exists()
    with ProcessPoolExecutor(max_workers=4) as pool,path.open('w',encoding='utf-8') as f:
        futures=[pool.submit(worker,j) for j in jobs]
        for fut in as_completed(futures):
            rec=fut.result();records.append(rec);f.write(json.dumps(rec,allow_nan=False)+'\n');f.flush()
            if len(records)%100==0:print('Synthetic controls',len(records),'/',len(jobs),flush=True)
    summary={}
    for kind in ['H1','H2']:
        summary[kind]={}
        for cell in e.CELLS:
            cells=[]
            for scenario in scenes:
                rr=[r for r in records if (r['kind'],r['cell'],r['scenario'])==(kind,cell,scenario)]
                if not rr:continue
                n=len(rr);k=sum(r['flag'] for r in rr);bounds=e.wilson(k,n)
                role='power' if scenario=='positive' else 'recovery_diagnostic' if kind=='H2' and scenario=='junction_only' else 'null'
                gate=bounds[0]>=.8 if role=='power' else bounds[1]<=.05 if role=='null' else None
                cells.append(dict(scenario=scenario,role=role,trials=n,flags=k,wilson95=bounds,gate=gate,not_tested=sum(r['result']['p'] is None for r in rr)))
            if cells:
                valid=all(v['gate'] for v in cells if v['role']=='null');power=all(v['gate'] for v in cells if v['role']=='power')
                summary[kind][cell]=dict(status='PASS_LIMITED_SCOPE' if valid and power else 'UNDERPOWERED' if valid else 'FAIL_NULL_QUALIFICATION',null_pass=valid,power_pass=power,controls=cells)
            else:summary[kind][cell]=dict(status='NOT_RUN_SUPPORT_FAILED',null_pass=False,power_pass=False,controls=[])
    save('QUALIFICATION.json',dict(results=summary,manuscript_outcomes_used=False,limits='Actual observed origin geometry, finite authored outcome controls only. Fixed allocation confounding can invalidate exchangeability; no universal mechanism qualification. H2 power control is strong interaction, not 15-point H1.'))
    save('QUALIFICATION-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(R/n):sha(R/n) for n in ['QUALIFICATION.json','SYNTHETIC-TRIALS.jsonl','ENGINEERING.json']}))
    log('qualification_complete',trials=len(records));print(json.dumps(summary,indent=2),flush=True)

def sensitivity(events,lines,cell):
    spec=importlib.util.spec_from_file_location('transported_weak',P/'sh-qok-weak-score-v2/core.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    lookup={(r['reading'],r['line']):r for r in lines};ev=[]
    for v in events:
        line=lookup[(v['cell'][-1],v['line'])];old=m.a.event(line['tokens'],v['position'],v['folio'],v['folio'],v['line']);ev.append(old)
    result=m.score(ev)
    return dict(cell=cell,status='TRANSPORTED_EXPLORATORY_SENSITIVITY',target='sh/ch origin; NOT qok',qualified_for_new_population=False,result=result)

def manuscript():
    check();check('SUPPORT-FREEZE.json');check('QUALIFICATION-FREEZE.json');assert not (R/'PRIMARY.json').exists()
    log('first_manuscript_outcome_computation')
    source,metadata=paths();lines=list(e.parse(source,metadata));events,ex,ledger=e.extract(lines,True)
    # Independently check masked extraction identical before using any inference.
    masked,_,_=e.extract(lines,False);assert masked==json.loads((R/'MASKED.json').read_text())
    with (R/'EVENTS.csv').open('w',encoding='utf-8',newline='') as f:
        names=list(ledger[0]);writer=csv.DictWriter(f,fieldnames=names);writer.writeheader();writer.writerows(ledger)
    support=json.loads((R/'SUPPORT.json').read_text());q=json.loads((R/'QUALIFICATION.json').read_text())['results'];primary=[];secondary=[];sens=[]
    for ci,cell in enumerate(e.CELLS):
        ev=[v for v in events if v['cell']==cell];common=dict(cell=cell,events=len(ev),support_gate=support[cell]['gate'],**e.effect(ev,240100+ci))
        q1=q['H1'][cell]
        if not support[cell]['gate']:h1=dict(status='NOT ESTIMABLE',p=None,reason='outcome-blind support gate failed')
        elif not q1['null_pass']:h1=dict(status='QUALIFICATION FAILED',p=None,reason='required synthetic null gate failed; manuscript inference blocked')
        else:
            h1=e.exact(ev);h1['status']='NOT ESTIMABLE' if h1['degenerate'] else 'UNDERPOWERED' if not q1['power_pass'] else 'SCORED'
        primary.append({**common,**h1,'qualification':q1['status']})
        q2=q['H2'][cell]
        if not support[cell]['gate']:h2=dict(status='NOT ESTIMABLE',p=None)
        elif not q2['null_pass']:h2=dict(status='QUALIFICATION FAILED',p=None)
        else:
            h2=e.h2(ev,receipts=True)
            if h2['status']=='SCORED' and not q2['power_pass']:h2['status']='UNDERPOWERED'
        secondary.append(dict(cell=cell,qualification=q2['status'],**h2))
        if support[cell]['gate']:sens.append(sensitivity(ev,lines,cell))
        else:sens.append(dict(cell=cell,status='NOT ESTIMABLE',reason='shared support gate failed'))
        print('Scored',cell,h1['status'],h2['status'],flush=True)
    for collection in [primary,secondary]:
        adjusted=e.holm([r['p'] for r in collection])
        for r,p in zip(collection,adjusted):
            r['holm_p']=p
            if r['status']=='SCORED':r['status']='PASS' if p is not None and p<.05 and r.get('effect_points',r.get('gain_bits',0))>0 else 'NO PASS'
    p0=[]
    for ci,(hand,sec) in enumerate([('2','Balneological'),('3','Starred paragraphs')]):
        for ri,reading in enumerate(['H','F']):
            ev=[v for v in events if v['cell']=='P0-'+reading and v['hand']==hand]
            p0.append(dict(cell='P0-'+hand+'-'+reading,section=sec,events=len(ev),descriptive_only=True,**e.effect(ev,240200+ci*2+ri)))
    save('PRIMARY.json',primary);save('SECONDARY.json',secondary);save('DESCRIPTIVE-P0.json',p0);save('SENSITIVITY.json',sens)
    log('manuscript_complete')

def report():
    primary=json.loads((R/'PRIMARY.json').read_text());secondary=json.loads((R/'SECONDARY.json').read_text());support=json.loads((R/'SUPPORT.json').read_text());panels=json.loads((R/'PANELS.json').read_text());qual=json.loads((R/'QUALIFICATION.json').read_text())['results'];p0=json.loads((R/'DESCRIPTIVE-P0.json').read_text())
    lines=[]
    for r in primary:
        val='unavailable' if r['effect_points'] is None else f"{r['effect_points']:+.3f} pts [{r['CI95_points'][0]:+.3f}, {r['CI95_points'][1]:+.3f}]"
        lines.append(f"{r['cell']}: {r['status']} — {val}; Holm p {r['holm_p'] if r['holm_p'] is not None else 'not computed'}")
    lines+=['','Attempt C was frozen before support and all outcome computations. H/F remain separate alternate readings, not independent samples. This is a single-target RETEST on previously searched botanical material, not untouched confirmation. Effects and folio-bootstrap intervals are descriptive when support or qualification fails.','', '## Primary support and qualification','', '| Cell | sh / ch | V | Supported pages | Largest page share | H1 null gate | +15 pt power gate |','|---|---:|---:|---:|---:|---|---|']
    for cell in e.CELLS:
        s=support[cell];q=qual['H1'][cell];lines.append(f"| {cell} | {s['sh']} / {s['ch']} | {s['V']:.3f} | {s['supported_pages']} | {(s['max_page_share'] or 0)*100:.2f}% | {q['null_pass']} | {q['power_pass']} |")
    both=all(r['status']=='PASS' for r in primary[:2]);lines+=['',f"Primary two-reading confirmation: {'PASS' if both else 'NOT CONFIRMED'}. A support failure is not evidence against the dependency; failed null qualification blocks inference. Underpowered cells cannot exclude smaller effects.",'','## Leakage-free H2','', 'The target is next-qok. P includes prefix main effects; J adds only origin-end/previous-end features and their prefix interactions. No follower or future token appears in either feature map. This is a newly defined prediction question, not unchanged replication of attempt B’s prefix-prediction gain.','']
    for r in secondary:lines.append(f"- {r['cell']}: {r['status']}; gain {r.get('gain_bits','unavailable')} bits; Holm p {r['holm_p']}; qualification {r['qualification']}.")
    lines+=['','## Descriptive discovery panels','', 'No P0 hypothesis test or p-value was computed. Bath hand2 and starred hand3 are kept separate.','']
    for r in p0:lines.append(f"- {r['cell']} ({r['section']}): {r['effect_points']:+.3f} points; 95% folio-bootstrap CI {r['CI95_points']}; n={r['events']}.")
    lines+=['','## Full freshness audit','', 'Membership comes from historical source rules and metadata. Prior numerical outcome tables were not opened. “Previously not passed” is inherited from the supplied spec, not newly verified. v49/v50 tested word-part section contrasts, not sh→qok adjacency. v75/v77 used the forced sh/qok comparison in their search. v94/context-transfer/nuisance were discovery-only; v98/v99 used discovery layouts for qualification/diagnostics without new original-arrangement inferential scoring. Preflight incidental historical-index exposure is recorded in PROTOCOL.json.','', '| Panel | Folio | Section | v49/v50 included | v75/v77 sh→qok searched | v94/v98/v99/A/B/repair included |','|---|---|---|---|---|---|']
    for a in panels['freshness_audit']:
        runs=a['prior_runs'];lines.append(f"| {a['panel']} | {a['folio']} | {a['section']} | {runs['v49']['included']} | {runs['v75']['scored_sh_qok']} | False |")
    lines+=['','PANELS.json retains every declared folio, coverage, per-reading line counts, per-run membership and freshness label. Missing P-unit folios are preserved, not replaced.','', '## Controls, sensitivity and limits','', 'QUALIFICATION.json gives every cell/scenario Wilson interval; SYNTHETIC-TRIALS.jsonl retains every trial with replay seed and outcome hash. H1 null rejection can reflect position/line or spelling confounding under the proposed exchangeability assumption. Such failures are preserved; no design was tuned to the results. H2 junction-only is a recovery diagnostic, not a null. H2 power uses a strong interaction and does not certify detection of a 15-point H1 effect.','', 'SENSITIVITY.json applies the unchanged repaired predictor to its original sh/ch target, with its original support and adequacy gates. Transport to the new event population is explicitly exploratory and cannot rescue primary inference.','', 'The new tokenizer follows literal comma-separator/comment-drop rules, with engineering fixtures; it intentionally differs from the older comma-masking atlas. All known paragraph loci in each reading are used, without forced shared-locus or Currier-B restriction. No signs were reserved/opened for zodiac scoring, no meanings were assigned, and no discovery-panel inferential test was run. Bootstrap CIs are descriptive and do not repair confounding or historical selection.','', 'VERIFICATION.json independently reparses raw EVT, checks every event/exclusion/count/effect and frozen hashes; engineering oracles verify the exact test on enumerated assignments.']
    (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='qualify':qualify()
    elif mode=='manuscript':manuscript()
    elif mode=='report':report()
    else:raise ValueError(mode)
