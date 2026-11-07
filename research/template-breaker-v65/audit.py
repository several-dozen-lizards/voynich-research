from pathlib import Path
import json,hashlib,itertools,html
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
for name in ['METHOD-FREEZE.json','TRAINING-FREEZE.json']:
 for p,h in load(R/name).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allocation=load(R/'ALLOCATION.json');assert not set(allocation['training'])&set(allocation['test'])
rows=load(P/'frequency-atlas-v48/rows.json');index={(r[0],r[6]):r for r in rows};top=load(R/'DISPLAY-CANDIDATES.json');wanted={(key,x['word']) for key,v in top.items() for x in v};tokens=load(R/'ALL-TOKENS.json');examples=[]
for x in tokens:
 if (x['stratum'],x['word']) not in wanted:continue
 tr=x['stratum'][0];other='F' if tr=='H' else 'H';rr=index.get((other,x['locator']));examples.append(dict(x,other_transcription=other,other_line=rr[7] if rr else None,warning='Whole source lines paired; token indices are not aligned across readings.'))
save('PAIRED-EXCEPTIONS.json',examples)
tests=load(R/'POSITION-TESTS.json');exact=[]
for x in tests:
 if x.get('passes'):
  vs=list(x['folio_differences'].values());obs=sum(vs);p=sum(sum(v*s for v,s in zip(vs,signs))>=obs-1e-12 for signs in itertools.product((-1,1),repeat=len(vs)))/2**len(vs)
  exact.append({'stratum':x['stratum'],'exact_sign_flip_p':p,'adjusted_six':min(1,p*6),'status':'Post-result numerical audit, not a changed analysis or second independent test.'})
save('EXACT-AUDIT.json',exact)
note='''<h2>Interpretation and coverage</h2><p>Hand-2 botanical paragraph line starts have higher template surprise than matched interior words in both readings: H +0.0756 and F +0.0900 nats per transition. All seven test folios point in this direction. Frozen Monte Carlo adjusted p values are .042 H / .036 F. A post-result exact sign-flip calculation gives .046875 after the same six-test correction in each reading. This verifies the numerical threshold, not the exchangeability assumption.</p><p>The hand-2 models trained on only three folios (522 H / 513 F tokens). This is a local line-position association under a simple character-bigram template, not a new language, phonetic mode, or identified names. Decoration, spelling conventions, transcription choices and paragraph-opening concentration remain alternatives. First word of a source line is not necessarily first word of a paragraph.</p><p>Hand-1 botanical adjusted p=.396 H/.354 F; starred paragraphs .096 H/.222 F: neither passes. Recipe models were trained, but their held-out matched-folio support was insufficient. Bath training support failed the frozen minimum. Labels, rings and other raw formats remain unsupported, not negative. No adaptive split was tried.</p><p>Ranks compare exact EVA length and exact training frequency, including unseen words as count zero. They do not control held-out word frequency, which was not used for selection. The model treats EVA characters individually; multi-character glyph conventions may produce apparent unusualness. Top lists are display selections, not significance claims. This test preserves H/F independently; a score agreement is transcription robustness, not independent evidence.</p><h2>Paired candidate lines and exceptions</h2>'''
for x in examples:
 note+='<details><summary>'+html.escape(x['stratum']+' '+x['locator']+' '+x['word'])+'</summary><p>'+html.escape(' · '.join(w or '[?]' for w in x['line']))+'</p><p>'+x['other_transcription']+': '+html.escape(' · '.join(w or '[?]' for w in x['other_line']))+'</p></details>'
note+='<p><a href="PAIRED-EXCEPTIONS.json">All paired candidate lines</a> · <a href="EXACT-AUDIT.json">Exact numerical audit</a></p>'
p=R/'report.html';p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8')
save('VERIFICATION.json',{'frozen_hashes_pass':True,'whole_folio_split_disjoint':True,'paired_display_occurrences':len(examples),'visual_check':'not performed','qualification_limit':'Synthetic engineering check only; no empirical false-positive calibration for manuscript nuisances.'})
save('SHA256SUMS.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps({'paired_examples':len(examples),'exact':exact}))
