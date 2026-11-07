"""Add newly retained research files at the publication assembly cutoff."""
import json, os
from datetime import datetime, timezone
from pathlib import Path

TOOLS=Path(__file__).resolve().parent
ROOT=TOOLS.parents[1]
data=json.loads((TOOLS/'inventory.json').read_text(encoding='utf-8'))
seen={r['path'] for r in data['files']}
excluded={'.git','github-export','tmp','JNAIQ-Builders-rename-20261030','indus-existing-work-audit-2026-10-26','indus-lab-v1','indus-replication-2026-10-26'}
runtime={'.runtime','.analysis-runtime','.analysis-cache','.dependency-cache','.matplotlib-cache','.venv','venv','node_modules','__pycache__','RUNTIME','runtime','.cache'}
added=[]
for base,dirs,files in os.walk(ROOT):
    rel=Path(base).relative_to(ROOT)
    dirs[:]=[d for d in dirs if d not in runtime and d!='.git' and not (rel==Path('.') and d in excluded)]
    for name in files:
        p=Path(base)/name; key=p.relative_to(ROOT).as_posix()
        if key in seen: continue
        st=p.stat(); added.append({'path':key,'bytes':st.st_size,'mtime_ns':st.st_mtime_ns})
data['files'].extend(added)
data['assembly_cutoff_utc']=datetime.now(timezone.utc).isoformat()
(TOOLS/'inventory.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(TOOLS/'inventory-supplement.json').write_text(json.dumps(added,indent=2),encoding='utf-8')
print(json.dumps({'new_files':len(added),'paths': [r['path'] for r in added[:25]]},indent=2))
