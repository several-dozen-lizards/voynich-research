from pathlib import Path
import csv, hashlib, json, re

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
DATA = Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data')
EVT = DATA / 'text16e6.original.evt'
RESERVED = {'f72v1', 'f72v2', 'f73r', 'f73v'}
CLASSES = ['STAR','SUN-MOON','PL-WHOLE','PL-ROOT','PL-UPPER','VESSEL','FIGURE','WATER','ROSETTE','ANIMAL','OTHER','NONE','UNCLEAR']
COLLAPSE = {'STAR':'CELESTIAL','SUN-MOON':'CELESTIAL','PL-WHOLE':'PLANT','PL-ROOT':'PLANT','PL-UPPER':'PLANT','VESSEL':'VESSEL','FIGURE':'FIGURE-WATER','WATER':'FIGURE-WATER'}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def write_csv(path, fields, rows):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def folio(page): return re.match(r'f\d+', page)[0]

def tokens(raw):
    # Preserve uncertain-space barriers and unreadable slots; padding is not text.
    text = re.sub(r'\{[^}]*\}', '~', raw.split('#')[0])
    text = re.sub(r'[!%\s]', '', text)
    text = re.sub(r'([=\-.,])~+$', r'\1', text).rstrip('=-.')
    parts = re.split(r'([.,=\-])', text)
    out=[]
    for i in range(0,len(parts),2):
        word=parts[i]
        if not word: continue
        uncertain=(i>0 and parts[i-1]==',') or (i+1<len(parts) and parts[i+1]==',')
        out.append(word if re.fullmatch('[a-z]+',word) and not uncertain else None)
    return out

def source():
    meta={r['Folio']:r for r in read_csv(DATA/'Davis-hands.original.csv')}
    units={}; rows=[]; current=None
    for line_no,line in enumerate(EVT.read_text(encoding='latin1').splitlines(),1):
        m=re.match(r'## <(f\d+[rv]\d*\.([^>]+))>',line)
        if m:
            current=m[1]; units[current]={'unit':current,'code':m[2],'comments':[],'source_line':line_no}
        elif line.startswith('## '): current=None
        elif current and line.startswith('# '):
            units[current]['comments'].append(line[2:])
        m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',line)
        if not m: continue
        page,code,num,reading,raw=m.groups(); h=meta.get(page,{})
        rows.append(dict(page=page,folio=folio(page),unit=f'{page}.{code}',code=code,
                         locus=f'{page}.{code}.{num}',line=num,reading=reading,raw=raw,
                         words=tokens(raw),section=h.get('Section','Unknown'),
                         scribe=h.get('Scribe','Unknown'),source_line=line_no))
    return units,rows

def kappa(a,b):
    from collections import Counter
    if len(a)!=len(b) or not a: return None
    ca,cb=Counter(a),Counter(b); n=len(a)
    po=sum(x==y for x,y in zip(a,b))/n
    pe=sum(ca[k]*cb[k] for k in set(ca)|set(cb))/n**2
    return None if pe==1 else (po-pe)/(1-pe)

def feature_dict(word):
    # Operational EVA code-character features, not assertions about handwriting glyphs.
    d={'length':len(word)}
    opener=next((x for x in ['qo','q','ch','sh','ot','ok','d'] if word.startswith(x)), 'other')
    d['opener:'+('q/qo' if opener in ['q','qo'] else opener)]=1
    ending=next((x for x in ['aiin','ain','iin','in','eedy','edy','eey','ey','dy','y','ol','or','ar','al','am','om','m','n','r','l'] if word.endswith(x)), 'other')
    d['ending:'+ending]=1
    for char in set(word): d['glyph:'+char]=1
    for n in (1,2,3):
        for i in range(len(word)-n+1): d[f'ng{n}:'+word[i:i+n]]=1
    d['shape:'+shape(word)]=1
    for glyph in set(re.findall(r'cth|ckh|cph|cfh|ch|sh|[a-z]',word)):
        d['grouped-glyph:'+glyph]=1
    return d

def shape(word):
    """v6.1 operational scaffold; no vowel/consonant or phonetic assumptions."""
    groups=re.findall(r'cth|ckh|cph|cfh|ch|sh|[a-z]',word)
    mapped=['G' if g in ['k','t','p','f','cth','ckh','cph','cfh'] else 'B' if g in ['ch','sh'] else g for g in groups]
    return re.sub('i+','I',re.sub('e+','E',''.join(mapped)))
