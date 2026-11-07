"""Build source-only Phase 10 receipts. Opens no corpus or target text files."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

registration = json.loads((ROOT / 'REGISTRATION.json').read_text(encoding='utf-8-sig'))
assert digest(ROOT / 'PROTOCOL.md') == registration['files']['PROTOCOL.md']
assert not (ROOT / 'SOURCE_FREEZE.json').exists(), 'Never overwrite a source freeze'

sources = {
    'RZ15': {'author':'René Zandbergen', 'url':'https://www.voynich.nu/q15/index.html', 'kind':'author research website', 'locator':'individual pharmaceutical folio Illustration(s) / Other information', 'retrieved':'2026-10-27'},
    'RZ19': {'author':'René Zandbergen', 'url':'https://www.voynich.nu/q19/index.html', 'kind':'author research website', 'locator':'individual pharmaceutical folio Illustration(s)', 'retrieved':'2026-10-27'},
    'RZ_OVERVIEW': {'author':'René Zandbergen', 'url':'https://www.voynich.nu/illustr.html', 'kind':'author research website', 'locator':'Pharmaceutical illustrations; example item 203 ↔ f37v', 'retrieved':'2026-10-27'},
    'N19': {'author':'Bernd; Jorge Stolfi', 'url':'https://www.voynich.ninja/thread-4067-page-19.html', 'kind':'dated public research discussion', 'locator':'Bernd 14–15 November 2025; Stolfi 16 November 2025 01:59 and 03:13', 'retrieved':'2026-10-27'},
    'N20': {'author':'Koen Gheuens; Jorge Stolfi; René Zandbergen', 'url':'https://www.voynich.ninja/archive/index.php/thread-4067-20.html', 'kind':'dated public research discussion', 'locator':'16–17 November 2025; especially Stolfi 17 November 17:16 correction', 'retrieved':'2026-10-27'},
    'N21': {'author':'Koen Gheuens', 'url':'https://www.voynich.ninja/archive/index.php/thread-4067-21.html', 'kind':'dated public research discussion', 'locator':'17 November 2025 17:28', 'retrieved':'2026-10-27'},
    'KNOWLES': {'author':'Mark Knowles', 'url':'https://www.voynich.ninja/archive/index.php/thread-4067.html', 'kind':'dated public research discussion', 'locator':'22 September 2023 opening post; linked Drive workbook is login-masked in public rendering', 'retrieved':'2026-10-27'},
    'KNOWLES2': {'author':'Mark Knowles and participants', 'url':'https://www.voynich.ninja/archive/index.php/thread-4067-2.html', 'kind':'dated public research discussion', 'locator':'22–23 September 2023; matches have varying strength and some false matches are acknowledged', 'retrieved':'2026-10-27'},
    'KARLOV': {'author':'Karlov', 'url':'https://www.voynich.ninja/thread-6044.html', 'kind':'dated public research proposal', 'locator':'27 August 2026 opening post; item-label and panel-level tests', 'retrieved':'2026-10-27'},
    'SDC': {'author':'Silvio de Carvalho', 'url':'https://silviodc.de/ai-projects/voynich/', 'kind':'author computational research website (self-reported; not independently reproduced)', 'locator':'27 September 2026; section 7, pharmaceutical/herbal comparison', 'retrieved':'2026-10-27'},
    'LABELS2023': {'author':'Mark Knowles and participants', 'url':'https://voynich.ninja/printthread.php?tid=4084', 'kind':'dated public research discussion', 'locator':'Small Plant Text Labels, 7 October 2023; search-result exposure only, not separately opened', 'retrieved':'2026-10-27'},
}

# page, Petersen item, row, column, herbal page, confidence, evidence locator
data = [
 ('f88r',11,3,2,'f90r2','tentative','RZ15'),
 ('f88r',8,2,3,'f15v','tentative','RZ15'),
 ('f88v',22,3,3,'f94v','tentative','RZ15'),
 ('f89r1',25,1,3,'f57r','tentative','RZ15'),
 ('f89r1',28,2,2,'f30r','tentative','RZ15'),
 ('f89r1',31,3,2,'f33r','tentative','RZ15'),
 ('f89r1',26,1,4,'f43v','tentative','RZ15'),
 ('f89r2',35,1,3,'f35v','tentative','RZ15'),
 ('f89r2',40,3,1,'f87v','tentative','RZ15'),
 ('f89v2',50,1,1,'f10v','tentative','RZ15'),
 ('f89v2',54,1,5,'f48v','confident','RZ15'),
 ('f89v2',56,2,2,'f24r','tentative','RZ15'),
 ('f89v2',61,3,4,'f48r','confident','RZ15'),
 ('f89v2',52,1,3,'f40v','tentative','RZ15'),
 ('f99r',80,3,1,'f51r','tentative','RZ19'),
 ('f99r',94,5,1,'f96v','tentative','RZ19'),
 ('f99v',95,1,1,'f44r','tentative','RZ19'),
 ('f99v',110,3,2,'f34v','tentative','RZ19'),
 ('f100r',116,1,2,'f96v','tentative','RZ19'),
 ('f100v',133,1,3,'f13v','tentative','RZ19'),
 ('f100v',136,2,2,'f90v2','tentative','RZ19'),
 ('f101r',150,2,2,'f30v','contested','RZ19'),
 ('f101r',150,2,2,'f55v','contested','RZ19'),
 ('f101r',155,3,2,'f49r','tentative','RZ19'),
 ('f101r',168,3,5,'f4v','tentative','RZ19'),
 ('f101v',188,1,7,'f37r','tentative','RZ19'),
 ('f102r1',203,3,1,'f37v','confident','RZ19'),
 ('f102r1',204,3,2,'f1v','confident','RZ19'),
 ('f102r2',205,1,1,'f47v','confident','RZ19'),
 ('f102r2',206,1,2,'f32v','confident','RZ19'),
 ('f102r2',209,2,3,'f53r','tentative','RZ19'),
 ('f102r2',212,3,1,'f18v','confident','RZ19'),
 ('f102r2',213,3,2,'f23r','confident','RZ19'),
 ('f102v2',225,2,5,'f36r','tentative','RZ19'),
 ('f102v1',240,2,2,'f19r','confident','RZ19'),
]
rows = []
for page,item,row,col,herbal,confidence,source in data:
    evidence = 'Source explicitly treats this as the same plant drawing.' if confidence == 'confident' else 'Source offers qualified or partial similarity only.'
    if confidence == 'contested':
        evidence = 'One pharmaceutical item has two unresolved alternative herbal destinations; excluded under the frozen competing-destination rule, not a claim of published disagreement.'
    if item in (8,26,40,52):
        evidence += ' Petersen comparison reported indirectly by Zandbergen; original marginal note not independently collated.'
    if item in (26,40):
        evidence += ' Website explicitly leaves this comparison needing further checking.'
    refs = [source]
    if confidence == 'confident' and item >=203:
        refs.append('N19')
    if item == 203:
        refs.append('RZ_OVERVIEW')
    if item in (54,61):
        refs.extend(['N20','N21'])
        evidence += ' The 17 November discussion initially confused herbal–herbal with herbal–pharma comparison; Stolfi explicitly withdrew that objection. Do not treat the withdrawn objection as unresolved pharma disagreement.'
    notes = ''
    if page == 'f101r':
        notes = 'Source page description says there are no plant labels on this page; picture match is not label availability.'
    if page.startswith('f102r'):
        notes = 'Source description reports few plant-fragment labels relative to items; adjacency/availability NOT established.'
    rows.append(dict(pair_id=f'P10-{len(rows)+1:03}', pharma_folio=page,petersen_item=item,row=row,column=col,
                     herbal_folio=herbal,confidence=confidence,source_ids=refs,
                     source_url=sources[source]['url'], source_locator=f'{page}, item {item} comparison to {herbal}',
                     confidence_reason=evidence,notes=notes,label='NOT LOADED',matched_words='NOT RUN',position='NOT LOADED',statistic='NOT RUN'))

unresolved = [
 {'source_id':'KNOWLES','scope':'roughly 108 proposed internal matches (includes other match types)','reason':'Public text does not expose the linked workbook or all item identities/ratings; not 108 confident pharma–herbal pairs. No hidden rows inferred.'},
 {'source_id':'N19','scope':'32 proposals rated at least 2 by more than one rater; 8 described as particularly unambiguous','reason':'Aggregate claims do not provide all item-level identities and confidence evidence; cannot pad primary set.'},
 {'source_id':'N19','scope':'f102r1 flat-top-root resemblance to herbal f95r2 and another herbal illustration','reason':'Author remains unconvinced and public text masks a herbal link; no precise pharmaceutical item independently resolved. Not admitted as a primary pair.'},
 {'source_id':'SDC','scope':'f99r illustrated hairy root / arrow-leaf fragment ↔ f96v, source calls high confidence','reason':'Attributable strong proposal, but no Petersen ID or row/column supplied in prose. Likely overlaps RZ19 item 94; not counted as another pair or used to promote it without image-only item disambiguation. Even treating it as one extra confident pair leaves at most 10, below 15.'},
 {'source_id':'SDC','scope':'11 reported image matches: 1 high, 6 medium, 4 low','reason':'Only one pair explicitly localized in inspected prose. Full item ledger not retrieved. Medium/low cannot become confident by aggregate count.'},
]
save('SOURCES.json',sources)
save('MATCHES.json',rows)
save('UNRESOLVED_SOURCES.json',unresolved)
with (ROOT / 'MATCHES.csv').open('w',encoding='utf-8',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader()
    for r in rows:
        writer.writerow({**r,'source_ids':';'.join(r['source_ids'])})

counts = dict(Counter(r['confidence'] for r in rows))
assert counts == {'tentative':24,'confident':9,'contested':2}, counts
assert len({(r['pharma_folio'],r['petersen_item'],r['herbal_folio']) for r in rows}) == len(rows)
assert counts['confident'] < 15
save('EXPOSURE_AND_RETRIEVAL.json',{
 'local_voynich_transcription_files_opened':False,'target_images_opened':False,
 'source_research_started_before_protocol_registration':True,
 'registration_timing':'Initial bibliography searches and prior protocol reads preceded registration; item-level collation, match-list freeze, control generation and scoring did not.',
 'incidental_web_exposure':True,
 'exposure_details':['Search snippets returned native-word examples and existing exact-match claims from unrelated repositories and research discussions.',
                     'Search results for historical source lists also returned label transcriptions and prior label/page comparisons.',
                     'The de Carvalho prior-work page includes native-word examples and reports previous negative textual results.'],
 'use_of_incidental_words':'Not copied into pair ledger, not used to select labels or picture matches, not scored. This is NOT an unexposed/blind investigator claim, and the literal no-Voynich-text-visible source condition was not fully achieved because of web snippets.',
 'limitations':['Linked Google workbook and some forum content masked behind login in public rendering; no attempt to bypass access controls.',
                'Direct shell web retrieval failed with DNS resolution error; public web-tool descriptions remained available.',
                'Not a census of every published picture proposal; nine is the verified admitted count under this audit.'],
 'no_calibration_dependencies_opened':True,
})
freeze_files=['PROTOCOL.md','REGISTRATION.json','SOURCES.json','MATCHES.json','MATCHES.csv','UNRESOLVED_SOURCES.json','EXPOSURE_AND_RETRIEVAL.json','freeze_sources.py']
save('SOURCE_FREEZE.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'status':'STOP_SOURCE_COUNT_BELOW_15',
 'counts':counts,'total_localized_candidates':len(rows),'required_confident':15,
 'count_scope':'Unique, item-localized published picture proposals verified in the cited sources; not all proposals in existence.',
 'files':{p:digest(ROOT / p) for p in freeze_files},'calibration':'NOT RUN','target_text':'CLOSED','target_statistics':'NOT RUN'})
save('STATUS.json',{'phase':10,'status':'STOP_SOURCE_COUNT_BELOW_15','confident_pairs':9,'tentative_pairs':24,'contested_pairs':2,
 'calibration':'NOT RUN — source gate failed','ZL':'NOT LOADED','LSI_H':'NOT LOADED','S1_S2_S3':'NOT RUN',
 'meaning_claim':False,'candidate_native_name_loci_established':False,'source_only_blinding':'LIMITED_BY_INCIDENTAL_WEB_SNIPPETS'})
print(json.dumps({'status':'STOP_SOURCE_COUNT_BELOW_15','counts':counts,'total':len(rows)}))
