from pathlib import Path
import json,sys,hashlib,importlib.util,re
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;Q=T/'multiword-v2'
spec=importlib.util.spec_from_file_location('qualified_reference',Q/'independent_audit.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
split=load(T/'SPLIT.json');eligible={f['folio']:f for f in split['folios'] if f['arm']=='DISCOVERY'};manifest=load(T.parent.parent/'complete-atlas-v56/SOURCE-MANIFEST.json');source=next(Path(p) for p in manifest['hashes'] if p.endswith('text16e6.original.evt'));assert sha(source)==manifest['hashes'][str(source)]
reserved={'f72v1','f72v2','f73r','f73v'};groups={};seen=set();lines=0;excluded=[]
for line in source.read_text(encoding='latin1').splitlines():
 head,close,body=line.partition('>')
 if not close:continue
 m=re.fullmatch(r'<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])',head)
 if not m:continue
 folio,place,number,reading=m.groups()
 if folio in reserved or folio not in eligible or reading!='H' or not place.startswith('P'):continue
 locus=folio+'.'+place+'.'+number;assert locus not in seen;seen.add(locus);clean=re.sub(r'\{[^}]*\}','',body.split('#')[0]);clean=re.sub(r'[!\s]','',clean);tokens=[w if re.fullmatch('[a-z]+',w) else None for w in re.split(r'[.,=\-]',clean) if w];groups.setdefault((folio,place),[]).append((locus,tokens,'=' in body.split('#')[0]));lines+=1
pp=[]
for (folio,place),rows in groups.items():
 a=[];loci=[]
 for locus,tokens,end in rows:
  a.extend(tokens);loci.append(locus)
  if end:
   if len(a)>1:pp.append(dict(folio=folio,scribe=eligible[folio]['scribe'],loci=loci[:],tokens=a[:]))
   else:excluded.append(dict(loci=loci[:],reason='fewer than two original slots'))
   a=[];loci=[]
 if loci:excluded.append(dict(loci=loci,reason='unterminated paragraph tail'))
assert pp==load(T/'DISCOVERY-PARAGRAPHS.json');outcomes=load(R/'DISCOVERY.json');results=[]
for s in ['1','2']:
 train=[p for p in pp if p['scribe']==s];result=ref.discover(train);actual=outcomes[s];assert result['screened']==actual['screened_early_frames'] and result['eligible']==actual['eligible_candidates'];c=actual['candidate']
 if c is None:assert result['candidate'] is None and actual['status']=='NO CANDIDATE'
 else:assert all(result['candidate'][k]==c[k] for k in ['left','right','gap','variants'])
 results.append(dict(scribe=s,paragraphs=len(train),folios=len({p['folio'] for p in train}),independent_result=result))
save('INDEPENDENT-DISCOVERY-AUDIT.json',dict(status='PASS',source_sha256=sha(source),original_extraction_exact=True,accepted_H_discovery_lines=lines,paragraphs=len(pp),exclusions=excluded,confirmation_bodies_tokenized=0,source_headers_filtered_before_body=True,results=results,scope='Separate Python implementation and source re-extraction; same agent, not external adjudication'))
print('INDEPENDENT DISCOVERY PASS')
