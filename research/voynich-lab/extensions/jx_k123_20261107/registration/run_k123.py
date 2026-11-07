"""Registered JX paragraph K1/K2 and annotated K3; never imports ring text."""
import sys
sys.dont_write_bytecode=True
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
LAB=HERE.parents[1]; WORK=LAB.parent
sys.path.insert(0,str(LAB/'extensions/jx_phase0_20261106'))
import jx_phase0 as j
sys.path.insert(0,str(LAB/'src'))
import parse_ivtff as iv
RD=j.RD
ID='JX-20261107-K123-1'; MASTER=2026110701
REG=HERE/'registration'; PREP=HERE/'intake'; OUT=LAB/'results/jx'/ID
P0=LAB/'results/jx/JX-20261106-P0-1'
SCOPES=['aggregate','variety_A','variety_B']+['scribe_'+str(i) for i in range(1,6)]
TYPES={'P0','P1','Pc','Pr','Pt'}
j.MASTER=MASTER

def save(p,v):j.save(p,v)
def load(p):return j.load(p)
def sha(p):return j.sha(p)
def now():return datetime.now(timezone.utc).isoformat()
def seed(s):return MASTER+int(hashlib.sha256(s.encode()).hexdigest()[:12],16)
def rng(s):return random.Random(seed(s))
def jsonlines(p,rs):RD.jsonlines(p,rs)
def in_scope(l,scope):
    return scope=='aggregate' or (scope.startswith('variety_') and l['variety']==scope[8:]) or (scope.startswith('scribe_') and l['scribe']==scope[7:])

def literal(raw):
    """Frozen first alternatives, then discard comments; never lose barriers."""
    s=re.sub(r'<[-~]>', '\ufffd',raw)
    s=re.sub(r'<[^>]*>', '',s)
    while '[' in s:
        s,n=re.subn(r'\[([^\[\]]*)\]',lambda m:re.split(r'[:|]',m[1])[0],s)
        if not n:raise ValueError('Unbalanced alternatives')
    s=re.sub(r'@\d{3};','\ufffd',s)
    s=s.replace('{','').replace('}','').replace('!','')
    s=re.sub(r'[?%]+','\ufffd',s)
    s=re.sub(r'[^a-zA-Z\ufffd.,\s]','\ufffd',s)
    return re.sub(r'\s+','',s)

def tokens(s,variant):
    """Canonical-literal offsets, retaining comma locations inside joined tokens."""
    out=[]; start=None
    for i,c in enumerate(s+'.'):
        sep=c=='.' or (c==',' and variant=='split') or c=='\ufffd'
        if sep:
            if start is not None:
                w=s[start:i].replace(',','')
                if w:out.append(dict(word=w,start=start,end=i))
            start=None
        elif c!=',' and start is None:start=i
    return out

def intake():
    PREP.mkdir()
    zl=iv.parse(LAB/'data/raw/ZL3b-n.txt','ZL')
    lsi=iv.parse(LAB/'data/raw/LSI_ivtff_0d.txt','LSI')
    # Inventory metadata only: no circular/radial strings enter a target panel.
    banned={RD.family(r['folio']) for r in j.rows(LAB/'results/ringdir/preflight/ring_inventory.csv')}
    zmeta={r['line_id']:r for r in zl if r['locus_code'][1:] in TYPES}
    allcodes=sorted({r['transcriber'] for r in lsi})
    ledger=[]; lines={}; offsets=[]
    for code,records in [('ZL',zl)]+[(c,[r for r in lsi if r['transcriber']==c]) for c in allcodes]:
        eligible=[]; current=None; idx=None; para=-1; previous_p=False
        for r in records:
            is_p=r['locus_code'][1:] in TYPES
            if r['folio']!=current:idx=None;current=r['folio'];para=-1;previous_p=False
            if code!='ZL':
                # Explicit IVTFF 1.5 locator start, not borrowed ZL lineation.
                if is_p and r['locus_code'][0] in '@*':idx=0;para+=1
                elif is_p and idx is not None and previous_p:idx+=1
                else:idx=None
                index=idx
            else:
                if is_p and r['is_para_start']:para+=1
                index=r['line_index_in_paragraph']
            previous_p=is_p
            if not is_p:continue
            fam=RD.family(r['folio']);s=literal(r['text_raw']); reasons=[]
            if fam in banned:reasons.append('ring_family_excluded')
            for k in ['is_spurious','has_missing_span','has_uncertainty','is_alternate_branch']:
                if r[k]:reasons.append(k)
            if '<->' in r['text_raw'] or '<~>' in r['text_raw']:reasons.append('drawing')
            if index is None:reasons.append('no_explicit_paragraph_context')
            if not s or '\ufffd' in s:reasons.append('unknown_or_empty')
            ts=tokens(s,'split')
            if not ts:reasons.append('empty_words')
            ledger.append(dict(reading=code,locus=r['line_id'],family=fam,eligible=not reasons,reasons=reasons,
                index=index,source_line=r['source_line'],n=len(ts)))
            if not reasons:
                zm=zmeta.get(r['line_id'],{})
                # Explicitly frozen exact-locus annotation alignment; no LSI Davis inference.
                eligible.append(dict(id=r['line_id'],folio=r['folio'],family=fam,index=index,
                    start=(r['is_para_start'] is True if code=='ZL' else r['locus_code'][0] in '@*'),
                    end=r['is_para_end'] is True,source_line=r['source_line'],literal=s,
                    split='train' if RD.stable('RD-v1-split|'+fam)/2**32<.60 else 'heldout',
                    scribe=zm.get('hand_scribe') or '',variety=zm.get('currier_lang') or '',
                    annotation_source='ZL exact line_id alignment',paragraph_group=para))
                if code=='ZL':offsets.append(dict(locus=r['line_id'],source_line=r['source_line'],literal=s,
                    split=tokens(s,'split'),join=tokens(s,'join')))
            if code!='ZL' and r['is_para_end']:idx=None
        lines[code]=eligible
    save(PREP/'lines.json',lines);jsonlines(PREP/'eligibility.jsonl',ledger);jsonlines(PREP/'comma_offsets.jsonl',offsets)
    inventory=[]
    for code in ['ZL']+allcodes:
        ancestry='primary' if code=='ZL' else ('independent_reading_documented' if code=='H' else ('derived' if code in 'DGIQM' else 'unresolved'))
        inventory.append(dict(code=code,ancestry=ancestry,eligible_lines=len(lines[code]),
            train_families=len({l['family'] for l in lines[code] if l['split']=='train'}),
            held_families=len({l['family'] for l in lines[code] if l['split']=='heldout'}),
            evidence='LSI lines 370-386; Zandbergen transcr.html TT/LSI/independent sections' if code=='H' else 'Phase0 inventory; composite or individual contribution not established independently at locus level'))
    save(PREP/'ancestry.json',dict(readings=inventory,independent_required=['H'],
        evidence_url='https://www.voynich.nu/transcr.html',checked_utc=now(),
        caveat='Independent reading, not independent manuscript/image sample. H retained in edited LSI; editorial line/paragraph layout is shared. C/F are edited composites; U/V contributions unresolved.'))
    # All eligible unresolved readers remain visible; no silent claim of independent replication.
    print(json.dumps(inventory,indent=2),flush=True)
    pools=build_pools(lines)
    save(PREP/'pools.json',pools)
    coverage=[]
    for scope in SCOPES:
        for panel,pool in pools.items():
            for b in [3,4]:
                sub=[c for c in pool if c['bin']==b and in_scope(c,scope)]
                coverage.append(dict(scope=scope,panel=panel,bin=b,windows=len(sub),families=len({c['family'] for c in sub}),
                    supported=len(sub)>=30 and len({c['family'] for c in sub})>=8))
    save(PREP/'coverage.json',coverage)
    save(PREP/'manifest.json',dict(id=ID,master_seed=MASTER,metadata_only=True,
        length_metadata=load(LAB/'extensions/jx_phase0_20261106/binding/EXECUTABLE_MANIFEST.json')['length_metadata'],
        scopes=SCOPES,case_count_per_bin=200,minimum_distinct_windows=30,minimum_families=8,
        target_readings_required=['ZL','H'],unresolved_readings='Inventory retained; not independent-required or interpreted as replications',
        phase0_specificity=load(P0/'specificity/STATUS.json')['status'],I2='CLOSED_FAILED_REFERENCE_ORDERING',
        I1='CLOSED_NOT_AUTHORIZED',real_rings='CLOSED',radial='HELD'))

def make_runs(lines,variant='split'):
    runs=[]; previous=None
    for l in lines:
        if (previous is None or l['folio']!=previous['folio'] or l['paragraph_group']!=previous['paragraph_group'] or l['index']!=previous['index']+1 or l['start'] or previous['end']):runs.append([])
        runs[-1].append(dict(l,words=[x['word'] for x in tokens(l['literal'],variant)]));previous=l
    return runs

def candidate(run,i,n,variant='split'):
    words=[];locs=[];ranges=[]
    for l in run[i:]:
        ts=tokens(l['literal'],variant);need=n-len(words);use=ts[:need]
        words.extend(x['word'] for x in use);locs.append(l['id'])
        ranges.append(dict(locus=l['id'],start=0,end=use[-1]['end'],full_line=len(use)==len(ts)))
        if len(words)>=n:break
    if len(words)<n:return None
    first=run[i]
    return dict(words=words,source=first['id'],family=first['family'],scribe=first['scribe'],variety=first['variety'],
        source_loci=locs,ranges=ranges,n=n)

def build_pools(lines):
    lengths=load(LAB/'extensions/jx_phase0_20261106/binding/EXECUTABLE_MANIFEST.json')['length_metadata']
    ns={int(b):sorted(set(v)) for b,v in lengths.items()}
    pools={k:[] for k in ['primary','spacing_own','spacing_matched','reading_native','reading_complete']}
    held=[l for l in lines['ZL'] if l['split']=='heldout']
    # Native RD line-start windows, with no scribe/section target matching: no real-ring metadata beyond frozen length list.
    for variant in ['split','join']:
        for run in make_runs(held,variant):
            for i in range(len(run)):
                for b,nn in ns.items():
                    for n in nn:
                        c=candidate(run,i,n,variant)
                        if c is None:continue
                        if variant=='split':pools['primary'].append(dict(c,bin=b,streams={'ZL':c['words']}))
                        pools['spacing_own'].append(dict(c,bin=b,variant=variant,streams={variant:c['words']}))
                        if variant!='split':continue
                        stream=[];safe=True
                        for l,span in zip(run[i:],c['ranges']):
                            join_ts=tokens(l['literal'],'join');end=span['end']
                            # Reject an endpoint cutting a comma-joined token; never manufacture a partial join.
                            if any(t['start']<end<t['end'] for t in join_ts):safe=False;break
                            stream.extend(t['word'] for t in join_ts if t['end']<=end)
                        lo,hi=RD.BINS[b]
                        if safe and lo<=len(stream)<=hi:
                            pools['spacing_matched'].append(dict(c,bin=b,streams={'split':c['words'],'join':stream},joined_n=len(stream)))
    # A common clean locus panel is fixed before fitting. RD-native n truncation is separately recorded for each reading.
    common={l['id'] for l in held}&{l['id'] for l in lines['H'] if l['split']=='heldout'}
    z=[l for l in held if l['id'] in common];h=[l for l in lines['H'] if l['id'] in common and l['split']=='heldout']
    hruns=make_runs(h);hstarts={l['id']:(r,i) for r in hruns for i,l in enumerate(r)}
    hmap={l['id']:l for l in h}
    for run in make_runs(z):
        for i,l in enumerate(run):
            for b,nn in ns.items():
                for n in nn:
                    a=candidate(run,i,n);hr,hi=hstarts[l['id']];v=candidate(hr,hi,n)
                    if a and v:
                        pools['reading_native'].append(dict(a,bin=b,streams={'ZL':a['words'],'H':v['words']},
                            H_source_loci=v['source_loci'],H_ranges=v['ranges'],alignment='same clean source-locus panel/start; n-word endpoint may differ'))
            # Additional exact complete-locus spans; both parses must stay in the same calibrated bin.
            zs=[];hs=[];locs=[];last_h=None
            for ll in run[i:]:
                hh=hmap[ll['id']]
                if last_h is not None and (hh['paragraph_group']!=last_h['paragraph_group'] or hh['index']!=last_h['index']+1 or hh['start'] or last_h['end']):break
                zs += [x['word'] for x in tokens(ll['literal'],'split')]
                hs += [x['word'] for x in tokens(hh['literal'],'split')];locs.append(ll['id']);last_h=hh
                if len(zs)>40 or len(hs)>40:break
                for b in [3,4]:
                    lo,hi=RD.BINS[b]
                    if lo<=len(zs)<=hi and lo<=len(hs)<=hi:
                        pools['reading_complete'].append(dict(source=l['id'],source_loci=locs[:],family=l['family'],scribe=l['scribe'],variety=l['variety'],
                            words=zs[:],n=len(zs),H_n=len(hs),bin=b,streams={'ZL':zs[:],'H':hs[:]},alignment='identical complete source-locus endpoints'))
    return pools

def register():
    assert not OUT.exists();REG.mkdir()
    assert load(P0/'specificity/STATUS.json')['status']=='PASS'
    assert load(HERE/'ENGINEERING.json')['status']=='PASS_ENGINEERING_ONLY'
    oldreg=load(LAB/'extensions/jx_phase0_20261106/registration/REGISTRATION.json')
    paths={WORK/p for p in oldreg['hashes']}
    for p,h in oldreg['hashes'].items():assert sha(WORK/p)==h,p
    for folder in [P0,PREP]:paths.update(p for p in folder.rglob('*') if p.is_file())
    paths.update([HERE/'run_k123.py',HERE/'EXECUTION.md',HERE/'test_k123.py',HERE/'verify_k123.py',HERE/'ENGINEERING.json'])
    paths.update([Path(sys.executable),Path(j.np.__file__)])
    save(REG/'REGISTRATION.json',dict(id=ID,registered_utc=now(),authority='User requested paragraph K1/K2 with K3 stratification; I/real rings closed',
        hashes={(p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else str(p)):sha(p) for p in sorted(paths)},python=sys.version,numpy=j.np.__version__,
        prior_exposure='Result-motivated follow-up to RD/JX Phase0; RD held-out families are historically exposed within the lab',
        master_seed=MASTER,PDF_used=False))
    for n in ['run_k123.py','EXECUTION.md','test_k123.py','verify_k123.py']:(REG/n).write_bytes((HERE/n).read_bytes())
    print('REGISTERED '+ID+'; no target features fitted/scored',flush=True)

def check():
    for p,h in load(REG/'REGISTRATION.json')['hashes'].items():assert sha(WORK/p)==h,p

def ci(vals,fams,name,adjusted=False):
    if not vals:return [None,None]
    groups=defaultdict(list)
    for v,f in zip(vals,fams):groups[f].append(float(v))
    data=list(groups.values());r=rng(name);a=[]
    for _ in range(2000):
        sel=[data[r.randrange(len(data))] for __ in data]
        a.append(sum(map(sum,sel))/sum(map(len,sel)))
    a.sort();q=.025/7 if adjusted else .025
    return [a[math.floor(2000*q)],a[math.ceil(2000*(1-q))-1]]

def select(pool,scope,name):
    out=[]; r=rng('select/'+scope+'/'+name)
    lengths=load(PREP/'manifest.json')['length_metadata']
    for b in [3,4]:
        sub=[c for c in pool if c['bin']==b and in_scope(c,scope)]
        ns=lengths[str(b)];order=[]
        while len(order)<200:
            cp=ns[:];r.shuffle(cp);order+=cp
        used=set()
        for k,n in enumerate(order[:200]):
            preferred=[c for c in sub if c['n']==n]
            options=preferred or sub
            if not options:continue
            fresh=[c for c in options if (c['source'],tuple(c['source_loci']),c['n']) not in used]
            c=r.choice(fresh or options);key=(c['source'],tuple(c['source_loci']),c['n']);used.add(key)
            out.append(dict(c,id=f'b{b}-{k:03d}',requested_n=n,length_fallback=not bool(preferred)))
    return out

def support(cases):
    details=[]
    for b in [3,4]:
        xs=[x for x in cases if x['bin']==b]
        n=len({(c['source'],tuple(c['source_loci']),c['n']) for c in xs});f=len({c['family'] for c in xs})
        details.append(dict(bin=b,cases=len(xs),distinct_windows=n,families=f,passed=n>=30 and f>=8))
    return details

def model_for(lines,reading,variant,scope):
    ls=[l for l in lines[reading] if l['split']=='train' and in_scope(l,scope)]
    blocks=[[w for l in r for w in l['words']] for r in make_runs(ls,variant)]
    if not blocks:return None
    models,meta,word=j.models_for(blocks)
    return models,meta,word,dict(reading=reading,variant=variant,training_lines=len(ls),training_families=len({l['family'] for l in ls}),training_words=sum(map(len,blocks)))

def evaluate(folder,cases,streams,lines,scope,name,k1=False):
    folder.mkdir(parents=True)
    sup=support(cases);save(folder/'support.json',sup)
    if not all(v['passed'] for v in sup):
        save(folder/'STATUS.json',dict(status='UNSUPPORTED',reason='Fewer than30 distinct windows or8 held-out families in a required bin',support=sup));return 'UNSUPPORTED'
    models={}
    for label,(reading,variant) in streams.items():
        m=model_for(lines,reading,variant,scope)
        if m is None or m[1]['units']['k']<1:
            save(folder/'STATUS.json',dict(status='UNSUPPORTED',reason='Training category support',stream=label));return 'UNSUPPORTED'
        models[label]=m
    save(folder/'models.json',{s:dict(meta=m[1],counts={'|'.join(k):[[a,b,n] for (a,b),n in sorted(c.items())] for k,c in m[0].items()},training=m[3]) for s,m in models.items()})
    stimuli=[];keys=[];r=rng('seal/'+scope+'/'+name)
    for c in cases:
        reverse=r.random()<.5;fraction=r.random();ss={};offsets={}
        for label in streams:
            ws=c['streams'][label][:]
            if reverse:ws.reverse()
            off=int(fraction*len(ws));ws=ws[off:]+ws[:off];ss[label]=ws;offsets[label]=off
        stimulus=dict(id=c['id'],family=c['family'],streams=ss)
        if k1:
            byid={l['id']:l for l in lines['ZL']};shuf=[]
            for span in c['ranges']:
                line=byid[span['locus']]
                ws=[t['word'] for t in tokens(line['literal'],'split') if t['end']<=span['end']]
                rng('C-shuf/'+scope+'/'+c['id']+'/'+span['locus']).shuffle(ws);shuf+=ws
            assert len(shuf)==len(c['words']) and Counter(shuf)==Counter(c['words'])
            if reverse:shuf.reverse()
            off=offsets['ZL'];stimulus['C_shuf_within_line']=shuf[off:]+shuf[:off]
        stimuli.append(stimulus)
        keys.append(dict(id=c['id'],family=c['family'],source=c['source'],source_loci=c['source_loci'],bin=c['bin'],n=c['n'],
            reverse=reverse,offsets=offsets,lengths={s:len(w) for s,w in ss.items()},requested_n=c['requested_n'],length_fallback=c['length_fallback']))
    jsonlines(folder/'stimuli.jsonl',stimuli);(folder/'sealed').mkdir();save(folder/'sealed/key.json',keys)
    j.event(folder,'KEY_SEALED',sha256=sha(folder/'sealed/key.json'))
    scores=[]
    for s in stimuli:
        row=dict(id=s['id'],streams={})
        for label,ws in s['streams'].items():
            ms,meta,word,_=models[label]
            shuffled=ws[:];rng('shuffle/'+scope+'/'+name+'/'+label+'/'+s['id']).shuffle(shuffled)
            # Within-line shuffle reference is separate below; this exchangeability gate matches Phase0 exactly.
            row['streams'][label]=dict(scores={'|'.join(k):j.pair_score(ws,m,*k,meta) for k,m in ms.items()},
                null_words=shuffled,null_J=j.pair_score(shuffled,ms['units','raw','J'],'units','raw','J',meta),
                coverage={'|'.join(k):sum(bool(m.get((j.parsed(a,k[0])[j.PAIRS[k[2]][0]],j.parsed(b,k[0])[j.PAIRS[k[2]][1]]),0)) for a,b in zip(ws,ws[1:]+ws[:1]))/len(ws) for k,m in ms.items() if k[1]=='raw'})
        if k1:
            ms,meta,_,_=models['ZL']
            row['C_shuf_within_line']={'|'.join(k):j.pair_score(s['C_shuf_within_line'],m,*k,meta) for k,m in ms.items()}
        scores.append(row)
    jsonlines(folder/'scores.jsonl',scores);j.event(folder,'SCORES_SAVED',sha256=sha(folder/'scores.jsonl'))
    j.event(folder,'KEY_OPENED',sha256=sha(folder/'sealed/key.json'))
    keys=load(folder/'sealed/key.json');trials=[]
    for key,s in zip(keys,scores):
        target=-1 if key['reverse'] else 1
        trials.append(dict(**key,streams={label:dict(correct={k:int(RD.sign(v)==target) for k,v in x['scores'].items()},
            ties={k:int(RD.sign(v)==0) for k,v in x['scores'].items()},null_correct=int(RD.sign(x['null_J'])==target),null_tie=RD.sign(x['null_J'])==0) for label,x in s['streams'].items()}))
    jsonlines(folder/'trials.jsonl',trials)
    if k1:
        save(folder/'C_shuf_descriptive.json',dict(role='Within-source-line word shuffle, no added gate and no claim of zero sequential statistics',
            bins=[dict(bin=b,accuracy={k:sum(RD.sign(s['C_shuf_within_line'][k])==(-1 if t['reverse'] else 1) for s,t in zip(scores,keys) if t['bin']==b)/sum(t['bin']==b for t in keys) for k in scores[0]['C_shuf_within_line']}) for b in [3,4]]))
    metrics=[];nulls={};adjusted=scope!='aggregate'
    for label in streams:
        nt=[t for t in trials if not t['streams'][label]['null_tie']]
        nc=ci([t['streams'][label]['null_correct'] for t in nt],[t['family'] for t in nt],name+scope+label+'null')
        na=sum(t['streams'][label]['null_correct'] for t in nt)/len(nt) if nt else None
        nulls[label]=dict(n=len(nt),families=len({t['family'] for t in nt}),accuracy=na,ci=nc,
            passed=bool(len(nt)>=100 and len({t['family'] for t in nt})>=8 and .4<=na<=.6 and nc[0]>=.35 and nc[1]<=.65))
        for b in [3,4]:
            sub=[t for t in trials if t['bin']==b];f=[t['family'] for t in sub]
            for parser in ['units','codepoints']:
                for variant in ['raw','matched']:
                    for pair in j.PAIRS:
                        k='|'.join([parser,variant,pair]);vals=[t['streams'][label]['correct'][k] for t in sub]
                        ac=sum(vals)/len(vals);bounds=ci(vals,f,name+scope+label+str(b)+k,adjusted)
                        contrasts={}
                        if k1 and pair=='J':
                            for other in ['SS','EE','SE']:
                                kk='|'.join([parser,variant,other]);ds=[t['streams'][label]['correct'][k]-t['streams'][label]['correct'][kk] for t in sub]
                                contrasts[other]=dict(margin=sum(ds)/len(ds),ci=ci(ds,f,name+scope+label+str(b)+k+other,adjusted))
                        metrics.append(dict(stream=label,bin=b,parser=parser,variant=variant,pair=pair,accuracy=ac,ci=bounds,
                            ties=sum(t['streams'][label]['ties'][k] for t in sub),contrasts=contrasts,
                            passed=ac>=.8 and bounds[0]>=.65))
    save(folder/'metrics.json',dict(metrics=metrics,nulls=nulls,scope=scope,adjusted_over_strata=7 if adjusted else 1,
        interval='2000 pooled family bootstrap; two-sided95% aggregate / Bonferroni7 strata',support=sup))
    if not all(x['passed'] for x in nulls.values()):status='FAIL_NULL'
    elif k1:
        primary=[m for m in metrics if m['parser']=='units' and m['pair']=='J']
        status='PASS' if all(all(c['margin']>=.1 and c['ci'][0]>0 for c in m['contrasts'].values()) for m in primary) else 'FAIL_SPECIFICITY'
    else:
        primary=[m for m in metrics if m['parser']=='units' and m['pair']=='J']
        status='PASS' if all(m['passed'] for m in primary) else 'FAIL_ROBUSTNESS'
    save(folder/'STATUS.json',dict(status=status,downstream='STOPPED' if status!='PASS' else 'K_ONLY; I remains unauthorized'))
    print(scope,name,status,flush=True)
    return status

def run():
    check();OUT.mkdir()
    j.event(OUT,'RUN_STARTED',registration_sha256=sha(REG/'REGISTRATION.json'))
    lines=load(PREP/'lines.json');pools=load(PREP/'pools.json');summary=[]
    for scope in SCOPES:
        root=OUT/scope;root.mkdir()
        # K1 and K2 are independent diagnostic chains. No I phase opens after either.
        cases=select(pools['primary'],scope,'K1')
        s=evaluate(root/'K1',cases,{'ZL':('ZL','split')},lines,scope,'K1',True)
        summary.append(dict(scope=scope,arm='K1',status=s))
        k2=[]
        panels=[('baseline','primary',{'ZL':('ZL','split')}),
                ('reading_native','reading_native',{'ZL':('ZL','split'),'H':('H','split')}),
                ('reading_complete','reading_complete',{'ZL':('ZL','split'),'H':('H','split')}),
                ('spacing_matched','spacing_matched',{'split':('ZL','split'),'join':('ZL','join')}),
                ('spacing_own_split','spacing_own',{'split':('ZL','split')}),
                ('spacing_own_join','spacing_own',{'join':('ZL','join')})]
        stopped=False
        for name,panel,streams in panels:
            folder=root/'K2'/name
            if stopped:
                folder.mkdir(parents=True);save(folder/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE',dependency=k2[-1]['panel']))
                k2.append(dict(panel=name,status='NOT_RUN_UPSTREAM_FAILURE'));continue
            pool=pools[panel]
            if name.startswith('spacing_own_'):pool=[c for c in pool if c['variant']==name.split('_')[-1]]
            cases=select(pool,scope,'K2/'+name)
            status=evaluate(folder,cases,streams,lines,scope,'K2/'+name)
            k2.append(dict(panel=name,status=status));stopped=status!='PASS'
        required=[x['status'] for x in k2 if x['status']!='NOT_RUN_UPSTREAM_FAILURE']
        status='PASS' if all(x=='PASS' for x in required) else next(x for x in required if x!='PASS')
        save(root/'K2/STATUS.json',dict(status=status,panels=k2));summary.append(dict(scope=scope,arm='K2',status=status,panels=k2))
    save(OUT/'summary.json',summary)
    save(OUT/'STATUS.json',dict(status='COMPLETE_WITH_STOPPED_CHAINS' if any(x['status']!='PASS' for x in summary) else 'K_COMPLETE',
        registered=ID,spacing_interpretation='CLOSED_FAILED_PHASE0',I1='CLOSED_NOT_AUTHORIZED',real_ring_scoring='CLOSED',radial='HELD',PDF_used=False))
    report(summary)
    check();j.event(OUT,'PRIOR_AND_BINDING_HASHES_VERIFIED')
    save(OUT/'ARTIFACT_MANIFEST.json',dict(id=ID,hashes={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))

def report(summary):
    text=['# JX paragraph K1/K2 with K3 stratification', '',f'Registration: {ID}.', '',
        'Paragraph targets only. Real-ring scoring CLOSED; radial HELD; spacing interpretation CLOSED after failed Phase0 reference ordering. I1 not authorized. No language ranking or PDF premises.', '',
        'RD held-out source families have prior laboratory exposure. This is a registered, result-motivated follow-up, not a historically unseen corpus.', '',
        '| Scope | Arm | Result |','|---|---|---|']
    for x in summary:text.append(f"| {x['scope']} | {x['arm']} | {x['status']} |")
    text += ['', '## Aggregate specificity measurements', '',
        '| Words | Categories | J accuracy | SS | EE | SE | J−SS (CI) | J−EE (CI) | J−SE (CI) |',
        '|---|---|---|---|---|---|---|---|---|']
    mp=OUT/'aggregate/K1/metrics.json'
    if mp.exists():
        metrics=load(mp)['metrics']
        for b in [3,4]:
            for variant in ['raw','matched']:
                ms={m['pair']:m for m in metrics if m['bin']==b and m['parser']=='units' and m['variant']==variant}
                c=ms['J']['contrasts']
                cs=[f"{c[p]['margin']:.3f} [{c[p]['ci'][0]:.3f}, {c[p]['ci'][1]:.3f}]" for p in ['SS','EE','SE']]
                text.append('| '+ ' | '.join([f'{RD.BINS[b][0]}–{RD.BINS[b][1]}',variant]+[f"{ms[p]['accuracy']:.3f}" for p in ['J','SS','EE','SE']]+cs)+' |')
        text += ['', 'The requirement is J-minus-each>=.10 with every lower bound>0, across all four rows. Raw-codepoint sensitivities, ties, shuffle results and category diagnostics are in the per-panel metrics/models.']
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
        for ax,b in zip(axes,[3,4]):
            for offset,variant in [(-.13,'raw'),(.13,'matched')]:
                ms={m['pair']:m for m in metrics if m['bin']==b and m['parser']=='units' and m['variant']==variant}
                vals=[ms[p]['accuracy'] for p in ['J','SS','EE','SE']]
                ax.bar([i+offset for i in range(4)],vals,width=.25,label=variant)
            ax.set_xticks(range(4),['J','SS','EE','SE']);ax.set_title(f'{RD.BINS[b][0]}–{RD.BINS[b][1]} words');ax.set_ylim(0,1)
            ax.axhline(.5,color='gray',linestyle=':',linewidth=.8);ax.legend()
        axes[0].set_ylabel('Direction accuracy (ties wrong)');fig.suptitle('JX K1 paragraph targets — aggregate, clustered units')
        fig.tight_layout();fig.savefig(OUT/'K1_aggregate.png',dpi=160);plt.close(fig)
    text += ['', '## K2 stopping panels', '']
    for x in summary:
        if x['arm']!='K2':continue
        evaluated=[p for p in x['panels'] if p['status']!='NOT_RUN_UPSTREAM_FAILURE']
        text.append(f"- {x['scope']}: "+'; '.join(f"{p['panel']} {p['status']}" for p in evaluated)+'.')
    text += ['', 'K1 is the full12-contrast conjunction across two bins and raw/matched units. K2 stops at its first failed/unsupported required panel; later panels are not scored. Each predeclared annotated stratum is a separate chain and cannot rescue the aggregate.', '',
        'LSI H is a separately produced Takahashi reading retained in an edited archive; paragraph layout is editorial. All other local reading IDs and unresolved/composite ancestry remain in the intake ledger. K3 LSI labels, where evaluated, are an explicitly frozen ZL exact-locus annotation alignment, not independent Davis identifications.', '',
        'A FAIL means this registered specificity/robustness requirement was not met; it does not establish absence of direction, a spacing mechanism, a transcription artifact, phonology, or language identity. UNSUPPORTED means inadequate source support.', '',
        'All scored stimuli, models, sealed keys, trial scores, null assignments and metrics are retained. Prior runs are hash-bound and checked unchanged.']
    (OUT/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['intake','register','run']);a=p.parse_args()
    try:{'intake':intake,'register':register,'run':run}[a.stage]()
    except Exception as exc:
        if a.stage=='run' and OUT.exists():
            save(OUT/'TECHNICAL_FAILURE.json',dict(status='STOP_TECHNICAL_FAILURE',error=repr(exc),utc=now(),no_rerun=True))
        raise
