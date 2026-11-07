# Voynich v5: independent development source cut 2

The new development cut supplies every previously missing literal unit and supports all seven prior source-size failures. **This is development qualification. H3 remains unresolved; fresh-reserve transfer, H1–H8 scoring, model survival and full recovery remain unrun.** No claim `FREEZE.json` exists.

## Development material and scope

- **Latin:** Dante's *Monarchia*, all three books, 18,753 word slots in one work. This supplies length as 14th-century political prose; it does not qualify a long medical/herbal register.
- **Occitan:** *Jaufre*, Charmaine Lee's RIALC 2000/revised 2002 edition, all 10,974 numbered lines in order without gaps or duplicates, 66,728 word slots. There are 153 literal `ç` occurrences. This is Old Occitan narrative, a dialect/register sensitivity alongside the earlier Gascon legal sources.
- **Italian:** all 33 *Purgatorio* cantos and the complete 366-poem Petrarch *Canzoniere* collection. Whole collections were selected before acquisition, rather than individual gap-bearing poems. Purgatorio shares Dante and the larger *Commedia* with the old Inferno control; Petrarch provides an independent author/work check. **Independent-author coverage of `ä` remains absent:** Petrarch supplies `x` but no `ä`. This is a retained independence limitation, not a reason to rewrite the letter or promote reserve text.
- **Czech:** Oxford's diplomatic *Mastickar* Muzejni fragment, 2,220 slots and304 literal `w` occurrences. Editorially supplied or uncertain forms remain opaque barriers. Modern stage directions and the parallel transliterated column are excluded. This is an alphabet supplement, not a full-length generation source.
- **Real abbreviated Latin:** 15 previously unused CREMMA manuscripts, 93 admitted pages, 4,279 lines and 38,399 written-token slots. Every missing digit (`0,1,2,3,4,6,7,8`) and U+0301 is attested. All nine units are already present in the nine manuscripts dated through 1399; the six 15th-century supplements are separately tabulated. Medical-only new material does not supply those nine units. The new coverage therefore belongs to the declared cross-genre graphematic pool, not a medical-only claim.

| Italian development work | `ä` occurrences | `x` occurrences |
|---|---:|---:|
| Dante:Purgatorio | 1 | 2 |
| Petrarch:Canzoniere | 0 | 78 |

The two acute-mark instances are literal transcriptions at CCCC-MSS-236/3r (`f́ornice`,1200–1225) and LaurentianusPluteus39.34/3r (`sb́`,15th century). Neither their matching Unicode labels nor their attestation establishes matching functions or an abbreviation expansion. `KNOWN-GAP-EVIDENCE.json`, `LANGUAGE-GAP-EVIDENCE.json` and `ABBREVIATED-LATIN-STRATA.json` retain exact manuscript/page/line or work/unit/slot provenance.

## Seven original-slot budgets

| Source/cell | Required slots | New consecutive same-work run |
|---|---:|---:|
| Latin / A-1-F | 10,137 | 18,753 |
| Latin / A-1-H | 10,352 | 18,753 |
| Latin / B-2-H | 10,031 | 18,753 |
| Latin / B-3-F | 10,912 | 18,753 |
| Latin / B-3-H | 11,331 | 18,753 |
| Occitan / B-3-F | 10,912 | 66,728 |
| Occitan / B-3-H | 11,331 | 66,728 |

`source_cut2.load_cut2_development` constructs immutable, hash-checked development runs and delegates generation to the existing `source_contract.produce_from_development`. Missing sections and work boundaries cannot be bridged; reserve/calibration requests and inventory-only supplements are rejected for generation. Starts are sampled uniformly over eligible positions. No wrapping, padding, cross-work stitching or partition pooling is used. The old development pool remains separately identified for alphabet fitting; old calibration/reserves never enter the new fits. Every readable development token contributes once to its declared source pool; no reserve-dependent weighting is fitted.

## Qualification and fresh reserves

**60/60 development codebooks pass capacity checks** across six source pools and ten EVA inventories. **22/22 actual-geometry generation checks pass** for the entrypoints previously blocked by these shortages: five Latin cells × G1–G4 and two Occitan cells × G1. These checks establish executable support at the stated sizes; they are not source-transfer or model-discrimination results. The earlier200-trial mechanism qualification remains a separate, earlier-source result.

**50/50 engineering tests pass.** The JVM initially failed before G5 could start, first with its default heap and then with a256MB bound. A64MB process-scoped heap with serial GC passes; the unmodified published generator source remains pinned. Test receipts retain both failures and the final command. No system-wide Java setting changed.

Fresh reserves were assigned before their bodies were acquired: *De vulgari eloquentia*, *Paradiso*, *Podkoni a zak*, manuscript Latin16195, and the10-page *Flamenca* manuscript GT sample at pinned gatmuza commit. **48 files are archived and byte-hashed separately; zero reserve bodies were parsed, counted for coverage, fitted or scored.** Source identity/readability and transfer support remain future gates; byte sealing does not certify them. The Flamenca sample is a native-page control, not an asserted manuscript-sized source. Paradiso/Purgatorio/Inferno remain same-author/larger-work related; Latin manuscripts are not automatically independent underlying texts.

The live RIALTO/RIALC certificate was expired. Jaufre was acquired from Internet Archive replays of the original scholarly edition; certificate verification was never disabled. Source URLs and hashes are in `JAUFRE-PROVENANCE.json`. CREMMA/gatmuza source attribution and CC-BY4.0 terms are retained; Wikisource attribution/declared licenses are retained. No open redistribution license was established for the RIALC electronic edition or Oxford teaching text: internal research only, not a public-source bundle.

## Preserved controls and remaining gates

The prior503-file delivery was verified byte-for-byte and its report, status, protocol and manifest preserved in `previous-cut/`. Its failed transfers remain failed controls. The initial cut2 section-only qualification is retained under `development-history/initial-section-control/`. New development attestation does not retroactively turn an exposed old reserve into a fresh test.

This cut has not been adopted into claim priors or the full recovery schedule. The existing recovery protocol and all held-statistic locks remain in force. H3 has no replacement estimator. Before claim execution, finish the unresolved definitions and freeze the source/register scope, mappings, priors, layout/runtime settings and reserve-access protocol.

Reproduce local checks with `python system-types-v5/source_cut2.py`, `python system-types-v5/qualify_source_cut2.py`, `python system-types-v5/check_source_cut2.py`, then `python system-types-v5/prepare.py`. Acquisition scripts are separate and are not needed to rerun these checks. Fresh reserve files remain outside every development loader.
