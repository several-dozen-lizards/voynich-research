"""Write the verified snapshot through Git's streaming pack importer."""
import concurrent.futures, json, os, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/'github-export/voynich-research'
receipt=json.loads((ROOT/'catalog/EXPORT-VERIFICATION.json').read_text(encoding='utf-8'))
if not receipt['passed']: raise RuntimeError('archive verification must pass before committing')
manifest=json.loads((ROOT/'catalog/FILES.json').read_text(encoding='utf-8'))
items=[(r['published_path'],r['published_bytes']) for r in manifest if r['published_path']]
extra=list(ROOT.glob('*.md'))+[ROOT/'LICENSE',ROOT/'.gitignore',ROOT/'.gitattributes']
extra.extend(p for p in (ROOT/'catalog').glob('*') if p.is_file())
extra.extend((ROOT/'catalog/studies').glob('*.md'))
extra.extend(p for p in (ROOT/'tools').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
items.extend((p.relative_to(ROOT).as_posix(),p.stat().st_size) for p in extra)
items=sorted(dict(items).items())
parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).strip()
identity=subprocess.check_output(['git','var','GIT_COMMITTER_IDENT'],cwd=ROOT).strip()
message=b'Archive Voynich studies, source records, controls, findings, and export verification\n'
process=subprocess.Popen(['git','fast-import','--quiet','--max-pack-size=256m'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stream=process.stdin
stream.write(b'feature done\ncommit refs/heads/main\ncommitter '+identity+b'\ndata '+str(len(message)).encode()+b'\n'+message+b'from '+parent+b'\ndeleteall\n')

def read_small(item):
    rel,size=item
    return item,(ROOT/rel).read_bytes() if size<=1_000_000 else None

start=time.time(); count=0
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for offset in range(0,len(items),64):
            for (rel,size),data in executor.map(read_small,items[offset:offset+64]):
                stream.write(('M 100644 inline '+json.dumps(rel,ensure_ascii=False)+'\ndata '+str(size)+'\n').encode('utf-8'))
                if data is not None:
                    if len(data)!=size: raise RuntimeError('file size changed: '+rel)
                    stream.write(data)
                else:
                    copied=0
                    with (ROOT/rel).open('rb') as source:
                        for chunk in iter(lambda:source.read(1024*1024),b''): stream.write(chunk); copied+=len(chunk)
                    if copied!=size: raise RuntimeError('file size changed: '+rel)
                stream.write(b'\n'); count+=1
            if offset%4096==0: print(json.dumps({'packed_files':count,'seconds':round(time.time()-start)}),flush=True)
    stream.write(b'\ndone\n'); stream.close()
    process.wait()
    if process.returncode: raise RuntimeError(process.stderr.read().decode('utf-8',errors='replace'))
except BaseException:
    process.kill(); process.wait(); raise
subprocess.run(['git','reset','--mixed','HEAD'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
print(json.dumps({'commit':head,'files':len(items),'parent':parent.decode()},indent=2))
