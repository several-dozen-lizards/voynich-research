# RD-C2 circular-only calibration continuation

| Gate | Result |
|---|---|
| unit_mirror | PASS |
| any_boundary | PASS |
| unique_origin | FAIL |
| boundary_pairing_null | NOT_RUN |

**STOP_FAILED_GATE**; stop stage: unique_origin.

Scope is circular 41–80-word calibration only. Radial text remains HELD. RD-v1 remains STOP_FAILED_GATE, with every registered prior-run byte unchanged. This is a separately authorized follow-up, not a retroactive pass of RD-v1.

Direction evidence is inherited: ZL 41–80 recovery 83%, cluster 95% CI 72.6–89.6%; Latin circular direction passed at this bin. The earlier circular shuffle-null checks were pooled over lengths, not separately requalified within this bin.

```json
{
  "name": "unit_mirror",
  "n": 200,
  "distinct_windows": 200,
  "families": 19,
  "accuracy": 1.0,
  "passed": true
}
```

```json
{
  "name": "any_boundary",
  "passed": true,
  "bins": [
    {
      "name": "any_boundary",
      "bin": 5,
      "n": 200,
      "distinct_windows": 200,
      "families": 19,
      "hit_rate": 0.935,
      "end_to_end_hit_rate": 0.875,
      "excess_ci": [
        0.41038494596218233,
        0.5252937417292205
      ],
      "end_to_end_excess_ci": [
        0.32341721845192356,
        0.4665554074750275
      ],
      "null_excess_ci": [
        -0.0859492637971467,
        0.0370801162444551
      ],
      "passed": true
    }
  ]
}
```

```json
{
  "name": "unique_origin",
  "passed": false,
  "bins": [
    {
      "name": "unique_origin",
      "bin": 5,
      "n": 0,
      "distinct_windows": 0,
      "families": 0,
      "hit_rate": 0,
      "end_to_end_hit_rate": 0,
      "excess_ci": [
        null,
        null
      ],
      "end_to_end_excess_ci": [
        null,
        null
      ],
      "null_excess_ci": [
        null,
        null
      ],
      "passed": false
    }
  ]
}
```

New nuisance transforms/mirror flags were sealed before new scores. All 200 scope-eligible windows were used in the dedicated mirror set, replacing an undersized 10% subset by a predeclared sample-size amendment. Signals, source windows and thresholds were not tuned. Trial-level CSV/JSON and event receipts accompany the report.

Any-boundary localization and unique original-line-origin recovery remain separate. Absent complete 41–80-word single-line support is an unsupported gate, not a reason to manufacture long lines or extrapolate shorter-line results.

Calibration failure concerns the instrument/source support; it makes no finding about manuscript circle direction, starts, meanings or ring kind. No real rings were scored, no Phases 1–4 ran and no corrected transcription layer was created.
