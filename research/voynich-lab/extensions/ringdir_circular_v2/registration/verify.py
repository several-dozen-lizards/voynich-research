"""RD-C2 authored checks and read-only post-run verification."""
import json
import math
import random
import sys
from collections import Counter

import followup as f


def engineering():
    for n in [3,41,68,80]:
        words=[str(i) for i in range(n)]
        for seed in range(100):
            c=dict(words=words,boundaries=[0,n//2],source='authored',family='authored')
            s,k=f.rd.make_case(c,'toy','circular','ZL',random.Random(seed))
            assert f.original_words(s,k)==words
            bounds=[(b+k['rotate'])%n for b in k['boundaries']]
            if k['reverse']:
                bounds=[(n-b)%n for b in bounds]
            assert set(bounds)=={0,n//2}
    assert f.rd.binof(41)==f.rd.binof(80)==5
    assert f.rd.binof(40)!=5 and f.rd.binof(81)!=5
    print('PASS authored transform inversion, boundary inversion, scope endpoints (400 transforms)')


def verify():
    f.check_registered()
    out=f.OUT
    registration=json.loads((f.REG/'REGISTRATION.json').read_text())
    for name,expected in json.loads((out/'ARTIFACT_MANIFEST.json').read_text())['sha256'].items():
        assert f.rd.sha(out/name)==expected,name
    events=f.rd.loadlines(out/'events.jsonl')
    assert registration['utc']<events[0]['utc']
    sealed=next(i for i,e in enumerate(events) if e['event']=='KEY_SEALED')
    scored=next(i for i,e in enumerate(events) if e['event']=='SCORES_SAVED')
    opened=next(i for i,e in enumerate(events) if e['event']=='KEY_OPENED')
    assert sealed<scored<opened
    assert events[sealed]['sha256']==f.rd.sha(out/'sealed/keys.json')
    assert events[scored]['sha256']==f.rd.sha(out/'mirror_scores.jsonl')
    key=json.loads((out/'sealed/keys.json').read_text())
    stimuli={s['id']:s for s in f.rd.loadlines(out/'stimuli.jsonl')}
    mirror={s['id']:s for s in f.rd.loadlines(out/'mirror_stimuli.jsonl')}
    assert len(stimuli)==len(mirror)==200
    assert all(s['kind']=='circular' and s['corpus']=='ZL' and 41<=len(s['words'])<=80 for s in stimuli.values())
    assert all(k['kind']=='circular' and 41<=k['n']<=80 for ks in key.values() for k in ks)
    prior=json.loads((f.PRIOR/'sealed/keys.json').read_text())
    oldkeys={k['id']:k for k in prior['direction']}
    oldstim={s['id']:s for s in f.rd.loadlines(f.PRIOR/'stimuli.jsonl')}
    for k in key['direction']:
        old_id=k['id'][3:]
        assert f.original_words(stimuli[k['id']],k)==f.original_words(oldstim[old_id],oldkeys[old_id])
    # Independent training-count and log-probability arithmetic for S-int.
    eligible={r['locus_id'] for r in f.rd.readcsv(f.PRIOR/'paragraph_eligibility.csv')
              if r['eligible']=='True' and r['split']=='train'}
    clusters=sorted('ch sh cth ckh cph cfh ii iii in iin aiin qo ee'.split(),key=lambda x:(-len(x),x))
    def tokenize(word):
        result=[]
        while word:
            unit=next((u for u in clusters if word.startswith(u)),word[0])
            result.append(unit)
            word=word[len(unit):]
        return result
    counts=[Counter(),Counter(),Counter()]
    vocab=set()
    for line in f.rd.readcsv(f.LAB/'data/voynich/ZL_lines_corrected.csv'):
        if line['line_id'] not in eligible:
            continue
        for word in line['text_eva'].split():
            u=tokenize(word)
            if len(u)<2:
                continue
            for i,x in enumerate(u):
                c=0 if i==0 else 2 if i==len(u)-1 else 1
                counts[c][x]+=1
                vocab.add(x)
    totals=[sum(c.values())+.5*len(vocab) for c in counts]
    def score(wordunits):
        values=[]
        for u in wordunits:
            if len(u)<2:
                continue
            value=0
            for i,x in enumerate(u):
                c=0 if i==0 else 2 if i==len(u)-1 else 1
                value+=math.log(counts[c][x]+.5)-math.log(totals[c])
            values.append(value/len(u))
        return sum(values)/len(values) if values else 0.
    scores={r['id']:r for r in f.rd.loadlines(out/'mirror_scores.jsonl')}
    correct=0
    for k in key['mirror']:
        s=mirror[k['id']]
        u=[tokenize(w) for w in s['words']]
        assert s['mirror_words']==([list(reversed(x)) for x in u] if k['mirrored'] else u)
        a=score(s['mirror_words'])
        b=score([list(reversed(x)) for x in s['mirror_words']])
        assert abs(a-scores[k['id']]['forward'])<1e-10
        assert abs(b-scores[k['id']]['reversed'])<1e-10
        predicted=0 if abs(a-b)<=1e-12 else (1 if a>b else -1)
        correct+=int(predicted==(-1 if k['mirrored'] else 1))
    gate=json.loads((out/'mirror_gate.json').read_text())
    assert abs(gate['accuracy']-correct/200)<1e-12
    assert gate['passed']==(correct/200>=.90 and gate['distinct_windows']>=30 and gate['families']>=8)
    status=json.loads((out/'STATUS.json').read_text())
    assert status['radial']=='HELD' and status['prior_run_hashes_unchanged']
    assert not status['real_ring_scores_computed'] and not status['phases_1_to_4_run']
    assert not status['corrected_order_generated']
    stages=['unit_mirror','any_boundary','unique_origin','boundary_pairing_null']
    if status['stopped_at']:
        stop=stages.index(status['stopped_at'])
        assert status['gates'][-1]['passed'] is False
        assert all(status['phase_stages'][s]=='NOT_RUN' for s in stages[stop+1:])
        assert events[-1]['event']=='STOP'
        scoredstages={e['stage'] for e in events if e['event']=='SCORES_SAVED'}
        assert not scoredstages.intersection(set(stages[stop+1:]))
    for name in ['any_boundary','unique_origin']:
        path=out/(name+'_gates.json')
        if not path.exists():
            continue
        for g in json.loads(path.read_text()):
            assert g['bin']==5
            passed=(g['distinct_windows']>=30 and g['families']>=8 and g['hit_rate']>=.5 and
                g['end_to_end_hit_rate']>=.5 and g['excess_ci'][0]>0 and g['end_to_end_excess_ci'][0]>0 and
                -.15<=g['null_excess_ci'][0]<=0<=g['null_excess_ci'][1]<=.15)
            assert g['passed']==passed
    f.check_registered()
    result=dict(status='PASS',scope='RD-C2 execution verification, not scientific qualification',
        checks=['prior-run bytes unchanged including failed status/verification',
                'registered instruments and inputs unchanged','new artifact hashes',
                'new registration/seal/score/key chronology',
                '200 circular-only windows, lengths 41–80, inherited source identity',
                'independent mirror tokenization/counts/score and accuracy arithmetic',
                'boundary-gate thresholds when reached','sequential stop and radial/target closure'])
    f.rd.dump(out/'VERIFICATION.json',result)
    print(json.dumps(result))


if __name__=='__main__':
    engineering() if len(sys.argv)>1 and sys.argv[1]=='engineering' else verify()
