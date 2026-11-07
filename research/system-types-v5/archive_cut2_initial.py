from source_cut2 import CUT,ROOT
from pathlib import Path
import shutil,json
p=CUT/'development-history/initial-section-control';p.mkdir(parents=True,exist_ok=True)
names=['QUALIFICATION-PLAN.json','RESULTS.json','DEVELOPMENT-SEAL.json','DEVELOPMENT-INVENTORY.json','DEVELOPMENT-UNITS.json','DEVELOPMENT-CODEBOOKS.json','SOURCE-ENTRYPOINT-TRIALS.json','SEVEN-SHORT-SOURCE-CASES.json','LANGUAGE-GAP-EVIDENCE.json']
for n in names:
    if not (p/n).exists():shutil.copyfile(CUT/n,p/n)
for n in ('source_cut2.py','qualify_source_cut2.py'):
    if not (p/n).exists():shutil.copyfile(ROOT/n,p/n)
print('Initial new-cantica control and qualification preserved before independent-author supplement.')
