# Voynich research archive

Research notes, experiments, code, checks, controls, findings, failures, and source records from the Voynich workspace, collected on 7 November 2026. This archive does not establish a decipherment, translation, language identification, or historical mechanism.

## Plain-English summary

The strongest findings so far concern **patterns in the writing**: where particular written forms occur, which forms tend to follow one another, and how those observations change with the transcription, page layout, and comparison method. The manuscript's language, meanings, and underlying writing system remain unresolved.

The Roman-letter strings in these reports, such as `sh`, `qok`, and `daiin`, are labels for transcribed manuscript signs. They are not established pronunciations or translated words. Different transcribers sometimes divide or identify those signs differently, so we keep their readings separate.

### What have we tested?

- **Distribution and word order.** We counted written forms and word parts across sections, writers, and positions, then checked whether selected differences survived fairer comparisons. We also tested repeated pairs, frames, and ordering patterns against shuffled versions of the same material.
- **Whether our methods can find a known answer.** Before applying many proposed tests to Voynich, we tried readable historical text, deliberately encoded text, planted patterns, and misleading lookalikes. These checks ask whether a method can detect its intended signal without being fooled by layout, frequency, or missing data.
- **Pictures, labels, names, and historical tables.** We inspected proposed plant and zodiac identifications, checked period name forms and source chains, prepared independent image annotations, and tested a specific degree-table alignment proposal.
- **Decoders and predictive models.** We tried restricted letter-, sign-group-, and written-syllable mappings, examined published approaches, and trained small models to compare text structure. Later studies tested segmentation, writing-convention comparisons, direction, and source fidelity.
- **The research record itself.** We audited what had already been seen, which material was genuinely protected, whether registration happened on time, and whether source conversions meant what the code assumed.

### What have we found?

| Area | What the evidence supports | What it leaves open |
|---|---|---|
| [Section and word-part patterns](guides/studies/word-parts-v50.md) | Several differences survive matching for recorded writer, format, and position. Some also retain their direction across retrospective page splits and removal of frequent words. | A form associated with bath or herbal pages is not thereby a word for water, a plant, or a grammatical category. |
| [The sh/ch–qok studies](guides/studies/sh-qok-retrospective-readjudication-v1.md) | Several specified retrospective comparisons support a local next-word association in both main readings. Later controls clarified availability effects, support limits, and earlier certification failures. | The association's cause is unsettled. Contextual spelling, local transitions, phrases, and other mechanisms can imitate an apparently grammar-like pattern. |
| [Phrases and contextual roles](guides/studies/phrase-transfer-v62.md) | We built inspectable phrase tests and role diagnostics, found specific scoring bugs, and measured tradeoffs between making more decisions and being confidently wrong. | The recorded results do not provide a generally qualified semantic reader. Some tests missed known positives or lacked usable support; several manuscript phrase findings did not survive both readings and the full correction. |
| [Plants and zodiac imagery](guides/studies/zodiac-clothing-continuation-v106.md) | Source and image audits corrected several attractive but insecure leads. Correcting the clothing annotations made the specified degree-table comparison estimable; that comparison then did not pass. | Plant identities, label ownership, and the link from a pictured object to a particular written name remain uncertain. Some other visual features could not be tested at all. |
| [Models, encodings, and units](guides/studies/voynich-lab.md) | The lab produced reproducible measurements, controlled encodings, and small predictive models. Some narrow calibration tasks passed; other recovery, alignment, and unit-finding methods failed or remained incomplete. | Similarity on a few measurements does not identify a historical mechanism. Short-budget models are not convergence-qualified, and no tested decoder established a translation. |
| [Direction and source checks](guides/studies/voynich-lab--results--ringdir--followup_v3.md) | Some paragraph-derived direction and origin calibrations passed within their stated bins. Later adapter checks also caught a mistaken interpretation of layout markers, followed by unresolved source-conversion differences. | Paragraph calibration has not established transfer to real rings. Real-ring scoring and spacing interpretation remain closed in the archived receipts. |

These are not all one kind of “pass.” A program can reproduce its arithmetic while its source interpretation is wrong. A test can work on a planted pattern while the manuscript supplies too few comparable cases. The later [adapter and source checks](LATEST.md) are a concrete example of why those distinctions matter.

### What is still unresolved?

We do not have an established language identification, sound system, dictionary, or translation. We have not uniquely separated grammatical relationships from contextual spelling, phrase templates, layout, or a particular encoding mechanism. Several promising comparisons still need reliable independent annotations, better source evidence, adequate support, or a method that first succeeds on the right known-answer controls.

Much of the text had already entered earlier searches. A new split or a freshly frozen script does not make those pages historically unseen. The archive therefore labels retrospective checks, control-only successes, unrun stages, and insufficient-data results explicitly.

**For the folder-by-folder explanation, use [the plain-English guide index](GUIDES.md).** It covers every one of the 145 study folders and 45 major nested studies, with the question, finding, unresolved issues, contents, and links to the owning evidence. Repeated trial directories are explained by their parent study. [A short glossary](GLOSSARY.md) explains the technical labels used in the original reports.

## Start here

- [Plain-English folder guides](GUIDES.md)
- [Latest recorded work and limits](LATEST.md)
- [All 145 study folders](STUDIES.md)
- [Browse by research theme](MAP.md)
- [Findings and owning reports](FINDINGS.md)
- [Checks, controls and verification](CHECKS.md)
- [Sources and provenance](SOURCES.md)
- [Chronology and ownership](CHRONOLOGY.md)
- [Coverage, omissions and publication policy](COVERAGE.md)
- [Reproduction and verification](REPRODUCING.md)
- [Archive integrity receipt](catalog/EXPORT-VERIFICATION.json)
- [Machine-readable file ledger](catalog/FILES.csv)

## What this collection contains

The snapshot inventories 108,043 files across the in-scope workspace. It copies 91,167 publishable files into `research/`, preserving original paths and content. Each file is accounted for in the ledger; exclusions are visible, not silently discarded. Large text artifacts are losslessly compressed with gzip, or XZ for the largest table. Original and published checksums are recorded separately.

Reports retain unsuccessful controls, bugs and repairs, insufficient support, resource failures, negative findings and inconclusive results. A result is qualified only for the task and controls its owning protocol actually tested. Source/synthetic-control success does not itself open manuscript scoring, and structural correspondences do not establish semantics.

The small EVA continuation model is published separately at [voynich-experimental](https://github.com/several-dozen-lizards/voynich-experimental). It generates EVA text; it has no established translation ability. Model checkpoint copies are indexed here rather than duplicated.

## Scope

Voynich only. Indus work and the unrelated JNAIQ checkout are outside this snapshot. The archive gathers records present in this workspace; it does not claim to contain every past chat, external attachment, unretained experiment or earlier file version. See [coverage](COVERAGE.md) for the exact boundary.

Third-party corpora, raw manuscript transcriptions, imported source/media files, private/blinded packets and nested archives needing review remain indexed locally rather than being redistributed by default. See [rights and attribution](RIGHTS.md). No experiment was rerun and no closed research gate was reopened to create this archive.
