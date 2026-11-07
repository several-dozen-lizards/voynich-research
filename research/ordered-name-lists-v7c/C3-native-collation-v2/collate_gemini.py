"""Historical source collation only; no Voynich input or scoring."""
from pathlib import Path
import json,csv,hashlib
P=Path(__file__).parent;V1=P.parent/'C3-native-collation-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
n=read(P/'GEMINI-NATIVE-FIRST-PASS.json')
printed=['Zarocan','del oro','Barcaduniticaz','tira la carne','Margul','Lurita','de la Sirpiente','del suenno','Bezahar','Bezahar','Bezahar','Coloquia','tira el vino','Taroc','Quedoritoz','Siphe','parece en la mar','Hetora','fallan en el vientre de la golondrina','Koloquid','Tarmicon','Gemezt','Camiulicaz','Mecelucan','tira el sebo','diente de cangreyo marino','Batocita','del figado','torna el agua sangre','Maduz']
modern=['zarocan','del oro','barcaduniticaz','tira la carne','margul','lurita','de la serpiente','del sueño','bezaar','bezaar','bezaar','coloquia','tira el vino','taroc','quedoritoz','siphe','parece en la mar','hetora','hallan en el vientre de la golondrina','koloquid','tarmicon','gemezt','camyulicaz','mecelucan','tira el sebo','diente de cangrejo marino','batocita','del hígado','torna el agua sangre','maduz']
pages=[317]*4+[318]*5+[319]*4+[320]*5+[321]*5+[322]*6+[323]
heads=read(V1/'MODERNIZED-CONTENTS-GROUPS.json')['groups']['Géminis']
rows=[]
for i,r in enumerate(n['rows']):
 rows.append(dict(sign='Gemini',degree=i+1,native=r,edition1881=dict(heading_name=printed[i],pdf_page=pages[i],printed_page=pages[i]-302,visual_checked=True,role='non-paleographic transcription of same witness',qualifier='second variety' if i==9 else None),modernized=dict(heading_name=modern[i],full_contents_heading=heads[i],role='modernized locator, not independent witness'),editorial_layers_differ=printed[i].casefold()!=modern[i],body_variants=['Kedoritoz'] if i==14 else [],body_variant_basis='1881 first paragraph; native initial remains under review' if i==14 else None,alias_completeness='NOT_EXHAUSTIVE',theophoric_analysis='NOT_INFERRED',scientific_admission=False))
out=dict(status='THIRTY_DEGREE_FIRST_PASS_WITH_UNCERTAINTIES',complete_native_paleographic_collation=False,independent_review=False,source_relationship='One medieval witness, its1881 transcription and modernized text; not three independent witnesses.',native_uncertain_degrees=[r['degree'] for r in rows if r['native']['uncertain']],duplicate_name_slots=[9,10,11],source_order='Explicit degree statements, not OCR paragraph sequence or name deduplication',rows=rows)
save(P/'GEMINI-SPELLING-COLLATION.json',out)
with (P/'GEMINI-SPELLING-TABLE.tsv').open('w',encoding='utf8',newline='') as fp:
 w=csv.writer(fp,delimiter='\t');w.writerow(['degree','native_excerpt','native_uncertain','folio','column','1881_heading','modernized_heading','1881_pdf_page','source_qualifier'])
 for r in rows:w.writerow([r['degree'],r['native']['reading'],r['native']['uncertain'],r['native']['folio'],r['native']['column'],r['edition1881']['heading_name'],r['modernized']['heading_name'],r['edition1881']['pdf_page'],r['native']['qualifier']])
# Aggregate by provenance references. Old records remain immutable; revisions are explicit overlays.
aggregate=[];review=read(P/'PRIOR-READING-REINSPECTION.json')
for sign,file in [('Aries','ARIES-SPELLING-COLLATION.json'),('Taurus','TAURUS-SPELLING-COLLATION.json'),('Gemini','GEMINI-SPELLING-COLLATION.json')]:
 source=P/file if sign=='Gemini' else V1/file
 for r in read(source)['rows']:
  native=r['native'];value=native.get('name_excerpt',native.get('reading'));overlay=next((x for x in review['rows'] if x['sign']==sign and x['degree']==r['degree']),None)
  aggregate.append(dict(sign=sign,degree=r['degree'],source_record=str(source),original_native_excerpt=value,working_native_excerpt=overlay['working_reading'] if overlay else value,working_body_excerpt=overlay['body_reading'] if overlay else None,uncertain=overlay['still_uncertain'] if overlay else native['uncertain'],overlay='PRIOR-READING-REINSPECTION.json' if overlay else None,kind=r.get('kind',native.get('kind')),scientific_admission=False))
save(P/'CUMULATIVE-NATIVE-90.json',dict(status='SOURCE_WORK_INDEX_NOT_FROZEN_SCORING_PROFILE',rows=aggregate,native_first_pass_entries=90,uncertain_entries=sum(r['uncertain'] for r in aggregate),preserved_C1_universe=True,new_source_profiles_admitted=0))
status=dict(status='SOURCE_COLLATION_CONTINUED_NOT_COMPLETE',new_native_block='Gemini',new_native_degree_entries=30,cumulative_native_degree_entries=90,Gemini_native_uncertain=len(out['native_uncertain_degrees']),prior_uncertainties_reinspected=14,prior_uncertainties_resolved_for_scoring=0,provisional_prior_working_revisions=4,cumulative_native_uncertain=sum(r['uncertain'] for r in aggregate),Gemini_editorial_disagreements=sum(r['editorial_layers_differ'] for r in rows),source_resolution='899x1348 confirmed by IIIF info; magnification adds no source detail',Greek_control='v1 complete native-script edition roster retained; direct manuscript image collation still pending',source_unrepresented_degree_slots=59,new_scoring_profiles_admitted=0,C2_looks_used=6,C2_look_cap=10,C3_fits=0,vault_open=False,next_work=['Cancer native block, then remaining complete degree blocks','Independent paleographic review of21 uncertain native excerpts','Exhaustive aliases and source-location-specific profile rules','Direct Greek manuscript images and independent review'])
save(P/'STATUS.json',status)
print(json.dumps(status))
