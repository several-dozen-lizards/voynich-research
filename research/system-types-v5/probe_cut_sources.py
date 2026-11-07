from source_cut_probe import get
from pathlib import Path
import json
from lxml import html
p=Path(__file__).parent/'source-cut-2';p.mkdir(exist_ok=True)
urls={
'latin-library':'https://www.thelatinlibrary.com/palladius.html',
'latin-wiki':'https://la.wikisource.org/wiki/Ruralia_commoda',
'flamenca':'https://oc.wikisource.org/wiki/Flamenca',
'indiana':'https://cl.indiana.edu/~mpmcguir/introduction.php',
'htr-metadata':'https://raw.githubusercontent.com/HTRomance-Project/medieval-latin/fe25eb9ffaa37a32333fe0e3f4093ff4dd8186db/htr-united.yml',
'cremma-metadata':'https://raw.githubusercontent.com/HTR-United/CREMMA-Medieval-LAT/292525969ad98380b398e6606a9c2a36d51913ae/data-registry.csv',
}
for name,u in urls.items():
    try:
        b=get(u);(p/(name+'.metadata')).write_bytes(b)
        if name.endswith('metadata'):print(name,b.decode()[:10000])
        else:
            t=html.fromstring(b);print(name,[(a.text_content()[:70],a.get('href')) for a in t.xpath('//a[@href]')][:120])
    except Exception as e:print(name,type(e).__name__,str(e))
