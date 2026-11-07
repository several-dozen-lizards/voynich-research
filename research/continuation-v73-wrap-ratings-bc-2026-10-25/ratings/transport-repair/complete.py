"""Human-authorized missing-role completion; original evidence and gates are read-only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,importlib.util,shutil,concurrent.futures
P=Path(__file__).parent;ROOT=P.parents[2];OLD=ROOT/'image-context-v4/ratings'
sys.path.insert(0,str(OLD))
import collect

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rule=json.loads((P/'COMPLETION-FREEZE.json').read_text());queue=json.loads((P/'QUEUE.json').read_text());assert sha(P/'QUEUE.json')==rule['queue_sha256']
    base=json.loads((OLD/'RATING-FREEZE.json').read_text());assert sha(OLD/'collect.py')==base['code_sha256']['collect.py'];assert sha(OLD/'agreement.py')==base['code_sha256']['agreement.py'];assert sha(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')==rule['geometry_sha256']
    base['manual_sha256']=rule['manual_sha256'];pending=queue['jobs'];receipt=[]
    for wave in range(1,4):
        if not pending:break
        dest=P/f'wave-{wave}';dest.mkdir(exist_ok=True)
        for name in ['MANUAL-RATER.md','RESPONSE-SCHEMA.json']:shutil.copy2(P/name,dest/name)
        collect.R=dest;collect.V=ROOT/'image-context-v4';collect.WORK=P/'isolated'
        next_pending=[]
        def call(job):
            assert not (OLD/'responses'/job['role']/(job['task_id']+'.json')).exists(),'Accepted original must not be rerated'
            return collect.call_one((job['role'],job['task']),base)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(call,job):job for job in pending}
            for future in concurrent.futures.as_completed(futures):
                job=futures[future]
                try:result=future.result()
                except Exception as exc:result=dict(role=job['role'],task_id=job['task_id'],status='RUNNER_ERROR',failure=repr(exc))
                response=dest/'responses'/job['role']/(job['task_id']+'.json');accepted=response.exists()
                record=dict(wave=wave,role=job['role'],task_id=job['task_id'],registered_lines=job['lines'],result=result,accepted=accepted,response_path=str(response.relative_to(ROOT)) if accepted else None,original_attempt_sha256=job['original_attempt_sha256'])
                receipt.append(record)
                if not accepted:next_pending.append(job)
                (P/'CALLS.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(record),flush=True)
        pending=next_pending
    result=dict(status='ALL_MISSING_ROLES_COMPLETED' if not pending else 'STILL_MISSING_AFTER_FROZEN_ATTEMPTS',calls=len(receipt),completed_jobs=len(queue['jobs'])-len(pending),remaining_jobs=[dict(role=j['role'],task_id=j['task_id'],lines=j['lines']) for j in pending],remaining_line_pairs=sum(j['lines'] for j in pending),original_evidence_unchanged=True,adjudication='NOT RUN',outcome_join='NOT RUN')
    (P/'COMPLETION-RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
