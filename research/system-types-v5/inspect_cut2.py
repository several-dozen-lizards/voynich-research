from pathlib import Path
import json,sys
from bs4 import BeautifulSoup
from collections import Counter
p=Path(__file__).parent/'source-cut-2'
if sys.argv[1]=='html':
    for lang in ('czech','latin'):
        path=p/'development'/lang/('index.html' if lang=='czech' else 'mon1.html')
        s=BeautifulSoup(path.read_bytes(),'html.parser')
        print(lang,[(x.get('class'),str(x)[:2200]) for x in s.select('[class*=field--name-field-text]')])
        if lang=='latin': print(str(s.body)[:1600].encode('ascii','backslashreplace').decode())
else:
    from source_cut_probe import get
    for n in ('GillesGuilhem/LemmOc','LostMa-ERC/gatmuza'):
        u='https://api.github.com/repos/'+n;r=json.loads(get(u));commit=json.loads(get(u+'/commits/'+r['default_branch']))['sha'];t=json.loads(get(u+'/git/trees/'+commit+'?recursive=1'))
        path=p/(n.replace('/','-')+'-tree.json');path.write_text(json.dumps(dict(commit=commit,tree=t['tree'])))
        print(n,commit,json.dumps([x['path'] for x in t['tree'] if x['type']=='blob' and not x['path'].endswith(('.jpg','.png'))],ensure_ascii=True)[:10000])
