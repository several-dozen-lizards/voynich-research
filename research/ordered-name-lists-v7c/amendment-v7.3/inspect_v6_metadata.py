import csv,json,collections
from pathlib import Path
p=Path(r'C:/Users/lewis/OneDrive/Documents/ChatGPT/Voynich/label-objects-v6/UNIT-TYPE-AUDIT.csv')
with p.open(encoding='utf-8-sig',newline='') as f:r=list(csv.DictReader(f))
print(json.dumps({'fields':list(r[0]),'sections':dict(collections.Counter(x['section'] for x in r)),'pharma_units':[x for x in r if x['status']=='INCLUDE' and x['section'] in ['Recipes','Pharmaceutical']]}))
