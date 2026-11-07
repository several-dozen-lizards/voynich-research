"""Download pinned published G5 source only; never executes downloaded code."""
from pathlib import Path
import hashlib, json, urllib.request

ROOT = Path(__file__).resolve().parent
API = 'https://api.github.com/repos/TorstenTimm/SelfCitationTextgenerator'

def read(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()

def main():
    commit = json.loads(read(API + '/commits/master'))['sha']
    tree = json.loads(read(API + '/git/trees/' + commit + '?recursive=1'))
    records = []
    for item in tree['tree']:
        name = item['path']
        if item['type'] != 'blob' or not (name.startswith('source/') or name in ('LICENSE', 'PROPERTIES.md', 'README.md')):
            continue
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe upstream path')
        url = f'https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/{commit}/{name}'
        content = read(url)
        path = ROOT / 'SOURCES' / 'timm-schinner' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != content:
            raise FileExistsError(path)
        path.write_bytes(content)
        records.append(dict(path=str(path.relative_to(ROOT)), url=url, sha256=hashlib.sha256(content).hexdigest()))
    (ROOT / 'SOURCES' / 'timm-schinner-manifest.json').write_text(json.dumps(dict(commit=commit, files=records), indent=2), encoding='utf-8')
    print(json.dumps(dict(commit=commit, downloaded=len(records), executed=False)))

if __name__ == '__main__':
    main()
