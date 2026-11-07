"""Image readback entered by the inspecting agent; no degree-table imports."""
from pathlib import Path
import json,hashlib,time
P=Path(__file__).resolve().parent
# Every character is a separately inspected location in existing ordinal order.
# B bare / G garment / ? unresolved; V vessel / N absent / ? unresolved.
READINGS={
'f70v1':{'outer':('BBBGBBB?BB','VVVVVVVVVV'),'inner':('?BBBB','VVVVV')},
'f71r':{'outer':('GGGGGGGGGG','VVVVVVVVVV'),'inner':('GG?BG','VVVVV')},
'f71v':{'outer':('GGGGBB?GGG','VVVVVVVVVV'),'inner':('GGBGG','VVVVV')},
'f72r1':{'outer':('BBBBBBBBBB','NNNNNNNNNN'),'inner':('BBBBB','VVVVV')},
'f70v2':{'outer':('BBBBBBBBBBBBBBBBBBB','VVVVVVVVVVVVVVVVVVV'),'inner':('BBBBBB?B?B','??????????')},
'f72r2':{'extra-top':('?BBBB','NNNNN'),'outer':('BBBBBBBBGGGG?BBB','NNNNNNNNNNNNNNNN'),'inner':('BBBBBBBBB','NNNNNNNNN')},
'f72r3':{'outer':('BB?BBBBB??BB','NN?NNNNNNNNN'),'middle':('BB???BBB?BB','NN???NNNNNN'),'inner':('BBBBBBB','NNNNNNN')},
'f72v3':{'outer':('BBBBBBBBBBBBBBB?BB','NNNNNNNNNNNNNNN?NN'),'inner':('BBBBBBBBB??B','NNNNNNNNN??N')}
}
NOTES={
'f70v1-outer-04':'Clear bounded neckline, horizontal chest band and vertical fabric folds/sleeve outline: garment, not naked torso.',
'f70v1-outer-06':'Enlarged view shows breast/anatomical strokes and continuous torso; do not treat the shoulder/neck line alone as a garment.',
'f70v1-outer-08':'Neck/chest band-like strokes could be collar or anatomical line; enlargement does not settle clothing. Downgraded to unresolved.',
'f70v1-inner-01':'Oblique torso with a band-like/dotted chest line. Garment versus exposed torso not secure at saved resolution.',
'f71r-outer-04':'Patterned bounded bodice and sleeve visible despite pale/red strokes.',
'f71r-inner-03':'Green torso area alone is insufficient evidence for clothing; neckline/anatomy remains unclear.',
'f71r-inner-04':'Exposed breasts and torso contour clearly visible above containing rim; bare torso among clothed inner-ring figures.',
'f71v-outer-05':'Breast/anatomical contour exposed above vessel; no garment boundary visible.',
'f71v-outer-06':'Exposed breasts and abdominal contour above rim.',
'f71v-outer-07':'Horizontal torso stripes could be garment, but faint drawing does not confidently establish anatomy or textile boundary.',
'f71v-inner-02':'Layered bodice bands and red sleeve edge visible.',
'f71v-inner-03':'Clear bare breast/torso strokes above rim; hat does not imply clothing on torso.',
'f71v-inner-04':'Red sleeve and bounded, patterned torso garment visible.',
'f72r1-inner-05':'Hole obscures raised-arm/label area, but exposed torso to its left and vessel rim/walls below remain visible. Label ownership still uncertain.',
'f72r2-extra-top-01':'Fold overlaps upper figure; lower body readable but torso clothing cannot confidently be classified.',
'f72r2-outer-09':'Bounded waist, sleeves and pleated short tunic/skirt; object under feet is not a containing vessel.',
'f72r2-outer-10':'Sleeved upper garment and layered skirt/hem; feet rest on rounded support, not inside a tub.',
'f72r2-outer-11':'Long patterned dress with defined waist and fabric contours; no containing vessel.',
'f72r2-outer-12':'Flared tunic/skirt and sleeve outlines; clothing visible despite nearby fold.',
'f72r2-outer-13':'Torso near fold is too faint to distinguish garment or bare anatomy securely.',
'f72v3-outer-16':'Fold-obscured candidate location; individual identity/presence remains uncertain. No confirmed thirtieth figure supplied.'
}
old=json.loads((P.parent/'zodiac-mapping-v84/ANNOTATIONS.json').read_text(encoding='utf-8'))
out=[]
for panel in old:
    counters={}
    for r in panel['rows']:
        group=r['group']; i=r['index']-1; body,enclosure=READINGS[panel['folio']][group]
        assert len(body)==len(enclosure)==sum(x['group']==group for x in panel['rows'])
        b,e=body[i],enclosure[i]
        evidence=NOTES.get(r['id'],'')
        if not evidence:
            evidence={'B':'Visible exposed torso contour/anatomical strokes; no garment structure established.','G':'Bounded garment with neckline/sleeve or fabric pattern visible.','?':'Torso obscured, faint or insufficiently resolved; leave unknown.'}[b]
        ee={'V':'Rim and containing vessel wall visible around lower body.','N':'Lower body/legs visible without a containing vessel; a support or border is not counted as enclosure.','?':'Containing relation or relevant contour cannot be securely read.'}[e]
        if panel['folio']=='f70v2' and group=='inner': ee='Horizontal green-sided forms lie alongside/behind figures; the image does not securely establish that they contain the lower body. Keep containing-versus-adjacent unresolved.'
        ordinal=next(j for j,x in enumerate(panel['rows']) if x['id']==r['id'])
        out.append({'id':r['id'],'folio':panel['folio'],'group':group,'index':r['index'],'body':{'B':'bare torso visible','G':'garment visible','?':None}[b],'enclosure':{'V':'enclosing vessel visible','N':'no enclosing vessel visible','?':None}[e],'body_evidence':evidence,'enclosure_evidence':ee,'sheet':f'{panel["folio"]}-{ordinal//12+1}.jpg','presence':'uncertain' if r['id']=='f72v3-outer-16' else 'existing location retained','label_status':'not re-read or reassigned','pigment_status':'not classified'})
assert len(out)==179 and len({r['id'] for r in out})==179
(P/'OBSERVATIONS.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(P/'OBSERVATION-FREEZE.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Save image observations before computed old/new comparison. Same agent previously exposed to original labels; not independently blinded. No degree sequences consulted and no alignment scoring.','sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['OBSERVATIONS.json','observations.py','AUDIT-PROTOCOL.json','CROP-MANIFEST.json','LEO-CROP-CORRECTION.json']}},indent=2),encoding='utf-8')
print('179 image observations saved and frozen; no old/new feature comparison computed yet.')
