from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image
P=Path(__file__).parent;old=P.parent/'C3-native-collation-v1'
doc=pdfium.PdfDocument(str(old/'sources/lapidary-1881.pdf'))
for n in range(317,324):doc[n-1].render(scale=2).to_pil().save(P/'qa'/f'lapidary-1881-pdf{n}.png')
print('native pixels',Image.open(P/'sources/FOL-0021R.jpg').size)
