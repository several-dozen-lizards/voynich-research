from pathlib import Path
import json,hashlib,collections,sys,html
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 protocol=dict(scope='Exact residual retrieval only; no inferred morphology, functions, phonetic values or name fitting.',anchor='oalcheg',hypotheses={'whole':'oalcheg','o + core':'alcheg','oa + core':'lcheg','oal + core':'cheg'},why_three='User proposes o and perhaps next letter. Recovered Review Voynich fold-out clues also explicitly compares cheol/oalcheol, motivating separate oal-removal sensitivity. These alternatives stay distinct.',candidate_rule='For every fully readable token in all18 readings, remove0,1,2,3 initial EVA characters and record exact matches to each frozen residual, preserving removed prefix/full token. No edit distances, suffix changes, vowel removal, sound-driven normalization or unknown repairs. Character lengths here are operational; letters are EVA symbols, not established manuscript glyphs.',exceptions='Every selected locus retains all readings and unknown slots. Original v86 whole-token findings stay unchanged; do not reinterpret exact raw uniqueness as content uniqueness.',limits='Previously exposed corpus and observed candidate pairs; descriptive search only. Chance shared tails, unrelated words and incompatible segmentations remain possible. Prefix deletion results cannot establish function. No claim of support from absent/untested comparisons.')
 save('PROTOCOL.json',protocol);save('PRE-SEARCH-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S]});print('Prefix hypotheses frozen.')
else:
 for p,h in json.loads((R/'PRE-SEARCH-FREEZE.json').read_text()).items():assert sha(Path(p))==h
 rows=json.loads(S.read_text());targets={'whole':'oalcheg','o + core':'alcheg','oa + core':'lcheg','oal + core':'cheg'};events=[];locs=set()
 for x in rows:
  for j,w in enumerate(x[9]):
   if not w:continue
   for n in range(4):
    if n>=len(w):continue
    for hypothesis,core in targets.items():
     if w[n:]==core:
      events.append(dict(hypothesis=hypothesis,core=core,removed_prefix=w[:n],full_word=w,reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],token_index=j,raw=x[10]));locs.add(x[8])
 alts={l:[dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],tokens=x[9],raw=x[10]) for x in rows if x[8]==l] for l in sorted(locs)}
 summary=[]
 for hyp,core in targets.items():
  a=[x for x in events if x['hypothesis']==hyp]
  summary.append(dict(hypothesis=hyp,core=core,physical_loci=len({x['locator'] for x in a}),forms=sorted({x['full_word'] for x in a}),prefixes=sorted({x['removed_prefix'] for x in a}),reading_events=len(a)))
 save('EVENTS.json',events);save('ALTERNATES.json',alts);save('SUMMARY.json',summary)
 assert all(e['full_word']==e['removed_prefix']+e['core'] for e in events)
 for l,a in alts.items():assert len(a)==sum(x[8]==l for x in rows)
 save('VERIFICATION.json',dict(exact_reconstruction=True,all_alternate_rows_preserved=True,functions_assigned=0,sounds_fitted=0))
 e=lambda x:html.escape(str(x))
 body='<h1>oalcheg · prefix sensitivity</h1><p>The opening may be functional. Raw-word uniqueness does not establish uniqueness of possible content. This appendix preserves competing subdivisions rather than selecting a root.</p><p>Recovered conversation: Review Voynich fold-out clues compares cheol/oalcheol in H/U (V cheal at the shorter-word location), and keol/okeol with disputed readings. Those are candidate subdivisions, not established operators. The prior astro-cycles-v82 ot/ok/yk stripping test was negative and did not establish their functions.</p><table><tr><th>Hypothesis</th><th>Residual</th><th>Physical loci</th><th>Full forms found</th></tr>'
 for x in summary:body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [x['hypothesis'],x['core'],x['physical_loci'],', '.join(x['forms'])])+'</tr>'
 body+='</table><p>All candidate words receive the same0–3 initial-EVA-character retrieval. Shared remaining strings are not proof of shared meaning or morphological boundaries. No sound fitting, historical names or functional assignments.</p>'
 for l,a in alts.items():body+='<details><summary>'+e(l)+' · '+e(' | '.join(x['reading']+': '+x['raw'] for x in a))+'</summary><pre>'+e(json.dumps([x for x in events if x['locator']==l],indent=2))+'</pre><pre>'+e(json.dumps(a,indent=2))+'</pre></details>'
 for n in ['PROTOCOL.json','EVENTS.json','ALTERNATES.json','SUMMARY.json','VERIFICATION.json']:body+=f'<p><a href="{n}">{n}</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>oalcheg prefix sensitivity v87</title><style>body{font:17px system-ui;max-width:1050px;margin:40px auto;padding:0 20px;background:#f5f2e9;color:#193c39;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #abc;padding:8px;text-align:left}pre{white-space:pre-wrap}details{padding:8px;border-bottom:1px solid #abc}</style>'+body,encoding='utf-8')
 save('SHA256SUMS.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
 print(json.dumps(summary,indent=2))
