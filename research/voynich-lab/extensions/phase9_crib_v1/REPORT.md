# Phase 9 source-feasibility audit

**The source audit is frozen; scoring is NOT registered and calibration has NOT run. Voynich native text and target scoring remain CLOSED. Phase 8 remains FAIL.**

This is a partial deliverable toward the requested experiment, not a completed label–illustration test, a synthetic qualification result or a translation claim. The source-stage check exposes missing prerequisites before any scoring.

## What is assembled

- All 129 herbal rows in the published pre-1960 identification compilation: 112 nonempty proposal/note rows, 111 with an identifiable candidate string. Empty and illegible-only rows remain visible.
- Twelve zodiac panels with ten distinct month identities (March–December), exact published annotation readings and abbreviation notation retained. Both user-requested approaches are represented separately: later Latin-script annotations and native-script month cribs.
- A 25-row historical name-evidence ledger: Latin 7, Italian 1, German 4, Occitan 13. These include month forms, generic plant terms, incompatible-species leads and edited/OCR evidence. They are not 25 qualified label-name pairs.
- Six previously audited botanical proposals are preserved separately, including decipherment-associated identification chains and contradictory proposals. No independent botanical consensus is inferred.
- Every herbal/zodiac inventory row has an explicit four-language coverage record. Missing evidence remains missing; modern translations and taxonomic binomials were not substituted for period spellings.

## Why registration and calibration have not started

| Track | Available evidence | Unmet prerequisite |
|---|---|---|
| Native herbal labels | Published tentative folio-level plant proposals | No independently established plant-name label locus in this inventory; incomplete dated four-language name coverage |
| Native zodiac months | Published zodiac sign/month associations | No established native-script month-name locus; a central-star/figure label is not automatically a month label |
| Later month annotations | Twelve published Latin-script annotation readings with illustration positions | Complete period-name candidate sets across all four languages and explicit abbreviation handling are unfinished |

The user requires cited candidate names before scoring and calibration before native target access. Inventing missing historical forms or converting folio identifications into assumed word labels would change the experiment. No such substitutions were made. Source absence in this audit is not proof that an appropriate attestation or label exists nowhere else.

The old label-objects-v6 gate and unaccepted geometry were not reused as qualified observations. The blocker here is the current Phase 9 source/crib support, not a claim that Phase 8 or the earlier method failure forbids a new method.

## Identification and historical-name cautions

- All pre-1960 identifications are explicitly tentative. Petersen, Holm/O’Neill attributions and Ethel Voynich compilations can share an evidential chain; columns are not independent votes. Source disagreements, question marks and illegibility are retained.
- The pre-1960 table reports hemp/aconite candidates for f16r, whereas the inherited Bax proposal uses juniper; f41v has fern/carrot/tansy alternatives while the inherited decipherment proposal uses coriander. These are unresolved alternatives, not corrections.
- Historical Centauria is not automatically modern Centaurea. Juniper berries are not an established species-level match to Juniperus oxycedrus. Violet/pansy distinctions and the ambiguous Iacea name remain conditional.
- The Latin headings come from an edited Irish medical witness associated with 1415; the 1485 Gart readings have explicit expansion/orthographic caveats. Levy is a 1909 historical lexicon with raw OCR, not a diplomatic medieval witness. The Italian coriander lead is a dated quotation in the CNR historical dictionary. Do not claim all these forms are equally secure or represent one region/time.
- Later zodiac annotations are a different script/hand layer; their Romance language is disputed. The annotation track is not native Voynich decipherment. Repeated Aries/April and Taurus/May panels are not independent identities.

## Requested method retained in the draft

PROTOCOL_DRAFT.md preserves the three requested encoding families, a global consistent mapping per model/track, identical maximization for observed and within-section shuffled assignments, separate annotation/native tracks, solver-certification requirements, identifiable-mapping recovery, wrong-pair calibration, and separation of source failures, search failures and method failures. It is explicitly not a complete executable or frozen scoring registration. Numeric gates and all remaining model freedoms must be finalized before outcomes, not inferred from a pilot.

No synthetic corpus was generated or scored. No label-name map, null score, p-value or real target result was fitted. There is no REGISTRATION.json or QUALIFICATION.json for Phase 9; SOURCE_FREEZE.json seals only this audit version.

## Files and citations

- HERBAL_IDENTIFICATIONS.json: full bounded published herbal table with source cells and contested/ownership status.
- SUPPLEMENTAL_PROPOSALS.json: inherited source-associated hypotheses with their original caveats.
- ZODIAC_MONTHS.json: separate annotation and native-month eligibility records.
- CANDIDATE_NAME_EVIDENCE.json and LANGUAGE_COVERAGE.json: historical forms, exact locators, evidence type and unfilled language cells.
- SOURCES.json and sources/: source URLs, saved web-tool extracts and the retrieved raw public-domain Levy OCR; network failures retained separately.
- SOURCE_GATE.json / RUN_STATE.json: source-stage incompleteness and closed target state.

Main source URLs: [Zandbergen, tentative herb identifications](https://www.voynich.nu/extra/herb_oldid.html); [Zandbergen, writing system and month annotations](https://www.voynich.nu/writing.html); [CELT Irish Materia Medica](https://celt.ucc.ie/document/G600005/); [Levy 1909 historical lexicon](https://archive.org/stream/petitdictionnair00levyuoft/petitdictionnair00levyuoft_djvu.txt); [TLIO dated coriander quotation](https://iris.cnr.it/retrieve/370f071c-7c17-4964-bff3-5e2d3772d8f6/prod_146433-doc_37011.pdf); [Gart 1485, chapter 310](https://daten.digitale-sammlungen.de/bsb00032739/image_498) and [chapter 432](https://daten.digitale-sammlungen.de/bsb00032739/image_674).

Preservation: all previously existing Phase 8 files, including its audit addendum and FAIL receipts, are hashed and unchanged. Original plant/astrology source-audit files and old label-object status/qualification are also unchanged. No earlier analysis, gate or registration was modified.
