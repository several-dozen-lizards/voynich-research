from pathlib import Path
import types,json,hashlib
P=Path(__file__).resolve().parent
for n,h in json.loads((P/'SURFACE-PARSER-FREEZE.json').read_text()).items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
s=(P/'run.py').read_text(encoding='utf8');old="tokens[k][3]=='PUNCT'";new="not any(c.isalnum() for c in tokens[k][1])";assert s.count(old)==1;s=s.replace(old,new)
m=types.ModuleType('surface_preparation');m.__file__=str(P/'run.py');exec(compile(s,m.__file__,'exec'),m.__dict__);m.prepare()
