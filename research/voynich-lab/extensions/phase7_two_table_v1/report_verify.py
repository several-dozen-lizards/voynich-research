from common import *
import numpy as np
def main():
    verify_registration();assert json.loads((R/'PROBE_PROGRESS.json').read_text())['status']=='COMPLETE';assert json.loads((R/'PROBE_REPLAY_QUALIFICATION.json').read_text())['status']=='PASS'
    freeze=json.loads((R/'TABLES_FROZEN.json').read_text());assert all(sha(R/p)==h for p,h in freeze['files'].items())
    evaluated=json.loads((R/'HELD_OUT_EVALUATED.json').read_text());assert all(sha(R/p)==h for p,h in evaluated['files'].items())
    snapshot=json.loads((R/'INPUT_SNAPSHOT.json').read_text());drift=[p for p,h in snapshot['original_lab_hashes'].items() if sha(LAB/p)!=h];holds=[p for p,h in snapshot['C16_hold_hashes'].items() if sha(Path(p))!=h];assert not drift and not holds
    probes=read(R/'probes.csv');fps=read(R/'fingerprints.csv');ovs=read(R/'vocabulary_overlap.csv');models=read(R/'models.csv');sp=split();meta=metadata();chosen=freeze['chosen']
    assert len(models)==30 and len(probes)==155 and len(fps)==279 and len(ovs)==93
    receipts=read(R/'ENCODING_RECEIPTS.csv');page_order=list(dict.fromkeys(x['folio'] for x in meta));position=0;intervals={}
    for page in page_order:
        width=2*sum(x['word_slots'] for x in meta if x['folio']==page);intervals[page]=(position,position+width);position+=width
    for r in receipts:assert (int(r['source_start']),int(r['source_stop']))==intervals[r['page']]
    # Retained raw metrics and rows allow independent recomputation of test length distances.
    from scipy.stats import wasserstein_distance
    details=json.loads((R/'fingerprint_details.json').read_text());checks=[]
    for f in fps:
        if f['split']!='test':continue
        a=details[f"{f['corpus']}:s{f['seed']}:test:{f['subset']}"]['hist'];b=details[f"ZL:s1729:test:{f['subset']}"]['hist'];w=wasserstein_distance([int(k) for k in a],[int(k) for k in b],list(a.values()),list(b.values()));assert math.isclose(w,float(f['word_length_W1']),abs_tol=1e-12,rel_tol=1e-12);checks.append(dict(corpus=f['corpus'],seed=f['seed'],subset=f['subset'],W1=w))
    sums=[]
    for name in ['ZL','C1_two','C1_single','C2_two','C2_single','C9_two','C9_single']:
        for label in ['A','B']:
            rs=[f for f in fps if f['corpus']==name and f['split']=='test' and f['subset']==label]
            row=dict(corpus=name,subset=label,seeds=len(rs))
            for key in ['h2','h2_distance','word_length_W1','identical','edit1','identical_difference','edit1_difference','words','types']:
                values=[float(r[key]) for r in rs];row[key+'_mean']=statistics.mean(values);row[key+'_sd']=statistics.stdev(values) if len(values)>1 else 0.
            sums.append(row)
    table(R/'TEST_FINGERPRINT_SUMMARY.csv',sums)
    ps=[]
    for name in ['ZL','C1_two','C1_single','C2_two','C2_single','C9_two','C9_single']:
        row=dict(corpus=name)
        for target,scope,key in [('currier_lang','all','AB'),('section','all','section'),('section','AB_only_baseline','section_AB_baseline')]:
            rs=[r for r in probes if r['corpus']==name and r['target']==target and r['scope']==scope];assert len(rs)==(1 if name=='ZL' else 5)
            for metric in ['accuracy','balanced_accuracy','majority_baseline'] if key!='section_AB_baseline' else ['accuracy']:
                vals=[float(r[metric]) for r in rs if r.get(metric) and r['status']=='PASS'];row[key+'_'+metric+'_mean']=statistics.mean(vals) if vals else None;row[key+'_'+metric+'_sd']=statistics.stdev(vals) if len(vals)>1 else 0.
        ps.append(row)
    table(R/'PROBE_SUMMARY.csv',ps)
    deltas=[]
    for family in ['C1','C2','C9']:
        for seed in SEEDS:
            for target in ['currier_lang','section']:
                a=next(r for r in probes if r['corpus']==family+'_two' and int(r['seed'])==seed and r['target']==target and r['scope']=='all');b=next(r for r in probes if r['corpus']==family+'_single' and int(r['seed'])==seed and r['target']==target and r['scope']=='all');deltas.append(dict(family=family,seed=seed,target=target,two_minus_single_accuracy=float(a['accuracy'])-float(b['accuracy'])))
    table(R/'PAIRED_PROBE_DIFFERENCES.csv',deltas)
    lines=['# Phase 7: two-table verbose cipher A/B test','', 'Training-only fitting and chosen-table freeze preceded this held-out evaluation. This is a registered retrospective extension: the historical held-out corpus had been examined in earlier phases. Naibbe tables were developed using Voynich statistics and are NOT blind controls. No translation or historical identification claim.','', '## Selected table settings','', '| Plaintext/control | A setting | B setting | Single/unknown setting | Same A/B? |','|---|---|---|---|---|']
    for family,settings in chosen.items():lines.append('| '+family+' | '+' | '.join(settings[k]['id'] for k in ['A','B','pooled'])+' | '+str(settings['A']['id']==settings['B']['id'])+' |')
    lines+=['','D52/D78 identify the author base weight vector, followed by the one-table weight adjustment and respacing numerator /36. Exact six-table weights and totals are in CHOSEN_TABLES.json; adjusted decks need not contain52/78 cards. G IDs identify original C9 shuffled cyclic-table arrangements. Encoder fitting used h2, W1, exact repetition and edit1 repetition, scaled by training candidate variation. Probes and vocabulary overlap did not select tables.','', '## Test fingerprints, mean across five paired seeds','', '| Corpus | Subset | h2 | abs delta h2 | W1 | Exact repetition | Edit1 repetition |','|---|---|---:|---:|---:|---:|---:|']
    for s in sums:lines.append(f"| {s['corpus']} | {s['subset']} | {s['h2_mean']:.6f} | {s['h2_distance_mean']:.6f} | {s['word_length_W1_mean']:.6f} | {s['identical_mean']:.3%} | {s['edit1_mean']:.3%} |")
    lines+=['','ZL is one fixed target and one cached1729 model; its displayed seed SD is0, not an estimate of target uncertainty. Full per-seed values, SDs, signed repetition differences, supports and A/B differences are in fingerprints.csv, TEST_FINGERPRINT_SUMMARY.csv and A_B_differences.csv. W1 compares each generated subset only with its matching held-out ZL subset.','', '## Held-out line probes','', '| Corpus | A/B accuracy mean +/- SD | A/B balanced accuracy | Section accuracy mean +/- SD | Section majority baseline | Section baseline using A/B alone |','|---|---:|---:|---:|---:|---:|']
    for p in ps:lines.append(f"| {p['corpus']} | {p['AB_accuracy_mean']:.3%} +/- {p['AB_accuracy_sd']:.3%} | {p['AB_balanced_accuracy_mean']:.3%} | {p['section_accuracy_mean']:.3%} +/- {p['section_accuracy_sd']:.3%} | {p['section_majority_baseline_mean']:.3%} | {p['section_AB_baseline_accuracy_mean']:.3%} |")
    lines+=['','These are the same Transformer/T1 baseline96-step representation and scaler/logistic instruments on all arms. Encoder/model seeds are paired, so their separate variability is not identifiable here. The primary1729 cached ZL model reproduces the old94.02% A/B and62.30% section probe exactly; section majority baseline61.50%. No approximately94% threshold was used to tune anything. Validation labels choose logistic C only; encoder settings use training pages only. Within-A/B section probes, class support and selected C are retained in probes.csv; rare/unseen sections and A/B-section confounding limit interpretation.','', '## Held-out A/B vocabulary overlap','', '| Corpus | Jaccard mean | A tokens covered by B vocabulary | B tokens covered by A vocabulary |','|---|---:|---:|---:|']
    for name in ['ZL','C1_two','C1_single','C2_two','C2_single','C9_two','C9_single']:
        rs=[r for r in ovs if r['corpus']==name and r['split']=='test'];means={k:statistics.mean(float(r[k]) for r in rs) for k in ['type_Jaccard','A_token_coverage_by_B','B_token_coverage_by_A']};lines.append('| '+name+' | '+' | '.join(f'{means[k]:.3%}' for k in means)+' |')
    lines+=['','## Scope and limitations','', 'One sequential Latin stream and one Italian stream were used, with disjoint fixed character chunks per page and no plaintext repetition/padding. The paired two/single arms receive identical source chunks. Exact ciphertext word-slot layout is imposed and native Naibbe alphabets are shared across A/B. Word resegmentation and discarded suffixes mean this is not source syntax preservation. Unknown A/B pages receive pooled settings; all page labels are inherited metadata.','', 'The C9 two-arrangement null keeps the same original512-cell word inventory and changes shuffled cyclic order/offset; it has less lexical flexibility than the Naibbe family. Candidate search budget is matched but mechanism/expressivity is not. The primary clean-only experiment adds no synthetic transcription noise.','', 'Both table settings, candidate losses, zero-scale fallbacks, source/code/input hashes, generation spans, five-seed metrics and paired two-minus-single probe differences are retained. Prior model/encoder failures are not erased. Ninety-six-step models are fixed-budget instruments and may still be learning. Descriptive point estimates and seed SDs are not equivalence or significance tests.','', 'Original phases, C12 terminal files and C16 holds remain hash-identical. No new C12 sweep, C16 decode/score or ZL language-model training occurred. New target fingerprints/probes are confined to this explicitly requested Phase7 test. Stop; no parameter rescue or follow-up sweep is scheduled.']
    (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    status=dict(status='COMPLETE',protocol_before_fit=True,tables_frozen_before_held_out=True,new_control_models=30,reused_ZL_models=1,ZL_probe_replay='EXACT_PASS',test_fingerprint_rows=len(checks),original_drift=drift,C16_hold_drift=holds,new_C12_sweeps=0,new_C16_scores=0,translation_claims=False)
    dump(R/'VERIFICATION.json',{**status,'independent_W1_checks':checks,'plaintext_intervals_disjoint':True,'all_source_hashes_pass':True});dump(R/'STATUS.json',status)
    dump(R/'OUTPUT_HASHES.json',{str(p.relative_to(R)):sha(p) for p in R.iterdir() if p.is_file() and p.name!='OUTPUT_HASHES.json'})
    print(json.dumps(status,indent=2));print(json.dumps(ps,indent=2))
if __name__=='__main__':main()
