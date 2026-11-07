"""RD-v2 registered, independent-arm calibration; no target text scoring."""
import argparse
import csv
import importlib.util
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
LAB=HERE.parents[1]
WORK=LAB.parent
REG=HERE/'registration'
OUT=LAB/'results/ringdir/v2'
FROZEN=LAB/'extensions/ringdir_v1/registration_v1/rd_phase0.py'
spec=importlib.util.spec_from_file_location('rdv1_frozen',FROZEN)
rd=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)
rd.LAB=LAB
SEED=2026110603
sys.path.insert(0,str(LAB/'.runtime'))
import numpy as np


def save(path,obj): rd.dump(path,obj)
def rows(path): return rd.readcsv(path)
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def rng(name): return random.Random(SEED+rd.stable(name))
def stamp(): return datetime.now(timezone.utc).isoformat()
def shared_namespace(folder): return '/'.join(p for p in folder.relative_to(OUT).parts if p not in {'word','glyph'})


def paths_to_bind():
    result={HERE/n for n in ['SPEC_USER_DRAFT.md','SPEC_WORKING_DRAFT.md','EXECUTION_FREEZE.md','run_v2.py','test_v2.py','verify_v2.py']}
    old=LAB/'extensions/ringdir_v1/registration_v1/REGISTRATION.json'
    result.update(LAB/n for n in load(old)['sha256'])
    for folder in [LAB/'results/ringdir/phase0_v1',LAB/'results/ringdir/circular_v2',
                   LAB/'extensions/ringdir_v1/registration_v1',LAB/'extensions/ringdir_circular_v2/registration']:
        result.update(p for p in folder.rglob('*') if p.is_file())
    result.update([WORK/'system-types-v5/GENERATORS/__init__.py',
                   LAB/'extensions/phase7_two_table_v1/author/naibbe.py',
                   LAB/'extensions/phase7_two_table_v1/author/naibbe_tables.csv'])
    return sorted(result)


def register():
    assert not OUT.exists()
    for prior in ['phase0_v1','circular_v2']:
        p=LAB/'results/ringdir'/prior
        for n,h in load(p/'ARTIFACT_MANIFEST.json')['sha256'].items():
            assert rd.sha(p/n)==h,(prior,n)
        assert load(p/'STATUS.json')['status']=='STOP_FAILED_GATE'
    REG.mkdir()
    save(REG/'REGISTRATION.json',dict(id='RD-v2',utc=stamp(),seed=SEED,python=sys.version,
        numpy=np.__version__,scope='Phase0 circular only; independent arm stops; no target scoring',
        hashes={str(p.relative_to(WORK)):rd.sha(p) for p in paths_to_bind()},
        unavailable=['S-dir-stem: exact Oct22 scripts unavailable','S-m: exact ending-table source unavailable',
                     'O combination: required S-m unavailable']))
    for n in ['EXECUTION_FREEZE.md','SPEC_WORKING_DRAFT.md','run_v2.py','test_v2.py','verify_v2.py']:
        (REG/n).write_bytes((HERE/n).read_bytes())
    print('REGISTERED RD-v2 before generation, fitting or scoring',flush=True)


def check():
    for n,h in load(REG/'REGISTRATION.json')['hashes'].items():
        assert rd.sha(WORK/n)==h,n


def event(folder,kind,**kw):
    with (folder/'events.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(event=kind,utc=stamp(),**kw))+'\n')


def seal(folder,stimuli,keys):
    rd.jsonlines(folder/'stimuli.jsonl',stimuli)
    (folder/'sealed').mkdir()
    save(folder/'sealed/key.json',keys)
    event(folder,'KEY_SEALED',sha256=rd.sha(folder/'sealed/key.json'),n=len(keys))


def scores_saved(folder,values):
    rd.jsonlines(folder/'scores.jsonl',values)
    event(folder,'SCORES_SAVED',sha256=rd.sha(folder/'scores.jsonl'))


def openkey(folder):
    event(folder,'KEY_OPENED',sha256=rd.sha(folder/'sealed/key.json'))
    return load(folder/'sealed/key.json')


def finish(folder,status,**kw):
    save(folder/'STATUS.json',dict(status=status,**kw))
    event(folder,'STOP' if status.startswith('FAIL') else 'COMPLETE',status=status)
    text=['# RD-v2 '+str(folder.relative_to(OUT)),'',f'**{status}**','',
          '```json',json.dumps(kw,indent=2,ensure_ascii=False),'```','',
          'Calibration only. No real-ring scores, radial arm or corrected-order export. '
          'Repeated windows/sets are conditional on the frozen source pool; source families '
          'are not multiplied into independent manuscript replications.','']
    (folder/'report.md').write_text('\n'.join(text),encoding='utf-8')
    print(str(folder.relative_to(OUT)),status,flush=True)
    return dict(chain=str(folder.relative_to(OUT)),status=status,**kw)


def eligible_inventory():
    inv=rows(LAB/'results/ringdir/preflight/ring_inventory.csv')
    selected,ledger=[],[]
    for r in inv:
        if r['type']!='circular': continue
        reason=[]
        if float(r['eva_codepoint_count'])/int(r['word_count'])<2: reason.append('codepoints_per_word_lt2')
        if float(r['unknown_word_count'])/int(r['word_count'])>.2: reason.append('unknown_fraction_gt20pct')
        if r['is_spurious']=='True' or r['is_alternate_branch']=='True': reason.append('spurious_or_branch')
        ledger.append(dict(locus=r['locus_id'],n=int(r['word_count']),eligible=not reason,reasons=';'.join(reason),
                           uncertainty=r['has_uncertainty'],family=rd.family(r['folio']),
                           source_locus_code=r['locus_code'],physical_group='NOT_INFERRED'))
        if not reason: selected.append(r)
    rd.table(OUT/'target_eligibility.csv',ledger)
    # Source-relative locator context is a ledger, not adjudicated ring geometry.
    raw=rows(LAB/'data/voynich/ZL_lines_corrected.csv')
    previous={}
    continuation=[]
    for r in raw:
        if r['locus_code'].startswith('+C'):
            continuation.append(dict(locus=r['line_id'],source_previous_locus=previous.get(r['folio'],''),
                                     locator=r['locus_code'],same_physical_ring='UNADJUDICATED'))
        previous[r['folio']]=r['line_id']
    rd.table(OUT/'continuation_context.csv',continuation)
    return selected


def make_runs(lines):
    runs=[]
    for l in lines:
        if (not runs or l['folio']!=runs[-1][-1]['folio'] or l['family']!=runs[-1][-1]['family'] or l['start'] or
            l['index']!=runs[-1][-1]['index']+1): runs.append([])
        runs[-1].append(l)
    return runs


def datasets(uncertain=False):
    inv,base,_,_,_,latinheld=rd.load_sources()
    source=rows(LAB/'data/voynich/ZL_lines_corrected.csv')
    rawmap={r['line_id']:r for r in source}
    if uncertain:
        banned={rd.family(r['folio']) for r in inv}
        base=[]
        for r in source:
            if r['locus_code'][1:] not in {'P0','P1','Pc','Pr','Pt'}: continue
            fam=rd.family(r['folio'])
            if (fam in banned or r['is_spurious']=='True' or r['has_missing_span']=='True' or
                '<->' in r['text_raw'] or '<~>' in r['text_raw'] or not r['line_index_in_paragraph']): continue
            words=r['text_eva'].split()
            if not words: continue
            base.append(dict(id=r['line_id'],folio=r['folio'],family=fam,
                split='train' if rd.stable('RD-v1-split|'+fam)/2**32<.60 else 'heldout',
                index=int(r['line_index_in_paragraph']),start=r['is_para_start']=='True',
                words=words,scribe=r['hand_scribe'],section=r['section']))
    for l in base: l['end']=rawmap[l['id']]['is_para_end']=='True'
    train=[r for r in base if r['split']=='train']
    held=[r for r in base if r['split']=='heldout']
    latinrows=rows(LAB/'data/controls/C1/clean.csv')
    inverse={v:k for k,v in load(LAB/'data/controls/C1/metadata.json')['symbol_mapping'].items()}
    decode=lambda w:''.join(inverse.get(c,c) for c in w)
    latinwords=[decode(w) for r in latinrows for w in r['text_eva'].split()]
    for run in latinheld:
        for line in run: line['words']=[decode(w) for w in line['words']]
    cut=int(len(latinwords)*.60)
    ltrain=[];lheld=[]
    for r in latinrows:
        a,b=int(r['source_word_start']),int(r['source_word_end'])
        split='train' if b<=cut else ('heldout' if a>=cut+128 and (a-cut-128)//512==(b-1-cut-128)//512 else None)
        if split is None: continue
        line=dict(id='C1line:'+str(a),folio=r['folio'],family='C1block:'+str((a-cut-128)//512),
                  words=[decode(w) for w in r['text_eva'].split()],index=int(r['line_index_in_paragraph']),
                  start=r['is_para_start']=='True',end=r['is_para_end']=='True',scribe='',section='')
        (ltrain if split=='train' else lheld).append(line)
    # D/P Latin uses source blocks, not remapped folio layout.
    trainlatin=[[dict(words=latinwords[:cut])]]
    return dict(ZL=dict(train=make_runs(train),held=make_runs(held),trainlines=train,heldlines=held),
                Latin=dict(train=trainlatin,held=latinheld,trainlines=ltrain,heldlines=lheld,
                           trainwords=latinwords[:cut],heldwords=latinwords[cut+128:]))


def badword(w): return '\ufffd' in w


def fit_models(data):
    word,glyph=Counter(),Counter()
    for run in data['train']:
        words=[w for l in run for w in l['words']]
        for a,b in zip(words,words[1:]):
            if badword(a) or badword(b): continue
            word[a,b]+=1
            glyph[rd.units(a)[-1],rd.units(b)[0]]+=1
    return dict(word=word,glyph=glyph)


def dscore(words,model,signal):
    if len(words)<2: return 0.,0.
    total=covered=0
    for a,b in zip(words,words[1:]+words[:1]):
        if badword(a) or badword(b): continue
        if signal=='word': forward,back=(a,b),(b,a)
        else:
            ua,ub=rd.units(a),rd.units(b)
            forward,back=(ua[-1],ub[0]),(ub[-1],ua[0])
        total+=math.log((model[forward]+.5)/(model[back]+.5))
        covered+=bool(model[forward] or model[back])
    return total/len(words),covered/len(words)


def transform(candidate,cid,r):
    return rd.make_case(candidate,cid,'circular','calibration',r)


def choose(pool,target,used,r):
    match='all_families'
    for label,pred in [('scribe+section',lambda c:c['scribe']==target['scribe'] and c['section']==target['section']),
                       ('scribe',lambda c:c['scribe']==target['scribe'])]:
        sub=[c for c in pool if pred(c)]
        if len({c['family'] for c in sub})>=8: pool,match=sub,label;break
    if not pool: return None,'UNAVAILABLE'
    minimum=min(used[c['source'],len(c['words'])] for c in pool)
    c=r.choice([c for c in pool if used[c['source'],len(c['words'])]==minimum])
    used[c['source'],len(c['words'])]+=1
    return c,match


def support(sub): return len({(r['source'],r['n']) for r in sub}),len({r['family'] for r in sub})
def ci(sub,field,name): return rd.bootstrap(sub,field,SEED+rd.stable(name))


def direction_chain(folder,data,targets,signal,model):
    folder.mkdir(parents=True)
    r=rng(shared_namespace(folder))
    rd.table(folder/'model.csv',[dict(a=a,b=b,count=n) for (a,b),n in sorted(model.items())])
    stimuli=[];keys=[];matching=[];cache={};used=Counter()
    bins=sorted({rd.binof(int(t['word_count'])) for t in targets})
    for b in bins:
        ts=[t for t in targets if rd.binof(int(t['word_count']))==b]
        cycle=[]
        while len(cycle)<200:
            cp=ts[:];r.shuffle(cp);cycle+=cp
        for i,t in enumerate(cycle[:200]):
            n=int(t['word_count'])
            if n not in cache: cache[n]=rd.candidates(data['held'],n)
            c,match=choose(cache[n],t,used,r)
            cid=f'b{b}-{i}'
            matching.append(dict(id=cid,n=n,target=t['locus_id'],match=match))
            if c is None: continue
            s,k=transform(c,cid,r);stimuli.append(s);keys.append(k)
    rd.table(folder/'matching.csv',matching)
    seal(folder,stimuli,keys)
    values=[]
    for s in rd.loadlines(folder/'stimuli.jsonl'):
        score,coverage=dscore(s['words'],model,signal)
        null=s['words'][:];r.shuffle(null)
        nv,_=dscore(null,model,signal)
        values.append(dict(id=s['id'],score=score,coverage=coverage,null_score=nv,null_words=null))
    scores_saved(folder,values)
    keyed=openkey(folder);lookup={v['id']:v for v in values}
    trials=[]
    for k in keyed:
        v=lookup[k['id']];target=-1 if k['reverse'] else 1
        trials.append(dict(**k,**{a:z for a,z in v.items() if a!='id'},
                           correct=int(rd.sign(v['score'])==target),
                           null_correct=int(rd.sign(v['null_score'])==target),null_tie=rd.sign(v['null_score'])==0))
    rd.table(folder/'trials.csv',trials)
    informative=[t for t in trials if not t['null_tie'] and t['n']>=3]
    nc=ci(informative,'null_correct',str(folder)+'null')
    na=sum(t['null_correct'] for t in informative)/len(informative) if informative else None
    npass=bool(len(informative)>=100 and len({t['family'] for t in informative})>=8 and
               .4<=na<=.6 and nc[0]>=.35 and nc[1]<=.65)
    null=dict(passed=npass,n_non_ties=len(informative),accuracy=na,cluster_ci=nc)
    save(folder/'null.json',null)
    metrics=[]
    for b in bins:
        sub=[t for t in trials if t['bin']==b]
        distinct,families=support(sub)
        acc=sum(t['correct'] for t in sub)/len(sub) if sub else 0
        interval=ci(sub,'correct',str(folder)+str(b))
        passed=bool(npass and distinct>=30 and families>=8 and acc>=.8 and interval[0]>=.65)
        metrics.append(dict(bin=b,length_min=rd.BINS[b][0],length_max=rd.BINS[b][1],n=len(sub),
            distinct_windows=distinct,families=families,accuracy=acc,cluster_ci=interval,
            ties=sum(rd.sign(t['score'])==0 for t in sub),
            mean_pair_coverage=sum(t['coverage'] for t in sub)/len(sub) if sub else None,passed=passed))
    save(folder/'bins.json',metrics)
    passing=[m['bin'] for m in metrics if m['passed']]
    status='FAIL_NULL' if not npass else ('PASS' if passing else 'FAIL_DIRECTION')
    return finish(folder,status,L_min=rd.BINS[min(passing)][0] if passing else None,
                  passing_bins=passing,null=null,bins=metrics)


def pooled_stat(words_by_member,families,model,signal,seed):
    # Cluster sign randomization, shared draws for weighted/unweighted versions.
    groups=sorted(set(families));index={f:i for i,f in enumerate(groups)}
    agg=np.zeros((len(groups),2))
    for words,fam in zip(words_by_member,families):
        val=rd.sign(dscore(words,model,signal)[0])
        agg[index[fam],0]+=val
        agg[index[fam],1]+=val*len(words)
    observed=agg.sum(axis=0)
    flips=np.random.default_rng(seed).integers(0,2,size=(1999,len(groups)))*2-1
    simulated=flips@agg
    p=(1+(np.abs(simulated)>=np.abs(observed)-1e-12).sum(axis=0))/2000
    calls=[int(np.sign(observed[i])) if p[i]<=.05 and observed[i]!=0 else 0 for i in range(2)]
    return dict(unweighted_call=calls[0],weighted_call=calls[1],unweighted_p=float(p[0]),weighted_p=float(p[1]),
                family_unweighted=agg[:,0].tolist(),family_weighted=agg[:,1].tolist())


def pooled_chain(folder,data,targets,signal,model):
    folder.mkdir(parents=True)
    r=rng(shared_namespace(folder))
    cache={n:rd.candidates(data['held'],n) for n in {int(t['word_count']) for t in targets}}
    stimuli=[];keys=[];unsupported=[]
    bins=sorted({rd.binof(int(t['word_count'])) for t in targets})
    for b in bins:
        ts=[t for t in targets if rd.binof(int(t['word_count']))==b]
        targetgroups=defaultdict(list)
        for t in ts: targetgroups[rd.family(t['folio'])].append(t)
        compatible={}
        for fam,group in targetgroups.items():
            sets=[{c['family'] for c in cache[int(t['word_count'])]} for t in group]
            compatible[fam]=set.intersection(*sets) if sets else set()
        for j in range(100):
            mapping={};taken=set()
            for fam in sorted(targetgroups,key=lambda x:(len(compatible[x]),x)):
                available=sorted(compatible[fam]-taken)
                if not available: break
                mapping[fam]=r.choice(available);taken.add(mapping[fam])
            if len(mapping)!=len(targetgroups):
                unsupported.append(dict(bin=b,set_index=j,reason='injective_family_mapping_unavailable'));continue
            originals=[];fams=[];sources=[];used=set();reuse=0
            for t in ts:
                fam=mapping[rd.family(t['folio'])];n=int(t['word_count'])
                pool=[c for c in cache[n] if c['family']==fam]
                fresh=[c for c in pool if (c['source'],n) not in used]
                if not fresh: reuse+=1
                c=r.choice(fresh or pool);used.add((c['source'],n))
                originals.append(c['words']);fams.append(fam);sources.append(c['source'])
            for cond in range(3):
                flags=[False]*len(ts) if cond==0 else ([True]*len(ts) if cond==1 else
                      [True]*(len(ts)//2+(j%2 if len(ts)%2 else 0))+[False]*(len(ts)-len(ts)//2-(j%2 if len(ts)%2 else 0)))
                if cond==2: r.shuffle(flags)
                members=[]
                for words,flag in zip(originals,flags):
                    seq=list(reversed(words)) if flag else words[:]
                    k=r.randrange(len(seq));members.append(seq[k:]+seq[:k])
                cid=f'b{b}-s{j}-c{cond}'
                stimuli.append(dict(id=cid,members=members,families=fams))
                keys.append(dict(id=cid,bin=b,condition=cond,set_index=j,n_members=len(ts),families=fams,
                                 sources=sources,reverse_flags=flags,reused_windows=reuse))
    rd.table(folder/'unsupported.csv',unsupported)
    seal(folder,stimuli,keys)
    values=[]
    for s in rd.loadlines(folder/'stimuli.jsonl'):
        values.append(dict(id=s['id'],**pooled_stat(s['members'],s['families'],model,signal,SEED+rd.stable(s['id']+shared_namespace(folder)))))
    scores_saved(folder,values)
    keyed=openkey(folder);vs={v['id']:v for v in values}
    trials=[]
    for k in keyed:
        v=vs[k['id']];expected=[1,-1,0][k['condition']]
        trials.append(dict(**k,**{a:z for a,z in v.items() if a!='id'},
                           unweighted_correct=int(v['unweighted_call']==expected),weighted_correct=int(v['weighted_call']==expected)))
    rd.jsonlines(folder/'trials.jsonl',trials)
    metrics=[]
    for b in bins:
        sub=[t for t in trials if t['bin']==b]
        rates={}
        for cond in range(3):
            ss=[t for t in sub if t['condition']==cond]
            for weight in ['unweighted','weighted']:
                rates[weight+'_'+str(cond)]=sum(t[weight+'_correct'] for t in ss)/len(ss) if ss else None
        families=len({f for t in sub for f in t['families']})
        passed=families>=8 and len(sub)==300 and all(v is not None and v>=.9 for v in rates.values())
        metrics.append(dict(bin=b,n_sets=len(sub),n_members=sub[0]['n_members'] if sub else None,
                            source_families=families,rates=rates,passed=passed))
    save(folder/'bins.json',metrics)
    passing=[m['bin'] for m in metrics if m['passed']]
    badnull=any(m['n_sets']==300 and any(m['rates'][w+'_2']<.9 for w in ['weighted','unweighted']) for m in metrics)
    return finish(folder,'FAIL_NULL' if badnull else ('PASS' if passing else ('FAIL_UNSUPPORTED' if not trials else 'FAIL_POOLED')),
                  null_failure_flag=badnull,
                  passing_bins=passing,bins=metrics)


def complete_paragraphs(lines):
    result=[]
    for run in make_runs(lines):
        if not run[0]['start'] or not run[-1]['end']: continue
        if any(l['end'] for l in run[:-1]): continue
        words=[w for l in run for w in l['words']]
        if 21<=len(words)<=80:
            result.append(dict(words=words,source=run[0]['id'],family=run[0]['family'],boundaries=[0],lines=len(run)))
    return result


def count_candidates(lines):
    result=[]
    for run in make_runs(lines):
        for start in range(len(run)):
            for k in range(1,6):
                chosen=run[start:start+k]
                if len(chosen)!=k: continue
                words=[w for l in chosen for w in l['words']]
                if 21<=len(words)<=80:
                    result.append(dict(words=words,source=chosen[0]['id']+f':k{k}',family=chosen[0]['family'],
                                       boundaries=[0],k=k,bin=rd.binof(len(words))))
    return result


def seam_counts(values,threshold):
    n=len(values);candidates=[]
    for i,v in enumerate(values):
        if v>threshold and v>=values[i-1] and v>=values[(i+1)%n]: candidates.append(i)
    # Collapse connected equal-height plateau representatives, including wraparound.
    reps=[]
    for i in candidates:
        connected={i};todo=[i]
        while todo:
            j=todo.pop()
            for z in [(j-1)%n,(j+1)%n]:
                if z in candidates and abs(values[z]-values[i])<=1e-12 and z not in connected:
                    connected.add(z);todo.append(z)
        if i==min(connected): reps.append(i)
    chosen=[]
    for i in sorted(reps,key=lambda x:(-values[x],x)):
        if all(min((i-j)%n,(j-i)%n)>=3 for j in chosen): chosen.append(i)
    return len(chosen)


def count_chain(folder,data):
    folder.mkdir(parents=True)
    candidates=count_candidates(data['heldlines'])
    support_rows=[];supported=[]
    for b in [4,5]:
        for cls in [1,2]:
            sub=[c for c in candidates if c['bin']==b and (c['k']==1 if cls==1 else c['k']>=2)]
            support_rows.append(dict(bin=b,binary_class=cls,n=len(sub),families=len({c['family'] for c in sub})))
        if all(s['n']>=30 and s['families']>=8 for s in support_rows[-2:]): supported.append(b)
    rd.table(folder/'support.csv',support_rows)
    if not supported: return finish(folder,'FAIL_UNSUPPORTED',reason='both binary classes require30 distinct windows and8 families',support=support_rows)
    r=rng(str(folder));stimuli=[];keys=[]
    for b in supported:
        one=[c for c in candidates if c['bin']==b and c['k']==1];r.shuffle(one)
        many=[]
        pools={k:[c for c in candidates if c['bin']==b and c['k']==k] for k in range(2,6)}
        for p in pools.values(): r.shuffle(p)
        while len(many)<200 and any(pools.values()):
            for k in range(2,6):
                if pools[k] and len(many)<200: many.append(pools[k].pop())
        take=min(200,len(one),len(many))
        for c in one[:take]+many[:take]:
            s,key=transform(c,str(len(keys)),r);key['true_k']=c['k'];stimuli.append(s);keys.append(key)
    seal(folder,stimuli,keys)
    pos=rd.fit_pos(data['trainlines']);values=[]
    for s in rd.loadlines(folder/'stimuli.jsonl'):
        profiles=rd.boundary_profile(s['words'],pos)
        nullmax=[]
        for _ in range(999):
            w=s['words'][:];r.shuffle(w);nullmax.append(max(rd.boundary_profile(w,pos)[0]))
        threshold=sorted(nullmax)[math.ceil(.99*999)-1]
        w=s['words'][:];r.shuffle(w);nullprof=rd.boundary_profile(w,pos)
        values.append(dict(id=s['id'],counts=[seam_counts(p,threshold) for p in profiles],threshold=threshold,
                           profiles=profiles,null_maxima=nullmax,null_words=w,
                           null_counts=[seam_counts(p,threshold) for p in nullprof]))
    scores_saved(folder,values);keyed=openkey(folder);lookup={v['id']:v for v in values};trials=[]
    for k in keyed:
        v=lookup[k['id']];idx=int(k['reverse']);count=v['counts'][idx]
        pred=1 if count==1 else 2 if count>=2 else 0
        trials.append(dict(**k,predicted_count=count,correct=int(pred==(1 if k['true_k']==1 else 2)),
                           exact=int(count==k['true_k']),null_called=int(v['null_counts'][idx]>0)))
    rd.table(folder/'trials.csv',trials)
    nullrate=sum(t['null_called'] for t in trials)/len(trials)
    if nullrate>.1: return finish(folder,'FAIL_NULL',null_false_positive_rate=nullrate)
    metrics=[]
    for b in supported:
        sub=[t for t in trials if t['bin']==b];acc=sum(t['correct'] for t in sub)/len(sub)
        interval=ci(sub,'correct',str(folder)+str(b))
        metrics.append(dict(bin=b,accuracy=acc,cluster_ci=interval,exact_accuracy=sum(t['exact'] for t in sub)/len(sub),
                            passed=acc>=.8 and interval[0]>=.65))
    save(folder/'bins.json',metrics)
    return finish(folder,'PASS' if any(m['passed'] for m in metrics) else 'FAIL_SEAM_COUNT',bins=metrics,null_false_positive_rate=nullrate)


def p1_fit(lines):
    first=[];other=[];lengths=[]
    for line in lines:
        flags=[int('p' in w or 'f' in w) for w in line['words']]
        (first if line['index']==0 else other).extend(flags)
        if line['index']==0: lengths.append(len(flags))
    return ((sum(first)+.5)/(len(first)+1),(sum(other)+.5)/(len(other)+1),max(1,round(statistics.median(lengths))))


def p1_profiles(words,model):
    pf,po,w=model;n=len(words)
    def value(i,reverse):
        indices=[(i-1-j)%n for j in range(w)] if reverse else [(i+j)%n for j in range(w)]
        return sum(math.log(pf/po) if ('p' in words[j] or 'f' in words[j]) else
                   math.log((1-pf)/(1-po)) for j in indices)/w
    return [[value(i,False) for i in range(n)],[value(i,True) for i in range(n)]]


def origin_chain(folder,data,signal,wordmodel):
    folder.mkdir(parents=True)
    candidates=complete_paragraphs(data['heldlines']);support_rows=[];supported=[]
    for b in [4,5]:
        sub=[c for c in candidates if rd.binof(len(c['words']))==b]
        families=len({c['family'] for c in sub})
        support_rows.append(dict(bin=b,n=len(sub),families=families))
        if len(sub)>=30 and families>=8:supported.append(b)
    rd.table(folder/'support.csv',support_rows)
    if not supported:return finish(folder,'FAIL_UNSUPPORTED',support=support_rows,reason='complete paragraphs lack30 windows/8 families in every bin')
    r=rng(str(folder));stimuli=[];keys=[]
    for c in candidates:
        if rd.binof(len(c['words'])) not in supported:continue
        s,k=rd.make_case(c,str(len(keys)),'circular','calibration',r,True);stimuli.append(s);keys.append(k)
    seal(folder,stimuli,keys)
    model=rd.fit_pos(data['trainlines']) if signal=='pos' else p1_fit(data['trainlines'])
    if signal=='p1':save(folder/'model.json',dict(first_rate=model[0],other_rate=model[1],window=model[2]))
    profile=(lambda w:rd.boundary_profile(w,model)) if signal=='pos' else (lambda w:p1_profiles(w,model))
    values=[]
    for s in rd.loadlines(folder/'stimuli.jsonl'):
        p=profile(s['words']);w=s['words'][:];r.shuffle(w);null=profile(w)
        ds,_=dscore(s['words'],wordmodel,'word')
        values.append(dict(id=s['id'],peaks=[rd.argmax_tie(z,r) for z in p],profiles=p,
                           null_words=w,null_profiles=null,
                           null_peaks=[rd.argmax_tie(z,r) for z in null],inferred_reverse=ds< -1e-12))
    scores_saved(folder,values);keyed=openkey(folder);lookup={v['id']:v for v in values};trials=[]
    for k in keyed:
        v=lookup[k['id']];acceptable=rd.window_union(k['boundaries'],k['n']);chance=len(acceptable)/k['n']
        hit=int(v['peaks'][int(k['reverse'])] in acceptable)
        endhit=int(v['peaks'][int(v['inferred_reverse'])] in acceptable)
        nullhit=int(v['null_peaks'][int(k['reverse'])] in acceptable)
        trials.append(dict(**k,hit=hit,end_to_end_hit=endhit,chance=chance,excess=hit-chance,null_excess=nullhit-chance))
    rd.table(folder/'trials.csv',trials);metrics=[]
    for b in supported:
        sub=[t for t in trials if t['bin']==b];ex=ci(sub,'excess',str(folder)+str(b)+'ex');nu=ci(sub,'null_excess',str(folder)+str(b)+'null')
        hit=sum(t['hit'] for t in sub)/len(sub);nullpass=-.15<=nu[0]<=0<=nu[1]<=.15
        metrics.append(dict(bin=b,n=len(sub),hit_rate=hit,end_to_end_hit_rate=sum(t['end_to_end_hit'] for t in sub)/len(sub),
            mean_chance=sum(t['chance'] for t in sub)/len(sub),excess_ci=ex,null_excess_ci=nu,
            null_passed=nullpass,passed=nullpass and hit>=.5 and ex[0]>0))
    save(folder/'bins.json',metrics)
    if not all(m['null_passed'] for m in metrics):return finish(folder,'FAIL_NULL',bins=metrics)
    return finish(folder,'PASS' if any(m['passed'] for m in metrics) else 'FAIL_ORIGIN',bins=metrics)


def fingerprint_data(name,latin,ntrain,nheld):
    plains={split:latin[key][:]
            for split,key in [('train','trainwords'),('held','heldwords')]}
    generated={};receipt={}
    if name.startswith('G'):
        spec=importlib.util.spec_from_file_location('rdv2_generators',WORK/'system-types-v5/GENERATORS/__init__.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        unit_words={}
        for split,n in [('train',ntrain),('held',nheld)]:
            if n>len(plains[split]):return None,dict(reason='nonwrapping Latin source too short')
            result=mod.generate(name,dict(abbreviation_probability=.35,symbol_probability=.6,null_probability=.1,
                max_expansion=3,allow_source_wrap=False,source_start=0),SEED+rd.stable(name+split),
                source=plains[split],line_lengths=[n])
            unit_words[split]=result['lines'][0];receipt[split]=dict(source_words=n,source_wraps=result['source_wraps'])
        vocab=sorted({u for stream in unit_words.values() for w in stream for u in w})
        mapping={u:chr(0xe000+i) for i,u in enumerate(vocab)}
        assert len(vocab)<0x1900
        generated={s:[''.join(mapping[u] for u in w) for w in stream] for s,stream in unit_words.items()}
        receipt['atomic_mapping']=mapping
    else:
        source=LAB/'extensions/phase7_two_table_v1/author/naibbe.py'
        csvpath=LAB/'extensions/phase7_two_table_v1/author/naibbe_tables.csv'
        namespace={'__name__':'rdv2_naibbe'}
        text=source.read_text(encoding='utf-8').replace('references/naibbe_tables.csv',csvpath.as_posix())
        exec(compile(text,str(source),'exec'),namespace)
        for split,n in [('train',ntrain),('held',nheld)]:
            namespace['random'].seed(SEED+rd.stable(name+split))
            words=namespace['encrypt_naibbe'](' '.join(plains[split]),namespace['naibbe_tables'],namespace['placeholder_to_glyph'])
            if len(words)<n:return None,dict(reason='nonwrapping Naibbe output too short',available=len(words),required=n)
            generated[split]=words[:n];receipt[split]=dict(available_output=len(words),retained=n,source_words=len(plains[split]))
        receipt['citation']='Greshko (2025), The Naibbe cipher, doi:10.1080/01611194.2025.2566408'
    held=[]
    for a in range(0,len(generated['held']),512):
        held.append([dict(words=generated['held'][a:a+512],source=f'{name}:{a}',id=f'{name}:{a}',family=f'{name}block:{a}',scribe='',section='')])
    data=dict(train=[[dict(words=generated['train'])]],held=held,trainlines=[],heldlines=[])
    return data,dict(receipt=receipt,generated=generated)


def plot_results(results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    chosen=[r for r in results if r['chain'].startswith('D/')]
    fig,axes=plt.subplots(1,2,figsize=(11,4),sharey=True)
    for ax,corpus in zip(axes,['ZL','Latin']):
        for signal in ['word','glyph']:
            result=next(r for r in chosen if r['chain']==f'D/{corpus}/{signal}')
            bins=result['bins'];ax.plot([b['length_min'] for b in bins],[b['accuracy'] for b in bins],'o-',label=signal)
        ax.axhline(.8,ls='--',color='gray');ax.set_title(corpus);ax.set_xlabel('Lower word-length bin edge');ax.legend();ax.set_ylim(0,1.03)
    axes[0].set_ylabel('Sealed reversal recovery; ties wrong');fig.suptitle('RD-v2 Arm D; full clustered intervals in bin tables')
    fig.tight_layout();fig.savefig(OUT/'direction_curves.png',dpi=150);plt.close(fig)


def mainrun():
    check();OUT.mkdir();save(OUT/'RUN_START.json',dict(utc=stamp(),registration_sha256=rd.sha(REG/'REGISTRATION.json')))
    targets=eligible_inventory();clean=[t for t in targets if t['has_uncertainty']=='False']
    data=datasets();udata=datasets(True);results=[]
    for arm,scope in [('D',data),('U',udata)]:
        for corpus in ['ZL','Latin']:
            models=fit_models(scope[corpus])
            for signal in ['word','glyph']:
                folder=OUT/arm/corpus/signal/('D' if arm=='U' else '')
                result=direction_chain(folder,scope[corpus],targets,signal,models[signal]);results.append(result)
                if arm=='U':
                    pfolder=OUT/arm/corpus/signal/'P'
                    if result['status']=='PASS':results.append(pooled_chain(pfolder,scope[corpus],targets,signal,models[signal]))
                    else:
                        pfolder.mkdir(parents=True);results.append(finish(pfolder,'NOT_RUN_UPSTREAM_FAILURE',dependency=result['chain']))
            if arm=='D':
                for signal in ['word','glyph']:
                    results.append(pooled_chain(OUT/'P'/corpus/signal,scope[corpus],clean,signal,models[signal]))
    for corpus in ['ZL','Latin']:
        models=fit_models(data[corpus])
        results.append(count_chain(OUT/'K'/corpus,data[corpus]))
        for signal in ['pos','p1']:
            results.append(origin_chain(OUT/'O'/corpus/signal,data[corpus],signal,models['word']))
    for name in ['G2','G3','G4','Naibbe']:
        folder=OUT/'F'/name;folder.mkdir(parents=True)
        nt=sum(len(l['words']) for l in data['ZL']['trainlines']);nh=sum(len(l['words']) for l in data['ZL']['heldlines'])
        generated,receipt=fingerprint_data(name,data['Latin'],nt,nh)
        save(folder/'generation.json',receipt)
        if generated is None:results.append(finish(folder,'NOT_RUN_SOURCE_TOO_SHORT',**receipt));continue
        models=fit_models(generated)
        for signal in ['word','glyph']:
            results.append(direction_chain(folder/signal,generated,targets,signal,models[signal]))
    for arm in ['D','P','U','O','F']:
        folder=OUT/arm/'missing_sources';folder.mkdir(parents=True)
        names=['stem'] if arm!='O' else ['S-m','specified_combination']
        results.append(finish(folder,'NOT_RUN_MISSING_SOURCE',signals=names))
    folder=OUT/'T';folder.mkdir()
    results.append(finish(folder,'REGISTERED_DESCRIPTIVE_ONLY',reason='no calibration analog; target comparisons closed'))
    check();plot_results(results)
    save(OUT/'SUMMARY.json',results)
    summary=[]
    for corpus in ['ZL','Latin','G2','G3','G4','Naibbe']:
        for signal in ['word','glyph','stem','pos','p1','S-m','combination']:
            def result(chain):return next((r for r in results if r['chain']==chain),None)
            d=result(f'D/{corpus}/{signal}');p=result(f'P/{corpus}/{signal}');u=result(f'U/{corpus}/{signal}/D')
            f=result(f'F/{corpus}/{signal}')
            up=result(f'U/{corpus}/{signal}/P')
            qualified_d=sorted(set(d.get('passing_bins',[]) if d and d['status']=='PASS' else []) &
                               set(u.get('passing_bins',[]) if u and u['status']=='PASS' else []))
            qualified_p=sorted(set(p.get('passing_bins',[]) if p and p['status']=='PASS' else []) &
                               set(up.get('passing_bins',[]) if up and up['status']=='PASS' else []))
            summary.append(dict(corpus=corpus,signal=signal,D_L_min=d.get('L_min') if d else None,
                D_status=d['status'] if d else ('NOT_RUN_MISSING_SOURCE' if signal=='stem' else 'NOT_APPLICABLE'),
                P_status=p['status'] if p else ('NOT_RUN_MISSING_SOURCE' if signal=='stem' else 'NOT_APPLICABLE'),
                U_D_status=u['status'] if u else 'NOT_RUN',U_P_status=up['status'] if up else 'NOT_RUN',
                matched_D_U_bins=json.dumps(qualified_d),matched_P_U_bins=json.dumps(qualified_p),
                K_status=(result(f'K/{corpus}') or {}).get('status','NOT_RUN'),
                O_pos_status=(result(f'O/{corpus}/pos') or {}).get('status','NOT_RUN'),
                O_p1_status=(result(f'O/{corpus}/p1') or {}).get('status','NOT_RUN'),F_L_min=f.get('L_min') if f else None,
                F_status=f['status'] if f else 'NOT_RUN'))
    rd.table(OUT/'summary.csv',summary)
    failed=[r['chain'] for r in results if r['status'].startswith('FAIL')]
    save(OUT/'STATUS.json',dict(status='PHASE0_COMPLETE_WITH_FAILURES' if failed else 'PHASE0_COMPLETE',failed_chains=failed,
        registered='RD-v2',prior_runs_unchanged=True,radial='HELD',real_ring_scores_computed=False,
        phases_1_plus_run=False,corrected_order_generated=False,utc=stamp()))
    text=['# RD-v2 Phase 0','', '| Chain | Outcome |','|---|---|']
    text += [f"| {r['chain']} | {r['status']} |" for r in results]
    text += ['', 'The registered arms are complete subject to the listed independent stops. Prior runs remain unchanged. '
             'No prior calibration pass was reused as a new gate pass. Radial text remains held; no real rings '
             'were scored, no Phase1+ comparison ran, and no corrected transcription was generated.','',
             'D/P clean calibration and U uncertainty calibration are distinct. U includes first-alternative '
             'uncertainty-bearing paragraphs with unknown barriers; Latin lacks independently annotated '
             'uncertainty and its U run is an unmarked control. K/O Latin uses artificial source layout. '
             'F is a fixed-seed engineering fingerprint, not identification of a historical mechanism.','',
             'See summary.csv for signal×corpus outcomes and each chain report for all bins/nulls/support. '
             'The predicted stem-collapse asymmetry and specified origin combination remain untested '
             'because their exact frozen sources are missing. Source windows overlap and Monte Carlo '
             'pooled sets share the fixed heldout pool. Clustered source intervals and conditional set '
             'reliability have different interpretations.','']
    (OUT/'report.md').write_text('\n'.join(text),encoding='utf-8')
    save(OUT/'ARTIFACT_MANIFEST.json',dict(hashes={str(p.relative_to(OUT)):rd.sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print('PHASE0 FINISHED; earlier runs unchanged; radial held; targets unscored',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','run'])
    register() if parser.parse_args().action=='register' else mainrun()
