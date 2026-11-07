from pathlib import Path
import json,re,hashlib,collections,importlib.util,html
R=Path(__file__).resolve().parent;P=R.parent
sp=importlib.util.spec_from_file_location('old',P/'herbal-relations-v54/run.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
def revised(rows,wording=True,reference=True,boundary=True):
 assertions=[];links=[]
 for r in rows:
  t=r['text'];parts=re.split(r'(?<=[.!?])\s+|;\s*',t) if boundary else [m.group() for m in re.finditer(r'[^.!?]+(?:[.!?]|$)',t)]
  for s in parts:
   ps=old.v53.extract(s)['planetary_association']
   named=[x['value'].lower() for x in ps]
   subject=bool(re.search(r'^\s*(?:it|this (?:herb|plant)|the herb)\s+(?:is|belongs)',s,re.I))
   if wording:
    m=re.search(r'\b(?:it|this (?:herb|plant)|the herb)\s+(?:is\s+(?:an?\s+)?(?:herb|plant)\s+of\s+(?:the\s+)?|belongs to\s+|is governed by\s+)(sun|moon|mercury|venus|mars|jupiter|saturn)\b',s,re.I)
    if m:named.append(m[1].lower());subject=True
   if named and subject:assertions.extend(named)
   slots=old.v53.extract(s)
   if not(slots['operation'] or slots['internal_application'] or slots['external_application']):continue
   neg=bool(re.search(r'\b(?:not|never|avoid|without)\b|apply (?:yourself|thyself|the rule)',s,re.I))
   explicit=bool(re.search(r'\b(?:this (?:herb|plant)|(?:juice|leaves|root|seeds|decoction|powder|oil) of (?:it|this herb)|(?:its|their) (?:leaves|roots?|seeds?|juice))\b',s,re.I))
   if reference:explicit=explicit or bool(re.search(r'\b(?:berries|roots|seeds|leaves|flowers|bark|herb|decoction|juice) of (?:it|this plant|this herb)\b|\b(?:apply|boil|bruise|take) the herb\b',s,re.I))
   unresolved=bool(re.search(r'\b(?:it|them|thereof|the root|the leaves|the seeds)\b',s,re.I)) and not explicit
   links.append({'paragraph':r['paragraph'],'text':s,'local_reference':explicit and not neg,'unresolved_reference':unresolved,'abstention':neg})
 planets=set(assertions);planet=next(iter(planets)) if len(planets)==1 else None
 return {'planet':planet,'candidate_links':sum(x['local_reference'] for x in links) if planet else 0,'references':sum(x['local_reference'] for x in links),'unresolved_references':sum(x['unresolved_reference'] for x in links),'sentences':links}
def main():
 for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 prior=json.loads((P/'herbal-slots-v53/LATER-EXTRACTIONS.json').read_text());by=collections.defaultdict(list)
 for x in prior:by[x['herb']].append(x)
 ablations={}
 for label,flags in [('baseline',(False,False,False)),('wording',(True,False,False)),('reference',(False,True,False)),('boundary',(False,False,True)),('combined',(True,True,True))]:
  es=[revised(x,*flags) for x in by.values()];ablations[label]={'entries_with_planet':sum(x['planet'] is not None for x in es),'candidate_links':sum(x['candidate_links'] for x in es),'unresolved_reference_segments':sum(x['unresolved_references'] for x in es)}
 (R/'ABLATIONS.json').write_text(json.dumps(ablations,indent=2))
 # Fresh to earlier extraction: unmatched source blocks only, deterministic source order; no planetary-cue selection.
 s=(P/'astrolabe-comparison-v52/sources/culpeper-later-edition.txt').read_text(encoding='utf-8-sig');hs=list(re.finditer(r'(?m)^[ \t]*([A-Z][A-Z ,&\-]+)\.?[ \t]*$',s));fresh=[];excluded=[]
 oldtext='\n'.join(x['text'] for x in prior)
 for i,m in enumerate(hs[:-1]):
  if m.start()<s.find('AMARA DULCIS.'):continue
  name=m[1];body=s[m.end():hs[i+1].start()].strip()
  if name in by or len(body.split())<100:continue
  pars=[re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n',body) if p.strip()]
  if any(p[:100] in oldtext for p in pars if len(p)>=100):excluded.append(name);continue
  rows=[{'paragraph':j,'text':p} for j,p in enumerate(pars)];fresh.append({'heading':name,'source_start':m.start(),'text':body,'baseline':revised(rows,False,False,False),'revised':revised(rows)})
  if len(fresh)==40:break
 (R/'FRESH-BLOCKS.json').write_text(json.dumps(fresh,indent=2),encoding='utf8')
 # All failures kept, not used for repairs this turn.
 fixtures=[('It belongs to Venus. Drink the juice of this herb.',True),('It is under the planet Mercury. Drink wine.',False),('It is under the planet Mercury. Do not drink the juice of this herb.',False),('It is under the planet Mercury. Bruise the berries of it and apply them.',True),('It is under the planet Mercury. Drink it.',False)]
 tests=[{'text':t,'expected_link':e,'actual_link':bool(revised([{'paragraph':0,'text':t}])['candidate_links']),'authored_not_gold':True} for t,e in fixtures]
 (R/'CONTROLS.json').write_text(json.dumps(tests,indent=2))
 summary={'diagnosis':ablations,'fresh_source_blocks':len(fresh),'overlap_blocks_excluded':excluded,'fresh_blocks_with_planet':sum(x['revised']['planet'] is not None for x in fresh),'fresh_candidate_links_baseline':sum(x['baseline']['candidate_links'] for x in fresh),'fresh_candidate_links_revised':sum(x['revised']['candidate_links'] for x in fresh),'qualification':'NOT QUALIFIED','limits':['Fresh blocks were excluded from v53 extraction, not a fresh independent manuscript. Some blocks are descriptions or other prose, not verified recipes.','No independent relation labels; increased coverage is not increased accuracy.','Medieval two-excerpt cohort remains insufficient and is not pooled.','Entry pronoun resolution and same-sentence ingredient attachment remain ambiguous.','Voynich closed; not accessed.']}
 (R/'RESULTS.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
 (R/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Herbal link diagnosis</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#f6f3e9;color:#173c38}pre{white-space:pre-wrap}</style><h1>Link diagnosis v55</h1><p>Frozen wording, reference and boundary ablations. All counts are candidate extraction coverage, not semantic accuracy.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre><p><a href="FRESH-BLOCKS.json">Fresh source blocks with both outputs</a> · <a href="CONTROLS.json">Authored controls</a> · <a href="PROTOCOL.json">Frozen protocol</a></p>',encoding='utf8')
if __name__=='__main__':main()
