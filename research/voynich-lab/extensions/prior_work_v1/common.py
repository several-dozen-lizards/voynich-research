import sys,json,csv,hashlib,random,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.runtime'));sys.path.insert(0,str(ROOT/'.analysis-runtime'))
from src.phase3 import dump,table,rng_for,load_words,layout,relabel
from src.extend_phase3 import read,typed
for d in ['data','report','runs','dictionaries']:(EXT/d).mkdir(exist_ok=True)
def rows(path):return typed(read(path))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def config():return json.loads((EXT/'config.json').read_text())
def registry():return json.loads((EXT/'data/registry.json').read_text())
def corpus(name):return rows(ROOT/registry()[name]['path'])
def split(name):return registry()[name]['split']
def progress(stage,**kwargs):
    dump(EXT/'report/PROGRESS.json',dict(status='RUNNING',stage=stage,**kwargs));print(stage,kwargs,flush=True)
def stable_split(selected,name):
    leaves=sorted({str(r.get('source_group') or re.sub(r'[rv].*$','',r['folio'])) for r in selected})
    rng_for(1729,name+':split').shuffle(leaves)
    n=len(leaves);a,b=max(1,int(.8*n)),max(2,int(.9*n))
    allocation={v:'train' if i<a else 'validation' if i<b else 'test' for i,v in enumerate(leaves)}
    return {r['folio']:allocation[str(r.get('source_group') or re.sub(r'[rv].*$','',r['folio']))] for r in selected}
