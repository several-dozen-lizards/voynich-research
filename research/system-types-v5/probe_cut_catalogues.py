from source_cut_probe import get
from pathlib import Path
from bs4 import BeautifulSoup
import json
p=Path(__file__).parent/'source-cut-2'
urls={
'dante-latin':'https://www.thelatinlibrary.com/dante.html',
'oot':'https://api.github.com/repos/UniversalDependencies/UD_Old_Occitan-OOT',
'occitan-digital':'https://api.github.com/search/repositories?q=flamenca',
'cremma-tree':'https://api.github.com/repos/HTR-United/CREMMA-Medieval-LAT/git/trees/292525969ad98380b398e6606a9c2a36d51913ae?recursive=1'}
for n,u in urls.items():
    try:
        b=get(u);(p/(n+'.metadata')).write_bytes(b)
        if n=='dante-latin':
            s=BeautifulSoup(b,'html.parser');print(n,[(a.get_text(),a.get('href')) for a in s.select('a[href]')])
        elif n=='occitan-digital':print(n,[(r['full_name'],r['description']) for r in json.loads(b)['items']][:20])
        elif n=='oot':print(n,json.loads(b).get('default_branch'))
        else:print(n,'saved')
    except Exception as e:print(n,str(e))
