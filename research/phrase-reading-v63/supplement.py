import runpy,json,re,html,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
source=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
lines=load(R/'LINES.json');loci={x['locator'] for x in lines};raw={}
for line in source.read_bytes().decode('latin-1').splitlines():
 m=re.match(r'<([^;>]+);([HF])>\s*(.*)',line)
 if m and m[1] in loci:raw.setdefault(m[1],{})[m[2]]=m[3]
save('RAW-SOURCE-LINES.json',{'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'lines':raw,'note':'Frozen parser removes ! rather than treating it as a word break. Raw punctuated strings retained; no image adjudication performed.'})
mapping={'daiin':'GLUE?','dy':'CLOSER?','dal':'CLOSER?','s':'CLOSER?','al':'CLOSER?','qokeedy':'INSTRUCTION?','qokeey':'INSTRUCTION?','qokaiin':'INSTRUCTION?','qol':'INSTRUCTION?','chedy':'CONTENT?','shedy':'CONTENT?','chey':'CONTENT?','cheol':'CONTENT?'}
protocol={'status':'Fifth authored reading, exploratory; no independent labels or semantic qualification','mapping':mapping,'policy':'Only explicit whole words in supplied proposal assigned. No general qo/ch/sh meaning inferred. All other words unassigned, uncertainties barriers; same mapping in every displayed passage and transcription. Prior four alternatives unchanged. No best-reading score.','prediction':'More candidate content with more daiin is untested. A valid test must condition on line length/readable opportunities and hand/section/format/position, preserve word frequency, qualify on known text with independent roles, then transfer to held-out pages. Lines are not established clauses.','limits':['Neighbour entropy rises with sample count and pooled strata; frequency-matched rarefaction needed before calling daiin unusually broad.','First/last percentages require each stratum baseline: 10% first can be ordinary for ten-word lines.','daiin can be a common content word, formula, orthographic form or context-dependent unit; broad neighbours do not identify and/ana.','Earlier qo evidence was a controlled bath-versus-botanical contrast, not a decoded recipe operation.','No collapse of dain/daiin/daiiin or oraiin/or aiin after seeing the results.']}
save('FIFTH-READING-PROTOCOL.json',protocol)
worksheet=load(P/'category-worksheet-v60/WORKSHEET.json');out=[]
for c in worksheet['cohorts']:
 for passage in c['passages']:
  for tr,reading in passage['readings'].items():
   ws=reading['tokens'];out.append({'cohort':c['id'],'locator':passage['locator'],'transcription':tr,'tokens':ws,'roles':[mapping.get(w,'UNKNOWN' if w is None else 'UNASSIGNED') for w in ws]})
save('FIFTH-READING.json',out)
note='''<h2>What causes the difference?</h2><p><b>or aiin:</b> H has two training occurrences, both on f55r; rank 5. F retains only one, below the count≥2 threshold, because f55r.P.5 reads yoraiin. Thus this selection was supported by one training folio, not cross-folio training recurrence. On test folios H has eight pairs, F three. Every one of the five lost F pairs is joined as oraiin: f33r.P.5, f33v.P.9, f39v.P.3, f39v.P.4, f43v.P.12. There is no target-letter change in those five. This is a segmentation-sensitive candidate, not a secure two-word phrase.</p><p><b>chol daiin:</b> rank 3 in both training readings, H 11 and F 13. The two extra F training examples are f17r.P.11 (H daiiin / F daiin) and f17v.P.8 (H choldaiin / F chol daiin). In test text, H 17 and F 18; the sole difference is f47v.P.9 (H dain / F daiin). Both have occurrences on the same 13 test folios. Their different permutation p values also reflect each reading's full line vocabulary and segmentation, not only this count difference.</p><p>Raw source strings are retained alongside parsed text. The frozen cleaning removes !; it does not treat ! as a word boundary. No manuscript image has been adjudicated here, and the two readings have not been harmonized.</p><p><a href="RAW-SOURCE-LINES.json">Raw transcription evidence</a></p><h2>Fifth reading: proposed instruction–content–glue–closer template</h2><p>Only explicitly named whole words are assigned below; the same word keeps the same tentative role. Existing worksheet readings are unchanged. This is an authored hypothesis, not a role learned from the data or a validated grammar. Unassigned words remain visible.</p>'''
for x in out:
 note+='<details><summary>'+html.escape(x['cohort']+' '+x['locator']+' '+x['transcription'])+'</summary><p>'+html.escape(' · '.join(('?' if w is None else w)+' ['+role+']' for w,role in zip(x['tokens'],x['roles'])))+'</p></details>'
note+='<pre>'+html.escape(json.dumps(protocol,indent=2))+'</pre><p><a href="FIFTH-READING.json">Fixed worksheet substitutions</a> · <a href="FIFTH-READING-PROTOCOL.json">Hypothesis and limits</a></p>'
p=R/'report.html';p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8')
assert len(out)==16
assert all((w is None or role==mapping.get(w,'UNASSIGNED')) for x in out for w,role in zip(x['tokens'],x['roles']))
save('VERIFICATION.json',{'matched_line_loci':len(lines),'raw_loci_found':len(raw),'worksheet_readings':len(out),'fixed_assignments_verified':True,'prior_versions_unchanged':True,'visual_check':'not performed'})
print('41 paired loci; 16 fixed worksheet readings; raw source evidence saved.')
