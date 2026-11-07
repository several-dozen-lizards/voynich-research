"""Archive an edited Latin herbal, with revision/attribution, not diplomatic text."""
from pathlib import Path
import hashlib,json,urllib.request,re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent

def main():
    url='https://la.wikisource.org/wiki/De_viribus_herbarum'
    request=urllib.request.Request(url,headers={'User-Agent':'VoynichResearch/1.0 (offline source comparison)'})
    with urllib.request.urlopen(request,timeout=60) as response:raw=response.read()
    folder=ROOT/'SOURCES'/'macer-floridus';folder.mkdir(exist_ok=True)
    (folder/'source.html').write_bytes(raw)
    soup=BeautifulSoup(raw,'html.parser')
    body=soup.select_one('.mw-parser-output')
    if body is None:raise ValueError('missing manuscript-edition body')
    poems=body.select('.poem')
    if not poems:raise ValueError('no verse containers; inspect extraction before using')
    segments=[re.findall('[a-z]+',p.get_text(' ',strip=True).lower()) for p in poems]
    words=[w for segment in segments for w in segment]
    if len(words)<2000:raise ValueError('insufficient extracted verse')
    data=dict(segments=segments,words=words)
    (folder/'words.json').write_text(json.dumps(data),encoding='utf-8')
    revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',raw.decode('utf-8'))
    manifest=dict(url=url,revision=revision[1] if revision else None,title='De viribus herbarum',
                  author='Odo Magdunensis / Macer Floridus',source_kind='edited Latin herbal verse; expanded orthography, not diplomatic',
                  attribution='Latin Wikisource contributors; page revision and source HTML archived',
                  reuse='Medieval underlying text public domain; Wikisource transcription under page footer CC BY-SA terms; preserve attribution',
                  normalization='regex lowercase ASCII a-z words within poem containers; no translation or orthographic modernization',
                  words=len(words),segments=len(segments),sha256_html=hashlib.sha256(raw).hexdigest(),
                  sha256_words=hashlib.sha256((folder/'words.json').read_bytes()).hexdigest(),
                  extraction_scope='poem containers only; page navigation and headings excluded')
    (folder/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest))

if __name__=='__main__':main()
