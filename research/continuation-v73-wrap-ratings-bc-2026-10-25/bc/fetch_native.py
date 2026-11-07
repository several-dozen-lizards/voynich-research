from pathlib import Path
import urllib.request,json,hashlib,zipfile,io
P=Path(__file__).parent;ROOT=P.parents[1];dest=P/'native-rapidfuzz-3.14.1';dest.mkdir(exist_ok=True)
meta=json.load(urllib.request.urlopen('https://pypi.org/pypi/RapidFuzz/3.14.1/json',timeout=30));items=[u for u in meta['urls'] if u['filename'].endswith('cp310-cp310-win_amd64.whl')];assert len(items)==1
u=items[0];data=urllib.request.urlopen(u['url'],timeout=45).read();assert hashlib.sha256(data).hexdigest()==u['digests']['sha256']
(P/u['filename']).write_bytes(data)
with zipfile.ZipFile(io.BytesIO(data)) as z:
 for name in z.namelist():assert (dest/name).resolve().is_relative_to(dest.resolve())
 z.extractall(dest)
comparison={}
for rel in ['process_py.py','distance/Levenshtein_py.py','_utils.py','utils_py.py']:
 a=ROOT/'ordered-name-lists-v7c/HARNESS/vendor/rapidfuzz'/rel;b=dest/'rapidfuzz'/rel;comparison[rel]=dict(same=a.read_bytes()==b.read_bytes(),baseline_sha256=hashlib.sha256(a.read_bytes()).hexdigest(),wheel_sha256=hashlib.sha256(b.read_bytes()).hexdigest())
out=dict(version='3.14.1',file=u['filename'],url=u['url'],sha256=u['digests']['sha256'],local_target=str(dest.relative_to(ROOT)),no_global_install=True,baseline_unchanged=True,pure_source_comparison=comparison)
(P/'NATIVE-ACQUISITION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
