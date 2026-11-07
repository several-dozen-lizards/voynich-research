"""Describe development provenance strata without opening fresh reserves."""
from pathlib import Path
import csv,json,io
from collections import Counter
from source_cut2 import CUT,dump

metadata=list(csv.DictReader(io.StringIO((CUT/'cremma-metadata.metadata').read_bytes().decode('utf-8-sig','replace'))))
lookup={r['Folder'].split('/')[-1]:r for r in metadata}
rows=json.loads((CUT/'ABBREVIATED-LATIN-ROWS.json').read_text())
needed=list(json.loads((CUT/'DEVELOPMENT-INVENTORY.json').read_text())['AbbreviatedLatin']['known_gap_support'])
records=[]
for ms in sorted(set(r['manuscript'] for r in rows)):
    rr=[r for r in rows if r['manuscript']==ms];m=lookup[ms]
    counts=Counter(u for r in rr for s in r['slots'] if s['units'] is not None for u in s['units'])
    records.append(dict(manuscript=ms,notBefore=int(m['notBefore']),notAfter=int(m['notAfter']),genre=m['Type'],content=m['Content'],
        pages=len(set(r['page'] for r in rr)),lines=len(rr),slots=sum(len(r['slots']) for r in rr),marked_readable_slots=sum(s.get('explicit_mark',False) for r in rr for s in r['slots']),
        known_gap_support={u:counts[u] for u in needed}))
strata={}
for label,predicate in [('through1399',lambda r:r['notAfter']<=1399),('15thcentury',lambda r:r['notBefore']>=1400),('medical',lambda r:r['genre']=='Medic.')]:
    selected=[r for r in records if predicate(r)]
    counts={u:sum(r['known_gap_support'][u] for r in selected) for u in needed}
    strata[label]=dict(manuscripts=[r['manuscript'] for r in selected],known_gap_support=counts,uncovered=[u for u,n in counts.items() if not n])
dump(CUT/'ABBREVIATED-LATIN-STRATA.json',dict(manuscripts=records,strata=strata,interpretation='Literal Unicode attestation only. Neither function, abbreviation expansion nor medical-register transfer follows from a shared codepoint.'))
print(json.dumps(strata))
