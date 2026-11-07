from pathlib import Path
from collections import Counter,defaultdict
from PIL import Image,ImageDraw
from html.parser import HTMLParser
import json,hashlib,html
P=Path(__file__).resolve().parent; OLD=P.parent/'zodiac-mapping-v84'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(P/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
def esc(v):return html.escape(str(v))
freeze=load(P/'OBSERVATION-FREEZE.json')
for n,h in freeze['sha256'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
old={r['id']:r for panel in load(OLD/'ANNOTATIONS.json') for r in panel['rows']}; new=load(P/'OBSERVATIONS.json')
assert hashlib.sha256((OLD/'ANNOTATIONS.json').read_bytes()).hexdigest()==load(P/'AUDIT-PROTOCOL.json')['inventory_sha256']
changes=[]; groups=defaultdict(list)
for r in new:
    groups[(r['folio'],r['group'])].append(r)
    for f in ['body','enclosure']:
        if old[r['id']][f]!=r[f]:changes.append({'id':r['id'],'feature':f,'old':old[r['id']][f],'new':r[f],'evidence':r[f+'_evidence'],'sheet':r['sheet']})
summary=[]
for (folio,group),rr in groups.items():
    obj={'folio':folio,'group':group,'n':len(rr),'eligible_v87':folio not in ['f70v2','f72v3']}
    for f in ['body','enclosure']:
        c=Counter(r[f] for r in rr);obj[f]={'counts':{'unresolved' if k is None else k:v for k,v in c.items()},'mixed_known':len({r[f] for r in rr if r[f] is not None})>1}
    summary.append(obj)
status={'same_agent_visual_audit':True,'independent_annotator':False,'degree_sequences_consulted_this_audit':False,'alignment_scored':False,'heldout_images_opened':False,'locations_reviewed':len(new),'old_inventory_unchanged':True,'feature_changes':len(changes),'changed_locations':len({r['id'] for r in changes}),'new_body_unknown':sum(r['body'] is None for r in new),'new_enclosure_unknown':sum(r['enclosure'] is None for r in new),'eligible_mixed_body_groups':sum(r['eligible_v87'] and r['body']['mixed_known'] for r in summary),'eligible_mixed_enclosure_groups':sum(r['eligible_v87'] and r['enclosure']['mixed_known'] for r in summary),'interpretation':'First-pass clothing uniformity was partly an annotation artifact. Enclosure remains uniform among known eligible cases. No table alignment claim.'}
dump('CHANGES.json',changes);dump('GROUPS.json',summary);dump('STATUS.json',status)
# Four visual receipts: two within-ring clothing contrasts, no table values.
manifest={r['id']:r for r in load(P/'CROP-MANIFEST.json')}
selected=[('f70v1-outer-01','Bare torso'),('f70v1-outer-04','Garment'),('f72r2-outer-08','Bare torso'),('f72r2-outer-10','Garment')]
canvas=Image.new('RGB',(900,940),'#eee6d4');d=ImageDraw.Draw(canvas)
for j,(id,label) in enumerate(selected):
    r=manifest[id];im=Image.open(OLD/r['source']).crop(r['box']).rotate(r['rotation'],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(235,225,204)); im.thumbnail((430,420));x=(j%2)*450;y=(j//2)*470
    canvas.paste(im,(x+(450-im.width)//2,y+40+(420-im.height)//2)); d.text((x+10,y+10),id+' : '+label,fill='black')
canvas.save(P/'clothing-evidence.jpg',quality=95)
css='body{font:17px/1.55 system-ui;background:#111d25;color:#e9eeee;max-width:1180px;margin:auto;padding:32px}h1,h2{color:#a8e5ce}a{color:#9cd4f5}.box{padding:20px;background:#293d47;border-left:5px solid #d7b775}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}td,th{border:1px solid #455962;padding:9px;text-align:left;vertical-align:top}th{background:#243942}img{max-width:100%}summary{cursor:pointer;color:#ace1ca}.scroll{overflow:auto}'
h=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v88 · Image reinspection</title><style>'+css+'</style><h1>Within-ring uniformity: partly an annotation artifact</h1><div class="box"><b>The first-pass clothing labels flattened real differences.</b><br>The reinspection finds both clothed and bare figures in five of the fourteen groups used by v87. Enclosure remains uniform among known figures in those eligible groups. No degree-table alignment was performed.</div><p>This is a second visual audit by the same agent, previously exposed to the first-pass labels and the general table hypothesis. It is not an independently blinded annotation. No degree sequences or alignment fits were consulted during this audit; held-out images were not opened.</p><h2>Direct image evidence</h2><img src="clothing-evidence.jpg" alt="Two pairs of figures from the same rings: bare and clothed examples in f70v1 and f72r2"><p>f70v1 outer-04 has a bounded neckline, chest band and fabric folds. Gemini outer-09 through outer-12 have tunics/dresses; outer-10 had been labelled bare. The images above show one bare/clothed pair from each ring. Crops are rotated for inspection, not redrawn or enhanced.</p><h2>What changes in the previous conclusion</h2><p>v87 correctly found zero within-group variation in the stored first-pass labels. Those labels were not sufficiently faithful to the images. Its statement that no usable clothing variation exists must therefore be withdrawn as a claim about the drawings. The old files and failed application remain preserved. This audit supplies revised candidate observations, not a new p-value or a winning rule.</p><p>Variation is now visible in f70v1 outer, f71r inner, f71v outer and inner, and f72r2 outer. It is localized: the audit does not turn every ring into a variable one. Clothing differences do not establish figure sex, a degree scheme or a reading direction.</p><h2>Coverage and uncertainty</h2>',f'<p>All {len(new)} existing development location records were reviewed. {status["changed_locations"]} locations have a changed classification ({len(changes)} feature-level changes). The revised inventory retains {status["new_body_unknown"]} unresolved torso and {status["new_enclosure_unknown"]} unresolved enclosure classifications. Counts overlap and are not counts of distinct uncertain figures.</p>', '<p>Pisces remains excluded at 29 locations. Its inner green-sided forms are now explicitly unresolved as containing vessels versus adjacent structures. Leo’s fold location remains uncertain presence; the audit does not supply a thirtieth figure. Pigment and label ownership were not classified. Known enclosure values remain uniform within all fourteen eligible groups.</p><h2>Groups: known classifications and unknowns</h2><div class="scroll"><table><tr><th>Folio / group</th><th>Torso</th><th>Mixed known torso?</th><th>Enclosure</th><th>Eligible in v87?</th></tr>']
for r in summary:h.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [r['folio']+' / '+r['group'],r['body']['counts'],r['body']['mixed_known'],r['enclosure']['counts'],r['eligible_v87']])+'</tr>')
h+=['</table></div><h2>Every changed classification</h2><table><tr><th>Figure / feature</th><th>First pass</th><th>Reinspection</th><th>Image evidence</th></tr>']
for c in changes:h.append(f'<tr><td><a href="{c["sheet"]}">{c["id"]}</a> / {c["feature"]}</td><td>{esc(c["old"] or "unresolved")}</td><td>{esc(c["new"] or "unresolved")}</td><td>{esc(c["evidence"])}</td></tr>')
h+=['</table><h2>Audit trail and limitations</h2><p>Contact sheets omit old feature values and table information, but location IDs and existing geometry are retained. The old annotation script was inspected for coordinate metadata and exposed its old labels; this prevents claiming full blinding. Observations were saved and hashed before the computed old/new comparison. Ambiguous neck bands and paint were not automatically called garments.</p><p>The initial Leo sheets used the wrong saved crop for its coordinate system. Those misregistered sheets are preserved under misregistered-leo and excluded as evidence. Corrected sheets use the original wide-image coordinate system and local figure crops. No held-out panel was opened.</p><p><a href="OBSERVATIONS.json">All new observations and evidence</a> · <a href="OBSERVATION-FREEZE.json">Observation freeze</a> · <a href="CHANGES.json">Complete change ledger</a> · <a href="GROUPS.json">Group counts</a> · <a href="AUDIT-PROTOCOL.json">Audit method</a> · <a href="LEO-CROP-CORRECTION.json">Leo crop failure/correction</a> · <a href="../zodiac-mapping-v84/ANNOTATIONS.json">Unchanged first-pass inventory</a></p><h2>Development-only inspection sheets</h2>']
for folio in ['f70v1','f71r','f71v','f72r1','f70v2','f72r2','f72r3','f72v3']:
    h.append('<details><summary>'+folio+'</summary>')
    for f in sorted(P.glob(folio+'-*.jpg')):h.append(f'<img loading="lazy" src="{f.name}" alt="{folio} development inspection sheet">')
    h.append('</details>')
h+=['<h2>Held-out boundary</h2><p>Virgo, Libra, Scorpio and Sagittarius remain untouched by this audit. Any subsequent alignment should use a separately frozen revised input, preserving these ambiguous alternatives and recognizing that actual within-ring variation is concentrated in a few groups. No new rule or score is implied here.</p></html>']
s='\n'.join(h);(P/'report.html').write_text(s,encoding='utf-8')
class QA(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src']:assert (P/v).exists(),v
QA().feed(s);assert s.count('<table')==s.count('</table>')
dump('SHA256SUMS.json',{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in str(p)})
print(json.dumps(status,indent=2))
