from pathlib import Path
import json,csv
P=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
n=read(P/'TAURUS-NATIVE-FIRST-PASS.json')
printed=['Diamant','Aguquiriaz','Camorica','Fuludia','Albarquiz','Raconic','tira los huesos','Meneffi','Zumberic','Zamorat','Coral','Coral negro','Nericech','Debaran','parece en la mar','Zamorat','Zavarger','Alambari','Querc','del algodon','fuye del vino','Atarráz','Aliaza','Fierro','Articam','fallan en la cabeza de la liebre','fallan al home','Iotarican','Aliaza','Camiruca']
modern=['diamante','aguquiriaz','camorica','fuludia','abarquid','raconie','tira los huesos','meneffi','zumberie','zamoricaz','coral','coral negro','nerizech','de baran','parece en la mar','zamorat','zavarget','ámbar','querc','del algodón','huye del vino','atarraz','aliaza','hierro','articam','hallan en la cabeza de la liebre','hallan al hombre','lotarican','aliaza','camiruca']
pages=[310]*2+[311]*6+[312]*5+[313]*6+[314]*3+[315]*5+[316]*3
rows=[]
for i,r in enumerate(n['rows']):
 rows.append(dict(degree=i+1,sign='Taurus',native=r,edition1881=dict(heading_name=printed[i],pdf_page=pages[i],printed_page=pages[i]-302,visual_checked=True,reading_uncertain=(i+1==8),role='1881 transcription of same witness'),modernized=dict(heading_name=modern[i],role='modernized locator, not separate witness'),editorial_layers_differ=printed[i].casefold()!=modern[i],body_variants=({10:['Zamoricaz'],17:['Zavarpet'],28:['Lotarican']}).get(i+1,[]),body_variants_status='Printed1881 body readings, not additional medieval witnesses',alias_completeness='NOT_EXHAUSTIVE',scientific_admission=False))
out=dict(status='THIRTY_DEGREE_FIRST_PASS_WITH_UNCERTAINTIES',complete_native_paleographic_collation=False,independent_review=False,native_uncertain_degrees=[r['degree'] for r in rows if r['native']['uncertain']],rows=rows)
(P/'TAURUS-SPELLING-COLLATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with (P/'TAURUS-SPELLING-TABLE.tsv').open('w',encoding='utf8',newline='') as fp:
 w=csv.writer(fp,delimiter='\t');w.writerow(['degree','native_excerpt','native_uncertain','folio','column','1881_heading','modernized_heading','1881_pdf_page'])
 for r in rows:w.writerow([r['degree'],r['native']['reading'],r['native']['uncertain'],r['native']['folio'],r['native']['column'],r['edition1881']['heading_name'],r['modernized']['heading_name'],r['edition1881']['pdf_page']])
s=read(P/'STATUS.json');s['status']='SOURCE_COLLATION_SUPPLEMENT_NOT_FULL_COLLATION';s['scope']='Aries30 + Taurus30 native first passes and sparse block transitions; complete30 Greek roster in native-script editions and reported witness apparatus';s['Taurus_degrees_first_pass']=30;s['Taurus_native_uncertain']=len(out['native_uncertain_degrees']);s['Taurus_editorial_disagreements']=sum(r['editorial_layers_differ'] for r in rows);s['Lapidary_native_degree_entries_first_pass']=60;s['next_native_work']=['Aries uncertain readings1,5,20,21,23,26 and Taurus5,6,9,10,13,17,18,28: paleographic adjudication','Gemini full native rubric collation, then remaining complete degree blocks','Exhaustive language aliases and body-versus-rubric spellings','Direct Greek manuscript images and independent review'];(P/'STATUS.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(Taurus_rows=30,Taurus_native_uncertain=s['Taurus_native_uncertain'],Taurus_editorial_disagreements=s['Taurus_editorial_disagreements'])))
