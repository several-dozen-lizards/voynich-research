"""Frozen, best-case paired-name encoding controls. No Voynich fitting."""
from pathlib import Path
import json, hashlib, random, html, re, statistics
from datetime import datetime, timezone
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
if not (P/'PROTOCOL.json').exists():
 names=['rosa','salvia','mentha','ruta','malva','viola','urtica','plantago','verbena','betonica','artemisia','angelica','lavandula','calendula','digitalis','primula','gentiana','valeriana','coriandrum','ricinus','nenufar','centauria','althaea','melissa']
 protocol={'date':'2026-10-23','scope':'Known-name synthetic coverage and consistency screen; not blind name identification, phonological validation, or decipherment qualification.',
 'names':'24 familiar botanical name strings used only as known experimental labels. This is not a new dated medieval-name lexicon. Do not infer historical usage, exact species, or pronunciations from this list.',
 'normalization':'Lowercase ASCII letters; vowels a e i o u y. No historical u/v or i/j normalization. No name selected for similarity to a Voynich token.',
 'models':{'full_letters':'One opaque group per written letter; retain every vowel.', 'internal_vowels_omitted':'Delete vowels except at first and last character positions; remaining letters each get a group.', 'consonants_only':'Delete all a/e/i/o/u/y; remaining letters each get a group.', 'written_syllable_groups':'One group per deterministic written chunk: contiguous vowel run is one nucleus; split inter-nucleus consonants before the last consonant; leading/trailing consonants attach to nearest nucleus. This is a syllable-like orthographic surrogate, not verified historical phonology.', 'vowelless_syllable_groups':'Same written chunks, then remove all vowels; discard empty chunks and merge equal remaining chunk types. Different full syllables can collide.'},
 'design':'Seeds 79000..79099. For each seed shuffle 24 distinct names. Last six are held out. First 2, 6, 10, 15 or 18 are training. Nested training sizes, same split across models. No replacement or tuning after results. Repeated splits are dependent; no p-values.',
 'encoding':'Independent injective opaque labels G000... for each model unit inventory, randomly assigned per seed. Test inventory is used by the synthetic encoder only. Learner receives only training pairs; target group boundaries and correct name identities supplied. Learner never receives encoder key or test name.',
 'fit':'Align training cipher groups with supplied target units. Every label must map consistently; contradictory training rejects the fit. Unseen groups become ?. Freeze each learned key before held-out decoding. This favourable alignment tests coverage, not segmentation discovery.',
 'negative':'Cyclically shift training name assignments by one, including their target units. Contradictory counts or mappings reject; otherwise score held-out outputs identically. Preserve every control.',
 'scores':'Exact transformed-name recovery, resolved group coverage, contradictions, and ambiguity: number of benchmark full names with same transformed string. Vowelless output is never silently expanded back to a name.',
 'engineering_gate':'For each model and training size: at least 90/100 splits recover >=5/6 held-out transformed names exactly with >=90% group coverage, and at most 5/100 wrong-pair controls reach the same threshold. This is a declared engineering target, not a statistical significance claim.',
 'application_gate':'Even engineering pass is insufficient: no Voynich fitting until independent plant/name pairing, historical-language/phonology decisions, segmentation and synonym-search controls qualify. Current small disputed inventory fails this application gate.',
 'f9v':'Excluded from any future key training or choice of segmentation/omission rules. Already exposed in conversation, so a prediction check, not pristine confirmation. Compare to all frozen eligible names, not a tuned viola-like similarity. H/F fochor retained.',
 'HF':'Preserve all v76/v77 records and v78 alternatives; f6v koar/koary remains distinct. No manuscript tokens enter the synthetic learner.'}
 save('KNOWN-NAMES.json',names);save('PROTOCOL.json',protocol)
 save('PRE-RUN-FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{n:sha(P/n) for n in ['run.py','KNOWN-NAMES.json','PROTOCOL.json']}})
 print('Protocol and inputs frozen. Run again to execute.');raise SystemExit
assert all(sha(P/n)==h for n,h in read(P/'PRE-RUN-FREEZE.json')['files'].items())
for folder in ['plant-candidates-v76','plant-image-audit-v77','plant-detail-names-v78']:
 b=P.parent/folder
 assert all(sha(b/n)==h for n,h in read(b/'FREEZE.json')['files'].items())
names=read(P/'KNOWN-NAMES.json');proto=read(P/'PROTOCOL.json');v=set('aeiouy')
def chunks(w):
 runs=list(re.finditer('[aeiouy]+',w))
 if not runs:return [w]
 cuts=[0]+[b.start()-1 if b.start()>a.end() else b.start() for a,b in zip(runs,runs[1:])]+[len(w)]
 return [w[a:b] for a,b in zip(cuts,cuts[1:]) if a<b]
def units(w,m):
 if m=='full_letters':return list(w)
 if m=='internal_vowels_omitted':return [c for i,c in enumerate(w) if c not in v or i in [0,len(w)-1]]
 if m=='consonants_only':return [c for c in w if c not in v]
 if m=='written_syllable_groups':return chunks(w)
 return [s for z in chunks(w) if (s:=''.join(c for c in z if c not in v))]
def fit(pairs):
 key={}
 for x,y in pairs:
  if len(x)!=len(y):return None,'unit-count disagreement'
  for a,b in zip(x,y):
   if a in key and key[a]!=b:return None,'inconsistent repeated group'
   key[a]=b
 return key,None
def score(key,test,enc,us):
 rows=[]
 for w in test:
  x=[enc[u] for u in us[w]];out=[key.get(g,'?') for g in x] if key is not None else ['?']*len(x)
  target=''.join(us[w]);pred=''.join(out)
  rows.append(dict(name=w,cipher=x,target_units=us[w],target=target,output=pred,exact=pred==target,resolved=sum(o!='?' for o in out),groups=len(out),benchmark_names_with_same_target=[z for z in names if ''.join(us[z])==target]))
 exact=sum(r['exact'] for r in rows);cov=sum(r['resolved'] for r in rows)/sum(r['groups'] for r in rows)
 return dict(exact_names=exact,group_coverage=cov,passes=exact>=5 and cov>=.9,rows=rows)
trials=[]
for m in proto['models']:
 us={w:units(w,m) for w in names}
 inventory=sorted({u for uu in us.values() for u in uu})
 for seed in range(79000,79100):
  rng=random.Random(seed);order=names.copy();rng.shuffle(order);test=order[-6:]
  labels=[f'G{i:03}' for i in range(len(inventory))];rng.shuffle(labels);enc=dict(zip(inventory,labels))
  for size in [2,6,10,15,18]:
   train=order[:size];xs=[[enc[u] for u in us[w]] for w in train];ys=[us[w] for w in train]
   key,err=fit(zip(xs,ys));bad,baderr=fit(zip(xs,ys[1:]+ys[:1]))
   trials.append(dict(model=m,seed=seed,train_size=size,train=train,test=test,key=key,error=err,positive=score(key,test,enc,us),wrong_pair_key=bad,wrong_pair_error=baderr,negative=score(bad,test,enc,us)))
summary=[]
for m in proto['models']:
 for size in [2,6,10,15,18]:
  rr=[t for t in trials if t['model']==m and t['train_size']==size]
  pos=sum(t['positive']['passes'] for t in rr);neg=sum(t['negative']['passes'] for t in rr)
  summary.append(dict(model=m,train_size=size,positive_passes=pos,negative_passes=neg,mean_exact_percent=100*statistics.mean(t['positive']['exact_names']/6 for t in rr),mean_group_coverage_percent=100*statistics.mean(t['positive']['group_coverage'] for t in rr),engineering_pass=pos>=90 and neg<=5,manuscript_application=False))
save('TRIALS.json',trials);save('SUMMARY.json',summary)
save('UNIT-DEFINITIONS.json',{m:{w:units(w,m) for w in names} for m in proto['models']})
save('H-F-SLOTS.json',read(P.parent/'plant-image-audit-v77/H-F-SLOTS.json'))
save('CANDIDATE-AMENDMENTS.json',{'preserve':'v76-v78 unchanged; amendments are explicit and do not authorize fitting.', 'f9v':{'additional_form':'Uiola','normalized_alias':'viola (u/v normalization not yet authorized for a fitting test)','source':'https://celt.ucc.ie/document/G600005/','locator':'chapter 276, witness marker 103a2','date':'work dated 1415; edited manuscript witness, not newly inspected autograph','status':'Genus-level conditional violet candidate; sweet-violet interpretation retained. Does not establish pansy species or any Voynich sound.','prediction':'f9v excluded from fit and method selection; already exposed. No fuzzy viola-like threshold permitted.'},'castor':{'forms':['Ricinus','Cataputia maior'],'source':'https://mateo.uni-mannheim.de/camenaref/lonitzer/loni1/Lonitzer_historia_1-2.html','locator':'CICI, page97','date':1551,'date_source':'https://mateo.uni-mannheim.de/camenaref/lonitzer.html','status':'Verified in scholarly transcription of later printed primary text. Later comparison only; not admitted as medieval witnesses. Bare cataputia not substituted for maior; minor refers to another entry. Earlier medieval attestation remains unverified.'}})
e=lambda x:html.escape(str(x))
out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Names with and without vowels · v79</title><style>body{font:16px/1.5 system-ui;max-width:1150px;margin:32px auto;padding:0 20px;background:#10241f;color:#edf2e9}a{color:#a5e8c1}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:9px;border-bottom:1px solid #456659}aside{padding:20px;background:#293f33;margin:20px 0}h1,h2{color:#cff0bd}</style><h1>Known names: with and without vowels</h1><p>v79 · Frozen synthetic screen · No Voynich fitting</p><aside>Correct plant/name pairs and group boundaries are supplied. This is deliberately easier than Voynich. Recovering a consonant skeleton is not recovering its full name. Written syllable-like groups are not validated historical sounds.</aside><p>24 known name strings, 100 fixed splits, six held-out names per split. Training sizes 2, 6, 10, 15, 18. Repeated splits are dependent; no significance claims. Engineering pass requires at least 90/100 successful splits and at most 5/100 successful wrong-pair controls. A successful split recovers at least 5/6 transformed names with at least 90% group coverage.</p><table><tr><th>Model</th><th>Training names</th><th>Exact recovery</th><th>Group coverage</th><th>Passing splits /100</th><th>Wrong pairs /100</th><th>Engineering gate</th></tr>']
for s in summary:out.append('<tr>'+''.join('<td>'+e(x)+'</td>' for x in [s['model'],s['train_size'],f"{s['mean_exact_percent']:.1f}%",f"{s['mean_group_coverage_percent']:.1f}%",s['positive_passes'],s['negative_passes'],'PASS' if s['engineering_pass'] else 'FAIL'])+'</tr>')
out+=['</table><h2>What this can establish</h2><p>These controls measure consistency and unseen-group coverage in a favourable paired-name setting. A pass does not validate inferred segmentation, uncertain plant identification, alternative-name selection or phonology. No model is cleared for Voynich application by this screen alone.</p><h2>Candidate corrections and f9v</h2><p>Uiola returns as a conditional genus-level violet candidate, with its sweet-violet ambiguity retained. Ricinus and Cataputia maior are verified in Lonitzer 1551 as later comparators, not medieval attestations. f9v stays out of fitting and method selection. Its fochor reading in H/F is preserved, as is f6v koar/koary. All earlier alternatives remain in v77/v78.</p><p><a href="CANDIDATE-AMENDMENTS.json">Dated source details and amendments</a> · <a href="H-F-SLOTS.json">Unchanged H/F lines</a> · <a href="PROTOCOL.json">Frozen rules</a> · <a href="PRE-RUN-FREEZE.json">Pre-run hashes</a> · <a href="TRIALS.json">Every trial, failure, key and unresolved group</a> · <a href="UNIT-DEFINITIONS.json">Every name segmentation</a></p></html>']
(P/'report.html').write_text('\n'.join(out),encoding='utf-8')
save('FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{f.name:sha(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='FREEZE.json'},'prior_versions_unchanged':True,'voynich_fit_performed':False})
assert all(sha(P/n)==h for n,h in read(P/'FREEZE.json')['files'].items())
print(json.dumps(summary,indent=2))
