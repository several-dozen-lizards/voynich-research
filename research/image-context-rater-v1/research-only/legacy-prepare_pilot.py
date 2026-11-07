"""Audit disclosed text candidates and fetch official source registration sheets.
No visual correspondence scoring; ambiguous canvases are not guessed.
"""
from run_topic import *
from concurrent.futures import ThreadPoolExecutor
import requests,csv
PAIRS=[('cpheor','f88v',['f17v','f96r']),('chokam','f89v2',['f49v','f52r']),('chtody','f89v2',['f4v']),('opol','f89v1',['f90v2']),('darar','f99r',['f33v']),('olsy','f99v',['f5r']),('chols','f100v',['f5v']),('okcheor','f100v',['f93r']),('sarol','f102v2',['f39v'])]
def canvas_label(c):return next(iter(c['label'].values()))[0]
def image_url(c,size='!1800,1800'):
    body=c['items'][0]['items'][0]['body'];return body['service'][0]['@id']+'/full/'+size+'/0/default.jpg'
def download(task):
    url,path=task
    if not path.exists():
        response=requests.get(url,timeout=90);response.raise_for_status();assert response.headers.get('Content-Type','').startswith('image/');path.write_bytes(response.content)
    from PIL import Image
    with Image.open(path) as im:im.verify()
    return {'url':url,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size}
def main():
    source=BASE/'data/text16e6.original.evt';tokens=read(BASE/'tokens.json');lines=source.read_text(encoding='latin-1').splitlines();aud=[]
    for word,page,targets in PAIRS:
        matches=[]
        for line in lines:
            m=re.match(r'^<('+re.escape(page)+r'\.[^;]+);H>\s*(.*)',line)
            if m and word in re.split(r'[.,=\-\s]+',m[2].replace('!','')):
                matches.append({'loc':m[1],'raw':m[2],'scope':'paragraph' if '.P' in m[1] else 'nonparagraph label/annotation'})
        hits=sorted({o['page'] for o in tokens if o['section']=='Botanical' and o['word']==word})
        aud.append({'word':word,'source_page':page,'supplied_targets':targets,'H_source_occurrences':matches,'verified_botanical_H_pages':hits,'extra_pages':sorted(set(hits)-set(targets)),'missing_pages':sorted(set(targets)-set(hits)),'caution':'Exact EVA match is a discovery link, not a plant identification. opol occurs in a multiword source label.' if word=='opol' else 'Discovery candidate; plant association unverified.'})
    dump('candidate-text-audit.json',aud)
    manifest=read(BASE/'botanical-v5/scans/yale-manifest.json');canvases=manifest['items'];selected=[]
    for c in canvases:
        label=canvas_label(c)
        if label in ('88v and 89r','89v (part)','89v (part) and 90r','99r','99v','100v and 101r','102v (part)'):
            selected.append(c)
    (ROOT/'registration').mkdir(exist_ok=True);tasks=[]
    for c in selected:
        oid=c['id'].split('/')[-1];tasks.append((image_url(c),ROOT/'registration'/('canvas-'+oid+'.jpg')))
    with ThreadPoolExecutor(max_workers=4) as pool:images=list(pool.map(download,tasks))
    dump('source-registration-images.json',{'purpose':'Source-panel registration only. These are NOT visual-match outcomes. No target images were inspected.','manifest_sha256':sha(BASE/'botanical-v5/scans/yale-manifest.json'),'images':images,'canvases':[{'id':c['id'],'label':canvas_label(c),'width':c['width'],'height':c['height']} for c in selected]})
    print(json.dumps({'candidate_audit':aud,'source_images':images},indent=2))
if __name__=='__main__':main()
