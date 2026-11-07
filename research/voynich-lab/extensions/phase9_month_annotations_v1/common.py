from pathlib import Path
import json,csv,hashlib,random,unicodedata,re,math,gzip,statistics,sys
R=Path(__file__).resolve().parent
SEEDS=[9011,9013,9019,9029,9041]
LANGS=['Latin','Italian','German','Occitan']
ALPHABET='abcdefghilmnopqrstuvxyz'
TABLES=['alpha','beta1','beta2','beta3','gamma1','gamma2']
FAMILIES=['mono','naibbe','position']
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((R/name).read_text(encoding='utf8'))
def dump(name,value):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sid(*parts):return int.from_bytes(hashlib.sha256(':'.join(map(str,parts)).encode()).digest()[:8],'big')
def letters(text):
 text=unicodedata.normalize('NFD',text)
 text=''.join(c for c in text if unicodedata.category(c)!='Mn')
 for a,b in {'æ':'ae','Æ':'ae','œ':'oe','Œ':'oe','ð':'d','Ð':'d','þ':'th','Þ':'th','ł':'l','Ł':'l','ß':'ss','ø':'o','Ø':'o','ſ':'s'}.items():text=text.replace(a,b)
 text=''.join(c for c in text if c.isalpha()).lower()
 assert all('a'<=c<='z' for c in text),'UNSUPPORTED_CHARACTER'
 return text
def plain(text):return letters(text).replace('w','uu').replace('j','i').replace('k','c')
def alternatives(text):
 # Parentheses denote a finite optional literal group, not arbitrary restoration.
 words=[text]
 while any('(' in w for w in words):
  nextwords=[]
  for word in words:
   m=re.search(r'\(([A-Za-z]+)\)',word)
   if not m:
    assert '(' not in word and ')' not in word;nextwords.append(word);continue
   nextwords.extend([word[:m.start()]+word[m.end():],word[:m.start()]+m[1]+word[m.end():]])
  words=nextwords
 return sorted(set(letters(w) for w in words))
def position(i,n):return 'B' if i==0 else 'E' if i==n-1 else 'M'
def names():
 result={lang:{} for lang in LANGS}
 for row in load('PERIOD_NAMES.json'):result[row['language']][row['month']]=plain(row['form'])
 return result
def codebooks():
 with (R/'author/naibbe_tables.csv').open(encoding='utf-8-sig',newline='') as f:rows={r['code']:r['glyphs'] for r in csv.DictReader(f)}
 return {t:{a:rows[f'unigram_{t}_{a}'] for a in ALPHABET}|{a+b:rows[f'prefix_{t}_{a}']+rows[f'suffix_{t}_{b}'] for a in ALPHABET for b in ALPHABET} for t in TABLES}
def verify():
 assert all(sha(R/p)==h for p,h in load('REGISTRATION.json')['files'].items()),'FROZEN_INPUT_DRIFT'
def jobs():
 return [dict(id=f'{lang}_{encoder}_s{seed}_{kind}',language=lang,encoder=encoder,seed=seed,kind=kind) for lang in LANGS for encoder in ['mono','position']+['naibbe_'+t for t in TABLES] for seed in SEEDS for kind in ['positive','negative']]
