from pathlib import Path
import collections,json
from engine import QUESTIONS,belongs
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json')
claims={('Balneological',0):(212,134),('Balneological',1):(102,50),('Balneological',2):(68,39),('Botanical',0):(71,40),('Botanical',3):(47,10),('Starred paragraphs',0):(172,88),('Starred paragraphs',2):(58,14),('Starred paragraphs',3):(104,31)}
comparison=[]
for (section,j),claim in claims.items():
 audit=next(p for p in d['pooled_reproduction_audit'] if p['section']==section and p['reading']=='H')['rules'][j]
 comparison.append(dict(section=section,A=audit['A'],B=audit['B'],supplied_forward=claim[0],supplied_reverse=claim[1],reconstructed_forward=audit['forward'],reconstructed_reverse=audit['reverse'],exact_count_match=claim==(audit['forward'],audit['reverse']),scope='H full-source rawP section pooling, audit only; unavailable original script/category definitions not recovered'))
(R/'CLAIM-COMPARISON.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
groups=collections.defaultdict(list)
for r in load(P/'frequency-atlas-v48/rows.json'):
 if r[2] in ['Balneological','Botanical','Starred paragraphs'] and r[5]!='P':groups[(r[2],r[3],r[4],r[5],r[0])].append(r)
out=[]
for key,rs in sorted(groups.items()):
 rules=[]
 for A,B in QUESTIONS:
  f=b=0
  for r in rs:
   for a,z in zip(r[7],r[7][1:]):
    if a is None or z is None:continue
    f+=belongs(a,A) and belongs(z,B);b+=belongs(a,B) and belongs(z,A)
  rules.append(dict(A=A,B=B,forward=f,reverse=b))
 out.append(dict(section=key[0],hand=key[1],variety=key[2],format=key[3],reading=key[4],lines=len(rs),rules=rules,scope='Non-P raw-format descriptive inventory only, not inferential test or pooled paragraph data'))
(R/'NON-P-FORMAT-INVENTORY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
alternatives=[]
raw=load(P/'frequency-atlas-v48/rows.json')
for section in ['Balneological','Botanical','Starred paragraphs']:
 rs=[r for r in raw if r[0]=='H' and r[2]==section and r[5]=='P']
 for name,A,B in [('qok-prefix versus ol/or-prefix union',lambda w:w.startswith('qok'),lambda w:w.startswith(('ol','or'))),('l/s opening excluding sh versus a opening',lambda w:w.startswith(('l','s')) and not w.startswith('sh'),lambda w:w.startswith('a'))]:
  f=b=0
  for r in rs:
   for a,z in zip(r[7],r[7][1:]):
    if a is None or z is None:continue
    f+=A(a) and B(z);b+=A(z) and B(a)
  alternatives.append(dict(section=section,reading='H',definition=name,forward=f,reverse=b,status='Postinspection definition-disambiguation audit only; no new statistical tests, no claim to recover missing script. Original frozen primary sh/qok test unchanged.'))
(R/'ALTERNATIVE-DEFINITION-AUDIT.json').write_text(json.dumps(alternatives,indent=2),encoding='utf-8')
print('Quoted-count comparison and separate non-P format inventory saved.')
