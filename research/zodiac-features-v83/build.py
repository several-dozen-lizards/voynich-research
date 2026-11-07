import json, hashlib, html
from pathlib import Path
P=Path(__file__).resolve().parent
def save(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
# Manual image observations. Coordinates are approximate head centres read from
# displayed IIIF crops, not measurements inferred from transcription.
panels=[
 ('f70v2','Pisces','1006200',[650,300,2650,2850],'Two bands; provisional count 19 outer + 10 inner. Do not insert a thirtieth figure. Fold crosses left side.'),
 ('f70v1','Aries','1006201',[600,450,2100,2400],'Two bands, 10 outer and 5 inner visible. Lower-body enclosures need close review; clothing must not be inferred from patterned enclosure.'),
 ('f71r','Aries','1006202',None,'Two bands, 10 outer and 5 inner visible. Pigmented garments/enclosures; the first crop cut off left figures, so full-page view was also checked.'),
 ('f71v','Taurus','1006203',[250,100,2050,2750],'Left panel of combined scan. Crop clips right edge; count and individual assignments not finalized.'),
 ('f72r1','Taurus','1006203',[2300,100,2100,2750],'Second panel. Standing outer figures contrast with inner enclosures. Hole near left of centre; missingness must stay explicit.'),
 ('f72r2','Gemini','1006203',[3950,0,2450,2850],'Circular bands plus figures above the bands. Ordering of the extra group is unresolved. Do not force into a two-ring rule.'),
 ('f72r3','Cancer','1006203',[5950,0,2850,2900],'Three bands visible. Original two-ring order wording is insufficient. Fold crosses right side.'),
 ('f72v3','Leo','1006204',[1000,300,2500,3000],'Circle extends across fold. First crop clipped right side; widened inspection exposed a narrow fringe of adjacent Virgo. No Virgo figures annotated or scored.')]
records=[]
for folio,sign,oid,region,note in panels:
 records.append(dict(folio=folio,sign=sign,oid=oid,region=region,note=note,status='overview inspected; individual audit incomplete',source=f'https://collections.library.yale.edu/iiif/2/{oid}/full/full/0/default.jpg'))
save('PANEL-INVENTORY.json',records)
figures=[]
def locators(folio,oid,region,display,rings):
 ox,oy,dw,dh=display; rx,ry,rw,rh=region
 for ring,points in rings.items():
  for i,(x,y) in enumerate(points,1):
   figures.append(dict(id=f'{folio}-{ring}-{i:02}',folio=folio,oid=oid,ring=ring,clockwise_index_from_top=i,head_xy_source=[round(rx+(x-ox)*rw/dw),round(ry+(y-oy)*rh/dh)],locator_precision='approximate visual head centre; not a glyph or label coordinate',body=None,vessel=None,star_pigmentation=None,label_box=None,label_connection=None,status='provisional locator only; feature and label close-review pending'))
locators('f70v2','1006200',[650,300,2650,2850],[306,0,669,720],{
 'outer':[(650,47),(710,70),(790,90),(860,140),(910,210),(950,310),(950,430),(900,530),(820,605),(720,655),(590,650),(485,620),(405,520),(365,435),(365,310),(410,200),(455,130),(525,80),(590,50)],
 'inner':[(655,160),(770,215),(845,310),(820,455),(735,540),(615,570),(500,480),(460,360),(480,260),(565,175)]})
locators('f70v1','1006201',[600,450,2100,2400],[325,0,630,720],{
 'outer':[(650,74),(840,150),(940,325),(920,485),(845,590),(695,660),(530,635),(410,530),(350,375),(435,165)],
 'inner':[(645,200),(800,320),(730,515),(510,455),(525,250)]})
save('PROVISIONAL-FIGURE-LOCATORS.json',figures)
save('SOURCE-ACCESS-LOG.json',[
 {'source':'Wright 1934 / al-Biruni, work dated 1029 on edition title','status':'Selected before mapping; actual degree table not inspected'},
 {'url':'https://www.skyscript.co.uk/pdf/pubs/texts/albiruni/docs/albiruni.pdf','status':'web403; browser blank; shell DNS failure'},
 {'url':'https://www.jphogendijk.nl/biruni.html','status':'Catalogue inspected; supplied alternate scan links. Catalogue distinguishes Arabic revision 1030-31 from original Persian work.'},
 {'url':'https://menadoc.bibliothek.uni-halle.de/ssg/content/titleinfo/1031770?query=biruni','status':'Redirected to general MENAlib search portal'},
 {'url':'https://opendata.uni-halle.de/handle/1981185920/32158','status':'Bot verification page; not bypassed'},
 {'url':'https://archive.org/details/TheBookOfInstructionOnTheElementsOfTheArtOfAstrologyByAlBiruni','status':'Item no longer available'},
 {'url':'https://pdfcoffee.com/arab-biruni-v3-the-book-of-instruction-on-the-elements-of-the-art-of-astrology-wright-1934-pdf-free.html','status':'Web timeout; browser security verification; not bypassed'},
 {'url':'https://www.skyscript.co.uk/glossary/degree-types/','status':'Secondary locator only: sex degree table section457; luminosity section458. No degree sequence admitted.'}])
save('STATUS.json',dict(status='INCOMPLETE; comparison not run',development_panels_overviewed=8,provisional_figure_locators=len(figures),completed_label_maps=0,completed_feature_inventories=0,primary_table_verified=False,scoring_rules_frozen=False,synthetic_qualification_run=False,holdout_scored=False,holdout_individual_annotation=False,exposure_notes=['Quire catalogue descriptions included holdout pages when retrieving panel order; not blind to general descriptions.','Narrow Virgo fringe appeared while finding Leo crop extent; no figure annotation or scoring.'],required_amendments=['Handle Pisces non-30 provisional count without inventing a figure.','Handle Gemini extra-band group and Cancer third band before numerical freeze.','Require panel/ring-conditioned null and panel-level baseline so layout differences cannot masquerade as degree agreement.','Freeze missingness and coverage gates, multiplicity correction, search budget and success criteria before scoring.']))
def esc(s):return html.escape(str(s))
cards=''
for r in records:
 region=','.join(map(str,r['region'])) if r['region'] else 'full'
 url=f"https://collections.library.yale.edu/iiif/2/{r['oid']}/{region}/1200,/0/default.jpg"
 cards+=f'<article><h2>{esc(r["folio"])} · {esc(r["sign"])}</h2><p>{esc(r["note"])}</p><a href="{url}">Open Yale inspection image</a><p class="muted">{esc(r["status"])}</p></article>'
rows=''.join(f'<tr><td>{esc(f["id"])}</td><td>{f["head_xy_source"]}</td><td>Unreviewed</td></tr>' for f in figures)
(P/'report.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Zodiac image inventory · v83</title><style>body{background:#101a22;color:#e6edf0;font:17px/1.6 system-ui;max-width:1100px;margin:45px auto;padding:0 24px}h1{font-size:36px}h2{font-size:22px}a{color:#8cddd0}.status{border-left:5px solid #efbb72;padding:16px;background:#253039}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}article{background:#192832;padding:22px;border-radius:12px}.muted{color:#acbcc7;font-size:14px}td,th{text-align:left;padding:8px;border-bottom:1px solid #36505a}table{border-collapse:collapse;width:100%}</style><h1>Zodiac image inventory · v83</h1><p class="status"><b>INCOMPLETE — no degree comparison has been run.</b> Eight development panels inspected at overview; 44 provisional head locators saved. Individual feature classifications and label boxes remain unreviewed. No primary degree table verified.</p><p>The pre-annotation protocol was frozen first. This is annotation independent of glyph readings, not independent human validation. No symbols have been transcribed or assigned meanings.</p><h2>Whole-sign split</h2><p>Development: Pisces, Aries, Taurus, Gemini, Cancer, Leo. Confirmation: Virgo, Libra, Scorpio, Sagittarius. Both panels of Aries/Taurus stay together. Confirmation has not been scored or individually annotated.</p><h2>Geometry catches before scoring</h2><ul><li>Pisces provisionally has 29 visible figure locations; no thirtieth figure was invented.</li><li>Gemini has an extra group above the bands; Cancer has three bands. The original ordering language must be amended and frozen before comparison.</li><li>Panel and ring differences need their own null control. A match driven merely by clothed versus unclothed panels is insufficient.</li><li>Patterned lower-body forms and pale star colour cannot be forced into confident categories.</li></ul><h2>Development image index</h2><div class="grid">'''+cards+'''</div><h2>Source access and remaining work</h2><p>Selected: al-Biruni, Wright's 1934 edition of the work dated 1029. The selected PDF returned403; the old Halle link redirected; its replacement showed bot verification; the linked Archive copy was removed; another mirror showed security verification. These failures are preserved. Modern summaries have not been substituted for the degree table.</p><p>Next: obtain readable primary sections457/458; finish native-resolution figure and label review; freeze inventory and revised ordering/missingness rules; qualify the full search on synthetic positive and layout-only negative controls; then development selection and untouched whole-sign confirmation. There is currently neither support nor a null result for the degree-table hypothesis.</p><p>Exposure limitation: catalogue descriptions included holdout pages and a narrow Virgo fringe appeared during Leo crop adjustment. No holdout figure has been annotated or scored; this is not complete visual blinding.</p><h2>Provisional locators</h2><p>Approximate source-image pixel coordinates of heads, not label assignments. All feature fields are null pending close review.</p><table><tr><th>Figure</th><th>Source x,y</th><th>Features</th></tr>'''+rows+'''</table><p><a href="PROTOCOL.json">Original protocol</a> · <a href="PRE-ANNOTATION-FREEZE.json">Original freeze</a> · <a href="PROVISIONAL-FIGURE-LOCATORS.json">Locator data</a> · <a href="SOURCE-ACCESS-LOG.json">Source failures</a> · <a href="STATUS.json">Status</a></p></html>''',encoding='utf-8')
save('RECEIPTS.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in P.iterdir() if p.is_file() and p.name!='RECEIPTS.json'})
print(json.dumps({'panels':len(records),'provisional_locators':len(figures),'comparison':'not run'}))
