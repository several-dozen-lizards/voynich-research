from source_cut2 import CUT
from bs4 import BeautifulSoup
import json
for item in json.loads((CUT/'PETRARCH-ACQUISITION.json').read_text())['files']:
    s=BeautifulSoup((CUT/item['path']).read_bytes(),'html.parser')
    if len(s.select('.poem'))==1:continue
    main=s.select_one('.mw-parser-output')
    print(item['order'],item['url'],'poems',len(s.select('.poem')))
    print(json.dumps([(x.name,x.get('class'),x.get('id'),x.get_text(' ',strip=True)[:1000]) for x in main.select('.testi,p')],ensure_ascii=True)[-3500:])
