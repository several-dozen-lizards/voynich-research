# v7.1 attempt 2

Start with [REPORT.md](REPORT.md). The final status is NOT_QUALIFIED: clean/noisy positives and random-not-PASS calibration pass, but actual H/F dictionary traps remain PARTIAL rather than the required FAIL.

AMENDMENT-FREEZE.json, PLAN-SEAL.json and CODE-FREEZE.json precede the scored run. Original attempt1 contents are preserved; external administrative replacements and byte-identical backups are recorded in CONCURRENT-ADMINISTRATION.json.

run_attempt2.py runs stages1–4; stage5.py uses the qualified v5 entrypoint and finalizes C2 outcomes. Banks have1000 keys each and checkpoint JSONL files. Do not rerun these scripts into this directory to change methods: create a new frozen attempt. verify_attempt2.py checks preserved history, key counts, control quantiles, noise masks, exact confidence bounds, generator provenance and11 focused tests.

The diagnostics/source_control_adapter.py follow-up was authored after attempt2 and has6 separate authored tests. It is not part of the scored CODE-FREEZE and does not revise any attempt2 verdict. No vault runner is present.
