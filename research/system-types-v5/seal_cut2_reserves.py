"""Acquire opaque reserve bytes only. No text/XML/HTML parsing, unit counting or fitting."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,urllib.parse
from source_cut_probe import get
from source_cut2 import CUT,dump,validate_selection
from core import sha

def roman(n):
    out=''
    for v,c in ((10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')):
        while n>=v:out+=c;n-=v
    return out

def main():
    validate_selection();path=CUT/'RESERVE-ACQUISITION-PLAN.json'
    if not path.exists():
        files=[]
        for i,u in enumerate(['https://www.thelatinlibrary.com/dante/vulgar.shtml','https://www.thelatinlibrary.com/dante/vulgar2.shtml'],1):files.append(dict(path=f'Latin/vulgar{i}.html',url=u))
        for i in range(1,34):files.append(dict(path=f'Italian/Canto_{roman(i)}.html',url='https://it.wikisource.org/wiki/Divina_Commedia/Paradiso/Canto_'+roman(i)))
        files.append(dict(path='Czech/Podkoni-a-zak.html',url='https://czech.mml.ox.ac.uk/podkoni-zak'))
        sources=[('cremma-tree.metadata','data/Latin16195/','AbbreviatedLatin','HTR-United/CREMMA-Medieval-LAT','292525969ad98380b398e6606a9c2a36d51913ae','.chocomufin.xml'),
                 ('LostMa-ERC-gatmuza-tree.json','Carcassonne_bm_34_flamenca/','Occitan','LostMa-ERC/gatmuza','e5f6397ce18b4ff68103ba7088d31ad4d99bade1','.xml')]
        for treefile,prefix,language,repo,commit,suffix in sources:
            tree=json.loads((CUT/treefile).read_bytes())
            for entry in tree['tree']:
                name=entry['path']
                if entry['type']=='blob' and name.startswith(prefix) and name.endswith(suffix) and not name.endswith('METS.xml'):
                    files.append(dict(path=language+'/'+name.rsplit('/',1)[1],url='https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+urllib.parse.quote(name),git_blob_sha1=entry['sha']))
        dump(path,dict(selection_sha256=sha(CUT/'SELECTION.json'),purpose='Opaque fresh reserve byte acquisition only; no body parsing, coverage counts, source-size adaptations or held scores.',
            Occitan_route='Flamenca work retained;10page manuscript GT rather than blocked Indiana edition. Native-page reserve, not asserted full-manuscript-size source.',
            files=files))
    plan=json.loads(path.read_text());dest=CUT/'fresh-reserves';dest.mkdir(exist_ok=True)
    def one(item):
        target=dest/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
        try:
            if not target.exists():target.write_bytes(get(item['url']))
            b=target.read_bytes()
            if 'git_blob_sha1' in item:
                assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==item['git_blob_sha1']
            return dict(**item,sha256=hashlib.sha256(b).hexdigest(),status='OPAQUE_BYTES_SEALED',partition='reserve')
        except Exception as e:return dict(**item,status='ACQUISITION_FAILED',error=str(e))
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(one,plan['files']))
    dump(CUT/'FRESH-RESERVE-SEAL.json',dict(plan_sha256=sha(path),files=records,bodies_parsed=0,coverage_counts_computed=False,held_scores_run=0,
        read_authority='Byte hashing only in this stage. No other source-cut2 module opens this directory. Access for transfer qualification requires a later explicit protocol decision.'))
    ledger=json.loads((CUT/'FRESH-RESERVE-LEDGER.json').read_text());ledger.update(body_files_downloaded=sum(r['status']=='OPAQUE_BYTES_SEALED' for r in records),bodies_parsed=0,reserve_seal_sha256=sha(CUT/'FRESH-RESERVE-SEAL.json'))
    dump(CUT/'FRESH-RESERVE-LEDGER.json',ledger)
    print(json.dumps(dict(opaque_files_sealed=ledger['body_files_downloaded'],failures=[r for r in records if r['status']=='ACQUISITION_FAILED'],bodies_parsed=0,held_scored=False)))

if __name__=='__main__':main()
