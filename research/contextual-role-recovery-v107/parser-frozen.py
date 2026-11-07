from pathlib import Path
import re,json,hashlib,collections,math,random,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent; OLD=R.parent/'voynich-role-v44'
NS={'t':'http://www.tei-c.org/ns/1.0'}; XI='{http://www.w3.org/XML/1998/namespace}id'
DAYS={'sunday','monday','tuesday','wednesday','thursday','friday','saturday'}
def tag(e):return e.tag.split('}')[-1]
def norm(s):return re.sub(r'\s+',' ',s.strip().lower())
def role(e):
    regs=[norm(''.join(c.itertext())) for c in e if tag(c) in ['reg','expan','corr']]
    if set(regs)&DAYS:return 'weekday'
    if set(regs)&{'am','pm','in meridie','ante meridiem','post meridiem','around noon'}:return 'day_period'
    if set(regs)&{'post','past','ante','before'}:return 'temporal_relation'
    return None
def tokenize(text):return re.findall(r"[^\W\d_]+|\d+|[☉☾☽♂☿♃♀♄]|[|\n]",text.lower(),re.UNICODE)
def parsefile(p):
    s=re.sub(r'<!DOCTYPE[\s\S]*?\]>','',p.read_text(encoding='utf8'))
    s=re.sub(r'&([a-zA-Z][\w.-]*);',lambda m:m[0] if m[1] in ['amp','lt','gt','apos','quot'] else ' | ',s)
    root=ET.fromstring(s);hands=[e.get('sameAs','') for e in root.findall('.//t:handNote',NS)]
    loc=root.find('.//t:locus',NS);ident=root.find('.//t:msIdentifier/t:idno',NS)
    if hands not in [['#sforman'],['#rnapier']] or loc is None or ident is None or loc.get('from')!=loc.get('to'):return None
    page=ident.get('n','?')+':'+re.sub('[^0-9]','',loc.get('from',''))
    # Record-level editorial labels are used only for the answer key.
    chunks=[]
    def put(s,lab=None,form=None):
        chunks.extend((t,lab,form) for t in s.lower())
    def walk(e,lab=None,form=None):
        t=tag(e)
        if 'translation' in e.get(XI,'') or '#translation' in e.get('decls','') or t in ['note','del','gap','unclear','supplied','figure','link']:
            put(' | ');return
        if t in ['lb','pb']:put('\n');return
        if t=='choice':
            c=next((c for name in ['orig','sic','abbr'] for c in e if tag(c)==name),None)
            if c is None:put(' | ');return
            lab=role(e);raw=''.join(c.itertext()).strip()
            form='symbol' if raw in '☉☾☽♂☿♃♀♄' else 'letter_form'
            walk(c,lab,form);return
        put(e.text or '',lab,form)
        for c in e:walk(c,lab,form);put(c.tail or '',lab,form)
        if t in ['p','div']:put('\n')
    body=root.find('t:text/t:body',NS)
    if body is None:return None
    walk(body);segments=[];seg=[];joined=''.join(c[0] for c in chunks);tokens=[]
    for m in re.finditer(r"[^\W\d_]+|\d+|[☉☾☽♂☿♃♀♄]|[|\n]",joined,re.UNICODE):
        chars=chunks[m.start():m.end()];labs=set(c[1] for c in chars);forms=set(c[2] for c in chars)
        tokens.append((m.group(),next(iter(labs)) if len(labs)==1 else None,next(iter(forms)) if len(forms)==1 else None))
    for x in tokens+[('|',None,None)]:
        if x[0] in ['|','\n']:
            if seg:segments.append(seg)
            seg=[]
        else:seg.append(x)
    return dict(case=p.stem,page=page,stratum=hands[0]+'|'+ident.get('n','?')+'|question',segments=segments)
def examples(records,n,shuffle=False):
    out=[];rng=random.Random(4501)
    for r in records:
        for seg0 in r['segments']:
            seg=list(seg0)
            if shuffle:rng.shuffle(seg)
            for i in range(len(seg)-n+1):
                window=seg[i:i+n]
                if any(x[1] is None for x in window) or len(set(x[1] for x in window))!=1:continue
                target=' '.join(x[0] for x in window)
                ctx=[]
                for offset,ix in [(-2,i-2),(-1,i-1),(1,i+n),(2,i+n+1)]:
                    token=seg[ix][0] if 0<=ix<len(seg) else '#edge'
                    ctx.append(str(offset)+':'+hashlib.sha256(token.encode()).hexdigest()[:16])
                ctx+=['leftpair:'+ctx[0]+ctx[1],'rightpair:'+ctx[2]+ctx[3]]
                out.append(dict(page=r['page'],case=r['case'],stratum=r['stratum'],target=target,form='+'.join(x[2] for x in window),y=window[0][1],features=ctx))
    return out
def fit_predict(train,test,kind):
    counts=collections.defaultdict(collections.Counter);tot=collections.Counter();vocab=set()
    for e in train:
        fs=e['features'] if kind=='context' else ['target:'+e['target']]
        counts[e['y']].update(fs);tot[e['y']]+=len(fs);vocab.update(fs)
    labels=sorted(tot)
    if not labels:return []
    preds=[]
    for e in test:
        fs=e['features'] if kind=='context' else ['target:'+e['target']]
        # Uniform class priors; opaque categorical features, add-one smoothing.
        scores={y:sum(math.log((counts[y][f]+1)/(tot[y]+len(vocab)+1)) for f in fs) for y in labels}
        preds.append(max(labels,key=lambda y:scores[y]))
    return preds
def metrics(test,preds):
    c=collections.Counter(e['y'] for e in test);correct=collections.Counter(e['y'] for e,p in zip(test,preds) if e['y']==p)
    return dict(n=len(test),counts=dict(c),macro_recall=sum(correct[y]/c[y] for y in c)/len(c) if c and preds else None,confusion=dict(collections.Counter(e['y']+' -> '+p for e,p in zip(test,preds))))
def main():
    freeze=json.loads((R/'FREEZE.json').read_text())
    for name,h in freeze.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
    old=[parsefile(p) for p in (OLD/'sources').glob('*.xml')];old=[r for r in old if r]
    oldpages=set(r['page'] for r in old)
    fresh=[parsefile(p) for p in sorted((R/'sources').glob('*.xml'))];fresh=[r for r in fresh if r]
    collision=[r['case'] for r in fresh if r['page'] in oldpages];fresh=[r for r in fresh if r['page'] not in oldpages]
    # Fresh training and heldout test folios; old corpus is parser development only.
    train=[r for r in fresh if int(hashlib.sha256(r['page'].encode()).hexdigest()[:8],16)%5>=2]
    test=[r for r in fresh if r not in train]
    outputs=[];allpred=[]
    for stratum in sorted(set(r['stratum'] for r in fresh)):
        tr=[r for r in train if r['stratum']==stratum];te=[r for r in test if r['stratum']==stratum]
        for n in [1,2]:
            a=examples(tr,n);b=examples(te,n);roles=collections.defaultdict(set)
            for e in a:roles[e['target']].add(e['y'])
            amb={k for k,v in roles.items() if len(v)>1}
            pred=fit_predict(a,b,'context');base=fit_predict(a,b,'identity')
            sh=fit_predict(examples(tr,n,True),examples(te,n,True),'context')
            perm=[dict(e) for e in a];ys=[e['y'] for e in perm];random.Random(4502).shuffle(ys)
            for e,y in zip(perm,ys):e['y']=y
            pp=fit_predict(perm,b,'context')
            subset=[i for i,e in enumerate(b) if e['target'] in amb]
            sub=[b[i] for i in subset];subpred=[pred[i] for i in subset] if pred else [];subbase=[base[i] for i in subset] if base else []
            m=metrics(b,pred);mi=metrics(b,base);ms=metrics(examples(te,n,True),sh);mp=metrics(b,pp)
            am=metrics(sub,subpred);ai=metrics(sub,subbase)
            support=len(m['counts'])>=2 and min(m['counts'].values(),default=0)>=20 and len(set(e['page'] for e in b))>=5 and len(sub)>=20 and len(am['counts'])>=2
            passed=support and m['macro_recall']>=.8 and am['macro_recall']>=.8 and am['macro_recall']-ai['macro_recall']>=.1 and m['macro_recall']-ms['macro_recall']>=.1 and mp['macro_recall']<=.6
            outputs.append(dict(stratum=stratum,n=n,status='pass' if passed else 'failed' if support else 'not_estimable',context=m,identity=mi,shuffled=ms,permuted=mp,ambiguous_targets=sorted(amb),ambiguous_context=am,ambiguous_identity=ai,train_occurrences=len(a),test_folios=len(set(e['page'] for e in b))))
            allpred.extend(dict(e,prediction=p,identity_prediction=q) for e,p,q in zip(b,pred,base))
    result=dict(fresh_records=len(fresh),train_records=len(train),test_records=len(test),old_folio_collisions=collision,results=outputs,Voynich='CLOSED',scope='Editorially expanded time/calendar expressions only; ordinary prose roles and semantic relationships not qualified')
    (R/'RESULTS.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    (R/'PREDICTIONS.json').write_text(json.dumps(allpred,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
