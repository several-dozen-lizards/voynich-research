# Voynich pattern-model lab

The accepted Phases 0–3 are preserved. C12/C13 and Phases 4–5 are complete. Final verification passes: 2,605 local neural fits, complete nonempty ZL coverage, and 25 passing unit/counterfactual tests. These are fixed 96-step instruments, not convergence-qualified models. Read [the final verification](report/PHASE5_VERIFICATION.json) and report/phase5_progress.json for receipts. **Stopped after Phase 5.**

Read [report/REPORT.md](report/REPORT.md), [DECISIONS.md](DECISIONS.md), and [SOURCES.md](SOURCES.md).

Python 3.11+; standard library for measurements, matplotlib for figures. From this directory:

Plotting dependencies are installed locally in .runtime on this machine. For a fresh environment: `python -m pip install -r requirements-phase3.txt` (normal dependency resolution also supplies numpy, Pillow, packaging and python-dateutil).

```powershell
python -m unittest discover -s tests -v
python -m src.phase3
python -m src.verify_phase3
```

On this machine the shell's default Python is too old. Use:

```powershell
& 'C:\Users\lewis\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.phase3
```

Rebuilding is offline and source-hash checked. Each run creates a unique folder with config/seed, environment, pre-metric input freeze, measurements, figures and output hashes. CSV nulls are empty cells; booleans are True/False. Raw source bytes stay untouched. The original user specification is preserved in SPEC.md. User amendments and protocol details are in DECISIONS.md.

The accepted Phase 0 report is preserved in report/PHASE0_REPORT.md and its original run folders. Do not rerun Phase 0 to replace the current report: use its source script only for historical intake reproduction. The current canonical corrected ZL table is data/voynich/ZL_lines_corrected.csv; the original Phase 0 table remains alongside it.

## Phase 4/5 reproduction

Use Python 3.11+ and the project-local CUDA/analysis libraries (requirements-phase45.txt). CUDA torch is pinned to 2.9.1+cu128 for this RTX 5060. No global/JNSQ environment change is needed.

```powershell
python -m src.extend_phase3
python -m unittest discover -s tests -v
python -m src.phase4
python -m src.phase5
```

Phase 4 and Phase 5 resume completed jobs in config-derived run folders. Do not change configs or source data during a registered run. Phase 5 refuses an incomplete Phase 4 matrix. Main, cross-fit, sweep and changed-seed fits use the declared 96-step budget; endpoint/exposure flags are material qualification limits. Check report/PHASE5_VERIFICATION.json before treating Phase 5 as complete.

report/PHASE3_ACCEPTED_REPORT.md preserves the accepted checkpoint; report/PHASE3_EXTENDED_REPORT.md contains C12/C13 and the T1/T2 comparison. C12-before-rigidity-fix/ preserves the superseded implementation/data with its correction receipt; no C12 model used it.
