"""Read-only RD-v2 outcome audit, no new generation or parameter fitting."""
import json
import math
from collections import Counter
import run_v2 as v


def independent_score(words,model,signal):
    clusters=sorted('ch sh cth ckh cph cfh ii iii in iin aiin qo ee'.split(),key=lambda x:(-len(x),x))
    def parse(word):
        out=[]
        while word:
            u=next((x for x in clusters if word.startswith(x)),word[0]);out.append(u);word=word[len(u):]
        return out
    if len(words)<2:return 0.
    total=0.
    for i,a in enumerate(words):
        b=words[(i+1)%len(words)]
        if '\ufffd' in a or '\ufffd' in b:continue
        if signal=='word':x,y=(a,b),(b,a)
        else:
            aa,bb=parse(a),parse(b);x,y=(aa[-1],bb[0]),(bb[-1],aa[0])
        total+=math.log(model.get(x,0)+.5)-math.log(model.get(y,0)+.5)
    return total/len(words)


def main():
    v.check()
    out=v.OUT;registration=v.load(v.REG/'REGISTRATION.json')
    assert registration['utc']<v.load(out/'RUN_START.json')['utc']
    for n,h in v.load(out/'ARTIFACT_MANIFEST.json')['hashes'].items():
        assert v.rd.sha(out/n)==h,n
    status=v.load(out/'STATUS.json')
    assert status['prior_runs_unchanged'] and status['radial']=='HELD'
    assert not status['real_ring_scores_computed'] and not status['phases_1_plus_run']
    assert not status['corrected_order_generated']
    dtrials=ptrials=otrials=0
    for scorefile in out.rglob('scores.jsonl'):
        folder=scorefile.parent;events=v.rd.loadlines(folder/'events.jsonl')
        names=[e['event'] for e in events]
        assert names.index('KEY_SEALED')<names.index('SCORES_SAVED')<names.index('KEY_OPENED')
        seal=next(e for e in events if e['event']=='KEY_SEALED')
        save=next(e for e in events if e['event']=='SCORES_SAVED')
        assert seal['sha256']==v.rd.sha(folder/'sealed/key.json')
        assert save['sha256']==v.rd.sha(scorefile)
        keys={k['id']:k for k in v.load(folder/'sealed/key.json')}
        stimuli={s['id']:s for s in v.rd.loadlines(folder/'stimuli.jsonl')}
        scores={s['id']:s for s in v.rd.loadlines(scorefile)}
        assert set(keys)==set(stimuli)==set(scores)
        if (folder/'model.csv').exists():
            signal='glyph' if 'glyph' in folder.parts else 'word'
            model={(r['a'],r['b']):int(r['count']) for r in v.rows(folder/'model.csv')}
            correct={}
            for cid,s in stimuli.items():
                k=keys[cid];x=scores[cid]
                assert s['kind']=='circular' and len(s['words'])==k['n']
                assert Counter(s['words'])==Counter(x['null_words'])
                score=independent_score(s['words'],model,signal)
                ns=independent_score(x['null_words'],model,signal)
                assert abs(score-x['score'])<1e-10 and abs(ns-x['null_score'])<1e-10
                pred=0 if abs(score)<=1e-12 else 1 if score>0 else -1
                correct[cid]=int(pred==(-1 if k['reverse'] else 1));dtrials+=1
            for b in v.load(folder/'bins.json'):
                ids=[k['id'] for k in keys.values() if k['bin']==b['bin']]
                assert len(ids)==b['n']
                acc=sum(correct[cid] for cid in ids)/len(ids) if ids else 0
                assert abs(acc-b['accuracy'])<1e-12
                passed=(v.load(folder/'null.json')['passed'] and b['distinct_windows']>=30 and b['families']>=8
                        and acc>=.8 and b['cluster_ci'][0]>=.65)
                assert b['passed']==passed
        elif 'members' in next(iter(stimuli.values()),{}):
            for cid,s in stimuli.items():
                k=keys[cid];x=scores[cid];count=len(s['members'])
                assert len(k['reverse_flags'])==count==k['n_members']
                if k['condition']==0:assert not any(k['reverse_flags'])
                if k['condition']==1:assert all(k['reverse_flags'])
                if k['condition']==2:
                    expected=count//2+(k['set_index']%2 if count%2 else 0)
                    assert sum(k['reverse_flags'])==expected
                seed=v.SEED+v.rd.stable(cid+v.shared_namespace(folder))
                for weight in ['unweighted','weighted']:
                    agg=v.np.array(x['family_'+weight]);observed=agg.sum()
                    flips=v.np.random.default_rng(seed).integers(0,2,size=(1999,len(agg)))*2-1
                    p=(1+sum(abs(a)>=abs(observed)-1e-12 for a in flips@agg))/2000
                    assert abs(float(p)-x[weight+'_p'])<1e-12
                    call=int(v.np.sign(observed)) if p<=.05 and observed!=0 else 0
                    assert call==x[weight+'_call']
                ptrials+=1
        elif folder.parts[-3]=='O':
            for cid,s in stimuli.items():
                k=keys[cid];x=scores[cid]
                assert 21<=len(s['words'])<=80
                assert Counter(s['words'])==Counter(x['null_words'])
                for j in range(2):
                    assert abs(x['profiles'][j][x['peaks'][j]]-max(x['profiles'][j]))<=1e-12
                    assert abs(x['null_profiles'][j][x['null_peaks'][j]]-max(x['null_profiles'][j]))<=1e-12
                otrials+=1
        chain=v.load(folder/'STATUS.json')
        assert events[-1]['event']==('STOP' if chain['status'].startswith('FAIL') else 'COMPLETE')
    # Verify shared cases across the two signals for direction and pooled comparisons.
    for wordfile in out.rglob('word/stimuli.jsonl'):
        glyphfile=wordfile.parent.parent/'glyph/stimuli.jsonl'
        if glyphfile.exists():assert v.rd.sha(wordfile)==v.rd.sha(glyphfile)
    for wordfile in (out/'U').glob('*/word/D/stimuli.jsonl'):
        glyphfile=wordfile.parents[2]/'glyph/D/stimuli.jsonl'
        if glyphfile.exists():assert v.rd.sha(wordfile)==v.rd.sha(glyphfile)
    for corpus in ['ZL','Latin']:
        for signal in ['word','glyph']:
            d=v.load(out/'U'/corpus/signal/'D/STATUS.json')
            p=v.load(out/'U'/corpus/signal/'P/STATUS.json')
            if d['status']!='PASS':
                assert p['status']=='NOT_RUN_UPSTREAM_FAILURE'
                assert not (out/'U'/corpus/signal/'P/scores.jsonl').exists()
    for arm in ['D','P','U','O','F']:
        missing=out/arm/'missing_sources'
        assert v.load(missing/'STATUS.json')['status']=='NOT_RUN_MISSING_SOURCE'
        assert not (missing/'scores.jsonl').exists()
    v.check()
    result=dict(status='PASS',direction_trials_independently_recomputed=dtrials,
        pooled_decisions_independently_recomputed=ptrials,origin_profile_choices_verified=otrials,
        checks=['registered inputs/instruments and prior-run hashes unchanged','all output artifact hashes',
                'registration-before-run and per-chain key/score chronology','word/unit/null-score arithmetic',
                'direction accuracy/gates','pooled cluster randomization and balanced mixed assignments',
                'shared signal stimuli','upstream U stops','missing-source and radial/target closure'])
    savepath=out/'VERIFICATION.json';v.save(savepath,result);print(json.dumps(result))


if __name__=='__main__':main()
