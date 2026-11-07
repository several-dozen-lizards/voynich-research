from pathlib import Path
import re
p=Path(r'C:/Users/lewis/.codex/visualizations/2026/10/21/01a15c3d-56da-7f02-bc15-2522dc396abd/voynich-layout/data/text16e6.original.evt')
out=[]
with p.open('rb') as f:
 for b in f:
  if re.match(rb'^<f[0-9]',b):break
  if b.startswith(b'#'):out.append(b.decode('latin1').rstrip())
r=Path(__file__).parent
(r/'SOURCE-GLOBAL-HEADER.txt').write_text('\n'.join(out)+'\n',encoding='utf8')
print('\n'.join(out)[:24000])
