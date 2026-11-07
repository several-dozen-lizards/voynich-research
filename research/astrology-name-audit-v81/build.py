from pathlib import Path
import json, re, hashlib, collections, html

R = Path(__file__).resolve().parent
P = R.parent
SOURCE = P / 'complete-atlas-v56/ROWS.json'
RAW = Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
HIST = P / 'wheel-parts-v51/historical/chaucer-astrolabe-edited.txt'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, x): (R/n).write_text(json.dumps(x, indent=2, ensure_ascii=False), encoding='utf-8')
protocol = {
 'scope': 'Referent and transcription feasibility audit, not a phonetic fit or statistical test. All twelve surviving zodiac panels, every reading, every source locus, uncertain slots retained. f69v separately inventoried as a conditional lunar-mansion lead.',
 'selection': 'Panels chosen from published illustration descriptions, not token sound resemblance. No rare-word or anomaly threshold selected here. Existing v65 model cannot be transferred as a qualified zodiac anomaly detector: its shared H/F prerequisite is absent.',
 'readings': 'No F rows on these twelve panels in the current source. H/U/V/C/K/Q/X kept by source code, never treated as independent samples or silently substituted for F. Source-code provenance/possible dependencies require audit before replication claims.',
 'referents': 'Sign-level identification does not establish any individual token as its name. Figure/star labels, circular text and central-star label kept separate. Later month annotations are excluded as Voynich phonetic ground truth. f70v2.C.1 is explicitly Central star in source comments, not a demonstrated Pisces label.',
 'historical': 'Candidate written forms from the already retrieved edited Chaucer Astrolabe c1391, not diplomatic manuscript spellings or reconstructed pronunciation. No language chosen by fit; this is one tradition, not a complete historical lexicon.',
 'next_gate': 'Audit image-to-locus geometry and reading provenance; qualify an anomaly ranking within same hand and source format before selection. Freeze candidate vocabulary, unit transformations, slot alternatives and language families before fitting. Qualify known-name controls at actual sample size with wrong pairings, all searched rotations/reversals and full selection procedure. Split by sign so both Aries panels or both Taurus panels stay together in generalisation tests. A separate predeclared repeat-panel consistency check may use the duplicates, but is not independent sign replication.',
 'limits': 'Rare or atypical is not equivalent to phonetic. Ordinary phonetic words may look typical. Symbol-to-written-letter controls are not historical phonology. Shared morphology, numerals, degree/calendar designations and uncertain reading are alternatives. No sounds assigned; prior work unchanged.'
}
save('PROTOCOL.json', protocol)
save('PRE-INVENTORY-FREEZE.json', {str(p): sha(p) for p in [Path(__file__), R/'PROTOCOL.json', SOURCE, RAW, HIST]})
signs = [('f70v2','Pisces'),('f70v1','Aries'),('f71r','Aries'),('f71v','Taurus'),('f72r1','Taurus'),('f72r2','Gemini'),('f72r3','Cancer'),('f72v3','Leo'),('f72v2','Virgo'),('f72v1','Libra'),('f73r','Scorpio'),('f73v','Sagittarius')]
signmap = dict(signs)
rows = json.loads(SOURCE.read_text(encoding='utf-8'))
def record(x):
 return dict(reading=x[0], page=x[1], sign=signmap.get(x[1]), section=x[2], hand=x[3], variety=x[4], source_unit=x[5], mapped_zone=x[6], locator=x[8], tokens=x[9], raw=x[10], role=('central star (source comment)' if x[8]=='f70v2.C.1' else 'circumferential text' if x[5].startswith('R') else 'figure/star-associated label; exact referent unresolved' if x[5].startswith('S') else 'unresolved'))
selected = [record(x) for x in rows if x[1] in signmap]
save('ALL-READINGS.json', selected)
save('F69V-CONDITIONAL.json', [record(x) for x in rows if x[1]=='f69v'])
byloc = collections.defaultdict(list)
for x in selected: byloc[x['locator']].append(x)
save('LOCUS-ALTERNATIVES.json', dict(byloc))
rawlines = RAW.read_text(encoding='latin1').splitlines()
comments = {}
for i, line in enumerate(rawlines):
 m = re.match(r'## <(f\d+[rv]\d*)\.([^>]+)>', line)
 if m and (m[1] in signmap or m[1]=='f69v'):
  out=[]
  for nxt in rawlines[i+1:]:
   if not nxt.startswith('#'): break
   out.append(nxt)
  comments[f'{m[1]}.{m[2]}'] = out
save('SOURCE-UNIT-COMMENTS.json', comments)
hist = HIST.read_text(encoding='utf-8')
forms = {'Aries':['Aries'], 'Taurus':['Taurus'], 'Gemini':['Gemini'], 'Cancer':['Cancer','Cancre'], 'Leo':['Leo'], 'Virgo':['Virgo'], 'Libra':['Libra'], 'Scorpio':['Scorpio','Scorpioun'], 'Sagittarius':['Sagittarius','Sagittarie'], 'Capricorn':['Capricornus','Capricorne','Capricorn'], 'Aquarius':['Aquarius','Aquarie'], 'Pisces':['Pisces']}
attested=[]
for sign, names in forms.items():
 for name in names:
  hits=list(re.finditer(r'\b'+name+r'\b',hist,re.I))
  assert hits, name
  attested.append(dict(sign=sign, form=name, occurrences=len(hits), examples=[dict(character_offset=m.start(), context=hist[max(0,m.start()-90):m.end()+100]) for m in hits[:2]], source='https://sourcebooks.web.fordham.edu/source/chaucer-astro.asp', status='edited written attestation only; no pronunciation or Voynich pairing'))
save('HISTORICAL-CANDIDATES.json', attested)
coverage=[]
for page, sign in signs:
 a=[x for x in selected if x['page']==page]
 coverage.append(dict(page=page,sign=sign,rows_by_reading=dict(collections.Counter(x['reading'] for x in a)),hands_in_local_metadata=sorted({x['hand'] for x in a}),H_readable_tokens=sum(w is not None for x in a if x['reading']=='H' for w in x['tokens']),H_unknown_slots=sum(w is None for x in a if x['reading']=='H' for w in x['tokens'])))
save('COVERAGE.json',coverage)
repeat=[]
for sign, p1, p2 in [('Aries','f70v1','f71r'),('Taurus','f71v','f72r1')]:
 for reading in sorted({x['reading'] for x in selected}):
  for role in ['circumferential text','figure/star-associated label; exact referent unresolved']:
   sets=[{w for x in selected if x['page']==p and x['reading']==reading and x['role']==role for w in x['tokens'] if w} for p in [p1,p2]]
   repeat.append(dict(sign=sign,reading=reading,role=role,pages=[p1,p2],type_counts=list(map(len,sets)),shared_types=sorted(sets[0]&sets[1]),status='descriptive overlap; no enrichment, anomaly, name or sound claim'))
save('REPEATED-SIGN-OVERLAPS.json',repeat)
sources=[dict(url='https://www.voynich.nu/writing.html',used='Later month annotations, twelve-panel/sign mapping; names not used as Voynich cribs'),dict(url='https://www.voynich.nu/q10/index.html',used='Pisces central-star label and conditional f69v lunar-mansion interpretation'),dict(url='https://www.voynich.nu/q11/index.html',used='Repeated Aries/Taurus and figure labels'),dict(url='https://www.voynich.nu/q12/index.html',used='Scorpio/Sagittarius and missing folio'),dict(url='https://sourcebooks.web.fordham.edu/source/chaucer-astro.asp',used='Edited c1391 primary text, written sign-name forms')]
save('SOURCES.json',sources)
summary=dict(panels=len(signs),distinct_signs=len(set(signmap.values())),rows=len(selected),loci=len(byloc),F_rows=sum(x['reading']=='F' for x in selected),historical_written_forms=len(attested),sound_mappings_fitted=0,warning='Local Davis-derived metadata assigns f73r/v hand3, whereas current voynich.nu descriptions list hand4. Conflict preserved; no pooling or inference resolving it.',central_star_alternatives=[dict(reading=x['reading'],tokens=x['tokens'],raw=x['raw']) for x in byloc['f70v2.C.1']])
save('SUMMARY.json',summary)
e=lambda x:html.escape(str(x))
body='<h1>Astrology name feasibility audit · v81</h1><p>Twelve panels give ten surviving sign identities. They do not give ten identified Voynich name tokens. No sounds fitted.</p>'
body+='<h2>What earlier work permits</h2><p>v65 atypical spelling is a model-relative candidate signal, not evidence of phonetic writing. v79/v80 supplied correct name pairs and boundaries; v80 first passed at 36 names for full letters and consonant-only in that benchmark. Ten signs cannot inherit that qualification, nor does 36 establish a universal requirement. f9v remains excluded from fitting.</p>'
body+='<h2>Coverage and referents</h2><p>No F transcription is present here. All available readings and uncertain slots are preserved. The later readable month annotations cannot supply Voynich glyph sounds. Most labels attach to figures/stars, possibly degree or calendar designations. Source comments call f70v2.C a central star, not the sign title.</p><p>'+e(summary['warning'])+'</p>'
body+='<table><tr><th>Panel</th><th>Sign</th><th>Local hand</th><th>Available readings: loci</th></tr>'
for x in coverage: body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [x['page'],x['sign'],', '.join(x['hands_in_local_metadata']),x['rows_by_reading']])+'</tr>'
body+='</table><h2>Central star · f70v2.C.1</h2><pre>'+e(json.dumps(summary['central_star_alternatives'],indent=2))+'</pre>'
body+='<h2>Historically attested written candidates</h2><p>One edited c1391 tradition, not a complete multilingual vocabulary or phonological reconstruction. Capricorn/Aquarius are source controls; their Voynich zodiac panels do not survive.</p><table><tr><th>Sign</th><th>Written forms</th></tr>'
for sign,names in forms.items():body+=f'<tr><td>{e(sign)}</td><td>{e(", ".join(names))}</td></tr>'
body+='</table><h2>Productive tests</h2><p>Register the exact image-to-label relation first. Repeated Aries and Taurus can test same-name consistency; shared words are currently descriptive only. Keep duplicate panels in one sign-level training/test group. Compare candidate outliers with same-hand, same-format peers, not body prose. Freeze all language, spelling, segmentation, vowel-omission and slot alternatives before evaluating a common mapping. Test wrong sign assignments with the entire selection/search procedure repeated. Require predictions for signs withheld as whole groups. A failure with ten signs may be low coverage rather than evidence against phonetic naming.</p><p>f69v has a published 28-lunar-mansion interpretation, but it remains conditional; count/order/name alignment must not be assumed. Stars, planets and the proposed f68r3 Pleiades need their own referent audits.</p>'
body+='<h2>Complete source loci</h2><p>Every locus is included; no attractive matches selected. Open each row for all readings.</p>'
for loc,alts in byloc.items():
 body+=f'<details><summary>{e(loc)} · {e(signmap[alts[0]["page"]])} · {e(alts[0]["role"])}</summary><pre>{e(json.dumps(alts,ensure_ascii=False,indent=2))}</pre></details>'
body+='<h2>Audit files</h2>'
for fn in ['PROTOCOL.json','COVERAGE.json','ALL-READINGS.json','LOCUS-ALTERNATIVES.json','SOURCE-UNIT-COMMENTS.json','HISTORICAL-CANDIDATES.json','REPEATED-SIGN-OVERLAPS.json','F69V-CONDITIONAL.json','SUMMARY.json','SOURCES.json']:
 body+=f'<p><a href="{fn}">{fn}</a></p>'
for s in sources:body+=f'<p><a href="{e(s["url"])}">{e(s["used"])}</a></p>'
(R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Astrology name audit v81</title><style>body{font:17px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;background:#f5f2e9;color:#193c39;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #a9b8ad;padding:8px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{border-bottom:1px solid #bbc7bd;padding:7px}a{color:#17616d}</style>'+body,encoding='utf-8')
assert summary['F_rows']==0 and len(byloc)==len([x for x in selected if x['reading']=='H'])
assert len(coverage)==12 and len(set(signmap.values()))==10
assert sum(len(x) for x in byloc.values())==len(selected)
for p,h in json.loads((R/'PRE-INVENTORY-FREEZE.json').read_text()).items():assert sha(Path(p))==h
save('VERIFICATION.json',dict(source_and_protocol_hashes_unchanged=True,every_selected_row_preserved=True,loci_have_H=True,no_F_rows=True,historical_forms_found=True,layout='HTML structure generated; browser appearance not reviewed',semantic_qualification=False))
save('SHA256SUMS.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps(summary,indent=2))
