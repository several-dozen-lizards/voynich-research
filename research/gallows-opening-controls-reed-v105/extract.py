"""Bounded-memory extraction of inspectable examples; never alter frozen results."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
def panels(path):
    decoder=json.JSONDecoder();buf='';done=False
    with path.open(encoding='utf8') as f:
        while True:
            buf=buf.lstrip(' \r\n\t,[')
            if buf.startswith(']'):return
            try:obj,end=decoder.raw_decode(buf)
            except json.JSONDecodeError:
                chunk=f.read(1024*1024)
                if not chunk:raise ValueError('Incomplete JSON array')
                buf+=chunk;continue
            yield obj;buf=buf[end:]

examples=[];compact=[]
for name in ['TRAINING-RESULTS.json','TEST-RESULTS.json']:
    for x in panels(R/name):
        compact.append({k:v for k,v in x.items() if k!='cells'})
        if x['view']!='main' or x['position']!='other' or x['B']!='kt' or x['A'] not in ['fp','f','p']:continue
        for c in x['cells']:
            if c['status']=='informative':examples.append({k:x[k] for k in ['transcriber','A','B','position','split']}|c)
(R/'PAGE-RESULTS.json').write_text(json.dumps(compact,indent=2),encoding='utf8')
(R/'INFORMATIVE-EXAMPLES.json').write_text(json.dumps(examples,indent=2),encoding='utf8')
for x in examples:
    if x['A']=='f' or x['split']=='test':print(json.dumps(x))
