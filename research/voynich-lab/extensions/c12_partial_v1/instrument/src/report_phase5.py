"""Render the final evidence report from saved artifacts, without new inference."""
from src.train import *
from src.extend_phase3 import read

def fmt(v,digits=4):return 'NA' if v in [None,''] else f'{float(v):.{digits}f}'

def render(experiment,config,p5):
    summary=read(ROOT/'report/model_summary.csv');gains=read(ROOT/'report/line_position_gain.csv')
    modelruns=read(ROOT/'report/model_runs.csv');master=read(ROOT/'report/master_metrics_extended.csv')
    classifier=json.loads((ROOT/'report/classifier_result.json').read_text())
    assignments=read(ROOT/'report/classifier_voynich_assignments.csv');sweep=read(ROOT/'report/shorthand_sweep.csv')
    probes=read(ROOT/'report/probes.csv');geometry=read(ROOT/'report/embedding_geometry.csv')
    best=json.loads((ROOT/'report/best_voynich_model.json').read_text());labels=read(ROOT/'report/labels_model_scores.csv')
    confirmation=read(ROOT/'report/confirmation_position_gain.csv');audit=json.loads((ROOT/'report/paragraph_audit.json').read_text())
    endpoint=sum(r['still_improving_at_budget']=='True' for r in modelruns)/len(modelruns)
    joined=[]
    for row in master:
        item=dict(row)
        for architecture in ['lstm','transformer']:
            for position,label in [('False','baseline'),('True','positioned')]:
                matches=[m for m in summary if m['corpus']==row['corpus'] and m['tokenization']==row['tokenization'] and m['architecture']==architecture and m['with_position']==position]
                if matches:
                    for key in ['test_bpt_mean','test_bpt_sd','test_bpc_mean','unknown_rate_mean','effective_epochs_mean','parameter_count','seeds']:
                        item[architecture+'_'+label+'_'+key]=matches[0][key]
            matching=[g for g in gains if g['corpus']==row['corpus'] and g['tokenization']==row['tokenization'] and g['architecture']==architecture]
            if matching:
                for key in ['gain_mean','gain_sd','transcription_gain_sensitivity','interpretation']:item[architecture+'_'+key]=matching[0][key]
        joined.append(item)
    table(ROOT/'report/master_metrics_final.csv',joined)
    names=['ZL_running','LSI_H_running']+[f'C{i}_{v}' for i in range(1,14) for v in ['clean','noise']]
    report=['# Voynich pattern-model pipeline — Phase 5 report','',
        '**COMPLETE AND STOPPED AFTER PHASE 5. No translation or decipherment was attempted.**','',
        f'Experiment: `{experiment.name}`. Phase 4 contains {len(modelruns):,} registered fits, five seeds for every corpus/tokenization/architecture/position condition. All models fit below 5M parameters and ran locally on the RTX 5060.','',
        f'**Qualification limit:** these are fixed-compute instruments (96 optimization steps, 32×64 sampled blocks), not convergence-qualified models. The final checkpoint attained the best observed validation loss in {endpoint:.1%} of main fits. Effective epoch counts, vocabulary coverage and curves are saved. Model differences, fingerprints and probe accuracies remain conditional on this budget and representation.','',
        '## Data, provenance and transcription sensitivity','',
        'Primary: ZL ordinary running paragraph text, 3,996 loci / **34,509 words / 172,280 nonspace EVA characters**. Alternate: LSI transcriber H alone, never pooled. Labels and other diagram/free-floating text remain separate. Sources, byte hashes and retrieval failures are in [SOURCES.md](../SOURCES.md); all choices/corrections are in [DECISIONS.md](../DECISIONS.md).','',
        'Historical pairwise agreement: **95.7273%**; disagreement: **4.2727%**, 33,785 edits / 790,720 normalized character positions, from 19,741 eligible LSI line-pairs. This is transcription sensitivity, not ground-truth error or a quantity in model bits/token. Pairwise operation reconstruction gives 2.1596% substitutions and symmetric 1.0566% insertion/deletion rates.','',
        f"The 1,329 original missing paragraph positions were fully accounted for: {audit['dispositions']}. Sixty-one ordinary paragraph positions were recovered by preserving state across interleaved labels; no primary positions remain missing. Thirteen unmarked Pb loci remain unknown in the separate free-floating corpus. [Full audit](paragraph_missing_loci.csv).",'',
        '## Controls, tokenization and the extended Phase 3 summary','',
        'C1 Latin medical prose; C2 Italian herbal; C3 German herbal; C4 scribal abbreviation; C5 shorthand; C6 astro-mixed shorthand; C7 verbose cipher; C8 simplified recent-word copying; C9 simplified table/grille; C10 page-local word shuffle; C11 within-word character shuffle; C12 expansive shorthand; C13 authentic manuscript lineation. Every control has clean and noise-injected versions.','',
        'C12 uses C5, then decomposes every atomic sign into a fixed multi-stroke sequence. Length and slot rigidity are explicit parameters. A pre-C12-training counterfactual test caught constant nominally-variable slots; the corrected encoder uses independent permutations in variable slots. Earlier C12 snapshots are preserved and superseded. No C12 neural model used the faulty encoder.','',
        'C13 is the CC0 diplomatic transcription of SBB-PK Ms. germ. fol. 516 (c.1457–1460): **2,252 authentic lines, 36 available pages, 11,056 word fragments**. Its original image-coordinate line records, abbreviations and cross-line fragments are preserved. It is shorter than ZL and differs in genre, language and transcription conventions; it is explicitly not word-count matched. Six deleted words caught in parser validation were removed before training.','',
        'Other clean controls match the primary word count exactly and use its word-slot layout. Noise can alter word count slightly; every C1–C12 noisy variant remains within the registered tolerance. [Word/character matching table](size_matching_extended.csv). C13 retains its own layout in both versions. “Clean” C1–C3 still contain uncorrected OCR. C8/C9 are schematic style controls, not validated published-code replications.','',
        'T1: code points including spaces. T2: the frozen 13 EVA clusters on Voynich; 13 training-page-only BPE merges per control, reused on its noisy version. T3: words. h0 is unigram Shannon entropy; h1/h2 condition on one/two preceding tokens within a locus. These are plug-in estimates, with sparse-context bias and support counts. T2 bits/token are not T1 bits/character.','',
        '| Corpus | Scheme | h0 | h1 | h2 |','|---|---|---:|---:|---:|']
    for r in read(ROOT/'report/T1_T2_entropy_comparison.csv'):
        report.append(f"| {r['corpus']} | {r['tokenization']} | {fmt(r['h0'])} | {fmt(r['h1'])} | {fmt(r['h2'])} |")
    report += ['', 'The full [105-row master metric matrix](master_metrics_final.csv) joins every primary/alternate/A/B/label/Pb/control row for all three schemes with Phase 4 model means/SDs, gains, OOV and exposure where applicable. [Phase 3-only matrix](master_metrics_extended.csv) · [Growth and length distributions](growth_and_lengths_extended.json). Alphabet sizes are disclosed; injective relabeling does not remove cardinality confounding.','',
        '| Authentic-line comparison | Line-edge MI, bits |','|---|---:|']
    for name in ['ZL_running','C1_clean','C13_clean','C13_noise']:
        r=next(r for r in master if r['corpus']==name and r['tokenization']=='T1')
        report.append(f"| {name} | {fmt(r['mi_glyph_line_word_edge'],6)} |")
    report += ['', '## Phase 4: held-out models and causal position information','',
        'Page splits group all sides/panels of a leaf; no random-line split. The main split is 80/10/10, frozen before fitting. Both architectures use tied 256-dimensional input/output embeddings: LSTM 2×512 plus projection, transformer 4 layers at d=256. The largest instantiated models are below 5M parameters. Every main condition uses seeds 1729/1733/1741/1753/1777.','',
        'The position model receives only events observed before the next content target: SOL, preceding EOL, explicit paragraph start. It never receives future line length or a target-last-word flag. Future-content/layout counterfactual tests pass for both architectures. Baseline and position models score identical content targets; padding is excluded.','',
        'T3 uses at most 4,096 training word types plus special classes. OOV rates accompany scores. Raw BPT measures the collapsed model vocabulary; cross-tokenization validation selection additionally charges each OOV token a literal fallback (32-bit UTF-8 byte length plus its bytes) and reports bits/nonspace source character. This conservative fallback is a declared coding convention, and is affected by display encoding; it is not a language-inherent compression rate. No raw BPT comparison across different schemes is used for best-model selection.','',
        'Gain is paired baseline BPT minus position BPT for each seed. Tables report mean ± sample SD. “No difference” means the gain magnitude is below seed SD or the observed ZL/LSI-H gain sensitivity in the same units. These are descriptive bands, not significance/equivalence tests.','',
        '| Corpus | LSTM T1 BPT, baseline | LSTM position gain | Transformer T1 BPT, baseline | Transformer position gain |','|---|---:|---:|---:|---:|']
    for name in names:
        cells=[]
        for arch in ['lstm','transformer']:
            r=next(r for r in summary if r['corpus']==name and r['tokenization']=='T1' and r['architecture']==arch and r['with_position']=='False')
            g=next(r for r in gains if r['corpus']==name and r['tokenization']=='T1' and r['architecture']==arch)
            cells.extend([fmt(r['test_bpt_mean'])+' ± '+fmt(r['test_bpt_sd']),fmt(g['gain_mean'])+' ± '+fmt(g['gain_sd'])])
        report.append('| '+name+' | '+' | '.join(cells)+' |')
    report += ['', '![Position gains](model_position_gain.png)','',
        '[All schemes and A/B model summaries](model_summary.csv) · [Paired gains and operational bands](line_position_gain.csv) · [Every run, OOV rate, exposure and checkpoint](model_runs.csv). Unknown Currier labels are excluded from A/B and never imputed. A/B scores use held-out tokens of the corresponding full-corpus model; anonymous inter-line joins are excluded.','',
        '## Phase 5: fingerprints and classification','',
        '![Control-fitted PCA](fingerprint_pca.png)','',
        'Scaling and PCA are fitted on controls only; ZL/LSI-H and their A/B subsets are projected afterward. [Full feature vectors](fingerprint_features.csv), [all control-neighbor rankings](nearest_controls.csv), [PCA definition](fingerprint_pca_metadata.json). Distance is to these settings/corpora, not to an entire historical mechanism.','',
        f"Chunk classifier: approximately 2,000 words per retained chunk. Source-word block indices are left out across ALL controls at once, preserving C1 derivative and clean/noise grouping. The classifier combines T1 model-free features with one-seed, five-fold leaf-cross-fitted LSTM T1 lexical BPC/position gain. Held-out accuracy **{classifier['accuracy']:.2%}**, balanced accuracy **{classifier['balanced_accuracy']:.2%}**, training-majority baseline **{classifier['majority_baseline']:.2%}**, over {classifier['test_chunks']} held-out chunks.",'',
        'Classifier C is selected on an inner source block. ZL, H, A and B queries never fit the scaler/classifier. Scores below are assignments among C1–C13 only. Probabilities are uncalibrated conditional class scores, not probabilities that a historical mechanism produced Voynich. C10/C11 derive from Voynich itself; shared vocabulary and source conventions can drive proximity. Each setting has one text/generator realization: chunk cross-validation tests new blocks of these corpora, not independent source corpora or generator instances.','',
        '| Query | Chunks | Most frequent assignment | Assignment share | Mean maximum class score |','|---|---:|---|---:|---:|']
    nearest=read(ROOT/'report/nearest_controls.csv')
    ranking=['| Query | Nearest three controls in full standardized feature space |','|---|---|']
    for query in sorted({r['query'] for r in nearest}):
        rs=sorted([r for r in nearest if r['query']==query],key=lambda r:int(r['rank']))[:3]
        ranking.append('| '+query+' | '+', '.join(r['control']+' ('+fmt(r['standardized_distance'],3)+')' for r in rs)+' |')
    ranking += ['', 'Distances in parentheses use the full standardized vector, not the two displayed PCA coordinates. C10 is a shuffle of the query manuscript: closeness to C10 carries a shared-vocabulary/source confound and does not identify a historical generator.','', 'Classifier audit corrected C13 noisy chunk boundaries to use clean source offsets, preserving its clean/noise ancestry across outer folds. Provisional classifier outputs are preserved and superseded; the figures below use the corrected rerun. [Source-line chunk membership](classifier_chunk_membership.csv).','']
    insertion=next(i for i,line in enumerate(report) if line.startswith('Chunk classifier:'))
    report[insertion:insertion]=ranking
    for query in sorted({r['corpus'] for r in assignments}):
        rs=[r for r in assignments if r['corpus']==query];counter=Counter(r['assigned_control'] for r in rs);c,n=counter.most_common(1)[0]
        report.append(f"| {query} | {len(rs)} | {c} | {n/len(rs):.2%} | {np.mean([float(r['confidence']) for r in rs]):.4f} |")
    report += ['', '[Every query assignment and class score](classifier_voynich_assignments.csv) · [Held-out predictions](classifier_heldout_predictions.csv) · [Confusion table](classifier_confusion.csv). Partial chunks below 1,600 words are excluded by the frozen rule; C13 contributes fewer chunks. The reference neural chunk features use one model seed per CV fold, so classifier uncertainty does not cover all neural seed variation.','',
        '## Shorthand sweep, including expansive decomposition','',
        'C4–C6 aggressiveness=.25/.65/1. C12: sequence length=2/3/4 × slot rigidity=0/.5/1 at aggressiveness=.65. Clean/noise versions use the same T1 LSTM baseline/position instrument and five seeds. Rigidity sets an integer number of shared slots, so some sampled points coincide (length 2, rigidity 0 and .5); they are not independent replications. This is a sampled grid; no interpolation or post-hoc parameter search is claimed.','',
        '![Shorthand aggressiveness sweep](shorthand_sweep.png)','',
        '![C12 length/rigidity grid](C12_sweep_grid.png)','',
        f"Settings matching h2, word-length distribution and model position gain simultaneously within the registered descriptive bands: **{sum(r['matches_all_three']=='True' for r in sweep)} / {len(sweep)} versioned grid points**.",'',
        'Bands use the observed ZL/H h2 difference, their word-length Wasserstein distance, and the larger seed/transcription sensitivity for gain. They are not formal equivalence margins. A match would only match these measurements; a failure only concerns this encoder/grid. In particular, C12 decomposes every atomic sign and therefore expands whole word lengths, not only abbreviation marks. [Full sweep receipts](shorthand_sweep.csv).','',
        '## Cross-fitted surprise map and labels','',
        f"Validation-only best registered Voynich coding model: **{best['architecture']} / {best['tokenization']} / position={best['with_position']}**. Mean validation BPC with the declared literal fallback: {best['validation_bpc_with_escape']:.5f}. This is best among the tested finite-budget instruments, not an optimal model of the manuscript.",'',
        'Five-fold scoring excludes the entire scored leaf (all sides/panels) from each fitted model’s training and internal validation. Vocabulary/BPE are refitted inside folds where applicable. Architecture/scheme/position choice is globally fixed from the original main validation split; this is not nested model-selection CV, and those selection pages also receive map scores. Running text has page context; actual labels and other C/R/Pb text are scored independently from BOS, without assuming an unregistered reading order. All nonempty ZL loci are covered.','',
        '![Cross-fitted surprise map](surprise_map.png)','',
        '[Per-model-token surprisal](best_model_token_surprise.csv) · [Per-word scores](surprise_words.csv) · [Per-folio heatmap values](surprise_folios.csv) · [Top 50 surprising words](top50_surprising_words.csv). Lexical word scores exclude separators and include the declared OOV escape. Sum and per-character scores, unknown flags, folio/line/word index and text role are retained. High scores can reflect length, rare glyphs, transcription uncertainty or OOV coding; they are not semantic discoveries.','',
        'Actual labels are compared with source words cut into matched pseudo-label word-slot lengths on every control. No words are duplicated to fill those sets. Actual ZL/H labels never enter running-model training. Each control pseudo-label is scored by a model excluding its entire source leaf; other leaves still supply ordinary running-text training words. Both actual and pseudo-labels are scored from independent BOS context.','',
        '| Corpus | Baseline label/pseudo-label lexical BPC | Positioned label/pseudo-label lexical BPC |','|---|---:|---:|']
    for name in names:
        a=next(r for r in labels if r['corpus']==name and r['with_position']=='False');b=next(r for r in labels if r['corpus']==name and r['with_position']=='True')
        report.append(f"| {name} | {fmt(a['heldout_lexical_bpc'])} | {fmt(b['heldout_lexical_bpc'])} |")
    report += ['', '[All label/pseudo-label statistics](labels_model_free.csv) · [Model scoring and OOV counts](labels_model_scores.csv). H’s label coverage differs from ZL; it remains separate. Pseudo-labels control length/context conventions, not historical referents or label meaning.','',
        '## Held-out probes','',
        'Single-line baseline-model representations; no paragraph/section/Currier/hand metadata enters the representation. Architecture/scheme is selected by validation coding rate, and logistic C by validation accuracy. Evaluation uses held-out leaf pages. Section/Currier use source metadata on ZL/H and independent fake page labels on controls. Hand/scribe and paragraph-start are **ZL-only**. Fake label distributions follow ZL training pages; they do not impute Currier language to a control.','',
        '| Corpus | Target | Accuracy | Training-majority baseline | Test lines |','|---|---|---:|---:|---:|']
    for r in probes:report.append(f"| {r['corpus']} | {r['target']} | {fmt(r.get('accuracy'))} | {fmt(r.get('majority_baseline'))} | {r['test']} |")
    report += ['', '[Probe class support, balanced accuracy and estimability](probes.csv). These diagnostic probes use the first seed’s validation-selected baseline representation. Some held-out sets lack classes seen in training; balanced accuracy then averages only the supported test classes. Page/section/hand covariation and C13’s small held-out page count limit interpretation. Predicting a Currier label does not identify or read a language.','',
        '## T3 embedding geometry','',
        'For ZL/C1/C5/C8, cosine neighbors of frequent training words are compared across both architectures and five model seeds. “Prefix family” means shared prefix length≥3 and at least half the shorter string; edit chains mean distance exactly1. These are explicit string heuristics, not linguistic or semantic annotation. Length-matched random neighbors provide a local reference.','',
        '| Corpus | Architecture | Edit-1 neighbor fraction, mean ± SD | Prefix-family fraction, mean ± SD |','|---|---|---:|---:|']
    for corpus in ['ZL_running','C1_clean','C5_clean','C8_clean']:
        for arch in ['lstm','transformer']:
            rs=[r for r in geometry if r['corpus']==corpus and r['architecture']==arch]
            report.append(f"| {corpus} | {arch} | {np.mean([float(r['edit1_fraction']) for r in rs]):.4f} ± {np.std([float(r['edit1_fraction']) for r in rs],ddof=1):.4f} | {np.mean([float(r['prefix_family_fraction']) for r in rs]):.4f} ± {np.std([float(r['prefix_family_fraction']) for r in rs],ddof=1):.4f} |")
    report += ['', '[All geometry and random-reference values](embedding_geometry.csv) · [Neighbor examples](embedding_neighbor_examples.csv). Stem-like strings and edit chains can overlap; no meanings or morphological analyses are assigned.','',
        '## Changed-seed qualification','',
        'The validation-selected headline instrument was additionally rerun with seeds 1783/1787/1789/1801/1811, on BOTH ZL and H and EVERY clean/noisy control, under the same budget. [All confirmation runs](confirmation_runs.csv) and [paired gains](confirmation_position_gain.csv) are retained. This does not retroactively qualify every single-seed CV/probe estimate or supply convergence.','',
        '## What this does NOT show','',
        'No translation, decipherment, word meaning, language identification or unique historical generator identification is established. Similarity to a known synthetic control is not a mechanism proof; mismatch with a schematic encoder does not exclude a historical class. Full-corpus fingerprints, small-source C13, classifier class scores and string-neighbor geometry have the limits stated beside them.','',
        'The finite training budget, OOV collapse/literal coding, OCR errors, alphabet differences, artificial layout on C1–C12, real manuscript transcription conventions on C13, and source ancestry are material confounds. Paragraph/line-position gains only concern the causal input definition actually tested. A small or negative gain is not evidence that layout is irrelevant. No metric is compared directly against a percentage edit floor.','',
        'All controls, failed attempts, corrections and negative results are preserved. Tests, leakage receipts, parameter caps, artifact coverage and run hashes are checked in [PHASE5_VERIFICATION.json](PHASE5_VERIFICATION.json). Accepted earlier checkpoints remain in their report snapshots and run folders. **Stop after Phase 5.**','']
    confirmation_table=['| Selected instrument | Original five-seed position gain | Five new seeds |','|---|---:|---:|']
    for name in ['ZL_running','LSI_H_running','C1_clean','C10_clean','C12_clean','C13_clean']:
        original=next(r for r in gains if r['corpus']==name and r['architecture']==best['architecture'] and r['tokenization']==best['tokenization'])
        fresh=next(r for r in confirmation if r['corpus']==name)
        confirmation_table.append('| '+name+' | '+fmt(original['gain_mean'])+' ± '+fmt(original['gain_sd'])+' | '+fmt(fresh['gain_mean'])+' ± '+fmt(fresh['gain_sd'])+' |')
    confirmation_table += ['', 'Paired gains are baseline minus positioned BPT, mean ± sample SD. The table uses the selected architecture/tokenization on every listed corpus. All 28 corpus/version confirmation rows are retained in the linked table. Seed agreement under the same short budget does not establish convergence or a historical mechanism.','']
    insertion=report.index('## What this does NOT show')
    report[insertion:insertion]=confirmation_table
    (ROOT/'report/REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    plot_gains(gains)

def plot_gains(gains):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    for row,arch in enumerate(['lstm','transformer']):
        for col,scheme in enumerate(['T1','T2','T3']):
            ax=axes[row,col]
            for version,color,offset in [('clean','#155f7b',-.1),('noise','#b36c20',.1)]:
                rs=[next(r for r in gains if r['corpus']==f'C{i}_{version}' and r['architecture']==arch and r['tokenization']==scheme) for i in range(1,14)]
                ax.errorbar(np.arange(1,14)+offset,[float(r['gain_mean']) for r in rs],yerr=[float(r['gain_sd']) for r in rs],fmt='o',ms=3,capsize=2,color=color,label=version)
            for name,color,style in [('ZL_running','#222222','-'),('LSI_H_running','#86529b','--')]:
                r=next(r for r in gains if r['corpus']==name and r['architecture']==arch and r['tokenization']==scheme)
                ax.axhline(float(r['gain_mean']),color=color,ls=style,label=name)
            ax.axhline(0,color='gray',lw=.7);ax.set_xticks(range(1,14),[f'C{i}' for i in range(1,14)],rotation=45)
            ax.set_title(arch+' '+scheme);ax.set_ylabel('Baseline − positioned BPT');ax.grid(alpha=.15)
    axes[0,0].legend(fontsize=7);fig.suptitle('Held-out causal line-position gain; paired five-seed mean ± sample SD')
    fig.savefig(ROOT/'report/model_position_gain.png',dpi=160);plt.close(fig)
