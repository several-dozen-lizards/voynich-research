from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).resolve().parent; old=P.parent/'zodiac-mapping-v84'
ids=['f70v1-outer-04','f70v1-outer-06','f70v1-outer-08','f70v1-inner-01','f71r-inner-03','f71r-inner-04','f71v-outer-07','f72r2-outer-09','f72r2-outer-10','f72r2-outer-11','f72r2-outer-12']
manifest={r['id']:r for r in json.loads((P/'CROP-MANIFEST.json').read_text())}
for id in ids:
    r=manifest[id]; im=Image.open(old/r['source']).crop(r['box']).rotate(r['rotation'],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(235,225,204)); im.thumbnail((650,650)); im.save(P/(id+'-detail.png'))
