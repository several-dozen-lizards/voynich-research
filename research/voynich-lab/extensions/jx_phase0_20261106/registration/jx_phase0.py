"""JX Phase 0 only. No manuscript feature scoring, no real-ring scoring."""
import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
import traceback
from collections import Counter,defaultdict
from datetime import datetime,timezone
from functools import lru_cache
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[1];WORK=LAB.parent
sys.path.insert(0,str(LAB/'extensions/ringdir_v2'))
import run_v2 as old
import numpy as np
RD=old.rd
REVIEW=LAB/'extensions/jx_review_20261106'
FROZEN=HERE/'candidate_freeze';REG=HERE/'registration'
OUT=LAB/'results/jx/JX-20261106-P0-1'
MASTER=2026110605
NT=8776;NH=13299;B=1000
PAIRS={'J':(-1,0),'SS':(0,0),'EE':(-1,-1),'SE':(0,-1)}
ALPHA='abdfgl'

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):old.save(p,x)
def rows(p):return old.rows(p)
def sha(p):return RD.sha(p)
def now():return datetime.now(timezone.utc).isoformat()
def seed(s):return MASTER+int(hashlib.sha256(s.encode()).hexdigest()[:12],16)
def rng(s):return random.Random(seed(s))
@lru_cache(maxsize=200000)
def units(w):return tuple(RD.units(w))

def approve():
    FROZEN.mkdir()
    source=REVIEW/'corrected_r1/CANDIDATE_REGISTER_CORRECTED_R1.md'
    text=source.read_text(encoding='utf-8')
    ids=[l.split('|')[1].strip() for l in text.splitlines() if l.startswith('| T')]
    assert len(ids)==len(set(ids))==36 and text.count('NP — uncalibrated')==36
    target=FROZEN/'CANDIDATES_APPROVED_PAYLOAD.md';target.write_bytes(source.read_bytes())
    save(FROZEN/'APPROVAL.json',dict(status='APPROVED_AND_FROZEN',recorded_utc=now(),
        authority='User explicitly approved corrected candidate list including NP predictions and requested freeze.',
        source=str(source),source_sha256=sha(source),frozen_payload_sha256=sha(target),candidate_ids=ids,
        operational_predictions='NP for all36; no language ranking',
        header_note='Payload preserves the historical review-draft header verbatim; this receipt records current approval.'))
    print('FROZEN approved36-row candidate payload; NP preserved',flush=True)

def bind():
    assert load(FROZEN/'APPROVAL.json')['status']=='APPROVED_AND_FROZEN'
    folder=HERE/'binding';folder.mkdir()
    counts=rows(LAB/'results/ringdir/preflight/all_locus_code_counts.csv')
    names={'H':'Takahashi','U':'Stolfi','V':'Grove','C':'Currier plus additions','F':'First Study Group plus edits',
        'T':'Tiltman','L':'Latham','R':'Roe','K':'Kluge','J':'Reeds','N':'Landini','P':'Petersen reports','X':'Mardle','Z':'Zandbergen'}
    codes=sorted({r['transcriber'] for r in counts if r['corpus']=='LSI'})
    ledger=[]
    for code in codes:
        ledger.append(dict(code=code,name=names.get(code,'unfolded alternative' if code in 'DGIQM' else 'unresolved'),
            ancestry='derived' if code in 'DGIQM' else 'unresolved',
            ordinary_paragraph_records=sum(int(r['n']) for r in counts if r['corpus']=='LSI' and r['transcriber']==code and r['locus_code'][1:] in {'P0','P1','Pc','Pr','Pt'}),
            independently_qualified=False,note='Named source identity is not locus-level independence proof.'))
    RD.table(folder/'transcription_inventory.csv',ledger)
    eligibility={r['locus_id']:r for r in rows(LAB/'results/ringdir/phase0_v1/paragraph_eligibility.csv') if r['eligible']=='True'}
    groups=defaultdict(set)
    # Metadata join only: no text field is used or scored.
    for r in rows(LAB/'data/voynich/ZL_lines_corrected.csv'):
        if r['line_id'] not in eligibility:continue
        e=eligibility[r['line_id']]
        if e['split']!='heldout':continue
        for kind,value in [('Currier_variety',r['currier_lang']),('Davis_scribe',r['hand_scribe'])]:
            if value:groups[kind,value].add(e['family'])
    RD.table(folder/'stratum_coverage_metadata.csv',[dict(kind=k,label=l,heldout_families=len(fs),
        minimum_family_count_met=len(fs)>=8,feature_qualification='NOT_RUN') for (k,l),fs in sorted(groups.items())])
    geometry=rows(LAB/'results/ringdir/v2/target_eligibility.csv')
    lengths={str(b):[int(r['n']) for r in geometry if r['eligible']=='True' and RD.binof(int(r['n']))==b] for b in [3,4]}
    assert all(lengths.values())
    save(folder/'EXECUTABLE_MANIFEST.json',dict(id='JX-20261106-P0-1',master_seed=MASTER,train_words=NT,heldout_words=NH,
        length_metadata=lengths,case_count_per_bin=200,block_words=512,bootstrap_draws=2000,permutations=1000,
        banks={'C-zero':100,'C-junc':20,'C-prog':20,'C-SS':1,'C-EE':1,'C-order':1},
        chain_graph={'K1':['zero_false_specificity','C-junc','C-SS','C-EE','C-order'],
            'I1':['zero_FWER','directional_positive_banks','regressive_Latin_added_rewrite'],
            'I2':['paired_source_reference_ordering'],
            'target_K1_K2_K3_I':'NOT_AUTHORIZED','real_rings':'CLOSED','C-shuf':'NOT_RUN_TARGET_DERIVED',
            'I1-full':'NOT_RUN_MISSING_SOURCE'},
        code_specification='EXECUTION.md and jx_phase0.py are normative executable bindings',
        candidate_payload_sha256=sha(FROZEN/'CANDIDATES_APPROVED_PAYLOAD.md'),np_predictions_preserved=True))
    print('BOUND metadata/source/control manifest; no features scored',flush=True)

def bind_paths():
    files={HERE/n for n in ['EXECUTION.md','jx_phase0.py','test_jx.py','verify_jx.py']}
    for folder in [FROZEN,HERE/'binding',REVIEW/'corrected_r1']:
        files.update(p for p in folder.rglob('*') if p.is_file())
    previous=load(LAB/'extensions/ringdir_followup_v3/registration/REGISTRATION.json')
    files.update(WORK/n for n in previous['hashes'])
    for folder in ['results/ringdir/phase0_v1','results/ringdir/circular_v2','results/ringdir/v2','results/ringdir/followup_v3',
                   'extensions/ringdir_followup_v3/registration']:
        files.update(p for p in (LAB/folder).rglob('*') if p.is_file())
    files.update([LAB/'src/parse_ivtff.py',LAB/'results/ringdir/preflight/all_locus_code_counts.csv'])
    return sorted(files)

def register():
    assert not OUT.exists();REG.mkdir()
    approved=load(FROZEN/'APPROVAL.json')
    assert approved['frozen_payload_sha256']==sha(FROZEN/'CANDIDATES_APPROVED_PAYLOAD.md')
    # Check complete previous-result manifests before registering, never overwrite them.
    for name in ['phase0_v1','circular_v2','v2','followup_v3']:
        root=LAB/'results/ringdir'/name;m=load(root/'ARTIFACT_MANIFEST.json')
        for path,h in m.get('hashes',m.get('sha256',{})).items():assert sha(root/path)==h,(name,path)
    excluded=[r for r in load(REVIEW/'REVIEW_STATUS.json')['sources'] if r['source'].endswith('.pdf')]
    save(REG/'REGISTRATION.json',dict(id='JX-20261106-P0-1',utc=now(),python=sys.version,numpy=np.__version__,
        authority='Approved candidate freeze and Phase0 only; no target scoring',
        hashes={str(p.relative_to(WORK)):sha(p) for p in bind_paths()},preservation_only_excluded_pdf=excluded))
    for n in ['EXECUTION.md','jx_phase0.py','test_jx.py','verify_jx.py']:(REG/n).write_bytes((HERE/n).read_bytes())
    print('REGISTERED JX Phase0 before generation/fitting/scoring',flush=True)

def check():
    r=load(REG/'REGISTRATION.json')
    for n,h in r['hashes'].items():assert sha(WORK/n)==h,n
    for item in r['preservation_only_excluded_pdf']:
        for k in ['source','review_copy']:assert sha(Path(item[k]))==item['sha256']

def event(folder,name,**x):
    with (folder/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(event=name,utc=now(),**x))+'\n')
def finish(folder,status,**x):
    save(folder/'STATUS.json',dict(status=status,**x));event(folder,'STOP' if status.startswith(('FAIL','UNSUPPORTED')) else 'COMPLETE',status=status)
    (folder/'report.md').write_text('# JX Phase0 '+folder.relative_to(OUT).as_posix()+'\n\n**'+status+'**\n\n```json\n'+json.dumps(x,indent=2)+'\n```\n',encoding='utf-8')
    print(folder.relative_to(OUT).as_posix(),status,flush=True)
    return dict(chain=folder.relative_to(OUT).as_posix(),status=status,**x)

def chunks(words):return [words[i:i+512] for i in range(0,len(words),512)]

def toy(mode,n,r):
    starts=[r.choice(ALPHA) for _ in range(n+1)];ends=[r.choice(ALPHA) for _ in range(n+1)]
    states=[]
    if mode in ['SS','EE','ORDER']:
        k=3 if mode=='ORDER' else 6;s=r.randrange(k)
        for i in range(n):
            states.append(s);s=(s+1)%k if r.random()<.9 else r.randrange(k)
        if mode=='SS':starts[:n]=[ALPHA[s] for s in states]
        if mode=='EE':ends[:n]=[ALPHA[s] for s in states]
    if mode=='REG':ends[:n]=[ALPHA[2*(ALPHA.index(starts[i+1])//2)+r.randrange(2)] for i in range(n)]
    if mode=='PROG':starts[1:n]=[ALPHA[2*(ALPHA.index(ends[i-1])//2)+r.randrange(2)] for i in range(1,n)]
    words=[]
    for i in range(n):
        mid=format(r.randrange(256),'08b').translate(str.maketrans('01','xv'))
        a,z=starts[i],ends[i]
        if mode=='ORDER':
            a,z=r.choice(ALPHA[:4]),r.choice(ALPHA[:4]);mid=['xvx','vxx','vvx'][states[i]]
        word=a+(ALPHA[ALPHA.index(a)//2] if mode=='REG' else 'z')+mid+(ALPHA[ALPHA.index(z)//2] if mode=='PROG' else 'z')+z
        assert units(word)==tuple(word),'Rendering changed intended units'
        words.append(word)
    if mode=='REG':assert all(ALPHA.index(words[i][-1])//2==ALPHA.index(words[i+1][0])//2 for i in range(n-1))
    if mode=='PROG':assert all(ALPHA.index(words[i][0])//2==ALPHA.index(words[i-1][-1])//2 for i in range(1,n))
    return words

def prepare_bank():
    bank=OUT/'bank';bank.mkdir()
    for name,mode,count in [('C-zero','ZERO',100),('C-junc','REG',20),('C-prog','PROG',20),('C-SS','SS',1),('C-EE','EE',1),('C-order','ORDER',1)]:
        folder=bank/name;folder.mkdir()
        for i in range(count):
            train=toy(mode,NT,rng(f'{name}/{i}/train'));held=toy(mode,NH,rng(f'{name}/{i}/held'))
            save(folder/f'{i:03d}.json',dict(name=name,member=i,mode=mode,train=train,held=chunks(held),
                train_seed=seed(f'{name}/{i}/train'),held_seed=seed(f'{name}/{i}/held'),render_roundtrip_pass=True,
                source_families_are='synthetic512-word clusters; independent bank draws, not manuscripts'))
    print('Synthetic bank generated and rendering-qualified',flush=True)

def latin_source():
    rs=rows(LAB/'data/controls/C1/clean.csv');offset=0;words=[]
    inverse={v:k for k,v in load(LAB/'data/controls/C1/metadata.json')['symbol_mapping'].items()}
    for r in rs:
        assert int(r['source_word_start'])==offset
        w=r['text_eva'].split();offset+=len(w);assert offset==int(r['source_word_end'])
        words.extend(''.join(inverse.get(c,c) for c in x) for x in w)
    cut=int(len(words)*.6)+128
    assert cut+NH<=len(words) and NT<cut
    return dict(train=chunks(words[:NT]),held=chunks(words[cut:cut+NH])),dict(train_span=[0,NT],held_span=[cut,cut+NH],total_words=len(words))

def rewrite(block,r):
    result=block[:];changes=[]
    for i,w in enumerate(block[:-1]):
        nxt=block[i+1]
        rule=None;new=w
        if w.endswith('m') and nxt[0] in 'dtn':rule='m_to_n_before_dtn';new=w[:-1]+'n'
        elif len(w)>=3 and w[-1] in 'aeiou' and nxt[0] in 'aeiou':rule='final_vowel_elision';new=w[:-1]
        if rule:
            draw=r.random();applied=draw<.8
            if applied:result[i]=new
            changes.append(dict(index=i,before=w,after=new if applied else w,rule=rule,draw=draw,applied=applied))
    return result,changes

def prepare_references():
    base,spans=latin_source();root=OUT/'references';root.mkdir();refs={'C-lat':base,'C-sandhi':{'train':[],'held':[]},'C-respace':{'train':[],'held':[]},'C-naibbe':{'train':[],'held':[]}}
    source=LAB/'extensions/phase7_two_table_v1/author/naibbe.py';csv=source.with_name('naibbe_tables.csv')
    ns={'__name__':'jx_naibbe'};text=source.read_text(encoding='utf-8').replace('references/naibbe_tables.csv',csv.as_posix())
    exec(compile(text,str(source),'exec'),ns)
    mutations={};boundaries={}
    for split,blocks in base.items():
        mutations[split]=[];boundaries[split]=[]
        for j,block in enumerate(blocks):
            mod,log=rewrite(block,rng(f'rewrite/{split}/{j}'));refs['C-sandhi'][split].append(mod);mutations[split].append(log)
            plain=' '.join(block);stream=''.join(block)
            ns['random'].seed(seed(f'respace/{split}/{j}'))
            resp=ns['respace_plaintext'](plain);assert ''.join(resp)==stream
            refs['C-respace'][split].append(resp)
            ns['random'].seed(seed(f'naibbe/{split}/{j}'))
            cipher=ns['encrypt_naibbe'](plain,ns['naibbe_tables'],ns['placeholder_to_glyph'])
            refs['C-naibbe'][split].append(cipher)
            oldoffs=np.cumsum([len(w) for w in block]).tolist()[:-1];new=np.cumsum([len(w) for w in resp]).tolist()[:-1]
            boundaries[split].append(dict(block=j,source_offsets=oldoffs,respaced_offsets=new,
                coincident=len(set(oldoffs)&set(new)),source_chars=len(stream),source_words=len(block),respaced_words=len(resp),cipher_words=len(cipher),
                respacing_seed=seed(f'respace/{split}/{j}'),cipher_seed=seed(f'naibbe/{split}/{j}')))
    for name,data in refs.items():save(root/(name+'.json'),dict(name=name,full=data,source_spans=spans,
        citation='Greshko (2025), doi:10.1080/01611194.2025.2566408' if name in ['C-respace','C-naibbe'] else None))
    save(root/'rewrite_receipts.json',mutations);save(root/'boundary_receipts.json',boundaries)
    return refs

def token_matched(data,base):
    out={}
    for split,blocks in data.items():
        out[split]=[]
        for j,w in enumerate(blocks):
            need=len(base[split][j]);assert len(w)>=need,'Transformed source block too short'
            out[split].append(w[:need])
    return out

def parsed(w,parser):return units(w) if parser=='units' else tuple(w)
def maps_for(train,parser):
    a=Counter();z=Counter()
    for block in train:
        for w in block:u=parsed(w,parser);a[u[0]]+=1;z[u[-1]]+=1
    k=min(11,len(a)-1,len(z)-1)
    maps=[];diagnostics=[]
    for counts in [a,z]:
        top=[x for x,n in sorted(counts.items(),key=lambda q:(-q[1],q[0]))[:max(0,k)]]
        maps.append(set(top));n=sum(counts.values())
        diagnostics.append(dict(categories=len(counts),entropy=-sum(c/n*math.log2(c/n) for c in counts.values()),OTHER_mass=sum(c for u,c in counts.items() if u not in top)/n))
    return k,maps,diagnostics

def models_for(train):
    models={};meta={}
    for parser in ['units','codepoints']:
        k,maps,diag=maps_for(train,parser);meta[parser]=dict(k=k,maps=[sorted(s) for s in maps],diagnostics=diag)
        for variant in ['raw','matched']:
            for name,(p,q) in PAIRS.items():
                c=Counter()
                for block in train:
                    for a,b in zip(block,block[1:]):
                        x,y=parsed(a,parser)[p],parsed(b,parser)[q]
                        if variant=='matched':x=x if x in maps[int(p==-1)] else '*';y=y if y in maps[int(q==-1)] else '*'
                        c[x,y]+=1
                models[parser,variant,name]=c
    word=Counter((a,b) for block in train for a,b in zip(block,block[1:]))
    return models,meta,word

def pair_score(words,model,parser,variant,pair,meta):
    p,q=PAIRS[pair];maps=[set(x) for x in meta[parser]['maps']];total=0
    for a,b in zip(words,words[1:]+words[:1]):
        ua,ub=parsed(a,parser),parsed(b,parser);x,y=ua[p],ub[q];rx,ry=ub[p],ua[q]
        if variant=='matched':
            x=x if x in maps[int(p==-1)] else '*';rx=rx if rx in maps[int(p==-1)] else '*'
            y=y if y in maps[int(q==-1)] else '*';ry=ry if ry in maps[int(q==-1)] else '*'
        total+=math.log((model[x,y]+.5)/(model[rx,ry]+.5))
    return total/len(words)

def cases_for(held,name):
    r=rng('cases/'+name);stimuli=[];keys=[];lengths=load(HERE/'binding/EXECUTABLE_MANIFEST.json')['length_metadata'];used=set()
    for bs,ns in lengths.items():
        cycle=[]
        while len(cycle)<200:cp=ns[:];r.shuffle(cp);cycle+=cp
        for j,n in enumerate(cycle[:200]):
            options=[(f,i) for f,block in enumerate(held) for i in range(0,len(block)-n+1,10)]
            fresh=[x for x in options if (x[0],x[1],n) not in used];f,i=r.choice(fresh or options);used.add((f,i,n))
            words=held[f][i:i+n];rev=r.random()<.5;off=r.randrange(n)
            if rev:words=list(reversed(words))
            words=words[off:]+words[:off];cid=f'b{bs}-{j}'
            stimuli.append(dict(id=cid,words=words,family=str(f)))
            keys.append(dict(id=cid,bin=int(bs),reverse=rev,rotation=off,n=n,family=str(f),source=f'{f}:{i}'))
    return stimuli,keys

def mean_ci(values,families,name):
    return RD.bootstrap([dict(family=f,x=float(x)) for x,f in zip(values,families)],'x',seed(name))

def predicate(metrics,truth='J',need_intervals=True):
    relevant=[m for m in metrics if m['parser']=='units' and m['pair']==truth]
    return bool(len(relevant)==4 and all(m['families']>=8 and m['distinct_windows']>=30 and
        (m['variant']!='matched' or m['matched_supported']) and
        all(v['margin']>=.10 and (not need_intervals or v['ci'][0]>0) for v in m['contrasts'].values()) for m in relevant))

def direction_control(folder,train,held,name,intervals=True):
    folder.mkdir(parents=True);models,meta,word=models_for(train)
    save(folder/'models.json',dict(meta=meta,counts={'|'.join(k):[[a,b,n] for (a,b),n in sorted(c.items())] for k,c in models.items()},word=[[a,b,n] for (a,b),n in sorted(word.items())]))
    stimuli,keys=cases_for(held,name);RD.jsonlines(folder/'stimuli.jsonl',stimuli)
    (folder/'sealed').mkdir();save(folder/'sealed/key.json',keys);event(folder,'KEY_SEALED',sha256=sha(folder/'sealed/key.json'))
    values=[];r=rng('shuffle/'+name)
    for s in stimuli:
        shuffled=s['words'][:];r.shuffle(shuffled);scores={}
        for (parser,variant,pair),m in models.items():scores['|'.join([parser,variant,pair])]=pair_score(s['words'],m,parser,variant,pair,meta)
        values.append(dict(id=s['id'],scores=scores,null_words=shuffled,
            null_J=pair_score(shuffled,models['units','raw','J'],'units','raw','J',meta),
            word_score=RD.direction(s['words'],word,'circular')[0]))
    RD.jsonlines(folder/'scores.jsonl',values);event(folder,'SCORES_SAVED',sha256=sha(folder/'scores.jsonl'))
    event(folder,'KEY_OPENED',sha256=sha(folder/'sealed/key.json'));keys=load(folder/'sealed/key.json')
    lookup={v['id']:v for v in values};trials=[]
    for k in keys:
        v=lookup[k['id']];target=-1 if k['reverse'] else 1
        trials.append(dict(**k,correct={m:int(RD.sign(x)==target) for m,x in v['scores'].items()},
            null_correct=int(RD.sign(v['null_J'])==target),null_tie=RD.sign(v['null_J'])==0,
            word_correct=int(RD.sign(v['word_score'])==target)))
    RD.jsonlines(folder/'trials.jsonl',trials);metrics=[]
    for b in [3,4]:
        sub=[t for t in trials if t['bin']==b];families=[t['family'] for t in sub]
        for parser in ['units','codepoints']:
            for variant in ['raw','matched']:
                for pair in PAIRS:
                    key='|'.join([parser,variant,pair]);correct=[t['correct'][key] for t in sub]
                    contrasts={}
                    for other in PAIRS:
                        if other==pair:continue
                        diff=[t['correct'][key]-t['correct']['|'.join([parser,variant,other])] for t in sub]
                        contrasts[other]=dict(margin=sum(diff)/len(diff),ci=mean_ci(diff,families,name+str(b)+key+other) if intervals else None)
                    metrics.append(dict(bin=b,parser=parser,variant=variant,pair=pair,accuracy=sum(correct)/len(correct),contrasts=contrasts,
                        families=len(set(families)),distinct_windows=len({(t['source'],t['n']) for t in sub}),
                        matched_supported=meta[parser]['k']>=1))
    null=[t for t in trials if not t['null_tie']];nc=mean_ci([t['null_correct'] for t in null],[t['family'] for t in null],name+'null') if null else [None,None]
    na=sum(t['null_correct'] for t in null)/len(null) if null else None
    npass=bool(len(null)>=100 and len({t['family'] for t in null})>=8 and .4<=na<=.6 and nc[0]>=.35 and nc[1]<=.65)
    word_bins=[]
    for b in [3,4]:
        sub=[t for t in trials if t['bin']==b];a=sum(t['word_correct'] for t in sub)/len(sub)
        c=mean_ci([t['word_correct'] for t in sub],[t['family'] for t in sub],name+str(b)+'word')
        word_bins.append(dict(bin=b,accuracy=a,ci=c,passed=a>=.8 and c[0]>=.65))
    save(folder/'metrics.json',dict(metrics=metrics,null=dict(passed=npass,accuracy=na,ci=nc,n=len(null)),word_bins=word_bins,
        intervals='computed' if intervals else 'not needed for a point-margin failure; score files retain all data'))
    # Null bank calls can be ruled out from point margins; compute intervals only if that hurdle passes.
    point=predicate(metrics,need_intervals=False)
    if not intervals and point:
        for m in metrics:
            if m['parser']!='units':continue
            sub=[t for t in trials if t['bin']==m['bin']];base='|'.join([m['parser'],m['variant'],m['pair']])
            for other,c in m['contrasts'].items():
                diff=[t['correct'][base]-t['correct']['|'.join([m['parser'],m['variant'],other])] for t in sub]
                c['ci']=mean_ci(diff,[t['family'] for t in sub],name+base+other+str(m['bin']))
        save(folder/'metrics.json',dict(metrics=metrics,null=dict(passed=npass,accuracy=na,ci=nc,n=len(null)),word_bins=word_bins,intervals='expanded after point hurdle'))
    call=point and predicate(metrics)
    return dict(specific=call,metrics=metrics,null_passed=npass,word_bins=word_bins)

def specificity_chain():
    root=OUT/'specificity';root.mkdir();calls=[]
    for i in range(100):
        c=load(OUT/f'bank/C-zero/{i:03d}.json')
        result=direction_control(root/f'null_{i:03d}',chunks(c['train']),c['held'],f'C-zero/{i}',False)
        calls.append(result['specific'])
    rate=sum(calls)/100;upper=RD.wilson(sum(calls),100)[1]
    save(root/'null_operating.json',dict(calls=calls,false_specificity_rate=rate,wilson_upper=upper))
    if rate>.1 or upper>.2:return finish(root,'FAIL_NULL',false_specificity_rate=rate,wilson_upper=upper)
    outcomes=[]
    sequence=[('C-junc','J'),('C-SS','SS'),('C-EE','EE'),('C-order',None)]
    for index,(name,expected) in enumerate(sequence):
        c=load(OUT/f'bank/{name}/000.json');folder=root/name
        r=direction_control(folder,chunks(c['train']),c['held'],name)
        good=predicate(r['metrics'],expected) if expected else (not r['specific'] and all(b['passed'] for b in r['word_bins']))
        passed=good and r['null_passed'];outcomes.append(dict(corpus=name,expected_pair=expected,passed=passed,shuffle_null=r['null_passed']))
        finish(folder,'PASS' if passed else ('FAIL_NULL' if not r['null_passed'] else 'FAIL_CONTROL'),expected_pair=expected)
        if not passed:
            for later,_ in sequence[index+1:]:
                p=root/later;p.mkdir();finish(p,'NOT_RUN_UPSTREAM_FAILURE',dependency=name)
            return finish(root,'FAIL_CONTROL',outcomes=outcomes,false_specificity_rate=rate)
    return finish(root,'PASS',outcomes=outcomes,false_specificity_rate=rate)

def xlogx(a):
    return np.where(a>0,a*np.log(np.maximum(a,1)),0.)

def info_test(blocks,direction,namespace,mask=None):
    families=[];null_total=np.zeros(B);obs_total=0.;informative=0;informative_families=0;all_pairs=0
    for f,words in enumerate(blocks):
        cells=defaultdict(list);n=0
        for i,(a,b) in enumerate(zip(words,words[1:])):
            ua,ub=units(a),units(b)
            if len(ua)<2 or len(ub)<2 or (mask is not None and i not in mask[f]):continue
            y,z,v=(ua[-1],ua[-2],ub[0]) if direction=='reg' else (ub[0],ub[1],ua[-1])
            cells[z].append((y,v));n+=1
        if not n:continue
        n_family=0;observed=0.;nulls=np.zeros(B)
        for z,pairs in sorted(cells.items()):
            yy,y=np.unique([p[0] for p in pairs],return_inverse=True);vv,v=np.unique([p[1] for p in pairs],return_inverse=True)
            ky,kv=len(yy),len(vv);size=len(pairs);joint=np.bincount(y*kv+v,minlength=ky*kv).reshape(ky,kv)
            cy=joint.sum(axis=1);cv=joint.sum(axis=0)
            const=size*math.log(size)-xlogx(cy).sum()-xlogx(cv).sum()
            def gain(counts):
                occupied=(counts>0).sum(axis=-2)
                correction=.5*(ky-1-((occupied-1)*(cv>0)).sum(axis=-1))
                return (const+xlogx(counts).sum(axis=(-2,-1))+correction)/(n*math.log(2))
            value=float(gain(joint));observed+=value
            if size<4 or ky<2 or kv<2:nulls+=value;continue
            n_family+=size;informative+=size
            nr=np.random.default_rng(seed(f'{namespace}/{direction}/{f}/{z}'))
            perm=nr.permuted(np.broadcast_to(v,(B,size)),axis=1)
            codes=np.arange(B)[:,None]*(ky*kv)+y[None,:]*kv+perm
            counts=np.bincount(codes.ravel(),minlength=B*ky*kv).reshape(B,ky,kv)
            nulls+=gain(counts)
        families.append(dict(family=str(f),gain=observed,pairs=n,informative=n_family))
        informative_families+=int(n_family>0);all_pairs+=n;obs_total+=observed;null_total+=nulls
    if not families:return dict(supported=False,families=[],p=None,statistic=None,null_statistics=[])
    obs_total/=len(families);null_total/=len(families)
    p=(1+int((null_total>=obs_total-1e-12).sum()))/(B+1)
    return dict(supported=informative>=200 and informative_families>=8,families=families,
        informative_pairs=informative,informative_families=informative_families,eligible_pairs=all_pairs,
        statistic=obs_total,p=p,null_statistics=null_total.tolist(),
        null_recipe=dict(seed_namespace=namespace,direction=direction,permutations=B,algorithm='NumPy Generator.permuted per(page,Z) cell; exact seed(namespace/direction/family/context)'))

def holm(ps):
    if any(p is None for p in ps):return [False,False]
    order=np.argsort(ps);reject=[False,False]
    for rank,j in enumerate(order):
        if ps[j]<=.01/(2-rank):reject[int(j)]=True
        else:break
    return reject

def paired_info(folder,blocks,namespace,mask=None):
    folder.mkdir(parents=True);answers={}
    if mask is not None:save(folder/'paired_eligible_indices.json',[sorted(x) for x in mask])
    for direction in ['reg','prog']:
        result=info_test(blocks,direction,namespace,mask);save(folder/(direction+'.json'),result);answers[direction]=result
    rejects=holm([answers[d]['p'] if answers[d]['supported'] else None for d in ['reg','prog']])
    save(folder/'decision.json',dict(rejects=rejects,supported=all(answers[d]['supported'] for d in answers)))
    return answers,rejects

def conditioning_chain(refs):
    root=OUT/'conditioning';root.mkdir();false=[]
    for i in range(100):
        c=load(OUT/f'bank/C-zero/{i:03d}.json')
        ans,rej=paired_info(root/f'null_{i:03d}',c['held'],f'I1-zero/{i}')
        if not all(a['supported'] for a in ans.values()):return finish(root,'UNSUPPORTED',reason='null support',member=i)
        false.append(any(rej))
    rate=sum(false)/100;upper=RD.wilson(sum(false),100)[1]
    save(root/'null_operating.json',dict(calls=false,false_rejection_rate=rate,wilson_upper=upper))
    if rate>.1 or upper>.2:return finish(root,'FAIL_NULL',false_rejection_rate=rate,wilson_upper=upper)
    qualified={};positives={}
    for direction,name in [('reg','C-junc'),('prog','C-prog')]:
        hits=[];gains=[]
        for i in range(20):
            c=load(OUT/f'bank/{name}/{i:03d}.json');ans,rej=paired_info(root/f'{direction}_{i:03d}',c['held'],f'I1-positive/{direction}/{i}')
            j=0 if direction=='reg' else 1
            hits.append(all(a['supported'] for a in ans.values()) and rej[j] and not rej[1-j]);gains.append(ans[direction]['statistic'])
        passed=sum(hits)>=18 and statistics.median(gains)>=.05
        qualified[direction]=passed;positives[direction]=dict(correct=sum(hits),n=20,median_gain=statistics.median(gains),passed=passed)
    save(root/'positive_gates.json',positives)
    transfer=None
    if qualified['reg']:
        base=refs['C-lat']['held'];mod=refs['C-sandhi']['held'];mask=[]
        for a,b in zip(base,mod):mask.append({i for i in range(len(a)-1) if min(len(units(a[i])),len(units(a[i+1])),len(units(b[i])),len(units(b[i+1])))>=2})
        original,_=paired_info(root/'Latin_original',base,'I1-Latin-original',mask)
        treatment,reject=paired_info(root/'Latin_rewrite',mod,'I1-Latin-rewrite',mask)
        before={r['family']:r['gain'] for r in original['reg']['families']}
        ds=[dict(family=r['family'],x=r['gain']-before[r['family']]) for r in treatment['reg']['families']]
        interval=RD.bootstrap(ds,'x',seed('I1-Latin-difference'))
        transfer=dict(passed=bool(treatment['reg']['supported'] and reject[0] and interval[0]>0),
            paired_gain=sum(d['x'] for d in ds)/len(ds),paired_ci=interval,treatment_p=treatment['reg']['p'],Holm_regressive_reject=reject[0])
        save(root/'Latin_added_rewrite_gate.json',transfer)
    else:
        p=root/'Latin_rewrite';p.mkdir();finish(p,'NOT_RUN_UPSTREAM_FAILURE',dependency='regressive positive calibration')
    return finish(root,'PASS' if all(qualified.values()) and transfer and transfer['passed'] else 'FAIL_CALIBRATION',
        false_rejection_rate=rate,positive_gates=positives,regressive_source_transfer=transfer,
        progressive_qualified=qualified['prog'],regressive_toy_qualified=qualified['reg'])

def pair_distributions(blocks):
    cross=[];within=[]
    for block in blocks:
        u=[units(w) for w in block]
        cross.append(Counter((a[-1],b[0]) for a,b in zip(u,u[1:])))
        within.append(Counter((a,b) for w in u for a,b in zip(w,w[1:])))
    support=sorted(set().union(*(set(c)|set(w) for c,w in zip(cross,within))))
    a=np.array([[c[x] for x in support] for c in cross],dtype=float);b=np.array([[c[x] for x in support] for c in within],dtype=float)
    return a,b,support

def jsd_counts(a,b):
    p=a/np.maximum(a.sum(axis=-1,keepdims=True),1);q=b/np.maximum(b.sum(axis=-1,keepdims=True),1);m=(p+q)/2
    lp=np.where(p>0,p*np.log2(np.maximum(p,1e-300)/np.maximum(m,1e-300)),0.)
    lq=np.where(q>0,q*np.log2(np.maximum(q,1e-300)/np.maximum(m,1e-300)),0.)
    return (lp+lq).sum(axis=-1)/2

def spacing_chain(refs):
    root=OUT/'spacing';root.mkdir();nf=len(refs['C-lat']['held']);ng=np.random.default_rng(seed('I2-bootstrap'))
    draws=ng.integers(0,nf,size=(2000,nf));weights=np.array([np.bincount(d,minlength=nf) for d in draws]);values={};metrics={}
    np.save(root/'bootstrap_family_draws.npy',draws)
    for name in ['C-lat','C-sandhi','C-respace','C-naibbe']:
        a,b,support=pair_distributions(refs[name]['held'])
        if nf<8 or a.sum()==0 or b.sum()==0:return finish(root,'UNSUPPORTED',corpus=name)
        js=float(jsd_counts(a.sum(axis=0),b.sum(axis=0)));boot=jsd_counts(weights@a,weights@b);values[name]=boot
        metrics[name]=dict(JSD=js,ci=np.quantile(boot,[.025,.975]).tolist(),families=nf,
            words=sum(map(len,refs[name]['held'])),cross_pairs=int(a.sum()),within_pairs=int(b.sum()),pair_support=len(support))
        save(root/(name+'_counts.json'),dict(pair_support=support,cross=a.astype(int).tolist(),within=b.astype(int).tolist()))
    contrasts=[]
    for a in ['C-lat','C-sandhi']:
        for b in ['C-respace','C-naibbe']:
            interval=np.quantile(values[a]-values[b],[.025,.975]).tolist()
            contrasts.append(dict(contrast=a+' minus '+b,ci=interval,passed=interval[0]>0))
    save(root/'metrics.json',dict(corpora=metrics,contrasts=contrasts))
    return finish(root,'PASS_REFERENCE_ORDERING' if all(x['passed'] for x in contrasts) else 'FAIL_REFERENCE_ORDERING',
        corpora=metrics,contrasts=contrasts,cross_language_plaintext_space_classification='NOT_QUALIFIED',target_readout='NOT_RUN')

def engineering():
    root=OUT/'engineering';root.mkdir();source=LAB/'src/parse_ivtff.py'
    spec=importlib.util.spec_from_file_location('jx_parser',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    def parse(raw,join):return m.clean(raw.replace('<->','.\ufffd.').replace('<~>','.\ufffd.').replace(',','' if join else ',')).split()
    checks=[parse('ab,cd.ef',False)==['ab','cd','ef'],parse('ab,cd.ef',True)==['abcd','ef'],
        '\ufffd' in parse('ab,?cd.ef',True)[0],parse('ab<->cd',True)==['ab','\ufffd','cd'],
        parse('[ab,cd:ef].gh',True)==['abcd','gh']]
    assert all(checks)
    return finish(root,'PASS_ENGINEERING_ONLY',fixture_checks=len(checks),K2_target_qualification='NOT_RUN',
        ancestry_ledger='binding/transcription_inventory.csv; unresolved readers not certified independent',K3_target='NOT_RUN')

def run():
    check();OUT.mkdir(parents=True);save(OUT/'RUN_START.json',dict(utc=now(),registration_sha256=sha(REG/'REGISTRATION.json')))
    results=[];prepare_bank();refs=prepare_references()
    for name,work in [('engineering',engineering),('specificity',specificity_chain),('conditioning',lambda:conditioning_chain(refs)),('spacing',lambda:spacing_chain(refs))]:
        try:results.append(work())
        except Exception as e:
            p=OUT/name;p.mkdir(exist_ok=True);(p/'EXECUTION_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
            results.append(finish(p,'FAIL_EXECUTION',error=str(e),retried=False))
    # References are empirical diagnostics, not synthetic gate rescues.
    for name in ['C-lat','C-sandhi','C-respace','C-naibbe']:
        folder=OUT/'reference_profiles'/name
        try:
            matched=token_matched(refs[name],refs['C-lat']);m=direction_control(folder,matched['train'],matched['held'],'empirical/'+name)
            results.append(finish(folder,'DESCRIPTIVE_ONLY',J_specificity_predicate=m['specific'],shuffle_equivalence=m['null_passed'],
                word_bins=m['word_bins'],not_a_known_zero_reference=True))
        except Exception as e:
            folder.mkdir(parents=True,exist_ok=True);(folder/'EXECUTION_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
            results.append(finish(folder,'FAIL_EXECUTION',error=str(e),retried=False))
    check();save(OUT/'SUMMARY.json',results)
    save(OUT/'STATUS.json',dict(status='PHASE0_COMPLETE_WITH_FAILURES' if any(r['status'].startswith(('FAIL','UNSUPPORTED')) for r in results) else 'PHASE0_COMPLETE',
        candidate_list='APPROVED_FROZEN_36_ALL_NP',registered='JX-20261106-P0-1',prior_runs_unchanged=True,
        manuscript_K_I_run=False,real_ring_scoring='CLOSED',radial='HELD',I1_full='NOT_RUN_MISSING_SOURCE',PDF_used=False))
    report=['# JX Phase0 — JX-20261106-P0-1','','| Chain | Outcome |','|---|---|']
    report += [f"| {r['chain']} | {r['status']} |" for r in results]
    report += ['', 'Approved36-row candidate list and NP predictions are frozen. Every result is a source/synthetic '
        'calibration or declared empirical reference diagnostic. No JX manuscript kill/interpretation test, '
        'real-ring score, language-ranking comparison or mapping search ran. Prior RD artifacts and excluded '
        'PDF are unchanged. Read individual reports/metrics for failed controls, nulls and support.','',
        'Generator code, literal rules, source spans, seeds, conditional permutation recipe and phase stops '
        'were bound before generation. A PASS in an unrelated chain never repairs a failure. Source-reference '
        'JSD ordering is not a plaintext-space or language classifier. I1 outputs are unit associations, not '
        'phonological or causal diagnoses.','']
    (OUT/'report.md').write_text('\n'.join(report),encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    p=OUT/'specificity/C-junc/metrics.json'
    if p.exists():
        ms=load(p)['metrics']
        for variant in ['raw','matched']:
            selected=[m for m in ms if m['parser']=='units' and m['variant']==variant and m['bin']==4]
            axes[0].plot([m['pair'] for m in selected],[m['accuracy'] for m in selected],'o-',label=variant)
        axes[0].legend();axes[0].set_ylim(0,1.03)
    else:axes[0].text(.1,.5,'Positive control not opened')
    axes[0].set_title('C-junc:21–40 known-order recovery');axes[0].set_ylabel('Accuracy; ties wrong')
    p=OUT/'spacing/metrics.json'
    if p.exists():
        m=load(p)['corpora'];names=list(m)
        axes[1].bar(range(len(names)),[m[n]['JSD'] for n in names])
        axes[1].set_xticks(range(len(names)),names,rotation=25)
    axes[1].set_title('Empirical full-stream reference JSD');axes[1].set_ylabel('Bits; not a plaintext-space classifier')
    fig.tight_layout();fig.savefig(OUT/'calibration_summary.png',dpi=150);plt.close(fig)
    save(OUT/'ARTIFACT_MANIFEST.json',dict(hashes={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print('JX Phase0 complete; manuscript and real-ring scoring closed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['approve','bind','register','run'])
    {'approve':approve,'bind':bind,'register':register,'run':run}[p.parse_args().action]()
