from pathlib import Path
import json, hashlib, math, collections, re, html

R=Path(__file__).resolve().parent; P=R.parent
def load(n):return json.loads((R/n).read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=lambda x:html.escape(str(x))
rows=load('TARGET-ALL-READINGS.json');occ=load('ALL-OCCURRENCES.json');types=load('ALL-TYPES.json');models=load('MODELS.json');alts=load('ALTERNATES-BY-LOCUS.json')
raw=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data\text16e6.original.evt')
lines=raw.read_text(encoding='latin1').splitlines();snippets={}
for loc in alts:
 for i,line in enumerate(lines):
  if line.startswith('<'+loc+';H>'):
   snippets[loc]='\n'.join(lines[max(0,i-4):i+7]);break
save('RAW-SOURCE-EXCERPTS.json',snippets)
provenance={'H':'Takeshi Takahashi','U':'Jorge Stolfi','V':'John Grove','C':'Currier plus subsequent additions','K':"Karl Kluge from Petersen's copies",'Q':'Second choice unfolded from K; not a separate transcriber','F':'Friedman First Study Group; absent on these panels','limits':'Common interlinear editing and source dependencies prevent treating agreements as independent samples. Raw archive transcriber-code header inspected.'}
save('READING-PROVENANCE.json',provenance)
labelrole='figure/star-associated label; exact referent unresolved'
focal=sorted({x['locator'] for x in occ if x['reading']=='H' and x['display_flag'] and (x['role']==labelrole or x['primary_central_ring'])})
matrix=[]
for loc in focal:
 a=alts[loc]; hs=[x for x in occ if x['locator']==loc and x['reading']=='H']; flagwords=sorted({x['word'] for x in hs if x['display_flag']})
 for w in flagwords:
  scores=[dict(reading=x['reading'],view=x['view'],word=x['word'],percentile=x['percentile'],peers=x['matched_peers'],surprise=x['surprise']) for x in occ if x['locator']==loc and x['word']==w]
  robust=all(any(x['reading']==rd and x['view']==vw and x['word']==w and x['display_flag'] for x in occ if x['locator']==loc) for rd in ['H','V'] for vw in ['characters','groups']) if hs[0]['role']==labelrole else False
  gap=any('{gap}' in x['raw'] for x in a)
  matrix.append(dict(locator=loc,H_word=w,role=hs[0]['role'],primary=hs[0]['primary_central_ring'],same_word_HV_both_views_flag=robust,scores=scores,all_readings=a,gap_in_locus=gap,interpretation='Spelling candidate only; figure/star association does not identify sign name' if hs[0]['role']==labelrole else 'Central-ring word; no isolated title or phonetic inference'))
save('CANDIDATE-MATRIX.json',matrix)
focused_inspection=[
 dict(locator='f70v1.S2.6',source_clock='04:45, outer figure/star band',image='https://collections.library.yale.edu/iiif/2/1006201/1900,1900,1000,1100/full/0/default.jpg',observation='Enlarged lower-right region inspected; label is among outer figure/star labels. No sign-title placement. H/K/V/U all oalcheg; no new palaeographic adjudication.'),
 dict(locator='f71v.S2.1',source_clock='Inner band starting at 10:00',image='https://collections.library.yale.edu/iiif/2/1006203/650,650,1050,1050/full/0/default.jpg',observation='Enlarged upper-left/central region inspected with dressed inner figure and star. H/V ofacfom, C opaepom, K ofa*fom. The unusually high score is not reading-unanimous.'),
 dict(locator='f72r1.S1.9',source_clock='07:30, outer band',image='https://collections.library.yale.edu/iiif/2/1006203/2300,1650,1100,1100/full/0/default.jpg',observation='Enlarged lower-left region inspected; multiword label associated with an outer figure/star. otalef stable across H/K/V, following as/ys differs. V grouped rank misses frozen .90 display flag.'),
]
save('FOCAL-IMAGE-CHECKS.json',focused_inspection)
reading_notes={
 'f70v1.S1.3':'H/K/V preserve alols as a word; U marks oteo,alols with comma uncertainty, so strict parser excludes both. The final word also differs asaly/araly.',
 'f70v1.S2.6':'H/K/V/U all oalcheg. High matched rank in both views under separately trained H and V models. All four readings share archive/editor history.',
 'f70v1.S2.7':'All four preserve otchodals, but H character rank lacks enough exact peers; V grouped rank .857 misses display threshold.',
 'f70v1.S2.10':'H/K/U ypsharal versus V ypcsaral. Preceding otol/otal differs. No merged consensus.',
 'f71r.S1.8':'H chsary versus K/V cheary. H flag only in grouped view.',
 'f71v.S1.1':'H orom, C orol, K oroj, V arom. Reading-sensitive, H grouped-view flag only.',
 'f71v.S1.5':'H/C olcphy versus K/V alcphy. H character-view flag only.',
 'f71v.S2.1':'H/V ofacfom, C opaepom, K ofa*fom. Matching H/V flags do not settle the alternate reading.',
 'f72r1.S1.5':'H ytal.shda versus K/V ytal!shdy (one joined token after ! removal). shda is not stable as a separate word.',
 'f72r1.S1.9':'H/K/V otalef; following as/ys differs. V grouped percentile .882 is below .90; keep that failure.',
 'f71r.R3.1':'H chekeen versus U cheku. H grouped rank .926, character rank .889. U cheku has an unseen u symbol under its own model; rank is sensitive to unknown-unit handling.',
 'f71v.R3.1':'H/C chkeeal stable; H character rank .926, grouped .889. No comparable U central ring. Neither H view makes kal atypical among matched peers.',
 'f72r1.R3.1':'H yroly/chckhy versus U aroly/chcthy. Both H words touch source gap markers. U ranks are lower (.625/.800 for aroly; .850/.714 for chcthy). No secure sound anchor.',
}
save('READING-AND-BOUNDARY-NOTES.json',reading_notes)

# Independent numerical audit using transition counters reconstructed from the saved source allocation.
source=json.loads((P/'astrology-name-audit-v81/ALL-READINGS.json').read_text())
def split(w,v):return list(w) if v=='characters' else re.findall('cth|ckh|cph|cfh|ch|sh|.',w)
maxerr=0
for key,entry in models.items():
 rd,role,view=key.split('|');tr=[x for x in source if x['reading']==rd and x['role']==role and x['hand']=='4' and x['sign'] not in ['Aries','Taurus']]
 assert {x['sign'] for x in tr}.isdisjoint({'Aries','Taurus'})
 assert not any(x['page'] in ['f70v1','f71r','f71v','f72r1'] for x in tr)
 words=[w for x in tr for w in x['tokens'] if w];cnt=collections.Counter();total=collections.Counter();abc={'$','?'}
 for w in words:
  u=split(w,view);abc.update(u)
  for a,b in zip(['^']+u,u+['$']):cnt[a,b]+=1;total[a]+=1
 assert dict(collections.Counter(words))==entry['frequency']
 for x in [t for t in types if t['model_key']==key]:
  u=[a if a in abc else '?' for a in split(x['word'],view)]
  vals=[math.log((cnt[a,b]+.5)/(total[a]+.5*len(abc))) for a,b in zip(['^']+u,u+['$'])]
  s=-sum(vals)/len(vals);err=abs(s-x['surprise']);maxerr=max(maxerr,err);assert err<1e-12
  peers=[t for t in types if t['model_key']==key and t['word']!=x['word'] and t['unit_length']==x['unit_length'] and t['training_count']==x['training_count']]
  assert len(peers)==x['matched_peers']
  pct=(sum(y['surprise']<s-1e-12 for y in peers)+.5*sum(abs(y['surprise']-s)<=1e-12 for y in peers))/len(peers) if len(peers)>=5 else None
  assert pct==x['percentile']
assert sum(len(x) for x in alts.values())==len(rows)
assert len([x for x in rows if x['reading']=='H' and x['role']==labelrole])==60
for p,h in load('PRE-SCORE-FREEZE.json').items():assert sha(Path(p))==h
verification=dict(numerical_scores_independently_reconstructed=True,max_absolute_error=maxerr,exact_peer_ranks_recomputed=True,no_target_sign_in_training=True,all_target_source_rows_preserved=len(rows),H_figure_star_loci=60,F_rows=sum(x['reading']=='F' for x in rows),frozen_inputs_unchanged=True,sounds_fitted=0,browser_visual_review='Local report preview blocked by browser file-URL security policy; no workaround attempted. Remote manuscript image inspection completed separately.')
save('VERIFICATION.json',verification)

body='<h1>Paired Aries / Taurus · images and label patterns</h1><p class="lede">Some spelling candidates survive comparison across readings. No isolated Voynich sign title has been identified. No sounds fitted.</p>'
body+='<p>The image positions and comparison rules were frozen before this scoring run. Earlier work already exposed the source words. Percentiles below are descriptive ranks among matched target types, not probabilities, statistical significance, or evidence of phonetic writing.</p>'
body+='<h2>1 · Where could a name be?</h2><p>The later April/May annotations occupy the clearest isolated naming positions inside all four animals. They are excluded as Voynich cribs. Light Aries and both Taurus panels have a Voynich text ring around the animal; dark Aries lacks that immediate ring. A word within a ring could name the sign, but the image does not identify which word.</p>'
for x in load('IMAGE-POSITIONS.json'):
 body+=f'<article><h3>{e(x["page"])} · {e(x["sign"])}</h3><a href="{e(x["catalogue"])}"><img src="{e(x["centre_image"])}" alt="Inspected centre of {e(x["page"])}"></a><p>{e(x["central_title"])}</p><p>Primary locus: <b>{e(x["primary_locus"] or "none identified")}</b>. {e(x["secondary"])} {e(x["damage"])}</p></article>'
body+='<h2>2 · How usual patterns were compared</h2><p>Training excludes both Aries and both Taurus panels. Models learn from the other six surviving zodiac signs assigned local hand 4. Individual labels and circular text stay separate. H, V and U stay separate. H label model: 209 readable training tokens; V: 194. H circular model: 503; U: 254. U label training is too sparse; V circular text is absent. Local hand 3 pages f73r/v are excluded; the v81 hand-metadata conflict remains unresolved.</p><p>Two fixed views use EVA characters or longest ch/sh/cth/ckh/cph/cfh groups. Add-half bigram surprise is compared only among other target types of the exact same unit length and training-word count, with at least five peers. A rank of 100 means above every matched peer, not 100% confidence. A frozen rank of 90 or above is a display flag only. Format pooling does not control inner/outer radial position.</p><p>Artificial-template and parser engineering checks passed before scoring. They do not qualify phonetic interpretation or provide a false-positive rate. No modern or historical name was fitted.</p>'
body+='<h2>3 · Individual label candidates and alternate readings</h2><p>These are associated with figures/stars, not demonstrated sign-name positions. Every H display-flagged label locus is shown; view-specific and reading-sensitive results remain visible. Full unflagged data follow below.</p>'
def pct(x):return 'unrankable' if x is None else f'{100*x:.1f}'
def rankcells(loc,w,reading):
 cells=[]
 for v in ['characters','groups']:
  hits=[x for x in occ if x['locator']==loc and x['word']==w and x['reading']==reading and x['view']==v]
  cells.append(pct(hits[0]['percentile']) if hits else 'absent/unsupported')
 return ' / '.join(cells)
body+='<table><thead><tr><th>Locus · H word</th><th>H rank<br>char / group</th><th>V same-word rank<br>char / group</th><th>Reading / boundary evidence</th></tr></thead><tbody>'
for x in matrix:
 if x['primary']:continue
 loc=x['locator'];w=x['H_word'];body+=f'<tr><td><a href="#{e(loc)}">{e(loc)}</a><br><b>{e(w)}</b></td><td>{rankcells(loc,w,"H")}</td><td>{rankcells(loc,w,"V")}</td><td>{e(reading_notes[loc])}</td></tr>'
body+='</tbody></table><p><b>oalcheg</b> has matching spelling in H/K/V/U and flags in both H/V views. <b>alols</b> flags in H/V but U marks uncertain boundaries. <b>ofacfom</b> flags in H/V, while C and K retain substantive alternatives. These are spelling candidates with different levels of reading support, not a consensus transcription.</p>'
body+='<h2>4 · Words in the central rings</h2><table><tr><th>Panel</th><th>H candidate</th><th>H char / group rank</th><th>Reading limitations</th></tr>'
for x in matrix:
 if not x['primary']:continue
 loc=x['locator'];w=x['H_word'];body+=f'<tr><td><a href="#{e(loc)}">{e(loc)}</a></td><td>{e(w)}</td><td>{rankcells(loc,w,"H")}</td><td>{e(reading_notes[loc])}</td></tr>'
body+='</table><p>The only exact complete word shared by the two H Taurus central rings is <b>otaiin</b>. It occurs in training and is not a distinctive atypical candidate under this screen. Dark Aries has no matching central-ring position. Neither repeated sign supplies a repeated unusual word in an established title slot.</p>'
body+='<h2>5 · Enlarged focal label checks</h2>'
for x in focused_inspection:body+=f'<details><summary>{e(x["locator"])} · {e(x["source_clock"])}</summary><img loading="lazy" src="{e(x["image"])}" alt="Focal label region"><p>{e(x["observation"])}</p></details>'
body+='<h2>6 · Every target locus, all readings</h2><p>H = Takahashi; U = Stolfi; V = Grove; C = Currier plus additions; K = Kluge from Petersen copies; Q = a K alternate. These are not independent sample replications. Null slots preserve the prior strict cleaner: commas and brace annotations can create barriers, including trailing editorial annotations. A null is not automatically a damaged glyph in the manuscript. Raw source is retained below for each locus.</p>'
for loc,a in alts.items():
 body+=f'<details id="{e(loc)}"><summary>{e(loc)} · '+e(' | '.join(x['reading']+': '+' · '.join(w or '[barrier]' for w in x['tokens']) for x in a))+'</summary>'
 if loc in reading_notes:body+=f'<p>{e(reading_notes[loc])}</p>'
 body+='<pre>'+e(json.dumps(a,ensure_ascii=False,indent=2))+'</pre><details><summary>Raw archive context</summary><pre>'+e(snippets.get(loc,''))+'</pre></details></details>'
body+='<h2>Frozen methods and complete results</h2>'
for fn in ['PROTOCOL.json','IMAGE-POSITIONS.json','QUALIFICATION.json','SUPPORT.json','ALL-TYPES.json','ALL-OCCURRENCES.json','TARGET-ALL-READINGS.json','ALTERNATE-SCORES-UNDER-H.json','CANDIDATE-MATRIX.json','READING-AND-BOUNDARY-NOTES.json','REPEATED-PANEL-WORDS.json','READING-PROVENANCE.json','VERIFICATION.json']:
 body+=f'<p><a href="{fn}">{fn}</a></p>'
body+='<p>Image provider: Yale University Library, Beinecke MS 408, <a href="https://collections.library.yale.edu/manifests/2002046">IIIF manifest</a>. Four full-panel views and enlarged central crops inspected; three focal label regions enlarged. Geometry is a reader audit, not independent expert palaeography or adjudication of every character. Images are loaded from Yale; the local audit files preserve URLs, regions and dimensions.</p>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Paired Aries/Taurus label patterns · v82</title><style>body{font:17px system-ui;max-width:1120px;margin:36px auto;padding:0 22px;background:#f5f2e9;color:#193c39;line-height:1.5}h1{line-height:1.2}.lede{font-size:22px}table{border-collapse:collapse;width:100%;font-size:15px}td,th{border:1px solid #9bb1a6;padding:9px;text-align:left;vertical-align:top}article{display:inline-block;width:calc(50% - 34px);vertical-align:top;margin:12px 12px 20px 0;padding:8px}img{width:100%;height:auto;max-width:720px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}details{border-bottom:1px solid #b9c8bd;padding:9px 0}summary{cursor:pointer;overflow-wrap:anywhere}a{color:#17616d}@media(max-width:700px){article{display:block;width:auto}table{font-size:12px}td,th{padding:5px}}</style>'+body+'</html>',encoding='utf-8')
save('SHA256SUMS.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps(dict(verification=verification,robust_label_candidates=[(x['locator'],x['H_word']) for x in matrix if x['same_word_HV_both_views_flag']],candidate_rows=len(matrix)),indent=2))
