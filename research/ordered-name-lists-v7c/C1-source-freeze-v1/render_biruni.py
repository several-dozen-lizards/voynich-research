import pypdfium2 as p
from pathlib import Path
r=Path(__file__).parent
d=p.PdfDocument(str(r/'sources/biruni-sachau1879.pdf'))
for n in range(362,370): d[n-1].render(scale=2).to_pil().save(str(r/'sources'/('biruni-p%03d.png'%n)))
