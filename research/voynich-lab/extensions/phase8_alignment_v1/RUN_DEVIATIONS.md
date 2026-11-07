# Phase 8 receipt limitations discovered after the run

This note changes no method, score, classification, gate, seed, dataset, registration or earlier result. Qualification remains FAIL and Voynich remains CLOSED. No replacement fits or scoring were performed.

- The null routine refits vocabulary and mapping for every assignment as registered, but persists only its assignment and final Q/D scores. Per-null fold vocabularies, permutations, component scores and FAQ iteration receipts were computed in memory and discarded. The protocol/report language promising full null optimizer receipts is therefore too broad. Observed held-out alignment mappings, fold scores, vocabulary coverage and optimizer receipts are retained in ALIGNMENT.json; all 99 null assignments and Q/D statistics are retained in PAGE_NULLS.json. The missing intermediate null receipts are unavailable without new fits, which were not run.
- Physical mappings and vocabularies are learned outside the entire tested quire as registered, but those intermediate mappings are not persisted. The saved physical receipts contain conjugate-pair similarities, partition-pair metadata, all 1,999 permutation statistics and the reported p-value. Do not describe these as complete mapping receipts.
- The initial unstratified split failed a support preflight before registration/control scoring. That attempt and its support failure are preserved; the registered split uses deterministic known-A/B-composition stratification. This is a pre-registration engineering revision, not an outcome-based calibration rescue.

These logging limitations reduce intermediate audit coverage. They do not permit a positive finding: the registered qualification fails even on the available completed scores.
