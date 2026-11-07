"""Independent stored-score/selection replay; no estimator fitting or threshold selection."""
from pathlib import Path
import ast,collections,hashlib,html,json,math
from datetime import datetime,timezone
import numpy as np
from scipy import stats,optimize
import run as experiment
from concurrent.futures import ProcessPoolExecutor

R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def esc(x):return html.escape(str(x))
tree=ast.parse((R.parent/'sh-qok-weak-score-v1/report.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_score'],type_ignores=[]),'independent_prior_scalar_audit','exec'),globals())

def replay(rec):
    s=rec['result'];di=rec['design_index'];seed=rec['seed'];regime=rec['regime']
    assert seed==2110000+di*100000+experiment.REGIMES.index(regime)*1000+rec['trial']
    if di<3:
        F,N=experiment.source.DESIGNS[di];events=experiment.source.generate(regime,seed,F,N)
    else:
        events,meta=experiment.matched_generate('H' if di==3 else 'F',regime,seed)
        assert meta==rec['matched_generation'] and meta['original_central_labels_used'] is False
    if s['status']!='SCORED':return 0
    count=verify_score(s);assert abs(s['p4']-min(1,4*s['p']))<1e-12 and abs(s['p24']-min(1,24*s['p']))<1e-12
    for f in s['per_folio']:assert f['n']==sum(p['folio']==f['folio'] for p in s['heldout'])
    c=s['calibration'];tr=c['learning_events'];y=np.array(c['learning_y']);n=len(y)
    assert y.tolist()==[events[i]['y'] for i in tr]
    fs=c['learning_folios'];assert set(fs)==set(s['train_folios'])
    expected_fs=sorted({e['folio'] for e in events},key=lambda f:hashlib.sha256(('weak-score-honest|'+f).encode()).hexdigest())
    expected_learning=set(expected_fs[:max(4,math.ceil(len(expected_fs)/4))]);assert set(fs)==expected_learning
    assert tr==[i for i,e in enumerate(events) if e['folio'] in expected_learning]
    const=np.array(c['oof']['constant']);penalty=(.5*math.log(n)+math.log(4))/n
    assert abs(c['penalty_nats']-penalty)<1e-12
    for a in c['assignments']:
        iv=[j for j,i in enumerate(tr) if events[i]['folio']==a['validation_folio']]
        it=[j for j,i in enumerate(tr) if events[i]['folio']!=a['validation_folio']]
        assert set(a['fit_folios'])==set(fs)-{a['validation_folio']} and len(iv)==a['validation_events']
        assert np.allclose(const[iv],(y[it].sum()+.5)/(len(it)+1),atol=1e-12)
    base=float(np.mean(-(y*np.log(const)+(1-y)*np.log(1-const))));choices=[]
    for m in ('P','J','L','F'):
        candidate=np.array(c['oof'][m]);d=candidate-const
        def derivative(w):
            p=const+w*d
            return float(np.mean(d*(p-y)/(p*(1-p))))
        w=0. if derivative(0)>=0 else 1. if derivative(1)<=0 else float(optimize.brentq(derivative,0,1,xtol=1e-14))
        mix=const+w*d;gain=base-float(np.mean(-(y*np.log(mix)+(1-y)*np.log(1-mix))))
        stored=next(x for x in c['candidates'] if x['model']==m)
        assert abs(stored['weight']-(w if gain>1/n else 0.))<1e-8 and abs(stored['pooled_gain_nats']-gain)<1e-10
        mix=const+stored['weight']*d;eg=np.where(y,np.log(mix/const),np.log((1-mix)/(1-const)))
        fg=[float(np.mean([eg[j] for j,i in enumerate(tr) if events[i]['folio']==f])) for f in fs]
        lower=float(np.mean(fg)-stats.t.ppf(.95,len(fs)-1)*np.std(fg,ddof=1)/math.sqrt(len(fs)))
        assert np.allclose(fg,stored['folio_gains'],atol=1e-12) and abs(lower-stored['lower95_gain_nats'])<1e-12 and abs(lower-penalty-stored['penalized_lower'])<1e-12
        choices.append((m,stored['weight'],lower-penalty))
    best=max(choices,key=lambda x:x[2]);selected=best[0] if best[2]>0 else 'constant';weight=best[1] if selected!='constant' else 0.
    assert c['selected']==selected and abs(c['weight']-weight)<1e-12
    rate=(y.sum()+.5)/(n+1);assert abs(rate-c['full_learning_constant'])<1e-12
    te=[i for i,e in enumerate(events) if e['folio'] not in expected_learning]
    assert len(te)==s['test_n'] and len(c['selected_raw_probabilities'])==n+len(te)
    for j,p in enumerate(s['heldout']):
        e=events[te[j]];assert p['event']==te[j] and p['folio']==e['folio'] and p['y']==e['y']
        assert abs(p['baseline']-((1-weight)*rate+weight*c['selected_raw_probabilities'][n+j]))<1e-12
    constant=float(np.mean([-math.log2(rate if events[i]['y'] else 1-rate) for i in te]));assert abs(s['constant']-constant)<1e-12
    # Independently reconstruct fit-only distant feature descriptors and their exact counts/scales.
    descriptors=[]
    for offset in (-4,-3,3,4):
        words=[events[i]['context'][str(offset)] for i in tr if not events[i]['context'][str(offset)].startswith('<')]
        extractors={'p1':lambda w:w[:1],'p2':lambda w:w[:2],'s1':lambda w:w[-1:],'s2':lambda w:w[-2:],'word':lambda w:w}
        for family,fn in extractors.items():
            counts=collections.Counter(fn(w) for w in words)
            descriptors.extend(dict(offset=offset,family=family,value=v,count=k) for v,k in sorted(counts.items(),key=lambda x:(-x[1],x[0])) if k>=8)
            same=[d for d in descriptors if d['offset']==offset and d['family']==family]
            for d in same[12:]:descriptors.remove(d)
        lens=np.array([math.log1p(len(w)) for w in words])
        if len(lens) and lens.std()>1e-12:descriptors.append(dict(offset=offset,family='loglen',mean=float(lens.mean()),sd=float(lens.std())))
    assert descriptors==s['descriptors']
    if rec['trial']==0:
        # One deterministic representative per cell also checks the stored learned direction.
        # Rebuild the frozen feature map, but solve the ridge equations afresh; no classifier refit.
        from scipy import sparse
        cache=experiment.core.cache_features(events);w,wt=experiment.core.fitted_matrix(cache,tr,te,'F')
        w=sparse.hstack([np.ones((n,1)),w],format='csr');wt=sparse.hstack([np.ones((len(te),1)),wt],format='csr')
        def val(e,d):
            word=e['context'][str(d['offset'])]
            if word.startswith('<'):return 0.
            if d['family']=='loglen':return (math.log1p(len(word))-d['mean'])/d['sd']
            return float(extractors[d['family']](word)==d['value'])
        def matrix(ids):return np.array([[val(events[i],d)*(1 if events[i]['context']['1'].startswith('qok') else -1) for d in descriptors] for i in ids])
        z,zt=matrix(tr),matrix(te);lam=math.sqrt(n);kernel=(w@w.T).toarray();alpha=np.linalg.solve(kernel+lam*np.eye(n),z)
        rz=z-kernel@alpha;rzt=zt-(wt@w.T)@alpha;raw=np.array(c['selected_raw_probabilities'][:n]);pt=(1-weight)*rate+weight*raw
        beta=np.linalg.solve(rz.T@rz+lam*np.eye(len(descriptors)),rz.T@(y-pt))
        assert np.allclose(beta,s['coefficients'],atol=1e-10) and np.allclose(rzt@beta,[p['direction'] for p in s['heldout']],atol=1e-10)
    return count

def audit_file(path):
    rec=json.loads(Path(path).read_text());count=replay(rec);s=rec['result']
    # Keep compact, already-audited aggregates instead of all probability arrays in memory.
    small={k:s[k] for k in ('status','p4','flag4','flag24','adequate') if k in s}
    small['calibration']={'selected':s.get('calibration',{}).get('selected','unsupported')}
    return count,dict(design=rec['design'],regime=rec['regime'],result=small,old_v2=rec['old_v2'])

def main():
    experiment.verify();assert read('ENGINEERING.json')['status']=='PASS'
    q=read('QUALIFICATION.json');cells=collections.defaultdict(list);checked=0
    with ProcessPoolExecutor(max_workers=4) as pool:
        for j,(count,rec) in enumerate(pool.map(audit_file,sorted((R/'trials').glob('*.json')),chunksize=8)):
            checked+=count;cells[rec['design'],rec['regime']].append(rec)
            if (j+1)%500==0:print('independent replay',j+1,flush=True)
    assert sum(map(len,cells.values()))==4500 and len(cells)==45
    failures=[]
    for s in q['cells']:
        rr=cells[s['design'],s['regime']];assert len(rr)==100
        k=sum(x['result'].get('flag4',False) for x in rr);assert k==s['flags4']
        assert sum(x['result'].get('flag24',False) for x in rr)==s['flags24']
        assert sum(x['result'].get('adequate',False) for x in rr)==s['adequate']
        z=stats.norm.ppf(.975);den=1+z*z/100;mid=(k/100+z*z/200)/den;rad=z*math.sqrt(k/100*(1-k/100)/100+z*z/40000)/den;bounds=[max(0,mid-rad),min(1,mid+rad)]
        assert np.allclose(bounds,s['wilson95'],atol=1e-12)
        expected=bounds[1]<=.10 if s['regime'] in experiment.REGIMES[:6] else bounds[0]>=.80 if s['regime'] in ('weak','strong') else None
        assert s['required_gate']==expected
        if 'paired_factor24' in s:
            pp=s['paired_factor24'];win=sum(x['result'].get('flag24',False) and not x['old_v2']['flag'] for x in rr);lose=sum(x['old_v2']['flag'] and not x['result'].get('flag24',False) for x in rr);pv=float(stats.binom.sf(win-1,win+lose,.5)) if win+lose else 1.
            assert win==pp['new_only'] and lose==pp['old_only'] and abs(pv-pp['p'])<1e-12 and pp['required_gate']==(pv<=.01)
        if expected is False or s.get('paired_factor24',{}).get('required_gate',True) is False:failures.append(s)
    assert q['manuscript_allowed']==(not failures)
    phases=[json.loads(x) for x in (R/'PHASES.jsonl').read_text().splitlines()]
    if failures:assert not any(p['phase']=='manuscript_read_start' for p in phases) and not (R/'RESULTS.json').exists()
    audit=dict(status='PASS',audited_at_utc=datetime.now(timezone.utc).isoformat(),trials=4500,heldout_scores_replayed=checked,OOF_mixtures_and_folio_uncertainty_replayed=True,learning_only_descriptors_replayed=True,ridge_directions_recomputed_first_trial_every_cell=True,synthetic_labels_regenerated=True,all_gate_decisions_replayed=True,hashes_unchanged=True,manuscript_block_required=bool(failures),manuscript_block_respected=not any(p['phase']=='manuscript_read_start' for p in phases))
    save('QUALIFICATION-AUDIT.json',audit)
    save('OUTCOME.json',dict(status=q['status'],failed_cells=failures,manuscript_rerun_permitted=not failures,manuscript_rerun_performed=False,audit=audit))
    parts=['<!doctype html><meta charset="utf-8"><title>Sparse written-part repair qualification</title><style>body{font:17px/1.6 system-ui;max-width:1240px;margin:40px auto;padding:24px;background:#fafbf7;color:#203c32}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px;margin:24px 0}td,th{padding:9px;text-align:left;border-bottom:1px solid #cbd7cf}th{background:#e6eee7}.note{padding:18px;background:#edf0e3}.fail{color:#942f29;font-weight:bold}a{color:#1a624b}</style>',f'<h1>Sparse written-part repair: {esc(q["status"])}</h1>',f'<p class="note">All 4,500 fresh controls completed. Required failing cells: {len(failures)}. '+('Manuscript rerun blocked; no new manuscript score was computed.' if failures else 'Synthetic qualification passed; manuscript application requires this completed independent audit.')+'</p>',
    '<p><a href="PROTOCOL.md">Frozen repair and unchanged thresholds</a> · <a href="FREEZE.json">Frozen hashes</a> · <a href="QUALIFICATION.json">All control outcomes</a> · <a href="QUALIFICATION-AUDIT.json">Independent replay</a> · <a href="PHASES.jsonl">Chronology</a> · <a href="../sh-qok-weak-score-v2/report.html">Prior nuisance failure retained</a> · <a href="../sh-qok-weak-score-v1/report.html">Earlier qualification failure retained</a></p>',
    '<h2>What changed before outcomes</h2><p>Shared literal one/two-character beginnings and endings, exact words and log length replace whole-word-only distant coverage. Categorical support remains at least eight learning occurrences. Nuisance selection now uses a one-sided 95% lower bound across learning-folio gains, with the existing selection penalty. No adequacy or qualification threshold was relaxed. Held-out labels never choose the representation or direction.</p>',
    '<h2>Exact sparse event designs</h2><p>H/F templates retain vocabulary, folios, context correlations, unknown slots and uneven event counts from the previously exposed inventories, with original central sh/ch labels removed. Synthetic central labels are redrawn independently in every trial. This is a conditional-event benchmark, not a physically coherent resynthesized manuscript. The planted positive cue is deliberately favorable: the supported binary column with greatest residual variance on learning covariates, selected before synthetic labels.</p>',
    '<table><tr><th>Template</th><th>Learning / testing events</th><th>New distant dimensions</th><th>Frozen positive cue</th><th>Learning cue support</th></tr>']
    for code,p in read('MATCHED-PROFILES.json').items():parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [code,f'{len(p["learning_events"])} / {len(p["test_events"])}',p['remote_feature_count'],p['cue'],p['cue']['count']])+'</tr>')
    parts.extend(['</table><h2>Every control cell and failure</h2><p>Nulls: Wilson 95% upper false-flag bound ≤ .10. Weak (.65 logit interaction) and strong (2.5): lower detection bound ≥ .80 in every design. Inadequate or unsupported positives are nondetections. Tiny (.35) remains descriptive. Adequacy is unchanged: loss ≤ learning-rate constant + .01 bits/event. Both factor 4 and factor 24 are retained.</p><table><tr><th>Design</th><th>Regime</th><th>Flags ×4 /100</th><th>Flags ×24 /100</th><th>Adequate /100</th><th>Wilson95 ×4</th><th>Gate</th></tr>'])
    for s in q['cells']:
        gate='descriptive' if s['required_gate'] is None else 'PASS' if s['required_gate'] else 'FAIL'
        parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [s['design'],s['regime'],s['flags4'],s['flags24'],s['adequate'],[round(x,4) for x in s['wilson95']],gate])+'</tr>')
    parts.append('</table>')
    for s in q['cells']:
        if 'paired_factor24' in s:parts.append('<p>Unchanged paired factor24 gate: '+esc(s['paired_factor24'])+'</p>')
    if failures:
        parts.append('<h2>Retained failure diagnostics</h2><p>These are synthetic-only diagnostics; they do not authorize a manuscript rerun or a within-freeze repair.</p><table><tr><th>Design / regime</th><th>Raw interaction significance /100</th><th>Valid flags /100</th><th>Inadequate /100</th><th>Selected nuisance models</th></tr>')
        for s in failures:
            rr=cells[s['design'],s['regime']];raw=sum(x['result'].get('p4',1)<=.05 for x in rr);models=collections.Counter(x['result'].get('calibration',{}).get('selected','unsupported') for x in rr)
            parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [s['design']+' / '+s['regime'],raw,s['flags4'],100-s['adequate'],dict(models)])+'</tr>')
        parts.append('</table>')
    parts.append('<h2>What this establishes</h2><p>Feature support is representation coverage, not demonstrated sensitivity. A passing null cell only qualifies its authored nuisance mechanism. A failed power cell remains a failure even if every baseline is adequate. Strong performance cannot substitute for weak power; uniform designs cannot substitute for sparse designs. H/F are dependent alternate readings. No result assigns meanings, sounds, morphology or grammar. A new repair would need another freeze and fresh controls.</p>')
    (R/'report.html').write_text('\n'.join(parts),encoding='utf-8');print(json.dumps(audit),flush=True)

if __name__=='__main__':main()
