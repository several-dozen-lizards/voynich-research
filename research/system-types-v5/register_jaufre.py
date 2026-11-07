"""Register archived RIALC edition of the already selected development work."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re
from core import sha
from source_cut2 import CUT,dump,validate_selection

validate_selection();lines=[];files=[]
for i in range(1,8):
    path=CUT/f'development/occitan/jaufre-{i}.htm';s=BeautifulSoup(path.read_bytes(),'html.parser')
    for p in s.find_all('p'):
        if not p.find('font',attrs={'color':re.compile('#c0c0c0',re.I)}):continue
        for br in p.find_all('br'):br.replace_with('\x1e')
        for chunk in p.get_text('').split('\x1e'):
            text=' '.join(chunk.split());match=re.fullmatch(r'(\d+)\s+(.+)',text)
            if not match:
                if text and text!='Jaufre':raise ValueError(('unparsed numbered text',i,text[:200]))
                continue
            lines.append(dict(line=int(match[1]),text=match[2],source_path=str(path.relative_to(CUT)),source_sha256=sha(path)))
    files.append(dict(path=str(path.relative_to(CUT)).replace('\\','/'),sha256=sha(path),url=path.with_suffix('.htm.url').read_text(),partition='development'))
ids=[r['line'] for r in lines]
if ids!=list(range(1,10975)):
    print('LINE DIAGNOSIS',len(ids),'missing',sorted(set(range(1,10975))-set(ids))[:60],'duplicates',len(ids)-len(set(ids)))
    raise ValueError('complete contiguous numbered edition required; no gap stitching')
dump(CUT/'JAUFRE-LINES.json',lines)
dump(CUT/'JAUFRE-PROVENANCE.json',dict(work='Jaufre',edition='Charmaine Lee, RIALC2000 revised2002',
    original_index='https://www.rialc.unina.it/jaufre-i.htm',bibliography='https://arlima.net/il/jaufre.html',
    route='Internet Archive replay of original scholarly edition. Live RIALTO/RIALC TLS certificate expired; certificate verification was never disabled.',
    selection_change='route/edition clarification for the same preregistered work, no reserve role change',
    reuse='No open redistribution license established for electronic edition; internal research only. Do not package for public release.',
    source_language='Old Occitan narrative, not Gascon legal prose',files=files,lines=10974))
print('All10974 lines registered once in edition order.')
