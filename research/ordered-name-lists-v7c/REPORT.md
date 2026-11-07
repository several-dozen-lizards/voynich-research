# Voynich v7 Parts A/C — infrastructure and historical source draft

25 October 2026. Status: **PART A NOT QUALIFIED; PART C NOT SCORED.**

The user supplied Part C, then clarified that Part A was a specification without code and supplied the joint B/C declaration. This branch built the first evaluator prototype and ran an initial known-text engineering qualification. The qualification did not pass. No proposed manuscript key, open-sign structural pre-test, name alignment or vault evaluation ran.

## Results that govern continuation

| Gate | Result | Consequence |
|---|---|---|
| Known Latin cipher, fixed context key | PARTIAL | A8 positive must PASS; admission fails |
| Same cipher with 5 of 27 base entries corrupted (rounded 20%) | PARTIAL | Retained near-miss result, no promotion |
| 100 independent random proposals | 93 FAIL, 7 PARTIAL, 0 PASS | Literal A8 requirement of>=99% FAIL is unmet |
| Actual Voynich flexible-key trap | NOT RUN | Still required |
| All required v5/v6 generator controls | NOT RUN | Shuffled-text surrogate is explicitly insufficient |
| Engineering/integrity checks | 20 tests; 129 verification checks pass | Does not override scientific qualification |

The true key scored E1 lexical matches 927/1200 (77.25%), against a C3 median 0.75%. Its target-Latin loss was 2.94015 bits/character against a C3 median 5.35701. Both reach the conservative 99th-percentile criterion (Monte Carlo upper-tail p=1/1001). Key complexity is 140.31275 bits; the implemented coherence total is 25247.65725 bits.

Those attractive scores DO NOT make a PASS. The true key's E3 order gain was 0.0377986 bits/character; the glyph-shuffled control's was 0.0466466. The implementation's strict real-versus-control gate therefore failed. The 20%-corrupted key's coherence also remained positive (7807.63515 bits), showing why a positive coherence number alone cannot be the verdict.

The negative proposals were independently sampled from the same fixed key family, with a separate seed, and compared against the 1000-key C3 bank. Seven reached PARTIAL and none PASS. “No random PASS” is 100% non-promotion; it is not the spec's narrower “>=99% FAIL”. That wording is applied literally here. 100 proposals are an empirical calibration sample, not a precise population false-alarm bound.

Full scores, the two 1000-key banks, reconstructed keys, seeds, data and plans are in [HARNESS](HARNESS/). The first slow attempt was interrupted before producing results and retained under [history/attempt-1](HARNESS/history/attempt-1/STATUS.json). The replacement uses pinned RapidFuzz 3.14.1 for exactly the same normalized edit-distance threshold; independent small-string comparison checks passed.

## Infrastructure delivered

[HARNESS/harness.py](HARNESS/harness.py) validates a fixed unit/value map, finite explicit context conditions, mapping provenance and declared training exposure. It rejects unknown custody, overlapping train/test IDs and all four reserved zodiac folios. It records K, E1–E6, both C1 variants, C2,1000 equal-complexity random keys and separate reading verdicts. Ambiguous or unknown tokens remain failures in rates; language losses abstain instead of benefitting from deletion.

This is a prototype, with deliberately explicit limits: it takes pre-tokenized unit arrays; E1/E2 use token annotations; the real v6 multi-token label/pair adapter is absent. E5 supports supplied sequence/sum checks but does not implement the Part B search. The period-language control is edited Latin herbal verse in expanded orthography, with artificial 12-word lines, from an already-exposed development source. The observed fixture is not a manuscript label task and is not an independent H/F qualification. See [implementation contract](HARNESS/IMPLEMENTATION-CONTRACT.json) and [source provenance](HARNESS/SOURCE.md).

[C2_pretest.py](C2_pretest.py) implements descriptive concentration and exact ordered-pair probabilities on upstream registered glyph units. It includes folio in ring identity, separates H/F, records missing coverage, rejects reserved signs and checks gates before opening its input. Only authored fixtures exercised it. Actual C2 looks used: 0 of 10. NOT RUN is not NO MARKER.

## Historical source assembly

[LISTS.json](LISTS.json) is **DRAFT_NOT_FROZEN**. Three Picatrix source sequences have 28 positions each: mansion names in I.4, mansion names in IV.9 and mansion spirits in IV.9. Across 84 positions, 82 contain edited names. Both IV.9 sequences preserve the blank 22nd mansion; spirit 7 preserves the distinct invocation Siely and declarative Selehe. No name was borrowed from a later source to fill a gap.

The source is [Pingree's 1986 Latin critical edition, hosted by the Warburg Institute](https://commons.warburg.sas.ac.uk/downloads/8g84mm241?locale=en). The 21,420,211-byte source PDF and page-numbered extraction are archived; all 13 relevant name-list pages were rendered and visually inspected. OCR ambiguities such as Al-/AI- and Aziel/Azie1 were checked against the printed page. The list order and source coordinates are retained; no Voynich unit has been assigned to a historical unit.

The edition's introduction supports a medieval Latin tradition, but its full apparatus was published separately on microfiches and is absent from the downloaded volume. Thus these are edited forms, not an exhaustive catalogue of every attested variant, nor a proof of an early witness for each individual spelling. All three lists are currently ineligible for claims. Automated suffix/prefix fields mark orthographic candidates only; they do not establish morphology.

[LISTS-LATE.json](LISTS-LATE.json) starts a separate 1559 Heptameron planetary/day sequence, including Cassiel/Caphriel at Saturday. It is also a draft. The [source edition and manuscript discussion](https://www.esotericarchives.com/solomon/heptamer.htm) distinguishes medieval planetary material from later arrangements; precursor evidence is not used to backdate the entire later list.

The [source audit](SOURCE-AUDIT.json) accounts individually for every candidate tradition named in C1. It records the early Escorial Lapidary witness from the [owning library](https://rbdigital.realbiblioteca.es/s/rbme-expo/item/13127), the mid14th-century Liber Juratus witness from [Boudet's manuscript-based study and edition](https://www.persee.fr/doc/mefr_1123-9883_2002_num_114_2_9254), and the later Raziel copy in [the British Library catalogue](https://searcharchives.bl.uk/catalog/040-002116236). Ordered texts and variants from these traditions remain to be extracted. Ars Notoria, Greek/Latin/Arabic decans, Arabic mansions and the other late sources remain unresolved individually. None is silently excluded as a negative finding.

## Declaration, custody and budget

The [full joint declaration](JOINT-VAULT-DECLARATION-SOURCE.md) is transcribed from the human's reply and SHA256-sealed in [its receipt](JOINT-DECLARATION-SOURCE-SEAL.json). An earlier summary and seal are retained. **Timing exception:** initial historical source collection preceded the arrival of this declaration. No raw Voynich transcription or label-sequence file was opened and no B/C score was computed. The project routing file was read for orientation and contains historical Voynich examples; this session must not be described as having no prior exposure to any Voynich strings.

[CUSTODY.md](ZODIAC/CUSTODY.md) records the human's answer and the relayed Claude statement, with receipt checks still pending for prior project runs. The provisional grade is untested-but-inventoried for each reserved sign, separately for B/C. It is not a certified fresh holdout.

[BUDGET.json](BUDGET.json) remains UNALLOCATED. The forwarded 0.05 value is a recommendation, not explicit human authorization. alpha_V is null and spend is 0. A numerical budget seal cannot be claimed yet. No vault result file has been created.

## Next required work

Diagnose and qualify Part A before scoring any real key or C2 input. Preserve this first failed qualification rather than modifying the frozen verdict after seeing its output. Settle the precise A6 control-gain comparison before a new qualification freeze: the current prototype compares E3 raw order gains and E4 raw negative loss against controls; separate C3-adjusted control gains are not computed. The full source adapter, real generator controls, noisy dual-reading positive, E2/E5 controls and actual flexible-key trap still need implementation/qualification.

Complete C1's source and variant audit, freeze its list/variant search universe, complete custody receipts, and obtain an explicit numerical alpha allocation. Resolve the unit-count and feature-definition questions in [DESIGN-ISSUES.md](DESIGN-ISSUES.md). Only then run the logged open-sign C2 step. C3 requires all arms to be frozen together, full-search nulls and qualification; B and C must both be ready before the single authorized vault session. Written vault OK remains a separate final requirement.

No finding about Voynich names, numerals, language or semantics follows from this delivery.
