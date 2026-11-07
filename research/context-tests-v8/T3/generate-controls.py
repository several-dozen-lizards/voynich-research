from pathlib import Path
import sys,json,subprocess,math,os,hashlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;P=R.parent.parent;V=P/'system-types-v5';sys.path.insert(0,str(V))
from GENERATORS import generate
from published_g5 import verify_source,runtime
verify_source()
paras=json.loads((R/'DISCOVERY-PARAGRAPHS.json').read_text())
results=[]
for family in ['G5','G6']:
 for scribe in ['1','2']:
  pp=[p for p in paras if p['scribe']==scribe];sizes=[len(p['tokens']) for p in pp];total=sum(sizes)
  folios=list(dict.fromkeys(p['folio'] for p in pp))
  for trial in range(20):
   seed=825000+(0 if family=='G5' else 10000)+int(scribe)*1000+trial
   folder=R/'generator-runs'/f'{family}-s{scribe}-{trial:02}';folder.mkdir(parents=True,exist_ok=False)
   row=dict(family=family,scribe=scribe,trial=trial,seed=seed,status='PENDING',paragraph_sizes=sizes)
   try:
    if family=='G5':
     native_lines=math.ceil(total/4)+2
     text=(V/'SOURCES/timm-schinner/source/src/main/resources/conf.properties').read_text()
     settings={'save.path':'./generated/','save.filename':'text.txt','text.lines_to_create':native_lines,'method.random':'pseudo','method.random.pseudo.seed':seed,'method.canFollow':'curveline'}
     text+='\n'+'\n'.join(f'{k}={v}' for k,v in settings.items())+'\n';(folder/'conf.properties').write_text(text)
     (folder/'generated').mkdir();env=dict(os.environ,JAVA_TOOL_OPTIONS='-Xmx64m')
     run=subprocess.run([runtime()['java'],'-cp',str(folder)+';'+str(V/'G5-BUILD/classes'),'de.voynich.text.SelfCitationTextGenerator'],cwd=folder,capture_output=True,text=True,timeout=120,env=env)
     (folder/'stdout.txt').write_text(run.stdout);(folder/'stderr.txt').write_text(run.stderr);run.check_returncode()
     files=list((folder/'generated').glob('*.txt'));assert len(files)==1
     lines=[x.split() for x in files[0].read_text(encoding='utf-8-sig').splitlines() if x.strip() and not x.startswith('#')]
     assert len(lines)==native_lines
     words=[w for ln in lines[1:] for w in ln];row.update(seed_line_excluded=True,native_lines=native_lines,generated_tokens=len(words),unused_tail_tokens=max(0,len(words)-total),published_source=True)
    else:
     generated=generate('G6',{},seed,line_lengths=sizes)
     (folder/'native-mechanism.json').write_text(json.dumps(generated))
     words=[''.join(w) for ln in generated['lines'] for w in ln];row.update(generated_tokens=len(words),unused_tail_tokens=0,published_source=False,model='v5 parametric repeated-column table/grille')
    if len(words)<total:raise ValueError('SOURCE_TOO_SHORT; no retry or wrapping')
    synthetic=[];cursor=0
    for j,p in enumerate(pp):
     f=f'control-{family}-s{scribe}-t{trial}-f{folios.index(p["folio"])}'
     synthetic.append(dict(folio=f,scribe=scribe,tokens=words[cursor:cursor+sizes[j]]));cursor+=sizes[j]
    (folder/'paragraphs.json').write_text(json.dumps(synthetic));row['status']='GENERATED'
   except Exception as e:row.update(status='FAILED',error=repr(e))
   results.append(row)
   (R/'GENERATOR-ACQUISITION.json').write_text(json.dumps(results,indent=2))
   print(family,scribe,trial,row['status'],flush=True)
