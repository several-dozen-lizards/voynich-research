"""Build unfilled, metadata-only preparation templates. No EVA payload input."""
from pathlib import Path
import json,hashlib,csv,shutil,datetime
from PIL import Image
P=Path(__file__).resolve().parent; B=P.parent; ROOT=B.parent
OPEN=('f70v1','f71r','f71v','f72r1','f70v2','f72r2','f72r3','f72v3')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
R=P/'registration';R.mkdir(exist_ok=True);(R/'images').mkdir(exist_ok=True)
anns=read(ROOT/'zodiac-mapping-v84/ANNOTATIONS.json')
flags=read(B/'amendment-v7.3/READABILITY-FLAGS.json')
meta=read(B/'C2-open-v1/METADATA-INVENTORY.json')['units']
images={'f70v1':'f70v1.jpg','f71r':'f71r.jpg','f71v':'f71v.jpg','f72r1':'f72r1.jpg','f70v2':'f70v2.jpg','f72r2':'f72r2.jpg','f72r3':'f72r3-expanded.jpg','f72v3':'leo-wide.jpg'}
manifest=[];figures=[]
for panel in anns:
 folio=panel['folio'];assert folio in OPEN
 src=ROOT/'zodiac-mapping-v84'/images[folio];dst=R/'images'/images[folio]
 shutil.copyfile(src,dst)
 with Image.open(dst) as im:w,h=im.size
 local=folio=='f72r3'
 reg=panel['region']
 manifest.append(dict(folio=folio,sign=panel['sign'],image='images/'+images[folio],sha256=sha(src),bytes=src.stat().st_size,image_pixels=[w,h],upstream_source=str(src),v84_oid=panel['oid'],v84_region=reg,old_point_coordinates=('local image pixels' if local else 'v84 original source pixels'),old_point_to_display=('identity' if local else dict(x='(x-region[0])*image_width/region[2]',y='(y-region[1])*image_height/region[3]')),warning='Transform is a coordinate contract from v84 metadata, not an independently checked pixel registration. Verify image framing before accepting boxes.',frame_verified=False))
 for row in panel['rows']:
  figures.append(dict(figure_id=row['id'],folio=folio,band=row['group'],v84_index=row['index'],v84_head_hint=row['head'],v84_label_hint=row['label_anchor'],uncertain_presence=row.get('presence'),hint_status='UNVALIDATED_CANDIDATE_NOT_OWNERSHIP',figure_bbox=None,physical_label_id=None,label_bbox=None,source_locus_id=None,association_status='UNREVIEWED',alternatives=[],reviewer=None,evidence=None))
# Source headers only: H union K flags plus H locator lists. S0 is absent from frozen flags.
tasks={}
for f in flags:
 if f['folio'] not in OPEN or f['reading'] not in ('H','K') or not f['unit'].split('.')[-1].startswith('S'):continue
 t=tasks.setdefault(f['id'],dict(source_locus_id=f['id'],folio=f['folio'],source_unit=f['unit'],H=None,K=None))
 t[f['reading']]=dict(present=True,readable=f['readable'],header_line=f['source_line'],basis='frozen readability flags')
for u in meta:
 if u['folio'] not in OPEN or not u['code'].startswith('S'):continue
 for loc in u['HF_locators']['H']:
  ident=u['unit']+'.'+loc
  t=tasks.setdefault(ident,dict(source_locus_id=ident,folio=u['folio'],source_unit=u['unit'],H=None,K=None))
  if t['H'] is None:t['H']=dict(present=True,readable=None,header_line=None,basis='frozen H header inventory; not C2-ranked')
labels=[]
for k in sorted(tasks):
 t=tasks[k];t.update(physical_label_id=None,label_bbox=None,figure_id=None,reviewer=None,evidence=None,status='UNREVIEWED');labels.append(t)
# Only retained spatial/order cues; original comments contain glyph content and must not leak.
guides=[]
for u in meta:
 if u['folio'] not in OPEN or not u['code'].startswith('S'):continue
 cues=[]
 for s in u['comments']:
  low=s.lower()
  if any(q in low for q in ('transcribed clockwise','transcription starting','transcription is clockwise','transcribed left to right','numbers by john grove','outer ring','inner ring','outer band','inner band','middle','outside the diagram')) or (':' in s and all(c in '0123456789: ' for c in s)):
   cues.append(s)
 guides.append(dict(source_unit=u['unit'],spatial_cues=cues,warning='Archive spatial notes only; not independently verified ownership or exact locator-to-point correspondence. No raw comment or EVA payload supplied.'))
save(R/'PAGES.json',manifest);save(R/'FIGURE-TASKS.json',figures);save(R/'LOCUS-TASKS.json',labels);save(R/'HEADER-ORDER-GUIDE.json',guides)
for name in ('PASS-A-TEMPLATE.json','PASS-B-TEMPLATE.json'):
 save(R/name,dict(status='UNFILLED_NOT_INDEPENDENT_REGISTRATION',reviewer=None,prior_exposure=None,independent_of_other_pass=None,figure_decisions=figures,locus_decisions=labels))
with (R/'DECISIONS-TEMPLATE.csv').open('w',encoding='utf8',newline='') as fp:
 wr=csv.writer(fp);wr.writerow(['folio','figure_id','physical_label_id','source_locus_id','label_bbox_x','label_bbox_y','label_bbox_width','label_bbox_height','coordinate_space','status','alternatives','reviewer','evidence'])
 for f in figures:wr.writerow([f['folio'],f['figure_id'],'','','','','','','local image pixels','UNREVIEWED','','',''])
# All positions remain blank. This is a source collation worksheet, not a list profile.
signs=('Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces')
save(P/'historical-sources/LAPIDARY-COLLATION-TEMPLATE.json',dict(status='UNFILLED_NOT_ADMITTED',unit='stone attached to explicit zodiac degree',witness='RBME h-I-15',rows=[dict(sign=s,degree=d,folio=None,column=None,line=None,canvas=None,degree_attestation=None,native_name=None,name_or_descriptor=None,language=None,aliases=[],normalized_form=None,normalization_steps=[],source_gap=None,theophoric_suffix=None,reviewer=None) for s in signs for d in range(1,31)]))
save(P/'historical-sources/WRONG-UNIT-COLLATION-TEMPLATE.json',dict(status='UNFILLED_NEGATIVE_CONTROL_CANDIDATE_ONLY',source='Xenophon Hellenica II.3.2',unit='person in political roster',rows=[dict(source_order=i,Greek_name=None,manuscript=None,folio=None,edition_locus=None,variants=[],transliteration=None,reviewer=None) for i in range(1,31)]))
save(P/'STATUS.json',dict(status='REVISED_PLAN_AND_UNFILLED_REGISTRATION_PACKET_READY',scientific_admission=False,new_source_profiles_admitted=0,completed_registration_passes=0,C3_fits=0,C3_scientific_qualification='NOT_RUN',C2_looks_used=6,C2_look_cap=10,eligible_C_arms=['C-FULL','C-STEM','C-MRK'],alpha_each='1/1200',vault_open=False,vault_authorized=False,unresolved=['Native source sequence and variant collation','Independent physical registration','Adoption of revised source/model contract','Full scientific qualification'],packet_counts=dict(open_panels=len(manifest),candidate_figure_tasks=len(figures),source_locus_tasks=len(labels))))
print(json.dumps(dict(panels=len(manifest),figure_tasks=len(figures),locus_tasks=len(labels),images=[dict(folio=x['folio'],pixels=x['image_pixels']) for x in manifest])))
