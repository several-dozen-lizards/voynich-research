import pypdfium2 as p
from pathlib import Path
r=Path(__file__).parent
d=p.PdfDocument(str(r.parent/'sources/picatrix-pingree-1986.pdf'))
for n in [51,52,53]: d[n-1].render(scale=2).to_pil().save(str(r/'sources'/('picatrix-p%03d.png'%n)))
