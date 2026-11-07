"""Independent development acquisition. Reserve bodies are deliberately inaccessible here."""
from pathlib import Path
import json,hashlib,re,urllib.parse,sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from source_cut_probe import get

ROOT=Path(__file__).resolve().parent
CUT=ROOT/'source-cut-2'
COMMIT='292525969ad98380b398e6606a9c2a36d51913ae'
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=True,indent=2),encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def register():
    path=CUT/'SELECTION.json'
    if path.exists():raise FileExistsError(path)
    dev=['Egerton821','WettF0015','BIS-193','Mazarine915','Arras-861','Latin6395','UBL758','CCCC-MSS-236','LaurentianusPluteus33.31',
         'LaurentianusPluteus39.34','LaurentianusPluteus53.08','LaurentianusPluteus53.09','Latin8236','BGO-511','SBB_PK_Hdschr25']
    plan=dict(cut='independent-development-2',date='2026-10-25',status='DEVELOPMENT_BUILD_NOT_CLAIM_FREEZE',
        selection_basis='Known cut1 alphabet and seven length shortages are exposed; development selection targets them. Fresh reserves are assigned by work/manuscript identity before body acquisition and are never searched for missing units.',
        development=dict(Latin=dict(work='Dante, Monarchia',urls=[f'https://www.thelatinlibrary.com/dante/mon{i}.shtml' for i in range(1,4)],scope='14th-century political prose, NONMEDICAL Latin length sensitivity; one continuous work; not herbal-register replacement'),
            Italian=dict(work='Dante, Commedia, Purgatorio',url='https://it.wikisource.org/wiki/Divina_Commedia/Purgatorio',scope='new cantica; shared author and larger work with old Inferno; NOT author/work-independent replication'),
            Czech=dict(work='Mastickar, Muzejni fragment',url='https://czech.mml.ox.ac.uk/mastickar',scope='14th-century dramatic fragment; diplomatic spelling supplement only; not a long generation source; no modernization or supplied expansions'),
            Occitan=dict(work='Jaufre',url='https://www.rialto.unina.it/poesia_narrativa/jaufre/',scope='13th-century narrative verse; broader Old Occitan, NOT independent Old Gascon legal-register qualification'),
            AbbreviatedLatin=dict(repository='HTR-United/CREMMA-Medieval-LAT',commit=COMMIT,manuscripts=dev,scope='unread manuscripts selected by pre-existing genre/date metadata; medical/scholastic/literary/ecclesiastical strata kept; 15th-century supplements reported separately')),
        fresh_reserves=dict(Latin=dict(work='Dante, De vulgari eloquentia',urls=['https://www.thelatinlibrary.com/dante/vulgar.shtml','https://www.thelatinlibrary.com/dante/vulgar2.shtml']),
            Italian=dict(work='Dante, Paradiso',url='https://it.wikisource.org/wiki/Divina_Commedia/Paradiso'),
            Czech=dict(work='Podkoni a zak',url='https://czech.mml.ox.ac.uk/podkoni-zak'),
            Occitan=dict(work='Flamenca',catalogue='https://cl.indiana.edu/~mpmcguir/introduction.php',status='source body acquisition pending; do not substitute translation'),
            AbbreviatedLatin=dict(manuscript='Latin16195',repository='HTR-United/CREMMA-Medieval-LAT',commit=COMMIT)),
        prohibited=['all cut1 calibration/reserve text and parallel editions as new development','reserve body reads, unit counts, fitting, or scoring','synthetic alphabet completion, accent stripping, mark merging','source wrapping, cross-work stitching, shrinking only a candidate'],
        old_sources='Cut1 development may remain separately identified. No old source file, map, result, or policy is overwritten. New development is not activated for claim generation.',
        H3='UNRESOLVED',held_scoring=False,claim_freeze=False)
    dump(path,plan)
    dump(CUT/'SELECTION-SEAL.json',dict(sha256=sha(path),role='source selection only; no claim freeze'))
    tree=json.loads((CUT/'cremma-tree.metadata').read_bytes())
    reserved=[dict(path=x['path'],git_blob_sha1=x['sha'],bytes=x['size']) for x in tree['tree'] if x['type']=='blob' and x['path'].startswith('data/Latin16195/') and x['path'].endswith('.chocomufin.xml')]
    if not reserved:raise ValueError('fresh reserve identity absent')
    dump(CUT/'FRESH-RESERVE-LEDGER.json',dict(selection_sha256=sha(path),body_files_downloaded=0,bodies_parsed=0,held_scores_run=0,
        Latin16195=reserved,other_reserves=plan['fresh_reserves'],old_reserves='remain exposed diagnostics, permanently excluded from new fitting'))
    print('Registered development and fresh reserve roles before new body reads.')

def acquire():
    plan=json.loads((CUT/'SELECTION.json').read_text());assert sha(CUT/'SELECTION.json')==json.loads((CUT/'SELECTION-SEAL.json').read_text())['sha256']
    dest=CUT/'development';dest.mkdir(exist_ok=True);records=[];failures=[]
    def store(name,url):
        path=dest/name;path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():path.write_bytes(get(url))
        data=path.read_bytes();rev=re.search(rb'"wgRevisionId"\s*:\s*(\d+)',data)
        return dict(path=str(path.relative_to(CUT)).replace('\\','/'),url=url,sha256=sha(path),revision=int(rev[1]) if rev else None,partition='development')
    for i,url in enumerate(plan['development']['Latin']['urls'],1):
        try:records.append(store(f'latin/mon{i}.html',url))
        except Exception as e:failures.append(dict(source=url,error=str(e)))
    for lang in ('Czech','Occitan','Italian'):
        url=plan['development'][lang]['url']
        try:records.append(store(lang.lower()+'/index.html',url))
        except Exception as e:failures.append(dict(source=url,error=str(e)));continue
        soup=BeautifulSoup((dest/lang.lower()/'index.html').read_bytes(),'html.parser')
        if lang=='Italian':
            links=sorted({urllib.parse.urljoin(url,a['href']) for a in soup.select('a[href]') if re.fullmatch(r'/wiki/Divina_Commedia/Purgatorio/Canto_[IVXLCDM]+',urllib.parse.urlparse(urllib.parse.urljoin(url,a['href'])).path)})
            if len(links)!=33:failures.append(dict(source=url,error=f'expected33cantos found{len(links)}'));continue
            def one(u):return store('italian/'+u.rsplit('/',1)[1]+'.html',u)
            with ThreadPoolExecutor(max_workers=4) as pool:records+=list(pool.map(one,links))
        elif lang=='Occitan':
            print('JAUFRE LINKS',json.dumps([(a.get_text(' ',strip=True),urllib.parse.urljoin(url,a['href'])) for a in soup.select('a[href]') if any(x in a['href'].lower() for x in ('jauf','pdf','htm','doc'))],ensure_ascii=True)[:6000])
    tree=json.loads((CUT/'cremma-tree.metadata').read_bytes());dev=set(plan['development']['AbbreviatedLatin']['manuscripts'])
    paths=[x['path'] for x in tree['tree'] if x['type']=='blob' and x['path'].endswith('.chocomufin.xml') and x['path'].split('/')[1] in dev]
    def latin(path):return store('abbreviated-latin/'+path,'https://raw.githubusercontent.com/HTR-United/CREMMA-Medieval-LAT/'+COMMIT+'/'+path)
    with ThreadPoolExecutor(max_workers=4) as pool:records+=list(pool.map(latin,paths))
    dump(CUT/'ACQUISITION.json',dict(selection_sha256=sha(CUT/'SELECTION.json'),files=records,failures=failures,reserve_bodies_accessed=False))
    print(json.dumps(dict(files=len(records),failures=failures),ensure_ascii=True))

if __name__=='__main__':{'register':register,'acquire':acquire}[sys.argv[1]]()
