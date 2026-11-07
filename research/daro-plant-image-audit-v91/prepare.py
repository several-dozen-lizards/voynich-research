from pathlib import Path
import json,hashlib,urllib.request,concurrent.futures,sys
R=Path(__file__).resolve().parent;P=R.parent
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
targets=['f14v','f18r','f18v','f19v','f43v'];sensitivity=['f24v']
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Image-first descriptive botanical triage, not a plant identification, blind experiment, phonetic test or statistical association.',primary=targets,selection='All five illustrated herbal pages with literal initial daro in any available reading in v90. Four fully readable H cases plus f43v H darod* / C,F,G,U darody.',sensitivity=sensitivity,sensitivity_reason='C doar f24v versus H/F/U doiir: adjacent query, not a daro hit. Display separately, never silently add to primary set.',excluded='f57v diagram not a plant illustration. No new folios selected by visual resemblance or names.',order='Record morphology from Yale images before opening plant identifications or botanical reference comparisons. Prior knowledge of fennel hypothesis and other Voynich work prevents a blind claim. Inspect all pages, preserve negatives, then compare fennel, plausible lookalikes and published page identifications separately.',morphology=['habit and branching','leaf attachment and division','leaf segment width and form','inflorescence structure and colour','root form','coherence of multiple organs','uncertainty and stylization'],comparison='Compare constellation of traits; a single feathery leaf or yellow mark cannot identify fennel. Keep absent, unclear and contradictory distinct. Illustrations need not be botanically literal. Do not derive identity from daro text or seek phonetic fit.',names='No name/sound fitting. Existing published IDs are proposals tagged to their source and dated provenance where available; distinguish visual proposal from text-driven decipherment.',limits='Selection by text is already exposed. No selected non-daro controls, full-manuscript image search, prevalence estimate, botanist review or causal/semantic claim.'))
 manifest=P/'g-ending-audit-v89/YALE-MANIFEST.json'
 save('PRE-IMAGE-FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',manifest,P/'oalch-hermetic-audit-v90/EVENTS.json']})
 m=json.loads(manifest.read_text());out=[]
 for page in targets+sensitivity:
  matches=[x for x in m['items'] if page in x.get('label',{}).get('none',[])]
  if not matches:matches=[x for x in m['items'] if any(t.strip('[] ')==page[1:] for t in x.get('label',{}).get('none',[]))]
  assert len(matches)==1,(page,len(matches))
  x=matches[0];b=x['items'][0]['items'][0]['body'];out.append(dict(page=page,label=x['label'],url=b['id'],width=b['width'],height=b['height'],canvas=x['id'],sensitivity=page in sensitivity))
 save('IMAGE-SOURCES.json',out);print(json.dumps(out,indent=2))
else:
 from PIL import Image,ImageOps,ImageDraw
 for p,h in json.loads((R/'PRE-IMAGE-FREEZE.json').read_text()).items():assert sha(Path(p))==h
 sources=json.loads((R/'IMAGE-SOURCES.json').read_text());(R/'images').mkdir(exist_ok=True)
 def fetch(x):
  p=R/'images'/f"{x['page']}.jpg"
  if not p.exists():
   with urllib.request.urlopen(x['url'],timeout=90) as q:p.write_bytes(q.read())
  im=Image.open(p);assert im.size==(x['width'],x['height'])
  return dict(**x,path=str(p),sha256=sha(p))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:receipts=list(pool.map(fetch,sources))
 save('IMAGE-RECEIPTS.json',receipts)
 for x in receipts:
  im=Image.open(x['path']).convert('RGB');im.thumbnail((1050,1500));im.save(R/f"{x['page']}-overview.jpg",quality=94)
 print('Downloaded and verified '+str(len(receipts))+' Yale images. Overview images ready.')
