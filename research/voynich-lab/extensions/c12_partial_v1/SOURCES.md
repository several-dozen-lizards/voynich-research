# C12 partial sweep provenance

This extension uses only existing local control inputs and cached manuscript measurements. It does not fetch or score manuscript text.

- C1: the exact existing 34,509-word Latin selection from Hildegard, *Causae et curae*, Paul Kaiser edition (1903), uncorrected OCR. Original provenance and licensing remain in `voynich-lab/SOURCES.md`. Raw bytes are copied to `instrument/data/raw/hildegard_1903_ocr.txt`, SHA256 `fd4c50319594f9819e8ebe099d4d399e2015f17272b23d8685b2b2be68e7bc44`. Existing automatic normalization and selected range are unchanged.
- Layout: copied C1 control rows preserve the previously borrowed running-text page/line/paragraph geometry. No fresh ZL/H transcription is loaded. Word-slot count and position events remain identical to the old sweep.
- Encoder/instrument: copied local `src` and configs, with the relevant source hashes checked against `runs/phase5-c2f38fa45d6b/FREEZE.json`. This is a synthetic partial-decomposition family, not a published historical-code replication.
- Endpoints: copies of SW04 and SW09–SW17 data/config/metrics from the completed Phase5 sweep. `CACHE_ADMISSION.json` records preparation identity; `REPLAY_VERIFICATION.json` checks exact baseline/position replay before reuse. Nominal duplicate settings are retained as aliases, never treated as independent observations.
- References: cached Phase5 ZL/LSI-H h2, word-length histograms and five-seed position gains. These descriptive sensitivity bands are reused exactly in scope; no new manuscript model or score is computed. Histograms permit W1 calculation without loading manuscript words.
- Noise: copied existing symmetric transcription-sensitivity channel and rates. One fixed realization per setting, coupled by the old namespace. Five model seeds do not measure encoder/noise uncertainty.
- Preservation: INPUT_SNAPSHOT.json records original source/config/report/C5/C12 hashes. REGISTRATION.json records active frozen code, references, codebooks, data and job plan. The earlier registration and failed implementation artifacts are preserved; the sole post-freeze bookkeeping repair is documented in EXECUTION_LOG.md.

The C16-KH failed runs, qualification receipts, ZL hold and actual-C11 hold are outside this extension and remain unchanged. No semantic, translation or historical identification follows from a match or failure on this grid.
