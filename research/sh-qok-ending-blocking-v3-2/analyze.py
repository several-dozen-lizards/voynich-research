"""v3.2 frozen retrospective descriptive ending-family check; no inference."""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction
from datetime import datetime,timezone
import csv,json,hashlib,sys,re

R=Path(__file__).resolve().parent;P=R.parent;V=P/'sh-qok-context-map-v3'
FAMILIES=['eey','edy','ey','y','other'];BLOCK=['eey','ey'];REST=['edy','y','other']
CONTEXTS={'C1':'hand2 bath','C2':'hand2 botanical','C3':'hand2 Rosettes','C4':'hand3 starred','C5':'hand3 botanical','C6':'hand1 botanical','C7':'hand1 recipes'}
POSTHOC=['C1','C4']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def phase(n,**kw):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=n,utc=datetime.now(timezone.utc).isoformat(),**kw))+'\n')

def freeze():
    assert not (R/'FREEZE.json').exists()
    # Metadata/schema access only: do not inspect family-level numerical values.
    old=P/'sh-qok-ending-qualification-reed-v94/RESULTS.json'
    records=json.loads(old.read_text());evidence=[]
    for rec in records:
        if rec['view']!='ending_family':continue
        cells=rec['observed'].get('cells',[])
        assert cells and {'sh_qok','ch_qok','delta','weight','key'}.issubset(cells[0])
        evidence.append(dict(source=str(old),context='C1' if rec['section']=='Balneological' else 'C4',section=rec['section'],reading=rec['reading'],view=rec['view'],schema=list(cells[0])))
    estimates=json.loads((V/'PART-B-ESTIMATES.json').read_text())
    # v3 aggregate saved support has no family outcome numerators or rates.
    schemas={}
    for key,rec in estimates.items():
        if rec.get('context') not in CONTEXTS:continue
        schemas[key]={}
        for view in ['aggregate','available']:
            s=rec[view]['support'].get('strata',[])
            assert all(set(z)<= {'folio','family','sh','ch','V'} for z in s)
            schemas[key][view]=dict(estimate_keys=list(rec[view]),stratum_keys=list(s[0]) if s else [])
    precheck=dict(answer='YES',outside_Rosettes_previously_saved_family_breakdowns=['C1 bath','C4 starred'],posthoc_excluded_contexts=POSTHOC,
        evidence=evidence,v3_saved_estimate_schemas=schemas,
        no_additional_saved_family_outcome_breakdown_found=['C2','C5','C6','C7'],known_hypothesis_origin='C3 Rosettes, already explored in this chat',
        operational_definition='Saved inspectable outcome breakdown by family or folio x family, such as arm qok counts and delta. Event ledgers alone and outcome-blind family support do not constitute a displayed family breakdown. Arithmetic inside an MH aggregate necessarily computes stratum contrasts; those transient intermediate values were not saved as family outcome summaries by v3/v3.1.',
        scope='Relevant saved sh/qok runs and source schemas in this workspace, notably v94, attempt C and exploratory subsets, context-transfer A/B, v3/v3.1 and qualification follow-up. This does not certify that no unrelated external session has ever examined a family.',
        caveat='All v3 contexts remain retrospective exposed/uncertified regardless of this narrower saved-breakdown audit. C1/C4 are discovery and post-hoc. C3 remains known-origin E. Counts excluding C3 are also supplied.')
    save('PRECHECK.json',precheck)
    save('PROTOCOL.json',dict(classification='RETROSPECTIVE DESCRIPTIVE; exploratory origin; no p-values',original_amendment_sha256=sha(R/'ORIGINAL-AMENDMENT.md'),contexts=CONTEXTS,readings=['H','F'],families=FAMILIES,
        source='Existing v3/v3.1 EVENTS.csv; original event population and availability flags preserved. No primary engine or result altered.',
        groups=dict(blocking=BLOCK,comparison=REST),views=['all','available'],
        family_rows='Each family: raw next-qok event counts/rates separately after sh/ch; MH effect weighted over folio x family strata; V and share of total context V; supported zero-qok strata (both prefixes present), plus all zero-qok strata count. All rows retained even below20 events; label descriptive support explicitly.',
        estimability='Literal strict20-event rule: each original family eey,edy,ey,y,other must have >=20 eligible events within context x reading x view before context can enter either prediction denominator. No pooling of sparse individual families to rescue eligibility. Prediction(a) further requires nonzero pooled group denominators; prediction(b) also requires positive MH weight in both grouped sets. Arm rates absent => unavailable, not0.',
        prediction_a='Raw qok rate after pooled sh/ch eey+ey strictly lower than pooled sh/ch edy+y+other; these are event-weighted rates, not MH effects.',
        prediction_b='abs(MH gap_eey+ey) < 0.5 * MH gap_edy+y+other, in percentage points, strictly. Right-hand comparison uses the signed positive-direction effect as written; a nonpositive comparison effect cannot satisfy the inequality. MH grouping remains folio x originalfamily, never merges endings before stratification.',
        headline='For each reading and each view, count whether(a)/(b) holds among separately estimable contexts, excluding prior outside-Rosettes family breakdowns C1/C4. C3 remains known-origin and identified; additionally report counts excluding C3. No independence/confirmation interpretation.',
        sensitivity='For every context x reading x view, recompute MH after dropping whole folio x family strata with zero qok outcomes in both arms. Keep all events of surviving strata, both arms. Record both supported and unsupported zero strata, removed V, event counts, baseline and exact agreement with v3 estimates. This is outcome-selected denominator removal, not an adjusted primary estimate.',
        inference='No p-values, Holm, intervals, pass/fail, qualification or model fits. Small support and prior selection remain visible. No meanings, grammar/junction or categorical blocking claims.',
        progression='Any broad pattern is at most motivation for a future independently frozen hypothesis; failures outside Rosettes must remain. No future-round protocol is silently frozen by this descriptive calculation.'))
    inputs=[R/'ORIGINAL-AMENDMENT.md',R/'PRECHECK.json',R/'PROTOCOL.json',R/'analyze.py',V/'EVENTS.csv',V/'PART-B-ESTIMATES.json',V/'AMENDMENT-v3.1.json',V/'PROTOCOL.json',V/'analysis.py',old]
    save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in inputs}))
    phase('amendment_and_definitions_frozen',before_family_values_from_EVENTS=True)
    print('Pre-check YES: C1 and C4 previously saved family-level outcomes; excluded from headline. Amendment and definitions frozen.')

def verify_inputs():
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h,('input changed',p)

def grouped(rows):
    out=defaultdict(lambda:[0,0,0,0])
    for row in rows:
        j=0 if row['prefix']=='sh' else 1
        out[row['folio'],row['family']][j]+=1;out[row['folio'],row['family']][2+j]+=row['qok']
    return out

def stats(rows):
    groups=grouped(rows);num=Fraction(0);den=Fraction(0);zero=0;supported=0;zero_all=0
    for ns,nc,a,b in groups.values():
        if a+b==0:zero_all+=1
        if not ns or not nc:continue
        w=Fraction(ns*nc,ns+nc);num+=Fraction(a*nc-b*ns,ns+nc);den+=w;supported+=1
        if a+b==0:zero+=1
    ns=sum(r['prefix']=='sh' for r in rows);nc=len(rows)-ns
    a=sum(r['qok'] for r in rows if r['prefix']=='sh');b=sum(r['qok'] for r in rows if r['prefix']=='ch')
    delta=100*num/den if den else None
    return dict(events=len(rows),sh_events=ns,ch_events=nc,sh_qok=a,ch_qok=b,
        sh_qok_rate=a/ns if ns else None,ch_qok_rate=b/nc if nc else None,
        pooled_qok=a+b,pooled_qok_rate=(a+b)/len(rows) if rows else None,
        MH_effect_points=float(delta) if delta is not None else None,exact_MH_effect_points=str(delta) if delta is not None else None,
        V=float(den),exact_V=str(den),numerator=float(num),total_strata=len(groups),supported_strata=supported,
        zero_qok_both_supported_strata=zero,zero_qok_all_strata=zero_all,
        contributing_folios=sorted({pg for (pg,f),(ns,nc,a,b) in groups.items() if ns and nc}))

def independent(rows):
    # Independently use x/y fields and rates, with ending classifications rederived from origins.
    counts=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        fam=next((s for s in FAMILIES[:-1] if r['origin'].endswith(s)),'other');assert fam==r['family']
        j=1-int(r['x']);assert j==int(r['prefix']=='ch')
        y=int(r['y']);assert y==int(r['follower'].startswith('qok'))==int(r['outcome'])
        z=counts[r['folio'],fam];z[j]+=1;z[2+j]+=y
    num=Fraction(0);den=Fraction(0)
    for ns,nc,a,b in counts.values():
        if ns and nc:
            weight=1/(Fraction(1,ns)+Fraction(1,nc));num+=weight*(Fraction(a,ns)-Fraction(b,nc));den+=weight
    return str(100*num/den) if den else None

def analyze():
    verify_inputs();assert not (R/'FAMILY-ROWS.csv').exists()
    phase('first_new_family_outcome_calculation')
    allrows=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')))
    rows=[]
    for r in allrows:
        if r['context'] not in CONTEXTS or r['reading'] not in ['H','F'] or r['exclusion_reason']:continue
        r=dict(r);r['qok']=int(r['follower'].startswith('qok'))
        assert r['qok']==int(r['outcome'])==int(r['y'])
        av=not r['follower'].startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
        r['is_available']=av;rows.append(r)
    previous=json.loads((V/'PART-B-ESTIMATES.json').read_text());family_rows=[];cells=[];sensitivity=[];checks=0
    for context in CONTEXTS:
        for reading in ['H','F']:
            for view in ['all','available']:
                rr=[r for r in rows if r['context']==context and r['reading']==reading and (view=='all' or r['is_available'])]
                baseline=stats(rr);assert baseline['exact_MH_effect_points']==independent(rr);checks+=1
                old=previous[context+'-'+reading]['aggregate' if view=='all' else 'available']['effect_points']
                assert (old is None and baseline['MH_effect_points'] is None) or abs(old-baseline['MH_effect_points'])<1e-9
                fam_stats={}
                for family in FAMILIES:
                    fr=[r for r in rr if r['family']==family];s=stats(fr)
                    assert s['exact_MH_effect_points']==independent(fr);checks+=1
                    s.update(context=context,context_name=CONTEXTS[context],reading=reading,view=view,family=family,
                        family_20_events=s['events']>=20,context_V_share=s['V']/baseline['V'] if baseline['V'] else None,
                        discovery=context in ['C1','C4'],posthoc=context in POSTHOC,known_origin=context=='C3')
                    family_rows.append(s);fam_stats[family]=s
                block=stats([r for r in rr if r['family'] in BLOCK]);rest=stats([r for r in rr if r['family'] in REST])
                for group,fams in [(block,BLOCK),(rest,REST)]:
                    assert group['exact_MH_effect_points']==independent([r for r in rr if r['family'] in fams]);checks+=1
                sparse=[f for f in FAMILIES if not fam_stats[f]['family_20_events']]
                a_estimable=not sparse and block['events']>0 and rest['events']>0
                b_estimable=a_estimable and block['V']>0 and rest['V']>0
                a_holds=block['pooled_qok_rate']<rest['pooled_qok_rate'] if a_estimable else None
                bg=block['MH_effect_points'];rg=rest['MH_effect_points']
                b_holds=abs(Fraction(block['exact_MH_effect_points']))<Fraction(rest['exact_MH_effect_points'])/2 if b_estimable else None
                cells.append(dict(context=context,context_name=CONTEXTS[context],reading=reading,view=view,discovery=context in ['C1','C4'],posthoc=context in POSTHOC,known_origin=context=='C3',headline_eligible_history=context not in POSTHOC,
                    sparse_families=sparse,family_event_counts={f:s['events'] for f,s in fam_stats.items()},prediction_a_estimable=a_estimable,prediction_a_holds=a_holds,prediction_b_estimable=b_estimable,prediction_b_holds=b_holds,
                    blocked_group=block,comparison_group=rest,baseline=baseline,b_half_comparison_gap=rg/2 if rg is not None else None))
                groups=grouped(rr);drop={key for key,z in groups.items() if z[2]+z[3]==0}
                kept=[r for r in rr if (r['folio'],r['family']) not in drop];remaining=stats(kept)
                assert remaining['exact_MH_effect_points']==independent(kept);checks+=1
                assert abs(remaining['numerator']-baseline['numerator'])<1e-12
                sensitivity.append(dict(context=context,context_name=CONTEXTS[context],reading=reading,view=view,posthoc=context in POSTHOC,discovery=context in ['C1','C4'],known_origin=context=='C3',
                    v3_baseline_effect_points=old,baseline=baseline,zero_qok_strata_removed=len(drop),zero_qok_supported_strata_removed=baseline['zero_qok_both_supported_strata'],
                    removed_events=len(rr)-len(kept),removed_V=baseline['V']-remaining['V'],remaining=remaining,
                    descriptive_shift_points=remaining['MH_effect_points']-baseline['MH_effect_points'] if remaining['MH_effect_points'] is not None and baseline['MH_effect_points'] is not None else None))
    headline={}
    for reading in ['H','F']:
        headline[reading]={}
        for view in ['all','available']:
            headline[reading][view]={}
            for origin_mode in ['requested_excluding_prior_outside_Rosettes_breakdowns','also_excluding_known_Rosettes_origin']:
                cc=[c for c in cells if c['reading']==reading and c['view']==view and not c['posthoc'] and (origin_mode.startswith('requested') or not c['known_origin'])]
                summary={}
                for prediction in ['a','b']:
                    estimable=[c for c in cc if c['prediction_'+prediction+'_estimable']]
                    summary[prediction]=dict(holds=sum(c['prediction_'+prediction+'_holds'] for c in estimable),estimable_contexts=len(estimable),denominator_contexts=[c['context'] for c in estimable],contexts_where_holds=[c['context'] for c in estimable if c['prediction_'+prediction+'_holds']],not_estimable={c['context']:c['sparse_families'] for c in cc if not c['prediction_'+prediction+'_estimable']})
                headline[reading][view][origin_mode]=summary
    save('FAMILY-ROWS.json',family_rows);save('PREDICTIONS.json',cells);save('SENSITIVITY.json',sensitivity);save('HEADLINE.json',headline)
    with (R/'FAMILY-ROWS.csv').open('w',encoding='utf-8',newline='') as f:
        flat=[{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in family_rows]
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    with (R/'ZERO-QOK-STRATA.csv').open('w',encoding='utf-8',newline='') as f:
        records=[]
        for context in CONTEXTS:
            for reading in ['H','F']:
                for view in ['all','available']:
                    rr=[r for r in rows if r['context']==context and r['reading']==reading and (view=='all' or r['is_available'])]
                    for (pg,fam),(ns,nc,a,b) in grouped(rr).items():
                        if a+b==0:records.append(dict(context=context,reading=reading,view=view,folio=pg,family=fam,sh=ns,ch=nc,supported=bool(ns and nc),V=ns*nc/(ns+nc)))
        w=csv.DictWriter(f,fieldnames=['context','reading','view','folio','family','sh','ch','supported','V']);w.writeheader();w.writerows(records)
    verify_inputs()
    save('VERIFICATION.json',dict(status='VERIFIED',eligible_event_rows=len(rows),family_rows=len(family_rows),prediction_cells=len(cells),sensitivity_cells=len(sensitivity),independent_exact_rational_MH_comparisons=checks,
        all_v3_aggregate_and_available_effects_reproduced=True,origin_endings_and_arm_labels_verified=True,available_flags_recomputed=True,zero_qok_removal_preserves_MH_numerator=True,all_frozen_inputs_unchanged=True,inferential_calculations_performed=False))
    phase('descriptive_calculations_complete',independent_checks=checks)
    report()
    print(json.dumps(dict(headline=headline,rows=len(family_rows),checks=checks),indent=2))

def report():
    families=json.loads((R/'FAMILY-ROWS.json').read_text());cells=json.loads((R/'PREDICTIONS.json').read_text());sens=json.loads((R/'SENSITIVITY.json').read_text());headline=json.loads((R/'HEADLINE.json').read_text())
    def fmt(x):return 'NA' if x is None else f'{x:+.3f}'
    def rate(x):return 'NA' if x is None else f'{100*x:.2f}%'
    def answer(x):return 'not estimable' if x is None else 'holds' if x else 'does not hold'
    text='PRE-CHECK: YES — C1 bath and C4 starred had saved ending-family outcome breakdowns in v94; they are discovery/post-hoc and excluded from headline counts.\n\n'
    text+='RETROSPECTIVE DESCRIPTIVE — v3.2, exploratory origin, no p-values.\n\n'
    text+='v3/v3.1 saved context effects and outcome-blind family support, without additional saved family outcome breakdowns for C2/C5/C6/C7. C3 Rosettes is the known origin of this hypothesis, not new evidence. PRECHECK.json records the schema audit and the distinction between a saved family outcome breakdown and transient stratum arithmetic used by every MH aggregate. All contexts remain exposed/uncertified in the broader project sense.\n\n'
    text+='The original amendment and explicit scoring definitions were hashed before reading new family-level values from EVENTS.csv. H/F remain separate. No v3 primary engine, result or source file was changed.\n\n'
    text+='## Headline descriptive counts\n\nEach of the five individual original families must have at least20 events in that context/reading/view; grouped pools do not rescue a sparse family. C1/C4 are excluded. The requested-count column permits the known-origin C3, which is explicitly flagged; counts excluding C3 are preserved separately. No count is prospective evidence.\n\n'
    text+='| Reading | View | (a) holds / estimable | Contexts in denominator | (b) holds / estimable | Contexts in denominator |\n|---|---|---|---|---|---|\n'
    for reading in ['H','F']:
        for view in ['all','available']:
            z=headline[reading][view]['requested_excluding_prior_outside_Rosettes_breakdowns'];a,b=z['a'],z['b']
            text+=f"| {reading} | {view} | {a['holds']}/{a['estimable_contexts']} | {', '.join(a['denominator_contexts']) or 'none'} | {b['holds']}/{b['estimable_contexts']} | {', '.join(b['denominator_contexts']) or 'none'} |\n"
    text+='\n## Predictions for every context\n\n(a) compares pooled event-weighted next-qok rates for eey+ey versus edy+y+other. (b) uses the corresponding MH effects, maintaining original family strata: abs(blocked-group gap) < half the signed comparison-group gap. Zero vs zero does not satisfy that strict inequality. Sparse cells are unscored, not failures.\n\n'
    text+='| Context | Reading | View | Prior role | eey+ey rate | edy+y+other rate | eey+ey MH pts | edy+y+other MH pts | Sparse families (<20) | (a) | (b) |\n|---|---|---|---|---:|---:|---:|---:|---|---|---|\n'
    for c in cells:
        role='discovery/post-hoc' if c['posthoc'] else 'known-origin E' if c['known_origin'] else 'retrospective; no prior saved family outcome breakdown found'
        text+=f"| {c['context']} {c['context_name']} | {c['reading']} | {c['view']} | {role} | {rate(c['blocked_group']['pooled_qok_rate'])} | {rate(c['comparison_group']['pooled_qok_rate'])} | {fmt(c['blocked_group']['MH_effect_points'])} | {fmt(c['comparison_group']['MH_effect_points'])} | {', '.join(c['sparse_families']) or 'none'} | {answer(c['prediction_a_holds'])} | {answer(c['prediction_b_holds'])} |\n"
    text+='\n## Family-level rows\n\nArm rates below are raw qok counts divided by eligible events. MH effects are weighted within physical folios; zero-comparison strata remain listed but carry no effect weight. Zero-qok count means strata with both prefixes present and no qok in either arm; an additional all-strata zero count is retained in the machine-readable files. Small families remain descriptive and labelled.\n'
    for view in ['all','available']:
        text+='\n### '+view+' followers\n\n| Context | Reading | Family | sh qok/events | sh rate | ch qok/events | ch rate | MH pts | V | Context V share | Zero-qok supported strata | ≥20 events |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|\n'
        for r in families:
            if r['view']!=view:continue
            text+=f"| {r['context']} | {r['reading']} | {r['family']} | {r['sh_qok']}/{r['sh_events']} | {rate(r['sh_qok_rate'])} | {r['ch_qok']}/{r['ch_events']} | {rate(r['ch_qok_rate'])} | {fmt(r['MH_effect_points'])} | {r['V']:.3f} | {rate(r['context_V_share'])} | {r['zero_qok_both_supported_strata']} | {r['family_20_events']} |\n"
    text+='\n## Zero-qok-stratum removal sensitivity\n\nBoth arms are retained for surviving folio x family strata. This outcome-selected removal drops zero contributions from the MH numerator but can shrink its denominator, mechanically enlarging any nonzero effect in magnitude. It is a dilution description, not a repaired or adjusted primary result. Baselines reproduce v3 exactly; available-only results use the v3.1 rule.\n\n'
    text+='| Context | Reading | View | v3 baseline MH pts | After zero-stratum removal | Zero supported strata removed | All zero strata removed | V removed | Remaining V |\n|---|---|---|---:|---:|---:|---:|---:|---:|\n'
    for r in sens:text+=f"| {r['context']} | {r['reading']} | {r['view']} | {fmt(r['v3_baseline_effect_points'])} | {fmt(r['remaining']['MH_effect_points'])} | {r['zero_qok_supported_strata_removed']} | {r['zero_qok_strata_removed']} | {r['removed_V']:.3f} | {r['remaining']['V']:.3f} |\n"
    text+='\n## Limits and verification\n\nNo absolute prohibition follows from a lower observed rate. Exact-zero MH differences can arise from no qok events, cancellation or no comparison support; arm counts distinguish them. A finite retrospective pattern may motivate a separately frozen future hypothesis, but cannot establish it here. No meanings or grammar-versus-junction inference is made.\n\n'
    text+='C1/C4 are excluded by prior family exposure even if their descriptive patterns align. C3 was the exploratory origin and is explicitly flagged. HEADLINE.json also provides counts excluding that origin. Eligibility applies independently to all and available-only views; unavailable denominators are not negative evidence.\n\n'
    text+='Independent exact-rational regrouping from x/y and literal follower/origin fields reproduced every baseline, individual-family MH effect, grouped effect and zero-stratum sensitivity (252 comparisons). All28 v3 baselines were reproduced; availability flags were independently recomputed; all frozen input hashes stayed unchanged. Detailed event counts and support are preserved in JSON/CSV.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('DELIVERY-MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='DELIVERY-MANIFEST.json'}))

if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze()
    elif sys.argv[1]=='analyze':analyze()
    else:raise ValueError(sys.argv[1])
