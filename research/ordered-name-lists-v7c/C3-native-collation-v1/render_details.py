from pathlib import Path
import pypdfium2 as pdfium
P=Path(__file__).parent
for name,nums in [('xenophon-bude',[19,28,133,135]),('lapidary-1881',[304,305,306,307,308,309,310,311,312,313,314,315,316])]:
 d=pdfium.PdfDocument(str(P/'sources'/f'{name}.pdf'))
 for n in nums:d[n-1].render(scale=2).to_pil().save(P/'qa'/f'{name}-pdf{n}.png')
print('detail images rendered')
