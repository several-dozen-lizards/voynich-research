"""Real-source ingestion and representation controls. Does not import held statistics."""
from pathlib import Path
from collections import Counter
import json,re,sys,unicodedata as U,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from core import save,sha,canonical_hash,group_rank_mapping,render_groups

ROOT=Path(__file__).resolve().parent
ABBREVIATION_SIGNS=frozenset('⁊ꝑꝓꝙꝗꝯꝰꝭꝵꝝꝜẜħł≈÷\uf1ac')

def plain_words(text):
    """NFC letters/combining marks, no accent stripping, no modern-language rewriting."""
    out=[];current=''
    for c in U.normalize('NFC',text).lower():
        if U.category(c)[0] in ('L','M'):current+=c
        elif current:out.append(current);current=''
    if current:out.append(current)
    return out

def diplomatic_slots(text):
    """Keep every written mark; no abbreviation expansion or silent unknown removal."""
    slots=[]
    for match in re.finditer(r'\S+',text):
        raw=match.group()
        # Damage/uncertainty and a line-final hyphenated piece remain a barrier.
        if any(c in raw for c in '[]{}?*�') or raw.endswith(('-', '¬')):
            slots.append(dict(raw=raw,start=match.start(),end=match.end(),units=None,reason='uncertain_or_split_word'))
            continue
        segment='';offset=match.start()
        def append_segment(s,at):
            nfd=U.normalize('NFD',s.lower())
            units=[f'MARK:U+{ord(c):04X}' if U.category(c)[0]=='M' else f'SIGN:U+{ord(c):04X}' if c in ABBREVIATION_SIGNS else f'DIGIT:U+{ord(c):04X}' if c.isdigit() else c for c in nfd]
            slots.append(dict(raw=s,start=at,end=at+len(s),units=units,normalized=nfd,
                              explicit_mark=any(u.startswith(('MARK:','SIGN:')) for u in units)))
        for index,c in enumerate(raw):
            if U.category(c)[0] in ('L','M','N') or c in ABBREVIATION_SIGNS:
                if not segment:offset=match.start()+index
                segment+=c
            else:
                if segment:append_segment(segment,offset);segment=''
        if segment:append_segment(segment,offset)
    return slots

def recover_units(units):
    return ''.join(chr(int(u.rsplit('+',1)[1],16)) if u.startswith(('MARK:','SIGN:','DIGIT:')) else u for u in units)

def parse_alto(path,manuscript):
    root=ET.parse(path).getroot();local=lambda e:e.tag.rsplit('}',1)[-1]
    if local(root)!='alto':raise ValueError('expected ALTO source, never infer format')
    tags={e.attrib['ID']:e.attrib.get('LABEL') for e in root.iter() if local(e)=='OtherTag'}
    rows=[];excluded=[]
    for block in (e for e in root.iter() if local(e)=='TextBlock'):
        labels=[tags.get(t,'?') for t in block.attrib.get('TAGREFS','').split()]
        if 'MainZone' not in labels:
            excluded.append(dict(block=block.attrib.get('ID'),labels=labels,reason='not_explicit_MainZone'));continue
        for line in (e for e in block if local(e)=='TextLine'):
            parts=[]
            for child in line:
                if local(child)=='String':parts.append(child.attrib.get('CONTENT',''))
                elif local(child)=='SP':parts.append(' ')
            raw=''.join(parts)
            if not raw.strip():continue
            rows.append(dict(manuscript=manuscript,page=path.name.replace('.chocomufin.xml',''),block=block.attrib.get('ID'),line=line.attrib.get('ID'),
                             raw=raw,slots=diplomatic_slots(raw),source_path=str(path.relative_to(ROOT)),source_sha256=sha(path)))
    if not rows:raise ValueError(('no explicit main text',path))
    return rows,excluded

def roman(s):
    values={'I':1,'V':5,'X':10,'L':50,'C':100};total=0;prior=0
    for c in reversed(s):
        n=values[c];total+=-n if n<prior else n;prior=max(prior,n)
    return total

def other_sources():
    records={}
    # Native units are whole cantos, not flattened page headers/notes.
    italian=[]
    paths=sorted((ROOT/'SOURCES/italian-dante').glob('Canto_*.html'),key=lambda p:roman(p.stem[6:]))
    for path in paths:
        soup=BeautifulSoup(path.read_bytes(),'html.parser')
        poems=soup.select('.poem')
        if len(poems)!=1:raise ValueError(('expected one poem',path))
        poem=poems[0]
        for node in poem.select('.reference,.mw-ref,.noprint,.ws-noexport,.riferimento'):node.decompose()
        words=plain_words(poem.get_text(' ',strip=True))
        italian.append(dict(unit=path.stem,words=words,source_sha256=sha(path)))
    records['Italian']=dict(kind='medieval literary verse; edited; not medical',units=italian,source_manifest='SOURCES/italian-dante/MANIFEST.json')
    soup=BeautifulSoup((ROOT/'SOURCES/old-czech-dalimil/source.html').read_bytes(),'html.parser')
    columns=soup.select('.field--name-field-text-2')
    if not columns:raise ValueError('Old Czech transliterated column not found')
    czech=[]
    for index,column in enumerate(columns):
        for heading in column.select('strong'):heading.decompose()
        text=re.sub(r'\[f\.[^]]*\]',' ',column.get_text(' ',strip=True))
        text=re.sub(r'<[^>]*>',' ',text)
        words=plain_words(text)
        czech.append(dict(unit=f'parallel-section-{index}',words=words))
    records['Czech']=dict(kind='Old Czech critical transliteration; chronicle; not medical',units=czech,source_manifest='SOURCES/old-czech-dalimil/MANIFEST.json',redistribution='internal research only; no open license established')
    # Use FORM once per integer token. MWT wrapper rows and empty nodes are not words.
    occitan=[];excluded=Counter();seen=set()
    for path in sorted((ROOT/'SOURCES/old-occitan-corag').glob('*.conllu')):
        for sentence in path.read_text(encoding='utf-8').strip().split('\n\n'):
            sid=next((line[12:] for line in sentence.splitlines() if line.startswith('# sent_id = ')),None)
            if sid is None:raise ValueError('missing sentence identity')
            if sid in seen:raise ValueError(('duplicate sentence',sid))
            seen.add(sid)
            if sid.startswith('1564_'):excluded['1564_source_sentences']+=1;continue
            words=[]
            for line in sentence.splitlines():
                cols=line.split('\t')
                if len(cols)==10 and cols[0].isdigit():words.extend(plain_words(cols[1]))
            occitan.append(dict(unit=sid,document=sid.rsplit('_',5)[0],words=words))
    records['Occitan']=dict(kind='Old Gascon legal editions; medieval texts only; not medical',units=occitan,excluded=dict(excluded),source_manifest='SOURCES/old-occitan-corag/MANIFEST.json')
    old=json.loads((ROOT/'development-history/source-controls-start/SOURCE-INVENTORY.json').read_text())
    germanpath=Path(old['German']['path'])
    check=sha(germanpath)
    if check!=old['German']['sha256']:raise ValueError('German source changed')
    document=ET.parse(germanpath);books=[]
    for i,book in enumerate(b for b in document.iter('div') if b.get('type')=='book'):
        words=[w for seg in book.iter('seg') for w in plain_words(''.join(seg.itertext()))]
        books.append(dict(unit=book.get('id',str(i)),words=words))
    if not books:raise ValueError('German book units absent')
    records['German']=dict(kind='Bible, pre-existing conventional control; period/version not authenticated; not medieval medical evidence',units=books,source_sha256=check,source_path=str(germanpath),better_period_source_attempt='TITUS Buch der Natur fetch failed TLS issuer verification; certificate checking was not disabled')
    latin=json.loads((ROOT/'SOURCES/macer-floridus/words.json').read_text())
    records['Latin']=dict(kind='edited Macer herbal verse',units=[dict(unit=f'chapter-{i+1}',words=s) for i,s in enumerate(latin['segments'])],source_manifest='SOURCES/macer-floridus/MANIFEST.json')
    return records

def plan():
    path=ROOT/'SOURCE-CONTROL-PLAN.json'
    if path.exists():raise FileExistsError(path)
    files=[ROOT/'source_controls.py',ROOT/'SOURCE-CONTROL-SELECTION.json',ROOT/'core.py']
    files += [p for name in ['cremma-lat','old-occitan-corag','italian-dante','old-czech-dalimil','macer-floridus'] for p in (ROOT/'SOURCES'/name).rglob('*') if p.is_file()]
    save(path,dict(tier='sandbox',held_scoring=False,H3='UNRESOLVED',
        representation='Unicode NFD marks/signs separate; raw lexical spans and coordinates retained; no abbreviation expansion; uncertain/split word remains None',
        real_control='all Phi_10a135 manuscript pages reserved from rule fitting; two earlier medical codices development; PalLat373 chronology/genre sensitivity',
        tests='Raw span roundtrip; all explicit marks retained; unique locus; same-map repeatability; ten panel capacity checks and development-map transfer checks with all unknowns/errors retained',
        language_controls='Five languages; explicit genre/period/source provenance; source lengths and disjoint source-unit partitions; no source padding/repetition to claim adequate manuscript size',
        gates=json.loads((ROOT/'SOURCE-CONTROL-SELECTION.json').read_text())['source_preflight_gates'],
        files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print('Source-control plan sealed; no claim FREEZE created.')

def run():
    assert not (ROOT/'FREEZE.json').exists()
    plan=json.loads((ROOT/'SOURCE-CONTROL-PLAN.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in plan['files'].items()),'source/control code changed after plan'
    selection=json.loads((ROOT/'SOURCE-CONTROL-SELECTION.json').read_text())
    rows=[];drops=[];summary=[]
    for manuscript in selection['latin_manuscripts']:
        for path in sorted((ROOT/'SOURCES/cremma-lat/data'/manuscript).glob('*.chocomufin.xml')):
            rr,dd=parse_alto(path,manuscript);rows+=rr;drops.extend(dict(manuscript=manuscript,page=path.stem,**d) for d in dd)
    assert len({(r['manuscript'],r['page'],r['block'],r['line']) for r in rows})==len(rows)
    for row in rows:
        for slot in row['slots']:
            if slot['units'] is not None:
                assert recover_units(slot['units'])==slot['normalized']
                assert row['raw'][slot['start']:slot['end']]==slot['raw']
    for manuscript in selection['latin_manuscripts']:
        rr=[r for r in rows if r['manuscript']==manuscript];ss=[s for r in rr for s in r['slots'] if s['units'] is not None]
        marked=sum(s['explicit_mark'] for s in ss)
        summary.append(dict(manuscript=manuscript,pages=len(set(r['page'] for r in rr)),lines=len(rr),readable_words=len(ss),unknown_slots=sum(s['units'] is None for r in rr for s in r['slots']),explicit_marked_words=marked,marked_word_share=marked/len(ss),mark_inventory=dict(Counter(u for s in ss for u in s['units'] if u.startswith(('MARK:','SIGN:'))))))
    primary=next(s for s in summary if s['manuscript']=='Phi_10a135')
    gates=plan['gates'];admitted=primary['readable_words']>=gates['minimum_reserve_readable_words'] and primary['lines']>=gates['minimum_reserve_lines'] and primary['explicit_marked_words']>=gates['minimum_marked_words']
    inventories=json.loads((ROOT/'EVA-GROUP-INVENTORIES.json').read_text())
    primary_words=[s['units'] for r in rows if r['manuscript']=='Phi_10a135' for s in r['slots'] if s['units'] is not None]
    dev_words=[s['units'] for r in rows if r['manuscript'] in selection['Latin_development'] for s in r['slots'] if s['units'] is not None]
    mapping=[]
    for cell,inventory in inventories.items():
        for view,words in [('primary-representation',primary_words),('development-map-transfer',dev_words)]:
            try:
                receipt=group_rank_mapping(words,inventory)
                if view=='primary-representation':rendered=render_groups(primary_words,receipt);unknown=[]
                else:
                    unknown=sorted({u for w in primary_words for u in w if u not in receipt['mapping']})
                    known=[w for w in primary_words if all(u in receipt['mapping'] for u in w)]
                    rendered=render_groups(known,receipt)
                mapping.append(dict(cell=cell,view=view,status='PASS' if not unknown else 'UNSEEN_UNITS_ABSTAIN',unknown_units=unknown,readable_words_mapped=len(rendered['words']),receipt=receipt))
            except ValueError as error:mapping.append(dict(cell=cell,view=view,status='CAPACITY_ABSTAIN',reason=str(error)))
    save(ROOT/'REAL-LATIN-ROWS.json',rows);save(ROOT/'REAL-LATIN-EXCLUSIONS.json',drops)
    save(ROOT/'REAL-LATIN-MAPPING.json',mapping)
    sources=other_sources();inventory={};splits={}
    for language,record in sources.items():
        units=record.pop('units');total=sum(len(u['words']) for u in units)
        # Entire natural source units; no random word split or duplicate source unit.
        n=len(units);a=max(1,int(n*.6));b=max(a+1,int(n*.8))
        parts=dict(development=units[:a],calibration=units[a:b],reserve=units[b:])
        if not parts['reserve']:parts=dict(development=units[:-1],calibration=[],reserve=units[-1:])
        splits[language]={k:dict(units=[u['unit'] for u in v],words=sum(len(u['words']) for u in v),sha256=canonical_hash(v)) for k,v in parts.items()}
        inventory[language]=dict(**record,words=total,source_units=n,word_policy='NFC Unicode letters retained; punctuation separates words; no accent stripping; no modern-language rewriting',status='LANGUAGE_SOURCE_AVAILABLE',manuscript_size_adequacy='not assumed; must compare source-part word counts with each claim geometry')
        save(ROOT/(language.upper()+'-SOURCE-UNITS.json'),units)
    save(ROOT/'SOURCE-INVENTORY.json',inventory);save(ROOT/'LANGUAGE-SOURCE-SPLITS.json',splits)
    result=dict(status='REAL_ABBREVIATED_LATIN_INGESTION_PASS' if admitted else 'REAL_LATIN_INSUFFICIENT_SUPPORT',
        manuscripts=summary,primary_control=primary,primary_support_gate=admitted,
        heavily_abbreviated=primary['marked_word_share']>=gates['minimum_marked_word_share_for_heavily_abbreviated_label'],
        raw_unit_roundtrips=True,abbreviations_expanded=False,main_text_only=True,all_excluded_blocks_retained=True,
        source_rule_fitting_on_primary=False,language_sources=list(inventory),
        representation_mapping_passes=sum(x['status']=='PASS' for x in mapping if x['view']=='primary-representation'),
        development_map_transfer_statuses=dict(Counter(x['status'] for x in mapping if x['view']=='development-map-transfer')),
        semantic_expansions_inferred=False,H3='UNRESOLVED',held_scoring=False,claim_control_survival='NOT_RUN',
        source_plan_sha256=sha(ROOT/'SOURCE-CONTROL-PLAN.json'),
        limitations=['Graphematic conventions already normalize some glyph variants; not facsimile-level glyph identity.','Marked-word share is an explicit-sign lower bound, not a count of all historical abbreviations.','Combining letters can also encode interlinear additions; mark labels are representational, not automatic semantic classifications.','Real G2 survival and all model discrimination remain unrun until claim freeze.'])
    save(ROOT/'SOURCE-CONTROL-RESULTS.json',result)
    print(json.dumps({k:result[k] for k in ('status','primary_control','heavily_abbreviated','language_sources','representation_mapping_passes','development_map_transfer_statuses','H3','held_scoring')}))

if __name__=='__main__':{'plan':plan,'run':run}[sys.argv[1]]()
