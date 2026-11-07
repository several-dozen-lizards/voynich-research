# RD-FO3 calibration follow-up

| Chain | Status | L_min |
|---|---|---:|
| F/G5_published/word | FAIL_DIRECTION | — |
| F/G5_published/glyph | FAIL_DIRECTION | — |
| F/G6/word | FAIL_DIRECTION | — |
| F/G6/glyph | FAIL_DIRECTION | — |
| O/ZL/p1_glyph_directed | PASS | — |
| O/Latin/p1_glyph_directed | FAIL_ORIGIN | — |

| System | Whole-word L_min | Junction-feature L_min |
|---|---:|---:|
| Latin | 6 | 41 |
| G2 | 11 | 41 |
| G3 | 11 | 41 |
| G4 | 21 | FAIL |
| Naibbe | FAIL | FAIL |
| ZL | FAIL | 6 |
| G5_published (new) | FAIL | FAIL |
| G6 (new) | FAIL | FAIL |

| Origin corpus | Words | n | Junction-directed hit | Chance | Excess95%CI | Gate |
|---|---|---:|---:|---:|---|---|
| ZL | 21–40 | 98 | 50.0% | 16.9% | 0.218–0.436 | True |
| ZL | 41–80 | 36 | 44.4% | 9.7% | 0.185–0.479 | False |
| Latin | 21–40 | 177 | 16.4% | 16.6% | -0.058–0.066 | False |
| Latin | 41–80 | 85 | 14.1% | 9.7% | -0.017–0.109 | False |

Full direction curves, support, ties and shuffle nulls are in each chain report/bin table. S-p1 isolated and paired word-directed diagnostics are descriptive; the new primary gate uses junction-inferred orientation, including its own inferred-orientation shuffled null.

G5 is the pinned published Java implementation, not the v5 surrogate. Published Voynich-inspired rules and initialization are retained; the literal first seed line is excluded but influences descendants. G6 is a fixed simplified table/grille implementation. Neither result identifies a historical mechanism; one realization is not a generator-class rejection.

These are new registered calibration runs motivated by earlier outcomes. Old gates/results are unchanged. Paragraph-to-ring transfer remains untested. Latin origin has artificial source layout. Real-ring scores, radial text, visual comparisons and corrected orders remain closed.
