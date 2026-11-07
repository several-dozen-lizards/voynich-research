2026-10-23 — Qualified replacement for v75 opening-search precision

Open report.html. User explicitly required qualification before manuscript rescoring. PROTOCOL.json and FREEZE.json fixed method, control banks, gates and guarded rescore before qualification. All8banks passed before rescore.py opened any v75 manuscript score matrix. No family narrowing, word recoding, panel pooling or new manuscript permutations.

This is a NEW count-unit-regularized maxT correction, not a refinement of the same v75 minP p-values. For each contrast use pooled observed+null mean and sqrt(pooled variance+1count^2). Compare selected absolute standardized contrast directly against each row's maximum across every original candidate contrast. Symmetric row transform supports exchangeable-row permutation ranks. Constant/rare columns retained, no Gaussian tail approximation. Original14panelBonferroni retained.

Qualification:8independent anonymous joint-score banks x14actual family dimensions x4096exchangeable integer rows, variable count scales, correlated columns, position-only offsets, rare1count spikes and constants. Eight global rotation flag counts189,193,193,191,195,193,193,191 (4.61–4.76%). These are DEPENDENT pseudorow rotations checking a finite rank bound, not independent false-positive trials. All empirical minimum adjusted p=.00341796875 below frozen.01 gate. Worst8SDpower63/64 (98.4%); all64injectionrows perbank/panel reused null scores.6SDpower78.1–100%,4SD10.9–79.7%,2SD0–10.9%, preserved without a moderate-dose pass requirement. H-onlypairedcontrols allbelow5%gate. Exact72row authored line-permutation orbit checked overlapping class counts, uncertainty barriers and tail ranks; too coarse for14panelpower. No historical/semantic qualification claimed.

After qualification, unchanged v75 4999shuffle matrices rescored for all14separate H/F/section/hand/Currier/rawP panels. Principal sh->qok passes bothreadings:
Bath hand2/B H211/130,F212/130; adjustedp.0028each.
Starred hand3/B H167/86,F166/86; adjustedp.0028each.
Each has zero null FAMILY-MAX exceedances; .0028 is the finiteMCpoint-estimate floor14/5000, not a claim of equal true probabilities or zero p. Other botanical and ambiguous-hand principal panels do not pass. All original reverse pairs and folio exceptions preserved via original source-ledger link and copied report details.

Qualification resolves the numerical correction problem under its specified generators and finite-row rank argument. It does not validate every linguistic null assumption. The unchanged within-line null fixes word multisets, endpoints and unknowns, not every interior ordinal or all junction mechanisms. Exposed corpus, not untouched confirmation. No word meaning, syntactic role, language or universal grammar inference. H/F are alternate readings, not independent manuscripts.

Verification: qualifications replayed; all14rescore arrays and target tails independently checked against original matrices/counts; exact matrix hashes stored. Independent scalar mean/scale check tolerates1e-12 floating summation differences; no method changes. MC-PRECISION.json uses explicitly approximate binomial uncertainty with dependence caveat, not exactCIs for pooled studentization.

Reproduce qualification: python qualify.py (no manuscript score access).
Guarded rescore: python rescore.py (refuses if QUALIFICATION.status != PASS).
Numerical replay: python verify.py.
Report: python make_report.py.

Original v75 failure artifacts and all other experiments unchanged. All gates, planted misses, low-dose failures, nonpassing panels and ambiguous hands retained. Browser visual review not performed; prior local-file URL policy block respected. Shared research index not modified while another chat is active.
