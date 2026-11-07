"""Use the same independent saved-prediction audit and table layout as attempt A."""
from pathlib import Path
import json

R=Path(__file__).resolve().parent
source=R.parent/'sh-qok-context-transfer-v1/report.py'
text=source.read_text(encoding='utf-8')
# Cache scores only; large prediction objects are discarded after each file read.
cache={p:json.loads(p.read_text())['scores'] for p in (R/'synthetic').glob('*.json')}
text=text.replace("json.loads(p.read_text())['scores']", "_score_cache[p]")
exec(compile(text,str(source),'exec'),dict(__file__=str(R/'report.py'),_score_cache=cache))
p=R/'report.html';s=p.read_text(encoding='utf-8')
s=s.replace('<h1>Can the sh/ch–qok relationship exceed local writing and phrases?</h1>',
'''<h1>sh/ch–qok context transfer: attempt B</h1><p>Attempt A failed its unchanged adequacy/power gate and never fitted manuscript data. <a href="../sh-qok-context-transfer-v1/report.html">Preserved attempt A</a>. Attempt B changes prediction to training-only hierarchical backoff; feature maps and support, adequacy, inference, and qualification gates remain unchanged.</p>''')
s=s.replace('<h2>Qualification before manuscript fitting</h2>',
'''<h2>Qualification before manuscript fitting</h2><p>Within each outer training partition, disjoint inner folios select convex backoff weights. Each model can fall back to its simpler predecessor, starting from the add-half constant. A fitted weight pays a one-parameter AIC-scale validation penalty. Raw models then refit on all outer-training folios; outer-test data never select weights. Saved predictions contain raw probabilities and every calibration allocation, weight, and validation gain.</p>''')
p.write_text(s,encoding='utf-8')

# Independently cross-check source event coverage against the previously saved v94 inventory.
results=R/'RESULTS.json'
if results.exists():
    old=json.loads((R.parent/'sh-qok-ending-qualification-reed-v94/EVENTS.json').read_text())
    panels=json.loads(results.read_text());checks=[];backoff=[]
    for pi,panel in enumerate(panels):
        ev=json.loads((R/(panel['panel']+'-events.json')).read_text())
        expected={(x['locator'],x['index'],x['word']) for x in old if x['panel']==pi}
        actual={(x['locator'],x['index'],x['word']) for x in ev}
        assert expected==actual,(panel['panel'],len(expected),len(actual))
        checks.append(dict(panel=panel['panel'],events=len(actual),v94_event_coverage_matches=True))
        if panel['status']=='SCORED':
            pp=json.loads((R/(panel['panel']+'-predictions.json')).read_text());fm=json.loads((R/(panel['panel']+'-folds.json')).read_text());fold_details=[]
            for e,p in zip(ev,pp):
                c=p['calibration'];inner=set(c['inner_fit_folios']);val=set(c['inner_validation_folios']);outer={f for f,k in fm.items() if k==p['fold']}
                assert not(inner&val or inner&outer or val&outer)
                assert inner|val=={f for f,k in fm.items() if k!=p['fold']}
                assert c['validation_n']==sum(x['folio'] in val for x in ev)
                mix=p['probability']['constant']
                for m in ('P','J','L','G'):
                    w=c['weights'][m];assert 0<=w<=1
                    if c['validation_gain_nats'][m]<=1/c['validation_n']:assert w==0
                    mix=(1-w)*mix+w*p['raw_probability'][m]
                    assert abs(mix-p['probability'][m])<1e-12
            for fold in range(5):
                p=next(x for x in pp if x['fold']==fold)
                fold_details.append(dict(fold=fold,**p['calibration']))
            backoff.append(dict(panel=panel['panel'],status='PASS',predictions=len(pp),mixtures_and_partitions_replayed=True,folds=fold_details))
    (R/'SOURCE-COVERAGE-AUDIT.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    (R/'BACKOFF-AUDIT.json').write_text(json.dumps(backoff,indent=2),encoding='utf-8')
