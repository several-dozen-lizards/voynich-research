"""Read-only inventory for the Voynich publication snapshot."""
import os, json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
EXCLUDE = {'.git','github-export','tmp','JNAIQ-Builders-rename-20261030','indus-existing-work-audit-2026-10-26','indus-lab-v1','indus-replication-2026-10-26'}
RUNTIME = {'.runtime','.analysis-runtime','.analysis-cache','.dependency-cache','.matplotlib-cache','.venv','venv','node_modules','__pycache__','RUNTIME','runtime','.cache'}
rows=[]; skipped=[]
for base, dirs, files in os.walk(ROOT):
    rel=Path(base).relative_to(ROOT)
    for d in list(dirs):
        if d in RUNTIME or d == '.git' or (rel == Path('.') and d in EXCLUDE):
            skipped.append((rel / d).as_posix()); dirs.remove(d)
    for name in files:
        p=Path(base)/name
        try:
            st=p.stat()
            rows.append({'path':p.relative_to(ROOT).as_posix(),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns})
        except OSError as e: rows.append({'path':p.relative_to(ROOT).as_posix(),'error':str(e)})
OUT.mkdir(exist_ok=True)
(OUT/'inventory.json').write_text(json.dumps({'files':rows,'skipped_directories':skipped},indent=2),encoding='utf-8')
groups=collections.defaultdict(lambda:[0,0])
for r in rows:
    k=r['path'].split('/')[0]; groups[k][0]+=1; groups[k][1]+=r.get('bytes',0)
print(json.dumps({'files':len(rows),'bytes':sum(r.get('bytes',0) for r in rows),'largest_groups':sorted(groups.items(),key=lambda x:-x[1][1])[:20],'largest_files':sorted(rows,key=lambda x:-x.get('bytes',0))[:15],'skipped':skipped[:30]},indent=2))
