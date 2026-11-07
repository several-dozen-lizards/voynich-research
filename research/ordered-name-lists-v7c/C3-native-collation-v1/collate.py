"""Source-only collation supplement. No Voynich, fitting, or vault dependency."""
from pathlib import Path
import json,re,unicodedata,hashlib,csv
P=Path(__file__).parent;OLD=P.parent/'C3-revised-plan-v1/historical-sources'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def normal(s):return ' '.join(s.casefold().split())
# Contents order is not used to invent a source degree when a degree attestation is absent.
groups=read(P/'MODERNIZED-CONTENTS-GROUPS.json')['groups']
signmap={'Aries':'Aries','Tauro':'Taurus','Géminis':'Gemini','cancro':'Cancer','León':'Leo','Virgo':'Virgo','Libra':'Libra','Escorpión':'Scorpio','Sagitario':'Sagittarius','Capricornio':'Capricorn','Acuario':'Aquarius','Piscis':'Pisces'}
ordered=[]
for source_sign,heads in groups.items():
 for j,h in enumerate(heads,1):ordered.append(dict(sign=signmap[source_sign],source_heading=h,contents_position=j,degree_candidate=30 if source_sign=='León' else j+28 if source_sign=='Piscis' else j,degree_candidate_basis='explicit degree formula checked for sparse Leo/Pisces; contents order otherwise pending individual native confirmation',native_verified=False))
assert len(ordered)==301
save(P/'LAPIDARY-CONTENTS-INVENTORY.json',dict(status='MODERNIZED_LOCATOR_NOT_CLAIM_LIST',total_contents_entries=len(ordered),rows=ordered))
# Preserve every degree slot. Never build a compressed 301-position or repaired360 profile.
slots=[]
for sign in signmap.values():
 for d in range(1,31):
  found=[x for x in ordered if x['sign']==sign and x['degree_candidate']==d]
  assert len(found)<=1
  slots.append(dict(sign=sign,degree=d,locator_heading=found[0]['source_heading'] if found else None,source_status='LOCATOR_ENTRY_NOT_NATIVE_CERTIFIED' if found else 'NOT_REPRESENTED_IN_COLLATION_SOURCES',gap_cause='not inferred',claim_name=None))
save(P/'LAPIDARY-360-SLOT-AUDIT.json',dict(status='GAPS_RETAINED_NO_RECONSTRUCTION',slots=slots,represented_locator_slots=sum(x['locator_heading'] is not None for x in slots),unrepresented_slots=sum(x['locator_heading'] is None for x in slots),missing=[dict(sign=x['sign'],degree=x['degree']) for x in slots if x['locator_heading'] is None],limits=['Contents order is a locator, not native degree verification of all301 entries.','Cross-references in later treatises are recorded separately, never used to silently fill gaps.','No cause, date or physical leaf count of a gap inferred from its degree count.']))
# Printed transcription was checked visually on PDF304–309 / printed2–7.
printed=['Magnetat','Zurudica','Gagatiz','Miliztiz','Ceritiz','Movedor','Goliztiz','Telliminuz','Milititaz','fuye de la leche','Aliofar','Anetatiz','Beruth','Piedra de Cin','tira el oro','chupa la sangre','parece en la mar cuando sube Mars','tira el vidrio','Annora','Izf','Tuminon','Astarnuz','Belinniz','Gaciuz','Azufaratiz','Abietitiz','Lubi','Zeraquiz','Bedunaz','Annoxatir']
modern=['magnitad','zurudica','gagatiz','miliztiz','centiz','movedor','goliztiz','telliminuz','milititaz','huye de la leche','aljófar','anetatiz','beruth','piedra de cinc','tira el oro','chupa la sangre','parece en la mar cuando sube Marte','tira el vidrio','annora','yzf','cuminon','astarnuz','belyniz','gaciuz','azufaratiz','abietityz','lubi','ceraquiz','berlimaz','annoxatir']
pdfpages=[304]*3+[305]*6+[306]*5+[307]*6+[308]*5+[309]*5
native=read(P/'ARIES-NATIVE-FIRST-PASS.json')
rows=[]
for i,n in enumerate(native['rows']):
 rows.append(dict(degree=i+1,sign='Aries',unit='degree-associated stone name or descriptor',kind=n['kind'],native=dict(name_excerpt=n['reading'],folio=n['folio'],column=n['column'],image=n['native_image'],uncertain=n['uncertain'],note=n.get('note'),normalization=native['normalization']),edition1881=dict(heading_name=printed[i],pdf_page=pdfpages[i],printed_page=pdfpages[i]-302,visual_checked=True,role='non-paleographic transcription, not independent witness'),modernized=dict(heading_name=modern[i],role='modernized locator, not independent medieval witness'),editorial_layers_differ=normal(printed[i])!=normal(modern[i]),alias_completeness='NOT_EXHAUSTIVE',theophoric_analysis='NOT_INFERRED',scientific_admission=False))
save(P/'ARIES-SPELLING-COLLATION.json',dict(status='THIRTY_DEGREE_FIRST_PASS_WITH_UNCERTAINTIES',complete_native_paleographic_collation=False,independent_review=False,uncertain_native_degrees=[r['degree'] for r in rows if r['native']['uncertain']],rows=rows,source_relationship='One medieval witness, its1881 transcription and a modernized text. Three representations are not three witnesses.'))
with (P/'ARIES-SPELLING-TABLE.tsv').open('w',encoding='utf8',newline='') as fp:
 w=csv.writer(fp,delimiter='\t');w.writerow(['degree','native_excerpt','native_uncertain','folio','column','1881_heading','modernized_heading','1881_pdf_page'])
 for r in rows:w.writerow([r['degree'],r['native']['name_excerpt'],r['native']['uncertain'],r['native']['folio'],r['native']['column'],r['edition1881']['heading_name'],r['modernized']['heading_name'],r['edition1881']['pdf_page']])
# Greek roster: complete30 names in both printed Hatzfeld1936 and Marchant digital edition.
greek=read(P/'GREEK-ROSTER-EXTRACT.json')['rows']
alpha=dict(zip('αβγδεζηθικλμνξοπρσςτυφχψω',['a','b','g','d','e','z','e','th','i','k','l','m','n','x','o','p','r','s','s','t','y','ph','ch','ps','o']))
def transliterate(name):
 d=unicodedata.normalize('NFD',name.casefold());h='h' if len(d)>1 and '\u0314' in d[:4] else ''
 chars=[c for c in d if not unicodedata.combining(c)]
 return h+''.join(alpha[c] for c in chars)
for i,r in enumerate(greek):
 r['Hatzfeld1936_visual_checked']=True;r['Hatzfeld_pdf_pages']=[133] if i<17 else [133,135] if i==17 else [135]
 r['Hatzfeld_section']='2.3.2';r['Hatzfeld_printed_pages']=[82] if i<17 else [82,83] if i==17 else [83]
 r['ASCII_working_form']=transliterate(r['name']);r['ASCII_status']='DERIVED_ENGINEERING_FORM_NOT_ATTESTED_LATIN_SPELLING_NOT_ADOPTED_FOR_SCORING'
 r['pre1440_witness_support']='Hatzfeld negative-apparatus convention reports main text for B/M absent a rejected reading; not direct image collation'
late=[dict(position=1,adopted='Πολυχάρης',variant='πολυαρχης',variant_transcription_note='Apparatus letter sequence; capitalization and accent not certified as diplomatic manuscript data',witness='C: Parisinus2080',date='mid15th century',status='EXCLUDED_FROM_PRE1440_VARIANTS',source='Hatzfeld1936 PDF133 printed82 apparatus line4; witness-date PDF28'),dict(position=22,adopted='Θεογένης',variant='θεαγ.',variant_transcription_note='Apparatus prints an abbreviation; no full name spelling supplied or admitted',witness='V: Marcianus368',date='mid15th century',status='EXCLUDED_FROM_PRE1440_VARIANTS',source='Hatzfeld1936 PDF135 printed83 apparatus line8; witness-date PDF28')]
profiles=[]
for witness,date in [('B: Parisinus1738','early14th century'),('M: AmbrosianusA4inf','1344')]:
 profiles.append(dict(witness=witness,date=date,names=[r['name'] for r in greek],evidence_type='EDITOR_REPORTED_WITNESS_PROFILE',basis='Hatzfeld1936 PDF28 gives negative-apparatus convention; roster main text PDF133/135, no B/M rejected name reading noted there.',direct_manuscript_image_collation=False,independent_review=False,scientific_admission=False))
save(P/'WRONG-UNIT-GREEK-COLLATION.json',dict(status='COMPLETE_NATIVE_SCRIPT_EDITION_COLLATION_NOT_DIPLOMATIC_MANUSCRIPT',unit='person in political roster',source_order_type='enumeration order, not appointment chronology',rows=greek,witness_profiles=profiles,late_apparatus_variants=late,pre1440_new_spelling_alternatives_verified=0,variants_exhaustive=False,riemann_check=dict(page=137,scope='No separate II.3.2/3 name variant is listed; reported agreement is against Sauppe1866, not direct proof of agreement with Marchant or Hatzfeld.',constant_orthography_caveat='Riemann says recurring orthographic differences may be reported once elsewhere. No exhaustive variant claim.'),transliteration=dict(status='WORKING_PROPOSAL_NOT_SCORING_ADMISSION',algorithm='Unicode NFD; lowercase; initial rough breathing=>h; strip combining marks; fixed Greek-letter table.',table=alpha,phonetic_claim=False),scientific_admission=False))
print(json.dumps(dict(locator_entries=len(ordered),unrepresented_degree_slots=sum(x['locator_heading'] is None for x in slots),Aries_rows=len(rows),Aries_native_uncertainties=sum(x['native']['uncertain'] for x in rows),editorial_layer_disagreements=sum(x['editorial_layers_differ'] for x in rows),Greek_names=len(greek),late_variants_excluded=len(late))))
