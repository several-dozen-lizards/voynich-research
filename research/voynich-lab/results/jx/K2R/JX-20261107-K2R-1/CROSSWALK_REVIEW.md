# K2R content-blind crosswalk — review required

This packet proposes structural identities only. No glyph strings, paired agreement, scores or direction calls were used. Equal folio/type line counts and ordinal position are the entire pairing rule. They require review and do not establish identity by themselves.

Original P/Pn units are body; T/Tn units are title. Other unit types are held. ZL Pt is title; P0/P1/Pc/Pr are body. Whole folio/type groups with unequal counts are held, without shifts or partial matching. Numeric IDs may differ.

## Counts

```json
{
  "proposed_pairs": 3219,
  "H_present": 3219,
  "H_missing": 0,
  "structural_folio_type_groups": 170,
  "ambiguous_folio_type_groups": 48,
  "unresolved_type_original_rows": 582,
  "proposed_H_heldout_families": 46,
  "glyph_content_used_for_pairing": false,
  "glyph_comparisons": 0,
  "models_fitted": 0,
  "scores_computed": 0
}
```

## Files to review

- crosswalk_candidates.csv: every proposed pair, reader coverage, source positions and confidence.
- folio_type_counts.csv: the complete count-equality basis by folio/type.
- held_metadata.csv: all count-mismatch groups and unresolved original types.
- reading_inventory.csv: all reader codes, provenance status and provisional metadata coverage.

## Sample proposals (metadata only)

| ZL | Original | Type | H present | Confidence |
|---|---|---|---|---|
| f100r.12 | f100r.P1.1 | body | True | structural, pending review |
| f100r.13 | f100r.P1.2 | body | True | structural, pending review |
| f100r.14 | f100r.P1.3 | body | True | structural, pending review |
| f100r.15 | f100r.P1.4 | body | True | structural, pending review |
| f100r.22 | f100r.P2.5 | body | True | structural, pending review |
| f100r.23 | f100r.P2.6 | body | True | structural, pending review |
| f100r.24 | f100r.P2.7 | body | True | structural, pending review |
| f100r.25 | f100r.P2.8 | body | True | structural, pending review |
| f100r.26 | f100r.P2.9 | body | True | structural, pending review |
| f100r.27 | f100r.P2.10 | body | True | structural, pending review |
| f100v.14 | f100v.P.1 | body | True | structural, pending review |
| f100v.15 | f100v.P.2 | body | True | structural, pending review |

Review decision requested from Re: approve these exact structural candidates with all listed ambiguous/unknown groups held, or identify metadata-supported corrections. Approval binds the exact CSV hashes; it does not certify glyph agreement or performance. No glyph-based corrections are allowed.

The supplied spec Stage1.3 requires this review before any glyph streams are compared. Stage1 span/support qualification and Stages2/3 remain NOT_RUN_PENDING_REVIEW. Thresholds remain .80 accuracy/.65 lower95% bound, with the inherited family support and stratum adjustment. No I-phase or real-ring scoring opens.
