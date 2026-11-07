import random,json,itertools
from c2_engine import *
from pathlib import Path
P=json.loads((Path(__file__).parent/'PLAN.json').read_text())
checks=[]
def check(name,value):
 checks.append({'check':name,'pass':bool(value)})
 if not value:raise AssertionError(name)
def row(i,unit,word='y',reading='H',set='zodiac',folio='f70v2'):
 return dict(id=str(i),unit=unit,words=[word],reading=reading,set=set,folio=folio)
check('comma uncertainties retained',tokens('ab,cd.ef')==[None,None,'ef'])
check('brace uncertainty not deleted',tokens('ab{gap}cd')==[None])
check('confirmed word boundaries retained',tokens('ot.edy-')==['ot','edy'])
check('longest grouped units',glyphs('achckh')==['a','ch','ckh'])
check('tail cannot cross a word boundary',feature(dict(words=['ot','ch']),dict(kind='ending',width=2),P) is None)
check('family specificity',feature(dict(words=['qokeedy']),dict(kind='ending_family'),P)=='eedy')
check('residual opener reported',feature(dict(words=['ar']),dict(kind='opener'),P)=='other')
rng=random.Random(20261025)
for trial in range(100):
 rows=[row(i,'S'+str(rng.randrange(3)),rng.choice(['y','n','d'])) for i in range(rng.randrange(2,16))]
 vals=[r['words'][0] for r in rows]
 for v in ['y','n','d']:
  for within in [True,False]:
   pairs=[(i,j) for i in range(len(rows)) for j in range(len(rows)) if i!=j and ((rows[i]['unit']==rows[j]['unit'])==within)]
   hit=sum(vals[i]==v and vals[j]==v for i,j in pairs)
   got=pair_counts(rows,vals,v,within)
   check('brute force pair agreement %d %s %s'%(trial,v,within),got['numerator']==hit and got['denominator']==len(pairs))
a=[row(i,'S1' if i<3 else 'S2',w) for i,w in enumerate(['y','y','n','y','y'])]
w=pair_counts(a,[r['words'][0] for r in a],'y')
b=baseline(['y','y','n','n'],'y')
check('known within probability',w['numerator']==4 and w['denominator']==8)
check('known ratio three',ratio_of(w,b)==dict(numerator=3,denominator=1,value=3.0))
check('zero baseline undefined',ratio_of(w,baseline(['y','n','n'],'y')) is None)
for field,value in [('folio','f73r'),('reading','V')]:
 bad=row('bad','S1');bad[field]=value
 try:validate([bad]);ok=False
 except ValueError:ok=True
 check('rejection '+field,ok)
try:validate([row(1,'S1'),row(1,'S1')]);ok=False
except ValueError:ok=True
check('duplicate physical label rejected',ok)
rr=a+[row(10+i,'L1',word=w,set='plant-jar',folio='f88r') for i,w in enumerate(['y','y','n','n'])]
looks=[compute_look(rr,f,P) for f in P['planned_looks']]
res=summarize(looks,P)
check('missing F not replaced',res['readings']['F']['status']=='NOT_ESTIMABLE')
check('missing F is not NO_MARKER',res['joint_marker_outcome']=='NOT_ESTIMABLE' and not res['NO_MARKER'])
check('no common operation admitted with missing F',all(x is None for x in res['joint_removal_candidates'].values()))
check('five looks fit ten cap',len(P['planned_looks'])+P['previous_feature_looks']<=P['look_cap'])
out={'status':'PASS','checks_run':len(checks),'checks':checks,'scope':'Synthetic engineering checks only, no manuscript features or keys'}
(Path(__file__).parent/'ENGINEERING-CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['status','checks_run']}))
