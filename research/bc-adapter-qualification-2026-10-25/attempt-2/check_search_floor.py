import sys
sys.dont_write_bytecode=True
import importlib.util,itertools,json
from pathlib import Path
import numpy as np
P=Path(__file__).parent
s=importlib.util.spec_from_file_location('study',P/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
g=m.Geometry([4,4,4]);target=np.arange(1,13)
null=np.array([a+b+c for a in itertools.permutations(range(1,5)) for b in itertools.permutations(range(5,9)) for c in itertools.permutations(range(9,13))])
scores=g.score(null,target);perfect=int((scores==12).sum());assert len(null)==13824 and perfect==512
out=dict(status='EXACTLY_VERIFIED',null_orders=len(null),perfect_matches=perfect,exact_tail_probability=perfect/len(null),fraction='1/27',frozen_alpha=.01,can_clear_frozen_alpha=False,interpretation='No tuning; exhaustive synthetic null proof explaining the failed small-band power cells')
(P/'EXACT-SEARCH-FLOOR.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
