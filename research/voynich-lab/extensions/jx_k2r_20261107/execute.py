"""K2R post-review source qualification, direction gates and descriptive edges."""
import sys
sys.dont_write_bytecode=True
import csv,hashlib,importlib.util,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
import stage1 as s
HERE=s.HERE;LAB=s.LAB;WORK=s.WORK;ROOT=s.OUT
OUT=ROOT/'execution_01';BIND=HERE/'registration/execution_01'
sys.path.insert(0,str(LAB/'.runtime'));sys.path.insert(0,str(LAB/'extensions/jx_phase0_20261106'));sys.path.insert(0,str(LAB/'src'))
import jx_phase0 as j
import parse_ivtff as iv
sp=importlib.util.spec_from_file_location('k2r_canonical',LAB/'extensions/jx_lsi_boundary_20261107/adapter.py');canon=importlib.util.module_from_spec(sp);sp.loader.exec_module(canon)
SCOPES=['aggregate','variety_A','variety_B']+['scribe_'+str(i) for i in range(1,6)]
load=s.load;save=s.save;sha=s.sha;table=s.table
def rng(n):return random.Random(s.SEED+int(hashlib.sha256(n.encode()).hexdigest()[:12],16))
def rows(p):return s.readtable(p)
def jsonlines(p,xs):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with Path(p).open('x',encoding='utf-8') as f:
        for x in xs:f.write(json.dumps(x,ensure_ascii=False)+'\n')
def event(folder,name,**kw):
    with (folder/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(event=name,utc=s.now(),**kw))+'\n')
def wordlist(lit,parse):return [x for x in re.split(r'[.,]+' if parse=='split' else r'\.+',lit if parse=='split' else lit.replace(',','')) if x]
def inside(r,scope):return scope=='aggregate' or scope=='variety_'+str(r.get('variety')) or scope=='scribe_'+str(r.get('scribe'))
def sign(x):return 0 if abs(x)<=1e-12 else (1 if x>0 else -1)
def edit(a,b,matrices=False):
    n,m=len(a),len(b);f=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1):f[i][0]=i
    for q in range(m+1):f[0][q]=q
    for i in range(1,n+1):
        for q in range(1,m+1):f[i][q]=min(f[i-1][q-1]+(a[i-1]!=b[q-1]),f[i-1][q]+1,f[i][q-1]+1)
    if not matrices:return f[n][m]
    z=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n,-1,-1):z[i][m]=n-i
    for q in range(m,-1,-1):z[n][q]=m-q
    for i in range(n-1,-1,-1):
        for q in range(m-1,-1,-1):z[i][q]=min(z[i+1][q+1]+(a[i]!=b[q]),z[i+1][q]+1,z[i][q+1]+1)
    return f,z

def align_classes(wa,wb):
    ua=[j.units(w) for w in wa];ub=[j.units(w) for w in wb];a=[x for w in ua for x in w];b=[x for w in ub for x in w]
    ca=[];cb=[];v=0
    for w in ua[:-1]:v+=len(w);ca.append(v)
    v=0
    for w in ub[:-1]:v+=len(w);cb.append(v)
    f,z=edit(a,b,True);d=f[-1][-1]
    am={i:[q for q in range(len(b)+1) if f[i][q]+z[i][q]==d] for i in ca}
    bm={q:[i for i in range(len(a)+1) if f[i][q]+z[i][q]==d] for q in cb}
    ac=[];bc=[]
    for i in ca:
        pos=am[i]
        ac.append('UNRESOLVED_ALIGNMENT' if len(pos)!=1 else ('AGREED' if pos[0] in cb and bm[pos[0]]==[i] else ('ZL_ONLY' if pos[0] not in cb else 'UNRESOLVED_ALIGNMENT')))
    for q in cb:
        pos=bm[q]
        bc.append('UNRESOLVED_ALIGNMENT' if len(pos)!=1 else ('AGREED' if pos[0] in ca and am[pos[0]]==[q] else ('H_ONLY' if pos[0] not in ca else 'UNRESOLVED_ALIGNMENT')))
    path=[];i=len(a);q=len(b)
    while i or q:
        if i and q and f[i][q]==f[i-1][q-1]+(a[i-1]!=b[q-1]):path.append([i-1,q-1]);i-=1;q-=1
        elif i and f[i][q]==f[i-1][q]+1:path.append([i-1,None]);i-=1
        else:path.append([None,q-1]);q-=1
    return dict(ZL=ac,H=bc,distance=d,traceback=list(reversed(path)),ambiguous_ZL=sum(len(v)!=1 for v in am.values()),ambiguous_H=sum(len(v)!=1 for v in bm.values()))

def boot(values,families,name,adjust=False,denominators=None):
    if not values:return [None,None]
    g={}
    for i,(v,f) in enumerate(zip(values,families)):
        if f not in g:g[f]=[0.,0.]
        g[f][0]+=float(v);g[f][1]+=float(denominators[i] if denominators is not None else 1)
    a=j.np.array(list(g.values()));r=rng('bootstrap/'+name)
    ix=j.np.array([[r.randrange(len(a)) for _ in a] for __ in range(2000)])
    num=a[ix,0].sum(axis=1);den=a[ix,1].sum(axis=1);valid=den>0
    if valid.sum()<1900:return [None,None]
    bs=sorted((num[valid]/den[valid]).tolist());lo=.025/7 if adjust else .025
    return [bs[math.floor(len(bs)*lo)],bs[math.ceil(len(bs)*(1-lo))-1]]

def fit(blocks):
    if not blocks:return None
    k,maps,diag=j.maps_for(blocks,'units');meta={'units':dict(k=k,maps=[sorted(x) for x in maps],diagnostics=diag)}
    counts={v:Counter() for v in ['raw','matched']}
    for block in blocks:
        for a,b in zip(block,block[1:]):
            x,y=j.units(a)[-1],j.units(b)[0];counts['raw'][x,y]+=1
            counts['matched'][x if x in maps[1] else '*',y if y in maps[0] else '*']+=1
    return dict(meta=meta,counts=counts,words=sum(map(len,blocks)),blocks=len(blocks))
def score(words,model,var):return j.pair_score(words,model['counts'][var],'units',var,'J',model['meta'])
def edge(a,b,model,var):
    x,y=j.units(a)[-1],j.units(b)[0];rx,ry=j.units(b)[-1],j.units(a)[0]
    if var=='matched':
        ma=model['meta']['units']['maps'];x=x if x in ma[1] else '*';rx=rx if rx in ma[1] else '*';y=y if y in ma[0] else '*';ry=ry if ry in ma[0] else '*'
    c=model['counts'][var];return math.log((c[x,y]+.5)/(c[rx,ry]+.5))

def fixtures():
    train=[['ab','cd','ef','gh','ij','kl','mn','op','qr','st','uv','wx']]*5;m=fit(train);ws=['ab','gh','cd','op']
    tests=[]
    for var in ['raw','matched']:
        tests.append(dict(name='antisymmetry_'+var,passed=math.isclose(score(ws,m,var),-score(list(reversed(ws)),m,var),abs_tol=1e-12)))
        tests.append(dict(name='edge_sum_'+var,passed=math.isclose(sum(edge(a,b,m,var) for a,b in zip(ws,ws[1:]+ws[:1]))/len(ws),score(ws,m,var),abs_tol=1e-12)))
    a=align_classes(['ab','cd'],['ab','cd']);tests.append(dict(name='identical_alignment',passed=a['ZL']==a['H']==['AGREED']))
    a=align_classes(['ab','cd'],['abcd']);tests.append(dict(name='planted_join',passed=a['ZL']==['ZL_ONLY'] and not a['H']))
    a=align_classes(['ab','cd'],['abx','cd']);tests.append(dict(name='gap_position_not_forced',passed=a['ZL']==['UNRESOLVED_ALIGNMENT']))
    tests.append(dict(name='distance_known_answer',passed=edit(['a','b'],['a','c'])==1))
    return tests

def bind():
    s.check();assert not OUT.exists();BIND.mkdir()
    approval=load(HERE/'registration/review_freeze/APPROVAL.json');assert approval['status']=='APPROVED_AND_FROZEN'
    for n,h in approval['hashes'].items():assert sha(ROOT/n)==h and sha(HERE/'registration/review_freeze'/n)==h
    assert load(LAB/'results/jx/JX-20261106-P0-1/specificity/STATUS.json')['status']=='PASS'
    paths={WORK/n for n in load(s.REG/'REGISTRATION.json')['hashes']}
    paths.update(p for p in ROOT.rglob('*') if p.is_file());paths.update(p for p in (HERE/'registration/review_freeze').rglob('*') if p.is_file())
    paths.update([HERE/'execute.py',HERE/'TARGET_BINDING.md',HERE/'verify_execution.py',s.REG/'REGISTRATION.json'])
    save(BIND/'EXECUTABLE_MANIFEST.json',dict(id=s.ID,utc=s.now(),approval_sha256=sha(HERE/'registration/review_freeze/APPROVAL.json'),
        hashes={(p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else str(p)):sha(p) for p in sorted(paths)},
        thresholds=dict(accuracy=.80,lower_bound=.65,distinct_windows=30,families=8),source_qc_min_agreement=.20,
        I_phase='CLOSED',spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',secondary_independent_readers=[]))
    for n in ['execute.py','TARGET_BINDING.md','verify_execution.py']:
        with (BIND/n).open('xb') as f:f.write((HERE/n).read_bytes())
    print('BOUND reviewed-crosswalk execution before glyph comparison',flush=True)

def check():
    for n,h in load(BIND/'EXECUTABLE_MANIFEST.json')['hashes'].items():assert sha(WORK/n)==h,n

def intake():
    zrows=iv.parse(s.ZL,'ZL');zmap={r['line_id']:r for r in zrows};hmap={};allh=[]
    metadata,_,unparsed=s.original_metadata(s.SOURCE);assert not unparsed
    order={r['source_id']:r['source_order'] for r in metadata};within=defaultdict(dict)
    for r in metadata:within[r['folio'],r['unit']][r['source_id']]=len(within[r['folio'],r['unit']])
    for n,line in enumerate(s.SOURCE.read_text(encoding='latin-1').splitlines(),1):
        if not line.startswith('<') or ';H>' not in line.split('>',1)[0]+'>':continue
        header,raw=line.split('>',1);d=s.original_header(header+'>')
        rr=dict(d,raw=raw.strip(),source_line=n,order=order[d['source_id']],unit_index=within[d['folio'],d['unit']][d['source_id']])
        assert d['source_id'] not in hmap;hmap[d['source_id']]=rr;allh.append(rr)
    banned={s.family(r['folio']) for r in rows(LAB/'results/ringdir/preflight/ring_inventory.csv')}
    def zlrec(r):
        c=canon.canonical(r['text_raw']);held=c['held'] or r['has_uncertainty'] or r['has_missing_span'] or r['is_spurious'] or r['line_index_in_paragraph'] is None
        return dict(id=r['line_id'],folio=r['folio'],family=s.family(r['folio']),split=s.split(r['folio']),variety=r['currier_lang'] or '',scribe=r['hand_scribe'] or '',literal=c['literal'],held=bool(held),end=r['is_para_end'],start=bool(r['is_para_start']),index=r['line_index_in_paragraph'],unit='ZL',source_line=r['source_line'])
    zz={r['line_id']:zlrec(r) for r in zrows if r['locus_code'][1:] in {'P0','P1','Pc','Pr','Pt'} and s.family(r['folio']) not in banned}
    hh={r['source_id']:dict(id=r['source_id'],folio=r['folio'],family=s.family(r['folio']),split=s.split(r['folio']),variety='',scribe='',literal=canon.canonical(r['raw'],True)['literal'],held=canon.canonical(r['raw'],True)['held'],end=canon.canonical(r['raw'],True)['paragraph_end'],start=False,index=r['unit_index'],unit=r['unit'],source_line=r['source_line']) for r in allh if r['kind'] in {'body','title'} and s.family(r['folio']) not in banned}
    pairrows=rows(HERE/'registration/review_freeze/crosswalk_candidates.csv');byz={r['ZL_id']:r for r in pairrows};ledger=[];valid={}
    for p in pairrows:
        a=zz.get(p['ZL_id']);b=hh.get(p['original_id']);reason=[];agreement=None
        if a is None or b is None:reason.append('MISSING_ELIGIBLE_SOURCE')
        elif a['held'] or b['held']:reason.append('UNCERTAIN_DAMAGE_DRAWING_OR_UNKNOWN_CONTEXT')
        else:
            ua=j.units(a['literal'].replace('.','').replace(',',''));ub=j.units(b['literal'].replace('.','').replace(',',''))
            agreement=1-edit(ua,ub)/max(len(ua),len(ub)) if max(len(ua),len(ub)) else None
            if agreement is None or agreement<.20:reason.append('PROBABLE_MISALIGNMENT_HELD_NO_REPAIR')
        row=dict(p,eligible=not reason,reasons=reason,glyph_unit_agreement=agreement)
        ledger.append(row)
        if not reason:
            b=dict(b,variety=a['variety'],scribe=a['scribe']);valid[p['ZL_id']]=dict(pair=p,ZL=a,H=b)
            hh[p['original_id']]=b
    # Walk the entire ordinary ZL sequence. Any unmapped/held row breaks a common block.
    blocks=[];last=None
    for r in zrows:
        if r['locus_code'][1:] not in {'P0','P1','Pc','Pr','Pt'}:last=None;continue
        c=valid.get(r['line_id'])
        if c is None:last=None;continue
        a,b=c['ZL'],c['H']
        br=last is None or a['folio']!=last['ZL']['folio'] or a['start'] or last['ZL']['end'] or last['H']['end'] or b['unit']!=last['H']['unit'] or b['index']!=last['H']['index']+1 or c['pair']['kind']!=last['pair']['kind']
        if br:blocks.append([])
        blocks[-1].append(c);last=c
    def native(rs):
        result=[];last=None
        for r in rs:
            if r['held']:last=None;continue
            br=last is None or r['folio']!=last['folio'] or r['unit']!=last['unit'] or r['start'] or last['end'] or r['index'] is None or last['index'] is None or r['index']!=last['index']+1
            if br:result.append([])
            result[-1].append(r);last=r
        return result
    natives={'ZL':native(list(zz.values())),'H':native(list(hh.values()))}
    return ledger,blocks,natives,zz,hh

def cases_from(blocks,common=True):
    out=[]
    for block in blocks:
        if (block[0]['ZL'] if common else block[0])['split']!='heldout':continue
        for i in range(len(block)):
            for end in range(i+1,len(block)+1):
                lines=block[i:end];streams={};ns={}
                for parse in ['split','join']:
                    streams[parse]={reader:[w for l in lines for w in wordlist((l[reader] if common else l)['literal'],parse)] for reader in (['ZL','H'] if common else ['ZL'])}
                    ns[parse]={r:len(w) for r,w in streams[parse].items()}
                if min(ns['join'].values())>40:break
                bins={3 if 11<=n<=20 else 4 if 21<=n<=40 else -1 for d in ns.values() for n in d.values()}
                if len(bins)!=1 or -1 in bins:continue
                a=lines[0]['ZL'] if common else lines[0]
                out.append(dict(id='w'+str(len(out)),bin=bins.pop(),family=a['family'],variety=a['variety'],scribe=a['scribe'],source_loci=[(l['ZL'] if common else l)['id'] for l in lines],
                    pair_ids=[l['pair']['pair_id'] for l in lines] if common else [],streams=streams,lengths=ns))
    return out

def support(cases):
    return [dict(bin=b,windows=len(xs),distinct_windows=len({tuple(x['source_loci']) for x in xs}),families=len({x['family'] for x in xs}),passed=len({tuple(x['source_loci']) for x in xs})>=30 and len({x['family'] for x in xs})>=8) for b in [3,4] for xs in [[c for c in cases if c['bin']==b]]]
def training(blocks,natives,reader,regime,scope,parse):
    source=([[c[reader] for c in b] for b in blocks] if regime=='common' else natives[reader]);out=[];families=set();loci=[]
    for block in source:
        group=[]
        for l in block:
            if l['split']!='train' or not inside(l,scope):
                if group:out.append(group);group=[]
                continue
            group+=wordlist(l['literal'],parse);families.add(l['family']);loci.append(l['id'])
        if group:out.append(group)
    return out,dict(training_families=len(families),training_loci=loci,training_words=sum(map(len,out)))

def direction_chain(folder,cases,blocks,natives,scope,parse,regime,readers=('ZL','H')):
    folder.mkdir(parents=True);sup=support(cases);save(folder/'support.json',sup)
    if not all(x['passed'] for x in sup):save(folder/'STATUS.json',dict(status='UNSUPPORTED_SOURCE_SUPPORT'));return 'UNSUPPORTED_SOURCE_SUPPORT'
    models={};training_info={}
    for reader in readers:
        train,info=training(blocks,natives,reader,regime,scope,parse);m=fit(train)
        if m is None or m['meta']['units']['k']<11:
            save(folder/'STATUS.json',dict(status='UNSUPPORTED_MATCHED_12_CLASSES',reader=reader,realized_k=m['meta']['units']['k'] if m else None));return 'UNSUPPORTED_MATCHED_12_CLASSES'
        models[reader]=m;training_info[reader]=info
    save(folder/'models.json',{r:dict(meta=m['meta'],counts={v:[[a,b,n] for (a,b),n in sorted(c.items())] for v,c in m['counts'].items()},training=training_info[r]) for r,m in models.items()})
    stimuli=[];keys=[];rr=rng(str(folder.relative_to(OUT))+'/seal')
    for c in cases:
        rev=rr.random()<.5;frac=rr.random();streams={};offsets={}
        for reader in readers:
            w=c['streams'][parse][reader][:]
            if rev:w.reverse()
            off=int(frac*len(w));streams[reader]=w[off:]+w[:off];offsets[reader]=off
        stimuli.append(dict(id=c['id'],streams=streams));keys.append(dict(id=c['id'],family=c['family'],bin=c['bin'],reverse=rev,offsets=offsets,source_loci=c['source_loci'],variety=c['variety'],scribe=c['scribe']))
    jsonlines(folder/'stimuli.jsonl',stimuli);save(folder/'sealed_keys.json',keys);event(folder,'KEY_SEALED',sha256=sha(folder/'sealed_keys.json'))
    scores=[]
    for st in stimuli:
        row=dict(id=st['id'],streams={})
        for reader,w in st['streams'].items():
            shuffled=w[:];rng(str(folder.relative_to(OUT))+reader+st['id']+'/shuffle').shuffle(shuffled)
            row['streams'][reader]=dict(scores={v:score(w,models[reader],v) for v in ['raw','matched']},null_words=shuffled,null_score=score(shuffled,models[reader],'raw'))
        scores.append(row)
    jsonlines(folder/'scores.jsonl',scores);event(folder,'SCORES_SAVED',sha256=sha(folder/'scores.jsonl'));event(folder,'KEY_OPENED',sha256=sha(folder/'sealed_keys.json'))
    keys=load(folder/'sealed_keys.json');trials=[]
    for k,sc in zip(keys,scores):
        target=-1 if k['reverse'] else 1
        trials.append(dict(**k,streams={r:dict(correct={v:int(sign(x)==target) for v,x in ss['scores'].items()},ties={v:int(sign(x)==0) for v,x in ss['scores'].items()},null_correct=int(sign(ss['null_score'])==target),null_tie=sign(ss['null_score'])==0) for r,ss in sc['streams'].items()}))
    jsonlines(folder/'trials.jsonl',trials);metrics=[];nulls={};ns=str(folder.relative_to(OUT))
    for reader in readers:
        nt=[t for t in trials if not t['streams'][reader]['null_tie']];vals=[t['streams'][reader]['null_correct'] for t in nt];fams=[t['family'] for t in nt];ci=boot(vals,fams,ns+reader+'null');acc=sum(vals)/len(vals) if vals else None
        nulls[reader]=dict(n=len(nt),families=len(set(fams)),accuracy=acc,ci=ci,passed=bool(len(nt)>=100 and len(set(fams))>=8 and ci[0] is not None and .4<=acc<=.6 and ci[0]>=.35 and ci[1]<=.65))
        for b in [3,4]:
            xs=[t for t in trials if t['bin']==b]
            for v in ['raw','matched']:
                vals=[t['streams'][reader]['correct'][v] for t in xs];ci=boot(vals,[t['family'] for t in xs],ns+reader+str(b)+v,scope!='aggregate');a=sum(vals)/len(vals)
                metrics.append(dict(reader=reader,bin=b,variant=v,accuracy=a,ci=ci,n=len(xs),families=len({t['family'] for t in xs}),ties=sum(t['streams'][reader]['ties'][v] for t in xs),passed=a>=.8 and ci[0] is not None and ci[0]>=.65))
    paired=[]
    if 'H' in readers:
        for b in [3,4]:
            xs=[t for t in trials if t['bin']==b]
            for v in ['raw','matched']:
                ds=[t['streams']['ZL']['correct'][v]-t['streams']['H']['correct'][v] for t in xs];ci=boot(ds,[t['family'] for t in xs],ns+'paired'+str(b)+v)
                paired.append(dict(bin=b,variant=v,ZL_minus_H=sum(ds)/len(ds),ci=ci,comparable_label=bool(ci[0] is not None and ci[0]>=-.05 and ci[1]<=.05),outcomes=dict(Counter(str((t['streams']['ZL']['correct'][v],t['streams']['H']['correct'][v])) for t in xs))))
    status='FAIL_NULL' if not all(x['passed'] for x in nulls.values()) else ('K2R_PASS_CELL' if all(m['passed'] for m in metrics if m['reader']==('H' if 'H' in readers else 'ZL')) else 'FAIL_ROBUSTNESS')
    composition=[]
    for b in [3,4]:
        xs=[t for t in trials if t['bin']==b]
        composition.append(dict(bin=b,n=len(xs),variety=dict(Counter(t['variety'] for t in xs)),scribe=dict(Counter(t['scribe'] for t in xs)),
            descriptive_ZL_within_variety=[dict(variety=label,variant=v,n=len(sub),accuracy=sum(t['streams']['ZL']['correct'][v] for t in sub)/len(sub)) for label in ['A','B'] for sub in [[t for t in xs if t['variety']==label]] if sub for v in ['raw','matched']]))
    save(folder/'metrics.json',dict(metrics=metrics,paired=paired,nulls=nulls,parse=parse,regime=regime,scope=scope,composition=composition));save(folder/'STATUS.json',dict(status=status))
    print(ns,status,flush=True);return status

def boundary_chain(folder,cases,blocks,natives,valid):
    folder.mkdir();results=[];allrows=[];alignment_cache={}
    for parse in ['split','join']:
        p=folder/parse;p.mkdir();models={}
        for reader in ['ZL','H']:
            train,info=training(blocks,natives,reader,'common','aggregate',parse);m=fit(train)
            if m is None or m['meta']['units']['k']<11:save(p/'STATUS.json',dict(status='UNSUPPORTED_TRAINING'));break
            models[reader]=m
        if len(models)!=2:results.append(dict(parse=parse,status='UNSUPPORTED_TRAINING'));continue
        save(p/'models.json',{r:dict(meta=m['meta'],counts={v:[[a,b,n] for (a,b),n in sorted(c.items())] for v,c in m['counts'].items()}) for r,m in models.items()})
        caseclasses={}
        for c in cases:
            classes={'ZL':[],'H':[]}
            for k,lid in enumerate(c['source_loci']):
                if (parse,lid) not in alignment_cache:
                    pair=valid[lid];wa=wordlist(pair['ZL']['literal'],parse);wb=wordlist(pair['H']['literal'],parse)
                    alignment_cache[parse,lid]=align_classes(wa,wb)
                al=alignment_cache[parse,lid]
                for reader in ['ZL','H']:
                    classes[reader]+=al[reader]
                    if k<len(c['source_loci'])-1:classes[reader].append('LINE_BOUNDARY')
            for reader in ['ZL','H']:classes[reader].append('SYNTHETIC_CLOSE');assert len(classes[reader])==len(c['streams'][parse][reader])
            caseclasses[c['id']]=classes
        stimuli=[];keys=[];rr=rng('boundary/'+parse+'/seal')
        for c in cases:
            rev=rr.random()<.5;frac=rr.random();streams={}
            for reader in ['ZL','H']:
                w=c['streams'][parse][reader];indices=list(range(len(w)))
                if rev:indices.reverse()
                off=int(frac*len(w));indices=indices[off:]+indices[:off]
                streams[reader]=dict(words=[w[i] for i in indices],indices=indices)
            stimuli.append(dict(id=c['id'],streams=streams));keys.append(dict(id=c['id'],reverse=rev,family=c['family'],bin=c['bin'],variety=c['variety'],scribe=c['scribe']))
        jsonlines(p/'stimuli.jsonl',stimuli);save(p/'sealed_keys.json',keys);event(p,'KEY_SEALED',sha256=sha(p/'sealed_keys.json'))
        scores=[]
        for st in stimuli:
            row=dict(id=st['id'],streams={})
            for reader,data in st['streams'].items():
                w=data['words'];ix=data['indices'];n=len(w);edgeclasses=caseclasses[st['id']][reader];edges=[]
                for i in range(n):
                    a,b=ix[i],ix[(i+1)%n];orig=a if b==(a+1)%n else b
                    edges.append(dict(classification=edgeclasses[orig],original_edge=orig,values={v:edge(w[i],w[(i+1)%n],models[reader],v) for v in ['raw','matched']}))
                row['streams'][reader]=edges
            scores.append(row)
        jsonlines(p/'edge_scores.jsonl',scores);event(p,'SCORES_SAVED',sha256=sha(p/'edge_scores.jsonl'));event(p,'KEY_OPENED',sha256=sha(p/'sealed_keys.json'));keys=load(p/'sealed_keys.json')
        trials=[];edge_rows=[]
        for k,sc in zip(keys,scores):
            target=-1 if k['reverse'] else 1
            for reader,edges in sc['streams'].items():
                for v in ['raw','matched']:
                    agreed=[e for e in edges if e['classification'] in {'AGREED','LINE_BOUNDARY'}];within=[e for e in edges if e['classification']=='AGREED']
                    trials.append(dict(**k,reader=reader,variant=v,agreed_edges=len(agreed),within_edges=len(within),agreed_score=sum(e['values'][v] for e in agreed),agreed_correct=int(sign(sum(e['values'][v] for e in agreed))==target),within_correct=int(sign(sum(e['values'][v] for e in within))==target)))
                    for e in edges:edge_rows.append(dict(id=k['id'],family=k['family'],bin=k['bin'],variety=k['variety'],scribe=k['scribe'],reader=reader,variant=v,classification=e['classification'],D=e['values'][v]*target))
        jsonlines(p/'trials.jsonl',trials);jsonlines(p/'original_orientation_edges.jsonl',edge_rows)
        metrics=[];classes=[]
        for reader in ['ZL','H']:
            for b in [3,4]:
                for v in ['raw','matched']:
                    ts=[t for t in trials if t['reader']==reader and t['bin']==b and t['variant']==v and t['agreed_edges']>0];fams={t['family'] for t in ts};distinct=len({t['id'] for t in ts});ok=distinct>=30 and len(fams)>=8
                    metrics.append(dict(reader=reader,bin=b,variant=v,windows=distinct,families=len(fams),status='SUPPORTED' if ok else 'UNSUPPORTED',accuracy=sum(t['agreed_correct'] for t in ts)/len(ts) if ts else None,ci=boot([t['agreed_correct'] for t in ts],[t['family'] for t in ts],'boundary'+parse+reader+str(b)+v) if ok else [None,None]))
                    es=[e for e in edge_rows if e['reader']==reader and e['bin']==b and e['variant']==v];families=sorted({e['family'] for e in es});total={f:sum(abs(e['D']) for e in es if e['family']==f and e['classification']!='SYNTHETIC_CLOSE') for f in families}
                    for cl in ['AGREED','LINE_BOUNDARY','ZL_ONLY','H_ONLY','UNRESOLVED_ALIGNMENT','SYNTHETIC_CLOSE']:
                        sub=[e for e in es if e['classification']==cl];num={f:sum(abs(e['D']) for e in sub if e['family']==f) for f in families};den={f:sum(e['family']==f for e in sub) for f in families}
                        classes.append(dict(reader=reader,bin=b,variant=v,classification=cl,n=len(sub),signed_sum=sum(e['D'] for e in sub),absolute_mass=sum(num.values()),mean_abs=sum(num.values())/len(sub) if sub else None,
                            mean_abs_ci=boot([num[f] for f in families],families,'classmean'+parse+reader+str(b)+v+cl,denominators=[den[f] for f in families]) if sub else [None,None],
                            absolute_share=sum(num.values())/sum(total.values()) if sum(total.values()) and cl!='SYNTHETIC_CLOSE' else None,
                            share_ci=boot([num[f] for f in families],families,'classshare'+parse+reader+str(b)+v+cl,denominators=[total[f] for f in families]) if sub and cl!='SYNTHETIC_CLOSE' else [None,None]))
        save(p/'metrics.json',dict(agreed_accuracy=metrics,junction_classes=classes,interpretation='Descriptive representation association only'));save(p/'STATUS.json',dict(status='DESCRIPTIVE_COMPLETE'));results.append(dict(parse=parse,status='DESCRIPTIVE_COMPLETE'));allrows+=metrics
        print('boundary',parse,'DESCRIPTIVE_COMPLETE',flush=True)
    jsonlines(folder/'locus_alignments.jsonl',[dict(parse=parse,locus=lid,**al) for (parse,lid),al in alignment_cache.items()]);save(folder/'summary.json',dict(outcomes=results,agreed_accuracy=allrows));return results

def run():
    check();OUT.mkdir();event(OUT,'RUN_STARTED',binding_sha256=sha(BIND/'EXECUTABLE_MANIFEST.json'))
    fs=fixtures();save(OUT/'fixtures.json',fs)
    if not all(t['passed'] for t in fs):
        save(OUT/'STATUS.json',dict(status='STOP_FAIL_ENGINEERING',I_phase='CLOSED',real_ring_scoring='CLOSED'));return
    event(OUT,'ENGINEERING_PASS');ledger,blocks,natives,zz,hh=intake();p=OUT/'source';p.mkdir();jsonlines(p/'span_validation.jsonl',ledger)
    cases=cases_from(blocks);baseline=cases_from(natives['ZL'],False);save(p/'common_windows.json',cases);save(p/'baseline_ZL_windows.json',baseline)
    sup=support(cases);source_pass=all(x['passed'] for x in sup);source=dict(status='PASS_SOURCE_SPANS' if source_pass else 'STOP_FAIL_SOURCE',support=sup,
        reviewed_pairs=len(ledger),eligible_pairs=sum(r['eligible'] for r in ledger),held_reasons=dict(Counter(x for r in ledger for x in r['reasons'])),
        identity_rule='Reviewed exact ledger; no re-pairing',QC='Agreement<.20 held, not manuscript-fidelity proof')
    agreements=sorted(r['glyph_unit_agreement'] for r in ledger if r['glyph_unit_agreement'] is not None)
    source['agreement_diagnostic']=dict(n=len(agreements),minimum=agreements[0] if agreements else None,median=agreements[len(agreements)//2] if agreements else None,exact_unit_stream_matches=sum(x==1 for x in agreements),screen_is_not_manuscript_accuracy=True)
    save(p/'STATUS.json',source);event(OUT,'SOURCE_GATE',status=source['status']);print('SOURCE',source['status'],sup,flush=True)
    inventories=rows(ROOT/'reading_inventory.csv');source_by_reader=defaultdict(dict)
    for line in s.SOURCE.read_text(encoding='latin-1').splitlines():
        if not line.startswith('<') or ';' not in line.split('>',1)[0]:continue
        head,raw=line.split('>',1);d=s.original_header(head+'>')
        if d['kind'] not in {'body','title'}:continue
        cc=canon.canonical(raw,True)
        if not cc['held']:source_by_reader[d['reader']][d['source_id']]=cc['literal']
    by_zid={r['ZL_id']:r for r in ledger}
    for inv in inventories:
        code=inv['code'];mapped=[r for r in ledger if code in r['original_readers'].split(';')]
        clean_mapped=[r for r in mapped if r['eligible'] and r['original_id'] in source_by_reader[code]]
        supported=[]
        for b in [3,4]:
            eligible=[]
            for c in cases:
                if c['bin']!=b:continue
                ids=[by_zid[lid]['original_id'] for lid in c['source_loci']]
                if not all(lid in source_by_reader[code] for lid in ids):continue
                lo,hi=(11,20) if b==3 else (21,40)
                if all(lo<=sum(len(wordlist(source_by_reader[code][lid],parse)) for lid in ids)<=hi for parse in ['split','join']):eligible.append(c)
            supported.append(dict(bin=b,windows=len(eligible),families=len({c['family'] for c in eligible}),meets_support=len(eligible)>=30 and len({c['family'] for c in eligible})>=8))
        inv.update(reviewed_mapped_loci=len(mapped),primary_admitted=code=='H',word_coverage_status='QUALIFIED_H_ONLY' if code=='H' and source_pass else 'INDEPENDENCE_UNKNOWN_OR_UNSUPPORTED',
            mapped_ZL_word_coverage_split=sum(len(wordlist(zz[r['ZL_id']]['literal'],'split')) for r in clean_mapped),
            heldout_mapped_ZL_word_coverage_split=sum(len(wordlist(zz[r['ZL_id']]['literal'],'split')) for r in clean_mapped if r['split']=='heldout'),
            common_H_panel_coverage_by_bin=supported,coverage_basis='H-qualified source panel; metadata coverage only, not independent-reading qualification')
    save(p/'reading_inventory_final.json',inventories)
    summary=[];boundary=None
    if not source_pass:
        for arm in ['robustness','boundary']:save(OUT/arm/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE',dependency='STOP_FAIL_SOURCE'))
        status='STOP_FAIL_SOURCE'
    else:
        for scope in SCOPES:
            cs=[c for c in cases if inside(c,scope)];stopped=False;primary=[]
            for parse in ['split','join']:
                folder=OUT/'robustness'/scope/'common'/parse
                if stopped:save(folder/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE'));primary.append('NOT_RUN_UPSTREAM_FAILURE');continue
                st=direction_chain(folder,cs,blocks,natives,scope,parse,'common');primary.append(st);stopped=st!='K2R_PASS_CELL'
            overall='K2R_PASS' if all(st=='K2R_PASS_CELL' for st in primary) else next(st for st in primary if st!='K2R_PASS_CELL')
            summary.append(dict(scope=scope,primary_status=overall,parse_status=primary))
            for parse in ['split','join']:
                direction_chain(OUT/'robustness'/scope/'native'/parse,cs,blocks,natives,scope,parse,'native')
        for parse in ['split','join']:direction_chain(OUT/'panel_sensitivity'/parse,baseline,blocks,natives,'aggregate',parse,'native',('ZL',))
        valid={c['ZL']['id']:c for b in blocks for c in b};boundary=boundary_chain(OUT/'boundary',cases,blocks,natives,valid)
        status=summary[0]['primary_status']
    predictions=dict(prediction1=[],prediction2='Panel composition and descriptive within-variety accuracy retained in metrics; no causal tracking test',prediction3=status,prediction4=[])
    if source_pass:
        for parse in ['split','join']:
            mp=OUT/'robustness/aggregate/common'/parse/'metrics.json'
            if mp.exists():
                mm=load(mp)['metrics']
                for v in ['raw','matched']:
                    vals={m['reader']:m['accuracy'] for m in mm if m['bin']==3 and m['variant']==v}
                    predictions['prediction1'].append(dict(parse=parse,variant=v,H_minus_ZL=vals['H']-vals['ZL'],within_2pp=abs(vals['H']-vals['ZL'])<=.02+1e-12))
            else:predictions['prediction1'].append(dict(parse=parse,status='UNTESTED_UPSTREAM_FAILURE_OR_UNSUPPORTED'))
        bm=OUT/'boundary/summary.json'
        if bm.exists():predictions['prediction4']=[dict(**r,at_least_80=bool(r['status']=='SUPPORTED' and r['accuracy']>=.80)) for r in load(bm)['agreed_accuracy'] if r['bin']==4]
    save(OUT/'predictions.json',predictions)
    metric_rows=[];paired_rows=[];class_rows=[];composition_rows=[]
    for mp in sorted((OUT/'robustness').glob('*/*/*/metrics.json')) if source_pass else []:
        mm=load(mp)
        for m in mm['metrics']:metric_rows.append(dict(scope=mm['scope'],training=mm['regime'],parse=mm['parse'],reader=m['reader'],bin=m['bin'],variant=m['variant'],accuracy=m['accuracy'],lower=m['ci'][0],upper=m['ci'][1],windows=m['n'],families=m['families'],ties=m['ties'],passed=m['passed']))
        for m in mm['paired']:paired_rows.append(dict(scope=mm['scope'],training=mm['regime'],parse=mm['parse'],bin=m['bin'],variant=m['variant'],ZL_minus_H=m['ZL_minus_H'],lower=m['ci'][0],upper=m['ci'][1],comparable_label=m['comparable_label']))
        if mm['scope']=='aggregate':
            for m in mm['composition']:composition_rows.append(dict(panel='common',training=mm['regime'],parse=mm['parse'],**m))
    if source_pass:
        for mp in sorted((OUT/'panel_sensitivity').glob('*/metrics.json')):
            mm=load(mp)
            for m in mm['composition']:composition_rows.append(dict(panel='full_ZL',training='native',parse=mm['parse'],**m))
        for mp in sorted((OUT/'boundary').glob('*/metrics.json')):
            for m in load(mp)['junction_classes']:class_rows.append(dict(parse=mp.parent.name,**m))
    if metric_rows:table(OUT/'summary_metrics.csv',metric_rows)
    if paired_rows:table(OUT/'paired_differences.csv',paired_rows)
    if class_rows:table(OUT/'junction_class_table.csv',class_rows)
    save(OUT/'panel_composition.json',composition_rows)
    save(OUT/'summary.json',dict(robustness=summary,boundary=boundary));save(OUT/'STATUS.json',dict(id=s.ID,status=status,source=source['status'],I_phase='CLOSED',spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',prior_gates='UNCHANGED',exposure='Result-motivated on laboratory-exposed material'))
    report=['# K2R execution after reviewed crosswalk','',f'**{status}**','',json.dumps(source,indent=2),'','| Scope | Primary H common-training |','|---|---|']+[f"| {x['scope']} | {x['primary_status']} |" for x in summary]
    report+=['','## Aggregate common-training measurements','','| Parse | Reader | Words | Categories | Accuracy | 95% family CI | Pass |','|---|---|---|---|---|---|---|']
    for m in metric_rows:
        if m['scope']=='aggregate' and m['training']=='common':report.append(f"| {m['parse']} | {m['reader']} | {'11–20' if m['bin']==3 else '21–40'} | {m['variant']} | {m['accuracy']:.3f} | [{m['lower']:.3f}, {m['upper']:.3f}] | {m['passed']} |")
    report+=['','Predictions are scored cell-by-cell in predictions.json. Unsupported or stopped cells are not counted as successes. Reader/native/stratum measurements are in summary_metrics.csv; paired differences in paired_differences.csv; class evidence in junction_class_table.csv; panel composition in panel_composition.json.']
    report+=['','All raw/matched × split/join × bin metrics, paired intervals and source cases are retained in per-chain files. Secondary/native and panel-sensitivity results cannot rescue a primary failure. Stage3 is independently gated by source qualification, not primary performance.','',
        'Earlier K2 and source failures remain unchanged. I-phase, spacing interpretation and real-ring scoring CLOSED; radial HELD. Source agreement screen does not certify manuscript truth or exclude every structural misalignment.']
    (OUT/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8');check();event(OUT,'FINAL_PRESERVATION_PASS')
    save(OUT/'ARTIFACT_MANIFEST.json',dict(hashes={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    save(ROOT/'EXECUTION_INDEX.json',dict(id=s.ID,execution='execution_01',status_file='execution_01/STATUS.json',review_approval='registration/review_freeze/APPROVAL.json',metadata_packet_status_is_historical=True))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['bind','run']);a=p.parse_args()
    try:{'bind':bind,'run':run}[a.stage]()
    except Exception as e:
        if a.stage=='run' and OUT.exists():save(OUT/'TECHNICAL_FAILURE.json',dict(status='STOP_TECHNICAL_FAILURE',error=repr(e),utc=s.now()))
        raise
