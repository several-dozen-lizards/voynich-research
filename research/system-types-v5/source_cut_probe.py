import json,urllib.request,ssl
from pathlib import Path
import certifi
ctx=ssl.create_default_context(cafile=certifi.where())
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Voynich-independent-controls/2'}),context=ctx,timeout=60).read()
if __name__=='__main__':
    p=Path(__file__).parent/'source-cut-2';p.mkdir(exist_ok=True)
    u='https://api.github.com/repos/HTRomance-Project/medieval-latin'
    try:
        r=json.loads(get(u)); c=json.loads(get(u+'/commits/'+r['default_branch']))['sha'];t=json.loads(get(u+'/git/trees/'+c+'?recursive=1'))
        (p/'htr-latin-tree.json').write_text(json.dumps({'commit':c,'tree':t['tree']}))
        print(c); print('\n'.join(x['path'] for x in t['tree'] if x['type']=='blob')[:7000])
    except Exception as e:print(type(e).__name__,str(e))
