"""Run frozen Phase 6 analysis. Never prints Hebrew output or opens sealed key."""
from core import *
from prepare import R,ROOT,LAB,dump,read,table,sha
import sys,json,csv,gzip,hashlib,time,pickle
from pathlib import Path
from collections import defaultdict,Counter
BOT=set(hebrew('צמח צמחים עשב עשבים עץ עצים עלה עלים שרש שורש שרשים שורשים פרח פרחים זרע זרעים פרי פירות גן גנים כרם כרמים חטה שעורה'))
AST=set(hebrew('שמש ירח כוכב כוכבים מזל מזלות גלגל גלגלים רקיע לבנה חמה תקופה תקופות ליקוי'))
def kind(r):
    return 'label' if r['is_label']=='True' else ('running' if r.get('locus_code','')[1:] in ['P0','P1','Pc','Pr','Pt'] or r.get('corpus')!='ZL' else 'other')
def metric(acc,tok,out,cs):
    acc['tokens']+=1;acc['hits']+=bool(cs);acc['candidate_total']+=len(cs);acc['ambiguous']+=len(cs)>1;acc['botanical']+=out in BOT;acc['astronomical']+=out in AST
    acc['botanical_any_candidate']+=bool(BOT.intersection(cs));acc['astronomical_any_candidate']+=bool(AST.intersection(cs))
def finalized(x):
    y=dict(x);n=x['tokens']
    for k in ['hits','candidate_total','ambiguous','botanical','astronomical','botanical_any_candidate','astronomical_any_candidate']:y[k+'_rate']=x[k]/n if n else None
    return y
def consistency(groups):
    allpairs=agree=knownpairs=knownagree=crosspairs=crossagree=0;eligible=0
    for source,obs in groups.items():
        if len(obs)<2:continue
        # Each observation corresponds to a different physical slot/context.
        eligible+=1;c=Counter(o for page,line,o in obs);n=len(obs)
        bycontext=defaultdict(Counter)
        for p,l,o in obs:bycontext[p,l][o]+=1
        samepairs=sum(sum(v.values())*(sum(v.values())-1)//2 for v in bycontext.values());sameagree=sum(sum(k*(k-1)//2 for k in v.values()) for v in bycontext.values())
        allpairs+=n*(n-1)//2-samepairs;agree+=sum(k*(k-1)//2 for k in c.values())-sameagree
        kc=Counter(o for page,line,o in obs if o!=UNK);kn=sum(kc.values())
        knownpairs+=kn*(kn-1)//2-sum((sum(k for o,k in v.items() if o!=UNK))*(sum(k for o,k in v.items() if o!=UNK)-1)//2 for v in bycontext.values())
        knownagree+=sum(k*(k-1)//2 for k in kc.values())-sum(sum(k*(k-1)//2 for o,k in v.items() if o!=UNK) for v in bycontext.values())
        bypage=defaultdict(Counter)
        for p,l,o in obs:bypage[p][o]+=1
        crosspairs+=n*(n-1)//2-sum(sum(v.values())*(sum(v.values())-1)//2 for v in bypage.values())
        crossagree+=sum(k*(k-1)//2 for k in c.values())-sum(sum(k*(k-1)//2 for k in v.values()) for v in bypage.values())
    return dict(repeated_types=eligible,pairs=allpairs,pair_agreement=agree/allpairs if allpairs else None,known_pairs=knownpairs,known_pair_agreement=knownagree/knownpairs if knownpairs else None,cross_page_pairs=crosspairs,cross_page_agreement=crossagree/crosspairs if crosspairs else None,within_key_pairs=allpairs-crosspairs,within_key_agreement=(agree-crossagree)/(allpairs-crosspairs) if allpairs>crosspairs else None)
def run(arm):
    outdir=R/'results'/arm;outdir.mkdir(parents=True,exist_ok=True);kroot=outdir/'keys';kroot.mkdir(exist_ok=True)
    p=R/'prepared';data=json.loads((p/f'{arm}.json').read_text());m=Model(data['train']);print(arm,'MODEL READY',flush=True)
    dump(outdir/'language-model.json',dict(train_words=sum(map(len,data['train'])),vocab=len(m.freq),interpolation=m.lm.weights,alphagram_interpolation=m.alm.weights,unknown_unigram_mass=m.lm.unkp,heldout_lines=len(data['test']),heldout_mean_score=sum(m.lm.score(s) for s in data['test'])/len(data['test'])))
    allsummary=[];allcons=[];bestfiles={};fitcache={};fitstats=[];source_specs=json.loads((p/'sources.json').read_text())
    for source in ['ZL','C1','C9','C11','C17']:
      for version in (['clean'] if source=='ZL' else ['clean','noise']):
        name=f'{source}-{version}';done=outdir/f'{name}-DONE.json'
        if done.exists():
            receipt=json.loads(done.read_text());allsummary+=receipt['summary'];allcons+=receipt['consistency'];fitstats+=receipt['fits'];bestfiles[name]=receipt['bestfile'];print(arm,name,'RESUMED COMPLETE',flush=True);continue
        rows=read(p/f'{name}.csv');pages=defaultdict(list)
        for r in rows:pages[r['folio']].append(r)
        sums=defaultdict(Counter);typed=defaultdict(dict);groups=defaultdict(lambda:defaultdict(list));scores=defaultdict(list);best={};writer_sums=defaultdict(Counter);keys={};fs=[]
        tokenpath=outdir/f'{name}-tokens.jsonl.gz';linepath=outdir/f'{name}-lines.jsonl.gz'
        with gzip.open(tokenpath,'wt',encoding='utf8') as tf,gzip.open(linepath,'wt',encoding='utf8') as lf:
          for pi,(page,prs) in enumerate(pages.items()):
            seqs=[r['text_eva'].split() for r in prs];kp=kroot/f'{source}-clean-{page}.json'
            if kp.exists():kr=json.loads(kp.read_text());key=kr['key'];f=kr['fit'];reuse='checkpoint'
            else:
                assert version=='clean','Missing clean key for noise'
                # Canonical alphagrams make character-shuffle control identical when its page coverage matches.
                ident=hashlib.sha256(json.dumps([[alpha(w) for w in s] for s in seqs],ensure_ascii=True).encode()).hexdigest()
                if ident in fitcache:key,f=fitcache[ident];reuse='identical_canonical_input'
                else:
                    m.alm.cache.clear()
                    if len(m.charcache)>200000:m.charcache.clear()
                    t=time.monotonic();key,f=fit(seqs,m);f=dict(f,seconds=time.monotonic()-t);fitcache[ident]=(key,f);reuse='fresh'
                kr=dict(key=key,fit=f,canonical_sha256=ident,registration_sha256=sha(R/'REGISTRATION.json'));dump(kp,kr)
            fs.append(dict(source=source,version=version,page=page,cache=reuse,**f));keys[page]=key
            dc={}
            for v in VARIANTS:
                vid=variant_id(v)
                for unit in traverse(prs,v):
                    ws=[t['word'] for t in unit];sig=tuple(alpha(w) for w in ws)
                    if sig not in dc:dc[sig]=m.decode(ws,key)
                    mapped,cs,outputs,score=dc[sig]
                    # Cached mapped words can differ in order; only alphagrams are stored below.
                    slots=sorted((t['row']['line_id'],t['slot']) for t in unit);identity=hashlib.sha256(json.dumps(slots).encode()).hexdigest()
                    record=dict(source=source,version=version,arm=arm,page=page,writer=prs[0].get('writer',''),size_mismatch=source=='C17',variant=vid,identity=identity,slots=slots,score=score,words=len(ws),unknowns=outputs.count(UNK),decoded=' '.join(outputs),approximate_column=v[3]=='column')
                    lf.write(json.dumps(record,ensure_ascii=True)+'\n');scores[vid].append(record)
                    if identity not in best or (score,-VARIANTS.index(v))>(best[identity]['score'],-best[identity]['variant_index']):best[identity]=dict(record,variant_index=VARIANTS.index(v))
                    for j,(tok,cands,chosen) in enumerate(zip(unit,cs,outputs)):
                        r=tok['row'];w=r['text_eva'].split()[tok['slot']];section=r.get('section') or 'unknown';k=kind(r);g=(vid,section,k)
                        for gg in [(vid,'ALL','ALL'),g]:metric(sums[gg],w,chosen,cands);typed[gg][w]=max(len(cands),typed[gg].get(w,0))
                        if source=='C17':metric(writer_sums[vid,r['writer']],w,chosen,cands)
                        groups[vid][w].append((page,r['line_id'],chosen))
                        tr=dict(source=source,version=version,arm=arm,variant=vid,page=page,line_id=r['line_id'],slot=tok['slot'],source_word=w,mapped_alphagram=alpha(''.join(key.get(c,'\ufffd') for c in w)),candidates=cands,candidate_count=len(cands),selected=chosen,section=section,kind=k,writer=r.get('writer',''),size_mismatch=source=='C17',has_uncertainty=r.get('has_uncertainty',''),is_spurious=r.get('is_spurious',''),is_alternate_branch=r.get('is_alternate_branch',''))
                        tf.write(json.dumps(tr,ensure_ascii=True)+'\n')
            if pi%20==0:print(arm,name,'page',pi+1,'/',len(pages),'evals',f['evaluations'],flush=True)
        summary=[];cons=[]
        for (vid,section,k),acc in sums.items():
            tt=typed[vid,section,k];rr=dict(source=source,version=version,arm=arm,variant=vid,section=section,kind=k,size_mismatch=source=='C17',types=len(tt),type_hits=sum(n>0 for n in tt.values()),type_hit_rate=sum(n>0 for n in tt.values())/len(tt),**finalized(acc))
            if section=='ALL':
                ss=scores[vid];n=100 if source=='ZL' else 25;top=sorted(ss,key=lambda r:(-r['score'],r['identity']))[:n]
                rr.update(lines=len(ss),mean_line_score=sum(r['score'] for r in ss)/len(ss),top_n=len(top),top_n_score=sum(r['score'] for r in top)/len(top),top25_score=sum(r['score'] for r in top[:25])/min(25,len(top)))
            summary.append(rr)
        for (vid,writer),acc in writer_sums.items():summary.append(dict(source=source,version=version,arm=arm,variant=vid,section='WRITER',writer=writer,kind='running',size_mismatch=True,**finalized(acc)))
        for vid,gg in groups.items():cons.append(dict(source=source,version=version,arm=arm,variant=vid,size_mismatch=source=='C17',**consistency(gg)))
        bp=outdir/f'{name}-best-lines.json.gz'
        with gzip.open(bp,'wt',encoding='utf8') as f:json.dump(sorted(best.values(),key=lambda r:(-r['score'],r['variant'],r['identity'])),f,ensure_ascii=True)
        receipt=dict(summary=summary,consistency=cons,fits=fs,bestfile=str(bp.relative_to(R)));dump(done,receipt);allsummary+=summary;allcons+=cons;fitstats+=fs;bestfiles[name]=str(bp.relative_to(R))
        print(arm,name,'DONE',flush=True);m.lm.cache.clear();m.alm.cache.clear()
    table(outdir/'variant-source-section.csv',allsummary);table(outdir/'cross-context-consistency.csv',allcons);table(outdir/'key-fit-receipts.csv',fitstats)
    dump(outdir/'COMPLETE.json',dict(arm=arm,bestfiles=bestfiles,source_versions=len(bestfiles),variants=len(VARIANTS),registration_sha256=sha(R/'REGISTRATION.json')))
if __name__=='__main__':run(sys.argv[1])
