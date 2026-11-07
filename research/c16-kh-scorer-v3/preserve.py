"""Write-once archive of v2. No imports or writes inside preserved directories."""
from pathlib import Path
import os,json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parent;V2=R.parent/'c16-kh-scorer-v2';V1=R.parent/'c16-kh'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def inventory(root):
    out={}
    for parent,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if not (os.lstat(Path(parent)/d).st_file_attributes & 0x400)]
        for name in files:
            p=Path(parent)/name
            if p.is_file():out[p.relative_to(root).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    return out
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
def main():
    dest=R/'preservation';dest.mkdir(parents=True,exist_ok=True);assert not (dest/'V2_MANIFEST.json').exists()
    files=inventory(V2)
    with zipfile.ZipFile(dest/'v2-failed-qualification.zip','w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for name in sorted(files):z.write(V2/name,name)
    assert inventory(V2)==files
    dump(dest/'V2_MANIFEST.json',dict(root=str(V2),files=files,archive_sha256=sha(dest/'v2-failed-qualification.zip'),sealed_key_opened=False))
    inputs=R/'inputs';inputs.mkdir(exist_ok=True)
    for name in ['tanakh.json','medieval.json','corpus-stats.json','banks.json','legacy_core.py']:shutil.copyfile(V2/'inputs'/name,inputs/('v2-banks.json' if name=='banks.json' else name))
    shutil.copyfile(V2/'corrected.py',inputs/'v2_corrected.py')
    shutil.copyfile(V2/'C17-LICENSE-README.md',R/'C17-LICENSE-README.md')
    print(json.dumps(dict(v2_files_preserved=len(files),archive_sha256=sha(dest/'v2-failed-qualification.zip'),v2_unchanged=True)))
if __name__=='__main__':main()
