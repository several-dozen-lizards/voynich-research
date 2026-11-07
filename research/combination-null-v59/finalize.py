from pathlib import Path
import json,shutil,html,importlib.util,random,collections
R=Path(__file__).resolve().parent
d=json.loads((R/'RESULTS.json').read_text());fixed=json.loads((R/'MULTIPLICITY-CORRECTION.json').read_text())['fixed_panel_family'];shutil.copyfile(R/'RESULTS.json',R/'RESULTS-before-fixed-family.json')
for r in d['results']:
 for p in r['patterns']:p['p_across_panels']=min(1,p['p_all_patterns_max']*fixed)
for r in d['paired']:
 for tr in ('H','F'):r[tr]['p_across_panels']=min(1,r[tr]['p_all_patterns_max']*fixed)
 r['passes_both']=r['H']['excess']>0 and r['F']['excess']>0 and max(r[t]['p_across_panels'] for t in ('H','F'))<=.05
d['fixed_multiplicity_family']=fixed;(R/'RESULTS.json').write_text(json.dumps(d,indent=2));summary={'nonempty_test_panels':d['panels'],'fixed_multiplicity_family':fixed,'selected_tests':sum(len(r['patterns']) for r in d['results']),'paired_patterns':len(d['paired']),'passes_both':sum(r['passes_both'] for r in d['paired'])};(R/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(summary)
body='<h1>Combinations beyond word frequency — v59</h1><p>'+html.escape(d['method'])+'</p><p>Final correction uses all48eligible context/orientation panels, including empty selections. Initial22nonempty-panel correction retained separately; stricter correction specified before manuscript outcomes were inspected.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><table><tr><th>Context</th><th>Phrase</th><th>H observed / null mean</th><th>F observed / null mean</th><th>Adjusted p H/F</th><th>Pass both</th></tr>'
for p in sorted(d['paired'],key=lambda p:(not p['passes_both'],-min(p['H']['excess'],p['F']['excess']))):
 vals=[' / '.join(p['context']),p['phrase'],f"{p['H']['observed']} / {p['H']['null_mean']:.2f}",f"{p['F']['observed']} / {p['F']['null_mean']:.2f}",f"{p['H']['p_across_panels']:.3f} / {p['F']['p_across_panels']:.3f}",p['passes_both']];body+='<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in vals)+'</tr>'
body+='</table><p>Failure is lack of support under this conservative screen, not proof of random text. Max raw counts have low power for rare phrases. H/F disagreement retained. This null controls broad position and within-line composition, not every exact ordinal or contextual process.</p><p><a href="RESULTS.json">Every result and failure</a> · <a href="QUALIFICATION.json">Synthetic checks</a> · <a href="PROTOCOL.json">Frozen protocol</a> · <a href="MULTIPLICITY-CORRECTION.json">Correction receipt</a></p>'
(R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Combination null v59</title><style>body{font:16px system-ui;max-width:1350px;margin:35px auto;background:#f5f2e9;color:#193c39}td,th{padding:8px;border-bottom:1px solid #bdcec4;text-align:left}p{line-height:1.6}</style>'+body,encoding='utf8')
sp=importlib.util.spec_from_file_location('owner',R/'run.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
ws=['edge','a','b',None,'c','d','last'];rng=random.Random(59)
for i in range(100):
 z=m.shuffle(ws,rng);assert z[0]=='edge' and z[-1]=='last' and z[3] is None;assert collections.Counter(z[1:3])==collections.Counter(ws[1:3]);assert collections.Counter(z[4:6])==collections.Counter(ws[4:6])
(R/'VERIFICATION.json').write_text(json.dumps({'unknown_barriers_and_edge_invariance':'pass100fixtures','frequency_conservation':'pass','fixed_family':fixed,'visual_review':'not performed'},indent=2))
