"""Independent full frozen-engine replay of the first synthetic null family flag."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
import importlib.util,json,numpy as np
P=Path(__file__).parent;ROOT=P.parent
s=importlib.util.spec_from_file_location('controls',P/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
rowsdata=json.loads((P/'SUPPORT-ROWS.json').read_text(encoding='utf-8'));trials=json.loads((P/'CONTROL-TRIALS.json').read_text(encoding='utf-8'));chosen=next(r for r in trials if r['scenario']=='independent-null' and r['scan_family_flag'] and r['scan_estimable_classes']==17);reading=chosen['reading'];rows=rowsdata[reading];j=next(j for j,p in enumerate(chosen['scan_holm']) if p is not None and p<.05)
maxline=defaultdict(int)
for r in json.loads((ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json').read_text(encoding='utf-8'))['lines']:maxline[(r['task_id'],r['block_id'])]=max(maxline[(r['task_id'],r['block_id'])],r['line_number'])
Y=c.simulate(rows,chosen['scenario'],reading,chosen['trial'],maxline);L=np.load(P/('PERMUTATION-'+reading+'.npy'));groups=defaultdict(list)
for i,r in enumerate(rows):groups[r['folio']].append(i)
keep=[i for i,r in enumerate(rows) if len({z['label'] for z in rows if z['folio']==r['folio']})>=2];small=[rows[i] for i in keep];sy=Y[keep]
full=c.m.cmh(c.refrows(rows,Y),c.m.CLASSES[j])['statistic'];reduced=c.m.cmh(c.refrows(small,sy),c.m.CLASSES[j])['statistic'];assert abs(full-reduced)<1e-8
for b in (1,5000,10000):assert abs(c.m.cmh(c.refrows(rows,Y,L[b]),c.m.CLASSES[j])['statistic']-c.m.cmh(c.refrows(small,sy,L[b,keep]),c.m.CLASSES[j])['statistic'])<1e-8
above=0
for b in range(1,10001):
 score=c.m.cmh(c.refrows(small,sy,L[b,keep]),c.m.CLASSES[j])['statistic'];above+=score>=full-1e-12
p=(1+above)/10001;assert p==chosen['scan_p'][j]
result=dict(status='EXACT_REFERENCE_P_MATCH',selection='First fully estimable independent-null family flag, then first flagged class; synthetic diagnostic only',reading=reading,trial=chosen['trial'],feature=c.m.CLASSES[j],original_engine_observed=full,draws=10000,reference_p=p,accelerated_p=chosen['scan_p'][j],holm_p=chosen['scan_holm'][j],removed_folios='Only immutable single-label folios; exact zero CMH contributions for all permutations, full/reduced checks passed',real_word_classes_used=False)
(P/'REFERENCE-COMPLETE-NULL-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
