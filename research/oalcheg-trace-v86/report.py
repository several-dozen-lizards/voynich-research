from pathlib import Path
import json, hashlib, collections, re, functools, html
R=Path(__file__).resolve().parent;P=R.parent
def load(n):return json.loads((R/n).read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=lambda x:html.escape(str(x))
variants=load('VARIANTS.json');events=load('ALL-EVENTS.json');alts=load('LOCUS-ALTERNATES.json');source=json.loads((P/'complete-atlas-v56/ROWS.json').read_text())
images=[
 dict(page='f70v1',locus='f70v1.S2.6',view='Local v84 panel image, plus prior native-resolution v82 focal inspection',image='../zodiac-mapping-v84/f70v1.jpg',source='https://collections.library.yale.edu/catalog/2002046?child_oid=1006201',observation='Outer-band figure/star label at source clock04:45, among fifteen figure/star units. A decorated green enclosure is visible, but no independently diagnostic named figure, constellation or star was established. Clock position is page geometry, not celestial longitude.'),
 dict(page='f39r',locus='f39r.P.4',view='Full scan and enlarged upper text',image='https://collections.library.yale.edu/iiif/2/1006150/400,300,2050,650/full/0/default.jpg',source='https://collections.library.yale.edu/catalog/2002046?child_oid=1006150',observation='Ordinary text at end of fourth line above plant drawing, not a standalone plant or star label. H okalcheg; C okal.cheg; F/U okalchem. No new glyph adjudication or botanical identity asserted.'),
 dict(page='f68r3',locus='f68r3.X.2',view='Full astronomical foldout and enlarged cluster/line region',image='https://collections.library.yale.edu/iiif/2/1006196/4800,1000,1400,1100/full/0/default.jpg',source='https://collections.library.yale.edu/catalog/2002046?child_oid=1006196',observation='Compact cluster has doaro (H/U), doary(V) beside it. oalcheol(H/U/V) is below the curved line toward the central moon, not clearly assigned to an individual member star. Nearby lone star has dchol.dal(H) versus dcholday(U/V). Pleiades interpretation remains conditional; seven planets is a published alternative.'),
 dict(page='f67v1',locus='f67v1.Y.2',view='Full foldout and enlarged right-hand radial text',image='https://collections.library.yale.edu/iiif/2/1006195/3850,1250,1100,700/full/0/default.jpg',source='https://collections.library.yale.edu/catalog/2002046?child_oid=1006195',observation='Four-word radial line beside stars, not an isolated fixed-star name label. U olcheeg is a two-edit neighbour. H has oloesdr; V olcheed{curled page}. Reading and damage uncertainty prevent treating this as secure recurrence.'),
]
save('IMAGE-AUDIT.json',images)
history=dict(admissible_specific_name_pairs_for_oalcheg=[],reason='No repeated independently identified referent connects the Aries figure/star label, botanical body text and astronomical connecting line. String similarity is not referent identity.',conditional_context_candidates=[dict(referent='Compact star cluster on f68r3, IF it represents the Pleiades',nearest_label={'H':'doaro','U':'doaro','V':'doary'},written_forms=[dict(form='Pliades',status='Exact nominative form in inspected Latin text'),dict(form='Vergilias',status='Exact accusative plural in inspected text; dictionary nominative Vergiliae')],source='https://www.thelatinlibrary.com/isidore/3.shtml',passage='Isidore, Etymologiae III.71.13',limits='Edited early-medieval primary text, not a Voynich-era local manuscript or reconstructed pronunciation. Candidate lexical family belongs to the cluster label, not automatically oalcheol or oalcheg. No fit performed.')],excluded_leads=[dict(lead='Alcyone or another individually named Pleiad',reason='Image does not attach oalcheol to an independently identified individual star. Search surfaced prior proposals; preserved as exposed but not adopted.'),dict(lead='Arabic al- star names inferred from EVA oal-',reason='EVA characters have no demonstrated sound values. This would select names by unqualified sound resemblance.'),dict(lead='Tail, dragon, occultation or lunar-event terminology',reason='Curved-line association motivates a relation/event comparison, but the geometry does not identify which event or named object. No particular historical word admitted.'),dict(lead='Aries degree, decan, calendar or named figure',reason='No independently fixed degree alignment or distinctive named figure here. Existing v85 is synthetic qualification only; no actual Voynich alignment available.')])
save('HISTORICAL-NAME-ASSESSMENT.json',history)
sources=[dict(url='https://www.voynich.nu/q09/index.html',used='f68r3 cluster/line distinction and alternative seven-planets interpretation; f67v1 radial format'),dict(url='https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/98-02-01-lotsa-labels/labels-t.html',used='Original label catalogue: X.1 cluster, X.2 tail near Pleiades, X.3 lone star. It shares archive provenance, not independent confirmation.'),dict(url='https://www.thelatinlibrary.com/isidore/3.shtml',used='Primary Latin text III.71.13: Pliades and Vergilias; no sound mapping'),dict(url='https://collections.library.yale.edu/manifests/2002046',used='Image IDs and native dimensions from rendered IIIF manifest')]
save('SOURCES.json',sources)
near_loci={x['locator'] for x in events if x['tier']!='secondary two-edit'}
astral_loci={x['locator'] for x in events if x['section']=='Astronomy/Astrology'}
label_loci={x['locator'] for x in events if x['source_unit'].startswith(('S','X','L'))}
survey=[]
for page in ['f68r1','f68r2','f68r3']:
 a=[x for x in source if x[1]==page and (x[5].startswith('S') if page!='f68r3' else x[5]=='X')]
 survey.append(dict(page=page,format='S star labels' if page!='f68r3' else 'X labels including cluster/line',loci=len({x[8] for x in a}),rows_by_reading=dict(collections.Counter(x[0] for x in a)),qualifying_event_loci=sorted({x['locator'] for x in events if x['page']==page and x['source_unit'].startswith(('S','X'))})))
save('STAR-LABEL-SURVEY.json',survey)

# Independent recursive edit-distance audit over the entire vocabulary, without importing the search implementation.
def edit(a,b):
 @functools.lru_cache(None)
 def go(i,j):
  if i==len(a):return len(b)-j
  if j==len(b):return len(a)-i
  return min(1+go(i+1,j),1+go(i,j+1),(a[i]!=b[j])+go(i+1,j+1))
 return go(0,0)
def group(w):return tuple(re.findall('cth|ckh|cph|cfh|ch|sh|.',w))
vocab={w for x in source for w in x[9] if w};found={}
for w in vocab:
 if abs(len(w)-7)>2 and abs(len(group(w))-6)>2:continue
 dc=edit('oalcheg',w);dg=edit(group('oalcheg'),group(w))
 if min(dc,dg)<=2:found[w]=(dc,dg)
assert set(found)=={x['word'] for x in variants}
for x in variants:assert found[x['word']]==(x['character_distance'],x['group_distance'])
expected=[]
for x in source:
 for j,w in enumerate(x[9]):
  if w in found:expected.append((x[0],x[8],j,w))
assert collections.Counter(expected)==collections.Counter((x['reading'],x['locator'],x['token_index'],x['word']) for x in events)
for loc,a in alts.items():assert len(a)==sum(x[8]==loc for x in source)
for fn in ['PRE-SEARCH-FREEZE.json','BOUNDARY-FREEZE.json']:
 for p,h in load(fn).items():assert sha(Path(p))==h
verification=dict(exhaustive_variant_set_independently_recomputed=True,event_multiset_exact=True,all_alternate_rows_preserved=True,frozen_inputs_unchanged=True,exact_anchor_physical_loci=1,whole_token_primary_neighbour_loci=1,multiword_primary_hits=len(load('MULTIWORD-NEAR-HITS.json')),admissible_oalcheg_name_pairs=0,sound_mappings_fitted=0,report_visual_review='Not performed: local file-URL preview blocked in prior turn. Remote manuscript images inspected; no policy workaround attempted.')
save('VERIFICATION.json',verification)
summary=load('SEARCH-SUMMARY.json');summary.update(dict(near_loci=sorted(near_loci),astronomical_variant_loci=sorted(astral_loci),label_like_loci=sorted(label_loci),historical_name_result='Conditional Pliades/Vergiliae vocabulary for adjacent cluster label doaro/doary, no specific historical name admitted for oalcheg/oalcheol.',verification=verification));save('RESULTS.json',summary)
body='<h1>Tracing oalcheg · v86</h1><p class="lede">One exact manuscript location. One disputed one-edit neighbour in botanical text. A wider astronomical lead labels a curved line, not an identified individual star.</p>'
body+='<p>All18 reading codes and all corpus sections searched. Frozen vocabulary:11,165 types. The character/group edit-distance search returned25 types across64 physical source loci (167 reading-token events, not167 independent attestations). Search is descriptive; no sound mappings or semantic scores.</p>'
body+='<h2>1 · Closest traces</h2><table><tr><th>Form · distance</th><th>Locus / association</th><th>Alternate readings</th></tr>'
focus=[('oalcheg','exact','f70v1.S2.6','Outer Aries figure/star label, source04:45'),('okalcheg','one insertion','f39r.P.4','Botanical paragraph, line ending'),('oalcheol','two edits','f68r3.X.2','Curved line beside cluster, toward moon'),('olcheeg','two edits','f67v1.Y.2','Four-word radial text, weaker reading')]
for w,d,loc,association in focus:
 readings=' | '.join(x['reading']+': '+x['raw'] for x in alts[loc]);body+=f'<tr><td><b>{e(w)}</b><br>{e(d)}</td><td><a href="#{e(loc)}">{e(loc)}</a><br>{e(association)}</td><td>{e(readings)}</td></tr>'
body+='</table><p>The one-edit botanical neighbour is not reading-stable: H joins okalcheg, C splits okal.cheg, F/U have okalchem. A separate frozen all-corpus multiword diagnostic found only the same C split as an additional exact/one-edit hit. It adds no new physical locus.</p>'
body+='<h2>2 · What the images show</h2>'
for x in images:
 body+=f'<details open><summary><b>{e(x["page"])} · {e(x["locus"])}</b></summary><a href="{e(x["source"])}"><img loading="lazy" src="{e(x["image"])}" alt="Inspected {e(x["page"])} region"></a><p>{e(x["observation"])}</p><p>{e(x["view"])}</p></details>'
body+='<h2>3 · Other star labels</h2><p>No exact or one-edit recurrence occurs in another star label. Within the frozen two-edit net, f68r3.X.2 is the only other astronomical label locus. No qualifying token occurs in the f68r1 or f68r2 S star-label sets. f67v1.Y.2 is radial text, not an isolated star label. A two-edit olchey reading also occurs at f80r.X.2, but that unit labels a bathing figure: H/U olchdy versus V olchey.</p><p>The broad net contains23 two-edit forms, including olchey at34 source loci across several sections. Those ordinary-looking body-text neighbours make a broad string family less specific, not a coherent set of repeated star names. No enrichment or common-meaning claim is made.</p>'
body+='<h2>4 · Is there a historical name to test?</h2><p><b>No specific historical name is currently justified for oalcheg.</b> Its Aries figure/star has no independently identified individual referent. The nearby-string astronomical lead oalcheol sits under a curved connector. The star cluster itself has a different label: H/U doaro, V doary.</p><p>If the cluster is the Pleiades, it provides a conditional lexical family for <b>doaro/doary</b>. Isidore, <i>Etymologiae</i> III.71.13, uses the written forms <b>Pliades</b> and <b>Vergilias</b> (nominative lemma <i>Vergiliae</i>). This is edited primary textual attestation, not evidence for Voynich language, local fifteenth-century usage or pronunciation. The published seven-planets alternative remains open. <a href="https://www.thelatinlibrary.com/isidore/3.shtml">Primary Latin text</a>.</p><p>Alcyone is not selected: the image does not identify an individual Pleiad as owner of the word. Arabic al- star names are not selected from EVA oal- resemblance. Tail/dragon/occultation/lunar-event ideas remain unassigned comparison leads; the curved line does not distinguish them.</p><p>The useful next discrimination is graphical: find a dated diagram that independently matches the cluster–connector–moon arrangement, retaining label ownership. This could constrain whether the connector carries a relation/event term rather than a proper name. Fitting sounds now would assume the fact we need to establish.</p>'
body+='<h2>5 · Full frozen variant inventory</h2><p>Levenshtein insertion/deletion/substitution, exact/one-edit primary and two-edit secondary, in either EVA characters or fixed longest ch/sh/cth/ckh/cph/cfh groups. Nearness does not imply equivalent words. Alternate-reading row counts are kept separate from physical loci.</p><table><tr><th>Form</th><th>Char / group edits</th><th>Source loci</th><th>Pages</th><th>Reading-token counts</th></tr>'
for x in variants:body+='<tr>'+''.join('<td>'+e(v)+'</td>' for v in [x['word'],str(x['character_distance'])+' / '+str(x['group_distance']),x['loci'],', '.join(x['pages']),x['rows_by_reading']])+'</tr>'
body+='</table><h2>6 · Every selected source locus and alternate</h2><p>Raw uncertainties, split/join alternatives and missing slots preserved. H/F remain distinct where both exist; F is absent on the Aries anchor. Shared archive/editor history means H/K/V/U agreement is not independent replication. Strict cleaning may create barriers from commas or editorial comments; raw source lines remain visible.</p>'
contexts=load('RAW-CONTEXT.json')
for loc,a in alts.items():
 body+=f'<details id="{e(loc)}"><summary>{e(loc)} · '+e(' | '.join(x['reading']+': '+' '.join(w or '[barrier]' for w in x['tokens']) for x in a))+'</summary><pre>'+e(json.dumps(a,indent=2,ensure_ascii=False))+'</pre><details><summary>Original source context</summary><pre>'+e(json.dumps(contexts.get(loc,[]),indent=2,ensure_ascii=False))+'</pre></details></details>'
body+='<h2>Audit files</h2>'
for fn in ['PROTOCOL.json','PRE-SEARCH-FREEZE.json','VARIANTS.json','ALL-EVENTS.json','LOCUS-ALTERNATES.json','RAW-LITERAL-HITS.json','UNIT-COMMENTS.json','BOUNDARY-PROTOCOL.json','MULTIWORD-NEAR-HITS.json','IMAGE-AUDIT.json','HISTORICAL-NAME-ASSESSMENT.json','STAR-LABEL-SURVEY.json','RESULTS.json','VERIFICATION.json']:
 body+=f'<p><a href="{fn}">{fn}</a></p>'
for x in sources:body+=f'<p><a href="{e(x["url"])}">{e(x["used"])}</a></p>'
body+='<p>Image provider: Yale University Library, Beinecke MS408. Three remote full scans and enlarged detail regions inspected in this turn; local Aries panel re-inspected. No independent palaeographic adjudication. The report layout has not been browser-reviewed.</p>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>oalcheg trace · v86</title><style>body{font:17px system-ui;max-width:1120px;margin:36px auto;padding:0 22px;background:#f5f2e9;color:#193c39;line-height:1.5}h1{line-height:1.2}.lede{font-size:22px}img{display:block;max-width:100%;max-height:780px;margin:16px auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #9bb1a6;padding:8px;text-align:left;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}details{border-bottom:1px solid #b9c8bd;padding:10px 0}summary{cursor:pointer;overflow-wrap:anywhere}a{color:#17616d}</style>'+body+'</html>',encoding='utf-8')
save('SHA256SUMS.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps(summary,indent=2))
