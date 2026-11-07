from pathlib import Path
import json,re,hashlib,collections,html
from html.parser import HTMLParser
R=Path(__file__).resolve().parent;P=R.parent
SOURCE=P/'astrolabe-comparison-v52/sources/culpeper-later-edition.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(text):
 patterns={
 'planetary_association':r'\b(?:under (?:the )?(?:planet|dominion|government)(?: of)?\s*|herb of (?:the )?|herb under (?:the )?dominion of )(?P<value>sun|moon|mercury|venus|mars|jupiter|saturn)\b',
 'preparation':r'\b(?:infusion|decoction|tincture|poultice|plaster|ointment|oil|powder|syrup|juice|distilled water)\b',
 'operation':r'\b(?:bruise[ds]?|boil(?:ed)?|strain(?:ed)?|infuse[ds]?|mix(?:ed)?|beat(?:en)?|distil(?:led)?)\b',
 'internal_application':r'\b(?:drink|drunk|drank|drinking|swallow(?:ed)?|taken inwardly|taken internally|inwardly|internally)\b',
 'external_application':r'\b(?:anoint(?:ed)?|appl(?:y|ied)|bathe[ds]?|outwardly|externally|laid (?:on|to)|bound (?:on|to))\b',
 'ingredient_material':r'\b(?:leaves|roots?|seeds?|flowers?|berries|bark|herb|herbs|wood|wine|water|honey|vinegar|milk)\b'}
 return {k:[{'span':[m.start(),m.end()],'text':m.group(),'value':m.groupdict().get('value') or m.group()} for m in re.finditer(v,text,re.I)] for k,v in patterns.items()}
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(R/p)==h,p
 s=SOURCE.read_text(encoding='utf-8-sig');head=list(re.finditer(r'(?m)^ {4}([A-Z][A-Z ,â€™\-]+)\.\s*$',s));entries=[]
 for i,m in enumerate(head):
  body=s[m.end():head[i+1].start() if i+1<len(head) else len(s)]
  gov=re.search(r'_Government and virtues\._\]',body,re.I)
  if not gov:continue
  name=m[1];split='test' if int(hashlib.sha256(('v53:'+name).encode()).hexdigest()[:8],16)%3==0 else 'development'
  entries.append({'name':name,'split':split,'text':body[gov.end():].strip(),'heading_start':m.start()})
 allrows=[]
 for e in entries:
  pars=[re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n',e['text']) if p.strip()]
  for j,p in enumerate(pars):
   slots=extract(p);candidate=bool(slots['operation'] or slots['internal_application'] or slots['external_application'])
   allrows.append({'source':'later-expanded-Culpeper','herb':e['name'],'split':e['split'],'paragraph':j,'text':p,'recipe_candidate':candidate,'slots':slots,'planet_inherited_from_entry':False})
 (R/'LATER-EXTRACTIONS.json').write_text(json.dumps(allrows,indent=2),encoding='utf8')
 # No editor-independent labels exist. Blank packet preserves that boundary.
 held=[x for x in allrows if x['split']=='test' and x['recipe_candidate']]
 packet=[{'herb':x['herb'],'paragraph':x['paragraph'],'text':x['text'],'ingredient':None,'planetary_association':None,'preparation':None,'application':None,'is_recipe':None} for x in held[:40]]
 (R/'UNLABELLED-TEST-PACKET.json').write_text(json.dumps(packet,indent=2),encoding='utf8')
 stats={}
 for split in ('development','test'):
  rs=[x for x in allrows if x['split']==split];recipes=[x for x in rs if x['recipe_candidate']]
  stats[split]={'herb_entries':sum(e['split']==split for e in entries),'paragraphs':len(rs),'recipe_candidates':len(recipes),'candidate_slot_coverage':{k:sum(bool(x['slots'][k]) for x in recipes) for k in extract('')},'all_four_explicit_same_paragraph':sum(bool(x['slots']['ingredient_material'] and x['slots']['planetary_association'] and x['slots']['preparation'] and (x['slots']['internal_application'] or x['slots']['external_application'])) for x in recipes)}
 # Median and source structure cannot certify semantics; report negative controls as extraction stress only.
 controls=[('planet_without_rule','The sun warms this plant in summer.'),('metaphorical_application','Apply yourself to the study of this herb.'),('external_water','Wash the wound with water.'),('negated_drink','Do not drink the juice.'),('planet_other_wording','This plant belongs to Venus.'),('ambiguous_ingredient','Take thereof and use it as before.')]
 failures=[{'id':k,'text':t,'extracted':extract(t),'interpretation':'authored diagnostic, not historical gold; detect ambiguity, negation, lexical blind spots'} for k,t in controls]
 (R/'CONTROLS-AND-FAILURES.json').write_text(json.dumps(failures,indent=2))
 class T(HTMLParser):
  def __init__(self):super().__init__();self.s=[]
  def handle_data(self,d):self.s.append(d)
 p=T();p.feed((P/'astrolabe-comparison-v52/sources/trinity-o8-31.html').read_text(encoding='utf8'));txt=' '.join(' '.join(p.s).split());med=[]
 for key in ['Take \u00feese','Recipe piperis']:
  start=txt.find(key)
  if start<0:continue
  end=txt.find('Full transcription.',start);t=txt[start:end].strip();med.append({'source':'Trinity O.8.31 f159v','text':t,'slots':extract(t),'status':'not estimable for transfer: two same-folio recipes, different languages; English lexicon not a Latin model'})
 (R/'MEDIEVAL-EXTRACTIONS.json').write_text(json.dumps(med,indent=2),encoding='utf8')
 result={'later':stats,'medieval_full_recipe_excerpts':len(med),'qualification':'NOT QUALIFIED','reason':'No independent reference labels; recipe eligibility selected by extractor; negation/metaphor/unseen wording failures; medieval support inadequate. Frozen held-out herb entries assess extraction coverage only, not accuracy.','split_overlap':sorted(set(x['herb'] for x in allrows if x['split']=='test')&set(x['herb'] for x in allrows if x['split']=='development'))}
 (R/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 body='<h1>Known-herbal slot pilot â€” v53</h1><p><strong>NOT QUALIFIED for Voynich.</strong> Frozen lexical extraction on herb-disjoint held-out entries. Later expanded Culpeper edition separated from two medieval same-folio recipes. Whole entries held out, but candidates are paragraphs, not independently verified recipe boundaries. Counts are coverage, not accuracy.</p><pre>'+html.escape(json.dumps(result,indent=2))+'</pre><h2>Retained evidence</h2><ul>'
 for f in ['PROTOCOL.json','LATER-EXTRACTIONS.json','MEDIEVAL-EXTRACTIONS.json','CONTROLS-AND-FAILURES.json','UNLABELLED-TEST-PACKET.json','CLAUDE-REVIEW.txt']:body+='<li><a href="'+f+'">'+f+'</a></li>'
 body+='</ul><p>Plant heading is not automatically an ingredient in every sentence. Planetary associations are not propagated into recipe paragraphs without a justified relation. Missing slot does not mean the concept is absent. No Voynich text was opened or scored by this test.</p>'
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Herbal slots v53</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f6f3e9;color:#173c38}p{line-height:1.6}pre{white-space:pre-wrap}</style>'+body,encoding='utf8')
if __name__=='__main__':main()
