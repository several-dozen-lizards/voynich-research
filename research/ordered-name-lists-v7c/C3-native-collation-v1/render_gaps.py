from pathlib import Path
import pypdfium2 as pdfium
P=Path(__file__).parent;d=pdfium.PdfDocument(str(P/'sources/lapidary-1881.pdf'))
for n in [328,360]:d[n-1].render(scale=2).to_pil().save(P/'qa'/f'lapidary-1881-pdf{n}.png')
