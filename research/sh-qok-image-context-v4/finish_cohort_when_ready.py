"""Finite completion helper for the exact already-authorized cohort process."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,json,subprocess,sys,os
from ctypes import wintypes
import continue_blind_cohort as runner
import prepare as core
from setup_packets import replace_json

def main():
    pid=int(sys.argv[1])
    library=ctypes.WinDLL('kernel32',use_last_error=True)
    library.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    library.OpenProcess.restype=wintypes.HANDLE
    library.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    library.WaitForSingleObject.restype=wintypes.DWORD
    library.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=library.OpenProcess(0x00100000,False,pid)  # SYNCHRONIZE only; no memory/process modification.
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    collector=core.R/'collect_blind_cohort.py'
    expected=core.sha(collector)
    core.save('COHORT-COMPLETION-HELPER.json',dict(status='WAITING_FOR_EXACT_RUNNER_PROCESS',
        runner_pid=pid,helper_pid=os.getpid(),utc_started=datetime.now(timezone.utc).isoformat(),
        collector_sha256=expected,helper_sha256=core.sha(Path(__file__)),
        behavior='Wait on this process handle. After exit, collect only if RUN-STATE is COMPLETE; otherwise preserve stop details. No model calls, retries, outcome joins, scoring or recurring automation.'))
    print(json.dumps(dict(status='WAITING_FOR_EXACT_RUNNER_PROCESS',runner_pid=pid)),flush=True)
    try:
        while True:
            result=library.WaitForSingleObject(handle,60000)
            if result==0:break
            if result!=258:raise ctypes.WinError(ctypes.get_last_error())
    finally:library.CloseHandle(handle)
    state=json.loads((runner.RUNS/'RUN-STATE.json').read_text(encoding='utf-8'))
    if state['status']=='COMPLETE':
        assert core.sha(collector)==expected,'Collector changed after helper registration.'
        with (runner.RUNS/'COLLECTION.log').open('wb') as log:
            result=subprocess.run([sys.executable,str(collector)],cwd=core.R.parent,stdout=log,stderr=subprocess.STDOUT)
        core.save('COHORT-COMPLETION-RESULT.json',dict(status='COLLECTED' if result.returncode==0 else 'COLLECTION_FAILED_RETAINED',
            returncode=result.returncode,utc=datetime.now(timezone.utc).isoformat(),log=str(runner.RUNS/'COLLECTION.log')))
    else:
        stop=runner.RUNS/'INFRASTRUCTURE-STOP.json'
        details=json.loads(stop.read_text(encoding='utf-8')) if stop.exists() else None
        core.save('COHORT-COMPLETION-RESULT.json',dict(status='RUNNER_EXITED_BEFORE_COHORT_COMPLETE',
            utc=datetime.now(timezone.utc).isoformat(),last_state=state,infrastructure_stop=details,
            behavior='No automatic retry or scientific scoring. Existing receipts preserved.'))
        delivery=json.loads((core.R/'DELIVERY.json').read_text(encoding='utf-8'))
        delivery.update(status='COHORT STOPPED BEFORE COMPLETION; RECEIPTS PRESERVED',completion_receipt='COHORT-COMPLETION-RESULT.json')
        replace_json('DELIVERY.json',delivery)
    print((core.R/'COHORT-COMPLETION-RESULT.json').read_text(encoding='utf-8'),flush=True)

if __name__=='__main__':main()
