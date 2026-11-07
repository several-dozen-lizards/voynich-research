# Phase 9b — design registered; source census incomplete

2026-10-27. **No Phase 9b calibration or annotation fit has run.** Native tracks remain CLOSED. The user approved a bounded, cited source census, with coverage limits reported. This is a progress receipt, not a completed variant freeze or a negative language-identification result.

## What is registered

[DESIGN_REGISTRATION.json](DESIGN_REGISTRATION.json) fixes [PROTOCOL.md](PROTOCOL.md) and [EQUIVALENCES.json](EQUIVALENCES.json) before variant collation, synthetic generation or scoring. Initial bibliography searches and inspection of Phase 9 source/code files preceded registration. Existing target readings and the user-supplied Phase 9 outcome were already known; sealing here concerns new target fitting, not investigator blinding.

The primary objective is DISTINCT months, with repeated April and repeated May each contributing at most one. Panel count is a separately optimized secondary statistic. The registered M1/M2 search, five-language maximum, Occitan-minus-Catalan contrast, 999 common panel shuffles, nine-month training for LOMO, and 100 per-month budget-equalization draws remain unrun. French is separate. Ties are unresolved rather than assigned to whichever language appears first.

The finite M2 spelling transducer is specified before scoring: original spans are consumed once and generated output is not recursively expanded. This makes the overlapping medieval spelling classes a finite operational search. It does not assert historical interchangeability of every generated spelling. Generated alternatives will remain distinguishable from attested variants.

Calibration is registered for five languages × eight encoding settings × fifty positive replicates, with corresponding wrong-pair negatives and the prior ZL disagreement-derived noise model. The fifty-replicate cell gates are ≥40 uniquely correct-language winners and ≤2 negative rejections. Missing source coverage is NOT a failed confusion test. No statement that ten month names cannot distinguish Occitan and Catalan is warranted yet.

## Current source accounting

[CANDIDATES.json](CANDIDATES.json) / [CANDIDATES.csv](CANDIDATES.csv) contain 128 candidate/provenance records, each with month, form, language, date, region/variety status, citation, evidence kind and admission limitation. [COUNTS.json](COUNTS.json) gives per-month counts. The following are **date-supported forms in the current audit**, not a final admitted scoring lexicon:

| Language | Distinct normalized dated forms | Months covered | Missing months / main limits |
|---|---:|---:|---|
| Latin | 10 | 10/10 | One Rennes-use calendar; not regional Latin coverage |
| Italian | 10 | 10/10 | One 1495 printed witness; no broad Italian dialect census |
| German | 10 | 10/10 | Printed 1474 Nuremberg headings; older candidate quotations remain under review |
| Occitan | 19 | 10/10 | Dated Auvergnat evidence; other regional witness leads unverified |
| Catalan | 8 | 6/10 | March, April, August, November lack a qualified dated spelling witness; most dated quotations also lack localized regional provenance |
| French, secondary | 0 | 0/10 | Twenty transcribed candidate records, but underlying period witness identities not independently verified |

Latin/Italian forms come from preserved Phase 9 source collations: [Brandeis/Rennes catalogue](https://www.manuscripts.org.uk/chd.dk/gui/Brandeis_gui.html), c1420–1430, and [Crescentio, Venice 1495](https://archive.org/details/pierocrescentiod00cres), Book XII month headings. Their prior evidence files remain in place. Neither source is treated as a complete language lexicon.

German headings were newly read against the [BSB Regiomontanus calendar](https://www.digitale-sammlungen.de/en/view/bsb00031080), dated 1474 by the library's saved IIIF metadata. Ten scans and the heading contact sheet are retained. Later handwritten marginal glosses are excluded from the printed witness set. Raw OCR of all sixty printed pages is retained as retrieval material, not automatically admitted as spelling evidence.

The [publisher's preview of Philippe Olivier's 2009 dictionary](https://api.pageplace.de/preview/DT0400.9783484971325_A16036970/preview-9783484971325_A16036970.pdf), printed pp6–7, supplies explicitly dated Auvergnat quotations. The month forms were read against the rendered pages. It documents five April spellings and month-bearing sequences from 1430 and 1459; edited quotation spellings are distinguished from normalized dictionary headwords. The 1459 sequence concerns calends/weather prognostics, using the month names metonymically. The cited medieval account books themselves were not re-collated. The dictionary's source apparatus localizes the latter witness to Auteroche/Couzans at Vebret.

The [DCVB July entry](https://dcvb.iec.cat/results.asp?word=juliol) supplies a Barcelona documentary form from 1358. Other exact dated examples appear in [maig](https://dcvb.iec.cat/results.asp?word=maig), [comptar](https://dcvb.iec.cat/results.asp?word=comptar), [desembre](https://dcvb.iec.cat/results.asp?word=desembre), [mes](https://dcvb.iec.cat/results.asp?word=mes) and [verema](https://dcvb.iec.cat/results.asp?word=verema). Present-day dialect pronunciations, undated lemmas, and quotations from earlier compositions without a verified in-window spelling witness remain outside scoring admission. Normalization collapses Juny/iuny into one candidate spelling, so nine dated Catalan records produce eight distinct normalized forms.

## Why calibration is still sealed

The approved bounded frame is specified in [SOURCE_FRAME.json](SOURCE_FRAME.json). Its collation is unfinished, including the four Catalan month gaps, incomplete regional provenance and the French secondary witnesses. Dropping those month identities, inserting modern Catalan forms, or silently carrying forward undated Phase 9 lemmas would change the requested experiment.

A cited 1513 Catalan almanac is a promising route: [the digital-table bibliography](https://locomat.loria.fr/locomat/digital-tables.html) links to [Google Books xF1r6kS4WjcC](https://books.google.com/books?id=xF1r6kS4WjcC); [Sciència.cat](https://www.sciencia.cat/db/textos.htm?obra=2954) documents the work's editions. The saved public search response contains April/March OCR hits, but the requested page scan returned an explicit unavailable-image placeholder. Those snippets were not repaired into admitted spellings. Additional Catalan witnesses identified in the search are leads, not collated replacements.

For French, the [BnF identifies a Paris 1493 calendar](https://www.bnf.fr/fr/mediatheque/le-kalendrier-des-bergiers), but the manifest request was blocked by Cloudflare. The [month-name discussion](https://www.voynich.ninja/printthread.php?page=14&tid=4751) gives transcriptions attributed to Bourges 1375, Metz 1457 and a Provençal almanac, but the public rendering masks their source links. These candidate lists cannot stand in for independently identified period witnesses.

An initial automatic approval review of the read-only BnF manifest download timed out; the permitted retry was approved and then blocked by the remote site. This was not a policy finding that the historical-source download was unsafe. Other retrieval failures and successes are retained, including certificate-chain errors without disabling validation, LOC HTTP 403, and the unavailable Google scan.

[SOURCE_AUDIT_SNAPSHOT.json](SOURCE_AUDIT_SNAPSHOT.json) hashes the current candidates, source material and design receipts. It deliberately says INCOMPLETE and does not admit calibration. A later completed source freeze must preserve this snapshot and all unresolved candidates. No scorer, synthetic bank, null fit, target fit, LOMO prediction or equalization result is represented as completed.

## Relation to Phase 9 and published proposals

The user-supplied Phase 9 prior was one frozen form per month/language, with an Occitan positional panel fit of 5/12 and p=.01 per bank. Phase 9b is designed to extend that comparison with period variation, Catalan and distinct-month counting, and to test mapping generalization. It has not yet replicated or contradicted the prior result. The old result must not be treated as a 9b language winner.

Published positions to distinguish in any eventual result include:

- [Nick Pelling (2009)](https://ciphermysteries.com/2009/08/22/jaume-deydiers-livre-de-raison) argues for an Occitan direction and discusses Stolfi's earlier searches, while documenting uncertainty over the historical Toulon source.
- [Thomas Sauvaget (2012)](https://voynichanalysis.wordpress.com/2012/03/25/about-month-names/) argues for northern French variants and differs over individual annotation readings. These are arguments and readings, not a frozen five-language test.
- [Stephen Bax (2014)](https://stephenbax.net/?p=1226) discusses French/Picard comparisons and quotes David King's caution about regional assignment. King's work is represented here through Bax's attribution, not as independently inspected direct evidence.
- [Bowern and Lindemann's linguistic review](https://alumniacademy.yale.edu/sites/default/files/2021-07/The%20Linguistics%20of%20the%20Voynich%20Manuscript.pdf) uses an Occitan designation for the month annotations. That terminology is not itself evidence that Occitan wins against period Catalan variants.
- [The 2025–2026 month-name collection](https://www.voynich.ninja/archive/index.php/thread-4751.html), including the [February 2026 discussion](https://www.voynich.ninja/printthread.php?page=14&tid=4751), includes both southern and northern French comparisons. Its evolving ratings/collections are source leads, not the 9b calibration.

## Preservation and current boundary

The prior experiment's 1,381-file SHA-256 baseline is recorded separately. Verification compares every baseline file and reports additions, changes or missing files rather than assuming preservation. The current audit makes no language claim. Winner, contrast p, mappings, top nulls, LOMO and budget-equalization frequencies are explicitly unavailable because the source freeze and calibration are unfinished. Native-script inference remains prohibited regardless of how the later annotation test eventually behaves.
