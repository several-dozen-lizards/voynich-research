"""Build a separate Phase 6 report from completed artifacts only."""
from .common import *
from collections import defaultdict,Counter
import statistics,math,os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from src.fingerprint import BASE_FEATURES
from threadpoolctl import threadpool_limits

def mdtable(records,keys,limit=None):
    def fmt(v):
        if v is None or v=='':return '—'
        if isinstance(v,float):return f'{v:.4g}'
        return str(v).replace('|','/').replace('\n',' ')
    selected=records if limit is None else records[:limit]
    return '| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(fmt(r.get(k)) for k in keys)+' |' for r in selected)+'\n'

def fingerprints():
    master=read(EXT/'report/master_metrics.csv');models=read(EXT/'report/model_summary.csv');gains=read(EXT/'report/line_position_gain.csv')
    names=[n for n,m in registry().items() if not m.get('analysis_only') and n not in ['C8_clean','C8_noise']]
    queries=['ZL_running_A','ZL_running_B','LSI_H_running_A','LSI_H_running_B'];names+=queries;records=[]
    for name in names:
        r=next(r for r in master if r['corpus']==name and r['tokenization']=='T1');d={k:float(r[k]) for k in BASE_FEATURES}
        for t in ['T2','T3','T4']:
            row=next(r for r in master if r['corpus']==name and r['tokenization']==t)
            d.update({t+'_'+k:float(row[k]) for k in ['h0','h1','h2']})
        for t in ['T1','T2','T3','T4']:
            for a in ['lstm','transformer']:
                r=next(r for r in models if (r['corpus'],r['tokenization'],r['architecture'],r['with_position'])==(name,t,a,'False'))
                g=next(r for r in gains if (r['corpus'],r['tokenization'],r['architecture'])==(name,t,a))
                d[f'{t}_{a}_bpc']=float(r['test_bpc_mean']);d[f'{t}_{a}_gain']=float(g['gain_mean'])
        records.append(dict(corpus=name,**d))
    project(records,list(records[0])[1:],'fingerprint',lambda r:r['corpus'].startswith('C'))
    baseline=[dict(corpus=r['corpus'],**{k:float(r[k]) for k in BASE_FEATURES}) for r in read(EXT/'report/natural_baseline_metrics.csv') if r['tokenization']=='T1']
    baseline += [dict(corpus=n,**{k:float(next(r for r in master if r['corpus']==n and r['tokenization']=='T1')[k]) for k in BASE_FEATURES}) for n in ['ZL_running','LSI_H_running']+queries]
    project(baseline,BASE_FEATURES,'natural_baseline',lambda r:':' in r['corpus'])

def project(records,keys,tag,fit_mask):
    x=np.array([[float(r[k]) for k in keys] for r in records]);mask=np.array([fit_mask(r) for r in records]);assert np.isfinite(x).all()
    scaler=StandardScaler().fit(x[mask]);z=scaler.transform(x);pca=PCA(2).fit(z[mask]);xy=pca.transform(z)
    table(EXT/f'report/{tag}_features.csv',records);table(EXT/f'report/{tag}_pca.csv',[dict(corpus=r['corpus'],PC1=float(v[0]),PC2=float(v[1])) for r,v in zip(records,xy)])
    nearest=[]
    for i,r in enumerate(records):
        if mask[i]:continue
        ds=sorted((float(np.linalg.norm(z[i]-z[j])),s['corpus']) for j,s in enumerate(records) if mask[j])
        nearest.extend(dict(query=r['corpus'],rank=k+1,control=n,standardized_distance=d) for k,(d,n) in enumerate(ds))
    table(EXT/f'report/{tag}_nearest.csv',nearest)
    dump(EXT/f'report/{tag}_PCA_RECEIPT.json',dict(fit='control/baseline only',features=keys,explained_variance=pca.explained_variance_ratio_.tolist(),query_used_to_fit=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(11,7),layout='constrained');ax.scatter(xy[mask,0],xy[mask,1],s=14,alpha=.5,label='Controls / natural baseline')
    for r,v,m in zip(records,xy,mask):
        if not m:ax.scatter(*v,marker='*',s=90,color='#a63838');ax.annotate(r['corpus'].replace('ZL_running','ZL').replace('LSI_H_running','H'),v,xytext=(5,5),textcoords='offset points',fontsize=8)
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})');ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})');ax.set_title('Descriptive projection; full feature-space distances define ranks');ax.legend();fig.savefig(EXT/f'report/{tag}_pca.png',dpi=150);plt.close(fig)

def c15_comparisons():
    master=read(EXT/'report/master_metrics.csv');output=[]
    from scipy.stats import wasserstein_distance
    lens=lambda rs:[len(w) for r in rs for w in r['text_eva'].split()]
    for name in registry():
        if not name.startswith('C15_'):continue
        for query in ['ZL_running','LSI_H_running']:
            for lang in ['A','B']:
                q=query+'_'+lang;qr=[r for r in corpus(query) if r.get('currier_lang')==lang]
                for t in ['T1','T2','T3','T4']:
                    a=next(r for r in master if r['corpus']==name and r['tokenization']==t);b=next(r for r in master if r['corpus']==q and r['tokenization']==t)
                    output.append(dict(control=name,query=q,tokenization=t,control_h0=float(a['h0']),query_h0=float(b['h0']),control_h1=float(a['h1']),query_h1=float(b['h1']),control_h2=float(a['h2']),query_h2=float(b['h2']),h2_difference=float(a['h2'])-float(b['h2']),word_length_W1=wasserstein_distance(lens(corpus(name)),lens(qr))))
    table(EXT/'report/C15_A_B_fit.csv',output)

def geometry():
    from src.parse_ivtff import edit_distance
    outputs=read(ROOT/'report/embedding_geometry.csv');p5=json.loads((ROOT/'configs/phase5.json').read_text())
    for job in sorted((EXT/'runs/models').glob('C8_published_clean-T3-*-p0-*')):
        if not (job/'embeddings.npz').exists():continue
        r=json.loads((job/'metrics.json').read_text());spec=json.loads((job/'config.json').read_text());emb=np.load(job/'embeddings.npz')['embedding']
        selected=corpus('C8_published_clean');allocation=split('C8_published_clean');counts=Counter(w for row in selected if allocation[row['folio']]=='train' for w in row['text_eva'].split())
        ids=[i for i,w in enumerate(spec['vocabulary']) if i>=3 and counts[w]>=3];ids.sort(key=lambda i:(-counts[spec['vocabulary'][i]],spec['vocabulary'][i]))
        matrix=emb[ids];matrix/=np.maximum(np.linalg.norm(matrix,axis=1,keepdims=True),1e-12);qn=min(500,len(ids));cos=matrix[:qn]@matrix.T
        for i in range(qn):cos[i,i]=-np.inf
        neighbors=np.argsort(-cos,axis=1)[:,:5];n=edit=stem=both=randedit=randstem=0;rng=random.Random(r['seed'])
        for i in range(qn):
            w=spec['vocabulary'][ids[i]]
            for j in neighbors[i]:
                v=spec['vocabulary'][ids[int(j)]];p=len(os.path.commonprefix([w,v]));e=edit_distance(w,v)==1;s=p>=3 and p>=min(len(w),len(v))/2;n+=1;edit+=e;stem+=s;both+=e and s
                candidates=[k for k in range(len(ids)) if k!=i and abs(len(spec['vocabulary'][ids[k]])-len(v))<=1];k=rng.choice(candidates or [k for k in range(len(ids)) if k!=i]);u=spec['vocabulary'][ids[k]];randedit+=edit_distance(w,u)==1;p=len(os.path.commonprefix([w,u]));randstem+=p>=3 and p>=min(len(w),len(u))/2
        outputs.append(dict(corpus=r['corpus'],architecture=r['architecture'],seed=r['seed'],pairs=n,edit1_fraction=edit/n,prefix_family_fraction=stem/n,both_fraction=both/n,length_matched_random_edit1_fraction=randedit/n,length_matched_random_prefix_fraction=randstem/n))
    table(EXT/'report/embedding_geometry.csv',outputs)

def mixture_tracking(assocs):
    output=[]
    for name,method,k,target in sorted({(r['corpus'],r['method'],r['k'],r['target']) for r in assocs}):
        rs=[r for r in assocs if (r['corpus'],r['method'],r['k'],r['target'])==(name,method,k,target)]
        numeric=lambda key:[float(r[key]) for r in rs if r.get(key) not in ['',None]]
        ami=numeric('line_AMI');leaf=numeric('leaf_AMI');ps=numeric('permutation_p')
        support=numeric('pure_metadata_leaves');passing=sum(p<=.05 for p in ps)
        output.append(dict(corpus=name,method=method,k=k,target=target,seeds=len(rs),median_line_AMI=statistics.median(ami) if ami else None,
            median_leaf_AMI=statistics.median(leaf) if leaf else None,median_pure_leaves=statistics.median(support) if support else 0,
            seeds_leaf_p_le_05=passing,tracking='stable marginal association' if passing>=4 else 'unresolved / no stable calibrated association',
            warning='post-hoc reporting synopsis at .05 in >=4 seeds; unadjusted covarying metadata; no unique cause, no latent-language qualification'))
    table(EXT/'report/mixture_metadata_tracking.csv',output);return output

def partial_plot(partial):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    zg=next(r for r in read(ROOT/'report/line_position_gain.csv') if r['corpus']=='ZL_running' and r['tokenization']=='T1' and r['architecture']=='lstm')
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    for L,R,version in sorted({(r['sequence_length'],r['slot_rigidity'],r['corpus'].rsplit('_',1)[1]) for r in partial}):
        rs=sorted([r for r in partial if (r['sequence_length'],r['slot_rigidity'],r['corpus'].rsplit('_',1)[1])==(L,R,version)],key=lambda r:float(r['fraction_requested']))
        xs=[float(r['fraction_requested']) for r in rs]
        values=[[float(r['h2_distance'])/max(float(r['h2_band']),1e-12) for r in rs],[float(r['word_length_W1'])/max(float(r['word_length_band']),1e-12) for r in rs],[abs(float(r['position_gain_mean'])-float(zg['gain_mean']))/max(float(r['gain_band']),1e-12) for r in rs]]
        for ax,ys in zip(axes,values):ax.plot(xs,ys,'o-' if version=='clean' else 's--',label=f'L{L} R{R} {version}',markersize=3)
    for ax,title in zip(axes,['Entropy distance / band','Word-length W1 / band','Position-gain distance / band']):
        ax.axhline(1,color='black',linewidth=.7);ax.set_title(title);ax.set_xlabel('Requested fraction of sign types decomposed');ax.set_ylabel('Normalized distance');ax.grid(alpha=.15)
    axes[-1].legend(fontsize=7);fig.suptitle('Exploratory partial decomposition; all three distances must be ≤1');fig.savefig(EXT/'report/C12_partial_sweep.png',dpi=150);plt.close(fig)

def build():
    with threadpool_limits(2):fingerprints();c15_comparisons();geometry()
    master=read(EXT/'report/master_metrics.csv');qual=read(EXT/'report/C14_mixture_qualification.csv');mix=read(EXT/'report/mixture_summary.csv');assocs=read(EXT/'report/mixture_associations.csv');tracking=mixture_tracking(assocs)
    entropy=[dict(corpus=r['corpus'],tokenization=r['tokenization'],h0=float(r['h0']),h1=float(r['h1']),h2=float(r['h2'])) for r in master if r['tokenization'] in ['T1','T2'] and (r['corpus']=='ZL_running' or r['corpus'].split('_')[0] in ['C4','C5','C6','C7','C8','C9','C12'])]
    table(EXT/'report/T1_T2_entropy_comparison.csv',entropy)
    conv=json.loads((EXT/'report/CONVERGENCE_STATUS.json').read_text());partial=read(EXT/'report/C12_partial_sweep.csv');partial_plot(partial);classifier=json.loads((EXT/'report/classifier_exclude_C10_C11_result.json').read_text())
    assignments=read(EXT/'report/classifier_exclude_C10_C11_assignments.csv');summary=[]
    for name,weight in sorted({(r['corpus'],r['class_weight']) for r in assignments}):
        current=[r for r in assignments if (r['corpus'],r['class_weight'])==(name,weight)];counts=Counter(r['assigned_control'] for r in current)
        summary.append(dict(query=name,class_weight=weight,chunks=len(current),assignments=json.dumps(dict(counts))))
    table(EXT/'report/classifier_exclude_C10_C11_query_summary.csv',summary)
    baseline=read(EXT/'report/natural_baseline_metrics.csv');bs=[]
    for t in ['T1','T2','T3','T4']:
        z=next(r for r in master if r['corpus']=='ZL_running' and r['tokenization']==t)
        for family in ['Wikipedia','Historical']:
            selected=[r for r in baseline if r['tokenization']==t and r['family'].lower().startswith(family.lower())]
            if not selected:continue
            vals=[float(r['h2']) for r in selected];bs.append(dict(tokenization=t,family=family,views=len(vals),ZL_h2=float(z['h2']),baseline_min=min(vals),baseline_median=statistics.median(vals),baseline_max=max(vals),views_at_or_below_ZL=sum(v<=float(z['h2']) for v in vals)))
    table(EXT/'report/natural_baseline_entropy_summary.csv',bs)
    c13=[dict(corpus=r['corpus'],line_edge_MI=float(r['mi_glyph_line_word_edge']),word_edge_MI=float(r['mi_glyph_word_edge'])) for r in master if r['corpus'] in ['ZL_running','C1_clean','C13_clean','C13_noise'] and r['tokenization']=='T1']
    kh=read(EXT/'c16_kh_ranking_v2/report/v1_v2_side_by_side.csv');khbrief=[r for r in kh if r['version']=='clean']
    topic=read(EXT/'report/within_cell_probe_summary.csv');ztopic=[r for r in topic if r['corpus']=='ZL_running']
    st='''# Phase 6 report

This is a separate extension of the accepted Phase 4/5 checkpoint. Original reports, classifiers, models and the C16-KH v1 failure are preserved. All fits run locally. The batch stops here. It does not translate the manuscript or establish a historical generator.

## Data, matching and noise

Primary ZL running text has 3,996 lines, 34,509 words and 172,280 nonspace EVA characters. Labels are separate. H is the sole alternate transcriber. Unknown Currier language is excluded from A/B comparisons. Real hand and paragraph metadata are ZL-only. Controls match words first, with the EVA-character ratio separately reported in [size_matching.csv](size_matching.csv). C13 and C17 retain authentic/sample-size limits rather than repeat text.

The symmetric transcription-disagreement channel is approximately 4.27%: substitution .0215955, insertion .0105657 and deletion .0105657 per input character. It includes spaces, not newlines. These are sensitivity rates from disagreement, not estimated true scribal-error probabilities. Clean and noisy results are separate. See [decisions](../DECISIONS.md), [execution amendments](../AMENDMENTS.md), and [pinned provenance](../SOURCES.md).

## Entropy and line layout

Our h0 is single-token Shannon entropy, h1 conditions on one predecessor and h2 on two. Lindemann/Bowern's h0 is Hartley entropy, and their h1/h2/h3 correspond in order to our h0/h1/h2. Tokenization, source size and boundary estimators still differ. The requested T1/T2 comparison is available in full as [CSV](T1_T2_entropy_comparison.csv).

'''
    st+=mdtable(entropy,['corpus','tokenization','h0','h1','h2'])
    st+='\nThe 294-language comparison includes all 24 historical views with their 18 work-family identities. They are not 318 independent language/work observations. Prefix matching and 200-word sensitivity blocks extend the published comparison rather than exactly reproduce its estimator.\n\n'+mdtable(bs,list(bs[0]) if bs else ['family'])
    st+='\nC13 retains its own manuscript line breaks. C1 and ZL are shown alongside its line-edge MI:\n\n'+mdtable(c13,['corpus','line_edge_MI','word_edge_MI'])
    st+='\nT4 coverage includes every token/type and lossless fallback, in [T4_coverage.csv](T4_coverage.csv) and [baseline coverage](natural_baseline_T4_coverage.csv). Native-spelling coverage is separate from pipeline relabeling. Zattera coverage is grammar conformity, not evidence of meaning.\n'
    st+='\n## Fingerprints and classifier amendment\n\n![Control-fitted PCA](fingerprint_pca.png)\n\n![Natural-baseline PCA](natural_baseline_pca.png)\n\nFull feature-space distances, not visual PCA proximity, define [nearest controls](fingerprint_nearest.csv). Queries do not fit the scaler or projection. The expanded classifier excludes C10/C11 in its primary rerun; an all-family Phase 6 comparison is separate, and the original Phase 5 run is untouched. C8 uses the published implementation; legacy C8 is retained separately. Exploratory partial C12 settings never train this classifier. Source-ancestry purging and unsupported-fold support are recorded in the [receipts](classifier_exclude_C10_C11_purge_receipts.json).\n\n'
    st+=mdtable(summary,['query','class_weight','chunks','assignments'])
    st+=f'\nThe ancestry-purged classifier has {classifier["estimable_folds"]}/{classifier["folds"]} estimable folds and {classifier["test_chunks"]} test chunks. Accuracy is {classifier["accuracy"]}, balanced accuracy {classifier["balanced_accuracy"]}. Scores are uncalibrated conditional membership among these specific control families. Variant counts affect class priors; balanced-class sensitivity is reported separately. Published C8 and C15 retain manuscript-informed design dependence. No assignment identifies a historical mechanism.\n'
    st+='\n## Fixed-budget and convergence comparisons\n\nThe original 96-step results remain in [model_summary.csv](model_summary.csv). The headline transformer T1/T2 rerun uses validation-only early stopping, baseline/position conditions and five seeds. C12 uses the best original full-grid point, with its own matched 96-step comparators. All C15/C18 variants and clean/noise conditions remain separate. See [paired comparison](convergence_comparison.csv), [per-run curves and metrics](convergence_runs.csv), and [converged position gains](converged_position_gain.csv).\n\n'
    st+=mdtable([conv],['status','runs','unfinished_fraction','literal_endpoint_best_fraction','final_cap'])
    st+='\nPlateau qualification is conditional on the registered validation/optimizer rule. The learning-rate schedule also changes. It does not prove a global optimum or turn a small gain into a meaningful one. Compare seed variation and the ZL/H transcription sensitivity. A/B fits for every Naibbe source/deck are reported independently in [C15_A_B_fit.csv](C15_A_B_fit.csv).\n'
    st+='\n## Partial C12 decomposition\n\nThe six requested fractions cross the best two distinct old grid settings, selected before new scores. Type and occurrence-weighted realized fractions, code collisions, entropy, word-length W1 and position gains are in [C12_partial_sweep.csv](C12_partial_sweep.csv). This is exploratory follow-up to the preserved 0/36 full-decomposition null.\n\n'
    st+='![Exploratory partial C12 sweep](C12_partial_sweep.png)\n\n'
    st+=f'{sum(r["matches_all_three"]=="True" for r in partial)}/{len(partial)} clean/noise rows meet all three empirical bands. These bands are not a formal equivalence test. The sweep retains the original fixed 96-step LSTM instrument; it is distinct from headline transformer convergence.\n'
    st+='\n## Mixtures and recovery gate\n\nC14 qualification ran before manuscript mixture interpretation. Whole-line mixtures recover the paragraph and label/text splits, but the word/phrase mixed-membership companions fail the registered general recovery gate. This failure is retained. Manuscript results at those scales cannot exclude macaronic mixing or support a qualified latent-language interpretation.\n\n'
    st+=mdtable([r for r in qual if r['k']=='2' and (r['method']=='line' or r['method']=='word_membership')],['corpus','method','k','recovery_status','recovery_balanced_accuracy_mean','median_seed_ARI'])
    st+='\nAll 1/2/3-component runs and five-seed summaries are supplied in [mixture results](mixture_results.csv), [stability/gain summary](mixture_summary.csv), [assignments](mixture_assignments.csv), and [metadata associations](mixture_associations.csv). The split flag combines held-out coding gain, occupancy and seed ARI; it does not name languages. Companion coding uses causal soft-count prequential membership. It is not the exact integrated Dirichlet mixture marginal and its denominator is not the neural model\'s nonspace BPC.\n\n'
    st+=mdtable([r for r in mix if r['corpus'] in ['ZL_running','LSI_H_running'] and r['method']=='line'],['corpus','method','k','gain_mean','gain_sd','median_seed_ARI','split_emerges'])
    st+='\nMetadata association estimates remain unadjusted and covarying. Unknown language is excluded, real hand is ZL-only, and leaf permutations retain support limits. The following stable/unresolved wording is a post-hoc reporting synopsis of whether unadjusted leaf p≤.05 in at least four seeds, not a registered additional discovery gate. A split associated with several targets does not uniquely track any one cause. Absence of a calibrated association is not proof of no relationship.\n'
    st+=mdtable([r for r in tracking if r['method']=='line'],['corpus','k','target','median_line_AMI','median_leaf_AMI','median_pure_leaves','seeds_leaf_p_le_05','tracking'])
    st+='\n## Within-cell topics and fake sections\n\nBoth LDA topic features and character TF-IDF probes are fit within one ZL scribe × known-Currier cell, with held-out leaves. The same methods are run on every generator/control with independent fake page sections; 20 fake assignments cycle five feature seeds. These are labels independent of text, not a model of deliberate generator changes by section. Missing classes/splits are retained as not estimable. Topic strings are uninterpreted.\n\n'
    st+=mdtable(ztopic,['cell','method','replicates','mean_accuracy','mean_majority','mean_balanced_accuracy'])
    st+='\nFull support and null comparisons are in [probe rows](within_cell_section_probes.csv) and [summary](within_cell_probe_summary.csv). Published C8 word-embedding geometry uses the original edit-distance/prefix and matched-random comparisons in [embedding_geometry.csv](embedding_geometry.csv); prefix similarity alone is not morphology.\n'
    st+='\n## C16 dictionary null and C16-KH rank-only v2\n\n[Dictionary hit rates](C16_dictionary_hits.csv) and [100-map null summaries](C16_dictionary_null_summary.csv) apply the same exact-anagram and dictionary-vowel-fill routines to C16 and C9/C11. Clean/noise, vowel variants and token/type/length strata remain separate. Unsupported symbols fail. Dictionary hits, especially short-word hits, do not establish a decoding.\n\nThe separately declared C16-KH v2 uses existing v1 decoded lines and the original LM, exactly as selected by the user. It omits UNK targets, requires ≥60% known tokens, retains original token history and averages known-target log probabilities. No key or model was refit, and no corrected-scorer artifact was imported. The mechanical rule passes and v1 inputs remain unchanged. This is not qualification of Hebrew coherence or of the original LM.\n\n'
    st+=mdtable(khbrief,['arm','source','eligible_identities','actual_n','mean_words','minimum_known_fraction','unknown_fraction','v1_unknown_fraction'])
    st+='\nThe 200-item clean-Tanakh blind export has 100 ZL and 25 each C1/C9/C11/C17, all eligible. It includes 97 repeated decoded strings, limiting independent rating information. Ratings are blank. The source key remains separately sealed. v1/v2 raw scores are on different scales and are not directly comparable. Equal-N null comparisons remain descriptive; calibrated p-values were not estimated. See [v1/v2 table](../c16_kh_ranking_v2/report/v1_v2_side_by_side.csv) and [blind rater package](../c16_kh_ranking_v2/blind/rater-only.zip).\n'
    st+='''
## Relation to prior work

| Result | Prior work | Relation and scope |
|---|---|---|
| Entropy across Wikipedia/historical corpora | [Lindemann & Bowern](https://arxiv.org/abs/2010.14697) | Extension using their supplied corpora, size sensitivity and this pipeline's boundaries/tokenizations. Not an exact estimator replication. Compare notation before any disagreement claim. |
| Human-gibberish comparison | [Gaskell & Bowern 2022](https://ceur-ws.org/Vol-3313/paper4.pdf) | Extension on the 38 supplied documents, preserving short samples and participant groups. Aggregate resemblance or classifier assignment does not distinguish meaning from its absence. |
| Published self-citation C8 | [Timm & Schinner code](https://github.com/TorstenTimm/SelfCitationTextgenerator) | Replication of the available executable procedure, followed by a documented prefix/reflow extension. Legacy simplified C8 remains separate. Generator resemblance is not authorship evidence. |
| Bigraph/addB C18 | [Bowern & Gaskell 2022](https://ceur-ws.org/Vol-3313/paper6.pdf) | Replicates the specified manipulation, extends it to C1 Latin, controls/noise and neural instruments. Not an exact reproduction of the original numerical setting. |
| Slot grammar T4 | [Zattera v4j](https://github.com/mzattera/v4j) | Port of documented grammar with every-control coverage and lossless fallback. Extends model measurement. Grammar is manuscript-derived, so coverage is not an independent test of language. |
| Naibbe C15 | [Greshko 2025](https://doi.org/10.1080/01611194.2025.2566408) | Replicates original author-code/table procedure with documented I/O/RNG adaptation and common-noise amendment. Extends to these Latin/Italian sources and separate A/B comparisons. Does not fit a fresh cipher to Voynich. |
| Alphagrams and vowel-fill matching | Historical alphabetization proposals and the preserved C16-KH v1 experiment | Extension with source-known positives and C9/C11 null calibration. Ranking v2 is a post-failure amendment, not an independent replication or repair of v1. Dictionary matches do not contradict the preserved coherence failure. |
| C12 partial redundancy | Preserved Phase 5 0/36 null | Explicit exploratory extension. New parameter points cannot retrospectively change the original null or become prospective confirmation. |
| Line/word/phrase mixtures | Known-source C14 qualification | New method calibration. Paragraph-scale success is retained alongside failed finer-scale recovery. Manuscript clustering does not by itself establish several languages. |
| Topics within scribe/language cells | Prior statistical section/topic analyses | Extension controlling these measured cells and adding fake-section controls. Sparse support, correlated metadata and uninterpreted topics prevent semantic conclusions. |
| Classifier/convergence amendment | Accepted Phase 4/5 instruments | Sensitivity extensions. Removing C10/C11 changes the comparison universe; training longer changes optimization. Neither alteration erases old outputs or identifies a historical mechanism. |

No result is called a contradiction of a cited study without matched methods, samples and estimators. Procedural replication and a numerical extension are distinguished throughout.

## What this does NOT show

No translation, decipherment, text meaning, historical shorthand identity, manuscript authorship, or proof of language/gibberish follows from these measurements. Transcription, alphabet decomposition, sample length, layout, manuscript-informed controls and correlated metadata affect the instruments. Short human samples, exploratory grids, failed recovery gates, unknown metadata, uncalibrated class scores, optimizer-dependent plateaus and unfilled human ratings remain visible. The accepted Phase 4/5 limitations still apply.

The original [Phase 5 report](../../../report/REPORT.md), surprise maps, label comparisons, original probes and failed controls remain intact. Verification of this batch is in [PHASE6_VERIFICATION.json](PHASE6_VERIFICATION.json).
'''
    (EXT/'report/REPORT.md').write_text(st,encoding='utf-8')
if __name__=='__main__':build()
