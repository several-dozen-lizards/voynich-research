from pathlib import Path
import pypdf
p=Path(__file__).parent
r=pypdf.PdfReader(p/'sources/herrmann-2017-v2.pdf')
for i,page in enumerate(r.pages):
 t=page.extract_text()
 if i<5: print('PAGE',i+1,t[:18000])
(p/'sources/herrmann-2017-v2-extract.txt').write_text('\n'.join(x.extract_text() for x in r.pages),encoding='utf-8')
import pypdfium2 as pdfium
pdf=pdfium.PdfDocument(p/'sources/herrmann-2017-v2.pdf')
for i in [2,3]: pdf[i].render(scale=1.5).to_pil().save(p/f'sources/herrmann-page-{i+1}.png')
