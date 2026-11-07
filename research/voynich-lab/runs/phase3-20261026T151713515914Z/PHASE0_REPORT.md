# Voynich pattern-model lab — Phase 0

**STOP: Phase 0 complete. Phases 1–5 have not run.**

Run: `phase0-20261026T135010369977Z`; Python 3.12.14; deterministic intake, seed 1729 (no sampling).

## Transcriber disagreement: operational noise floor

LSI pair-weighted character agreement: **95.73%**; disagreement: **4.27%**.
19,741 included line-pairs; 5,282 loci have multiple recorded versions.

Agreement = 1 − exact Levenshtein distance / maximum cleaned line length, pooled by summing distances and denominators. Includes normalized word spaces; unknown symbols never match. See agreement_by_pair.csv for H/F and every other pair separately.

This is an operational transcription-sensitivity estimate, not a universal statistical floor or a quantity in bits/token. Historical readings share ancestry, coverage and alphabet conversion; pair counts are dependent. No corpus-wide accuracy or full-coverage agreement is inferred. Locus alignment is within LSI only; ZL/LSI locus IDs are not assumed physically interchangeable.

Exclusions: {'multi_transcriber_loci': 5282, 'candidate_pairs': 21474, 'included_pairs': 19741, 'excluded_alternate_branch': 1478, 'excluded_missing_span': 248, 'excluded_empty': 7}. All candidate pairs and reasons are retained in agreement_lines.csv.

## Intake counts

Characters exclude spaces; words split both certain and uncertain spaces. Vocabulary includes UNK-bearing words. These are EVA code-point counts, not manuscript glyph counts. Each row is one IVTFF locus/version; split line segments and labels are not merged into physical lines. LSI rows must not be pooled as a single corpus.

| Source | Transcriber | Loci | Pages | Words | EVA characters | Vocabulary |
|---|---|---:|---:|---:|---:|---:|
| LSI | C | 2,550 | 145 | 18,116 | 90,903 | 4,677 |
| LSI | D | 42 | 13 | 284 | 1,459 | 229 |
| LSI | F | 4,074 | 202 | 33,331 | 169,676 | 6,748 |
| LSI | G | 446 | 36 | 4,177 | 21,661 | 1,765 |
| LSI | H | 5,216 | 225 | 37,920 | 191,724 | 8,147 |
| LSI | I | 1 | 1 | 5 | 20 | 5 |
| LSI | J | 15 | 4 | 112 | 556 | 81 |
| LSI | K | 209 | 13 | 258 | 1,442 | 216 |
| LSI | L | 205 | 10 | 1,232 | 6,312 | 701 |
| LSI | N | 28 | 1 | 216 | 995 | 167 |
| LSI | P | 2 | 1 | 2 | 10 | 2 |
| LSI | Q | 5 | 3 | 7 | 40 | 7 |
| LSI | R | 31 | 1 | 73 | 437 | 70 |
| LSI | T | 568 | 12 | 5,362 | 29,698 | 1,971 |
| LSI | U | 1,990 | 123 | 11,386 | 53,963 | 3,632 |
| LSI | V | 1,918 | 68 | 9,653 | 46,061 | 2,506 |
| LSI | X | 37 | 2 | 62 | 296 | 59 |
| LSI | Z | 7 | 1 | 9 | 52 | 9 |
| ZL | ZL | 5,385 | 227 | 39,026 | 194,687 | 8,329 |

## Per-section counts

| Source | Transcriber | Section | Loci | Words | Characters |
|---|---|---|---:|---:|---:|
| LSI | C | astronomical | 36 | 239 | 1283 |
| LSI | C | biological | 787 | 6453 | 33722 |
| LSI | C | cosmological | 54 | 318 | 1632 |
| LSI | C | herbal | 1428 | 9777 | 47443 |
| LSI | C | pharmaceutical | 37 | 119 | 666 |
| LSI | C | stars | 47 | 433 | 2371 |
| LSI | C | text_only | 110 | 554 | 2648 |
| LSI | C | zodiac | 51 | 223 | 1138 |
| LSI | D | astronomical | 1 | 31 | 178 |
| LSI | D | herbal | 27 | 163 | 795 |
| LSI | D | pharmaceutical | 6 | 12 | 67 |
| LSI | D | stars | 7 | 69 | 375 |
| LSI | D | text_only | 1 | 9 | 44 |
| LSI | F | astronomical | 21 | 177 | 975 |
| LSI | F | biological | 806 | 6681 | 33777 |
| LSI | F | cosmological | 127 | 1171 | 5692 |
| LSI | F | herbal | 1627 | 11133 | 54816 |
| LSI | F | pharmaceutical | 224 | 2226 | 11082 |
| LSI | F | stars | 1084 | 10705 | 57054 |
| LSI | F | text_only | 185 | 1238 | 6280 |
| LSI | G | astronomical | 5 | 53 | 264 |
| LSI | G | herbal | 177 | 1443 | 7344 |
| LSI | G | stars | 264 | 2681 | 14053 |
| LSI | H | astronomical | 240 | 846 | 4596 |
| LSI | H | biological | 917 | 6915 | 34681 |
| LSI | H | cosmological | 323 | 2560 | 12137 |
| LSI | H | herbal | 1636 | 11392 | 55242 |
| LSI | H | pharmaceutical | 456 | 2568 | 12982 |
| LSI | H | stars | 1084 | 10683 | 56924 |
| LSI | H | text_only | 225 | 1626 | 8196 |
| LSI | H | zodiac | 335 | 1330 | 6966 |
| LSI | I | stars | 1 | 5 | 20 |
| LSI | J | stars | 12 | 109 | 553 |
| LSI | J | text_only | 3 | 3 | 3 |
| LSI | K | biological | 1 | 2 | 9 |
| LSI | K | pharmaceutical | 89 | 98 | 585 |
| LSI | K | zodiac | 119 | 158 | 848 |
| LSI | L | herbal | 34 | 279 | 1407 |
| LSI | L | pharmaceutical | 171 | 953 | 4905 |
| LSI | N | text_only | 28 | 216 | 995 |
| LSI | P | pharmaceutical | 2 | 2 | 10 |
| LSI | Q | pharmaceutical | 1 | 3 | 10 |
| LSI | Q | zodiac | 4 | 4 | 30 |
| LSI | R | astronomical | 31 | 73 | 437 |
| LSI | T | stars | 568 | 5362 | 29698 |
| LSI | U | astronomical | 225 | 756 | 3949 |
| LSI | U | biological | 172 | 479 | 2306 |
| LSI | U | cosmological | 343 | 2143 | 9557 |
| LSI | U | herbal | 601 | 4162 | 19828 |
| LSI | U | pharmaceutical | 309 | 1698 | 8132 |
| LSI | U | stars | 44 | 427 | 2043 |
| LSI | U | text_only | 117 | 641 | 2936 |
| LSI | U | zodiac | 179 | 1080 | 5212 |
| LSI | V | astronomical | 219 | 603 | 3239 |
| LSI | V | biological | 917 | 7329 | 34675 |
| LSI | V | cosmological | 232 | 954 | 4028 |
| LSI | V | herbal | 33 | 164 | 767 |
| LSI | V | pharmaceutical | 216 | 239 | 1339 |
| LSI | V | text_only | 2 | 8 | 41 |
| LSI | V | zodiac | 299 | 356 | 1972 |
| LSI | X | text_only | 8 | 28 | 126 |
| LSI | X | zodiac | 29 | 34 | 170 |
| LSI | Z | astronomical | 7 | 9 | 52 |
| ZL | ZL | astronomical | 240 | 883 | 4607 |
| ZL | ZL | biological | 861 | 6387 | 31965 |
| ZL | ZL | cosmological | 401 | 2255 | 10536 |
| ZL | ZL | herbal | 1640 | 11588 | 55313 |
| ZL | ZL | pharmaceutical | 458 | 2589 | 13066 |
| ZL | ZL | stars | 1164 | 11646 | 60743 |
| ZL | ZL | text_only | 286 | 2362 | 11464 |
| ZL | ZL | zodiac | 335 | 1316 | 6993 |

## Missing metadata

| Source | Field | Missing | Total |
|---|---|---:|---:|
| LSI | section | 0 | 17344 |
| LSI | currier_lang | 2365 | 17344 |
| LSI | hand_scribe | 17344 | 17344 |
| LSI | currier_hand | 6420 | 17344 |
| LSI | line_index_in_paragraph | 17344 | 17344 |
| LSI | is_para_start | 17344 | 17344 |
| LSI | is_para_end | 3768 | 17344 |
| ZL | section | 0 | 5385 |
| ZL | currier_lang | 755 | 5385 |
| ZL | hand_scribe | 0 | 5385 |
| ZL | currier_hand | 2087 | 5385 |
| ZL | line_index_in_paragraph | 1329 | 5385 |
| ZL | is_para_start | 1329 | 5385 |
| ZL | is_para_end | 1255 | 5385 |

See DECISIONS.md for null/paragraph/hand/markup policies; SOURCES.md for byte hashes and provenance.

## What this does NOT show

No controls have been prepared and no generator, language, shorthand, cipher, entropy or semantic inference has been tested. No model has been trained. Intake counts and disagreement describe these files only; they do not identify how Voynich text was generated and do not constitute decipherment or translation.

The next stage is Phase 1 controls, then Phase 2 tokenization and Phase 3 paired measurements, with another mandatory stop.
