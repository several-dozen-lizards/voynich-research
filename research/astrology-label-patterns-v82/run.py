from pathlib import Path
import json, hashlib, math, re, collections, sys, html

R=Path(__file__).resolve().parent; P=R.parent; SOURCE=P/'astrology-name-audit-v81/ALL-READINGS.json'
TARGETS=['f70v1','f71r','f71v','f72r1']
LABEL='figure/star-associated label; exact referent unresolved'; RING='circumferential text'
GROUPS=['cth','ckh','cph','cfh','ch','sh']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def units(w,view):return list(w) if view=='characters' else re.findall('cth|ckh|cph|cfh|ch|sh|.',w)
def train(words,view):
 pairs=collections.Counter(); totals=collections.Counter(); alphabet={'$','?'}
 for w in words:
  u=units(w,view);alphabet.update(u)
  for a,b in zip(['^']+u,u+['$']):pairs[a+'|'+b]+=1;totals[a]+=1
 return dict(pairs=dict(pairs),totals=dict(totals),alphabet=sorted(alphabet))
def score(w,m,view):
 u=units(w,view); alphabet=set(m['alphabet']);u=[x if x in alphabet else '?' for x in u]
 pp=list(zip(['^']+u,u+['$'])); terms=[-math.log((m['pairs'].get(a+'|'+b,0)+.5)/(m['totals'].get(a,0)+.5*len(alphabet))) for a,b in pp]
 return dict(surprise=sum(terms)/len(terms),unseen_transitions=sum(a+'|'+b not in m['pairs'] for a,b in pp),transitions=len(pp),unseen_units=sum(x=='?' for x in u))
def verify_freeze():
 for p,h in load(R/'PRE-SCORE-FREEZE.json').items():assert sha(Path(p))==h,p

stage=sys.argv[1]
if stage=='freeze':
 observations=[
  dict(page='f70v1',sign='Aries',image_id='1006201',size=[2979,3700],crop='1000,1100,1450,1300',central_title='No isolated Voynich word or encircling Voynich text inside/along the animal medallion is apparent in inspected centre. Later April annotation inside.',primary_locus=None,secondary='S1/S2 individual figure/star labels; R1/R2 circumferential text outside inner figures. R1 is NOT equivalent in geometry to f71r.R3.',damage='Fold/page curvature; no new glyph reading supplied.'),
  dict(page='f71r',sign='Aries',image_id='1006202',size=[2793,3762],crop='700,1150,1400,1400',central_title='Voynich text runs around animal medallion; later April annotation inside. No single isolated Voynich title identified.',primary_locus='f71r.R3.1',secondary='S1 outer and S2 inner figure/star labels; R1 outer/R2 middle circumferential text.',damage='Inner text close to plant/animal and tubs; word boundaries inherited from source, not independently adjudicated.'),
  dict(page='f71v',sign='Taurus',image_id='1006203',size=[8865,3018],crop='650,700,1550,1550',central_title='Voynich text runs around animal medallion; later May annotation inside. No isolated Voynich title identified.',primary_locus='f71v.R3.1',secondary='S1 outer and S2 inner figure/star labels; R1 outer/R2 middle circular text.',damage='Faint ink in full foldout; enlarged centre inspected.'),
  dict(page='f72r1',sign='Taurus',image_id='1006203',size=[8865,3018],crop='2400,700,1550,1550',central_title='Voynich text runs around animal medallion; later May annotation inside. No isolated Voynich title identified.',primary_locus='f72r1.R3.1',secondary='S1 outer and S2 inner figure/star labels; R1 outer/R2 middle circular text.',damage='Large hole left of medallion; source gap markers retained in central and middle circular text. Do not promote fragments to secure words.'),
 ]
 for x in observations:
  x['full_image']=f'https://collections.library.yale.edu/iiif/2/{x["image_id"]}/full/full/0/default.jpg'
  x['centre_image']=f'https://collections.library.yale.edu/iiif/2/{x["image_id"]}/{x["crop"]}/full/0/default.jpg'
  x['catalogue']=f'https://collections.library.yale.edu/catalog/2002046?child_oid={x["image_id"]}'
 save('IMAGE-POSITIONS.json',observations)
 protocol=dict(date='2026-10-23',status='Exploratory spelling-pattern screen, not a phonetic test or significance result.',exposure='v81 source words and coverage were previously inspected. Current image positions fixed after centre inspection, before new scoring. Coverage counts seen before support criterion; no claim of untouched discovery.',
  geometry='Image-based primary positions: entire central medallion ring R3 on f71r/f71v/f72r1, no primary counterpart on f70v1. Retain every word in those rings. Secondary all S labels and other R rings on all four panels. No endpoint word promoted to a title from transcription order.',
  allocation='Training: six other surviving zodiac sign identities with local hand4: Pisces/Gemini/Cancer/Leo/Virgo/Libra. Target: both Aries and both Taurus pages wholly excluded from training. f73r/v local hand3 excluded from baseline; unresolved hand assignment conflict retained from v81. Previously exposed corpus, not prospective holdout.',
  model='v65-style add-half within-word bigram model, mean negative log probability including word boundaries. Two views: EVA characters; longest groups cth/ckh/cph/cfh/ch/sh then single characters. EVA/group units are not phonemes. Unseen units mapped to explicit ? bucket. Full training counts and units saved.',
  strata='Individual figure/star labels versus circumferential text modelled separately; all S subrings pooled as label format, all R subrings pooled as circular format. Radial position not controlled by this coarse model. H/U/V trained separately where >=150 readable tokens and >=3 training sign groups; small-support strata retained unsupported. Other transcriptions shown under H reference model as sensitivities, never independent confirmation.',
  ranking='For each view/reference model, target types compared with OTHER target types of exact unit length and exact training word frequency, same format and transcription. Minimum five distinct peers. Percentile uses strict-less plus half ties. >=.90 is a display flag only, not p-value. Save all types, unrankable types, every occurrence, and no pass/fail phonetic decision. Raw surprise shown for sparse peer sets without claiming calibrated anomaly.',
  qualification='Before manuscript scoring: artificial template engineering check in both views, unusual reverse strings all score above normal heldout strings; grouped parser exact tokenisation tests; repeated-word score invariant to training-list permutation. This does not establish historical realism, power, false-positive rate, or semantics.',
  repeat='Exact shared complete words in corresponding role displayed descriptively, including alternate readings. No same-sign enrichment test, no rotation search or invented label alignment.',
  preservation='No sounds fitted, no historical name assignment, no normalization across readings. All source rows including unknowns retained. f9v excluded. Prior artifacts unchanged.')
 save('PROTOCOL.json',protocol)
 save('PRE-SCORE-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),SOURCE,R/'PROTOCOL.json',R/'IMAGE-POSITIONS.json']})
 print('Image positions and scoring protocol frozen.')
elif stage=='qualify':
 verify_freeze(); results=[]
 for view in ['characters','groups']:
  words=['abac','abec','ibac','ibec']*100;m=train(words,view)
  normal=[score(w,m,view)['surprise'] for w in ['abac','abec','ibac','ibec']]
  odd=[score(w,m,view)['surprise'] for w in ['caba','ceba','cabi','cebi']]
  invariant=train(list(reversed(words)),view)==m
  results.append(dict(view=view,normal=normal,unusual=odd,passes=min(odd)>max(normal) and invariant,permutation_invariant=invariant))
 assert units('qockhchshcthcphcfhy','groups')==['q','o','ckh','ch','sh','cth','cph','cfh','y']
 assert all(x['passes'] for x in results)
 save('QUALIFICATION.json',dict(results=results,parser_exact=True,status='Engineering gate passes; not empirical anomaly/phonetic qualification'))
 save('QUALIFICATION-FREEZE.json',{str(R/'QUALIFICATION.json'):sha(R/'QUALIFICATION.json')})
 print('Engineering gate passed in both views.')
elif stage=='score':
 verify_freeze()
 for p,h in load(R/'QUALIFICATION-FREEZE.json').items():assert sha(Path(p))==h
 rows=load(SOURCE);models={};alltypes=[];occ=[];support=[]
 for reading in ['H','U','V']:
  for role in [LABEL,RING]:
   training=[x for x in rows if x['reading']==reading and x['role']==role and x['hand']=='4' and x['sign'] not in ['Aries','Taurus']]
   words=[w for x in training for w in x['tokens'] if w]; target=[x for x in rows if x['reading']==reading and x['role']==role and x['page'] in TARGETS]
   sup=dict(reading=reading,role=role,training_tokens=len(words),training_signs=sorted({x['sign'] for x in training}),training_loci=[x['locator'] for x in training],target_loci=len(target),eligible=len(words)>=150 and len({x['sign'] for x in training})>=3)
   support.append(sup)
   if not sup['eligible']:continue
   freq=collections.Counter(words)
   for view in ['characters','groups']:
    key='|'.join([reading,role,view]);m=train(words,view);models[key]=dict(model=m,frequency=dict(freq),support=sup)
    types=sorted({w for x in target for w in x['tokens'] if w});ss={w:score(w,m,view) for w in types}
    for w in types:
     peers=[p for p in types if p!=w and len(units(p,view))==len(units(w,view)) and freq[p]==freq[w]]
     pct=(sum(ss[p]['surprise']<ss[w]['surprise']-1e-12 for p in peers)+.5*sum(abs(ss[p]['surprise']-ss[w]['surprise'])<=1e-12 for p in peers))/len(peers) if len(peers)>=5 else None
     rec=dict(model_key=key,reading=reading,role=role,view=view,word=w,unit_length=len(units(w,view)),training_count=freq[w],matched_peers=len(peers),percentile=pct,display_flag=pct is not None and pct>=.90,**ss[w])
     alltypes.append(rec)
     for x in target:
      for j,t in enumerate(x['tokens']):
       if t==w:occ.append(dict(**rec,locator=x['locator'],token_index=j,page=x['page'],sign=x['sign'],raw=x['raw'],primary_central_ring=x['locator'] in ['f71r.R3.1','f71v.R3.1','f72r1.R3.1']))
 save('SUPPORT.json',support);save('MODELS.json',models);save('ALL-TYPES.json',alltypes);save('ALL-OCCURRENCES.json',occ)
 targetrows=[x for x in rows if x['page'] in TARGETS];save('TARGET-ALL-READINGS.json',targetrows)
 byloc=collections.defaultdict(list)
 for x in targetrows:byloc[x['locator']].append(x)
 save('ALTERNATES-BY-LOCUS.json',dict(byloc))
 alt=[]
 for x in targetrows:
  if x['role'] not in [LABEL,RING]:continue
  for view in ['characters','groups']:
   key='|'.join(['H',x['role'],view]);m=models[key]['model']
   alt.append(dict(locator=x['locator'],reading=x['reading'],view=view,raw=x['raw'],tokens=[dict(word=w,**score(w,m,view)) if w else None for w in x['tokens']],status='H-model sensitivity only, no cross-reading percentile'))
 save('ALTERNATE-SCORES-UNDER-H.json',alt)
 shared=[]
 for sign,pages in [('Aries',['f70v1','f71r']),('Taurus',['f71v','f72r1'])]:
  for reading in sorted({x['reading'] for x in targetrows}):
   for zone in ['primary central ring',LABEL,RING]:
    sets=[]
    for page in pages:
     sets.append({w for x in targetrows if x['page']==page and x['reading']==reading and (x['source_unit']=='R3' if zone=='primary central ring' else x['role']==zone) for w in x['tokens'] if w})
    shared.append(dict(sign=sign,reading=reading,zone=zone,type_counts=[len(s) for s in sets],shared=sorted(sets[0]&sets[1]),status='No primary counterpart on dark Aries' if sign=='Aries' and zone=='primary central ring' else 'Descriptive exact overlap only'))
 save('REPEATED-PANEL-WORDS.json',shared)
 flags=[x for x in occ if x['reading']=='H' and x['display_flag']]
 primary=[x for x in occ if x['reading']=='H' and x['primary_central_ring']]
 summary=dict(primary_H_ranked=[dict(locator=x['locator'],word=x['word'],view=x['view'],percentile=x['percentile'],matched_peers=x['matched_peers'],surprise=x['surprise']) for x in sorted(primary,key=lambda x:(x['view'],-x['surprise']))],H_flagged_occurrences=flags,source_rows_preserved=len(targetrows),target_loci=len(byloc),sounds_fitted=0,claims='Exploratory within-format spelling ranks only; no p values, name identifications or phonetic inference.')
 save('SUMMARY.json',summary)
 print(json.dumps(dict(support=support,H_flags=[dict(locator=x['locator'],word=x['word'],view=x['view'],percentile=x['percentile']) for x in flags],primary=[dict(locator=x['locator'],word=x['word'],view=x['view'],pct=x['percentile']) for x in primary]),indent=2))
