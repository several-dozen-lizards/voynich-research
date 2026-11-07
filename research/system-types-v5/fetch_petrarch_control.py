"""Additional independent-author development control; selected before body inspection."""
from pathlib import Path
from source_cut_probe import get
from source_cut2 import CUT,dump,validate_selection
from core import sha
from bs4 import BeautifulSoup
import json
validate_selection()
plan=CUT/'ITALIAN-INDEPENDENCE-ADDENDUM.json'
if not plan.exists():dump(plan,dict(role='development only',work='Petrarch, Canzoniere/Rerum vulgarium fragmenta',reason='Independently authored14th-century Italian verse; avoid treating a new Commedia cantica as independent-work evidence.',
    selection_sha256=sha(CUT/'SELECTION.json'),reserve_roles_changed=False,new_reserve_bodies_accessed=False,
    policy='Acquire complete published collection; do not search fresh reserves, cherry-pick gap words, or rewrite diaereses. If absent, retain gap as independent-source limitation.'))
dest=CUT/'development/petrarch';dest.mkdir(exist_ok=True)
urls=[('collection.txt','https://www.liberliber.eu/mediateca/libri/p/petrarca/canzoniere/txt/petrarca_canzoniere.txt'),
      ('index.html','https://linux.studenti.polito.it/static_resources/liberliber/biblioteca/p/petrarca/canzoniere/html/index.htm')]
for name,u in urls:
    try:
        path=dest/name
        if not path.exists():path.write_bytes(get(u))
        print(name,len(path.read_bytes()),flush=True)
        if name.endswith('html'):
            s=BeautifulSoup(path.read_bytes(),'html.parser');print(json.dumps([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]')],ensure_ascii=True)[:10000],flush=True)
        else:print(path.read_bytes()[:900].decode('utf-8','replace').encode('ascii','backslashreplace').decode(),flush=True)
    except Exception as e:print(name,str(e),flush=True)
