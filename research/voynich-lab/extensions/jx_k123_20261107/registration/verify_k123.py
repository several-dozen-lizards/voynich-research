"""Read-only arithmetic, chronology, source separation and preservation audit."""
import sys
sys.dont_write_bytecode=True
import json, math, random
from collections import Counter,defaultdict
import run_k123 as k

def readlines(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()]
def independent_score(words,model,parser,variant,pair,meta):
    p,q=k.j.PAIRS[pair];maps=meta[parser]['maps'];total=0
    for i,a in enumerate(words):
        b=words[(i+1)%len(words)]
        aa=list(a) if parser=='codepoints' else k.RD.units(a)
        bb=list(b) if parser=='codepoints' else k.RD.units(b)
        x,y,rx,ry=aa[p],bb[q],bb[p],aa[q]
        if variant=='matched':
            x=x if x in maps[p==-1] else '*';rx=rx if rx in maps[p==-1] else '*'
            y=y if y in maps[q==-1] else '*';ry=ry if ry in maps[q==-1] else '*'
        total+=math.log((model.get((x,y),0)+.5)/(model.get((rx,ry),0)+.5))
    return total/len(words)

def independent_ci(values,families,name,adjust):
    groups=defaultdict(lambda:[0.,0])
    for value,f in zip(values,families):groups[f][0]+=value;groups[f][1]+=1
    groups=list(groups.values());r=random.Random(k.seed(name));boot=[]
    for _ in range(2000):
        draws=[groups[r.randrange(len(groups))] for __ in groups]
        boot.append(sum(a for a,b in draws)/sum(b for a,b in draws))
    boot.sort();q=.025/7 if adjust else .025
    return [boot[math.floor(2000*q)],boot[math.ceil(2000*(1-q))-1]]

def main():
    k.check();out=k.OUT;reg=k.load(k.REG/'REGISTRATION.json')
    manifest=k.load(out/'ARTIFACT_MANIFEST.json')
    for p,h in manifest['hashes'].items():assert k.sha(out/p)==h,p
    events=readlines(out/'events.jsonl');assert reg['registered_utc']<events[0]['utc']
    lines=k.load(k.PREP/'lines.json');families=defaultdict(set)
    banned={k.RD.family(r['folio']) for r in k.j.rows(k.LAB/'results/ringdir/preflight/ring_inventory.csv')}
    for reading,rs in lines.items():
        for l in rs:
            assert l['family'] not in banned and '\ufffd' not in l['literal']
            families[l['split']].add(l['family'])
    assert families['train'].isdisjoint(families['heldout'])
    checked=0;intervals=0;panels=0
    for metricpath in out.rglob('metrics.json'):
        folder=metricpath.parent;panels+=1
        ev=readlines(folder/'events.jsonl');assert [x['event'] for x in ev]==['KEY_SEALED','SCORES_SAVED','KEY_OPENED']
        assert ev[0]['utc']<=ev[1]['utc']<=ev[2]['utc']
        assert ev[0]['sha256']==ev[2]['sha256']==k.sha(folder/'sealed/key.json')
        assert ev[1]['sha256']==k.sha(folder/'scores.jsonl')
        stimuli=readlines(folder/'stimuli.jsonl');scores=readlines(folder/'scores.jsonl');keys=k.load(folder/'sealed/key.json');trials=readlines(folder/'trials.jsonl')
        ms=k.load(folder/'models.json');metrics=k.load(metricpath);scope=folder.relative_to(out).parts[0]
        name='K1' if folder.name=='K1' else 'K2/'+folder.name
        for s,sc,key,t in zip(stimuli,scores,keys,trials):
            assert s['id']==sc['id']==key['id']==t['id'];assert key['family'] in families['heldout']
            for label,w in s['streams'].items():
                m=ms[label];target=-1 if key['reverse'] else 1
                for packed,count in m['counts'].items():
                    parser,variant,pair=packed.split('|');counts={(a,b):n for a,b,n in count}
                    v=independent_score(w,counts,parser,variant,pair,m['meta'])
                    assert math.isclose(v,sc['streams'][label]['scores'][packed],abs_tol=1e-12)
                    sign=0 if abs(v)<=1e-12 else (1 if v>0 else -1)
                    assert int(sign==target)==t['streams'][label]['correct'][packed]
                    checked+=1
                nw=sc['streams'][label]['null_words'];assert Counter(nw)==Counter(w)
                counts={(a,b):n for a,b,n in m['counts']['units|raw|J']}
                v=independent_score(nw,counts,'units','raw','J',m['meta'])
                assert math.isclose(v,sc['streams'][label]['null_J'],abs_tol=1e-12)
                assert len(w)==key['lengths'][label] and k.RD.BINS[key['bin']][0]<=len(w)<=k.RD.BINS[key['bin']][1]
            if 'C_shuf_within_line' in s:assert Counter(s['C_shuf_within_line'])==Counter(s['streams']['ZL'])
        for m in metrics['metrics']:
            xs=[t for t in trials if t['bin']==m['bin']];label=m['stream'];packed='|'.join([m['parser'],m['variant'],m['pair']])
            vals=[t['streams'][label]['correct'][packed] for t in xs];fs=[t['family'] for t in xs]
            assert math.isclose(sum(vals)/len(vals),m['accuracy'])
            if m['parser']=='units' and m['pair']=='J':
                stem=name+scope+label+str(m['bin'])+packed
                bounds=independent_ci(vals,fs,stem,scope!='aggregate');intervals+=1
                assert all(math.isclose(a,b,abs_tol=1e-12) for a,b in zip(bounds,m['ci']))
                assert m['passed']==(m['accuracy']>=.8 and bounds[0]>=.65)
                for other,c in m['contrasts'].items():
                    ds=[t['streams'][label]['correct'][packed]-t['streams'][label]['correct']['|'.join([m['parser'],m['variant'],other])] for t in xs]
                    assert math.isclose(sum(ds)/len(ds),c['margin'],abs_tol=1e-12)
                    bounds=independent_ci(ds,fs,stem+other,scope!='aggregate');intervals+=1
                    assert all(math.isclose(a,b,abs_tol=1e-12) for a,b in zip(bounds,c['ci']))
        nullpass=all(n['passed'] for n in metrics['nulls'].values())
        primary=[m for m in metrics['metrics'] if m['parser']=='units' and m['pair']=='J']
        expected='FAIL_NULL' if not nullpass else ('PASS' if (all(all(c['margin']>=.1 and c['ci'][0]>0 for c in m['contrasts'].values()) for m in primary) if name=='K1' else all(m['passed'] for m in primary)) else ('FAIL_SPECIFICITY' if name=='K1' else 'FAIL_ROBUSTNESS'))
        assert k.load(folder/'STATUS.json')['status']==expected
    summary=k.load(out/'summary.json')
    for row in summary:
        if row['arm']=='K2':
            stopped=False
            for p in row['panels']:
                path=out/row['scope']/'K2'/p['panel'];s=k.load(path/'STATUS.json')['status']
                assert s==p['status']
                if stopped:assert s=='NOT_RUN_UPSTREAM_FAILURE' and not (path/'scores.jsonl').exists()
                elif s!='PASS':stopped=True
    state=k.load(out/'STATUS.json');assert state['real_ring_scoring']=='CLOSED' and state['spacing_interpretation']=='CLOSED_FAILED_PHASE0'
    k.check()
    receipt=dict(status='PASS',panels_audited=panels,position_scores_recomputed=checked,primary_intervals_recomputed=intervals,
        source_family_separation=True,ring_families_excluded=True,key_chronology=True,stop_graph=True,prior_runs_unchanged=True,real_ring_scoring='CLOSED',spacing_interpretation='CLOSED',utc=k.now())
    k.save(out/'VERIFICATION.json',receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
