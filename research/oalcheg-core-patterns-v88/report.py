from pathlib import Path
import json,math,hashlib,html,collections
R=Path(__file__).resolve().parent
def load(n):return json.loads((R/n).read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=lambda x:html.escape(str(x))
results=load('ANCHOR-RESULTS.json');types=load('ALL-PEER-TYPES.json');models=load('MODELS.json');rows=load('ALL-READINGS.json');lookup={(x['job'],x['view'],x['rule']):x for x in models}
maxerr=0
for x in results:
 m=lookup[x['job'],x['view'],x['rule']];c={(p['left'],p['right']):p['count'] for p in m['pair_counts']};a=set(m['alphabet']);u=[v if v in a else '?' for v in x['anchor_units']]
 value=-sum(math.log((c.get((p,q),0)+.5)/(m['totals'].get(p,0)+.5*len(a))) for p,q in zip(['^']+u,u+['$']))/(len(u)+1)
 maxerr=max(maxerr,abs(value-x['surprise']));assert abs(value-x['surprise'])<1e-12
 peers=[t for t in types if (t['job'],t['view'],t['rule'])==(x['job'],x['view'],x['rule']) and t['units']!=x['anchor_units'] and len(t['units'])==len(x['anchor_units']) and t['training_count']==x['training_anchor_count']]
 assert len(peers)==x['peer_types']
 pct=(sum(t['surprise']<value-1e-12 for t in peers)+.5*sum(abs(t['surprise']-value)<=1e-12 for t in peers))/len(peers) if len(peers)>=5 else None
 assert pct==x['percentile']
for n in ['PRE-SCORE-FREEZE.json','QUALIFICATION-FREEZE.json']:
 for p,h in load(n).items():assert sha(Path(p))==h
readingnotes=dict(anchor='H/K/V/U all oalcheg; this agreement concerns one source location, not independent sample replication. F absent. U/K do not have comparable six-sign coverage for the zodiac baseline; their original target rows stay visible.',linked_core_examples=['f39r: H okalcheg, C okal.cheg, F/U okalchem','f103r: H lcheg versus F lchem','f67v1 radial text: H/U/V ypcheg'],interpretation='No m/y repair is applied to the agreed anchor. g/m differences elsewhere remain a reason to inspect the written ending before treating a recurring stem as secure.')
save('READING-NOTES.json',readingnotes)
verification=dict(anchor_results_recomputed=len(results),peer_sets_and_percentiles_recomputed=True,max_score_difference=maxerr,raw_v82_regression=load('RAW-REGRESSION.json'),frozen_inputs_unchanged=True,readings_separate=True,sounds_fitted=0,historical_names_tested=0,visual_QA='Report appearance unreviewed; no local-file browser preview attempted because prior policy rejected it.')
save('VERIFICATION.json',verification)
main=[x for x in results if x['job'].startswith('zodiac') and x['rule'] in ['raw','literal_o','literal_oa','literal_oal']]
summary=dict(conclusion='Prefix removal does not generally eliminate model-relative atypicality. alcheg/lcheg retain high matched zodiac ranks, while cheg is view/reading-sensitive. Detached-star reference samples lack g and are too sparse for robust core ranking. No function, phonetic status or name inferred.',literal_zodiac=main,terminal_transition_observation='Training e->g (character view) is absent in both H/V zodiac baselines for raw/literal transformations. All proposed cores retain g. H raw training g count3; V4. Detached f68r1/f68r2 H/U/V each contain zero g in their S label training arms.',verification=verification)
save('RESULTS.json',summary)
def cell(x):return ('— ('+str(x['peer_types'])+' peers)') if x['percentile'] is None else f'{100*x["percentile"]:.1f} ({x["peer_types"]})'
def get(job,view,rule):return next(x for x in results if (x['job'],x['view'],x['rule'])==(job,view,rule))
rules=['raw','literal_o','literal_oa','literal_oal'];names={'raw':'No removal','literal_o':'Remove literal o-','literal_oa':'Remove literal oa-','literal_oal':'Remove literal oal-','first_1':'Remove first unit everywhere','first_2':'Remove first2 units everywhere','first_3':'Remove first3 units everywhere'}
body='<h1>oalcheg and candidate cores · star-label comparison</h1><p class="lede">The opening is not the sole source of atypical spelling. Shorter cores remain candidates, but their rankings depend on the segmentation, transcription and reference labels.</p>'
body+='<p>Rules were frozen before the transformed scores. The original word and prior raw results were already exposed. All rankings are descriptive percentiles among exact-length / exact-training-frequency peer types, not p-values, confidence levels or evidence of phonetic writing.</p>'
body+='<h2>1 · Zodiac figure/star labels</h2><p>Train on the six other surviving sign identities assigned local hand4; exclude both Aries and both Taurus panels. H and V trained separately, as in v82. H209 / V194 original readable training tokens. Every eligible training and comparison token receives the same transformation. Literal removal changes only words beginning with that exact opening.</p><p>Cells show <b>percentile (number of other matched types)</b>, minimum five peers. A100 means above all available peers, sometimes only a handful.</p><table><tr><th>Rule</th><th>Candidate</th><th>H characters</th><th>H groups</th><th>V characters</th><th>V groups</th></tr>'
for rule in rules:
 x=get('zodiac_H','characters',rule);body+='<tr><td>'+e(names[rule])+'</td><td><b>'+e(x['anchor'])+'</b></td>'+''.join('<td>'+cell(get('zodiac_'+rd,v,rule))+'</td>' for rd,v in [('H','characters'),('H','groups'),('V','characters'),('V','groups')])+'</tr>'
body+='</table><p><b>alcheg</b> stays high, although V character rank is88.9 rather than the old90 display cutoff. <b>lcheg</b> ranks above every matched peer in all four views. <b>cheg</b> is unstable: H87.5–90.0, V57.1–100.0, with only5–10 peers. Those differences do not select a root.</p>'
body+='<h2>2 · Equal-width sensitivity</h2><p>As a broader alternative, remove the first1/2/3 units from every label, regardless of the initial symbols. Units are EVA characters or fixed longest ch/sh/cth/ckh/cph/cfh groups. This avoids giving only the candidate permission to lose its opening, but assumes a uniform prefix width that is not established. Empty residues are excluded with counts preserved.</p><table><tr><th>Rule</th><th>Candidate</th><th>H characters</th><th>H groups</th><th>V characters</th><th>V groups</th></tr>'
for rule in ['first_1','first_2','first_3']:
 x=get('zodiac_H','characters',rule);body+='<tr><td>'+e(names[rule])+'</td><td>'+e(x['anchor'])+'</td>'+''.join('<td>'+cell(get('zodiac_'+rd,v,rule))+'</td>' for rd,v in [('H','characters'),('H','groups'),('V','characters'),('V','groups')])+'</tr>'
body+='</table><p>These sensitivities retain high ranks too. Peer sets and learned distributions change with removal, so percentile differences are not a calibrated measurement of a prefix effect. All transformed-string collisions are preserved in MODELS.json; collapsed forms are counted as one peer type.</p>'
body+='<h2>3 · What remains unusual?</h2><p>Under the H/V zodiac character models, o itself is a common beginning. The full word contains a rare o→a transition and unseen l→c and e→g transitions. Grouping ch changes l→c into l→ch; it does not turn the written pattern into phonemes. Removing o or oa leaves the l/ch and e/g junctions. Removing oal leaves e→g as an unseen transition in both readings. Thus the remaining unusualness is not simply proof of an unusual proper-name root.</p><table><tr><th>Reading / rule</th><th>Transition contributions to total surprise (natural-log units)</th></tr>'
for rd in ['H','V']:
 for rule in ['raw','literal_o','literal_oa','literal_oal']:
  x=get('zodiac_'+rd,'characters',rule);text='; '.join(f'{c["left"]}→{c["right"]}: {c["surprise"]:.2f} [training count {c["training_pair_count"]}]' for c in x['contributions'])
  body+=f'<tr><td>{rd} · {e(rule)}</td><td>{e(text)}</td></tr>'
body+='</table><p>These are additive model-score components, not causal percentages of linguistic unusualness. The written g occurs3 times in H zodiac training and4 times in V; all proposed cores keep it.</p>'
body+='<h2>4 · Detached astronomical star labels</h2><p>Compare separately with f68r1/f68r2 S labels:53 physical loci, H/U/V kept separate. Train one page and rank against transformed types on the other; repeat the reverse direction. These small models contain only20–30 readable training tokens. <b>No g occurs on either reference page in H/U/V</b>; every candidate therefore includes an unseen symbol mapped to the explicit unknown bucket. Core rankings here are sparse, model-sensitive diagnostics, not matched replication of zodiac findings. f68r3 cluster/connector labels are excluded from this individual-star cohort.</p>'
for job in sorted({x['job'] for x in results if x['job'].startswith('stars')}):
 body+=f'<details><summary>{e(job)} · both views, all seven transformations</summary><table><tr><th>Rule</th><th>Core</th><th>View</th><th>Rank (peers)</th><th>Training tokens</th><th>Unknown units</th></tr>'
 for x in results:
  if x['job']==job:body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [x['rule'],x['anchor'],x['view'],cell(x),x['training_tokens'],x['unknown_units']])+'</tr>'
 body+='</table></details>'
body+='<h2>5 · Alternate readings and interpretation</h2><p>'+e(readingnotes['anchor'])+'</p><p>Linked non-star body-text forms remain H okalcheg versus C okal.cheg and F/U okalchem on f39r, and H lcheg versus F lchem on f103r. These do not replace the four agreeing readings of the Aries anchor.</p><p><b>Result:</b> functional openings remain a viable hypothesis. Their removal does not generally erase the measured anomaly, but the data do not identify a content core or establish phonetic status. The next useful check is the g-ending and its neighbouring signs across the agreed label and disputed text forms, retaining each image reading. Historical names have not been fitted.</p>'
body+='<h2>6 · Complete source readings</h2><p>H/Takahashi, U/Stolfi, V/Grove, K/Kluge-from-Petersen, and other available source codes are not independent samples. Null barriers and raw comments remain visible.</p>'
byloc=collections.defaultdict(list)
for x in rows:byloc[x['locator']].append(x)
for loc,a in byloc.items():body+='<details><summary>'+e(loc)+' · '+e(' | '.join(x['reading']+': '+x['raw'] for x in a))+'</summary><pre>'+e(json.dumps(a,indent=2))+'</pre></details>'
body+='<h2>Frozen method and full scores</h2>'
for fn in ['PROTOCOL.json','QUALIFICATION.json','RAW-REGRESSION.json','ANCHOR-RESULTS.json','ALL-PEER-TYPES.json','MODELS.json','ALL-READINGS.json','READING-NOTES.json','RESULTS.json','VERIFICATION.json']:
 body+=f'<p><a href="{fn}">{fn}</a></p>'
body+='<p>All112 anchor calculations and peer sets independently reconstructed from saved models; raw zodiac scores/ranks reproduce v82. Report appearance unreviewed. Prior artifacts preserved.</p>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>oalcheg core patterns · v88</title><style>body{font:17px system-ui;max-width:1120px;margin:36px auto;padding:0 22px;background:#f5f2e9;color:#193c39;line-height:1.5}.lede{font-size:22px}h1{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #9bb1a6;padding:8px;text-align:left;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}details{padding:8px;border-bottom:1px solid #b9c8bd}summary{cursor:pointer;overflow-wrap:anywhere}a{color:#17616d}</style>'+body+'</html>',encoding='utf-8')
save('SHA256SUMS.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps(verification,indent=2))
