from pathlib import Path
import hashlib,html,json
R=Path(__file__).resolve().parent
load=lambda n:json.loads((R/n).read_text(encoding='utf8'))
summary=load('SUMMARY.json');pages=load('PAGE-RESULTS.json');examples=load('INFORMATIVE-EXAMPLES.json')
def brief(x):
    return f"{x['positive_pages']}/{x['eligible_pages']} pages positive; {x['negative_pages']} reverse; {x['informative_cells']} informative cells"
def label(x):return f"{x['transcriber']} {x['A']} vs {x['B']} / {x['position']} / {x['view']}"
lines=['Gallows and opening lines: exact-frame controls, v105',
'Result: the descriptive plume-class opening-line preference survives stricter local matching; p supplies most support. f has matching examples, but the reused test subset is too sparse to validate an f-specific rule.',
'', 'METHOD',
'H/F strict readable P-locus events from v102; unknown and comma-marked slots never promoted. Words with exactly one k/t/f/p and no cth/ckh/cph/cfh compound only. Mask that one character and hold every other character fixed.',
'Match exact page, hand, Currier classification, section, masked word frame and original word index. First words compare paragraph opening versus continuation starts. Other words compare the same nonzero word index between opening and continuation lines. Also require exact original line length in the frozen sensitivity. Complete source lines and alternate H/F readings saved.',
'The original v1 numbered-folio allocation is reused. All training panel directions were frozen before calculating test panels. These pages were historically exposed: this is retrospective consistency, not untouched prediction. No f57v model is fitted.',
'Each informative cell has both positions and both classes. Within-page gaps use harmonic exposure weights; eligible pages receive equal weight. Sparse, often one-token cells can have 100 percentage-point differences. Such numbers are conditional on eligibility and are not all-word probabilities, calibrated effect sizes, statistical significance or predictive accuracy.',
'', 'NON-FIRST WORDS: SAME WORD POSITION, OPENING LINE VERSUS CONTINUATION',
'Reading / contrast | training | reused test']
for s in summary:
    if s['view']=='main' and s['position']=='other' and (s['A'],s['B']) in [('fp','kt'),('f','kt'),('p','kt')]:
        lines.append(f"{s['transcriber']} {s['A']} vs {s['B']} | {brief(s['training'])} | {brief(s['test'])}")
lines += ['', 'SENSITIVITIES',
'With exact line length added, pooled fp/kt remains positive on 10/10 H training pages (11 cells), 12/12 F (18 cells); reused test H 1/1 page and F 3/3 pages. This stronger control sharply reduces support. f/kt alone has 2 eligible training pages per reading and zero test pages. Requiring agreeing H/F structural opening flags also preserves the pooled direction. H/F are dependent readings, not replications.',
'The word-first analysis is much sparser: pooled fp/kt training H 6/7 pages positive and F 7/10; test H zero informative cells, F one. f/kt has zero H training cells, and only one F training cell, which is reversed. Thus this audit supports a line-wide association more clearly than a separate exact-first-word rule.',
'', 'CONCRETE f EXAMPLES',
'H and F, f95r1, word 3: opening f95r1.P.1 ofaiin versus continuation f95r1.P.10 okaiin. Identical page and remaining word aiin with leading o; internal f/k substitution.',
'H, f50r, word 3: opening f50r.P.1 olfchedy versus continuation f50r.P.6 olkchedy. F separates the latter as ol.kchedy, so F does not supply the same frame at the same word index. Do not count this as shared evidence.',
'H/F, f108r, word 8: opening ofal and okal versus continuation otal twice. Mixed opening forms retained; no deterministic rewrite claim.',
'The only f-specific test cell is F f113v, word 10: opening ofar plus okar versus continuation otar/okar/otar. H reads the focal opening word ofchr rather than F ofar; H has no eligible test cell. This is reading-sensitive, not confirmed transfer.',
'', 'REVERSE CASES',
'H test f94v, word 4: opening f94v.P.5 okchdy versus continuation f94v.P.6 opchdy. F reads onchdy on the continuation line; no matched gallows contrast there. The H reversal stays in the result.',
'F training pooled non-first reversals: f105v and f79v. First-word reversals include H f75r and F f114r/f75r/f82v. All cells, missing-position cases, single-class cases and source passages remain saved.',
'', 'WHAT THIS ADDS',
'Raw opening enrichment is not only a difference in which entire words appear. In some same-page, same-index, otherwise identical written forms, the gallows class changes with opening-line context. Both f and p have such examples. Different meaning or syntax could still influence the variants; identical frames do not establish equivalent words or allographs.',
'A candidate line-context writing convention is a better-supported description than a generic first-sign-after-boundary rule. It may extend well into the opening line; exact word index is matched. This audit does not estimate a distance-decay curve or establish a causal mechanism.',
'The distinction between plumed and unplumed forms and the choice f versus p are separate questions. Pooling f+p cannot explain f57v slot9 f/f/p/p, because all four copies remain in the same plumed class. No diagram transfer or new ring divider is established.',
'', 'VALIDATION AND RECEIPTS',
'Nine arithmetic/frame checks passed. Independent bounded-memory replay recounted all 389,925 cells and recomputed all 192 train/test panels, including controls and unsupported cells. Exact counts, frames, positions and page gaps agree. Input hash and training-freeze checks pass. These are engineering checks, not statistical-null qualification.',
'Files: PROTOCOL.json; INPUT-FREEZE.json; TRAINING-FREEZE.json; SUMMARY.json; PAGE-RESULTS.json; INFORMATIVE-EXAMPLES.json; SOURCE-EXCERPTS.json; TRAINING-RESULTS.json; TEST-RESULTS.json; INDEPENDENT-VERIFICATION.json. The two full result arrays are large: extract.py reads them one panel at a time; do not load the training array in the 32-bit Python process.',
'Reproduce: python run.py, python extract.py, python verify.py, python publish.py. All scripts resolve their own folder. No prior experiment files modified.'
]
(R/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
def table(ss):
    return '<div class="scroll"><table><tr><th>Reading / contrast</th><th>Training pages positive</th><th>Test pages positive</th><th>Train / test cells</th></tr>'+''.join(
        f"<tr><td>{html.escape(s['transcriber']+' '+s['A']+'/'+s['B'])}</td><td>{s['training']['positive_pages']}/{s['training']['eligible_pages']}</td><td>{s['test']['positive_pages']}/{s['test']['eligible_pages']}</td><td>{s['training']['informative_cells']} / {s['test']['informative_cells']}</td></tr>" for s in ss)+'</table></div>'
main=[s for s in summary if s['view']=='main' and s['position']=='other' and (s['A'],s['B']) in [('fp','kt'),('f','kt'),('p','kt')]]
all_panels=''.join('<details><summary>'+html.escape(label(s))+'</summary><pre>'+html.escape(json.dumps(s,indent=2))+'</pre></details>' for s in summary)
example_rows=''.join('<tr><td>'+html.escape(x['transcriber']+' '+x['key'][0])+'</td><td>'+str(x['key'][5]+1)+'</td><td>'+html.escape(x['key'][4])+'</td><td>'+html.escape(', '.join(z[2]+' ['+z[0]+']' for z in x['opening_events']))+'</td><td>'+html.escape(', '.join(z[2]+' ['+z[0]+']' for z in x['continuation_events']))+'</td></tr>' for x in examples if x['A']=='f')
body=''.join('<p>'+html.escape(s)+'</p>' for s in lines[lines.index('SENSITIVITIES')+1:] if s)
doc='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gallows and opening lines · v105</title><style>body{max-width:1120px;margin:48px auto;padding:0 24px;background:#f8f5ed;color:#213b37;font:17px/1.65 system-ui}h1{font-size:43px;line-height:1.15}h2{margin-top:40px}.kicker{font-size:13px;letter-spacing:.12em;color:#21695f;font-weight:700}.finding{background:#dfebe3;border-left:5px solid #226b60;padding:20px}table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #cdd8cf}th{font-size:14px}td{font-size:15px}.scroll{overflow:auto}p{max-width:970px}a{color:#196b61}details{margin:10px 0;border-top:1px solid #d0d9d0;padding:10px}summary{cursor:pointer}pre{white-space:pre-wrap;font-size:13px}.limit{color:#67552e}</style><div class="kicker">V105 · EXACT-FRAME MATCHING · RETROSPECTIVE</div><h1>The opening-line preference<br>survives word-frame controls.</h1><p class="finding">Both f and p have same-page, same-word-position examples against k/t, with every other letter held fixed. p provides most of the support. f-specific test evidence remains sparse and reading-sensitive.</p><p>Only words with one non-benched gallows are eligible. Match page, hand, Currier, section, exact masked word and exact original word index. Compare paragraph-opening lines with continuation lines; first words are analyzed separately.</p><h2>Words after the first word</h2>'''+table(main)+'''<p class="limit">Denominators are eligible pages, often contributing just one small matched cell. H/F are alternate readings. Reused test folios are disjoint from training but historically exposed. These fractions are descriptive consistency, not significance or prediction accuracy.</p><h2>Every informative f-specific example</h2><div class="scroll"><table><tr><th>Reading / page</th><th>Word</th><th>Exact frame</th><th>Opening-line forms</th><th>Continuation forms</th></tr>'''+example_rows+'''</table></div><h2>Interpretation, sensitivities and failures</h2>'''+body+'''<h2>All 96 fixed panels</h2><p>Each includes both training and test results. Zero-support panels and reverse cases remain visible.</p>'''+all_panels+'''<p><a href="REPORT.txt">Plain-text report</a> · <a href="SUMMARY.json">Summary data</a> · <a href="INFORMATIVE-EXAMPLES.json">Examples</a> · <a href="SOURCE-EXCERPTS.json">Original and alternate source lines</a> · <a href="INDEPENDENT-VERIFICATION.json">Independent replay</a></p>'''
(R/'report.html').write_text(doc,encoding='utf8')
# Local-link integrity, without claiming browser-rendered appearance was reviewed.
import re
links=re.findall(r'href="([^"]+)"',doc)
assert all((R/l).is_file() for l in links)
(R/'DELIVERY-VERIFICATION.json').write_text(json.dumps({'all_local_report_links_exist':True,'link_count':len(links),'html_appearance':'Not browser-reviewed'},indent=2),encoding='utf8')
(R/'SHA256SUMS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'},indent=2),encoding='utf8')
print('Published report.html and REPORT.txt; all local links resolve.')
