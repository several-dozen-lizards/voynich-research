from pathlib import Path
import json,sys,hashlib,math,subprocess,os,re
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;T=R.parent;P=T.parent.parent;V=P/'system-types-v5';sys.path.insert(0,str(V))
from GENERATORS import generate
from published_g5 import verify_source,runtime

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(p)
def parity(f):return 'DISCOVERY' if int(hashlib.sha256(('v8-T3:'+f).encode()).hexdigest(),16)%2==0 else 'CONFIRMATION'
def geometry(dataset,profiles):
 out=[]
 for j,p in enumerate(profiles):
  salt=0
  while True:
   folio=f'PS4:{dataset}:f{j}:s{salt}'
   if parity(folio)==p['arm']:break
   salt+=1
  for k,q in enumerate(p['paragraphs']):out.append(dict(folio=folio,paragraph=k,arm=p['arm'],length=q['length'],unknown=q['unknown'],source_geometry_profile=p['profile']))
 return out

def main():
 family,gn,tt=sys.argv[1:4];trial=int(tt);fi=0 if family=='G5' else 1000000
 gi={'Latin':0,'scribe1':10000,'scribe2':20000}[gn];geo=json.loads((R/'GEOMETRIES.json').read_text())['geometries'];conf=(V/'SOURCES/timm-schinner/source/src/main/resources/conf.properties').read_text(encoding='utf-8');classes=T/'g5-compiled'
 name=f'{family}-{gn}-{trial:03}';seed=892600000+fi+gi+trial;folder=R/'controls'/name;folder.mkdir(parents=True,exist_ok=False);shapes=geometry(name,geo[gn]);save(folder/'GEOMETRY.json',shapes);geometry_sha=sha(folder/'GEOMETRY.json');row=dict(name=name,family=family,geometry=gn,trial=trial,seed=seed,status='PENDING',geometry_sha256=geometry_sha)
 try:
  sizes=[p['length'] for p in shapes];total=sum(sizes)
  if family=='G5':
   native_lines=math.ceil(total/4)+2;settings={'save.path':'./generated/','save.filename':'text.txt','text.lines_to_create':native_lines,'method.random':'pseudo','method.random.pseudo.seed':seed,'method.canFollow':'curveline'}
   (folder/'conf.properties').write_text(conf+'\n'+'\n'.join(f'{k}={v}' for k,v in settings.items())+'\n',encoding='utf-8');(folder/'generated').mkdir();env=dict(os.environ,JAVA_TOOL_OPTIONS='-Xmx64m');rr=subprocess.run([runtime()['java'],'-cp',str(folder)+';'+str(classes),'de.voynich.text.SelfCitationTextGenerator'],cwd=folder,capture_output=True,text=True,timeout=120,env=env)
   (folder/'stdout.txt').write_text(rr.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(rr.stderr,encoding='utf-8');rr.check_returncode();ff=list((folder/'generated').glob('*.txt'));assert len(ff)==1;lines=[s.split() for s in ff[0].read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')];assert len(lines)==native_lines;words=[w for line in lines[1:] for w in line];assert all(re.fullmatch('[a-z]+',w) for w in words);row.update(seed_line_excluded=True,published_source=True,native_lines=native_lines,generated_tokens=len(words),unused_tail_tokens=max(0,len(words)-total))
  else:
   gg=generate('G6',{},seed,line_lengths=sizes);words=[''.join(w) for ln in gg['lines'] for w in ln];save(folder/'NATIVE-MECHANISM.json',dict(table=gg['table'],grille_offsets=gg['grille_offsets'],fidelity=gg['fidelity'],draws=gg['draws']));row.update(generated_tokens=len(words),unused_tail_tokens=0,published_source=False)
  if len(words)<total:raise ValueError('SOURCE_TOO_SHORT: no retry or wrap')
  paras=[];at=0
  for p in shapes:
   tokens=words[at:at+p['length']];at+=p['length']
   for i in p['unknown']:tokens[i]=None
   paras.append(dict(folio=p['folio'],paragraph=p['paragraph'],arm=p['arm'],tokens=tokens))
  assert sha(folder/'GEOMETRY.json')==geometry_sha;save(folder/'PARAGRAPHS.json',paras);row.update(status='GENERATED',paragraphs=len(paras),folios=len({p['folio'] for p in paras}),original_slots=total,unknown_slots=sum(w is None for p in paras for w in p['tokens']),paragraphs_sha256=sha(folder/'PARAGRAPHS.json'))
 except Exception as ex:row.update(status='FAILED',error=repr(ex))
 save(folder/'GENERATION.json',row)
if __name__=='__main__':main()
