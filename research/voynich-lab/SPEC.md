# Voynich Pattern-Model Pipeline — Spec for Codex

## Purpose
Use small, cheap models as *measuring instruments* on the Voynich Manuscript text. Goal is NOT translation. Goal is to find out what kind of system generated the text by comparing it, through an identical pipeline, against control texts made by known generators (natural language, shorthand, cipher, gibberish generators).

**Core rule: no finding about Voynich counts unless the same measurement was run on the controls.** A model will find patterns in anything, including gibberish. Every number in the report must sit next to the control numbers.

## Hardware / stack
- Local Windows machine, consumer GPU. Everything must run locally. No cloud.
- Python 3.11+, PyTorch, numpy, pandas, scikit-learn, matplotlib. Jupyter optional for the report.
- Models are tiny (≤5M params). Each training run should take minutes, not hours.
- Fixed seeds. Every run logged to `runs/<run_id>/` with config, seed, metrics JSON.

## Repo layout
```
voynich-lab/
  data/
    raw/            # downloaded source files, untouched
    voynich/        # parsed Voynich lines + metadata (parquet/csv)
    controls/       # one folder per control corpus
  src/
    parse_ivtff.py
    tokenize.py     # three tokenization schemes
    encoders/       # shorthand / cipher / generator implementations
    metrics.py      # model-free statistics
    train.py        # single config-driven trainer
    probes.py
    surprise.py
  configs/
  runs/
  report/
  SOURCES.md        # provenance for every file in data/raw
  DECISIONS.md      # every judgment call, with reason
```

## Phase 0 — Data (stop and report when done)
1. Obtain Voynich transliterations in IVTFF format (René Zandbergen's site, voynich.nu, hosts these). Need at minimum: the ZL transcription and the Landini–Stolfi interlinear (multiple transcribers). If you cannot download, STOP and ask Re to supply the files. Do not substitute a different transcription silently.
2. Parse into one row per line with fields: `folio, line_id, transcriber, text_eva, section, currier_lang, hand/scribe, is_label, line_index_in_paragraph, is_para_start, is_para_end`. Take section/language/hand from IVTFF page headers where present. Record anything you could not populate in DECISIONS.md.
3. Handle uncertain-reading markup (`?`, `[a:b]` alternates, `{}` ligatures, weirdo chars): keep a "clean" version (first reading, uncertain glyphs → a single UNK symbol) and keep the raw string too.
4. Report: total lines, words, characters, vocabulary size, per-section counts, and transcriber agreement rate (character-level) on lines covered by more than one transcriber. **Transcriber disagreement is the noise floor; report it prominently.**

## Phase 1 — Control corpora
Each control truncated/sampled to match Voynich's size (character count ±5%) and formatted into lines/paragraphs of matching length distribution. Provenance in SOURCES.md. Public-domain sources only.

| ID | Control | Notes |
|---|---|---|
| C1 | Latin herbal/medical prose (medieval or early-modern) | plain orthography |
| C2 | Same, Italian | |
| C3 | Same, German | |
| C4 | C1 run through **medieval Latin scribal abbreviation** encoder | suspension, contraction, common -us/-um/-rum/-orum endings → single marks, per/pro/prae sigla |
| C5 | C1 run through **Tironian-style shorthand** encoder | high-frequency words → single sigla, others → abbreviated stems + ending marks |
| C6 | C1 run through **astro-mixed shorthand** encoder | as C5, plus planet/zodiac/astro terms → single glyph symbols |
| C7 | **Verbose cipher** of C1 | each letter → fixed 1–3 glyph group from a Voynich-sized alphabet |
| C8 | **Self-citation generator** (Timm & Schinner style) | new words made by copying a recent word and mutating it |
| C9 | **Table-and-grille gibberish** (Rugg style) | prefix/mid/suffix tables + grille |
| C10 | Shuffled Voynich (words shuffled within page) | destroys order, keeps vocabulary |
| C11 | Shuffled Voynich (chars shuffled within word) | |

Encoders C4–C9 must be deterministic given a seed, documented in their own module docstring, and parameterized (e.g. abbreviation aggressiveness) so we can sweep them later. All controls are mapped to a symbol alphabet of comparable size to EVA before training, so alphabet size isn't a confound.

## Phase 2 — Tokenization schemes
Implement three, applied identically to Voynich and every control:
- **T1 char**: one EVA character = one token.
- **T2 cluster**: greedy merge of known EVA multi-char units (`ch, sh, cth, ckh, cph, cfh, ii, iii, in, iin, aiin, qo, ee` — list lives in config, editable).
- **T3 word**: whitespace-delimited words (EVA `.` and line breaks as separators).
For controls, T2 uses the control's own top-k BPE merges with k matched to the number of T2 clusters in Voynich.

## Phase 3 — Model-free metrics (metrics.py)
Per corpus × tokenization:
- h0, h1, h2 (conditional character entropy) — Voynich's low h2 is the famous anomaly; this is a headline row.
- Zipf slope + fit quality, type/token growth curve, hapax ratio.
- Word length distribution (mean, variance, shape).
- **Line-position effects**: mutual information between glyph identity and (a) position in line (first/last word), (b) paragraph-start line, (c) position in word.
- Word-repetition: rate of identical and near-identical (edit distance 1) consecutive words.
Output: one table, rows = corpora, columns = metrics.

## Phase 4 — Models (train.py, one script, config-driven)
- Architectures: small char/token LSTM (2 layers, ~512 hidden) and small transformer (4 layers, d=256). Both, every corpus.
- 80/10/10 split **by folio/page**, never by random line (prevents leakage of near-duplicate lines).
- Variants per corpus: with and without line-position embedding (start-of-line / end-of-line / paragraph-start tokens).
- Metrics: held-out bits per token; the **gain** in bits from adding line-position info (natural language ≈ near zero; this is a key Voynich test).
- 5 seeds per config. Report mean ± sd. A difference smaller than seed variance or transcriber noise is reported as "no difference."

## Phase 5 — Analyses
1. **Generator fingerprinting.** Feature vector per corpus = Phase 3 metrics + Phase 4 metrics. Plot PCA/UMAP; nearest-neighbor ranking of controls to Voynich; leave-one-out classifier over many sampled chunks of each corpus (chunk ~2k words) to say which generator class Voynich chunks get assigned to, with confidence. Run separately for Currier A and B.
2. **Shorthand sweep.** For C4–C6, sweep encoder aggressiveness parameters; plot where on each curve the corpus best matches Voynich's h2, word-length distribution, and line-position gain. Report whether ANY setting matches on all three at once.
3. **Surprise map.** Per-token surprisal from the best Voynich model (cross-validated: each folio scored by a model not trained on it). Output a per-folio heatmap CSV and plot; list top 50 most-surprising words with folio/line. Flag labels separately.
4. **Labels vs. running text.** Compare label tokens to running-text tokens on all metrics. Score labels under the running-text model.
5. **Probes.** From a single line's model representation, predict: section, Currier language, scribe/hand, is-paragraph-start. Same probes on controls with fake section labels as a sanity floor. Report accuracy vs. majority-class baseline.
6. **Embedding geometry (T3).** Word embeddings → check whether nearest neighbors are morphological families (shared stem, varied affix) or edit-distance chains. Compare the same structure in C1, C5, C8.

## Deliverable
`report/REPORT.md` (+ figures) containing: data summary and noise floor; the master metrics table; fingerprint plot + classifier result; shorthand sweep result; surprise map + top-50 list; probe table; a section "What this does NOT show." Every Voynich claim cites its control comparison.

## Guardrails for the agent
- Do not claim, imply, or attempt decipherment or translation.
- Do not tune anything on Voynich that isn't tuned identically on every control.
- Do not drop or replace a control because it's inconvenient; log failures instead.
- Do not change the transcription source, tokenization lists, or split method without logging it in DECISIONS.md.
- Stop and report to Re at the end of Phase 0, Phase 3, and Phase 5. Do not run ahead.
- If a result looks dramatic, re-run with different seeds and the alternate transcription before reporting it, and say you did.