from pathlib import Path
import sys,json,csv,hashlib,random,math,statistics,ast,types
from collections import Counter,defaultdict
R=Path(__file__).resolve().parent;LAB=R.parents[1];I=R/'instrument'
sys.path.insert(0,str(I));sys.path.insert(0,str(LAB/'.runtime'));sys.path.insert(0,str(LAB/'.analysis-runtime'))
SEEDS=[1729,1733,1741,1753,1777]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,allow_nan=False)+'\n',encoding='utf8')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for x in rows for k in x)));w.writeheader();w.writerows(rows)
def typed(rows):return [{**r,'is_para_start':None if r.get('is_para_start','')=='' else str(r['is_para_start'])=='True'} for r in rows]
def seed_for(*parts):return int.from_bytes(hashlib.sha256(':'.join(map(str,parts)).encode()).digest()[:8],'big')
def module():
    path=R/'author/naibbe.py';tree=ast.parse(path.read_text(encoding='utf8'));nodes=[]
    for node in tree.body:
        if isinstance(node,ast.Import):
            node.names=[n for n in node.names if n.name not in ['pandas','random']]
            if not node.names:continue
        if isinstance(node,ast.If):continue
        nodes.append(node)
    def rcsv(ignored):
        data=read(R/'author/naibbe_tables.csv');return {k:[r[k] for r in data] for k in data[0]}
    m=types.ModuleType('pinned_naibbe');m.__dict__.update(random=random.Random(1729),pd=types.SimpleNamespace(read_csv=rcsv))
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),m.__dict__);return m
def candidates():return json.loads((R/'CANDIDATES.json').read_text())
def metadata():return json.loads((R/'LAYOUT.json').read_text())
def split():return json.loads((I/'configs/page_split.json').read_text())
def plaintext(family):return (R/'plaintext'/f'{family}.txt').read_text(encoding='utf8')
def generated(family,candidate,seed,only_train=False):
    meta=metadata();sp=split();rows=[];receipts=[];offset=0
    if family=='C9':
        from src.encoders import grille
        cfg=json.loads((I/'configs/phase3.json').read_text());words,book=grille(sum(x['word_slots'] for x in meta),random.Random(seed_for(seed,family,candidate['id'])),cfg)
    else:plain=plaintext(family);m=module();m.RESPACING=candidate['respacing'];m.CARD_WEIGHTS[False]=candidate['weights']
    bypage=defaultdict(list)
    for x in meta:bypage[x['folio']].append(x)
    for page,lines in bypage.items():
        n=sum(x['word_slots'] for x in lines);start=offset;offset+=2*n
        if only_train and sp[page]!='train':continue
        if family=='C9':tokens=words[start//2:offset//2];used=n;retries=0
        else:
            chunk=plain[start:offset];assert len(chunk)==2*n
            m.random=random.Random(seed_for(seed,family,candidate['id'],page));m.ambiguity_retries=0
            units=[];orig=m.respace_plaintext
            def capture(*args,**kwargs):
                value=orig(*args,**kwargs);units.extend(value);return value
            m.respace_plaintext=capture
            try:tokens=m.encrypt_naibbe(chunk,m.naibbe_tables,m.placeholder_to_glyph,use_78=False)
            finally:m.respace_plaintext=orig
            assert len(tokens)>=n;tokens=tokens[:n];used=sum(map(len,units[:n]));retries=m.ambiguity_retries
        receipts.append(dict(page=page,source_start=start,source_stop=offset,plaintext_used_characters=used,unused_suffix_characters=2*n-used if family!='C9' else None,ambiguity_retries=retries,setting=candidate['id'],seed=seed,split=sp[page]))
        j=0
        for line in lines:
            count=line['word_slots'];rows.append({**line,'text_eva':' '.join(tokens[j:j+count])});j+=count
        assert j==len(tokens)==n
    return rows,receipts
def edit1(a,b):
    if abs(len(a)-len(b))>1:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b):a,b=b,a
    j=0
    while j<len(a) and a[j]==b[j]:j+=1
    return a[j:]==b[j+1:]
def fingerprint(rows):
    from src.metrics import conditional
    h2,support=conditional([list(r['text_eva']) for r in rows],2);hist=Counter();vocab=Counter();same=near=total=0
    for r in rows:
        words=r['text_eva'].split();vocab.update(words);hist.update(map(len,words))
        for a,b in zip(words,words[1:]):same+=a==b;near+=edit1(a,b);total+=1
    return dict(h2=h2,h2_support=support,hist=dict(hist),vocab=dict(vocab),identical=same/total if total else None,edit1=near/total if total else None,transitions=total,words=sum(hist.values()),types=len(vocab),lines=len(rows),pages=len({r['folio'] for r in rows}))
def w1(a,b):
    a={int(k):v for k,v in a.items()};b={int(k):v for k,v in b.items()};na=sum(a.values());nb=sum(b.values());ca=cb=0.;terms=[]
    for k in range(max(max(a),max(b))+1):ca+=a.get(k,0)/na;cb+=b.get(k,0)/nb;terms.append(abs(ca-cb))
    return math.fsum(terms)
def verify_registration():
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items()),'Registration drift'
def target_train():
    rows=typed(read(R/'train_target.csv'));assert all(split()[r['folio']]=='train' for r in rows);return rows
def choose_rows(rows,label):return [r for r in rows if r['currier_lang'] in ['A','B'] and (label=='pooled' or r['currier_lang']==label)]
