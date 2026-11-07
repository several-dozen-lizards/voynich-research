import sys,json,re,copy,random,hashlib,time
from pathlib import Path
P=Path(__file__).parent;B=P.parent;A2=B/'attempt-2-v7.1';V5=B.parent/'system-types-v5';sys.path.insert(0,str(V5));sys.path.insert(0,str(B/'HARNESS'))
from core import load_evt
from sandbox import DATA
from harness import digest

def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(p):return json.loads(p.read_text(encoding='utf8'))
base=read(B/'HARNESS/KNOWN-CIPHER-DATA.json');k=read(B/'HARNESS/KNOWN-KEY.json')
for part in ('train','held'):
 for r in base[part]:r['raw_words']=[''.join('a' if u=='INIT_A' else u[1:] for u in w) if w else None for w in r['words']]
save('KNOWN-DATA.json',base);save('KNOWN-KEY.json',k);save('CORRUPT-KEY.json',read(B/'HARNESS/NEAR-MISS-KEY.json'))
rate=read(A2/'HF-DISAGREEMENT.json')['rate'];H=copy.deepcopy(base);F=copy.deepcopy(base);sites=[(ri,wi,ci) for ri,r in enumerate(base['held']) for wi,w in enumerate(r['raw_words']) for ci in range(len(w))];rng=random.Random(3712);chosen=rng.sample(sites,round(rate*len(sites)));mask=[]
for i,(ri,wi,ci) in enumerate(chosen):
 dest=H if i%2==0 else F;word=list(dest['held'][ri]['raw_words'][wi]);old=word[ci];word[ci]=rng.choice([c for c in k['target']['alphabet'] if c!=old]);dest['held'][ri]['raw_words'][wi]=''.join(word);mask.append({'reading':'H' if i%2==0 else 'F','line':ri,'word':wi,'character':ci,'old':old,'new':word[ci]})
for data in (H,F):
 for r in data['held']:r['words']=[[('INIT_A' if i==0 and c=='a' else 'u'+c) for i,c in enumerate(w)] for w in r['raw_words']]
save('NOISY-H-DATA.json',H);save('NOISY-F-DATA.json',F);save('NOISE-MASK.json',{'source_rate':rate,'sites':len(sites),'changed':len(chosen),'realized_rate':len(chosen)/len(sites),'seed':3712,'edits':mask})
# Source-only native support cohort, selected BEFORE fitting the actual trap.
rows,manifest=load_evt(DATA/'text16e6.original.evt',DATA/'Davis-hands.original.csv');split=read(A2/'TRAP-SLICES.json')['folios'];selected=set(split['train']+split['held']);rows=[r for r in rows if r['folio'] in selected];assert not any(67<=int(re.match(r'f(\d+)',r['folio'])[1])<=73 for r in rows)
by={}
for r in rows:by.setdefault(r['locus'],{})[r['reading']]=r
ledger=[];eligible={'train':[],'held':[]};seen=set()
for r in rows:
 if r['reading']!='H' or r['locus'] in seen:continue
 seen.add(r['locus']);pair=by[r['locus']];part='train' if r['folio'] in split['train'] else 'held';why=[]
 if set(pair)!=set(('H','F')):why.append('missing reading')
 elif any(not pair[q]['tokens'] or any(w is None for w in pair[q]['tokens']) for q in ('H','F')):why.append('native unreadable slot or empty line')
 eligible_now=not why
 admitted=eligible_now and len(eligible[part])<40
 if admitted:eligible[part].append(pair)
 ledger.append({'locus':r['locus'],'folio':r['folio'],'partition':part,'admitted':admitted,'native_eligible':eligible_now,'reason':why if why else ['after fixed first40 limit'] if not admitted else [],'unknown_counts':{q:sum(w is None for w in pair[q]['tokens']) for q in pair}})
for loc,pair in by.items():
 if 'H' not in pair:ledger.append({'locus':loc,'folio':pair['F']['folio'],'admitted':False,'native_eligible':False,'reason':['missingHreading']})
assert all(len(x)==40 for x in eligible.values()),'insufficient native-readable joint support'
cohort={q:{part:[pair[q] for pair in pp] for part,pp in eligible.items()} for q in ('H','F')}
save('TRAP-COHORT.json',{'status':'SOURCE_SUPPORT_FROZEN_BEFORE_KEY_FIT','folios':split,'source_manifest':manifest,'readings':cohort,'selection':'joint native readable H/F; Hsourceorder first40lines per fixed partition'})
save('TRAP-COVERAGE.json',ledger);save('INPUT-SEAL.json',{'utc':time.time(),'files':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['KNOWN-DATA.json','KNOWN-KEY.json','CORRUPT-KEY.json','NOISY-H-DATA.json','NOISY-F-DATA.json','NOISE-MASK.json','TRAP-COHORT.json','TRAP-COVERAGE.json']}})
print(json.dumps({'joint_lines':{p:len(v) for p,v in eligible.items()},'native_unreadable_exclusions':sum('native unreadable slot or empty line' in r['reason'] for r in ledger),'mask':len(chosen)}))
