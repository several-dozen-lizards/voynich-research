from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;old=P.parent/'C3-native-collation-v1';earlier=P.parent/'C3-revised-plan-v1/historical-sources'
jobs=[('Aries1',earlier/'FOL-0001V.jpg',(430,270,750,620)),('Aries5',old/'sources/FOL-0003R.jpg',(440,200,750,430)),('Aries20',old/'sources/FOL-0007R.jpg',(440,490,750,730)),('Aries21',old/'sources/FOL-0007V.jpg',(425,235,735,430)),('Aries23',old/'sources/FOL-0008R.jpg',(440,490,750,700)),('Aries26',old/'sources/FOL-0009R.jpg',(170,630,470,870)),('Taurus5',old/'sources/FOL-0013R.jpg',(165,250,455,450)),('Taurus6',old/'sources/FOL-0013R.jpg',(445,250,750,450)),('Taurus9',old/'sources/FOL-0014R.jpg',(165,250,465,450)),('Taurus10',old/'sources/FOL-0014R.jpg',(450,250,750,460)),('Taurus13',old/'sources/FOL-0015R.jpg',(155,465,455,685)),('Taurus17',old/'sources/FOL-0016R.jpg',(165,700,465,970)),('Taurus18',old/'sources/FOL-0016R.jpg',(440,750,750,1000)),('Taurus28',old/'sources/FOL-0019V.jpg',(150,660,455,925))]
receipt=[]
for title,path,box in jobs:
 im=Image.open(path).convert('RGB');crop=im.crop(box);crop=crop.resize((crop.width*2,crop.height*2))
 crop.save(P/'qa'/f'reinspect-{title}.png');receipt.append(dict(id=title,source=str(path),original_pixels=list(im.size),box=list(box),display_magnification=2,new_native_information=False,status='CROP_FOR_SAME_REVIEWER_REINSPECTION_NOT_INDEPENDENT_ADJUDICATION'))
(P/'qa/PRIOR-REVIEW-CROP-LOCATORS.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print('14 source crops prepared; magnification does not add pixels')
