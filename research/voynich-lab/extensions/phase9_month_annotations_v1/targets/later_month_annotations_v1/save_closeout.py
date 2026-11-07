"""Save the approved closeout and verify preservation; no research execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

T = Path(__file__).resolve().parent
R = T.parents[1]
P8 = R.parent/'phase8_alignment_v1'
def load(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (T/'CLOSEOUT.md').exists()
assert not (T/'CLOSEOUT_PRESERVATION_RECEIPT.json').exists()
before = {str(p.resolve()):sha(p) for root in [R,P8] for p in root.rglob('*') if p.is_file()}
earlier = load(R/'PRESERVATION_BEFORE.json')
assert all(sha(Path(p))==h for p,h in earlier.items())
assert all(sha(R/p)==h for p,h in load(T/'PREEXISTING_FILES.json').items())
assert all(sha(R/p)==h for p,h in load(R/'TARGET_MANIFEST.json')['files'].items())
assert all(sha(T/p)==h for p,h in load(T/'OUTPUT_HASHES.json').items())
addendum = load(T/'AUDIT_ADDENDUM_RECEIPT.json')
assert all(sha(R/p)==h for p,h in addendum['prior_file_hashes'].items())
assert all(sha(T/p)==h for p,h in addendum['addendum_files'].items())
reg = load(R/'REGISTRATION.json')
drift = [p for p,h in reg['files'].items() if sha(R/p)!=h]
assert drift==['RUN_STATE.json']
assert sha(R/'RUN_STATE.registered_snapshot.json')==reg['files']['RUN_STATE.json']
assert load(R/'RUN_STATE.json')['native_gate']=='CLOSED'
assert load(T/'TARGET_RUN_STATE.json')['native_tracks']=='CLOSED'
assert load(P8/'QUALIFICATION.json')['status']=='FAIL'

closeout = '''Phase 9 found **an association between the later Latin-script month annotations and their assigned month candidates under the frozen matching procedure**.

The observed maximum was **5/12 exact panel matches**, using the Occitan candidate list with positional substitution. No shuffled assignment reached five in any frozen bank: **p=.01 separately in each of five 99-shuffle banks**, after the same maximization over languages, families, and tables. These banks are Monte Carlo repeats on one target, not independent replications.

That result has clear limits:

- **Mapping generalization remains untested.** No held-out-month prediction or leave-one-month-out refitting was performed. In every saved observed and top-null witness, each matched month needs at least one assignment unsupported by other distinct months.
- **Duplicate May contributes an extra point without another mapping constraint.** The observed five matches span four distinct months. The null preserves the duplicates, but the registered statistic still weights both panels.
- **Language identity and historical encoding remain unresolved.** The winning candidate list does not establish the annotator’s language, a unique mapping, or an actual cipher. Conclusions remain conditional on the frozen spellings, normalization, alternatives, and tested families.

**This provides no support for native-script interpretation.** The target consists of later Latin-script annotations. No native token was established as a month-name locus, and no native-script mapping, prediction, or translation was tested. Synthetic calibration qualified the matching procedure; it did not establish transfer to native writing.

[The closeout evidence and audit addendum](C:/Users/lewis/OneDrive/Documents/ChatGPT/Voynich/voynich-lab/extensions/phase9_month_annotations_v1/targets/later_month_annotations_v1/AUDIT_ADDENDUM.md) remain preserved. The original strict calibration receipt still fails solely at its documented mutable `RUN_STATE.json` entry; that defect has not been repaired or relabeled PASS.

**Native tracks remain CLOSED. Phase 8 remains FAIL. No new fits, scoring, or registration were performed for this closeout.**
'''
(T/'CLOSEOUT.md').write_text(closeout,encoding='utf8')
assert all(sha(Path(p))==h for p,h in before.items())
assert all(sha(Path(p))==h for p,h in earlier.items())
receipt = dict(status='SAVED_CLOSEOUT_PRESERVATION_VERIFIED',created_at_utc=datetime.now(timezone.utc).isoformat(),
    scope='Save the preceding Phase 9 closeout; preservation and documentation only; stop',
    closeout_sha256=sha(T/'CLOSEOUT.md'),save_script_sha256=sha(Path(__file__)),
    new_fits=0,new_scoring=0,new_null_draws=0,new_registration=False,
    native_tracks='CLOSED',native_tracks_scored=False,Phase8_status='FAIL_PRESERVED',
    original_calibration_strict_manifest='FAIL_MUTABLE_RUN_STATE_ONLY_PRESERVED',
    original_calibration_drift=drift,target_manifest_sha256=sha(R/'TARGET_MANIFEST.json'),
    original_target_output_manifest_sha256=sha(T/'OUTPUT_HASHES.json'),
    original_target_completion_receipt_sha256=sha(T/'COMPLETION_RECEIPT.json'),
    addendum_receipt_sha256=sha(T/'AUDIT_ADDENDUM_RECEIPT.json'),
    existing_artifacts_changed=0,preexisting_phase9_and_phase8_files=len(before),
    earlier_preservation_entries_verified=len(earlier),preexisting_file_sha256=before,stop=True)
path = T/'CLOSEOUT_PRESERVATION_RECEIPT.json'
path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
saved = load(path)
assert sha(T/'CLOSEOUT.md')==saved['closeout_sha256']
assert all(sha(Path(p))==h for p,h in saved['preexisting_file_sha256'].items())
print(json.dumps({k:v for k,v in saved.items() if k!='preexisting_file_sha256'},indent=2))
