# Frozen maps on unused annotation loci

**No complete multi-letter word was recovered under either saved map.** This establishes limited alphabet coverage on the admitted readings; it is not evidence that the month relationship is false, nor a valid negative test of every annotation convention. Translation accuracy is NOT ESTIMABLE without independently established plaintext answers.

The check used 19 ledger entries representing 18 distinct annotation locations on 12 folios. Two entries contain competing scholarly readings of the SAME f66r location. There are 24 reading-alternative rows per map, including single letters, and 28 whitespace-delimited token occurrences per map when alternatives are counted. These counts are accounting, not independent sample sizes. Every locus is outside the twelve month-fit folios. Sources were previously available to the research; these are unused fit loci, not pristine blind data.

## Application

The saved Occitan monoalphabetic and beginning/interior/end maps were copied exactly from the old OBSERVED.json. Both encode candidate letter to annotation letter, so each injective class was inverted for this check. No assignments were added. Unknown letters remain ?. Annotation normalization retains cipher-side j/k/w rather than applying plaintext spelling replacements. Position is computed within each published whitespace-delimited token, with beginning precedence for singleton marks. Spatially separated marks were not joined. This boundary assumption was declared before application; handwriting boundaries were not newly adjudicated.

PROTOCOL.md and the input/code/map hashes were sealed in REGISTRATION.json before application. No fitter, native text corpus, dictionary or language model was imported or called. The code applies only the two selected old partial witnesses; it does not search other equally optimal witnesses.

## Word-bearing readings

| Folio | Published reading | Frozen mono inverse | Frozen positional inverse |
|---|---|---|---|
| f2v | fo | ?? | ?? |
| f2v | fa (alternative) | ?a | ?? |
| f4r | rot | r?t | ?ut |
| f7r | rot (tentative) | r?t | ?ut |
| f9v | por (tentative) | ??r | ?u? |
| f66r | der Mussdel | ??r mgss??? | ??? mgss??? |
| f66r | Musmel (alternative) | mgsm?? | mgs??? |
| f66r | der mvs del (another author's reading) | ??r m?s ??? | ??? m?s ??? |
| f116v | pox leber | ??? ????r | ?u? ????? |

Only single letters were completely covered: seven token occurrences including reading alternatives under mono, one under position. Examples are annotation g to candidate o under mono, r to r under mono, and J to i under positional beginning. These are mechanical substitutions, not identified meanings or validated initials. No gloss was used to complete a word or score correctness.

| Saved map | Fully covered multi-letter tokens | Fully covered single-letter occurrences | Partial token occurrences | Entirely unknown token occurrences |
|---|---:|---:|---:|---:|
| Mono | 0 | 7 | 10 | 11 |
| Positional | 0 | 1 | 7 | 20 |

Full location/readings/outputs and letter counts are in RESULTS.csv and RESULTS.json. INPUT.json retains source locators, alternatives and uncertainty notes. Do not turn these alternative-inclusive token counts into accuracy rates.

## Sources and coverage limits

- [Zandbergen's writing-system overview](https://www.voynich.nu/writing.html), additional-writing table, COL/LET rows f1v, f2v, f4r, f7r, f9v, f20r, f29r, f32r, f39v, f99v; f66r mixed-writing discussion. Every explicitly transcribed Latin-letter COL/LET reading in this bounded table was admitted; unreadable marks were not invented. Many readings and the colour-note interpretation are tentative. The f32r first mark may have an unspecified following character: the observed fragment was kept without filling it.
- [Philip Neal's marginalia discussion](https://philipneal.net/voynichsources/marginalia/), f66r and f116v headings. Readings were available in the web search extract; direct-page retrieval timed out twice. The two short fragments are attributed source readings, not fresh facsimile transcription. f116v's remaining text and native-script words were not processed.

No source establishes that these notes use the month annotator's hand, language or code. No source gold plaintext was supplied to fitting, and no modern gloss was substituted as an Occitan crib. No palaeographic arbitration was attempted. Multi-letter outputs were not judged by resemblance to plausible words.

Excluded: the used month loci, modern pencil foliation, numeric/quire marks, ownership inscription, unspecified alphabets, unreadable scribbles and f17r's insufficiently specified Latin-letter reading in these bounded sources. ALL native-script portions were excluded, including those on mixed-script pages. This is not an exhaustive search of all possible marginalia readings in the literature.

## Verification and preservation

122 character applications were independently checked by scanning the saved FORWARD mapping assignments, rather than reusing the decoding inverse lookup. All checks passed. The sealed inputs, code and maps remain unchanged. All 3,191 pre-existing files checked across the month-annotation and Phase 8 runs remain byte-identical.

No new fits, key completions, shuffles, model selection, semantic ratings or native-script scoring. Native tracks remain CLOSED. Phase 8 remains FAIL. The original mutable-state registration receipt defect remains STRICT_FULL_MANIFEST_CHECK_FAIL_MUTABLE_STATE_ONLY. Nothing was rewritten to hide or repair it.

**Result: no demonstrated word-level transfer in this bounded application. The frozen maps produce partial strings; they do not yet supply additional translations.**
