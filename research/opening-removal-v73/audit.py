from pathlib import Path
import json,hashlib,re,html
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
for fn in ['FREEZE.json','VOCABULARY-FREEZE.json']:
 for p,h in load(R/fn).items():
  path=Path(p) if Path(p).is_absolute() else R/p
  assert hashlib.sha256(path.read_bytes()).hexdigest()==h
allocation=load(P/'template-breaker-v65/ALLOCATION.json');assert not set(allocation['training'])&set(allocation['test'])
events=load(R/'EVENTS.json');voc=load(R/'VOCABULARIES.json');tests=load(R/'TESTS.json');M=sum(len(x.get('outcomes',[])) for x in tests);power=[]
for x in tests:
 if 'outcomes' in x:
  n=x['matched_folios'];floor=min(1,M/(2**n)) if n<=16 else M/10000
  power.append({'stratum':x['stratum'],'unit':x['unit'],'control':x['control'],'matched_folios':n,'best_possible_adjusted_p':floor,'cannot_pass_at_05':floor>.05,'note':'Best case; zero effects/ties can make actual floor worse.'})
for x in events:
 assert re.match(r'f\d+',x['folio'])[0] in allocation['test']
 assert x['first_hit']==bool(x['first_removed'] and x['first_removed'] in voc[x['stratum']])
 assert x['final_hit']==bool(x['final_removed'] and x['final_removed'] in voc[x['stratum']])
opened={(x['stratum'][0],x['locator'],x['unit']):x for x in events if x['category']=='opening'};pairs=[]
for (tr,loc,unit),x in opened.items():
 if tr!='H':continue
 y=opened.get(('F',loc,unit))
 pairs.append({'locator':loc,'unit':unit,'H':x,'F':y,'difference':y is None or any(x[k]!=y[k] for k in ['word','first_removed','final_removed','first_hit','final_hit'])})
save('PAIRED-OPENERS.json',pairs);save('POWER-LIMITS.json',power)
summary={'frozen_hashes_pass':True,'train_test_folios_disjoint':True,'membership_events_checked':len(events),'paired_openers':len(pairs),'paired_differences':sum(x['difference'] for x in pairs),'estimated_comparisons_unable_to_pass_frozen_threshold':sum(x['cannot_pass_at_05'] for x in power),'visual_check':'not performed','limits':'Implementation checks only; no calibrated false-positive or empirical power qualification.'};save('VERIFICATION.json',summary)
body='''<h2>Interpretation: examples survive, paragraph specificity does not</h2><p>Hand-2 botanical examples shared by H/F include pchey → chey (f40r.P.1), pchedar → chedar (f34v.P.6), pdair → dair (f39v.P.1), and pody → ody (f46v.P.1). Remainders occur in independent same-stratum training-folio vocabulary. These are examples of form relationships, not meanings.</p><p>Against matched ordinary line starts, paragraph-opening removal succeeds less often: character removal −27.4 percentage points H / −29.3 F; grouped-sign removal −21.2 H / −23.9 F. Against interior words the character effect is small (+1.1 H / +5.1 F), while grouped-unit effects are −8.4 H / −0.6 F. Matching changes between unit definitions because unit lengths change. Final-removal controls and all matched cells remain available.</p><p>No comparison meets both frozen corrected criteria. This must not be presented as a decisive statistical null: with48 corrected outcomes, seven matched folios have a best possible adjusted p=.375; six have .75. Thus hand-2 botanical and starred cohorts cannot pass this correction at their available size. Hand-1 botanical has more matched folios, but also does not pass. The descriptive direction against ordinary line starts does not support a paragraph-specific added-first-unit effect in this run.</p><p>Recipes lack enough matched test folios; baths lack enough training support under the unchanged split. Both unit definitions and every unmatched opener remain visible. Paragraph starts derive from transcription structure, not newly adjudicated images.</p><h2>H/F differences at paired opening loci</h2>'''
for x in pairs:
 if not x['difference']:continue
 body+='<details><summary>'+html.escape(x['locator']+' '+x['unit'])+'</summary>'
 for tr in ['H','F']:
  y=x[tr]
  body+='<p>'+tr+': '+(html.escape(f"{y['word']} → {y['first_removed']} (vocabulary hit {y['first_hit']}); final removal {y['final_removed']} ({y['final_hit']})") if y else 'not eligible in this reading')+'</p>'
 body+='</details>'
body+='<p><a href="PAIRED-OPENERS.json">All paired openers</a> · <a href="POWER-LIMITS.json">Attainable significance audit</a> · <a href="VERIFICATION.json">Verification</a></p>'
p=R/'report.html';p.write_text(p.read_text(encoding='utf-8')+body,encoding='utf-8');save('SHA256SUMS.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'});print(json.dumps(summary))
