import json, hashlib, html, re
from pathlib import Path
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
ATLAS=ROOT/'frequency-atlas-v48/rows.json'
EVT=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources={
 'bax':{'url':'https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf','type':'Original decipherment proposal, 2014; botanical claims partly inherited','independence':'Not a blind botanical reference set'},
 'stolfi':{'url':'https://www.ic.unicamp.br/~stolfi/voynich/Notes/061/work/Notes/040/html/f2v.htm','type':'Compiled folio notes, attribution to Rene','independence':'Rene claim and Stolfi compilation are one chain'},
 'vatne':{'url':'https://crackingthevoynichcipher.com/wp-content/uploads/2022/10/5_the_morphology_of_the_voynich_plants_siv_bugge_vatne_2022.pdf','type':'Original morphology discussion, 2022, associated with name-reading project','independence':'Independent authorship does not establish independent identification'},
 'celt':{'url':'https://celt.ucc.ie/document/G600005/','type':'Edited historical text; modern interim edition','work_date':'1415','witness':'TCD 1343 (H.3.22), pp.47–106; believed fifteenth century; some editorial emendations','independence':'Independent historical naming evidence, NOT independent Voynich identification; one textual tradition'},
 'med_failed':{'url':'https://quod.lib.umich.edu/m/middle-english-dictionary/dictionary/MED51217','type':'Access failed (403); no attestation admitted'}
}
claims=[
 {'page':'f2v','candidates':['water lily, species unresolved','Nymphaea candida','Nymphaea alba','unidentified / stylized or composite plant'],'source':'stolfi','locator':'Comments; Rene attribution','note':'Retain both names as reported; do not adopt the source’s asserted synonymy as modern taxonomy. Vatne p.5 also proposes alba but notes flower mismatches; no extra independent vote.','status':'Provisional visual identification; not a confirmed species','names':['nenufar']},
 {'page':'f2r','candidates':['Centaurea, genus only','Centaurea diffusa','Centaurea biebersteinii','unidentified / stylized or composite plant'],'source':'bax','locator':'pp.25–27','note':'Bax reports Sherwood’s two species alternatives and cites Velinska; original antecedents not checked. Count as one retrieved chain, not three votes.','status':'Decipherment-associated; originals unresolved','names':['centauria']},
 {'page':'f16r','candidates':['Juniperus oxycedrus','juniper, species unresolved','unidentified / stylized or composite plant'],'source':'bax','locator':'pp.14–17','note':'Peterson was invited to assess the suggested identity; prompted corroboration. OROR analysis and image identification are coupled.','status':'Decipherment-associated; no blind corroboration','names':['juniper']},
 {'page':'f41v','candidates':['Coriandrum sativum','unidentified / stylized or composite plant'],'source':'bax','locator':'pp.22–25','note':'Identification attributed to Sherwood; original not inspected. Proposed reading concerns marginal text, not the frozen paragraph-first slot.','status':'Decipherment-associated; slot mismatch retained','names':['coriandrum']},
 {'page':'f9v','candidates':['violet / pansy (unverified lead)','unidentified / stylized or composite plant'],'source':None,'locator':None,'note':'Search lead not verified to a folio-specific original passage. No plant-name pairing admitted. Uiola kept in historical-name ledger only.','status':'BLOCKED: identification provenance incomplete','names':[]},
 {'page':'f6v','candidates':['Ricinus communis (unverified lead)','unidentified / stylized or composite plant'],'source':None,'locator':None,'note':'Secondary lead only; original identification and period name not verified.','status':'BLOCKED: identification and name evidence incomplete','names':[]}
]
names=[
 {'id':'nenufar','form':'Nenufar','language':'Latin medical heading in Irish text','locator':'chapter 207, witness marker 91b2','referent':'water-lily flower','compatibility':'Broad water-lily candidate only; species not established'},
 {'id':'centauria','form':'Centauria','language':'Latin medical heading in Irish text','locator':'chapter 80, 67b1','referent':'greater / lesser centaury distinction','compatibility':'BLOCKED as species anchor: historical centaury is not automatically modern Centaurea'},
 {'id':'juniper','form':'Fructus iuniperi','language':'Latin medical heading in Irish text','locator':'chapter 139, chapter index; glossary iubar craigi','referent':'juniper berries','compatibility':'BLOCKED as species anchor: glossary identifies communis, not oxycedrus; full phrase retained, no trimming'},
 {'id':'coriandrum','form':'Coriandrum','language':'Latin medical heading in Irish text','locator':'chapter 95','referent':'coriander','compatibility':'Conditional botanical link only; page identification and text-slot function unverified'},
 {'id':'uiola','form':'Uiola','language':'Latin medical heading in Irish text','locator':'chapter 276, 103a2','referent':'violet; glossary distinguishes sweet violet from pansy','compatibility':'UNPAIRED: f9v identification not verified; do not merge violet and pansy'}
]
for n in names:
    n.update(source='celt',phonetic_value=None,normalization='Exact edited heading preserved; no sound normalization',attestation='Edited witness, not direct facsimile verification')
rows=json.loads(ATLAS.read_text(encoding='utf-8'))
raw=EVT.read_text(encoding='latin1').splitlines()
slots=[]
for c in claims:
    for tr in ['H','F']:
        rr=[r for r in rows if r[0]==tr and r[1]==c['page'] and r[5]=='P']
        if not rr:
            slots.append(dict(page=c['page'],transcription=tr,status='missing')); continue
        r=rr[0]
        matches=[x for x in raw if re.match(r'^<'+re.escape(r[6])+';'+tr+r'>',x)]
        slots.append(dict(page=r[1],transcription=tr,section=r[2],hand=r[3],currier=r[4],format=r[5],locus=r[6],first_token=r[7][0] if r[7] else None,full_line=r[7],raw=matches,status='uncertainty retained' if not r[7] or r[7][0] is None else 'transcribed; not a semantic label'))
protocol={
 'version':'plant-candidates-v76', 'scope':'First bounded evidence inventory: six folios, four sourced identification records and two blocked leads. Not a complete botanical catalogue.',
 'candidate_selection':'Published identification leads selected without fitting or scoring sound resemblance in this build. Prior exposure to manuscript and published proposed readings acknowledged; not blind.',
 'slot':'First source paragraph row, first token, separately H/F. Null stays unresolved; never promote next word. Marginal text and later paragraph openings not substituted.',
 'transcriptions':'H and F are alternate readings of one manuscript, not independent replication.',
 'unknown_option':'Every page retains unidentified/stylized/composite as an alternative; no forced identity.',
 'freeze':'Claims, competing identities, exact name forms, sources and slots frozen by SHA256 before any new sound fitting. Additions require a new version.',
 'sound_mapping_fitted':False,'ready_for_confirmatory_decoding':False,
 'next_gate':'Verify image identifications and taxon/name compatibility independently; qualify a decoder on known controls and freeze split/search budget before fitting. These already-exposed pages are not fresh confirmation.',
 'future_null':'If exploratory fitting is later authorized, permute whole plant-page pairings and repeat the entire selection/search with identical alternatives and budget; H/F assessed separately.',
 'excluded':'Modern multilingual synonyms, inferred pronunciations, unverified historical spellings, and published sound keys are not candidate sound mappings.'
}
save('SOURCES.json',sources); save('IDENTIFICATIONS.json',claims);save('HISTORICAL-NAMES.json',names);save('H-F-SLOTS.json',slots);save('PROTOCOL.json',protocol)
e=lambda x:html.escape(str(x))
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Plant candidates — frozen evidence table</title><style>body{font:16px/1.55 system-ui;margin:36px auto;max-width:1250px;padding:0 22px;background:#102020;color:#e8eee8}a{color:#9fdfbd}h1,h2{color:#c7efcb}table{border-collapse:collapse;width:100%;margin:22px 0}td,th{border:1px solid #47605a;padding:12px;text-align:left;vertical-align:top}small{color:#b8c9c0}.notice{padding:18px;background:#293a30;border-left:4px solid #dbbb73}code{overflow-wrap:anywhere}details{margin:12px 0}li{margin:6px 0}</style><h1>Plant candidates & historical names</h1><p>v76 · Frozen research inventory · 23 October 2026</p><p class="notice">Six folios. No plant identity is treated as confirmed. No sound mapping fitted. Four sourced identification records; two blocked leads. This is a starting table, not a qualified decipherment dataset.</p><h2>Identifications and text slots</h2><table><tr><th>Folio / metadata</th><th>Competing candidates</th><th>H / F opening</th><th>Evidence and limits</th></tr>']
for c in claims:
    ss=[s for s in slots if s['page']==c['page']]
    meta=ss[0]
    src=f'<a href="{sources[c["source"]]["url"]}">{e(c["source"])} {e(c["locator"])}</a>' if c['source'] else 'Original source unresolved'
    parts.append(f'<tr><td><b>{e(c["page"])}</b><br><small>Hand {e(meta.get("hand"))}; Currier {e(meta.get("currier"))}; {e(meta.get("section"))}; P</small></td><td>'+ '<br>'.join(e(x) for x in c['candidates'])+'</td><td>'+ '<br>'.join(f'{s["transcription"]}: <code>{e(s.get("first_token") or "[unresolved]")}</code>' for s in ss)+f'</td><td>{src}<p>{e(c["note"])}</p><b>{e(c["status"])}</b></td></tr>')
parts.append('</table><h2>Historical name ledger</h2><p>All five forms below come from one edited tradition: <a href="'+sources['celt']['url']+'">Ó Cuinn’s Materia Medica</a>, composed 1415; the base witness TCD H.3.22 is assigned to the fifteenth century. Editorial forms are not direct image checks. This establishes availability in that tradition, not Voynich’s language or exact species.</p><table><tr><th>Written form</th><th>Attestation</th><th>Compatibility / unresolved alternatives</th></tr>')
for n in names: parts.append(f'<tr><td><code>{e(n["form"])}</code><br><small>{e(n["language"])}</small></td><td>{e(n["locator"])}</td><td>{e(n["compatibility"])}</td></tr>')
parts.append('</table><h2>Neighboring text and original readings</h2>')
for s in slots:
    parts.append(f'<details><summary>{e(s["page"])} / {s["transcription"]} / {e(s.get("locus"))}</summary><p><code>{e(" ".join(w if w is not None else "[uncertain]" for w in s.get("full_line",[])))}</code></p><pre>{e(chr(10).join(s.get("raw",[])))}</pre></details>')
parts.append('<h2>Source independence</h2><p>Sherwood → Bax is a citation chain. Peterson’s response to Bax’s suggested juniper is prompted corroboration. Rene → Stolfi is another chain. Vatne’s separate authorship does not demonstrate blind independence. Historical name attestations verify names, not these Voynich plants.</p><h2>Freeze and exclusions</h2><ul>'+''.join('<li>'+e(protocol[k])+'</li>' for k in ['slot','candidate_selection','freeze','next_gate','excluded'])+'</ul><p>Unverified f6v/f9v leads remain blocked. MED access failed; no dictionary spelling was silently supplied. No held-out decoding score exists.</p><p><a href="FREEZE.json">SHA256 freeze</a> · <a href="IDENTIFICATIONS.json">Identifications</a> · <a href="HISTORICAL-NAMES.json">Names</a> · <a href="H-F-SLOTS.json">H/F data</a> · <a href="SOURCES.json">Sources</a> · <a href="PROTOCOL.json">Protocol</a></p></html>')
(OUT/'report.html').write_text(''.join(parts),encoding='utf-8')
assert len(slots)==12 and all(s.get('raw') for s in slots)
assert len({(s['page'],s['transcription']) for s in slots})==12
save('VERIFICATION.json',{'slot_records':12,'raw_loci_found':12,'first_token_equals_atlas':True,'mappings_fitted':0,'visual_browser_review':'not performed','checked':'JSON parsed, source slots matched, all expected H/F records present'})
files=[p for p in OUT.iterdir() if p.is_file() and p.name!='FREEZE.json']
save('FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{p.name:sha(p) for p in sorted(files)},'inputs':{str(ATLAS):sha(ATLAS),str(EVT):sha(EVT)},'mapping_fit_started':False})
print(json.dumps({'folder':str(OUT),'folios':len(claims),'names':len(names),'slots':[(s['page'],s['transcription'],s.get('first_token')) for s in slots]}))
