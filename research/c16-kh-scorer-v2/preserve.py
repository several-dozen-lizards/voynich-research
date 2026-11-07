"""Copy-first preservation. Never traverse the failed run's dependency junction."""
from pathlib import Path
import os,json,hashlib,zipfile,shutil,datetime
R=Path(__file__).resolve().parent;OLD=R.parent/'c16-kh'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def inventory():
    result={}
    for parent,dirs,files in os.walk(OLD,followlinks=False):
        dirs[:]=[d for d in dirs if not (os.lstat(Path(parent)/d).st_file_attributes & 0x400)]
        for name in files:
            p=Path(parent)/name
            if p.is_file():result[p.relative_to(OLD).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    return result
def main():
    dest=R/'preservation';dest.mkdir(parents=True,exist_ok=True)
    assert not (dest/'FAILED_RUN_MANIFEST.json').exists(),'Preservation is write-once'
    files=inventory()
    with zipfile.ZipFile(dest/'failed-c16-kh.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for name in sorted(files):z.write(OLD/name,name)
    assert inventory()==files
    (dest/'FAILED_RUN_MANIFEST.json').write_text(json.dumps(dict(failed_root=str(OLD),files=files,archive_sha256=sha(dest/'failed-c16-kh.zip'),excluded='directory reparse points, including node_modules',sealed_key_contents_opened=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2),encoding='utf8')
    (R/'inputs').mkdir(exist_ok=True)
    shutil.copyfile(OLD/'core.py',R/'inputs/legacy_core.py')
    for name in ['tanakh.json','medieval.json','corpus-stats.json']:shutil.copyfile(OLD/'prepared'/name,R/'inputs'/name)
    print(json.dumps(dict(preserved_files=len(files),bytes=sum(v['bytes'] for v in files.values()),archive_sha256=sha(dest/'failed-c16-kh.zip'),old_tree_unchanged=True)))
if __name__=='__main__':main()
