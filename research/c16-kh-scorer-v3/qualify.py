"""Frozen v3 tests. Scorer tests never call a decoder or fitter."""
from corrected import *
from preserve import R,sha,dump
from register import rng,read
import json,csv,hashlib,itertools,statistics,importlib.util,time
from collections import Counter,defaultdict
def table(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [c-r,c+r]
def mechanics(m,train):
    spec=importlib.util.spec_from_file_location('frozen_v2_reference',R/'inputs/v2_corrected.py');v2=importlib.util.module_from_spec(spec);spec.loader.exec_module(v2);legacy.LM=LM
    checks=[]
    for lm,alphagrams in [(m.lm,False),(m.alm,True)]:
        old=v2.LM(train,alphagrams);outgoing=Counter()
        for (a,b,c),n in lm.t.items():outgoing[a,b]+=n
        ctx_exact=outgoing==lm.ctx and all(b!=EOS for a,b in lm.ctx)
        identical=old.u==lm.u and old.b==lm.b and old.t==lm.t and old.bctx==lm.bctx and old.weights==lm.weights and {k:v for k,v in old.ctx.items() if k[1]!=EOS}==dict(lm.ctx)
        max_nonterminal_delta=0.
        for a,b,c in lm.t:max_nonterminal_delta=max(max_nonterminal_delta,abs(math.log(lm.prob(a,b,c))-math.log(old.prob(a,b,c))))
        contexts=sorted(lm.ctx)[:70]+[(UNK,UNK),(BOS,BOS),('unseen-a','unseen-b'),(BOS,'unseen-b'),(UNK,EOS),(EOS,EOS),('unseen',EOS)]
        contexts=(contexts*2)[:100];worst=0.;lo=1.;hi=0.
        for a,b in contexts:
            ps=[lm.prob(a,b,c) for c in lm.vocab];worst=max(worst,abs(sum(ps)-1));lo=min(lo,min(ps));hi=max(hi,max(ps))
        passed=ctx_exact and identical and max_nonterminal_delta<=1e-12 and worst<=1e-10 and lo>0 and hi<=1 and lm.u[UNK]==1 and lm.logp('new-a','new-b','new-c')==lm.logp(UNK,UNK,UNK) and lm.score([UNK])==lm.logp(BOS,BOS,UNK)
        checks.append(dict(model='alphagram' if alphagrams else 'word',contexts=100,ctx_exactly_outgoing=ctx_exact,v2_nonterminal_counter_identity=identical,observed_events_checked=len(lm.t),max_v2_nonterminal_log_delta=max_nonterminal_delta,max_normalization_error=worst,min_probability=lo,max_probability=hi,passed=passed))
    small=Model([['אב','גד','בא']]*20+[['בא','גד','אב']]*10);key={c:c for c in HEB};_,cs,out,_=small.decode(['בא','דג','אב'],key)
    def joint(ws):
        a=b=BOS;s=0.
        for c in ws+[EOS]:s+=small.lm.logp(a,b,c);a,b=b,c
        return s
    exact=joint(out)==max(joint(list(x)) for x in itertools.product(*cs));rows=[dict(line_id='a',text_eva='אב גד'),dict(line_id='b',text_eva='בא אב גד')];conserve=all(sorted(alpha(t['word']) for u in traverse(rows,v) for t in u)==sorted(['אב','אב','אב','גד','גד']) for v in VARIANTS)
    return dict(models=checks,exhaustive_Viterbi=exact,traversal_conservation=conserve,passed=all(c['passed'] for c in checks) and exact and conserve)
def transform(rows,family,tag):
    rd=rng(tag);out=[];perm=list(HEB);rd.shuffle(perm);wrong=dict(zip(HEB,perm))
    for row in rows:
        original=row['text_eva'].split();ws=original[:]
        if family=='word_shuffle':rd.shuffle(ws)
        elif family=='quarter_UNKNOWN':
            idx=set(rd.sample(range(len(ws)),math.ceil(.25*len(ws))));ws=[UNK if i in idx else w for i,w in enumerate(ws)]
        elif family=='all_UNKNOWN':ws=[UNK]*len(ws)
        elif family=='wrong_key':ws=[''.join(wrong.get(c,c) for c in w) for w in ws]
        elif family=='within_word':
            ns=[]
            for w in ws:chars=list(w);rd.shuffle(chars);ns.append(''.join(chars))
            ws=ns
        else:raise ValueError(family)
        out.append(dict(row,text_eva=' '.join(ws),gold_words=original if family=='within_word' else ws))
    return out
def evaluate(rows,m,mode,key=None):
    assert mode in ['gold_scorer','decoded'];variants=[];envelope={};cache={}
    for v in VARIANTS:
        vid=variant_id(v);records=[];dig=[]
        for unit in traverse(rows,v):
            if mode=='gold_scorer':
                out=[t['row'].get('gold_words',t['row']['text_eva'].split())[t['slot']] for t in unit];score=m.lm.score(out);candidate_signature=None
            else:
                words=[t['word'] for t in unit];sig=tuple(alpha(w) for w in words)
                if sig not in cache:cache[sig]=m.decode(words,key)
                _,candidate_signature,out,score=cache[sig]
            identity=tuple(sorted((t['row']['line_id'],t['slot']) for t in unit));unknown=sum(m.lm.canonical(w)==UNK for w in out)
            rec=dict(identity=identity,score=score,words=len(out),unknowns=unknown,variant=vid);records.append(rec);dig.append([identity,out,candidate_signature,score])
            if identity not in envelope or score>envelope[identity]['score']:envelope[identity]=rec
        top=sorted(records,key=lambda r:(-r['score'],r['identity']))[:3]
        variants.append(dict(variant=vid,mode=mode,score=sum(r['score'] for r in top)/len(top),n=len(top),unknown_fraction=sum(r['unknowns'] for r in top)/sum(r['words'] for r in top),digest=hashlib.sha256(json.dumps(dig,ensure_ascii=True).encode()).hexdigest()))
    best=max(variants,key=lambda r:r['score']);top=sorted(envelope.values(),key=lambda r:(-r['score'],r['identity']))[:3]
    return dict(maximum=best['score'],best_variant=best['variant'],unknown_fraction=best['unknown_fraction'],envelope_items=top,variants=variants)
def auc(pos,neg):return sum((p>n)+.5*(p==n) for p in pos for n in neg)/(len(pos)*len(neg))
def run(arm):
    dest=R/'results'/arm;dest.mkdir(parents=True,exist_ok=True);assert not (dest/'RESULT.json').exists(),'Never overwrite exposed results'
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items());banks=json.loads((R/'inputs/banks.json').read_text());data=json.loads((R/'inputs'/f'{arm}.json').read_text());m=Model(data['train']);key={c:c for c in HEB}
    mech=mechanics(m,data['train']);dump(dest/'MATH.json',mech);print(arm,'MATH',mech['passed'],flush=True)
    variant_rows=[];raw_scores=[];decoded_scores=[];corrupt=Counter();prefix=Counter();nlines=unknown_wins=unknown_docwins=0;wins=losses=ties=0;raw_equal=decoded_equal=True;iv=iv_ok=total=total_ok=0
    for i,doc in enumerate(banks['hebrew'][arm]):
        rows=doc['rows'];raw={}
        for family in ['Hebrew','word_shuffle','wrong_key','quarter_UNKNOWN','all_UNKNOWN','within_word']:
            rr=rows if family=='Hebrew' else transform(rows,family,f"{arm}:{doc['document']}:{family}");e=evaluate(rr,m,'gold_scorer');raw[family]=e
            variant_rows.extend(dict(arm=arm,bank=doc['bank'],document=doc['document'],family=family,**v) for v in e['variants']);raw_scores.append(dict(arm=arm,bank=doc['bank'],document=doc['document'],family=family,score=e['maximum'],unknown_fraction=e['unknown_fraction']))
        raw_equal &= all(a['digest']==b['digest'] for a,b in zip(raw['Hebrew']['variants'],raw['within_word']['variants']))
        de=evaluate(rows,m,'decoded',key);ds=evaluate(transform(rows,'within_word',f'{arm}:{doc["document"]}:decode-shuffle'),m,'decoded',key);decoded_equal &= all(a['digest']==b['digest'] for a,b in zip(de['variants'],ds['variants']))
        decoded_scores.append(dict(arm=arm,bank=doc['bank'],document=doc['document'],family='Hebrew_known_key',score=de['maximum'],unknown_fraction=de['unknown_fraction']))
        variant_rows.extend(dict(arm=arm,bank=doc['bank'],document=doc['document'],family='Hebrew_known_key',**v) for v in de['variants'])
        if doc['bank']=='confirmation':
            a=raw['Hebrew']['maximum'];b=raw['word_shuffle']['maximum'];wins+=a>b;losses+=a<b;ties+=a==b;unknown_docwins+=raw['all_UNKNOWN']['maximum']>=a
            comp=[dict(r,family=f) for f in ['Hebrew','quarter_UNKNOWN','all_UNKNOWN'] for r in raw[f]['envelope_items']];unknown_wins+=sum(r['family']=='all_UNKNOWN' for r in sorted(comp,key=lambda r:-r['score'])[:3])
            quarter=transform(rows,'quarter_UNKNOWN',f'{arm}:{doc["document"]}:line-quarter')
            for r,q in zip(rows,quarter):
                ws=r['text_eva'].split();nlines+=1;s=m.lm.score(ws);corrupt['quarter']+=s>m.lm.score(q['text_eva'].split());corrupt['all']+=s>m.lm.score([UNK]*len(ws))
                for k in [1,2,3]:prefix[f'{k}_n']+=1;prefix[f'{k}_beats_UNKNOWN']+=m.lm.score(ws[:k])>m.lm.score([UNK]*k)
                _,_,out,_=m.decode(ws,key)
                for w,o in zip(ws,out):total+=1;iv+=w in m.freq;total_ok+=w==o;iv_ok+=w==o and w in m.freq
        if i%20==0:print(arm,'gold scorer/decoder',i+1,'/80',flush=True)
        if len(m.lm.cache)>200000:m.lm.cache.clear()
    corruption=dict(n=nlines,original_beats_quarter=corrupt['quarter'],original_beats_all=corrupt['all'],UNKNOWN_top3=unknown_wins,UNKNOWN_docwins=unknown_docwins,prefixes=dict(prefix));corruption_pass=nlines==320 and min(corrupt.values())>=.95*nlines and unknown_wins==0 and unknown_docwins==0
    sign=sum(math.comb(wins+losses,k) for k in range(wins,wins+losses+1))/2**(wins+losses);ordering=dict(wins=wins,losses=losses,ties=ties,half_tie_wins=wins+.5*ties,n=40,exact_sign_tail=sign,interval=wilson(wins+.5*ties,40),within_word_equal=raw_equal);order_pass=wins+.5*ties>=32 and raw_equal
    negative=['word_shuffle','wrong_key','quarter_UNKNOWN','all_UNKNOWN'];thresholds={}
    for f in negative:
        xs=sorted(r['score'] for r in raw_scores if r['bank']=='calibration' and r['family']==f);thresholds[f]=xs[math.ceil(.95*len(xs))-1]
    threshold=max(thresholds.values());pos=[r['score'] for r in raw_scores if r['bank']=='confirmation' and r['family']=='Hebrew'];power=sum(x>threshold for x in pos);null_gate=[]
    for f in negative:
        xs=[r['score'] for r in raw_scores if r['bank']=='confirmation' and r['family']==f];fp=sum(x>threshold for x in xs);null_gate.append(dict(family=f,threshold=threshold,positive_exceed=power,positive_n=40,false_positive=fp,n=len(xs),false_positive_interval=wilson(fp,len(xs)),AUC=auc(pos,xs),passed=power>=32 and fp<=2 and len(xs)==40))
    decoder=dict(IV_accuracy=iv_ok/iv,all_token_accuracy=total_ok/total,IV_tokens=iv,all_tokens=total,within_word_equal=decoded_equal,passed=iv_ok/iv>=.9 and total_ok/total>=.8 and decoded_equal)
    scorer=dict(MATH=mech['passed'],CORRUPTION=corruption_pass,ORDER=order_pass,NULL=all(r['passed'] for r in null_gate));scorer_pass=all(scorer.values())
    dump(dest/'SCORER_DECODER.json',dict(scorer_gates=scorer,scorer_passed=scorer_pass,decoder=decoder,corruption=corruption,ordering=ordering,null_gate=null_gate,calibration_thresholds=thresholds))
    # All stages below are separate search/objective/external diagnostics.
    cases=[]
    for i,doc in enumerate([d for d in banks['hebrew'][arm] if d['bank']=='confirmation'][:6]):
        rd=rng(f'{arm}:cipher:{i}');symbols=[chr(0xe500+j) for j in range(22)];rd.shuffle(symbols);enc=dict(zip(HEB,symbols));gold={v:k for k,v in enc.items()};plain=[r['text_eva'].split() for r in doc['rows']];cipher=[]
        for s in plain:
            ns=[]
            for w in s:cs=[enc[c] for c in w];rd.shuffle(cs);ns.append(''.join(cs))
            cipher.append(ns)
        m.alm.cache.clear();fitted,receipt=fit(cipher,m);count=ok=chars=charok=0
        for ps,cs in zip(plain,cipher):
            for w,cw in zip(ps,cs):count+=1;ok+=Counter(w)==Counter(fitted.get(c,'?') for c in cw);chars+=len(cw);charok+=sum(fitted.get(c)==gold[c] for c in cw)
        trueobj=key_objective(cipher,m,gold);fitobj=key_objective(cipher,m,fitted);wrong_scores=[]
        for j in range(100):vals=list(HEB);rng(f'{arm}:cipher:{i}:wrong:{j}').shuffle(vals);wrong_scores.append(key_objective(cipher,m,dict(zip(symbols,vals))))
        lower=sum(trueobj>s for s in wrong_scores);r=dict(case=i,document=doc['document'],alphagram_recovery=ok/count,character_recovery=charok/chars,tokens=count,true_key_objective=trueobj,fitted_key_objective=fitobj,true_minus_fit=trueobj-fitobj,wrong_keys_lower=lower,wrong_keys=100,fit=receipt);cases.append(r)
        dump(dest/f'cipher-{i}.json',dict(result=r,plaintext=plain,ciphertext=cipher,gold_key=gold,fitted_key=fitted,wrong_scores=wrong_scores));print(arm,'separate search',i+1,'/6',round(ok/count,4),flush=True)
    objective_pass=all(r['wrong_keys_lower']>=99 for r in cases);recover=[r['alphagram_recovery'] for r in cases];search_pass=statistics.median(recover)>=.9 and min(recover)>=.75
    external=[]
    for i,d in enumerate([d for d in banks['external'] if d['family']=='C1' or d.get('arm')==arm]):
        assert d['family'] in ['C1','C9'];m.alm.cache.clear();fitted,receipt=fit([r['text_eva'].split() for r in d['clean']],m)
        for version in ['clean','noise']:
            e=evaluate(d[version],m,'decoded',fitted);external.append(dict(arm=arm,family=d['family'],bank=d['bank'],document=d['document'],version=version,score=e['maximum'],unknown_fraction=e['unknown_fraction'],scorer_gate=False,search_involved=True,provenance=d['provenance']));variant_rows.extend(dict(arm=arm,family=d['family'],bank=d['bank'],document=d['document'],version=version,**v) for v in e['variants'])
        dump(dest/f'external-key-{d["family"]}-{d["document"]}.json',dict(key=fitted,fit=receipt))
        if i%20==0:print(arm,'external diagnostic',i+1,'/80',flush=True)
        m.lm.cache.clear()
    table(dest/'variant-source.csv',variant_rows);table(dest/'raw-scorer-maxima.csv',raw_scores);table(dest/'known-key-decoder-maxima.csv',decoded_scores);table(dest/'fitted-external-null-maxima.csv',external)
    result=dict(arm=arm,scorer_gates=scorer,SCORER='PASS' if scorer_pass else 'FAIL',DECODER='PASS' if decoder['passed'] else 'FAIL',OBJECTIVE='PASS' if objective_pass else 'FAIL',SEARCH='PASS' if search_pass else 'FAIL',FRESH_C17='UNAVAILABLE',full_qualification=False,ZL='CLOSED',actual_C11='CLOSED',math=mech,corruption=corruption,ordering=ordering,null_operating_point=null_gate,decoder=decoder,cipher_cases=cases,search_median=statistics.median(recover),search_minimum=min(recover),external_diagnostic_documents=len(external)//2,registration_sha256=sha(R/'REGISTRATION.json'))
    dump(dest/'RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k in ['arm','SCORER','DECODER','OBJECTIVE','SEARCH','FRESH_C17']}),flush=True)
if __name__=='__main__':run(sys.argv[1])
