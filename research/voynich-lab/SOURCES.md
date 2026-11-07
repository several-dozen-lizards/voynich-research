# Sources

Downloaded 2026-10-26; raw bytes preserved unchanged. No cloud models or training.

- [LSI_ivtff_0d.txt](https://www.voynich.nu/data/beta/LSI_ivtff_0d.txt): 1,754,295 bytes; SHA-256 `3f3f2af18cde10efe75c582f49b07b651c3397022fcbfa5854fecc424c121afa`.
- [ZL3b-n.txt](https://www.voynich.nu/data/ZL3b-n.txt): 411,671 bytes; SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.

Catalog: https://www.voynich.nu/transcr.html
Format: https://www.voynich.nu/software/ivtt/IVTFF_format.pdf

LSI is the catalog-linked beta IVTFF 1.5 conversion (0d), not an IT-only substitute.
The files are publicly downloadable; no public-domain or redistribution license is inferred. Keep local pending license review for any release.

## Phase 1 sources — public-domain underlying editions

- C1: Hildegard, *Causae et curae*, medieval Latin medical prose, Paul Kaiser edition, Leipzig 1903. [Archive metadata](https://archive.org/metadata/hildegardiscaus00hildgoog) records NOT_IN_COPYRIGHT, US. [OCR](https://archive.org/download/hildegardiscaus00hildgoog/hildegardiscaus00hildgoog_djvu.txt).
- C2: Mattioli, *I discorsi ... della materia medicinale*, Venice 1568, Italian herbal/medical prose. Getty/Archive metadata records NOT_IN_COPYRIGHT. [Catalog](https://archive.org/details/gri_33125014246561), [OCR](https://archive.org/download/gri_33125014246561/gri_33125014246561_djvu.txt).
- C3: Bock, *Kreutterbuch*, Strasbourg 1595, ETH-Bibliothek Zürich, Rar 10995. [Catalog and Public Domain Mark](https://www.e-rara.ch/zut/content/titleinfo/32316756), [OCR](https://www.e-rara.ch/zut/download/ftpack/plain/32316756), DOI 10.3931/e-rara-151544.

Underlying historical texts/editions are public domain. OCR is not corrected transcription: scan headers, glosses, cross-column ordering and recognition errors can remain. “Clean” means without added simulated noise. Never interpret OCR effects as inherent properties of Latin/Italian/German.

Source selection uses the first N words after frozen body-text markers, with N=ZL ordinary running-text word count. Source_slices.json records ranges and samples; normalization is in config. No selection by measured resemblance. C1 includes the medical work’s cosmological exposition, not just remedy entries.

- `hildegard_1903_ocr.txt` SHA-256 `fd4c50319594f9819e8ebe099d4d399e2015f17272b23d8685b2b2be68e7bc44`.
- `mattioli_1568_ocr.txt` SHA-256 `f011d86894d0635a30eab9f97d98e51fafb7d82fd85f28c627e5282c4f161880`.
- `bock_1595_ocr.txt` SHA-256 `6ad45002293f2174149a7743a24fcfb488b65ae6d951102ff178fadcdb2c34fa`.

Other raw lookup/download receipts retained:
- `mattioli_metadata.json`, `hildegard_metadata.json`: Archive metadata URLs above.
- `bock_1595_catalog.html`: e-rara catalog above.
- `bock_catalog.html`: attempted https://digital.ulb.hhu.de/vester/content/titleinfo/5277713 returned a JavaScript challenge; not used as corpus text. Attempted /download/fulltext/5277713 returned 404; no text file substituted.
- `bock_archive_search.json`: https://archive.org/advancedsearch.php?q=creator%3A%22Bock%2C+Hieronymus%22&output=json&rows=20 ; lookup only.
- `physica_catalog.html`: https://www.medievalbestiary.info/biblios/biblio113744.htm ; considered Physica before selecting the accessible Causae et curae medical prose edition; lookup only.
- C4–C7 derive from the exact selected C1 word sequence; C8/C9 are local deterministic synthetic generators. C10/C11 derive from the primary ZL running text. Their Voynich-source redistribution status remains as in Phase 0.

## Phase 4 additions

- C12 is a local, deterministic, expansive encoding of C1 through C5. Each atomic sign becomes a fixed stroke sequence. No new external text.
- C13: Nicole Eichenberger and Hedwig Suwelack, *Faithful Transcriptions Data Set*, version 1.0 (2021), DOI 10.5281/zenodo.5582483. [Publisher description and CC0 license](https://lab.sbb.berlin/datensets-transkribathon/?lang=en), [archive download](https://zenodo.org/records/5582483/files/Faithful_Transcriptions_all_transcriptions.zip?download=1).
- Raw file `faithful_transcriptions_5582483.zip`, SHA-256 `051ae4e6bbd984d967fdacea6de75b7e39da9b7259503479e232f16124040642`. `faithful_catalog.html` preserves the publisher page. Select only nested `SBB_PK_Mgf516.zip`, its 36 individual folio XML files, not the duplicate aggregate XML.
- Manuscript: Berlin, SBB-PK, Ms. germ. fol. 516, Niederrheinische Historienbibel, c.1457–1460. Middle High German, Bastarda. All 2,252 available physical line records and their image coordinates are retained. Individual XML hashes are in C13/metadata.json. Abbreviated readings are selected from TEI choice elements; expanded alternatives, deleted text, and modern notes do not get counted as extra manuscript words. Original line boundaries and split-word fragments remain intact. The final corrected selection has 11,056 word fragments; six deleted words included by the first descendant-word parser were removed before any model training.
- This is a deliberately shorter authentic-layout control (about 32% of the primary word count). Do not label it word-count matched, or repeat/reflow it to manufacture coverage. Its manuscript genre, abbreviation conventions and size differ from C1/ZL.
- The CREMMA repository was inspected as a candidate but its current license metadata says CC-BY; it was not substituted for this CC0 source.
