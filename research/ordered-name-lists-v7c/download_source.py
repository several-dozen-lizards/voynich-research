import urllib.request
from pathlib import Path
p=Path(__file__).parent/'sources'/'picatrix-pingree-1986.pdf'
req=urllib.request.Request('https://commons.warburg.sas.ac.uk/downloads/8g84mm241?locale=en',headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=45) as r: data=r.read()
assert data.startswith(b'%PDF'), 'not PDF'
p.write_bytes(data)
print(len(data))
