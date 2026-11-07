"""Independent read-only audit of RD-FO3 trial arithmetic and provenance."""
import math
import json
from collections import Counter
import run_followup as f
from verify_v2 import independent_score


def parse_properties(text):
    result={}
    for line in text.splitlines():
        line=line.strip()
        if line and not line.startswith('#') and '=' in line:
            a,b=line.split('=',1);result[a.strip()]=b.strip()
    return result


def main():
    f.check();f.check_published();out=f.OUT
    reg=f.v.load(f.REG/'REGISTRATION.json')
    assert reg['utc']<f.v.load(out/'RUN_START.json')['utc']
    for n,h in f.v.load(out/'ARTIFACT_MANIFEST.json')['hashes'].items():assert f.v.rd.sha(out/n)==h,n
    status=f.v.load(out/'STATUS.json')
    assert status['prior_runs_unchanged'] and status['radial']=='HELD'
    assert not status['real_ring_scores_computed'] and not status['phase1_run'] and not status['corrected_order_generated']
    n_direction=n_origin=0
    for scorefile in out.rglob('scores.jsonl'):
        folder=scorefile.parent;events=f.v.rd.loadlines(folder/'events.jsonl');names=[e['event'] for e in events]
        assert names.index('KEY_SEALED')<names.index('SCORES_SAVED')<names.index('KEY_OPENED')
        assert next(e['sha256'] for e in events if e['event']=='KEY_SEALED')==f.v.rd.sha(folder/'sealed/key.json')
        assert next(e['sha256'] for e in events if e['event']=='SCORES_SAVED')==f.v.rd.sha(scorefile)
        keys={k['id']:k for k in f.v.load(folder/'sealed/key.json')}
        stimuli={s['id']:s for s in f.v.rd.loadlines(folder/'stimuli.jsonl')}
        scores={s['id']:s for s in f.v.rd.loadlines(scorefile)}
        assert set(keys)==set(stimuli)==set(scores)
        if (folder/'model.csv').exists():
            model={(r['a'],r['b']):int(r['count']) for r in f.v.rows(folder/'model.csv')}
            sig=folder.name;correct={}
            for cid,s in stimuli.items():
                x=scores[cid];k=keys[cid]
                assert s['kind']=='circular' and len(s['words'])==k['n']
                assert Counter(s['words'])==Counter(x['null_words'])
                d=independent_score(s['words'],model,sig);nd=independent_score(x['null_words'],model,sig)
                assert abs(d-x['score'])<1e-10 and abs(nd-x['null_score'])<1e-10
                correct[cid]=int(f.v.rd.sign(d)==(-1 if k['reverse'] else 1));n_direction+=1
            nullpassed=f.v.load(folder/'null.json')['passed']
            for b in f.v.load(folder/'bins.json'):
                ids=[k['id'] for k in keys.values() if k['bin']==b['bin']]
                acc=sum(correct[i] for i in ids)/len(ids) if ids else 0
                assert abs(acc-b['accuracy'])<1e-12
                assert b['passed']==bool(nullpassed and b['distinct_windows']>=30 and b['families']>=8 and acc>=.8 and b['cluster_ci'][0]>=.65)
        else:
            models={sig:{(r['a'],r['b']):int(r['count']) for r in f.v.rows(folder/(sig+'_model.csv'))} for sig in ['word','glyph']}
            p1=f.v.load(folder/'p1_model.json');pf,po,w=p1['first_rate'],p1['other_rate'],p1['window']
            trialmap={t['id']:t for t in f.v.rows(folder/'trials.csv')}
            recomputed={}
            def profiles(words):
                n=len(words);answer=[[],[]]
                for reverse in [False,True]:
                    for i in range(n):
                        positions=[(i-1-j)%n if reverse else (i+j)%n for j in range(w)]
                        answer[int(reverse)].append(sum(math.log(pf/po) if ('p' in words[j] or 'f' in words[j])
                            else math.log((1-pf)/(1-po)) for j in positions)/w)
                return answer
            for cid,s in stimuli.items():
                x=scores[cid];k=keys[cid];n=len(s['words']);assert 21<=n<=80
                assert Counter(s['words'])==Counter(x['null_words'])
                gs=independent_score(s['words'],models['glyph'],'glyph')
                ws=independent_score(s['words'],models['word'],'word')
                ns=independent_score(x['null_words'],models['glyph'],'glyph')
                assert abs(gs-x['glyph_score'])<1e-10 and abs(ws-x['word_score'])<1e-10 and abs(ns-x['null_glyph_score'])<1e-10
                for words,field,peakfield in [(s['words'],'profiles','peaks'),(x['null_words'],'null_profiles','null_peaks')]:
                    expected=profiles(words)
                    for j in range(2):
                        assert all(abs(a-b)<1e-12 for a,b in zip(expected[j],x[field][j]))
                        assert abs(x[field][j][x[peakfield][j]]-max(x[field][j]))<=1e-12
                chosen=None if f.v.rd.sign(gs)==0 else x['peaks'][int(gs<0)]
                nullchosen=None if f.v.rd.sign(ns)==0 else x['null_peaks'][int(ns<0)]
                assert x['selected_peak']==chosen and x['null_selected_peak']==nullchosen
                origin=k['boundaries'][0];acceptable={(origin+d)%n for d in range(-2,3)}
                hit=int(chosen in acceptable);nullhit=int(nullchosen in acceptable)
                assert int(trialmap[cid]['hit'])==hit
                chance=5/n
                assert abs(float(trialmap[cid]['excess'])-(hit-chance))<1e-12
                assert abs(float(trialmap[cid]['null_excess'])-(nullhit-chance))<1e-12
                recomputed[cid]=hit;n_origin+=1
            for b in f.v.load(folder/'bins.json'):
                ids=[k['id'] for k in keys.values() if k['bin']==b['bin']]
                assert len(ids)==b['n']
                assert abs(sum(recomputed[i] for i in ids)/len(ids)-b['hit_rate'])<1e-12
                assert b['passed']==bool(b['null_passed'] and b['hit_rate']>=.5 and b['excess_ci'][0]>0)
        chain=f.v.load(folder/'STATUS.json')
        assert events[-1]['event']==('STOP' if chain['status'].startswith('FAIL') else 'COMPLETE')
    g5=out/'F/G5_published'
    if (g5/'generation.json').exists():
        generation=f.v.load(g5/'generation.json');assert generation['surrogate_used'] is False
        assert generation['published_commit']==reg['published_commit']
        assert (g5/'classes/de/voynich/text/SelfCitationTextGenerator.class').exists()
        for split,seed,n in [('train',4011,8776),('held',4012,13299)]:
            props=parse_properties((g5/split/'conf.properties').read_text(encoding='utf-8'))
            assert props['method.random.pseudo.seed']==str(seed) and props['method.canFollow']=='curveline'
            assert props['text.lines_to_create']=='4000'
            raw=(g5/split/'generated/text.txt').read_text(encoding='utf-8-sig')
            data=[l.strip() for l in raw.splitlines() if l.strip() and not l.lstrip().startswith('#')]
            expected=[word for line in data[1:] for word in line.split()][:n]
            assert expected==generation['words'][split] and len(expected)==n
    g6=out/'F/G6'
    if (g6/'generation.json').exists():
        gen=f.v.load(g6/'generation.json')
        for split in ['train','held']:
            result=f.v.load(g6/(split+'_generator.json'))['result'];table=result['table']
            expected=[''.join(table[a][b] for a,b in d['coordinates']) for d in result['draws'] if d['emitted']]
            assert expected==gen['words'][split]
    for name in ['G5_published','G6']:
        a=out/'F'/name/'word/stimuli.jsonl';b=out/'F'/name/'glyph/stimuli.jsonl'
        if a.exists() and b.exists():assert f.v.rd.sha(a)==f.v.rd.sha(b)
    f.check()
    result=dict(status='PASS',direction_trials_independently_recomputed=n_direction,
        composite_origin_trials_independently_recomputed=n_origin,
        checks=['registered inputs/instruments/prior runs unchanged','all new artifact hashes',
                'seal-score-key chronology','independent direction and shuffled-null arithmetic',
                'independent S-p1 profiles, joint orientation selection, hits and thresholds',
                'published G5 source/build/default-mode and literal-seed omission',
                'G6 reconstruction from saved table coordinates','matched signal cases','radial/target closure'])
    f.v.save(out/'VERIFICATION.json',result);print(json.dumps(result))


if __name__=='__main__':main()
