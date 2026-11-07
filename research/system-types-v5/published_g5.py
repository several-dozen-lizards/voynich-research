"""Compile/run the pinned, unmodified Timm-Schinner source in isolated run folders."""
from pathlib import Path
import json, subprocess
from core import sha, save

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'SOURCES'/'timm-schinner'/'source'/'src'/'main'

def runtime():
    return json.loads((ROOT/'RUNTIME'/'MANIFEST.json').read_text(encoding='utf-8'))

def verify_source():
    manifest = json.loads((ROOT/'SOURCES'/'timm-schinner-manifest.json').read_text(encoding='utf-8'))
    if not all(sha(ROOT/r['path']) == r['sha256'] for r in manifest['files']):
        raise ValueError('published source hash changed')
    return manifest['commit']

def compile_source():
    commit = verify_source()
    classes = ROOT/'G5-BUILD'/'classes'
    classes.mkdir(parents=True,exist_ok=True)
    files = sorted((SOURCE/'java').rglob('*.java'))
    args = [runtime()['javac'],'-encoding','UTF-8','-d',str(classes)]+[str(p) for p in files]
    result = subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
    save(ROOT/'G5-BUILD'/'COMPILE.json',dict(commit=commit,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,source_files=len(files),source_modified=False))
    result.check_returncode()
    return classes

def run_published(name, seed=19, lines=100, overrides=None):
    verify_source()
    classes = ROOT/'G5-BUILD'/'classes'
    if not (classes/'de/voynich/text/SelfCitationTextGenerator.class').exists(): compile_source()
    folder = ROOT/'G5-RUNS'/name
    folder.mkdir(parents=True,exist_ok=True)
    text = (SOURCE/'resources'/'conf.properties').read_text(encoding='utf-8')
    settings = dict(overrides or {})
    if settings.get('method.canFollow','curveline') not in ('curveline','none'):
        raise ValueError('corpus-derived built-in VMS follow tables are excluded from this experiment')
    if any('\n' in str(v) or '\r' in str(v) or '\n' in k or '\r' in k for k,v in settings.items()):
        raise ValueError('property line injection')
    settings.update({'save.path':'./generated/', 'save.filename':'text.txt', 'text.lines_to_create':str(lines),
                     'method.random':'pseudo','method.random.pseudo.seed':str(seed)})
    # Java Properties keeps the last assignment. Original source stays untouched.
    text += '\n'+'\n'.join(f'{k}={v}' for k,v in settings.items())+'\n'
    (folder/'conf.properties').write_text(text,encoding='utf-8')
    (folder/'generated').mkdir(exist_ok=True)
    result = subprocess.run([runtime()['java'],'-cp',str(folder)+';'+str(classes),'de.voynich.text.SelfCitationTextGenerator'],cwd=folder,capture_output=True,text=True,timeout=120)
    (folder/'stdout.txt').write_text(result.stdout,encoding='utf-8')
    (folder/'stderr.txt').write_text(result.stderr,encoding='utf-8')
    result.check_returncode()
    outputs = list((folder/'generated').glob('*'))
    textfiles = [p for p in outputs if p.is_file() and p.suffix=='.txt']
    if len(textfiles)!=1: raise ValueError(('unexpected output files',outputs))
    raw = textfiles[0].read_text(encoding='utf-8-sig')
    return dict(raw=raw,path=str(textfiles[0]),settings=settings,config_sha256=sha(folder/'conf.properties'))

if __name__ == '__main__':
    compile_source()
    output=run_published('initial-default')
    print(json.dumps({k:v for k,v in output.items() if k!='raw'}))
