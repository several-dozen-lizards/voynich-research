"""Operational restart only: retain completed seed records; unchanged frozen worker/gates."""
import run as r
from concurrent.futures import ProcessPoolExecutor,as_completed
import json

def main():
    r.verify();r.log('qualification_resume',reason='execution session ended; completed records retained')
    summary=[]
    for di in range(5):
        for regime in r.REGIMES:
            rows=[];missing=[]
            for trial in range(100):
                p=r.R/f'trials/d{di}-{regime}-{trial:03d}.json'
                if p.exists():
                    rec=json.loads(p.read_text());assert rec['seed']==2110000+di*100000+r.REGIMES.index(regime)*1000+trial
                    rows.append(rec)
                else:missing.append(trial)
            with ProcessPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(r.worker,di,regime,t) for t in missing]
                for future in as_completed(futures):
                    row=future.result();r.save(f'trials/d{di}-{regime}-{row["trial"]:03d}.json',row);rows.append(row)
                    if len(rows)%25==0:print(r.DESIGNS[di],regime,len(rows),'/100',flush=True)
            k=sum(x['result'].get('flag4',False) for x in rows);k24=sum(x['result'].get('flag24',False) for x in rows);bounds=r.core.a.ci(k,100)
            gate=bounds[1]<=.10 if regime in r.REGIMES[:6] else bounds[0]>=.80 if regime in ('weak','strong') else None
            s=dict(design=r.DESIGNS[di],design_index=di,regime=regime,n=100,flags4=k,flags24=k24,wilson95=bounds,required_gate=gate,adequate=sum(x['result'].get('adequate',False) for x in rows),supported=sum(x['result']['status']=='SCORED' for x in rows),zero_directions=sum(x['result'].get('status')=='SCORED' and all(v['direction']==0 for v in x['result']['heldout']) for x in rows))
            if di==0 and regime=='weak':
                win=sum(x['result'].get('flag24',False) and not x['old_v2']['flag'] for x in rows);lose=sum(x['old_v2']['flag'] and not x['result'].get('flag24',False) for x in rows);pv=float(r.stats.binomtest(win,win+lose,.5,alternative='greater').pvalue) if win+lose else 1.
                s['paired_factor24']=dict(new_only=win,old_only=lose,p=pv,old_detections=sum(x['old_v2']['flag'] for x in rows),required_gate=pv<=.01)
            summary.append(s);r.save('QUALIFICATION-PROGRESS.json',summary)
    passed=all(s['required_gate'] is not False and s.get('paired_factor24',{}).get('required_gate',True) for s in summary)
    r.save('QUALIFICATION.json',dict(status='PASS_LIMITED' if passed else 'FAIL',cells=summary,manuscript_allowed=passed));r.verify();r.log('qualification_complete',status='PASS_LIMITED' if passed else 'FAIL')
    print('QUALIFICATION','PASS_LIMITED' if passed else 'FAIL',flush=True)

if __name__=='__main__':main()
