# Native source collation supplement

The source work has advanced to **60 degree entries in native-image first passes**: all thirty Aries entries and all thirty Taurus entries. Each is compared separately with the 1881 transcription and the modernized locator. The thirty-name Greek wrong-unit roster is complete in the checked native-script editions, with the apparatus and manuscript dates recorded. This supplement is not a completed all-witness collation or an admitted C3 source/model freeze.

The old C1/C2/v7.3/preparation freezes, budget and C3 placeholder are preserved. This work reads historical sources only. No Voynich payload, registration decision, new C2 look, alignment fit or reserved material was opened. C2 remains six of ten looks. The vault remains closed and execution unauthorized.

## Lapidary: actual source support

The owning library dates the surviving Escorial h-I-15 manuscript copy to about 1270–1275. The 1881 edition reproduces the manuscript and supplies a non-paleographic transcription. Those are two representations of one witness; the modernized text is another representation, not a third medieval witness. [Owning library catalogue](https://rbdigital.realbiblioteca.es/s/rbme-expo/item/13127), [CSIC edition catalogue](https://simurg.csic.es/view/CSIC000472601/lapidario-del-rey-d-alfonso-x-codice-original).

`ARIES-SPELLING-COLLATION.json` and `TAURUS-SPELLING-COLLATION.json` retain native excerpts, folio/column/image references, printed heading readings and modernized readings. The TSV files provide compact review tables. These are lowercase name/descriptor excerpts, with regularized spacing and long-s represented as s; they are not complete diplomatic transcripts. A descriptor such as a stone that attracts something is kept as a descriptor. Neither a modern mineral identification nor a theophoric analysis has been inferred.

There are **six uncertain native Aries readings** (degrees 1, 5, 20, 21, 23, 26) and **eight uncertain native Taurus readings** (5, 6, 9, 10, 13, 17, 18, 28). Taurus degree 8 also retains uncertainty in the printed heading. They stay unresolved rather than becoming extra selectable spellings. These are single-reviewer first passes, with no independent paleographic certification. All aliases in the running text have not yet been exhaustively collated.

The heading excerpts differ between the 1881 and modernized layers in 12 Aries positions and 16 Taurus positions. These counts include modernization, word choice and descriptor changes; they are not counts of independent medieval variants or transcription-error estimates. Examples requiring preservation rather than reconciliation include Aries Ceritiz/centiz, Tuminon/cuminon and Bedunaz/berlimaz; Taurus Albarquiz/abarquid, Raconic/raconie and Alambari/ámbar. Native readings are an additional layer, sometimes uncertain. A convenient spelling is never selected by alignment.

Rubric and body differences are also retained: Taurus degree 10 has printed heading Zamorat with body Zamoricaz; degree 17 has heading Zavarger with body Zavarpet; degree 28 has heading Iotarican with body Lotarican. These do not become arbitrarily interchangeable profile entries. Aries degree 28's printed folio locator disagrees with the native image position; the actual rubric is at the foot of f9v column a, with the body continuing in b. The image reference is preserved rather than silently inheriting the printed locator.

## The degree-block gaps are now explicit

The modernized contents contain **301 entries**, distributed as follows. The inventory is a locator count, not a certification of 301 proper names or full native degree collation.

| Block | Entries represented in the locator | Degree positions left unrepresented |
| --- | ---: | --- |
| Aries, Taurus, Gemini, Cancer, Virgo, Libra, Scorpio, Sagittarius, Capricorn | 30 each | None inferred from the contents count; individual native checks still required outside Aries/Taurus |
| Leo | 1 | 1–29 |
| Aquarius | 28 | 29–30 |
| Pisces | 2 | 1–28 |

`LAPIDARY-360-SLOT-AUDIT.json` retains all 360 sign/degree positions with **59 unrepresented slots**, never a compressed 301-position list or a repaired 360-name profile. It distinguishes contents-order candidates from directly checked degree formulas. The sparse transitions were checked visually in native f40r (Leo30), f91v (Aquarius27/28) and f92r (Pisces29/30), and in the 1881 transcription at PDF328/360, printed26/58. `GAP-AND-SPARSE-BLOCK-REVIEWS.json` records the evidence and tentative Pisces name readings.

This is the distribution in the collated sources. It does not establish the cause or date of a physical loss. Later-treatise cross-references to otherwise absent degree entries are not used to fill these blocks. The modernized text's generalized statements about thirty stones per sign cannot replace surviving entries.

## Thirty-name wrong-unit control

`WRONG-UNIT-GREEK-COLLATION.json` preserves the Greek roster in source enumeration order. It is a political roster, a different-unit negative control candidate. It is not a chronological sequence of appointments or an astral reference list. There is no truncation, cycling, padding or reordering to reach thirty.

The complete roster spans **II.3.2–3 in the Marchant/Perseus digital edition**: the first 26 names are in section2 and the last four in section3. In Hatzfeld's 1936 edition the whole roster is under II.3.2, across printed82–83 (PDF133/135). All thirty native-script edition readings were compared visually. The section-boundary difference is recorded rather than used to omit four names. [Perseus native-text source](https://github.com/PerseusDL/canonical-greekLit/blob/master/data/tlg0032/tlg001/tlg0032.tlg001.perseus-grc2.xml), [Hatzfeld digitized edition](https://fr.wikisource.org/wiki/Livre:X%C3%A9nophon_-_Hell%C3%A9niques,_Les_Belles_Lettres,_tome_I.pdf).

Hatzfeld's manuscript notice and sigla (PDF19/28) date **B, Parisinus1738, to the early fourteenth century**, and **M, AmbrosianusA4 inf., to 1344**. His stated apparatus convention records rejected readings for the four principal manuscripts. The supplement therefore provides complete B/M name profiles **as editor-reported witness support**, with no B/M rejected name reading indicated at this passage. It does not certify manuscript-specific accents, exact diplomatic spelling, or direct image collation. The catalogue route to B's digitization could not be retrieved here; the failed request is preserved. No unsupported manuscript folio number was invented.

The apparatus records two later-witness alternatives. At roster position1 it reports `πολυαρχης` for C (Parisinus2080, mid-fifteenth century); at position22 it prints the abbreviated `θεαγ.` for V (Marcianus368, mid-fifteenth century). Both are retained as **excluded from pre-1440 variants**. The abbreviation has not been expanded into an invented full attested spelling. Riemann's older claim that all four witnesses are fourteenth-century is not used to override the later edition's more specific dates for C/V.

Riemann's 1878 collation page137 has no separate name variant entry for II.3.2/3. That is agreement against **Sauppe1866**, not an independent demonstration that each manuscript agrees exactly with Marchant or Hatzfeld. His warning that recurrent orthographic differences can be recorded only once elsewhere also prevents an exhaustive-variants claim. The primary page image and text are saved; its PDF request returned403, which is recorded rather than omitted. [Riemann primary collation](https://www.persee.fr/doc/bch_0007-4217_1878_num_2_1_4446).

A fixed Greek-to-ASCII working transformation is supplied for reproducibility and clearly labeled **derived, not attested Latin spelling and not adopted for scoring**. Modern English renderings are not counted as medieval spelling variants. No phonetic key or mapping to Voynich is attached. The two B/M reported profiles are identical in these name readings and must not be counted as independent successful controls.

## Remaining work and release status

The next native block is Gemini, followed by the other complete degree blocks. The fourteen uncertain Aries/Taurus readings need paleographic adjudication; aliases and rubric/body differences need exhaustive review. The Greek control still needs direct manuscript-image confirmation and independent review. The morphology-matched fake-list null remains necessary even when a thirty-person control is available.

No new source profile has entered the frozen scoring universe. No best spelling, source or arm was selected by a Voynich result. Historical data, raw acquisition receipts, failed requests, rendered page checks and every uncertainty are retained in this new directory. `VERIFICATION.json` verifies preparation integrity and preservation only; it is not C3 scientific qualification.
