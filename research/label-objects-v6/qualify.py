"""Frozen repeated synthetic controls; no manuscript outcomes are read."""
from common import *
from batch_cv import BatchCV,assignments
import t1, numpy as np, argparse, time

def interval(x,n):
    z=1.95996398454;p=x/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;radius=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,float(center-radius)),min(1,float(center+radius))]

def fixture(K,reading,regime):
    plan=load(ROOT/'CONTROL-PLAN.json');words=plan[reading+'_prototypes'][:K]
    perpage=12 if K==2 else 15
    types=np.tile(np.arange(perpage)%K,12);groups=np.repeat([f'f{i}' for i in range(1,13)],perpage)
    if regime=='balanced':y=types.copy()
    else:
        margins=[9,3] if K==2 else [7,5,3]
        y=np.tile(np.repeat(np.arange(K),margins),12)
    return [feature_dict(w) for w in words],types,groups,groups.copy(),y

def check_freeze():
    d=load(ROOT/'FREEZE.json')
    if d['tier']!='CLAIM_PROTOCOL_V6_1':raise ValueError('v6.1 claim seal missing')
    for name,value in d['hashes'].items():
        if sha(ROOT/name)!=value:raise ValueError('Frozen file changed: '+name)

def parity():
    check_freeze();results=[]
    for K in [2,3]:
        for reading in ['H','F']:
            prototypes,types,groups,pages,y=fixture(K,reading,'balanced')
            engine=BatchCV(prototypes,types,groups,pages,K)
            for case in range(2):
                rng=np.random.default_rng(79000+K*100+case)
                truth=t1.permute(y,pages,rng) if case else y.copy()
                if case==0:
                    for page in set(pages):
                        ix=np.flatnonzero(pages==page);a,b=rng.choice(ix,2,replace=False);truth[a],truth[b]=truth[b],truth[a]
                fast=engine.evaluate(truth,True)
                slow=t1.evaluate([prototypes[i] for i in types],truth,groups,pages)
                gap=abs(float(fast['gain'][0])-slow['gain']);assert gap<=2e-5,(K,reading,gap)
                csfast=[t['chosen_C'][0] for t in fast['trace']];csslow=[t['C'] for t in slow['tuning']]
                assert csfast==csslow,(K,reading,csfast,csslow)
                train,test=engine.outer[0];pdiff=0
                for C in t1.GRID:
                    pfast=engine.fit(truth[None,:],train,C)[0,types[test],:]
                    pslow=t1.fit_predict([prototypes[i] for i in types],truth,train,test,C,np.arange(K))
                    pdiff=max(pdiff,float(np.max(np.abs(pfast-pslow))))
                assert pdiff<=2e-5,pdiff
                results.append(dict(classes=K,reading=reading,case=case,gain_difference=gap,max_probability_difference=pdiff,selected_C_match=True))
                print('parity',K,reading,case,'passed',flush=True)
    save(ROOT/'controls/PARITY.json',dict(status='PASS',cases=results,original_engine_sha256=sha(ROOT/'t1.py'),batch_engine_sha256=sha(ROOT/'batch_cv.py')))

def banks():
    check_freeze()
    if load(ROOT/'controls/PARITY.json')['status']!='PASS':raise ValueError('Parity not passed')
    plan=load(ROOT/'CONTROL-PLAN.json')
    for K in [2,3]:
        for reading in ['H','F']:
            for regime in ['balanced','section']:
                name=f'{K}-{reading}-{regime}';dest=ROOT/'controls'/f'BANK-{name}.npz';receipt=dest.with_suffix('.json')
                if dest.exists() and receipt.exists():
                    assert sha(dest)==load(receipt)['output_sha256'];continue
                prototypes,types,groups,pages,y=fixture(K,reading,regime)
                seed=plan['bank_seeds'][name];Y=assignments(y,pages,plan['permutations'],seed)
                start=time.perf_counter();engine=BatchCV(prototypes,types,groups,pages,K)
                # Batches limit peak RAM; they do not alter any per-assignment fit or tune.
                outputs=[]
                for begin in range(0,len(Y),256):
                    outputs.append(engine.evaluate(Y[begin:begin+256]))
                    print('bank',name,min(begin+256,len(Y)),'/',len(Y),flush=True)
                combined={key:np.concatenate([r[key] for r in outputs]) for key in outputs[0]}
                np.savez_compressed(dest,**combined)
                save(receipt,dict(status='COMPLETE',permutations=plan['permutations'],seed=seed,rows=len(y),physical_folios=len(set(groups)),
                    class_page_margins='fixed by fixture()',seconds=time.perf_counter()-start,output_sha256=sha(dest),null_assignment_reuse='Only identical X/folds/page margins share this bank'))

def trials():
    check_freeze();plan=load(ROOT/'CONTROL-PLAN.json');records=[];summaries=[]
    for K in [2,3]:
        fixtures={};engines={};nulls={}
        for reading in ['H','F']:
            for regime in ['balanced','section']:
                f=fixture(K,reading,regime);fixtures[reading,regime]=f
                engines[reading,regime]=BatchCV(*f[:4],K)
                data=np.load(ROOT/'controls'/f'BANK-{K}-{reading}-{regime}.npz');nulls[reading,regime]=data['gain'][1:]
        for regime_index,regime in enumerate(['positive','section_only']):
            truth=[];sections=1 if regime=='positive' else 2
            basefixture=fixtures['H','balanced' if regime=='positive' else 'section']
            prototypes,types,groups,pages,y=basefixture
            for trial in range(plan['trials']):
                for section in range(sections):
                    seed=610241+K*100000+regime_index*10000+trial*10+section;rng=np.random.default_rng(seed)
                    if regime=='positive':
                        yy=types.copy()
                        for page in sorted(set(pages)):
                            ix=np.flatnonzero(pages==page)
                            for attempt in range(rng.binomial(len(ix)//2,.12)):
                                a,b=rng.choice(ix,2,replace=False);yy[a],yy[b]=yy[b],yy[a]
                    else:yy=t1.permute(y,pages,rng)
                    truth.append(dict(trial=trial,section=section,seed=seed,Y=yy))
            decisions={}
            for reading in ['H','F']:
                bankregime='balanced' if regime=='positive' else 'section'
                engine=engines[reading,bankregime];scores=engine.evaluate(np.stack([x['Y'] for x in truth]))
                for i,entry in enumerate(truth):
                    gain=float(scores['gain'][i]);p=(1+np.sum(nulls[reading,bankregime]>=gain-1e-12))/(plan['permutations']+1)
                    row=dict(classes=K,regime=regime,reading=reading,trial=entry['trial'],section=entry['section'],seed=entry['seed'],
                        gain=gain,p_raw=float(p),truth=entry['Y'].tolist());records.append(row)
                for trial in range(plan['trials']):
                    rr=[r for r in records if r['classes']==K and r['regime']==regime and r['reading']==reading and r['trial']==trial]
                    for r,p in zip(rr,t1.holm([r['p_raw'] for r in rr])):r.update(p_holm=p,passed=bool(p<=.05 and r['gain']>0))
                    decisions[reading,trial]=any(r['passed'] for r in rr)
            joint=sum(decisions['H',trial] and decisions['F',trial] for trial in range(plan['trials']))
            n=plan['trials'];passed=joint/n>=.8 if regime=='positive' else all(sum(decisions[r,t] for t in range(n))/n<=.05 for r in ['H','F']) and joint/n<=.05
            summaries.append(dict(classes=K,regime=regime,n=n,H_flags=sum(decisions['H',t] for t in range(n)),F_flags=sum(decisions['F',t] for t in range(n)),
                HF_joint_flags=joint,HF_joint_rate=joint/n,HF_joint_wilson95=interval(joint,n),passed=passed))
            print('trials',K,regime,summaries[-1],flush=True)
        # Page-only exact singleton orbit: full support but zero permissible change.
        nfolio=6*K;perpage=12 if K==2 else 15
        groups=np.repeat([f'f{i}' for i in range(1,nfolio+1)],perpage);types=np.tile(np.arange(perpage)%K,nfolio)
        y=np.repeat(np.arange(nfolio)%K,perpage)
        for reading in ['H','F']:
            prototypes=[feature_dict(w) for w in plan[reading+'_prototypes'][:K]]
            engine=BatchCV(prototypes,types,groups,groups,K);result=engine.evaluate(y)
            assert np.array_equal(t1.permute(y,groups,np.random.default_rng(717)),y)
            summaries.append(dict(classes=K,reading=reading,regime='page_only',n=100,flags=0,p_exact=1.,singleton_orbit_proved=True,
                observed_gain=float(result['gain'][0]),passed=True))
    save(ROOT/'controls/TRIALS.json',records);save(ROOT/'controls/SUMMARY.json',dict(status='PASS' if all(s['passed'] for s in summaries) else 'FAIL',results=summaries,
        limits='Conditional finite-prototype synthetic controls; shared-bank conditional rates, not a survey of historical texts, weak effects or all manuscript confounds.'))
    print('qualification',load(ROOT/'controls/SUMMARY.json')['status'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['parity','banks','trials']);args=ap.parse_args()
    globals()[args.stage]()
