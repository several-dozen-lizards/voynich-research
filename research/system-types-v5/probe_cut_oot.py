from source_cut_probe import get
from pathlib import Path
import json
p=Path(__file__).parent/'source-cut-2'
r=json.loads((p/'occitan-digital.metadata').read_bytes());print(json.dumps([(x['full_name'],x['description']) for x in r['items']],ensure_ascii=True))
for name,url in {'oot-readme':'https://raw.githubusercontent.com/UniversalDependencies/UD_Old_Occitan-OOT/master/README.md','oot-tree':'https://api.github.com/repos/UniversalDependencies/UD_Old_Occitan-OOT/git/trees/master?recursive=1'}.items():
    try:
        b=get(url);(p/(name+'.metadata')).write_bytes(b);print(name,b.decode('utf-8').encode('ascii','backslashreplace').decode()[:13000])
    except Exception as e:print(e)
