"""Record user interpretation without changing sealed ratings, coefficients or prior rules."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import json,hashlib
R=Path(__file__).resolve().parent;V=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=json.loads((R/'AGREEMENT.json').read_text());seal=json.loads((R/'AGREEMENT-FINAL-SEAL.json').read_text())
 assert all(sha(R/n)==h for n,h in seal['files'].items()) and all(sha(R/n)==h for n,h in seal['data'].items())
 checks={}
 for name in ['G6','G2']:
  g=a[name];checks[name]=dict(kappa=g['kappa'],exact_kappa=g['exact_kappa'],paired_lines=g['n'],observed_pair_agreement_check='MEETS_0.60' if Fraction(g['exact_kappa'])>=Fraction(3,5) else 'BELOW_0.60',interpretation='Agreement check on valid paired lines only.',historical_full_population_gate_status=g['gate_status'])
 d=dict(status='PRE_ADJUDICATION AGREEMENT CHECKS ONLY',utc=datetime.now(timezone.utc).isoformat(),authority='User: proceed with the two blind model-rating sets, preserve coordinate-control failures; treat G6/G2 as agreement checks only, before adjudication; timing exception explicit; v103 parked.',existing_rating_sets_retained=True,new_model_calls=0,ratings_or_geometry_changed=False,checks=checks,coverage=dict(paired_lines=912,frozen_lines=1145,missing_pairs=233,valid_pages=a['valid_page_responses']),coverage_interpretation='Both observed-pair numerical comparisons meet0.60. They do not establish agreement over the233 unpaired lines. The earlier full-coverage admission condition and its incomplete status remain preserved as historical frozen records, not confused with the defined subset kappas.',coordinate_control_failures='Retained. Agreement is not evidence of coordinate accuracy, correct image context, semantic validity or an H-IMG/H-PLANT effect.',timing_exception=a['timing_exception'],adjudication='NOT RUN',OT_merge='NOT RUN',support_controls_outcome_joins_tests='NOT RUN',v103='PARKED',original_agreement_sha256=sha(R/'AGREEMENT.json'),original_final_seal_sha256=sha(R/'AGREEMENT-FINAL-SEAL.json'))
 (R/'AGREEMENT-CLARIFICATION.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
 text='PROSPECTIVE IN IMAGE VARIABLE ONLY — text events exposed (v100/v102).\n\nCurrent interpretation: G6/G2 are pre-adjudication agreement checks only. Existing two model-rating sets retained; no new calls, rating edits, geometry changes or adjudication.\n\n912/1145 frozen physical lines have valid pairs.\nG6 six-way kappa:0.7005823 — observed-pair comparison meets0.60.\nG2 PL/not-PL kappa:0.7358105 — observed-pair comparison meets0.60.\n\n233 missing pairs leave full-population agreement unestablished. The prior full-coverage admission status remains in the original sealed records; it does not mean the paired-subset coefficients are undefined or numerically below threshold.\n\nCoordinate-control failures remain explicit: these are agreement measurements, not coordinate-accuracy qualification, external image-context truth, semantic evidence or test results.\n\nTiming exception: v4.2 was NOT frozen before initial registration. The existing blind geometry was retained under the documented exception. No backdating or clean pre-registration claim.\n\nNo adjudication, OT merge, support, scientific controls, outcome join or H-IMG/H-PLANT tests ran. v103 remains parked; no Rosettes leave-out grids. Original REPORT.txt, AGREEMENT.json, data and seal remain unchanged.\n'
 (R/'CURRENT-AGREEMENT-READOUT.txt').write_text(text,encoding='utf-8')
 names=['record_agreement_clarification.py','AGREEMENT-CLARIFICATION.json','CURRENT-AGREEMENT-READOUT.txt']
 (R/'AGREEMENT-CLARIFICATION-SEAL.json').write_text(json.dumps({n:sha(R/n) for n in names},indent=2)+'\n',encoding='utf-8')
 status=json.loads((V/'STATUS.json').read_text());status['agreement_interpretation']='Agreement checks only; numeric threshold met on912 paired lines, full-population coverage incomplete; no accuracy or semantic validation.';status['current_agreement_readout']='ratings/CURRENT-AGREEMENT-READOUT.txt';(V/'STATUS.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(new_calls=0,original_seal_unchanged=True,checks=checks),indent=2))
if __name__=='__main__':main()
