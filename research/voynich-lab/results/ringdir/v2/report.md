# RD-v2 Phase 0

| Chain | Outcome |
|---|---|
| D/Latin/glyph | PASS |
| D/Latin/word | PASS |
| D/missing_sources | NOT_RUN_MISSING_SOURCE |
| D/ZL/glyph | PASS |
| D/ZL/word | FAIL_DIRECTION |
| F/G2/glyph | PASS |
| F/G2/word | PASS |
| F/G3/glyph | PASS |
| F/G3/word | PASS |
| F/G4/glyph | FAIL_DIRECTION |
| F/G4/word | PASS |
| F/missing_sources | NOT_RUN_MISSING_SOURCE |
| F/Naibbe/glyph | FAIL_DIRECTION |
| F/Naibbe/word | FAIL_DIRECTION |
| K/Latin | FAIL_UNSUPPORTED |
| K/ZL | FAIL_UNSUPPORTED |
| O/Latin/p1 | FAIL_ORIGIN |
| O/Latin/pos | FAIL_ORIGIN |
| O/missing_sources | NOT_RUN_MISSING_SOURCE |
| O/ZL/p1 | PASS |
| O/ZL/pos | FAIL_ORIGIN |
| P/Latin/glyph | FAIL_POOLED |
| P/Latin/word | PASS |
| P/missing_sources | NOT_RUN_MISSING_SOURCE |
| P/ZL/glyph | FAIL_POOLED |
| P/ZL/word | FAIL_POOLED |
| T | REGISTERED_DESCRIPTIVE_ONLY |
| U/Latin/glyph/D | PASS |
| U/Latin/glyph/P | FAIL_POOLED |
| U/Latin/word/D | PASS |
| U/Latin/word/P | PASS |
| U/missing_sources | NOT_RUN_MISSING_SOURCE |
| U/ZL/glyph/D | PASS |
| U/ZL/glyph/P | FAIL_POOLED |
| U/ZL/word/D | FAIL_DIRECTION |
| U/ZL/word/P | NOT_RUN_UPSTREAM_FAILURE |

| ZL direction signal | 6–10 | 11–20 | 21–40 | 41–80 |
|---|---:|---:|---:|---:|
| word | 37.5% | 50.5% | 74.0% | 77.5% |
| glyph | 84.0% | 85.5% | 97.5% | 97.5% |

**Cross-boundary unit direction:** freshly qualified ZL bins6–10,11–20,21–40,41–80. Its uncertainty-inclusive counterpart also qualifies those bins. Every word/glyph direction shuffle-null check is retained in its chain receipt; failures cannot be overridden by prior runs.

**Fresh word-bigram direction:** ZL no bin qualifies; 41–80 accuracy77.5% with cluster95% CI64.4–87.3%, below the registered80% threshold. RD-v1/C2 are not overwritten.

**Pooled direction:** ZL clean and uncertainty-inclusive word/glyph pooled chains do not qualify. Clean21–40 comprises13 loci; the uncertainty-inclusive planned21–40 set comprises47. The full mixed-condition, forward/reverse and weighting rates appear in each P/U-P bin table. Limited family-level power is retained, not replaced by individual-locus accuracy.

**Paragraph-origin S-p1:** isolated known-direction21–40 gate passes:98 paragraphs, 57.1% hit,16.9% mean chance, excess95% CI31.0–48.8 percentage points. End-to-end with freshly inferred word direction is38.8% (descriptive, not a passed end-to-end gate). At41–80 isolated hits41.7% fail the50% threshold despite positive excess. S-pos origin does not qualify. The paragraph-to-ring transfer assumption remains untested.

**Seam count:** unsupported in both corpora. ZL k=1 at21–40 has3 examples from1 family, and41–80 has0. No seam-count accuracy was invented.

Stem-collapse, S-m and the specified three-signal combination are NOT_RUN_MISSING_SOURCE. The exact Oct22 definitions were not substituted. F uses bound engineering generators and Naibbe source/table; its full direction curves are descriptive, not mechanism identification. T is registered for a later descriptive comparison only.

U preserves first alternatives and unknown barriers. Latin has no independent uncertainty annotation and is an unmarked control; K/O Latin uses artificial layout. Shared-source Monte Carlo sets are not independent manuscript replications. All predictions and failures are reported without choosing a successful replacement pipeline.

Every calibration chain completed or stopped before final aggregation. A Windows path-label mismatch then failed report assembly. The frozen instrument and all arm artifacts were left unchanged. The report-only finalizer is separately hash-bound in reporting_receipt, and no calibration was rerun. See REPORTING_FAILURE.json.

**Preservation:** earlier run hashes unchanged; radial held; no real-ring scores, Phase1+ comparisons or corrected-order export.
