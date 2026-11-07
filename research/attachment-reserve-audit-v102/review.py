from pathlib import Path
import collections,hashlib,html,json,re,zipfile
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[R/'FREEZE.json',R/'RESERVE-LEADS.json',R/'LOCUS-MENTION-MAP.json',R/'review.py']
freeze={str(p):sha(p) for p in paths};save('REVIEW-FREEZE.json',freeze)
leads=load(R/'RESERVE-LEADS.json');unique={}
for i,x in enumerate(leads):
 t=x['excerpt'];s=t.lower()
 if 'preserv' in s and not re.search(r'untouched|unseen|hold[ -]?out|held[ -]?out|\breserv|\bblind|sequester|never (seen|used|inspect)|not (seen|used|inspect)',s):
  cat='keyword false match: preserved';why='Preserved line numbering or files is not a reserve declaration.'
 elif 'cut 6' in s:
  cat='explicitly used text; proposed image validation';why='Explicitly treats the 17 test folios as used. Next untouched test is proposed independent image judgment, not unexposed text or a custody record.'
 elif 'root type' in s or 'valence' in s or 'rater' in s or 'blind image pilot' in s or 'blind visual' in s:
  cat='image/annotation blinding';why='Blind raters or withheld image screens concern annotation outcomes. They do not certify that manuscript word sequences were protected from analysis.'
 elif 'held-out folios' in s or 'held-out counts' in s or 'held-out short/long' in s:
  cat='retrospective model test split';why='Previously scored fitting/evaluation split; does not create a new historical source reserve.'
 elif '119 diagram rings' in s:
  cat='previously analysed diagram/text pairs';why='Explicit inherited account of pair-order comparison with running text and paragraph controls. Not a protected reserve; numbers are not independently validated here.'
 elif 'not in the model?' in s:
  cat='held-out control relative to one model';why='batch3.py trains on paragraph boundaries except f57v and evaluates non-P lines with >=20 words. A model-relative control inspected in this script is not an untouched reserve for the later hypothesis.'
 else:
  cat='generic blinding/advice or scope text';why='No fixed protected Voynich passage list with exposure and custody history is specified.'
 rec=dict(index=i,**x,category=cat,disposition=why,reserve_admitted=False)
 unique.setdefault(t,dict(category=cat,disposition=why,references=[],excerpt=t))['references'].append(dict(source=x['source'],member=x['member'],line=x['line']))
 leads[i]=rec
save('RESERVE-REVIEW.json',leads);save('UNIQUE-RESERVE-LEADS.json',list(unique.values()))
# Read the original source text only. Record selector lines, never execute the archive.
zpath=Path('C:/Users/lewis/Downloads/claude-circles-2026-10-21.zip')
with zipfile.ZipFile(zpath) as z:
 member=next(n for n in z.namelist() if n.endswith('/batch3.py'));lines=z.read(member).decode('utf-8-sig').splitlines()
 selected=[dict(line=i+1,text=t) for i,t in enumerate(lines) if i in list(range(13,22))+list(range(116,138))]
 save('BOUNDARY-MODEL-RECEIPT.json',dict(archive=str(zpath),archive_sha256=sha(zpath),member=member,lines=selected,reading='H only in this script; no F result inferred',hand='No hand-stratified result reconstructed',interpretation='Source describes exploratory prior H boundary-order training on all paragraph lines except f57v and evaluation of sufficiently long non-P lines. This is source-selector evidence, not a rerun or independently verified effect.'))
assert all(not x['reserve_admitted'] for x in leads)
for p,h in freeze.items():assert sha(Path(p))==h
f=load(R/'FREEZE.json');inv=f['attachments'];units=load(R/'TEXT-UNITS.json');members=load(R/'ARCHIVE-MEMBERS.json');strata=load(R/'STRATA.json');mapped=load(R/'LOCUS-MENTION-MAP.json')
for x in inv:
 if x['exists']:assert sha(Path(x['path']))==x['sha256']
old=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert old['status']=='FAIL' and old['robustness_banks_not_run']==[2,3]
result=dict(status='NO GENUINE WORD-SEQUENCE RESERVE ESTABLISHED',attached_paths=len(inv),available=sum(x['exists'] for x in inv),archives=sum(x['path'].endswith('.zip') for x in inv),text_units=len(units),unique_content_hashes=len({x['sha256'] for x in units}),reserve_keyword_hits=len(leads),distinct_lead_lines=len(unique),reserve_admitted=0,power='CLOSED / NOT RUN',scoring='CLOSED / NOT RUN',v98='FAIL unchanged; banks2/3 unrun',limits='28 named local attachment paths from fixed eight-chat histories, not a full external Claude export; no claim about inaccessible/deleted or unmentioned material.')
save('RESULTS.json',result)
save('VERIFICATION.json',dict(attachment_hashes='PASS',review_hashes='PASS',all_leads_dispositioned=len(leads),mapped_reading_loci=len(mapped),strata=len(strata),source_scripts_executed=0,archives_extracted=0,power='NOT RUN',new_score='NOT COMPUTED',v98='FAIL unchanged',browser_visual_review='not performed'))
e=html.escape
def table(h,rr):return '<div class="scroll"><table><tr>'+''.join('<th>'+e(x)+'</th>' for x in h)+'</tr>'+''.join('<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in r)+'</tr>' for r in rr)+'</table></div>'
body='<p>VOYNICH · SAVED CLAUDE ATTACHMENT RESERVE AUDIT · v102</p><h1>Do the attachments contain a genuine reserve?</h1><p><strong>No protected word-sequence reserve was established. Power and scoring remain CLOSED.</strong> All failed v97/v98 gates and unrun v98 banks remain preserved. No archive script or historical test was executed.</p>'
body+=table(['Check','Result'],[['Explicit attachment paths',len(inv)],['Available paths',result['available']],['ZIP packages',result['archives']],['Text units inspected',len(units)],['Distinct content hashes',result['unique_content_hashes']],['Reserve keyword leads',len(leads)],['Distinct lead lines',len(unique)],['Admitted reserve',0]])
body+='<h2>The strongest leads describe other kinds of holdout</h2><p>The saved research history explicitly says to <strong>treat the 17 held-out folios as used</strong>. Its proposed next untouched test is label-to-entry correspondence judged independently from images. This can be a new annotation outcome while the underlying word sequences are already exposed; it does not create a fresh sh→qok passage reserve.</p><p>A pilot also withheld some image screens and sought an uninformed rater. That is blinding for image judgments, not evidence that those physical passages were withheld from text analysis. These are dated pilot statements, not claims that the annotation remains uncollected today. Later history includes image-comparison failures, which remain preserved.</p><p>Other held-out references concern fitting/test splits, vocabulary prediction, or controls relative to a model. Generic advice to preregister and count blind is not a record that such custody was established.</p>'
body+='<h2>Earlier boundary-order work adds exposure</h2><p>The Claude circle package labels itself exploratory. Its batch3.py selects H readings, learns word-boundary transitions from paragraph text except f57v, and evaluates long non-paragraph lines. The held-out comment therefore means outside that model’s paragraph training set, not historically untouched for a later order hypothesis. F and hand-specific results are not inferred from this H-only source.</p><p>The pasted history also reports diagram-ring versus running-text pair comparisons. We retain that as an inherited exposure claim, without rerunning the script or treating its effect size as validated here. This adds evidence of prior neighbouring-word exploration outside the narrow v75 test.</p>'
body+='<h2>Every reserve lead and disposition</h2>'+table(['Category','Disposition','Distinct source line'],[[x['category'],x['disposition'],x['excerpt']] for x in unique.values()])
body+='<h2>H/F and hands remain separate</h2><p>Attachment locator mentions often do not specify a reading. The following column counts shared locator references only; it is <strong>not</strong> evidence of separate H and F inspection or a new word count. No missing reading is supplied and the f73 hand conflict is unchanged. The full ledger retains source file/member/line references.</p>'
body+=table(['Section','Hand','Variety','Format','Reading','Loci','Locator referenced; reading unspecified'],[[x['section'],x['hand'],x['variety'],x['format'],x['reading'],x['loci'],x['loci_with_reading_unspecified_locator_reference']] for x in strata])
body+='<h2>Boundary reached</h2><p>All 28 explicitly attached local files were available. Every non-directory ZIP member fell within the frozen text-format/size limits and was read without extraction or execution. These are saved excerpts and packages, not complete access to the external Claude workspace. Missing external custody evidence remains missing; no local keyword search can establish its absence everywhere.</p><p>The available attachment trail supplies no protected passage list for the requested prospective test. Candidate power remains NOT RUN because reserve admission is unmet, not because measured power is low. Repeatedly repartitioning the exposed corpus cannot repair that. Any further manuscript work must be explicitly treated as retrospective, or start from genuinely independent evidence under a separately frozen design.</p><p><a href="PROTOCOL.json">Frozen rules</a> · <a href="FREEZE.json">All attached paths and hashes</a> · <a href="RESERVE-REVIEW.json">All lead dispositions</a> · <a href="BOUNDARY-MODEL-RECEIPT.json">Historical selector lines</a> · <a href="PASSAGE-MENTIONS.json">Passage-reference receipts</a> · <a href="LOCUS-MENTION-MAP.json">Locus map</a> · <a href="ARCHIVE-MEMBERS.json">ZIP member audit</a> · <a href="VERIFICATION.json">Verification</a> · <a href="../exposure-history-v101/report.html">Previous conversation trace</a></p><p>Source verification only; browser appearance unreviewed. H/F are dependent alternate readings.</p>'
css='<style>body{max-width:1400px;margin:auto;padding:28px;background:#f5f2e9;color:#203f35;font:16px/1.55 system-ui}h1{font-size:32px}h2{margin-top:30px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%}th,td{padding:9px;border-bottom:1px solid #bbc9bb;text-align:left;vertical-align:top}a{color:inherit}</style>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Saved attachment reserve audit · v102</title>'+css+'<main>'+body+'</main></html>',encoding='utf-8')
print(json.dumps(result))
