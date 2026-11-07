"""Cut2 development-only ingestion and access. Never reads a reserve body or held statistic."""
from pathlib import Path
from collections import Counter
import json,re,unicodedata as U
from bs4 import BeautifulSoup
from core import sha,canonical_hash
from source_controls import plain_words,parse_alto,roman,recover_units
from transfer_policy import SourceSupportError
from source_contract import DevelopmentCorpus

ROOT=Path(__file__).resolve().parent
CUT=ROOT/'source-cut-2'
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=True,indent=2),encoding='utf-8')

def validate_selection(cut=CUT):
    plan=json.loads((cut/'SELECTION.json').read_text())
    if sha(cut/'SELECTION.json')!=json.loads((cut/'SELECTION-SEAL.json').read_text())['sha256']:raise SourceSupportError('selection changed')
    return plan

def load_cut2_development(language,partition='development',cut=CUT):
    if partition!='development':raise SourceSupportError('cut2 reserve and calibration bodies are locked')
    validate_selection(cut)
    seal=json.loads((cut/'DEVELOPMENT-SEAL.json').read_text())
    for name,digest in seal['files'].items():
        if sha(cut/name)!=digest:raise SourceSupportError('cut2 development input drift')
    data=json.loads((cut/'DEVELOPMENT-UNITS.json').read_text())
    selected=[u for u in data if u['language']==language and u.get('generation_eligible',True)]
    runs=[]
    for unit in selected:
        # Join only explicitly consecutive units of one work, never across manuscripts or a gap.
        if runs and runs[-1]['work']==unit['work'] and runs[-1]['last_order']+1==unit['order']:
            runs[-1]['tokens']+=unit['words'];runs[-1]['units'].append(unit['unit']);runs[-1]['last_order']=unit['order']
        else:runs.append(dict(work=unit['work'],units=[unit['unit']],tokens=list(unit['words']),last_order=unit['order']))
    frozen=tuple((r['work'],tuple(r['units']),tuple(r['tokens'])) for r in runs)
    return DevelopmentCorpus(language,frozen,canonical_hash(frozen))

def build():
    plan=validate_selection();acq=json.loads((CUT/'ACQUISITION.json').read_text())
    for item in acq['files']:
        assert item['partition']=='development' and sha(CUT/item['path'])==item['sha256']
    units=[];exclusions=[];raw=[]
    for i in range(1,4):
        path=CUT/f'development/latin/mon{i}.html';s=BeautifulSoup(path.read_bytes(),'html.parser');parts=[]
        for p in s.body.find_all('p'):
            if p.get('class') or p.find('a',href=re.compile(r'^(?!#).+')):continue
            for node in p.select('b'):node.decompose()
            text=p.get_text(' ',strip=True)
            if text:parts.append(text)
        units.append(dict(language='Latin',unit=f'Monarchia:book{i}',work='Dante:Monarchia',order=i,words=plain_words('\n'.join(parts)),source_sha256=sha(path),source_path=str(path.relative_to(CUT))))
    paths=sorted((CUT/'development/italian').glob('Canto_*.html'),key=lambda p:roman(p.stem[6:]))
    if len(paths)!=33:raise SourceSupportError('Purgatorio incomplete')
    for i,path in enumerate(paths,1):
        s=BeautifulSoup(path.read_bytes(),'html.parser');poems=s.select('.poem')
        if len(poems)!=1:raise SourceSupportError('ambiguous poem')
        for node in poems[0].select('.reference,.mw-ref,.noprint,.ws-noexport,.riferimento'):node.decompose()
        units.append(dict(language='Italian',work='Dante:Purgatorio',unit='Purgatorio:'+path.stem,order=i,words=plain_words(poems[0].get_text(' ',strip=True)),source_sha256=sha(path),source_path=str(path.relative_to(CUT))))
    if (CUT/'PETRARCH-ACQUISITION.json').exists():
        collection=json.loads((CUT/'PETRARCH-ACQUISITION.json').read_text())
        if len(collection['files'])!=366:raise SourceSupportError('independent Petrarch collection incomplete')
        for item in collection['files']:
            path=CUT/item['path'];assert sha(path)==item['sha256']
            s=BeautifulSoup(path.read_bytes(),'html.parser');poems=s.select('.poem')
            if not poems:
                poems=[p for p in s.select('.testi p') if p.find('br')]
            if len(poems)!=1:raise SourceSupportError(('ambiguous Petrarch poem',item['order'],len(poems)))
            for node in poems[0].select('.reference,.mw-ref,.noprint,.ws-noexport,.riferimento'):node.decompose()
            units.append(dict(language='Italian',work='Petrarch:Canzoniere',unit=f"Canzoniere:{item['order']}",order=item['order'],words=plain_words(poems[0].get_text(' ',strip=True)),source_sha256=sha(path),source_path=item['path'],generation_eligible=False))
    path=CUT/'development/czech/index.html';s=BeautifulSoup(path.read_bytes(),'html.parser');columns=s.select('.field--name-field-text-1')
    if len(columns)!=1:raise SourceSupportError('diplomatic Czech column ambiguous')
    column=columns[0]
    for n in column.select('em'):n.decompose() # modernized stage-direction labels explicitly editorial
    text=re.sub(r'\[\d+[ab]\]',' ',column.get_text(' ',strip=True));text=re.sub(r'\(\s*\)',' ',text)
    words=[]
    for match in re.finditer(r'\S+',text):
        token=match.group()
        if any(c in token for c in '<>[]?'):
            words.append(None);raw.append(dict(work='Mastickar',slot=len(words)-1,raw=token,reason='supplied_expansion_or_uncertainty',start=match.start(),end=match.end()))
        else:words.extend(plain_words(token))
    units.append(dict(language='Czech',work='Mastickar:Muzejni',unit='Mastickar:fragment',order=1,words=words,source_sha256=sha(path),source_path=str(path.relative_to(CUT)),generation_eligible=False))
    # A separately acquired authenticated Jaufre edition can register explicit line units here.
    if (CUT/'JAUFRE-LINES.json').exists():
        lines=json.loads((CUT/'JAUFRE-LINES.json').read_text())
        for i,line in enumerate(lines,1):units.append(dict(language='Occitan',work='Jaufre',unit=f'Jaufre:{i}',order=i,words=plain_words(line['text']),source_path=line['source_path'],source_sha256=line['source_sha256']))
    abbrev=[]
    for ms in plan['development']['AbbreviatedLatin']['manuscripts']:
        for path in sorted((CUT/'development/abbreviated-latin/data'/ms).glob('*.chocomufin.xml')):
            try:rows,drops=parse_alto(path,ms)
            except ValueError as error:
                if 'no explicit main text' not in str(error):raise
                exclusions.append(dict(manuscript=ms,page=path.name,reason='no_explicit_MainZone',source_sha256=sha(path)))
                continue
            abbrev+=rows;exclusions+=drops
    for row in abbrev:
        for slot in row['slots']:
            if slot['units'] is not None:
                assert recover_units(slot['units'])==slot['normalized']
                assert row['raw'][slot['start']:slot['end']]==slot['raw']
    dump(CUT/'DEVELOPMENT-UNITS.json',units);dump(CUT/'ABBREVIATED-LATIN-ROWS.json',abbrev)
    dump(CUT/'CZECH-BARRIERS.json',raw);dump(CUT/'ABBREVIATED-LATIN-EXCLUSIONS.json',exclusions)
    inventory={}
    for lang in ('Latin','Italian','Czech','Occitan'):
        uu=[u for u in units if u['language']==lang];counts=Counter(c for u in uu for w in u['words'] if w is not None for c in w)
        targets={'Latin':[],'Italian':['\u00e4','x'],'Czech':['w'],'Occitan':['\u00e7']}[lang]
        inventory[lang]=dict(units=len(uu),slots=sum(len(u['words']) for u in uu),known_gap_support={c:counts[c] for c in targets},uncovered=[c for c in targets if not counts[c]],inventory=dict(counts),
            known_gap_support_by_work={work:{c:sum(w.count(c) for u in uu if u['work']==work for w in u['words'] if w is not None) for c in targets} for work in sorted(set(u['work'] for u in uu))})
    counts=Counter(u for row in abbrev for s in row['slots'] if s['units'] is not None for u in s['units'])
    needed=[f'DIGIT:U+003{i}' for i in (0,1,2,3,4,6,7,8)]+['MARK:U+0301']
    inventory['AbbreviatedLatin']=dict(manuscripts=len(set(r['manuscript'] for r in abbrev)),pages=len(set((r['manuscript'],r['page']) for r in abbrev)),lines=len(abbrev),slots=sum(len(r['slots']) for r in abbrev),known_gap_support={u:counts[u] for u in needed},uncovered=[u for u in needed if not counts[u]],inventory=dict(counts))
    evidence=[]
    for row in abbrev:
        for si,s in enumerate(row['slots']):
            hit=sorted(set(s['units'] or [])&set(needed))
            if hit:evidence.append(dict(manuscript=row['manuscript'],page=row['page'],line=row['line'],slot=si,raw=s['raw'],start=s['start'],end=s['end'],units=hit,source_path=row['source_path'],source_sha256=row['source_sha256']))
    dump(CUT/'KNOWN-GAP-EVIDENCE.json',evidence);dump(CUT/'DEVELOPMENT-INVENTORY.json',inventory)
    files=['SELECTION.json','ACQUISITION.json','DEVELOPMENT-UNITS.json','ABBREVIATED-LATIN-ROWS.json','CZECH-BARRIERS.json']
    if (CUT/'JAUFRE-LINES.json').exists():files+=['JAUFRE-LINES.json','JAUFRE-PROVENANCE.json']
    if (CUT/'PETRARCH-ACQUISITION.json').exists():files+=['PETRARCH-ACQUISITION.json','ITALIAN-INDEPENDENCE-ADDENDUM.json']
    dump(CUT/'DEVELOPMENT-SEAL.json',dict(role='development input seal, NOT claim FREEZE',files={f:sha(CUT/f) for f in files},H3='UNRESOLVED',held_scoring=False))
    old=json.loads((ROOT/'CONTIGUOUS-SOURCE-SUPPORT.json').read_text())
    support=[]
    for r in old:
        if r['partition']=='development' and r['status']=='SOURCE_TOO_SHORT':
            corpus=load_cut2_development(r['language']);n=max([len(tokens) for _,_,tokens in corpus.runs] or [0]);budget=r['required_original_slots']
            support.append(dict(language=r['language'],cell=r['cell'],required_slots=budget,new_longest_run=n,status='SUPPORTED_AT_SIZE' if n>=budget else 'SOURCE_TOO_SHORT',scope=plan['development'][r['language']]['scope']))
    dump(CUT/'SEVEN-SHORT-SOURCE-CASES.json',support)
    print(json.dumps(dict(inventories={k:{x:v[x] for x in v if x!='inventory'} for k,v in inventory.items()},seven_cases=support),ensure_ascii=True))

if __name__=='__main__':build()
