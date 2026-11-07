"""Wait for independent CPU analyses, then report/audit and stop."""
from .common import *
import time,traceback
def main():
    while True:
        try:
            complete=(EXT/'report/CLASSIFIER_STATUS.json').exists() and (EXT/'report/within_cell_probe_summary.csv').exists() and len(read(EXT/'report/mixture_summary.csv'))==372
        except (FileNotFoundError,ValueError,KeyError):complete=False
        if complete:break
        time.sleep(10)
    try:
        from .report_phase6 import build
        from .verify_phase6 import verify
        build();result=verify()
        (EXT/'STATUS.md').write_text('# Phase 6 batch\n\nStatus: COMPLETE. Requested batch finished and stopped. Phase4/5 and C16-KH v1 preserved. See report/REPORT.md and report/PHASE6_VERIFICATION.json. C14 partial qualification, original KH scorer limitations, blank human ratings and exploratory sweeps remain explicit.\n',encoding='utf-8')
        dump(EXT/'report/BATCH_STATUS.json',dict(status='COMPLETE',stop_after='Phase6 requested batch',verification=result['status']))
    except Exception as error:
        dump(EXT/'report/BATCH_STATUS.json',dict(status='FINALIZATION_FAILED',error=repr(error),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
