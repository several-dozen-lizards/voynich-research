"""Resume only missing frozen jobs after the first worker process disappeared.

No change to protocol, seeds, generators, trial quotas, models or gates.
Every completed trial is retained. Original frozen run.py remains unchanged.
"""
import json
from concurrent.futures import ProcessPoolExecutor,as_completed
import run
import engine as e
from protocol import R,save,sha

def main():
    run.check();run.check('SUPPORT-FREEZE.json')
    assert not (R/'QUALIFICATION.json').exists()
    path=R/'SYNTHETIC-TRIALS.jsonl';before=sha(path)
    records=[json.loads(s) for s in path.read_text().splitlines()]
    keys={(r['cell'],r['kind'],r['scenario'],r['trial']) for r in records}
    assert len(keys)==len(records)
    support=json.loads((R/'SUPPORT.json').read_text());scenes=['null_low','null_high','additive','junction_only','positive']
    jobs=[(c,'H1',s,t) for c in e.CELLS for s in scenes for t in range(200)]
    jobs += [(c,'H2',s,t) for c in e.CELLS if support[c]['gate'] for s in scenes for t in range(100)]
    pending=[j for j in jobs if j not in keys]
    save('RESUME.json',dict(reason='Original exec session ceased to exist; no python processes remained; cause unverified.',retained_trials=len(records),retained_file_sha256=before,missing_trials=len(pending),design_changed=False,resume_script_sha256=sha(__file__)))
    run.log('qualification_resumed',retained=len(records),pending=len(pending))
    with ProcessPoolExecutor(max_workers=4) as pool,path.open('a',encoding='utf-8') as f:
        futures=[pool.submit(run.worker,j) for j in pending]
        for fut in as_completed(futures):
            r=fut.result();records.append(r);f.write(json.dumps(r,allow_nan=False)+'\n');f.flush()
            if len(records)%50==0:print('Retained+resumed',len(records),'/',len(jobs),flush=True)
    assert len(records)==len(jobs)
    assert len({(r['cell'],r['kind'],r['scenario'],r['trial']) for r in records})==len(jobs)
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
    from datetime import datetime,timezone
    save('QUALIFICATION-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(R/n):sha(R/n) for n in ['QUALIFICATION.json','SYNTHETIC-TRIALS.jsonl','ENGINEERING.json','RESUME.json','resume_qualification.py']}))
    run.log('qualification_complete',trials=len(records));print(json.dumps({kind:{cell:v['status'] for cell,v in cells.items()} for kind,cells in summary.items()},indent=2),flush=True)

if __name__=='__main__':main()
