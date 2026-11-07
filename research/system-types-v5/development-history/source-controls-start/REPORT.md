SANDBOX MECHANICS QUALIFIED — CLAIM SCORING LOCKED; H3 UNRESOLVED.

# Voynich system types v5: mapping and generator qualification

Recorded 24 October 2026, America/New_York. This continuation implements explicit EVA groups and qualifies the generator mechanics. It does not fit or eliminate manuscript production families.

## Results

- **19/19 engineering and candidate-entrypoint tests pass.**
- **200/200 known-source and mechanism trials pass**, across20 seeds and two layouts for G1–G4/G6.
- **1,600/1,600 EVA group maps pass**: four families ×20 seeds ×two layouts ×10 separate Currier/scribe/H-F cells. Every tested map is injective, all rendered groups are registered, and inverse recovery works with retained unit boundaries.
- **Published G5 passes five repeat pairs**: seeds19/23/31/43/59 each produce identical output on repetition and different output across seeds. All100 native lines parse. Its initial seed line is excluded from the fit-only summaries.
- **No H1–H8 computation ran. No claim FREEZE exists. H3 remains unresolved.**

`GENERATOR-QUALIFICATION.json`, `GROUP-MAPPING-QUALIFICATION.json`, `MECHANISM-CONTROLS.json`, `G5-PUBLISHED-QUALIFICATION.json` and `TEST-RESULTS.json` contain the results. The source/code/settings plan was hashed before each qualification run. `QUALIFICATION-PLAN-v3.json` is a sandbox seal, not a claim freeze.

## Mapping implemented

Longest-match atoms are `cth/ckh/cph/cfh/ch/sh`, then single lowercase EVA characters. These are operational transcription units, not established manuscript graphemes. Each target inventory contains every observed overlapping span of1–3 such atoms **within a readable word**. No word boundary, unknown slot, neighboring-word outcome, line-opening flag or H3 estimator contributes.

Each source unit and target span receives one position class from its own distribution: initial, medial or final at>=95%, otherwise free. Whole-word target spans and source singletons count as free. Units are ranked by frequency within class, with SHA256(seed:unit) ties. Assignments are injective. Capacity failure or an unseen source unit raises an error; there is no silent merging, invented span, wider fallback or borrowed class. The exact inventories and hashes are saved.

G4 maps each source letter/code variant to a span of1–3 atoms; its width comes from the fixed rank mapping. Optional null units and position variants are explicit. The earlier version independently preassigned widths and exhausted the one-atom position classes; all400 failures remain archived. Narrow max_expansion settings can still abstain honestly.

Mapped unit boundaries accompany the display strings. Concatenated EVA is not claimed uniquely decodable, and reparsing a flat string can fuse atoms across latent group boundaries. Fit summaries continue to use literal EVA characters as previously specified. Group counts and classes are an explicit target-informed mapping input beyond the single-character fit summaries; this information budget must be retained in the eventual claim protocol.

## Generator scope

| Family | What was qualified | Remaining scope limit |
|---|---|---|
| G1 | Source order/letters preserved; deterministic mapping on edited Latin herbal | Italian/Czech/Occitan coverage remains pending; current Latin/German Bible sources are not medical |
| G2 | Sourced abbreviation rule subset; probability0 identity; probability1 applies all eligible suffix rules; intermediate rate checked against binomial variation | Synthetic rule rates on expanded text; no real diplomatic abbreviated-Latin control |
| G3 | Reduces to G2 at symbol probability0; at probability1 all `et` opportunities get a separate symbol unit | `et` sign is attested; after-vowel/context variants are synthetic parameters; broad medical concept inventory pending |
| G4 | One letter/code variant per source letter,1–3-atom mapped groups, optional nulls, repeatability | Mapping and position/null boundary settings overlap G1; not independently identifiable there |
| G5 | Pinned **unmodified published Java source**, compiled and run with native layout; repeat-seed and distinct-seed controls | Full mechanism/model recovery remains unrun; seed-line policy and parameter priors still need claim freeze |
| G6 | Repeated prefix/root/suffix column blocks, explicit three-hole offsets, irregular vertical moves, blanks; every output reconstructed independently from cell coordinates | A specified Rugg-style parameterization, not a unique historical table or human movement law |

The candidate entrypoint is **`registry.produce`**. Its G5 route always runs the published implementation and rejects forced target token-count layouts. The earlier Python G5 surrogate remains available solely as a development control; it is not the qualified candidate. Corpus-derived built-in VMS follow tables are rejected; only `curveline`/`none` follow options are admitted here. Java is portable within this experiment; no system settings were changed. Download/archive checksums and source commit hashes are retained.

Source provenance: [Timm–Schinner published repository](https://github.com/TorstenTimm/SelfCitationTextgenerator); [Rugg's mechanism account](https://hydeandrugg.wordpress.com/2014/03/02/hoaxing-the-voynich-manuscript-part-7-producing-the-text/). The G6 implementation follows repeated three-column blocks with offset holes and variable vertical movement; its finite step law and edge handling are explicit modeling choices.

G2/G3 sources: [HMML abbreviation reference](https://hmmlschool.org/lexicon/14357/), [Ad fontes](https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/abkuerzungen), and [Folger's rum example](https://www.folger.edu/blogs/collation/abbreviations-and-signatures/). These support rule types, not the chosen probabilities or a particular herbal's usage. `RULE-SOURCES.json` links each rule and distinguishes attestation from synthetic choices.

## Known-source controls

The edited Latin [Macer / De viribus herbarum](https://la.wikisource.org/wiki/De_viribus_herbarum) was archived at Wikisource revision272959 with HTML, source-word hashes and attribution. It contains13,967 extracted words in77 poem sections. Entire sections were split first60% development / final40% qualification, and all qualification trials use the latter source sections. This is edited herbal verse with expanded orthography, not a14th–15th-century diplomatic source. Lowercase ASCII word extraction and source wrapping are explicit development policies; normalization/length robustness remain before the claim run. Source sections are disjoint; vocabulary is not.

The abbreviation sign units remain separate inside source words. The source/control results establish implementation behavior, not historical accuracy, language identification or readability of mapped EVA.

## Preserved failures and current boundaries

`development-history/sandbox-1/` preserves the original40 mapping abstentions. `development-history/group-qualification-1/` preserves all400 exact-width cipher failures and an insufficient-capacity test fixture; the fixture was corrected without relaxing the rejection rule. Qualification2's passing results remain archived before the production wrapper's corpus-table guard and candidate-entrypoint checks were added. Qualification3 replays the full schedule with current owner hashes. No held score was used to choose the repairs.

H3 remains **UNRESOLVED**. Its earlier noise correction and context construction have not been replaced. H1/H2 retain Re's approved move to log odds ratio with recomputed targets later; the old RD strengthening numbers are not reused. Exact H1/H2/H5/H6/H7/H8 definitions, H4's overlap with fitted position shares, fair layout/source-length conditioning, all source-language coverage, priors/tolerances, real abbreviated-Latin control and full recovery/confusion gates remain before a claim freeze.

“Mechanics qualified” is deliberately narrower than “family qualified for elimination.” The full recovery/confusion experiment requires H1–H8 and remains closed. No posterior samples, PPC percentiles, ABC model probabilities, survivors or eliminations have been produced.

## Reproduce

```powershell
$env:OPENBLAS_NUM_THREADS='1'
python -m unittest discover -s system-types-v5 -p 'test_*.py' -v
python system-types-v5/qualify_generators.py run
python system-types-v5/prepare.py
```

The existing qualification plan must match its owners. Starting a new plan is a separate explicit sandbox cut, preserving the old trials first. `held.score` continues to refuse scoring without a complete valid claim freeze; its statistic dispatch remains unimplemented rather than returning surrogate scores.
