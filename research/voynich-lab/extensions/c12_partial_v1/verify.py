"""Independent data/codebook/accounting checks; no manuscript text is loaded."""
from common import *
from collections import Counter
import math,statistics
from src.encoders import encode,SIGLA
from src.phase3 import rng_for,load_words
def main():
    cfg=json.loads((I/'configs/phase3.json').read_text());cfg['encoder_aggressiveness']=.65;source,_=load_words(cfg['source_slices']['C1'],34509);bases={mode:encode(source,'C5',rng_for(1729,mode),cfg)[0] for mode in ['C5','C12']};count=0;checks=[]
    for s in settings():
        base=bases['C5' if s['mode']=='C5_external' else 'C12'];source_counts=Counter(''.join(base));record=json.loads((R/'data'/s['setting']/'encoder.json').read_text());meta=record['metadata'];book=meta['codebook'];selected=set(meta['selected']);retained=set(book)-selected;l=s['sequence_length'];inverse={v:k for k,v in book.items()};mapping={v:k for k,v in record['relabel_mapping'].items()}
        assert len(inverse)==len(book)==len(source_counts);assert all(book[c]==c for c in retained);assert all(len(book[c])==l and set(book[c])<=selected for c in selected)
        assert all(not b.startswith(a) for a in inverse for b in inverse if a!=b)
        expected_order=sorted(source_counts,key=lambda c:hashlib.sha256(('C12-partial-type-order-1729:'+c).encode()).hexdigest());assert expected_order==meta['sign_order']
        expected=set(SIGLA)&set(source_counts) if s['mode']=='sigla_only' else set(expected_order[:math.floor(s['fraction']*len(expected_order))]);assert selected==expected
        clean=read(R/'data'/s['setting']/'clean.csv');ws=[w for r in clean for w in r['text_eva'].split()];assert len(ws)==len(base)==34509;decoded=[];encoded_source=[]
        for w in ws:
            native=''.join(mapping[c] for c in w);encoded_source.append(native);pos=0;pieces=[]
            while pos<len(native):
                if native[pos] in retained:pieces.append(native[pos]);pos+=1
                else:pieces.append(inverse[native[pos:pos+l]]);pos+=l
            decoded.append(''.join(pieces))
        assert decoded==base
        selected_events=sum(source_counts[c] for c in selected);expected_chars=sum(source_counts.values())+(l-1)*selected_events;assert sum(map(len,ws))==expected_chars and selected_events==meta['expanded_occurrences'];count+=len(ws)
        checks.append(dict(setting=s['setting'],words=34509,types=len(book),selected_types=len(selected),expanded_occurrences=selected_events,character_accounting=True,roundtrip=True,prefix_free=True))
    dump(R/'INDEPENDENT_DATA_VERIFICATION.json',dict(status='PASS',words_roundtripped=count,settings=len(checks),checks=checks,manuscript_text_loaded=False))
    before=R/'run-before-table-fix.py.txt'
    if before.exists():
        old=before.read_text(encoding='utf8');new=(R/'run.py').read_text(encoding='utf8');assert old.replace("rows.append(dict(**manifest[s['setting'],version],**metric))","rows.append({**manifest[s['setting'],version],**metric})")==new
    if not (R/'model_runs.csv').exists():print(json.dumps(dict(data_verification='PASS',words=count,neural_verification='PENDING')));return
    plan=json.loads((R/'JOB_PLAN.json').read_text());rs=read(R/'model_runs.csv');assert len(rs)==len(plan)==940;lu={r['job']:r for r in rs};assert len(lu)==940;reused=trained=0
    for j in plan:
        r=lu[j['job']];assert r['tensor_sha256']==j['tensor_sha256'];folder=I/'runs'/j['job'];raw=json.loads((folder/'metrics.json').read_text());assert raw['seed']==j['seed'] and raw['with_position']==j['with_position'];assert int(r['parameter_count'])<5_000_000 and int(r['selected_step']) in [24,48,72,96]
        if j['status']=='TRAIN':assert r['status']=='TRAINED';trained+=1
        else:
            rr=json.loads((folder/'REUSE.json').read_text());p=R/rr['source'];assert sha(p)==rr['source_sha256'];origin=json.loads(p.read_text());assert raw['test_bpt']==origin['test_bpt'] and raw['validation_bpt']==origin['validation_bpt'];reused+=1
    gains=read(R/'position_gains_by_seed.csv')
    for r in gains:
        a=lu[f"{r['setting']}-{r['version']}-p0-s{r['seed']}"];b=lu[f"{r['setting']}-{r['version']}-p1-s{r['seed']}"];assert float(r['gain'])==float(a['test_bpt'])-float(b['test_bpt'])
    cached=json.loads((R/'reference/growth_and_lengths_extended.json').read_text());z={int(k):n for k,n in cached['ZL_running:T1']['word_length_distribution'].items()};nz=sum(z.values());results=read(R/'sweep_results.csv');lengths=json.loads((R/'growth_and_lengths.json').read_text())
    for r in results:
        c={int(k):n for k,n in lengths[r['setting']+':'+r['version']]['word_length_distribution'].items()};nc=sum(c.values());support=sorted(set(z)|set(c));value=0.
        for a,b in zip(support,support[1:]):value+=(b-a)*abs(sum(n for k,n in z.items() if k<=a)/nz-sum(n for k,n in c.items() if k<=a)/nc)
        assert abs(value-float(r['word_length_W1']))<1e-10
        within=(float(r['h2_distance'])<=float(r['h2_band']) and value<=float(r['word_length_band']) and float(r['gain_distance'])<=float(r['gain_band']));assert within==(r['all_three_within']=='True')
    snapshot=json.loads((R/'INPUT_SNAPSHOT.json').read_text());changed=[p for p,h in snapshot['original_lab_hashes'].items() if sha(LAB/p)!=h];reg=json.loads((R/'REGISTRATION.json').read_text());drift=[p for p,h in reg['files'].items() if sha(R/p)!=h];assert not drift
    dump(R/'VERIFICATION.json',dict(status='PASS' if not changed else 'PASS_WITH_SHARED_WORKSPACE_DRIFT',encoder_words=count,nominal_jobs=940,trained_jobs=trained,reused_jobs=reused,seed_gains_checked=len(gains),independent_W1_and_match_checks=len(results),exact_cache_replays=2,original_lab_drift=changed,frozen_drift=drift,new_manuscript_scores=0))
    print(json.dumps(dict(status='PASS',encoder_words=count,nominal_jobs=940,trained_jobs=trained,reused_jobs=reused,original_lab_drift=changed)))
if __name__=='__main__':main()
