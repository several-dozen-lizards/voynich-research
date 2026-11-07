from pathlib import Path
import json,re,math,hashlib,collections,sys
R=Path(__file__).resolve().parent;P=R.parent;S=P/'complete-atlas-v56/ROWS.json'
TARGET={'f70v1','f71r','f71v','f72r1'}
TRAIN={'f70v2','f72r2','f72r3','f72v3','f72v2','f72v1'}
TRANSFORMS=['raw','literal_o','literal_oa','literal_oal','first_1','first_2','first_3']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def split(w,view):return tuple(w) if view=='characters' else tuple(re.findall('cth|ckh|cph|cfh|ch|sh|.',w))
def transform(w,view,rule):
 u=split(w,view)
 if rule=='raw':return u
 if rule.startswith('first_'):return u[int(rule[-1]):]
 prefix=split(rule.split('_')[1],view)
 return u[len(prefix):] if u[:len(prefix)]==prefix else u
def train(words):
 c=collections.Counter();t=collections.Counter();a={'$','?'}
 for u in words:
  a.update(u)
  for x,y in zip(('^',)+u,u+('$',)):c[x,y]+=1;t[x]+=1
 return c,t,a
def score(u,m):
 c,t,a=m;v=len(a);mapped=tuple(x if x in a else '?' for x in u);pairs=list(zip(('^',)+mapped,mapped+('$',)))
 contributions=[dict(left=x,right=y,surprise=-math.log((c[x,y]+.5)/(t[x]+.5*v)),training_pair_count=c[x,y]) for x,y in pairs]
 return dict(surprise=sum(x['surprise'] for x in contributions)/len(contributions),unknown_units=[x for x in u if x not in a],contributions=contributions)
def freezecheck():
 for p,h in load(R/'PRE-SCORE-FREEZE.json').items():assert sha(Path(p))==h
if sys.argv[1]=='freeze':
 protocol=dict(date='2026-10-23',scope='Exploratory spelling sensitivity, no phonetic/name fitting. Distinguish zodiac figure/star labels from detached astronomical star labels. No cross-reading pooling or significance claims.',exposure='Anchor, proposed cores, source corpus and prior raw ranks already seen. Rules frozen before new transformed scores. This is not untouched confirmation.',views='EVA characters and longest cth/ckh/cph/cfh/ch/sh groups. Prefix lengths in first_k refer to units of the chosen view, preventing cutting a grouped symbol. Anchor o/a/l are single units in both views.',transformations=TRANSFORMS,transformation_meanings='raw unchanged; literal_o/oa/oal removes exactly that opening only when present; first_1/2/3 removes that many initial units from EVERY token as a broader equal-width sensitivity. Candidate becomes oalcheg/alcheg/lcheg/cheg. These are competing hypotheses, not accepted morphological analyses. Empty residues excluded with counts, unknown barriers never promoted.',zodiac='H and V separately. Same raw training/test allocation as v82: six other hand4 sign panels training, four Aries/Taurus panels test. Only S figure/star labels. All target signs excluded from fitting. Target peer vocabulary is distinct transformed types, not duplicated spelling collisions. Save collisions. U/K/C/Q target rows retained as reading alternatives; insufficient coverage for equivalent six-sign models.',detached_stars='H/U/V separately. Train f68r1 S, compare with f68r2 S; repeat reverse direction, never select better direction. Only53 physical S loci, sparse page-specific models; these stars are a different label format from zodiac figures. Descriptive context sensitivity, not independent matched replication. f68r3 cluster and connector excluded from this individual-star cohort. F absent from these star-label panels.',model='Same add-half within-word bigram surprise as v82, including word boundaries; explicit unseen-unit bucket. Train after identical transformation of all reference words. No body-text training. Save start/interior/end transition contributions and symbol counts, so terminal-g scarcity stays visible.',rank='Anchor residual compared with distinct reference/test transformed types of EXACT same unit length and EXACT training transformed-string count. At least5 peers. Strict-less plus half ties; descriptive percentile, not p/confidence. Anchor omitted from peer set if present. Save all low-support/missing ranks without relaxed matching. Compare ranks across transforms as sensitivities, not effect sizes because peer sets change.',qualification='Before scoring: fixed v82-style artificial template unusual-over-normal gate, parser grouping check, explicit unseen-symbol detection. Then verify raw zodiac H/V target surprises and percentiles exactly reproduce saved v82 results. Engineering only; not biological/phonetic/statistical validation.',limits='Functional prefixes could have varying length or context; neither literal nor equal-width removal exhausts possible mechanisms. All narrow endings/reading ambiguities remain. No best transform chosen from outcomes. No historical names or sounds fitted.')
 save('PROTOCOL.json',protocol);save('PRE-SCORE-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',S,P/'astrology-label-patterns-v82/ALL-TYPES.json']});print('Prefix/core comparison frozen.')
elif sys.argv[1]=='qualify':
 freezecheck();receipts=[]
 for v in ['characters','groups']:
  m=train([split(w,v) for w in ['abac','abec','ibac','ibec']*100]);n=[score(split(w,v),m)['surprise'] for w in ['abac','abec','ibac','ibec']];a=[score(split(w,v),m)['surprise'] for w in ['caba','ceba','cabi','cebi']];assert min(a)>max(n)
  assert score(split('zbac',v),m)['unknown_units']==['z']
  receipts.append(dict(view=v,normal=n,unusual=a,gate=True))
 assert split('qockhchshcthcphcfhy','groups')==('q','o','ckh','ch','sh','cth','cph','cfh','y')
 save('QUALIFICATION.json',dict(receipts=receipts,parser_exact=True,unknown_symbol_detected=True,limit='Engineering only'))
 save('QUALIFICATION-FREEZE.json',{str(R/'QUALIFICATION.json'):sha(R/'QUALIFICATION.json')});print('Engineering checks pass.')
else:
 freezecheck()
 for p,h in load(R/'QUALIFICATION-FREEZE.json').items():assert sha(Path(p))==h
 rows=load(S);jobs=[];results=[];alltypes=[];models=[]
 for rd in ['H','V']:
  jobs.append((f'zodiac_{rd}',rd,[x for x in rows if x[0]==rd and x[1] in TRAIN and x[5].startswith('S')],[x for x in rows if x[0]==rd and x[1] in TARGET and x[5].startswith('S')]))
 for rd in ['H','U','V']:
  for tr,te in [('f68r1','f68r2'),('f68r2','f68r1')]:jobs.append((f'stars_{tr}_to_{te}_{rd}',rd,[x for x in rows if x[0]==rd and x[1]==tr and x[5]=='S'],[x for x in rows if x[0]==rd and x[1]==te and x[5]=='S']))
 old={ (x['reading'],x['view'],x['word']):x for x in load(P/'astrology-label-patterns-v82/ALL-TYPES.json') if x['role'].startswith('figure') }
 regression=[]
 for job,rd,tr,te in jobs:
  tw=[w for x in tr for w in x[9] if w];pw=[w for x in te for w in x[9] if w]
  for view in ['characters','groups']:
   for rule in TRANSFORMS:
    trainwords=[transform(w,view,rule) for w in tw];testwords=[transform(w,view,rule) for w in pw];freq=collections.Counter(u for u in trainwords if u);m=train([u for u in trainwords if u]);atype=transform('oalcheg',view,rule)
    peer_types=sorted({u for u in testwords if u});ss={u:score(u,m) for u in peer_types};a=score(atype,m);peers=[u for u in peer_types if u!=atype and len(u)==len(atype) and freq[u]==freq[atype]]
    pct=(sum(ss[u]['surprise']<a['surprise']-1e-12 for u in peers)+.5*sum(abs(ss[u]['surprise']-a['surprise'])<=1e-12 for u in peers))/len(peers) if len(peers)>=5 else None
    collisions=collections.defaultdict(set)
    for w in pw:
     u=transform(w,view,rule)
     if u:collisions[''.join(u)].add(w)
    result=dict(job=job,reading=rd,view=view,rule=rule,anchor=''.join(atype),anchor_units=list(atype),training_tokens=sum(bool(u) for u in trainwords),training_empty=sum(not u for u in trainwords),test_tokens=sum(bool(u) for u in testwords),test_empty=sum(not u for u in testwords),training_loci=len(tr),test_loci=len(te),training_anchor_count=freq[atype],peer_types=len(peers),percentile=pct,peer_words=[''.join(u) for u in peers],g_training_count=sum(u.count('g') for u in trainwords),g_word_final_count=sum(bool(u) and u[-1]=='g' for u in trainwords),a_training_count=sum(u.count('a') for u in trainwords),**a)
    results.append(result)
    models.append(dict(job=job,view=view,rule=rule,alphabet=sorted(m[2]),pair_counts=[dict(left=x,right=y,count=c) for (x,y),c in sorted(m[0].items())],totals=dict(m[1]),collisions={k:sorted(v) for k,v in collisions.items() if len(v)>1},frequency=[dict(units=list(u),count=n) for u,n in sorted(freq.items())]))
    for u in peer_types:
     ps=[p for p in peer_types if p!=u and len(p)==len(u) and freq[p]==freq[u]]
     pctl=(sum(ss[p]['surprise']<ss[u]['surprise']-1e-12 for p in ps)+.5*sum(abs(ss[p]['surprise']-ss[u]['surprise'])<=1e-12 for p in ps))/len(ps) if len(ps)>=5 else None
     alltypes.append(dict(job=job,view=view,rule=rule,units=list(u),word=''.join(u),training_count=freq[u],peers=len(ps),percentile=pctl,**ss[u]))
     if job.startswith('zodiac') and rule=='raw':
      before=old[(rd,view,''.join(u))];assert abs(before['surprise']-ss[u]['surprise'])<1e-12 and before['percentile']==pctl
      regression.append((rd,view,''.join(u)))
 save('ANCHOR-RESULTS.json',results);save('MODELS.json',models);save('ALL-PEER-TYPES.json',alltypes);save('RAW-REGRESSION.json',dict(verified=len(regression),old_surprises_and_ranks_exact=True))
 selected={x[8] for _,_,tr,te in jobs for x in tr+te};selected.add('f70v1.S2.6')
 save('ALL-READINGS.json',[dict(reading=x[0],page=x[1],section=x[2],hand=x[3],format=x[5],locator=x[8],tokens=x[9],raw=x[10]) for x in rows if x[8] in selected])
 print(json.dumps([dict(job=x['job'],view=x['view'],rule=x['rule'],core=x['anchor'],pct=x['percentile'],peers=x['peer_types'],g_count=x['g_training_count']) for x in results if x['job'].startswith('zodiac')],indent=2))
