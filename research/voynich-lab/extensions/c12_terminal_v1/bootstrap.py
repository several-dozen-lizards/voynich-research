"""Prepare an isolated terminal grid. Never edits an earlier run."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parent;LAB=R.parents[1];P=R.parent/'c12_partial_v1'
assert not (R/'INPUT_SNAPSHOT.json').exists()
for name in ['common.py','generate.py','run.py','summarize.py','setup.py']:
    shutil.copyfile(P/name,R/name)
common=(R/'common.py').read_text()
a=common.index('def settings():');b=common.index('def tensor_fingerprint',a)
common=common[:a]+'''def final_settings():
    out=[]
    for agg in [.65,.8,.9,1.]:
        for mode,fraction in [('sigla_only',None),('subset25',.25)]:
            for rigidity in [0.,1.]:
                out.append(dict(setting=f'T{len(out):02d}',mode=mode,fraction=fraction,sequence_length=2,slot_rigidity=rigidity,aggressiveness=agg,old_reference=None,role='terminal'))
    return out
def settings():
    out=final_settings()
    for name in ['C15_Italian_52','C15_Italian_78','C15_Latin_52','C15_Latin_78','C9','C18_bigraph2','C18_addB']:
        out.append(dict(setting=name,mode=name,fraction=None,sequence_length=None,slot_rigidity=None,aggressiveness=None,old_reference=None,role='comparison'))
    return out
''' +common[b:]
(R/'common.py').write_text(common,encoding='utf8')
gen=(R/'generate.py').read_text().replace('for s in settings():','for s in final_settings():').replace("out,meta=encode_partial(words,cfg,s);", "cfg['encoder_aggressiveness']=s['aggressiveness'];out,meta=encode_partial(words,cfg,s);")
gen=gen.replace("    table(R/'DATA_MANIFEST.csv',manifest);",'''    for s in settings():
        if s['role']!='comparison':continue
        for version in ['clean','noise']:
            path=R/'data'/s['setting']/f'{version}.csv';rs=typed(read(path))
            manifest.append({**s,'version':version,'words':sum(len(r['text_eva'].split()) for r in rs),'characters':sum(len(r['text_eva'].replace(' ','')) for r in rs),'data_sha256':sha(path)})
    table(R/'DATA_MANIFEST.csv',manifest);''')
(R/'generate.py').write_text(gen,encoding='utf8')
# The original snapshot routine checks unchanged sources against Phase 5.
import setup
setup.main()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf8')
snap=json.loads((R/'INPUT_SNAPSHOT.json').read_text())
prior=LAB/'extensions/prior_work_v1';registry=json.loads((prior/'data/registry.json').read_text())
from common import settings
for s in settings():
    if s['role']!='comparison':continue
    for v in ['clean','noise']:
        name=s['setting']+'_'+v;src=LAB/registry[name]['path'];dst=R/'data'/s['setting']/f'{v}.csv';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        snap.setdefault('comparison_source_hashes',{})[str(src.relative_to(LAB))]=sha(src)
        split=json.loads((R/'instrument/configs/page_split.json').read_text())
        assert registry[name]['split']==split,(name,'split mismatch')
# Preserve every previous partial result, source, receipt, dataset and model/config file.
snap['previous_partial_hashes']={str(p.relative_to(LAB)):sha(p) for p in P.rglob('*') if p.is_file() and '__pycache__' not in str(p) and '.mplcache' not in str(p)}
snap['comparison_registry_hash']=sha(prior/'data/registry.json')
dump(R/'INPUT_SNAPSHOT.json',snap)
print('Isolated setup complete; earlier partial snapshot',len(snap['previous_partial_hashes']))
