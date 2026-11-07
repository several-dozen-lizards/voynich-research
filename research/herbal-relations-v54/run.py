from pathlib import Path
import json,re,hashlib,collections,html,importlib.util
R=Path(__file__).resolve().parent;P=R.parent
sp=importlib.util.spec_from_file_location('v53',P/'herbal-slots-v53/pilot.py');v53=importlib.util.module_from_spec(sp);sp.loader.exec_module(v53)
def relations(entry):
 assertions=[];out=[]
 for row in entry:
  text=row['text'];sentences=list(re.finditer(r'[^.!?]+(?:[.!?]|$)',text))
  for sm in sentences:
   s=sm.group();slots=v53.extract(s);lower=s.lower()
   planets=slots['planetary_association']
   # Entry attribution must be explicit local reference, not any planet mention.
   attribution=bool(re.search(r'^\s*(?:it|this (?:herb|plant)|the herb)\s+(?:is|belongs)',lower))
   if planets:
    assertions.append({'paragraph':row['paragraph'],'sentence':s.strip(),'planets':[x['value'].lower() for x in planets],'subject':'entry plant' if attribution else 'unresolved','status':'candidate explicit association' if attribution else 'unresolved referent'})
   if not (slots['operation'] or slots['internal_application'] or slots['external_application']):continue
   neg=bool(re.search(r'\b(?:not|never|avoid|without)\b',lower));metaphor=bool(re.search(r'apply (?:yourself|thyself|the rule)',lower))
   current=bool(re.search(r'\b(?:this (?:herb|plant)|(?:juice|leaves|root|seeds|decoction|powder|oil) of (?:it|this herb)|(?:its|their) (?:leaves|roots?|seeds?|juice))\b',lower))
   # Relation remains candidate even with direct coreference; no external gold labels.
   out.append({'paragraph':row['paragraph'],'sentence_span':[sm.start(),sm.end()],'sentence':s.strip(),'materials':slots['ingredient_material'],'preparations':slots['preparation'],'applications':{'internal':slots['internal_application'],'external':slots['external_application']},'entry_ingredient_link':'candidate local reference' if current and not neg and not metaphor else 'unresolved','negation_or_metaphor':neg or metaphor,'preparation_application_link':'candidate same sentence only' if slots['preparation'] and (slots['internal_application'] or slots['external_application']) and not neg and not metaphor else 'unresolved'})
 named={p for a in assertions if a['subject']=='entry plant' for p in a['planets']}
 association=next(iter(named)) if len(named)==1 else None
 for x in out:
  x['context_planet']=association
  x['planet_to_recipe_ingredient']='candidate via entry reference' if association and x['entry_ingredient_link']=='candidate local reference' else 'unresolved'
  x['other_ingredient_planets']='not inferred'
 return {'assertions':assertions,'entry_planet':association,'entry_association_status':'single explicit candidate' if len(named)==1 else 'conflicting or absent','recipes':out}
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 rows=json.loads((P/'herbal-slots-v53/LATER-EXTRACTIONS.json').read_text());by=collections.defaultdict(list)
 for x in rows:by[x['herb']].append(x)
 results=[{'herb':name,'split':es[0]['split'],**relations(es)} for name,es in by.items()]
 (R/'LATER-RELATIONS.json').write_text(json.dumps(results,indent=2),encoding='utf8')
 controls=[('direct','It is under the planet Mercury. Drink the juice of this herb.','candidate via entry reference'),('unrelated ingredient','It is under the planet Mercury. Drink wine.','unresolved'),('negation','It is under the planet Mercury. Do not drink the juice of this herb.','unresolved'),('metaphor','It is under the planet Mercury. Apply yourself to the study of this herb.','unresolved'),('unassigned planet','The sun warms the leaves. Drink the juice of this herb.','unresolved'),('conflicting','It is under the planet Mercury. This herb is under the planet Mars. Drink the juice of this herb.','unresolved'),('pronoun gap','It is under the planet Mercury. Drink it.','unresolved'),('synonym gap','This herb belongs to Venus. Drink the juice of this herb.','candidate via entry reference')]
 checks=[]
 for name,text,expected in controls:
  r=relations([{'paragraph':0,'text':text}]);got=r['recipes'][-1]['planet_to_recipe_ingredient'] if r['recipes'] else 'unresolved';checks.append(dict(name=name,text=text,expected=expected,observed=got,passed=got==expected,kind='authored engineering control, not independent historical validation'))
 (R/'CONTROLS.json').write_text(json.dumps(checks,indent=2))
 med=json.loads((P/'herbal-slots-v53/MEDIEVAL-EXTRACTIONS.json').read_text());mres=[{'source':m['source'],'text':m['text'],**relations([{'paragraph':0,'text':m['text']}]),'status':'not estimable: two same-folio excerpts, English/Latin, no independent relation labels'} for m in med];(R/'MEDIEVAL-RELATIONS.json').write_text(json.dumps(mres,indent=2),encoding='utf8')
 stats={}
 for split in ('development','test'):
  es=[r for r in results if r['split']==split];ss=[s for e in es for s in e['recipes']]
  stats[split]={'entries':len(es),'single_planet_candidate_entries':sum(e['entry_planet'] is not None for e in es),'treatment_candidate_sentences':len(ss),'candidate_entry_ingredient_links':sum(s['entry_ingredient_link']=='candidate local reference' for s in ss),'candidate_planet_ingredient_links':sum(s['planet_to_recipe_ingredient']=='candidate via entry reference' for s in ss),'candidate_preparation_application_links':sum(s['preparation_application_link']!='unresolved' for s in ss),'negation_metaphor_abstentions':sum(s['negation_or_metaphor'] for s in ss)}
 result={'later':stats,'controls_passed':sum(c['passed'] for c in checks),'controls_total':len(checks),'qualification':'NOT QUALIFIED','limits':['Reserve reused from v53: held out from rule construction, not previously untouched text.','Sentences are candidates, not verified recipe units; sentence punctuation and pronouns can break links.','Same-sentence preparation/application does not prove correct attachment.','No independent historical relation labels; counts are coverage, not precision/recall.','Medieval support inadequate; later expanded edition never pooled with medieval.','Voynich not read or scored.']}
 (R/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 packet=[{'herb':e['herb'],'assertions':e['assertions'],'sentence':s['sentence'],'gold_entry_ingredient':None,'gold_planet_ingredient':None,'gold_preparation_application':None} for e in results if e['split']=='test' for s in e['recipes']];(R/'UNLABELLED-RELATION-PACKET.json').write_text(json.dumps(packet,indent=2),encoding='utf8')
 body='<h1>Entry-to-recipe relations — v54</h1><p><strong>Not qualified. Voynich stays closed.</strong> Associations retained at entry level; ingredient inheritance requires local reference. Other ingredients never receive the entry planet automatically. Negation/metaphor cause abstention. Reserved entries were previously processed by v53; this is not fresh confirmation.</p><pre>'+html.escape(json.dumps(result,indent=2))+'</pre>'
 for f in ['LATER-RELATIONS.json','MEDIEVAL-RELATIONS.json','CONTROLS.json','UNLABELLED-RELATION-PACKET.json','PROTOCOL.json']:body+='<p><a href="'+f+'">'+f+'</a></p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Herbal relations v54</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f6f3e9;color:#173c38}pre{white-space:pre-wrap}p{line-height:1.6}</style>'+body,encoding='utf8')
if __name__=='__main__':main()
