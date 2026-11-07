from common import *
from alignment import evaluate,nulls
from conjugacy import run as conjugacy
from threadpoolctl import threadpool_limits
def main():
    verify();assert json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS','PHASE8 CALIBRATION GATE CLOSED'
    assert not (R/'TARGET_MANIFEST.json').exists();dump(R/'TARGET_MANIFEST.json',dict(status='FROZEN_BEFORE_TARGET_GRAPHS',qualification_sha256=sha(R/'QUALIFICATION.json'),registration_sha256=sha(R/'REGISTRATION.json'),code_sha256=sha(Path(__file__))))
    meta=json.loads((R/'LAYOUT.json').read_text());known={r['line_id'] for r in meta if r.get('currier_lang') in ['A','B']};labels=known_labels();result=[]
    with threadpool_limits(limits=1):
        for transcription,filename in [('ZL','ZL_running.csv'),('H','LSI_H_running.csv')]:
            rows=[r for r in read(LAB/'data/voynich'/filename) if r['line_id'] in known and leaf(r['folio']) in labels]
            for seed in QUAL:
                folder=R/'targets'/transcription/f's{seed}';observed=evaluate(rows,labels,seed,folder/'ALIGNMENT.json');stats=nulls(rows,labels,seed,observed,folder/'PAGE_NULLS.json');physical=conjugacy(rows,labels,seed,folder/'WITHIN_QUIRE_CONJUGACY.json');result.append(dict(transcription=transcription,seed=seed,Q=observed['Q'],D=observed['D'],Q0=observed['Q0'],null_statistics=stats,within_quire_conjugacy=physical))
    dump(R/'TARGET_RESULTS.json',result);dump(R/'RUN_STATE.json',dict(status='COMPLETE',Voynich_gate='QUALIFIED_PHASE8_COMPLETE',target_features_read=True,retired_physical_tests_called=False,translation_claims=False))
if __name__=='__main__':main()
