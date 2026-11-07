"""Audit JX Phase0 outputs; no new trial generation or target feature scoring."""
import math
import json
from collections import Counter,defaultdict
import jx_phase0 as j


def independent_gain(blocks,direction,mask=None):
    values=[]
    # Direct conditional-entropy implementation, independently of the contingency formula.
    def entropy(c):
        n=sum(c.values());k=len(c)
        return -sum(v/n*math.log2(v/n) for v in c.values())+(k-1)/(2*n*math.log(2))
    for f,words in enumerate(blocks):
        zgroups=defaultdict(Counter);zvgroups=defaultdict(Counter);n=0
        for i,(a,b) in enumerate(zip(words,words[1:])):
            ua,ub=j.units(a),j.units(b)
            if len(ua)<2 or len(ub)<2 or (mask is not None and i not in mask[f]):continue
            y,z,v=(ua[-1],ua[-2],ub[0]) if direction=='reg' else (ub[0],ub[1],ua[-1])
            zgroups[z][y]+=1;zvgroups[z,v][y]+=1;n+=1
        if n:
            h1=sum(sum(c.values())/n*entropy(c) for c in zgroups.values())
            h2=sum(sum(c.values())/n*entropy(c) for c in zvgroups.values())
            values.append(h1-h2)
    return values


def main():
    j.check();out=j.OUT
    assert j.load(j.REG/'REGISTRATION.json')['utc']<j.load(out/'RUN_START.json')['utc']
    for n,h in j.load(out/'ARTIFACT_MANIFEST.json')['hashes'].items():assert j.sha(out/n)==h,n
    frozen=(j.FROZEN/'CANDIDATES_APPROVED_PAYLOAD.md').read_text(encoding='utf-8')
    assert frozen.count('NP — uncalibrated')==36
    directions=0;entropy_tests=0
    for scorefile in out.rglob('scores.jsonl'):
        folder=scorefile.parent;events=j.RD.loadlines(folder/'events.jsonl');names=[e['event'] for e in events]
        assert names.index('KEY_SEALED')<names.index('SCORES_SAVED')<names.index('KEY_OPENED')
        assert next(e['sha256'] for e in events if e['event']=='KEY_SEALED')==j.sha(folder/'sealed/key.json')
        assert next(e['sha256'] for e in events if e['event']=='SCORES_SAVED')==j.sha(scorefile)
        models=j.load(folder/'models.json');meta=models['meta']
        counts={k:{(a,b):n for a,b,n in v} for k,v in models['counts'].items()}
        stimuli={s['id']:s for s in j.RD.loadlines(folder/'stimuli.jsonl')}
        for value in j.RD.loadlines(scorefile):
            words=stimuli[value['id']]['words'];n=len(words)
            assert Counter(words)==Counter(value['null_words'])
            for parser in ['units','codepoints']:
                for variant in ['raw','matched']:
                    # Independently audit J on every case; alternatives are algebraically tested in unit fixtures.
                    key='|'.join([parser,variant,'J']);model=counts[key];maps=list(map(set,meta[parser]['maps']));total=0.
                    for a,b in zip(words,words[1:]+words[:1]):
                        aa=j.units(a) if parser=='units' else tuple(a);bb=j.units(b) if parser=='units' else tuple(b)
                        x,y,rx,ry=aa[-1],bb[0],bb[-1],aa[0]
                        if variant=='matched':
                            x=x if x in maps[1] else '*';rx=rx if rx in maps[1] else '*'
                            y=y if y in maps[0] else '*';ry=ry if ry in maps[0] else '*'
                        total+=math.log(model.get((x,y),0)+.5)-math.log(model.get((rx,ry),0)+.5)
                    assert abs(total/n-value['scores'][key])<1e-10
            directions+=1
    # Recompute every stored observed entropy gain from a second estimator implementation.
    for file in (out/'conditioning').rglob('reg.json'):
        folder=file.parent;name=folder.name;mask=None
        if name.startswith('null_'):blocks=j.load(out/f'bank/C-zero/{int(name[5:]):03d}.json')['held']
        elif name.startswith('reg_'):blocks=j.load(out/f'bank/C-junc/{int(name[4:]):03d}.json')['held']
        elif name.startswith('prog_'):blocks=j.load(out/f'bank/C-prog/{int(name[5:]):03d}.json')['held']
        elif name in ['Latin_original','Latin_rewrite']:
            corpus='C-lat' if name=='Latin_original' else 'C-sandhi';blocks=j.load(out/f'references/{corpus}.json')['full']['held']
            mask=[set(x) for x in j.load(folder/'paired_eligible_indices.json')]
        else:raise AssertionError(name)
        for direction in ['reg','prog']:
            r=j.load(folder/(direction+'.json'));gains=independent_gain(blocks,direction,mask)
            if gains:
                assert abs(sum(gains)/len(gains)-r['statistic'])<1e-10
                assert all(abs(a-b['gain'])<1e-10 for a,b in zip(gains,r['families']))
            if r['p'] is not None:
                p=(1+sum(v>=r['statistic']-1e-12 for v in r['null_statistics']))/1001
                assert abs(p-r['p'])<1e-12
            entropy_tests+=1
        r=j.load(folder/'reg.json');p=j.load(folder/'prog.json');decision=j.load(folder/'decision.json')
        ps=[r['p'] if r['supported'] else None,p['p'] if p['supported'] else None]
        assert j.holm(ps)==decision['rejects']
    spacing=j.load(out/'spacing/metrics.json') if (out/'spacing/metrics.json').exists() else None
    if spacing:
        draws=j.np.load(out/'spacing/bootstrap_family_draws.npy');nf=draws.shape[1]
        w=j.np.array([j.np.bincount(d,minlength=nf) for d in draws]);boots={}
        for name,m in spacing['corpora'].items():
            saved=j.load(out/'spacing'/(name+'_counts.json'));a=j.np.array(saved['cross']);b=j.np.array(saved['within'])
            assert abs(float(j.jsd_counts(a.sum(axis=0),b.sum(axis=0)))-m['JSD'])<1e-12
            boots[name]=j.jsd_counts(w@a,w@b)
        for c in spacing['contrasts']:
            a,b=c['contrast'].split(' minus ');interval=j.np.quantile(boots[a]-boots[b],[.025,.975]).tolist()
            assert all(abs(x-y)<1e-12 for x,y in zip(interval,c['ci']))
            assert c['passed']==(interval[0]>0)
    status=j.load(out/'STATUS.json')
    assert status['real_ring_scoring']=='CLOSED' and status['radial']=='HELD'
    assert not status['manuscript_K_I_run'] and not status['PDF_used'] and status['prior_runs_unchanged']
    spec=j.load(out/'specificity/STATUS.json')
    outcomes=spec.get('outcomes',[])
    failed=[r['corpus'] for r in outcomes if not r['passed']]
    if failed:
        seq=['C-junc','C-SS','C-EE','C-order'];idx=seq.index(failed[0])
        for name in seq[idx+1:]:
            assert not (out/'specificity'/name/'scores.jsonl').exists()
            assert j.load(out/'specificity'/name/'STATUS.json')['status']=='NOT_RUN_UPSTREAM_FAILURE'
    j.check()
    result=dict(status='PASS',direction_cases_primary_J_audited=directions,observed_entropy_tests_independently_recomputed=entropy_tests,
        checks=['approved36-row payload and NP freeze','registered input and prior-run hashes','output hashes',
        'score-before-key chronology','all-case primary J arithmetic for both parsers/maps',
        'independent Miller-Madow conditional entropy and permutation-tail p values','Holm decisions',
        'source-paired JSD bootstrap contrasts','dependent K1 stops','PDF exclusion and target closure'])
    j.save(out/'VERIFICATION.json',result);print(json.dumps(result))

if __name__=='__main__':main()
