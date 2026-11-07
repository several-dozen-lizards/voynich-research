from pathlib import Path
import json,csv,hashlib,zipfile,sys,re,unicodedata,random
from collections import Counter
from core import hebrew,VARIANTS,variant_id
R=Path(__file__).resolve().parent;ROOT=R.parent;LAB=ROOT/'voynich-lab';sys.path.insert(0,str(LAB))
from src.noise import inject
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(p,rs):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rs for k in r)));w.writeheader();w.writerows(rs)
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def flatten(x):
    if isinstance(x,str):yield x
    elif isinstance(x,list):
        for y in x:yield from flatten(y)
def main():
    P=R/'prepared';P.mkdir(exist_ok=True);manifest={};exclusions=[];corpusstats={}
    for arm in ['tanakh','medieval']:
        train=[];test=[];versions=[]
        for p in sorted((R/'sources'/arm).glob('*.json')):
            obj=json.loads(p.read_text(encoding='utf8'))
            if obj.get('license')!='Public Domain':
                exclusions.append(dict(file=str(p.relative_to(R)),reason='license '+str(obj.get('license')),title=obj.get('title')));continue
            seqs=[hebrew(s) for s in flatten(obj['text'])];seqs=[s for s in seqs if s];n=int(.8*len(seqs))
            train.extend(seqs[:n]);test.extend(seqs[n:]);versions.append(dict(file=str(p.relative_to(R)),sha256=sha(p),title=obj['title'],license=obj['license'],version=obj['versionTitle'],train_segments=n,test_segments=len(seqs)-n))
        assert train and test
        dump(P/f'{arm}.json',dict(train=train,test=test,versions=versions))
        corpusstats[arm]=dict(works=len(versions),train_words=sum(map(len,train)),test_words=sum(map(len,test)),vocab=len({w for s in train for w in s}),versions=versions)
    zl=read(LAB/'data/voynich/ZL_lines_corrected.csv');page={r['folio']:r for r in zl};sources={'ZL:clean':zl}
    for c in ['C1','C9','C11']:
        for version in ['clean','noise']:
            rows=read(LAB/f'data/controls/{c}/{version}.csv')
            if c=='C1':
                for r in rows:r['text_eva']=r['text_eva'].replace('\ufffd','\ue3ff')
            for r in rows:r.update(section=page[r['folio']]['section'],is_label='False',writer='',size_mismatch='False')
            sources[c+':'+version]=rows
    noise=json.loads((LAB/'report/noise_model.json').read_text())['rates'];z=zipfile.ZipFile(R/'sources/gibberish_transcriptions.zip');c17=[];c17n=[];docs=[]
    for di,name in enumerate(sorted(z.namelist())):
        if not name.endswith('.txt'):continue
        raw=z.read(name);writer=Path(name).stem.replace('Gibberish - ','');text=raw.decode('utf-8-sig');lines=[];removed=Counter()
        for li,s in enumerate(text.splitlines()):
            # Preserve letters/marks; punctuation as word separation, never join through it.
            clean=''.join(c if (unicodedata.category(c)[0] in 'LM' or c.isspace()) else ' ' for c in s)
            removed.update(c for c in s if not (unicodedata.category(c)[0] in 'LM' or c.isspace()))
            ws=clean.split()
            if ws:lines.append((li,' '.join(ws)))
        native=sorted(set(''.join(t.replace(' ','') for _,t in lines)))
        inventory=list('abcdefghijklmnopqrstuvxyz')+['\ufffd']+[chr(0xe200+i) for i in range(10000)]
        # Unlike Phase 3's legacy inventory, reserve U+FFFD solely for unknowns.
        inventory=[x for x in inventory if x!='\ufffd'];mapping=dict(zip(native,inventory))
        rng=random.Random(int.from_bytes(hashlib.sha256(('C16-KH:C17:'+writer).encode()).digest()[:8],'big'))
        folios=sorted(page);assigned=folios[di%len(folios)];section=page[assigned]['section'];alpha=set(mapping.values());ops=Counter()
        for li,s in lines:
            mapped=''.join(mapping.get(c,c) for c in s)
            r=dict(corpus='C17',folio=writer,line_id=f'{writer}.{li+1}',text_eva=mapped,section=section,is_label='False',writer=writer,size_mismatch='True',assigned_page=assigned,metadata_origin='arbitrary_cyclic_ZL_label')
            c17.append(r);noisy,o,preraw=inject(mapped,noise,alpha,rng);ops.update(o);c17n.append(dict(r,text_eva=noisy,pre_whitespace_normalization=preraw))
        docs.append(dict(writer=writer,file=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),lines=len(lines),words=sum(len(s.split()) for _,s in lines),alphabet=len(native),symbol_mapping=mapping,removed_punctuation=dict(removed),noise_operations=dict(ops),size_mismatch=True,assigned_page=assigned,section=section))
    sources['C17:clean']=c17;sources['C17:noise']=c17n
    for k,rs in sources.items():
        family,version=k.split(':');table(P/f'{family}-{version}.csv',rs)
        manifest[k]=dict(lines=len(rs),words=sum(len(r['text_eva'].split()) for r in rs),alphabet=len(set(''.join(r['text_eva'].replace(' ','') for r in rs))),pages=len({r['folio'] for r in rs}),size_mismatch=family=='C17')
    dump(P/'c17-documents.json',docs);dump(P/'corpus-stats.json',corpusstats);dump(P/'corpus-exclusions.json',exclusions);dump(P/'sources.json',manifest)
    prior={str(p.relative_to(ROOT)):sha(p) for sub in ['data','configs','src','report'] for p in (LAB/sub).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    dump(P/'prior-files.json',prior)
    files={str(p.relative_to(R)):sha(p) for p in P.rglob('*') if p.is_file()}
    files.update({str(p.relative_to(R)):sha(p) for p in R.glob('*.py')});files['DECISIONS.md']=sha(R/'DECISIONS.md')
    files['PRE_SCORING_AMENDMENTS.md']=sha(R/'PRE_SCORING_AMENDMENTS.md')
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_SCORING',variants=[variant_id(v) for v in VARIANTS],sources=manifest,files=files,seed_noise='sha256 C16-KH:C17:<writer>',blind='OS entropy, sealed key',corpus_exclusions=exclusions))
    print(json.dumps(dict(sources=manifest,corpora={k:{a:b for a,b in v.items() if a!='versions'} for k,v in corpusstats.items()},excluded_licenses=len(exclusions),c17_files=len(docs)),indent=2))
if __name__=='__main__':main()
