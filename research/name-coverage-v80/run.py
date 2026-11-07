import json,hashlib,random,re,statistics,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;B=P.parent/'name-encoding-v79'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if not (P/'PRE-RUN-FREEZE.json').exists():
 raw='''acer achillea aconitum actaea adonis aegopodium aesculus agrimonia agrostemma ajuga alchemilla alisma allium alnus althaea amaranthus anagallis anemone anethum antirrhinum apium aquilegia arabis arbutus arctium arenaria aristolochia armeria arnica artemisia arum asarum asclepias asparagus asperula asplenium astragalus atriplex atropa avena ballota bellis berberis beta betula borago brassica briza bromus bryonia buxus calamintha calluna caltha campanula cannabis capsella cardamine carduus carlina carpinus carum castanea centaurea centaurium cerastium ceratonia cheiranthus chelidonium chenopodium cichorium cicuta cirsium cistus clematis clinopodium colchicum conium convallaria convolvulus cornus crataegus crepis crocus cucumis cucurbita cupressus cyclamen cynoglossum cytisus daphne datura daucus delphinium dianthus dipsacus drosera echium epilobium equisetum erica erigeron eryngium eupatorium euphorbia euphrasia fagus festuca ficus filipendula foeniculum fragaria fraxinus fumaria galega galeopsis galium gaultheria geranium geum glechoma glycyrrhiza gnaphalium hedera helianthus helleborus heracleum hieracium hippophae hordeum humulus hyacinthus hydrocotyle hyoscyamus hypericum hyssopus ilex inula iris isatis jasminum juglans juniperus lactuca lamium lathyrus laurus leontodon lepidium levisticum ligustrum lilium linaria linum lonicera lotus lunaria lupinus lychnis lycopodium lycopus lysimachia lythrum marrubium matricaria medicago melilotus mercurialis mespilus molinia morus myosotis myrica myrtus narcissus nasturtium nepeta nigella nuphar nymphaea ocimum olea ononis ophioglossum orchis origanum ornithogalum oxalis paeonia papaver parietaria paris pastinaca pedicularis persicaria petasites petroselinum peucedanum phalaris pimpinella pinus pistacia pisum platanus polygala polygonatum polypodium populus potentilla prunella prunus pteridium pulmonaria punica pyrus quercus ranunculus raphanus reseda rhamnus rheum rhododendron ribes robinia rubia rubus rumex ruscus sagina salix sambucus sanguisorba sanicula saponaria saxifraga scabiosa scilla scrophularia scutellaria secale sedum sempervivum senecio sherardia silene silybum sinapis sisymbrium smilax solanum solidago sonchus sorbus spergula stachys stellaria succisa symphytum tamarix tanacetum taraxacum taxus teucrium thalictrum thymus tilia tragopogon trifolium trigonella triticum tussilago typha ulex ulmus vaccinium veratrum verbascum veronica viburnum vicia vinca viscum vitis'''.split()
 old=set(read(B/'KNOWN-NAMES.json'));names=sorted(set(raw)-old)
 assert len(names)==len(set(names)) and not old.intersection(names)
 rng=random.Random(80001);order=names.copy();rng.shuffle(order)
 split={'development':order[:30],'confirmation':order[30:60],'training_pool':order[60:]}
 save('NAMES.json',names);save('SPLIT.json',split)
 proto={'date':'2026-10-23','scope':'Fresh synthetic botanical-name string benchmark. Curated genus-style labels, not a dated medieval lexicon, expert identifications or phonetic ground truth. Taxonomic synonyms/families may be related; counts are strings, not independent species evidence.',
 'freshness':'Exclude all24 v79 strings. Fixed disjoint30 development and30 confirmation names; all remaining names training only. Seed80001. f9v/fochor and every Voynich token excluded. No Voynich name pairings fitted.',
 'models':'Exactly the five transformations from v79, copied unchanged. Written syllable surrogate is not historical phonology. Vowelless recovery is transformed-string recovery, not unique full-name recovery.',
 'sizes':[10,15,18,24,36,48,64,80,100,120,150,180,200],
 'replicates':'100 nested random training orders, seeds80100..80199. Include full training pool as final size; omit requested sizes exceeding pool. These repetitions measure selection sensitivity, not independent sampling or confidence intervals.',
 'learning':'Known pairings and target boundaries supplied. Opaque group labels assigned injectively by encoder; learner sees only sampled training pairs. Fixed group-to-unit dictionary; unknowns ?. Same best-case learner as v79. No guessing, backoff or language-model expansion.',
 'criterion':'At least90/100 training selections recover at least27/30 development transformed strings exactly AND >=90% group coverage. Wrong-pair cyclic shifts must pass at most5/100. Select smallest tested passing size; also require all larger tested sizes pass. Numeric threshold fixed before outcomes, not estimated evidence.',
 'confirmation':'Evaluate selected size once as a predeclared100-selection batch on the separate30 names. Same90/100 and27/30 and90%coverage thresholds. No alternate size chosen if confirmation fails. If none passes development, confirmation stays unscored.',
 'diagnosis':'For development only report missing group types even with whole training pool, per-name errors and exact transformed-string ceiling. Do not open confirmation outputs for failed models.',
 'limits':'No universal number of plants follows from this finite name pool. Synonyms, languages, segmentation uncertainty, pronunciation and wrong plant identities remain unqualified. A passing control does not open Voynich automatically.',
 'preservation':'v79 freeze must verify. Preserve every key, error, unknown and wrong-pair trial. H/F inherited unchanged; f9v remains excluded from fitting and method selection, and is already exposed historically.'}
 save('PROTOCOL.json',proto)
 save('PRE-RUN-FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{n:sha(P/n) for n in ['run.py','NAMES.json','SPLIT.json','PROTOCOL.json']},'v79_freeze_sha256':sha(B/'FREEZE.json')})
 print(f'Frozen {len(names)} fresh strings: training {len(split["training_pool"])}, development30, confirmation30.');raise SystemExit
assert all(sha(P/n)==h for n,h in read(P/'PRE-RUN-FREEZE.json')['files'].items())
assert all(sha(B/n)==h for n,h in read(B/'FREEZE.json')['files'].items())
proto=read(P/'PROTOCOL.json');split=read(P/'SPLIT.json');names=read(P/'NAMES.json');v=set('aeiouy')
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
def fit(xs,ys):
 key={}
 for x,y in zip(xs,ys):
  if len(x)!=len(y):return None,'length conflict'
  for a,b in zip(x,y):
   if a in key and key[a]!=b:return None,'mapping conflict'
   key[a]=b
 return key,None
def score(key,test,us,enc):
 rr=[]
 for w in test:
  gs=[enc[u] for u in us[w]];out=[(key or {}).get(g,'?') for g in gs]
  rr.append({'name':w,'cipher':gs,'target':''.join(us[w]),'output':''.join(out),'exact':out==us[w],'resolved':sum(x!='?' for x in out),'groups':len(out),'unseen':[g for g in gs if g not in (key or {})]})
 ex=sum(r['exact'] for r in rr);cov=sum(r['resolved'] for r in rr)/sum(r['groups'] for r in rr)
 return dict(exact=ex,coverage=cov,passes=ex>=27 and cov>=.9,rows=rr)
sizes=sorted(set([n for n in proto['sizes'] if n<=len(split['training_pool'])]+[len(split['training_pool'])]))
models=list(read(B/'PROTOCOL.json')['models']);results=[];curves=[];confirm=[];diagnosis=[]
for m in models:
 us={w:units(w,m) for w in names};inventory=sorted({x for w in names for x in us[w]});enc={x:f'G{i:04}' for i,x in enumerate(inventory)}
 full={x for w in split['training_pool'] for x in us[w]};devmissing={w:[x for x in us[w] if x not in full] for w in split['development']}
 diagnosis.append(dict(model=m,training_unit_types=len(full),unrecoverable_development_names={w:x for w,x in devmissing.items() if x},max_exact_development=sum(not x for x in devmissing.values()),development_total=30))
 bysize={}
 for n in sizes:
  rr=[]
  for seed in range(80100,80200):
   order=split['training_pool'].copy();random.Random(seed).shuffle(order);train=order[:n];xs=[[enc[x] for x in us[w]] for w in train];ys=[us[w] for w in train]
   key,err=fit(xs,ys);bad,berr=fit(xs,ys[1:]+ys[:1]);assert err is None
   t=dict(model=m,size=n,seed=seed,train=train,key=key,negative_key=bad,negative_error=berr,positive=score(key,split['development'],us,enc),negative=score(bad,split['development'],us,enc));rr.append(t)
  results.extend(rr);pos=sum(t['positive']['passes'] for t in rr);neg=sum(t['negative']['passes'] for t in rr)
  s=dict(model=m,size=n,passing_selections=pos,wrong_pair_passes=neg,mean_exact_pct=100*statistics.mean(t['positive']['exact']/30 for t in rr),mean_coverage_pct=100*statistics.mean(t['positive']['coverage'] for t in rr),pass_gate=pos>=90 and neg<=5)
  bysize[n]=s;curves.append(s)
 candidates=[n for n in sizes if all(bysize[k]['pass_gate'] for k in sizes if k>=n)]
 if not candidates:confirm.append(dict(model=m,selected_size=None,status='No development pass; confirmation unscored'));continue
 n=min(candidates);rr=[]
 for seed in range(80100,80200):
  t=next(t for t in results if t['model']==m and t['size']==n and t['seed']==seed)
  rr.append(dict(seed=seed,positive=score(t['key'],split['confirmation'],us,enc),negative=score(t['negative_key'],split['confirmation'],us,enc)))
 pos=sum(t['positive']['passes'] for t in rr);neg=sum(t['negative']['passes'] for t in rr)
 confirm.append(dict(model=m,selected_size=n,passing_selections=pos,wrong_pair_passes=neg,mean_exact_pct=100*statistics.mean(t['positive']['exact']/30 for t in rr),status='PASS' if pos>=90 and neg<=5 else 'FAIL; no retuning',trials=rr))
save('DEVELOPMENT-TRIALS.json',results);save('CURVES.json',curves);save('CONFIRMATION.json',confirm);save('COVERAGE-CEILING.json',diagnosis);save('H-F-SLOTS.json',read(B/'H-F-SLOTS.json'))
e=lambda x:html.escape(str(x))
out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Name coverage v80</title><style>body{font:16px/1.55 system-ui;background:#10241f;color:#e5eee4;max-width:1100px;margin:32px auto;padding:0 22px}a{color:#a5e4bd}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #456457;text-align:left}aside{padding:20px;background:#304535}h1,h2{color:#ccebb9}</style><h1>How many known names cover the groups?</h1><p>v80 · Frozen before execution · No Voynich fitting</p><aside>'+str(len(names))+' fresh botanical name strings; '+str(len(split['training_pool']))+' training candidates; 30 development and 30 separate confirmation names. All24 v79 strings excluded. These are experimental name labels, not newly authenticated medieval names.</aside><h2>Selected size and fresh confirmation</h2><table><tr><th>Model</th><th>Selected training size</th><th>Confirmation passing selections /100</th><th>Outcome</th></tr>']
for c in confirm:out.append('<tr>'+''.join('<td>'+e(x)+'</td>' for x in [c['model'],c['selected_size'],c.get('passing_selections','unscored'),c['status']])+'</tr>')
out.append('</table><p>Reliability means at least90/100 training selections recover at least27/30 target strings exactly, with at least90% group coverage. Wrong-pair passing selections must be at most5/100. Smallest tested development size is selected once; confirmation failures are not retuned.</p><h2>Development curves</h2><table><tr><th>Model</th><th>Training size</th><th>Exact target recovery</th><th>Unit coverage</th><th>Passing selections /100</th><th>Wrong pairs /100</th></tr>')
for c in curves:out.append('<tr>'+''.join('<td>'+e(x)+'</td>' for x in [c['model'],c['size'],f"{c['mean_exact_pct']:.1f}%",f"{c['mean_coverage_pct']:.1f}%",c['passing_selections'],c['wrong_pair_passes']])+'</tr>')
out.append('</table><h2>What remains outside the test</h2><p>Correct pairings and group boundaries were supplied. Written syllable chunks are the unchanged v79 surrogate, not historical phonology. Consonant recovery does not restore vowels or uniquely identify a plant. Counts depend on this pool and its unit overlap; no universal required number follows. Confirmation and development name sets are disjoint, but repeated training selections are dependent. Genus-style labels are not independent plant identifications. f9v remains excluded and H/F differences remain unchanged.</p><p><a href="PROTOCOL.json">Protocol</a> · <a href="PRE-RUN-FREEZE.json">Pre-run hashes</a> · <a href="SPLIT.json">Fixed name split</a> · <a href="COVERAGE-CEILING.json">Unseen groups even at full training size</a> · <a href="DEVELOPMENT-TRIALS.json">Every development trial</a> · <a href="CONFIRMATION.json">Confirmation failures and outputs</a> · <a href="H-F-SLOTS.json">H/F record, untouched</a></p></html>')
(P/'report.html').write_text('\n'.join(out),encoding='utf-8')
save('FREEZE.json',{'utc':datetime.now(timezone.utc).isoformat(),'files':{f.name:sha(f) for f in P.iterdir() if f.is_file() and f.name!='FREEZE.json'},'v79_unchanged':True,'voynich_fitting':False})
print(json.dumps([{k:v for k,v in c.items() if k!='trials'} for c in confirm],indent=2));print(json.dumps(diagnosis,indent=2))
