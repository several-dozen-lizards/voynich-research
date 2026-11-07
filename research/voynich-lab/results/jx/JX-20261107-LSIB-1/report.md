# JX-20261107-LSIB-1 — corrected adapter and source gates

**STOP_FAIL_SOURCE_FIDELITY**

Adapter: PASS_ADAPTER_ENGINEERING; 15/15 authored fixtures passed.

Layout locators no longer assert paragraph starts. Unknown starts remain null; locus-local text is retained. Safe fragments are not recovered paragraphs.

Source collation against the hash-bound original Stolfi1.6e6 archive:

```json
{
  "status": "FAIL_SOURCE_FIDELITY",
  "selected_loci": 3810,
  "counts": {
    "MATCH": 1890,
    "HELD_SOURCE_SPAN": 1190,
    "FAIL_SOURCE_DIFFERENCE": 335,
    "UNRESOLVED_IDENTITY": 395
  },
  "difference_types": {
    "paragraph_end_conversion": 104,
    "glyph_stream": 330,
    "word_boundary_offsets_or_types": 330
  },
  "unparsed_original_H": 0,
  "clean_compared": 2225,
  "clean_families": 89,
  "original_sha256": "309e717d0dcc13115eace006eb40ece6c0ac89faab48f1569dcb9732d26b02f0",
  "lsi_sha256": "3f3f2af18cde10efe75c582f49b07b651c3397022fcbfa5854fecc424c121afa",
  "unknown_start_records": 3810,
  "scope": "Non-ring ordinary paragraph H only; original publisher/editorial source, not manuscript truth"
}
```

Every mismatch and held span is retained in source/collation.jsonl. A mismatch is an unresolved conversion difference, not automatically a demonstrated error in either editorial representation. No title-attachment or other exception was introduced after comparison.

Boundary diagnostic: NOT_RUN_UPSTREAM_FAILURE.

Prior K1/K2 results, failed adapter run and all gate labels remain preserved. Numerical verification did not certify source semantics. No direction calibration or I-phase was rerun. Spacing interpretation and real-ring scoring CLOSED; radial HELD.
