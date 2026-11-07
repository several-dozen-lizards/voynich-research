"""Single-GPU continuation, after headline convergence finishes."""
from .common import *
import time
def main():
    while not (EXT/'report/CONVERGENCE_STATUS.json').exists():time.sleep(10)
    from .additions import partial_sweep
    partial_sweep()
    dump(EXT/'report/PARTIAL_STATUS.json',dict(status='COMPLETE',new_fits=240))
    from .classifier_extension import run
    run()
if __name__=='__main__':main()
