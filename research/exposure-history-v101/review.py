from pathlib import Path
import collections,datetime,hashlib,html,json
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(R/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
C=Path('C:/Users/lewis/.codex/visualizations/2026/10/21/01a15c3d-56da-7f02-bc15-2522dc396abd/voynich-layout/circle-atlas-v13')
paths=[C/'atlas.json',C/'PROTOCOL.txt',P/'astrology-name-audit-v81/ALL-READINGS.json',P/'astrology-name-audit-v81/F69V-CONDITIONAL.json',P/'astrology-name-audit-v81/PROTOCOL.json',R/'LOCUS-EXPOSURE.json',R/'TIMELINE.json',R/'review.py',R/'chat-snapshots/01a16491-3972-7430-a33e-0da82c066bb4.json']
freeze={str(p):sha(p) for p in paths}
if (R/'REVIEW-FREEZE.json').exists():assert load(R/'REVIEW-FREEZE.json')==freeze
else:save('REVIEW-FREEZE.json',freeze)
circle=set()
for pg in load(C/'atlas.json')['pages']:
 for u in pg['units']:
  for en in u['entries']:
   for rd in en.get('readings',[]):
    if rd['transcriber'] in ('H','F'):circle.add((rd['transcriber'],en['locator']))
names={(x['reading'],x['locator']) for p in paths[2:4] for x in load(p) if x['reading'] in ('H','F')}
ledger=load(R/'LOCUS-EXPOSURE.json')
for x in ledger:
 key=(x['reading'],x['locus'])
 if key in circle:x['historical_evidence'].append('circle_atlas_v13_saved_reading')
 if key in names:x['historical_evidence'].append('v81_referent_audit_saved_passage')
save('LOCUS-EXPOSURE-REVIEWED.json',ledger)
groups=collections.defaultdict(list)
for x in ledger:groups[(x['section'],x['hand'],x['variety'],x['reading'])].append(x)
summary=[]
for k,rr in sorted(groups.items()):summary.append(dict(zip(['section','hand','variety','reading'],k),lines=len(rr),circle_atlas_rows=sum('circle_atlas_v13_saved_reading' in x['historical_evidence'] for x in rr),referent_audit_rows=sum('v81_referent_audit_saved_passage' in x['historical_evidence'] for x in rr)))
save('SUPPLEMENTARY-SUMMARY.json',summary)
timeline=load(R/'TIMELINE.json')
# An empty keyword accidentally matched the original conversational review, before a run.
# Correct the annotation explicitly, retaining the initial timeline as an audit receipt.
old=next(x for x in timeline if x['claim']=='Original full-paragraph spelling/layout development')
history=load(R/'HISTORY-EXCERPTS.json')
new=next(x for x in history if x['thread_id']=='01a15c3d-56da-7f02-bc15-2522dc396abd' and x['jsonl_line']==228)
old.update(timestamp=new['timestamp'],jsonl_line=new['jsonl_line'],excerpt=new['text'],claim='First saved original paragraph-layout model result (prior conversational review excluded)')
missing=next(x for x in timeline if x['claim']=='f68r3 full local sequence catalogue')
snap=load(paths[-1]);found=[]
for turn in snap['turns']:
 for item in turn['items']:
  if item.get('type')=='agentMessage' and 'LOCAL-SEQUENCE-CATALOGUE' in item.get('text',''):
   found.append((turn,item))
assert len(found)==1
t,item=found[0]
stamp=datetime.datetime.fromtimestamp(t['completedAt'],datetime.timezone.utc).isoformat()
missing.clear();missing.update(claim='f68r3 full local sequence catalogue',thread_id=snap['thread']['id'],timestamp=stamp,turn_id=t['id'],message_id=item['id'],snapshot=str(paths[-1]),excerpt=item['text'],evidence_limit='API snapshot final; absent from keyword-filtered history excerpts because final does not spell out a matched section/page keyword.')
save('TIMELINE-REVIEWED.json',timeline)
save('REVIEW-NOTES.json',dict(correction='Initial timeline picked the original chat review rather than a completed model result due to an empty keyword. Corrected to the first saved model result at session line228. Initial timeline/report preserved.',supplement='Added exact circle-atlas and v81 saved-passage membership. Fold-out catalogue final recovered from API snapshot; no missing timestamp invented.',scoring='Still CLOSED; no target score or power calculation.'))
report=(R/'report.html').read_text(encoding='utf-8')
if not (R/'report-initial.html').exists():(R/'report-initial.html').write_text(report,encoding='utf-8')
e=html.escape
report=report.replace('2026-10-21T02:17:09.023Z','2026-10-21T02:27:02.247Z').replace('Original full-paragraph spelling/layout development','First saved original paragraph-layout model result').replace('<td>66</td></tr>','<td>228</td></tr>')
report=report.replace('<td>unmatched filename</td><td>f68r3 full local sequence catalogue</td><td>see artifact</td>', '<td>'+e(stamp)+'</td><td>f68r3 full local sequence catalogue</td><td>API turn '+e(t['id'])+'</td>')
report=report.replace('href="TIMELINE.json"','href="TIMELINE-REVIEWED.json"').replace('href="LOCUS-EXPOSURE.json"','href="LOCUS-EXPOSURE-REVIEWED.json"')
block='<h2>Earlier circle and zodiac receipts</h2><p>The original circle-atlas-v13 saved exact H/F readings on its diagram pages on 21 October. This is text extraction/display evidence, not a new order test or proof of every line being human-inspected. The later astrology-name-audit-v81 also saved zodiac and f69v passages for referent/transcription investigation. That reaches the locally hand3 f73 pages as well as hand4 pages, without filling missing F from U/V.</p><div class="scroll"><table><tr><th>Section</th><th>Hand</th><th>Variety</th><th>Reading</th><th>Loci</th><th>Saved circle-atlas readings</th><th>Saved v81 passages</th></tr>'
for x in summary:block+='<tr>'+''.join('<td>'+e(str(x[k]))+'</td>' for k in ['section','hand','variety','reading','lines','circle_atlas_rows','referent_audit_rows'])+'</tr>'
block+='</table></div><p>These columns overlap earlier receipts. <a href="REVIEW-NOTES.json">Annotation correction and supplementary review</a> · <a href="REVIEW-FREEZE.json">Supplementary input hashes</a>. The initial timeline mislabeled the first conversational review as a model result; the final timeline corrects that to the first reported model result. No numerical result, admission rule or gate changed.</p>'
report=report.replace('<h2>Decision and remaining uncertainty</h2>',block+'<h2>Decision and remaining uncertainty</h2>')
(R/'report.html').write_text(report,encoding='utf-8')
assert len(ledger)==1783 and all(x['reserve_admission'].startswith('CLOSED') for x in ledger)
save('REVIEW-VERIFICATION.json',dict(new_artifact_hashes='PASS',distinct_HF_locus_membership='PASS',loci=1783,new_score='NOT COMPUTED',power='NOT RUN',reserve=0,timeline_annotation_corrected=True))
print(json.dumps(summary))
