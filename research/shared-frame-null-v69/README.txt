2026-10-23 — Shared shedy ___ shedy frame under conditional nulls

Open report.html. Same bath/hand2/CurrierB/rawP and v61 original-folio exclusions, shared H/F source loci; readings separate. Every readable middle word allowed. H total10, F11; in both, exactly3 middle types recur across>=2numberedfolios: ol, qokedy, qol.

Earlier v66 frame counts8H/8F restricted middle words to already observed qol-neighbour types. Full inventory adds Hqotol/ykedy and Fqotol/ykedy/sol. Prior subset counts are verified unchanged. All one-folio middle words, unknown middle cases, one-shedy-flank background windows and exact source lines retained. No semantic category assignments.

Frozen T=total occurrences; R=number of distinct middle types each across>=2folios. Primary null exchanges words within page/exactordinal/linelength/unknownmask buckets. Sensitivity shuffles readable interior spans within each line with endpoints and unknown barriers fixed. All words, including shedy, can move under those constraints; locking shedy would condition away frame recurrence. Bucket invariants and mobility recorded.

1999shuffles each. Frame-search correction uses maximum T/R across all ordered flank pairs and any middles, including frames not previously inspected. Raw maxima are conservative and can be set by common frames. Further factor8 covers H/F x2nulls x2statistics.

T never passes even the all-frame correction. R results:
H exact-slot: raw.0025; allframes.012; full8.096
H within-line: raw.0015; allframes.0045; full8.036
F exact-slot: raw.0100; allframes.0135; full8.108
F within-line: raw.0005; allframes.0195; full8.156

Only H sensitivity passes the frozen full point-estimate screen; primary exact-position results do not pass. A post-run exact-binomial Monte Carlo uncertainty calculation places the H sensitivity adjusted tail probability around.014–.063 at95%, crossing.05. No shuffles were added or tests changed. This is a narrow, control-dependent numerical result, not a robust H/F-shared result. Raw rarity, conservative selection correction and eight-panel correction remain separately visible.

Engineering diagnostics: each mode0/20exchangeable flags and20/20planted T detections, under one small generator. R power, historical-text validity and semantic roles are not qualified by these diagnostics. Exact source counts, original subset and all8saved-null result calculations verified.

Reproduce: python run.py (frozen input/script hash checks), python verify.py, python mc_uncertainty.py, python make_report.py.
NPZ files save target scores and all-frame maxima. RESULTS.json includes all observed frames and contexts. PROTOCOL.json/FREEZE.json fixed before manuscript outcomes. Browser visual review not performed; prior local-file policy block respected. Other reports and shared index unchanged.
