from pathlib import Path
import json
import numpy as np
from scipy.stats import binomtest
R=Path(__file__).resolve().parent;d=json.loads((R/'RESULTS.json').read_text(encoding='utf-8'));out=[]
for p in d['panels']:
 a=np.load(R/(p['reading']+'-'+p['mode']+'-null.npz'))['maxima'];k=int((a[:,1]>=3).sum())
 ci=binomtest(k,1999).proportion_ci(confidence_level=.95,method='exact')
 out.append(dict(reading=p['reading'],mode=p['mode'],statistic='crossfolio_recurring_middle_types',max_tail_exceedances=k,shuffles=1999,eight_panel_tail_probability_CI95=[min(1,8*ci.low),min(1,8*ci.high)],scope='Post-run Monte Carlo uncertainty in conditional max-tail probability only; no additional shuffles or test changes.'))
(R/'MC-UNCERTAINTY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Finite-shuffle uncertainty recorded without changing frozen tests.')
