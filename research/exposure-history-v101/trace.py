from pathlib import Path
import ast,collections,csv,datetime,hashlib,html,json,re
R=Path(__file__).resolve().parent;P=R.parent
V=Path('C:/Users/lewis/.codex/visualizations/2026/10')
B=V/'21/01a15c3d-56da-7f02-bc15-2522dc396abd/voynich-layout'
FOLD=V/'22/01a16491-3972-7430-a33e-0da82c066bb4'
PROF=V/'22/01a16529-fd24-7d02-99e0-9a5bef58ed94/section-profiles-v1'
QODY=PROF.parent/'qody-arody-content-v1'
SETS=V/'22/01a16601-47fd-7c73-aa74-e1137076d1d5/manuscript-sets-v1'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(R/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[P/'untouched-passage-audit-v100/LOCUS-LEDGER.json',B/'run_layout.py',B/'tokens.json',B/'data/text16e6.original.evt',B/'data/Davis-hands.original.csv',SETS/'run.py',SETS/'results.json',SETS/'PROTOCOL.md',PROF/'profile.py',PROF/'profiles.json',PROF/'source-manifest.json',QODY/'analyse.py',QODY/'all-locus-occurrences.json',FOLD/'local-context-comparison.json',FOLD/'catalogue_local_sequences.py',P/'oal-boundary-check-reed-v93/OAL-EVENTS.json',P/'oal-boundary-check-reed-v93/PROTOCOL.json',P/'contrast-context-v58/RESULTS.json',P/'contrast-context-v58/build.py',P/'e-run-format-audit-reed-v95/SOURCE-ROWS-METADATA.json',P/'e-run-format-audit-reed-v95/run.py',P/'transition-maxT-qual-v98/QUALIFICATION.json',R/'trace.py']
frozen={str(p):sha(p) for p in paths}
if (R/'ARTIFACT-FREEZE.json').exists():assert load(R/'ARTIFACT-FREEZE.json')==frozen
else:save('ARTIFACT-FREEZE.json',frozen)
ledger=[x for x in load(paths[0]) if x['status']=='freshness_uncertified']
assert len(ledger)==1783
assert sha(B/'data/text16e6.original.evt')==load(P/'frequency-atlas-v48/source-manifest.json')['sources'][str(B/'data/text16e6.original.evt')]
profiles=load(PROF/'profiles.json')
profile_scopes={(x['tr'],x['section']) for x in profiles if x['scope']=='all'}
assert all((x['reading'],x['section']) in profile_scopes for x in ledger)
# Reconstruct only historical parser membership; never call a model, statistic or shuffle.
# Old parser excludes <3-slot lines. Do not silently equate raw P with that population.
ns={'ROOT':B,'csv':csv,'re':re,'Counter':collections.Counter,'hashlib':hashlib}
nodes=[n for n in ast.parse((B/'run_layout.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name in ['parse','split']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'historical-metadata-parser','exec'),ns)
membership={};historic_counts={}
for tr in ('H','F'):
    records,audit=ns['parse'](tr)
    if tr=='H':assert records==load(B/'tokens.json')
    membership[tr]={x['loc'] for x in records}
    historic_counts[tr]=len(membership[tr])
historical_sets=load(SETS/'results.json')
for tr in ('H','F'):assert historical_sets['results'][tr+'_all_P']['lines']==historic_counts[tr]
erun={(x['reading'],x['locator']) for x in load(P/'e-run-format-audit-reed-v95/SOURCE-ROWS-METADATA.json')}
qody={(x['tr'],x['locator']) for x in load(QODY/'all-locus-occurrences.json') if x['tr'] in ('H','F')}
oal={(x['reading'],x['locator']) for x in load(P/'oal-boundary-check-reed-v93/OAL-EVENTS.json') if x['reading'] in ('H','F')}
fold={(x['transcriber'],x['locator']) for x in load(FOLD/'local-context-comparison.json')['rows'] if x['transcriber'] in ('H','F')}
ctx=set()
for c in load(P/'contrast-context-v58/RESULTS.json')['contrasts']:
    for g in c['groups']:
        ctx.update((g['transcription'],z['locator']) for z in g['events'])
out=[]
for x in ledger:
    key=(x['reading'],x['locus'])
    z=dict(x)
    z['historical_evidence']=['section_profiles_all_row_selector']
    if x['locus'] in membership[x['reading']]:z['historical_evidence'].append('all_P_neighbor_computation_membership')
    for tag,keys in [('e_run_saved_row_metadata',erun),('qody_arody_saved_context',qody),('oal_saved_context',oal),('f68r3_saved_passage',fold),('v58_saved_neighbors',ctx)]:
        if key in keys:z['historical_evidence'].append(tag)
    z['human_inspection_of_this_entire_locus']='not inferred from aggregate processing'
    z['direct_sh_qok_direction_score_in_other_chats']='not established by the mapped receipts'
    z['reserve_admission']='CLOSED: no protected sequence reserve established'
    if x['numbered_folio']=='f73':z['hand_conflict']='Local Davis metadata hand3; published-description hand4 conflict retained. No reassignment.'
    out.append(z)
groups=collections.defaultdict(list)
for x in out:groups[(x['section'],x['hand'],x['variety'],x['format'],x['reading'])].append(x)
summary=[]
for k,rr in sorted(groups.items()):
    summary.append(dict(zip(['section','hand','variety','format','reading'],k),lines=len(rr),pages=sorted({x['page'] for x in rr}),evidence_counts=dict(collections.Counter(t for x in rr for t in x['historical_evidence'])),reserve_admitted=0))
save('LOCUS-EXPOSURE.json',out);save('STRATA-EXPOSURE.json',summary)
excerpts=load(R/'HISTORY-EXCERPTS.json')
needles=[('01a15c3d-56da-7f02-bc15-2522dc396abd','', 'Original full-paragraph spelling/layout development'),('01a16529-fd24-7d02-99e0-9a5bef58ed94','section-profiles-v1','All-section word-form profiles'),('01a16529-fd24-7d02-99e0-9a5bef58ed94','qody-arody-content-v1','Saved plant-label and paragraph contexts'),('01a16601-47fd-7c73-aa74-e1137076d1d5','manuscript-sets-v1','All-P neighbour shared-beginning test'),('01a16491-3972-7430-a33e-0da82c066bb4','LOCAL-SEQUENCE-CATALOGUE','f68r3 full local sequence catalogue'),('01a160c2-56f0-7303-b3bf-ed8594c6ec40','section-controls-v49','Controlled recipes feature comparisons'),('01a160c2-56f0-7303-b3bf-ed8594c6ec40','contrast-context-v58','Selected recipes full-line neighbours'),('01a16ab3-be61-74b2-95d2-d38c0ba2a642','f86v5','Rose-obverse literal context identified'),('01a16ab3-be61-74b2-95d2-d38c0ba2a642','e-run-format-audit','Recipes/label e-run investigation')]
timeline=[]
for id,needle,claim in needles:
    matches=[x for x in excerpts if x['thread_id']==id and x['role']=='assistant' and x['phase']=='final_answer' and (needle.lower() in x['text'].lower())]
    if matches:
        x=min(matches,key=lambda x:x['timestamp']);timeline.append(dict(claim=claim,thread_id=id,timestamp=x['timestamp'],session_path=x['path'],jsonl_line=x['jsonl_line'],excerpt=x['text'],evidence_limit='Historical statement; mapped scope/event membership separately verified.'))
    else:timeline.append(dict(claim=claim,thread_id=id,status='No final-message filename match; use artifact receipt and complete history excerpts, not an invented timestamp.'))
save('TIMELINE.json',timeline)
bygroup=[]
for k,rr in sorted(collections.defaultdict(list,{}).items()):pass
gg=collections.defaultdict(list)
for x in out:gg[(x['section'],x['hand'],x['variety'],x['reading'])].append(x)
for k,rr in sorted(gg.items()):bygroup.append(dict(zip(['section','hand','variety','reading'],k),lines=len(rr),neighbor_membership=sum('all_P_neighbor_computation_membership' in x['historical_evidence'] for x in rr),saved_context_rows=sum(any(t in x['historical_evidence'] for t in ['qody_arody_saved_context','oal_saved_context','f68r3_saved_passage','v58_saved_neighbors']) for x in rr),e_run_rows=sum('e_run_saved_row_metadata' in x['historical_evidence'] for x in rr)))
save('SUMMARY.json',bygroup)
q=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert q['status']=='FAIL' and q['robustness_banks_not_run']==[2,3]
for p,h in frozen.items():assert sha(Path(p))==h,p
sf=load(R/'SCAN-FREEZE.json')
for x in sf['session_prefixes']:
    with Path(x['path']).open('rb') as f:b=f.read(x['bytes'])
    assert hashlib.sha256(b).hexdigest()==x['sha256']
assert len({(x['reading'],x['locus']) for x in out})==1783
save('VERIFICATION.json',dict(frozen_artifacts='PASS',session_prefixes='PASS',source_identity='PASS',H_historical_parser_saved_token_replay='PASS',HF_historical_all_P_line_count_replay='PASS',locus_count=1783,strata=len(summary),distinct_readings_hands_formats='PASS',new_order_score='NOT COMPUTED',candidate_power='NOT RUN',reserve_admitted=0,v98='FAIL unchanged; banks2/3 remain unrun',visual_review='not performed'))
save('RESULTS.json',dict(status='NO GENUINE RESERVE ESTABLISHED',candidate_power='CLOSED / NOT RUN',scoring='CLOSED / NOT RUN',source_units=1783,profile_scope=1783,neighbor_membership=sum(x['neighbor_membership'] for x in bygroup),saved_context_rows=sum(x['saved_context_rows'] for x in bygroup),interpretation='Other chats demonstrate actual feature processing and neighbor exploration beyond atlas availability. This does not imply every locus was viewed by a human or every locus had a sh/qok directional score. No protected reserve has emerged.',limits='Eight local history byte-prefixes; two ChatGPT chats. Reference-only ChatGPT assistant contents and external Claude/deleted/unavailable activity remain gaps.'))
e=html.escape
def table(h,rs):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in r)+'</tr>' for r in rs)+'</tbody></table></div>'
body='<p>VOYNICH · CROSS-CONVERSATION EXPOSURE TRACE · v101</p><h1>What happened to the uncertified passages?</h1><p><strong>No genuine protected passage reserve was established. Power and scoring remain CLOSED.</strong> This audit reads historical evidence; it does not calculate a new order score, inferential p-value or power estimate. v97/v98 failures remain intact.</p>'
body+='<h2>Availability was only the first layer</h2><p>The other conversations establish prior feature computation and neighbour exploration, not merely access to an atlas. All 1,783 v100-uncertified H/F reading-loci fall within the all-row selector of the earlier section-profiles script. Its saved results include their sections in both readings. This is selector scope, not proof that every line supplied a readable token or was seen by a human.</p><p>The all-P shared-beginning experiment used the original parser, which excludes short lines and some tokens. Only membership reconstructed under that parser is marked neighbour-exposed below. Exact saved contexts are recorded separately. None of these receipts alone establishes an earlier sh→qok direction test in every remaining section.</p>'
body+=table(['Section','Local hand','Variety','Reading','Loci','Historical all-P neighbour population','Saved focal/context rows','E-run row metadata'],[[x['section'],x['hand'],x['variety'],x['reading'],x['lines'],x['neighbor_membership'],x['saved_context_rows'],x['e_run_rows']] for x in bygroup])
body+='<p>Columns overlap. Saved contexts here cover the mapped qody/arody and oal events, f68r3 passages and v58 neighbours; they are a documented lower bound, not an exhaustive count of all historical inspection. Aggregate old results are not retroactively split into separate hand-specific scores. f73r/v retain local hand3 and the competing hand4 description; no reassignment was made.</p>'
body+='<h2>Conversation trail</h2><p><strong>Summarize VONICH experiments:</strong> section-profiles-v1 computed H/F section-wide word forms, including Astronomy/Astrology, Recipes and Rose obverse. Its qody/arody branch saved full contexts and inspected f88v plant-associated labels.</p><p><strong>Create a Voynich-style cataloguing:</strong> manuscript-sets-v1 evaluated immediate-neighbour shared beginnings across all retained P text in H and F, beyond its three narrower substitution cohorts. Rose-obverse and recipe paragraphs therefore were not protected from neighbour exploration wherever retained by its parser.</p><p><strong>Review Voynich fold-out clues:</strong> the f68r3 catalogue enumerated local words, additions, neighbour frames and sequences. These are H/U/V readings. Missing F is retained; U/V do not become F evidence.</p><p><strong>Review Voynich handoff:</strong> controlled Recipes hand1/A feature screens and v58 concordances inspected full-line neighbours. The oal seam audit also reached Rose obverse. The chat’s later synthetic qualification work does not reopen an old passage reserve.</p><p><strong>Explore Voynich astrology phonetics:</strong> oal contexts explicitly include f86v5 in H and F; e-run-format-v95 saved paragraph/label coverage and feature events, including Recipes. Later qualifications or sparse results do not undo that exposure.</p><p><strong>Analyze Voynich manuscript</strong> and <strong>Resume Voynich analysis handoff:</strong> original paragraph-level parsing/fitting and its handoff precede these later branches. <strong>Summarize Voynich research attempts</strong> reused the exposed bath/starred panels; its later work supplies no reserve for these sections.</p><p><strong>Voynich Decipherments Explained:</strong> accessible user messages quote f68r3 passages; several assistant replies are reference placeholders, so their contents remain unaudited. <strong>Assess Astrolabe Usefulness:</strong> the accessible chat discusses a photographed instrument and supplies no Voynich passage-reserve evidence.</p>'
body+='<h2>Chronological receipts</h2>'+table(['UTC','Historical step','Session JSONL line'],[[x.get('timestamp','unmatched filename'),x['claim'],x.get('jsonl_line','see artifact')] for x in sorted(timeline,key=lambda x:x.get('timestamp','z'))])
body+='<h2>Every stratum stays separate</h2>'+table(['Section','Hand','Variety','Format','Reading','Loci','Evidence counts'],[[x['section'],x['hand'],x['variety'],x['format'],x['reading'],x['lines'],json.dumps(x['evidence_counts'],sort_keys=True)] for x in summary])
body+='<h2>Decision and remaining uncertainty</h2><p>No saved declaration establishes a protected H/F sequence reserve in these sections. Retrospective folds, a different hand, an alternate transcription, and image-feature holdouts do not supply one. Passage-level target non-use is still not proven either way where only aggregate feature scopes are recorded. The defensible outcome is no admission, not a claim that every passage was consciously read.</p><p>This is bounded to the accessible histories and linked receipts. External Claude work, missing assistant contents and deleted/unavailable records could add exposure or custody evidence. A credible independently documented protected unit list could change admission. Until then no candidate power run, sh/qok test or manuscript rescore is authorized by these audit findings.</p><p><a href="PROTOCOL.json">Audit rules</a> · <a href="SCAN-FREEZE.json">Conversation prefix freeze</a> · <a href="ARTIFACT-FREEZE.json">Artifact hashes</a> · <a href="TIMELINE.json">Timestamped messages</a> · <a href="HISTORY-EXCERPTS.json">History excerpts</a> · <a href="LOCUS-EXPOSURE.json">Every locus</a> · <a href="STRATA-EXPOSURE.json">Every stratum</a> · <a href="VERIFICATION.json">Verification</a></p><p>Numerical/source review only; browser appearance unreviewed. H/F are dependent alternate readings.</p>'
style='<style>body{max-width:1450px;margin:auto;padding:28px;background:#f5f2e9;color:#203f35;font:16px/1.55 system-ui}h1{font-size:32px}h2{margin-top:30px}table{border-collapse:collapse;width:100%}th,td{padding:9px;text-align:left;vertical-align:top;border-bottom:1px solid #bac9bb}.scroll{overflow:auto}a{color:inherit}</style>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cross-conversation exposure history · v101</title>'+style+'<main>'+body+'</main></html>',encoding='utf-8')
print(json.dumps(dict(summary=bygroup,status='NO GENUINE RESERVE ESTABLISHED',power='CLOSED',scoring='CLOSED')))
