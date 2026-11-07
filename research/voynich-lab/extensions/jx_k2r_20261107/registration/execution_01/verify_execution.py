"""Independent saved-arithmetic audit; never refits target models."""
import sys
sys.dont_write_bytecode=True
import json,math,random
from collections import Counter,defaultdict
import execute as e

def jl(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()]
def independent_edge(a,b,m,v):
    aa=e.j.RD.units(a);bb=e.j.RD.units(b);x,y,rx,ry=aa[-1],bb[0],bb[-1],aa[0]
    if v=='matched':
        maps=m['meta']['units']['maps'];x=x if x in maps[1] else '*';rx=rx if rx in maps[1] else '*';y=y if y in maps[0] else '*';ry=ry if ry in maps[0] else '*'
    counts={(a,b):n for a,b,n in m['counts'][v]}
    return math.log((counts.get((x,y),0)+.5)/(counts.get((rx,ry),0)+.5))

def icdf(values,families,name,adjust=False):
    groups={}
    for v,f in zip(values,families):
        if f not in groups:groups[f]=[0.,0]
        groups[f][0]+=v;groups[f][1]+=1
    groups=list(groups.values());r=e.rng('bootstrap/'+name);bs=[]
    for _ in range(2000):
        draw=[groups[r.randrange(len(groups))] for __ in groups];bs.append(sum(a for a,b in draw)/sum(b for a,b in draw))
    bs.sort();p=.025/7 if adjust else .025
    return [bs[math.floor(2000*p)],bs[math.ceil(2000*(1-p))-1]]

def main():
    e.check();out=e.OUT
    for p,h in e.load(out/'ARTIFACT_MANIFEST.json')['hashes'].items():assert e.sha(out/p)==h,p
    assert e.load(e.BIND/'EXECUTABLE_MANIFEST.json')['utc']<jl(out/'events.jsonl')[0]['utc']
    source=e.load(out/'source/STATUS.json');cases=e.load(out/'source/common_windows.json');ledger=jl(out/'source/span_validation.jsonl');valid={r['ZL_id'] for r in ledger if r['eligible']}
    approved={r['ZL_id']:r for r in e.rows(e.HERE/'registration/review_freeze/crosswalk_candidates.csv')}
    for r in ledger:assert r['original_id']==approved[r['ZL_id']]['original_id']
    for c in cases:
        assert all(l in valid for l in c['source_loci'])
        assert e.s.split(approved[c['source_loci'][0]]['folio'])=='heldout'
        for parse,d in c['streams'].items():
            for reader,w in d.items():assert (11<=len(w)<=20 if c['bin']==3 else 21<=len(w)<=40)
    scores_checked=0;intervals=0;edge_checked=0
    for mp in out.glob('robustness/*/*/*/metrics.json'):
        folder=mp.parent;models=e.load(folder/'models.json');stim=jl(folder/'stimuli.jsonl');scores=jl(folder/'scores.jsonl');keys=e.load(folder/'sealed_keys.json');trials=jl(folder/'trials.jsonl');metrics=e.load(mp)
        events=jl(folder/'events.jsonl');assert [x['event'] for x in events]==['KEY_SEALED','SCORES_SAVED','KEY_OPENED'];assert events[0]['sha256']==events[2]['sha256']==e.sha(folder/'sealed_keys.json');assert events[1]['sha256']==e.sha(folder/'scores.jsonl')
        for st,sc,k,t in zip(stim,scores,keys,trials):
            assert st['id']==sc['id']==k['id']==t['id']
            for reader,w in st['streams'].items():
                for v in ['raw','matched']:
                    val=sum(independent_edge(a,b,models[reader],v) for a,b in zip(w,w[1:]+w[:1]))/len(w)
                    assert math.isclose(val,sc['streams'][reader]['scores'][v],abs_tol=1e-12)
                    assert int(e.sign(val)==(-1 if k['reverse'] else 1))==t['streams'][reader]['correct'][v];scores_checked+=1
                assert Counter(w)==Counter(sc['streams'][reader]['null_words'])
        ns=folder.relative_to(out).as_posix()
        for m in metrics['metrics']:
            xs=[t for t in trials if t['bin']==m['bin']];vals=[t['streams'][m['reader']]['correct'][m['variant']] for t in xs];f=[t['family'] for t in xs]
            assert m['accuracy']==sum(vals)/len(vals)
            ci=icdf(vals,f,ns+m['reader']+str(m['bin'])+m['variant'],metrics['scope']!='aggregate')
            assert all(math.isclose(a,b,abs_tol=1e-12) for a,b in zip(ci,m['ci']));intervals+=1
            assert m['passed']==(m['accuracy']>=.8 and ci[0]>=.65)
        expected='FAIL_NULL' if not all(n['passed'] for n in metrics['nulls'].values()) else ('K2R_PASS_CELL' if all(m['passed'] for m in metrics['metrics'] if m['reader']=='H') else 'FAIL_ROBUSTNESS')
        assert e.load(folder/'STATUS.json')['status']==expected
    for p in out.glob('boundary/*/edge_scores.jsonl'):
        folder=p.parent;models=e.load(folder/'models.json');st=jl(folder/'stimuli.jsonl');sc=jl(p);events=jl(folder/'events.jsonl')
        assert [x['event'] for x in events]==['KEY_SEALED','SCORES_SAVED','KEY_OPENED'];assert events[1]['sha256']==e.sha(p)
        for stimulus,scores in zip(st,sc):
            assert stimulus['id']==scores['id']
            for reader,data in stimulus['streams'].items():
                w=data['words']
                for i,edge in enumerate(scores['streams'][reader]):
                    for v,val in edge['values'].items():
                        assert math.isclose(val,independent_edge(w[i],w[(i+1)%len(w)],models[reader],v),abs_tol=1e-12);edge_checked+=1
        edge_rows=jl(folder/'original_orientation_edges.jsonl');metrics=e.load(folder/'metrics.json')
        for cl in metrics['junction_classes']:
            xs=[r for r in edge_rows if r['reader']==cl['reader'] and r['bin']==cl['bin'] and r['variant']==cl['variant'] and r['classification']==cl['classification']]
            assert len(xs)==cl['n'];assert math.isclose(sum(x['D'] for x in xs),cl['signed_sum'],abs_tol=1e-8);assert math.isclose(sum(abs(x['D']) for x in xs),cl['absolute_mass'],abs_tol=1e-8)
    summary=e.load(out/'summary.json')['robustness']
    for row in summary:
        p=out/'robustness'/row['scope']/'common'
        if row['parse_status'][0]!='K2R_PASS_CELL':assert not (p/'join/scores.jsonl').exists()
    state=e.load(out/'STATUS.json');assert state['I_phase']=='CLOSED' and state['real_ring_scoring']=='CLOSED';e.check()
    receipt=dict(status='PASS_AUDIT',position_scores_recomputed=scores_checked,primary_intervals_recomputed=intervals,edge_contributions_recomputed=edge_checked,
        approved_pairings_unchanged=True,source_family_separation=True,stop_graph=True,prior_runs_unchanged=True,I_phase='CLOSED',real_ring_scoring='CLOSED',utc=e.s.now())
    e.save(out/'VERIFICATION.json',receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
