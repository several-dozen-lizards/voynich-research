import run as r
import random,collections,json,html
g=r.panels();f=r.load(r.R/'FROZEN-CANDIDATES.json');checks=0
for p,h in r.load(r.R/'FREEZE.json').items():assert r.sha(r.Path(p))==h
for key,x in g.items():
 assert not set(x['train_folios'])&set(x['test_folios'])
 partner=g[key[:-1]+('F' if key.endswith('H') else 'H')]
 assert x['train_folios']==partner['train_folios'] and x['test_folios']==partner['test_folios']
 for row in x['train']+x['test']:
  ws=row[7];out=r.v.old.shuffle(ws,random.Random(62));assert collections.Counter(ws)==collections.Counter(out)
  if ws:assert ws[0]==out[0] and ws[-1]==out[-1]
  assert [i for i,w in enumerate(ws) if w is None]==[i for i,w in enumerate(out) if w is None]
  checks+=1
audit={key:{x['phrase']:r.details(g[key]['train'],x['phrase']) for x in v['candidates']} for key,v in f.items()}
r.save('TRAINING-OCCURRENCES.json',audit)
desc={'status':'Post-result descriptive lookup only; not added to confirmatory tests','pair':'or aiin','F_selected_in_training':any(x['phrase']=='or aiin' for x in f['2-B-Botanical-F']['candidates']),'F_test':r.details(g['2-B-Botanical-F']['test'],'or aiin')}
r.save('TRANSCRIPTION-EXCEPTION.json',desc)
r.save('VERIFICATION.json',{'freeze_hashes_pass':True,'folios_disjoint':True,'H_F_identical_allocations':True,'shuffled_lines_checked':checks,'word_multisets_edges_unknown_positions_preserved':True,'visual_browser_check':'not performed'})
note='''<h2>Interpretation and exceptions</h2><p>No pair passed the full correction in both readings. Hand-2 botanical <b>or aiin</b> passed in H (8 observed, 1.70 expected; global p=.040, at the permutation resolution floor), across f33, f39 and f43. F did not select this pair in training: it is untested there under the frozen confirmatory list, not a failed F test.</p><p>Hand-1 botanical <b>chol daiin</b> passed within-panel correction in H/F (.035/.010), but failed global correction (.280/.080). It occurred on 13 held-out folios in each reading. Recipes and baths had no globally passing selected pair. These results identify candidate ordering regularities, not translations or grammatical phrases.</p><p>Only broad interior position is controlled; exact within-line ordinal, paragraph position and shared scribal routines can remain. The method was narrowly qualified on edited known-text prose with artificial lines; this is not complete qualification against all manuscript nuisances. Only one split was tested; absence of significance does not establish absence of phrases.</p><p>The initial empty bath panel was a source-label bug (Baths versus Balneological), corrected before held-out scoring. Its code and freeze remain in <a href="failed-label-freeze/README.txt">the failure archive</a>.</p><p><a href="TRAINING-OCCURRENCES.json">Training occurrences</a> · <a href="TRANSCRIPTION-EXCEPTION.json">F descriptive exception</a> · <a href="VERIFICATION.json">Verification</a></p>'''
p=r.R/'report.html';p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8')
r.save('SHA256SUMS.json',{p.name:r.sha(p) for p in r.R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps({'checked_lines':checks,'F_descriptive_count':sum(desc['F_test']['folio_counts'].values()),'F_folios':desc['F_test']['folio_counts']}))
