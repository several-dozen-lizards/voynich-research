"""Produce a dated source audit, not a scoring lexicon or calibration result."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, unicodedata

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'phase9_month_annotations_v1'
PRIMARY=['Latin','Italian','German','Occitan','Catalan']
LANGS=PRIMARY+['French']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):
 s=unicodedata.normalize('NFD',s)
 s=''.join(c for c in s.lower() if unicodedata.category(c)!='Mn' and c.isalpha())
 return s.replace('w','uu').replace('j','i').replace('k','c').replace('ß','ss')

assert not (ROOT/'SOURCE_AUDIT_SNAPSHOT.json').exists(),'Do not overwrite an audit snapshot'
rows=[]
def add(lang,month,form,date,region,variety,url,locator,status='DATED_FORM_VERIFIED',kind='scholarly historical quotation',notes='',source_file=None):
 rows.append(dict(id=f'V{len(rows)+1:04}',language=lang,primary=lang in PRIMARY,month=month,
  form=form,normalized=norm(form),date=date,region=region,variety=variety,url=url,
  locator=locator,status=status,evidence_kind=kind,notes=notes,source_file=source_file))

# Preserve every old lexeme as a candidate; Phase 9 admission does not imply 9b admission.
for r in load(PRIOR/'PERIOD_NAMES.json'):
 lang=r['language'];date=None;region='UNKNOWN';variety='UNKNOWN'
 status='PENDING_DATED_WITNESS';notes='Prior Phase 9 candidate; no automatic promotion to the narrower period/variety source freeze.'
 if lang=='Latin':
  date=[1420,1430];region='Brittany, France (liturgical use); production provenance unknown';variety='late medieval liturgical Latin'
  status='DATED_FORM_VERIFIED';notes='Scholarly catalogue transcription, not a new facsimile reading. Calendar for Rennes use.'
 if lang=='Italian':
  date=[1495,1495];region='Venice, Italy (printing place)';variety='Italian, printed Venetian witness; precise linguistic variety not established'
  status='DATED_FORM_VERIFIED';notes='Previously visually collated printed heading retained with exact spelling; not an all-Italian-varieties sample.'
 add(lang,r['month'],r['form'],date,region,variety,r['url'],r['locator'],status,
     'prior source collation, provenance retained',notes,str((PRIOR/r['saved_source']).relative_to(ROOT.parent)))

# Exact headings newly read in the dated BSB witness. Handwritten later glosses excluded.
for month,form,page in [(3,'Mertz',11),(4,'April',13),(5,'Mai',15),(6,'Brachmonde',17),(7,'Hewmonde',19),(8,'Augstmonde',21),(9,'Herbstmonde',23),(10,'Weinmonde',25),(11,'Wintermonde',27),(12,'Cristmonde',29)]:
 add('German',month,form,[1474,1474],'Nuremberg, Germany (printing place)',
     'Early New High German, Nuremberg printed witness; local dialect attribution not asserted',
     f'https://www.digitale-sammlungen.de/en/view/bsb00031080?page={page}',
     f'BSB 4 Inc.s.a. 1551 r / BSB-Ink R-78; scan {page}, printed month heading',
     kind='direct facsimile reading',notes='Long s transcribed s. The later marginal Latin month gloss is not part of this attestation.',
     source_file=f'sources/german1474_images/page_{page:02}.jpg')

olivier='https://api.pageplace.de/preview/DT0400.9783484971325_A16036970/preview-9783484971325_A16036970.pdf'
oc=[(4,'abril',1379,'CConsSFlour 2, 10r; printed p6'),
    (4,'abrial',1379,'CConsSFlour 2, 11v; printed p6'),
    (4,'april',1379,'CConsSFlour 2, 33r; printed p6'),
    (4,'abriel',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (5,'may',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (6,'juign',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (7,'julhet',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (8,'aoust',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (9,'septembre',1430,'CConsSFlour 41, 38v; printed pp6–7'),
    (3,'mars',1459,'LRecAuterocheCouzans 7v and 11r; printed p7'),
    (4,'aprial',1459,'LRecAuterocheCouzans 7v; printed p7'),
    (6,'jun',1459,'LRecAuterocheCouzans 7v and 11r; printed p7'),
    (7,'juliet',1459,'LRecAuterocheCouzans 7v and 11r; printed p7'),
    (8,'aussotz',1459,'LRecAuterocheCouzans 7v; printed p7'),
    (8,'ausohtz',1459,'LRecAuterocheCouzans 11r; printed p7'),
    (9,'setembre',1459,'LRecAuterocheCouzans 11r; printed p7'),
    (10,'octobre',1459,'LRecAuterocheCouzans 11r; printed p7'),
    (11,'novembre',1459,'LRecAuterocheCouzans 11r; printed p7'),
    (12,'desembre',1459,'LRecAuterocheCouzans 11r; printed p7')]
for month,form,date,loc in oc:
 region='Saint-Flour, Haute-Auvergne, France' if date!=1459 else 'Auteroche/Couzans, Vebret, Haute-Auvergne, France'
 add('Occitan',month,form,[date,date],region,'Old Auvergnat (Mauriacois/Sanflorain source area)',olivier,
     'Philippe Olivier (2009), entry abril; '+loc,kind='scholarly transcription visually checked in publisher preview',
     notes='Quotation spellings, not normalized headwords. 1459 calends/weather sequence uses month names metonymically. Original manuscripts not re-collated.',
     source_file='sources/olivier2009_preview.pdf')

# DCVB date-bearing documentary examples; dialect phonetics elsewhere are not historical spellings.
cat=[(5,'Maig',1381,'maig','month sense; Col. Bof. xl, 207'),
     (6,'Juny',1373,'comptar','II, documentary quotation; Miret Templers 555'),
     (7,'juyol',1358,'juliol','Var. ant.; Clavari, municipal archive of Barcelona'),
     (12,'decembre',1392,'desembre','documentary quotation; Boll. Lul. viii, 55'),
     (9,'setembre',1351,'mes','month sense; Rubió Docs. cult. ii, 94'),
     (10,'octobre',1351,'mes','same documentary quotation; Rubió Docs. cult. ii, 94'),
     (6,'iuny',1470,'verema','month-bearing documentary quotation; BABL xi, 280'),
     (7,'iuliol',1470,'verema','same documentary quotation; BABL xi, 280'),
     (10,'octubre',1470,'verema','same documentary quotation; BABL xi, 280')]
for month,form,date,entry,loc in cat:
 region='Barcelona, Catalonia (archive cited)' if form=='juyol' else 'UNKNOWN — source citation does not establish document place'
 # Date/form verified, but regional attribution remains unfinished for most quotations.
 add('Catalan',month,form,[date,date],region,
     'Catalan documentary spelling; regional variety UNKNOWN',
     f'https://dcvb.iec.cat/results.asp?word={entry}',f'DCVB {entry}; {loc}',
     status='DATED_FORM_REGION_PENDING' if form!='juyol' else 'DATED_FORM_VERIFIED',
     notes='Exact historical quotation, not the modern lemma or pronunciation. DCVB edition date is not the witness date.',
     source_file=f'sources/cat_{entry}.html')

# Other spellings encountered in the selected month entries, retained without invented dates.
cat_candidates={3:['març'],4:['abril','bril'],5:['mag','may','mai','matx'],6:['juyn'],7:['juliol','joliol','juriol'],8:['agost','gost'],9:['septembre'],10:['vuitubre'],11:['novembre','noembre','nohembre'],12:['desembre','dehembre']}
for month,forms in cat_candidates.items():
 for form in forms:
  add('Catalan',month,form,None,'UNKNOWN','UNKNOWN',
      'https://dcvb.iec.cat/',f'DCVB month {month} entry and variant/citation apparatus',
      status='PENDING_DATED_WITNESS',notes='Early text, modern dialect form or unlocalized edited citation; exact in-window spelling witness not established in this audit.')

# Bibliographic leads with transcriptions but masked witness identities are not admitted forms.
for lang,place,date,forms in [
 ('Occitan','Montpellier, Provençal as claimed by contributor',[1453,1500],['Martz','Abrill','May','Iun','Iull','Aost','Setembre','Octembre','Nouembre','Decembre']),
 ('French','Bourges',[1375,1375],['Mars','Auril','May','Iuing','Iuignet','Aoust','Septembre','Octembre','Nouembre','Decembre']),
 ('French','Metz',[1457,1457],['Mars','Auri','May','Jung','Jungnet','Auost','Septembre','Octembre','Nouembre','Decembre'])]:
 for month,form in enumerate(forms,3):
  add(lang,month,form,date,place,'Contributor attribution; independently unverified',
      'https://www.voynich.ninja/printthread.php?page=14&tid=4751',
      f'davidma, 17 February 2026, listed calendar from {place}',status='PENDING_IDENTIFIED_WITNESS',
      notes='Public rendering masks source link. No catalogue identifier or primary scan verified; not a scored period variant.',source_file='sources/month_collection14.html')

save('CANDIDATES.json',rows)
with (ROOT/'CANDIDATES.csv').open('w',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
counts={}
supported={'DATED_FORM_VERIFIED','DATED_FORM_REGION_PENDING'}
for lang in LANGS:
 rs=[r for r in rows if r['language']==lang]
 dated=[r for r in rs if r['status'] in supported]
 keys={(r['month'],r['normalized']) for r in dated}
 months=sorted({m for m,v in keys})
 counts[lang]={'candidate_records':len(rs),'dated_form_records':len(dated),'distinct_dated_normalized_variants':len(keys),
  'dated_month_coverage':len(months),'missing_months':[m for m in range(3,13) if m not in months],
  'date_supported_counts_by_month':{str(m):len({v for mm,v in keys if mm==m}) for m in range(3,13)},
  'regional_or_variety_gaps':sum(r['status']=='DATED_FORM_REGION_PENDING' for r in dated),
  'scoring_admission':'CLOSED — census incomplete'}
save('COUNTS.json',counts)
save('SOURCE_FRAME.json',{
 'user_clarification':'Use a bounded, cited source census',
 'scope':'Work in progress: cited forms in the selected month headings/entries and their month-bearing documentary quotations, not a universal regional census.',
 'reviewed':['Phase 9 forty-form provenance ledger and cited local source evidence','Brandeis/Rennes calendar month headings, c1420–1430','Crescentio 1495 Book XII monthly headings (prior collation)','BSB bsb00031080 printed March–December headings, 1474','Olivier 2009 entry abril, printed pp6–7 with dated month sequences; relevant source sigla','DCVB ten month entries, plus mes, comptar and verema month-bearing quotations','Month-name collection discussion page 14, leads only'],
 'not_complete':['All date-supported variants in every selected dictionary entry have not yet been independently localized to regional witnesses.','Catalan March, April, August and November lack a qualified dated form in the current admitted evidence.','The separate French witness set is not yet qualified.','The full range of regional varieties is not represented.'],
 'retrieval_issues':['Google Books 1513 Catalan almanac search returns OCR hits, but requested PP28 scan is an image-not-available placeholder; no OCR reconstruction admitted.','BnF 1493 French calendar manifest blocked by Cloudflare after a read-only retry.','Direct Python retrieval of Grotefend failed TLS certificate-chain validation; existing snapshots and web tool remained available; validation not disabled.','LOC public JSON request returned HTTP 403.'],
 'no_calibration_or_target_scoring':True})
save('RUN_STATE.json',{'status':'SOURCE_CENSUS_INCOMPLETE','variant_scoring_freeze':'NOT READY','calibration':'NOT RUN',
 'annotation_target_fit':'CLOSED','native_tracks':'CLOSED','winner':None,'contrast_p':None,'LOMO':'NOT RUN','equalization':'NOT RUN',
 'inseparability_conclusion':'NOT ESTABLISHED — no synthetic confusion bank has run'})
files=['PROTOCOL.md','EQUIVALENCES.json','DESIGN_REGISTRATION.json','PHASE9_PRESERVATION_BEFORE.json','SOURCE_FRAME.json','CANDIDATES.json','CANDIDATES.csv','COUNTS.json','RUN_STATE.json','build_source_audit.py','SOURCE_RETRIEVAL.json']
save('SOURCE_AUDIT_SNAPSHOT.json',{'status':'IMMUTABLE_INCOMPLETE_AUDIT_SNAPSHOT_NOT_SCORING_ADMISSION','files':{p:sha(ROOT/p) for p in files},
 'source_files':{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'sources').rglob('*') if p.is_file()},'counts':counts})
print(json.dumps(counts,ensure_ascii=True))
