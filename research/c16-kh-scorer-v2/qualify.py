"""Frozen candidate qualification. This module admits no manuscript inputs."""
from corrected import *
from preserve import R,OLD,sha,inventory
from register import dump,order
import json,random,hashlib,itertools,statistics,time,csv
from collections import defaultdict,Counter
def rng(tag):return random.Random(int(order('rng',tag)[:16],16))
def table(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [c-r,c+r]
def mechanics(m):
    lm=m.lm;seen=sorted(lm.ctx)[:50];contexts=seen+[(UNK,UNK),(BOS,BOS),('unseen-a','unseen-b'),(BOS,'unseen-b')]
    contexts=(contexts*2)[:100];worst=0.;minimum=1.;maximum=0.
    for a,b in contexts:
        ps=[lm.prob(a,b,c) for c in lm.vocab];worst=max(worst,abs(sum(ps)-1));minimum=min(minimum,min(ps));maximum=max(maximum,max(ps))
    assert len(contexts)==100
    ooveq=lm.logp('unseen-a','unseen-b','unseen-c')==lm.logp(UNK,UNK,UNK)
    one=lm.score([UNK])==lm.logp(BOS,BOS,UNK)
    small=Model([['אב','גד','בא']]*20+[['בא','גד','אב']]*10);key={c:c for c in HEB}
    words=['בא','דג','אב'];_,cs,out,s=small.decode(words,key)
    def joint(ws):
        a=b=BOS;v=0.
        for c in ws+[EOS]:v+=small.lm.logp(a,b,c);a,b=b,c
        return v
    exhaustive=joint(out)==max(joint(list(x)) for x in itertools.product(*cs))
    rows=[dict(line_id='a',text_eva='אב גד'),dict(line_id='b',text_eva='בא אב גד')]
    conservation=all(sorted(alpha(t['word']) for u in traverse(rows,v) for t in u)==sorted(['אב','גד','אב','אב','גד']) for v in VARIANTS)
    return dict(contexts=100,max_normalization_error=worst,min_probability=minimum,max_probability=maximum,UNKNOWN_count=lm.u[UNK],OOV_canonical_equal=ooveq,one_word_rank_excludes_EOS=one,exhaustive_Viterbi=exhaustive,slot_conservation=conservation,passed=worst<=1e-10 and minimum>0 and maximum<=1 and lm.u[UNK]==1 and ooveq and one and exhaustive and conservation)
def transform(rows,family,tag):
    rd=rng(tag);out=[]
    for row in rows:
        ws=row['text_eva'].split()
        if family=='word_shuffle':rd.shuffle(ws)
        elif family=='quarter_UNKNOWN':
            ix=rd.sample(range(len(ws)),math.ceil(.25*len(ws)));ws=[UNK if i in ix else w for i,w in enumerate(ws)]
        elif family=='all_UNKNOWN':ws=[UNK]*len(ws)
        elif family=='within_word':
            tmp=[]
            for w in ws:cs=list(w);rd.shuffle(cs);tmp.append(''.join(cs))
            ws=tmp
        else:raise ValueError(family)
        out.append(dict(row,text_eva=' '.join(ws)))
    return out
def evaluate(rows,m,key):
    variants=[];envelope={};cache={}
    for v in VARIANTS:
        vid=variant_id(v);records=[];dig=[]
        for unit in traverse(rows,v):
            words=[t['word'] for t in unit];sig=tuple(alpha(w) for w in words)
            if sig not in cache:cache[sig]=m.decode(words,key)
            _,cs,out,score=cache[sig];identity=tuple(sorted((t['row']['line_id'],t['slot']) for t in unit))
            record=dict(identity=identity,score=score,words=len(out),unknowns=out.count(UNK),variant=vid)
            records.append(record);dig.append([identity,cs,out,score])
            if identity not in envelope or score>envelope[identity]['score']:envelope[identity]=record
        top=sorted(records,key=lambda r:(-r['score'],r['identity']))[:3]
        variants.append(dict(variant=vid,score=sum(r['score'] for r in top)/len(top),n=len(top),unknown_fraction=sum(r['unknowns'] for r in top)/sum(r['words'] for r in top),digest=hashlib.sha256(json.dumps(dig,ensure_ascii=True).encode()).hexdigest()))
    best=max(variants,key=lambda r:r['score']);top=sorted(envelope.values(),key=lambda r:(-r['score'],r['identity']))[:3]
    return dict(maximum=best['score'],best_variant=best['variant'],unknown_fraction=best['unknown_fraction'],envelope=sum(r['score'] for r in top)/len(top),envelope_items=top,variants=variants)
def auc(positives,negatives):return sum((p>n)+.5*(p==n) for p in positives for n in negatives)/(len(positives)*len(negatives))
def run(arm):
    outdir=R/'results'/arm;outdir.mkdir(parents=True,exist_ok=True);assert not (outdir/'RESULT.json').exists(),'No rerun over a scored bank'
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items())
    banks=json.loads((R/'inputs/banks.json').read_text());data=json.loads((R/'inputs'/f'{arm}.json').read_text());m=Model(data['train']);identity={c:c for c in HEB};gates={};details={};allvariants=[];hebrews=[];nullscores=[];recoveries=[]
    details['mechanics']=mechanics(m);gates['G1']=details['mechanics']['passed'];print(arm,'mechanics',gates['G1'],flush=True)
    corruption_success=Counter();line_n=0;gold_n=iv_n=recovered_iv=recovered_all=0;unknown_wins=0;unknown_doc_wins=0;order_wins=0.;invariance=True;prefix=Counter()
    for di,doc in enumerate(banks['hebrew'][arm]):
        rows=doc['rows'];evaluated={}
        for family in ['Hebrew','word_shuffle','quarter_UNKNOWN','all_UNKNOWN','within_word']:
            rr=rows if family=='Hebrew' else transform(rows,family,f"{arm}:{doc['document']}:{family}")
            e=evaluate(rr,m,identity);evaluated[family]=e
            allvariants.extend(dict(arm=arm,bank=doc['bank'],document=doc['document'],family=family,size_mismatch=False,**v) for v in e['variants'])
        e=evaluated['Hebrew'];hebrews.append(dict(arm=arm,bank=doc['bank'],document=doc['document'],family='Hebrew',size_mismatch=False,score=e['maximum'],unknown_fraction=e['unknown_fraction']))
        invariance &= all(x['digest']==y['digest'] for x,y in zip(e['variants'],evaluated['within_word']['variants']))
        if doc['bank']=='confirmation':
            order_wins+=(e['maximum']>evaluated['word_shuffle']['maximum'])+.5*(e['maximum']==evaluated['word_shuffle']['maximum'])
            unknown_doc_wins+=evaluated['all_UNKNOWN']['maximum']>=e['maximum']
            competitors=[]
            for family in ['Hebrew','quarter_UNKNOWN','all_UNKNOWN']:
                competitors.extend(dict(r,family=family) for r in evaluated[family]['envelope_items'])
            unknown_wins+=sum(r['family']=='all_UNKNOWN' for r in sorted(competitors,key=lambda r:-r['score'])[:3])
            for row,corrupt,missing in zip(rows,transform(rows,'quarter_UNKNOWN',f"{arm}:{doc['document']}:line-quarter"),transform(rows,'all_UNKNOWN','constant')):
                ws=row['text_eva'].split();line_n+=1;s=m.lm.score(ws)
                corruption_success['quarter']+=s>m.lm.score(corrupt['text_eva'].split());corruption_success['all']+=s>m.lm.score(missing['text_eva'].split())
                for length in [1,2,3]:prefix[f'{length}_n']+=1;prefix[f'{length}_positive_beats_UNKNOWN']+=m.lm.score(ws[:length])>m.lm.score([UNK]*length)
                _,cs,out,_=m.decode(ws,identity)
                for w,c,o in zip(ws,cs,out):
                    gold_n+=1;iv_n+=w in m.freq;recovered_all+=w==o;recovered_iv+=(w==o and w in m.freq)
        if di%20==0:print(arm,'Hebrew',di+1,'/80',flush=True)
        if len(m.lm.cache)>200000:m.lm.cache.clear()
    details['G2']=dict(confirmation_lines=line_n,original_beats_quarter=corruption_success['quarter'],original_beats_all=corruption_success['all'],IV_accuracy=recovered_iv/iv_n,all_token_accuracy=recovered_all/gold_n,IV_tokens=iv_n,all_tokens=gold_n,all_UNKNOWN_envelope_selected=unknown_wins,all_UNKNOWN_document_wins=unknown_doc_wins,prefix_audit=dict(prefix))
    gates['G2']=line_n==320 and min(corruption_success.values())>=.95*line_n and recovered_iv/iv_n>=.9 and recovered_all/gold_n>=.8 and unknown_wins==0 and unknown_doc_wins==0
    details['G3']=dict(paired_document_wins=order_wins,n=40,within_word_invariance=invariance,sign_tail=sum(math.comb(40,k) for k in range(math.ceil(order_wins),41))/2**40,win_interval=wilson(order_wins,40))
    gates['G3']=order_wins>=32 and invariance
    for di,doc in enumerate(banks['nulls']):
        assert doc['family'] in ['C1','C9','C17'];rows=doc['clean'];seqs=[r['text_eva'].split() for r in rows];m.alm.cache.clear();key,receipt=fit(seqs,m)
        dump(outdir/f"key-{doc['family']}-{doc['document']}.json",dict(key=key,fit=receipt))
        for version in ['clean','noise']:
            e=evaluate(doc[version],m,key);nullscores.append(dict(arm=arm,bank=doc['bank'],family=doc['family'],document=doc['document'],version=version,size_mismatch=doc['family']=='C17',lines=len(doc[version]),words=sum(len(r['text_eva'].split()) for r in doc[version]),score=e['maximum'],envelope=e['envelope'],unknown_fraction=e['unknown_fraction']))
            allvariants.extend(dict(arm=arm,bank=doc['bank'],document=doc['document'],family=doc['family'],version=version,size_mismatch=doc['family']=='C17',**v) for v in e['variants'])
        if di%20==0:print(arm,'nulls',di+1,'/',len(banks['nulls']),flush=True)
        m.lm.cache.clear()
        if len(m.charcache)>200000:m.charcache.clear()
    g4=[];pos=[r['score'] for r in hebrews if r['bank']=='confirmation']
    for version in ['clean','noise']:
        thresholds={}
        for family in ['C1','C9','C17']:
            cal=sorted(r['score'] for r in nullscores if r['bank']=='calibration' and r['version']==version and r['family']==family);thresholds[family]=cal[math.ceil(.95*len(cal))-1]
        threshold=max(thresholds.values());power=sum(s>threshold for s in pos)
        for family in ['C1','C9','C17']:
            neg=[r['score'] for r in nullscores if r['bank']=='confirmation' and r['version']==version and r['family']==family];fp=sum(s>threshold for s in neg)
            g4.append(dict(version=version,family=family,size_mismatch=family=='C17',threshold=threshold,calibration_thresholds=thresholds,positive_exceed=power,positive_n=len(pos),positive_interval=wilson(power,len(pos)),false_positive=fp,null_n=len(neg),false_positive_interval=wilson(fp,len(neg)),AUC=auc(pos,neg),passed=power>=32 and fp<=1 and len(neg)==(19 if family=='C17' else 20)))
    details['G4']=g4;gates['G4']=all(r['passed'] for r in g4)
    confirm=[d for d in banks['hebrew'][arm] if d['bank']=='confirmation'][:6]
    for ci,doc in enumerate(confirm):
        rd=rng(f'{arm}:cipher:{ci}');alphabet=list(HEB);symbols=[chr(0xe500+i) for i in range(22)];rd.shuffle(symbols);enc=dict(zip(alphabet,symbols));gold={v:k for k,v in enc.items()};plaintext=[r['text_eva'].split() for r in doc['rows']];cipher=[]
        for s in plaintext:
            ns=[]
            for w in s:cs=[enc[c] for c in w];rd.shuffle(cs);ns.append(''.join(cs))
            cipher.append(ns)
        m.alm.cache.clear();key,fitreceipt=fit(cipher,m);total=correct=chars=rightchars=0
        for plain,s in zip(plaintext,cipher):
            for w,cw in zip(plain,s):
                total+=1;correct+=alpha(w)==alpha(''.join(key.get(c,'?') for c in cw));chars+=len(cw);rightchars+=sum(key.get(c)==gold[c] for c in cw)
        trueobj=key_objective(cipher,m,gold);lower=0;wrong_scores=[]
        for trial in range(100):
            vals=list(HEB);rng(f'{arm}:cipher:{ci}:wrong:{trial}').shuffle(vals);wrong=dict(zip(symbols,vals));s=key_objective(cipher,m,wrong);wrong_scores.append(s);lower+=trueobj>s
        record=dict(arm=arm,case=ci,document=doc['document'],tokens=total,alphagram_recovery=correct/total,character_recovery=rightchars/chars,true_key_objective=trueobj,wrong_keys_lower=lower,wrong_keys=100,fit=fitreceipt)
        recoveries.append(record);dump(outdir/f'cipher-{ci}.json',dict(result=record,gold_key=gold,fitted_key=key,plaintext=plaintext,ciphertext=cipher,wrong_objectives=wrong_scores));print(arm,'cipher',ci+1,'/6',round(correct/total,4),flush=True)
    details['G5']=recoveries;rates=[r['alphagram_recovery'] for r in recoveries];gates['G5']=statistics.median(rates)>=.9 and min(rates)>=.75 and all(r['wrong_keys_lower']>=99 for r in recoveries)
    table(outdir/'variant-source.csv',allvariants);table(outdir/'Hebrew-maxima.csv',hebrews);table(outdir/'null-maxima.csv',nullscores)
    dump(outdir/'RESULT.json',dict(arm=arm,gates=gates,details=details,passed=all(gates.values()),ZL='CLOSED',registration_sha256=sha(R/'REGISTRATION.json')))
    print(json.dumps(dict(arm=arm,gates=gates,passed=all(gates.values()))),flush=True)
if __name__=='__main__':run(sys.argv[1])
