from pathlib import Path
import hashlib,html,json
R=Path(__file__).resolve().parent
data=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'))
e=lambda x:html.escape(str(x))
f=lambda x:f'{x:.4f}'
body='''<p class="muted">VOYNICH · CONDITIONAL DIRECTION TEST · v67</p><h1>Does the qo-form direction exceed frequency and position?</h1>
<p class="notice"><strong>The selected two-pair pattern does not pass the declared search correction in either reading or null.</strong> It exceeds the average shuffle, particularly in F. This retrospective result neither identifies a grammatical function nor demonstrates absence of structure.</p>
<p>Fixed stratum: bath section · hand 2 · Currier B · raw format P. Original worksheet folio f75 excluded. H/F share eligible source loci, retain separate tokenization and are alternate readings of the same manuscript.</p>
<p>Observed statistic: <code>D = prefixed-before − prefixed-after + base-after − base-before</code>, summed over <code>qokedy/kedy</code> and <code>qokeedy/keedy</code>. Positive means the noticed direction. This measures written-word arrangement, not a prefix meaning.</p>
<h2>Selected pattern under both nulls</h2><div class="scroll"><table><thead><tr><th>Reading / null</th><th>Observed D</th><th>Null mean</th><th>Central 95% null range</th><th>Raw two-sided p</th><th>Pair-search adjusted p</th><th>Four-panel adjusted p</th></tr></thead><tbody>'''
for p in data['panels']:
 x=p['noticed_result']
 body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [p['reading']+' / '+p['mode'],x['observed'],f'{x["null_mean"]:.2f}',str(x['null_95']),f(x['p_two_sided']),f(x['p_search_family']),f(x['p_four_panels'])])+'</tr>'
body+='''</tbody></table></div><p>Each panel uses 1,999 conditional shuffles plus the observed arrangement. The displayed null range describes shuffled scores, not an effect-size confidence interval. Raw p-values do not account for inspecting and choosing word pairs.</p>
<h2>What each control preserves</h2><p><strong>Exact slot (primary):</strong> locks all qol and unknown slots; exchanges other words only within the same page, line length, exact ordinal and unknown-slot mask. This preserves frequency conditional on those positions. It does not preserve every source line’s word multiset.</p>
<p><strong>Within line (sensitivity):</strong> preserves each line’s words, first/last words, every qol, and unknowns as barriers. Other words shuffle within readable interior spans. This controls broad position, but not every other word’s exact interior ordinal.</p>
<p><strong>Selection correction:</strong> within each reading, all literal qoX/X pairs present anywhere in the fixed stratum, all single- and two-pair choices, and the full inventory are considered, in both directions. A pooled-rank minP calibration corrects that family. A further factor of four covers H/F × the two nulls. This addresses the declared family, not every anchor, spelling rule or earlier research choice.</p>
<h2>Mobility and full family</h2><div class="scroll"><table><thead><tr><th>Panel</th><th>Word-form pairs</th><th>Pair subsets</th><th>Movable adjacent slots / readable adjacent slots</th><th>All movable word slots</th></tr></thead><tbody>'''
for p in data['panels']:
 m=p['mobility'];body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [p['reading']+' / '+p['mode'],len(p['pairs']),p['family_size'],str(m['movable_neighbor_slots'])+'/'+str(m['readable_neighbor_slots']),m['movable_slots']])+'</tr>'
body+='</tbody></table></div><p>Adjacent slots are unique physical token slots, so a word between two qol tokens is counted once for mobility but can contribute to both adjacent relations. Frozen slots limit sensitivity.</p>'
for tr in ['H','F']:
 p=next(p for p in data['panels'] if p['reading']==tr and p['mode']=='exact_slot')
 body+='<h2>'+tr+' · every pair, including zero and opposite-direction cases</h2><details><summary>All constituent cells and single-pair tests</summary><div class="scroll"><table><thead><tr><th>Prefixed / base</th><th>Prefixed before / after</th><th>Base before / after</th><th>D</th><th>Single-pair family-adjusted p · exact slot</th></tr></thead><tbody>'
 singles={r['pair_indices'][0]:r for r in p['records'] if len(r['pair_indices'])==1}
 for i,(pair,c) in enumerate(zip(p['pairs'],p['cells'])):
  x=singles[i];body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [' / '.join(pair),str(c['prefixed_left'])+' / '+str(c['prefixed_right']),str(c['base_left'])+' / '+str(c['base_right']),x['observed'],f(x['p_search_family'])])+'</tr>'
 body+='</tbody></table></div></details><p>Selected-pattern folio contributions: '+e(p['noticed_folio_D'])+'. Zero and negative folios are retained.</p><details open><summary>All selected-pair source occurrences and exceptions</summary>'
 for ev in p['noticed_events']:
  adverse=[]
  if ev['left'] in ('kedy','keedy'):adverse.append('base before qol: opposite the noticed direction')
  if ev['right'] in ('qokedy','qokeedy'):adverse.append('prefixed form after qol: opposite the noticed direction')
  body+='<article><p><strong>'+e(ev['locator'])+'</strong> · anchor ordinal '+e(ev['ordinal'])+' · before '+e(ev['left'])+' / after '+e(ev['right'])+'</p><p class="raw">'+' '.join('□' if w is None else '<mark>'+e(w)+'</mark>' if w in ('qol','qokedy','qokeedy','kedy','keedy') else e(w) for w in ev['tokens'])+'</p>'
  if adverse:body+='<p>'+e('; '.join(adverse))+'</p>'
  body+='</article>'
 body+='</details>'
body+='<h2>Engineering diagnostics and limits</h2><p>Before manuscript scoring, both shuffle schemes passed their frozen conservation checks. Each synthetic diagnostic had 2 flags among 20 exchangeable samples and detected 20/20 planted samples under its generator. These small diagnostics are engineering checks, not historical-text validation or a precise false-positive-rate estimate.</p><p>All single-, two-pair and whole-inventory results are retained, including failures. Raw permutation scores are saved in the four NPZ files for numerical replay. No new semantic labels were assigned. Browser visual review was not performed.</p><p><a href="RESULTS.json">All tests and exceptions</a> · <a href="PROTOCOL.json">Frozen protocol</a> · <a href="FREEZE.json">Input/method hashes</a> · <a href="QUALIFICATION.json">Diagnostics</a> · <a href="VERIFICATION.json">Verification</a> · <a href="../neighbor-patterns-v66/report.html">Original neighbour report</a></p>'
css='''<style>:root{color-scheme:light dark;--bg:light-dark(#f5f2e9,#18251f);--fg:light-dark(#203f35,#e2e9df);--sub:light-dark(#54695b,#b4c7b7);--rule:light-dark(#c0ccbd,#48604d);--fill:light-dark(#e5ebda,#2a3e2d);--mark:light-dark(#e6edb7,#526330)}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui}main{max-width:1400px;padding:30px;margin:auto}h1{font-size:32px;line-height:1.2}h2{font-size:23px;margin-top:30px}p{max-width:1100px}a{color:inherit}.muted{color:var(--sub)}.notice{padding:16px;background:var(--fill)}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid var(--rule)}.raw{font:15px/1.8 ui-monospace,monospace;overflow-wrap:anywhere}mark{background:var(--mark);color:inherit}article{border-bottom:1px solid var(--rule)}summary{cursor:pointer}details{margin:16px 0}@media(max-width:700px){main{padding:16px}}</style>'''
(R/'report.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>qol qo-form direction test · v67</title>'+css+'</head><body><main>'+body+'</main></body></html>',encoding='utf-8')
print('Report written; full tests retained in RESULTS.json')
