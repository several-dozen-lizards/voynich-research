import json,hashlib
from pathlib import Path
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');res=json.loads((p/'REVIEW.v06.pending.json').read_text());a=json.loads((p/'PAGES.json').read_text());receipt=json.loads((p/'SOURCE-QA-RECEIPT.json').read_text())
# Correct native first-lower-row ascender on f52v.
b=res['pages'][35]['blocks'][0];q=b['lines'][6]['box'];dy=7/(a[35]['native_height']/a[35]['native_width']*600)*a[35]['native_height'];q[1]=round(q[1]-dy,2);q[3]=round(q[3]+dy,2)
verified=[];abstained=[];errors=[];unfinished=[]
for i,page in enumerate(res['pages']):
 if not page['geometry_complete']:unfinished.append(page['folio'])
 for b in page['blocks']:
  x,y,w,h=b['box'];
  if min(x,y,w,h)<0 or x+w>a[i]['native_width']+.1 or y+h>a[i]['native_height']+.1:errors.append([page['folio'],b['block_id'],'bounds'])
  if b['decision']=='VERIFIED':
   verified.append([page['folio'],b['block_id'],b['unit'],len(b['lines'])]);prev=-1
   for k,z in enumerate(b['lines']):
    xx,yy,ww,hh=z['box'];
    if z['line_number']!=k+1 or yy<prev or xx<x-.1 or yy<y-.1 or xx+ww>x+w+.1 or yy+hh>y+h+.1:errors.append([page['folio'],b['block_id'],k,'line QA'])
    prev=yy
  else:abstained.append([page['folio'],b['block_id'],b['registration_status']])
assert not errors,errors
(p/'REVIEW.v06.json').write_text(json.dumps(res,indent=2));(p/'REVIEW.json').write_text(json.dumps(res,indent=2));sha=hashlib.sha256((p/'REVIEW.json').read_bytes()).hexdigest();receipt.update(final_review_sha256=sha,verified_blocks=verified,verified_block_count=len(verified),abstained_block_count=len(abstained),unfinished_fine_segmentation_pages=unfinished);receipt['checkpoints'].append('REVIEW.v06.json');receipt['actual_views']['native_endpoint_correction_overlays']=['corrected13.png','corrected34.png','corrected35.png','corrected41.png'];receipt['corrections'].append('Completed native source endpoint correction for f20v, f51r, f6v and f52v, restoring four registrations only after visual enclosure QA. Corrected f52v lower first-row ascender enclosure.');receipt['limitations'].append('Ten pages retain explicit unfinished fine segmentation, rather than being represented as intrinsic manuscript ambiguity.');(p/'SOURCE-QA-RECEIPT.json').write_text(json.dumps(receipt,indent=2));(p/'PROGRESS.txt').write_text('Source inspection 51/51. v06: 20 certified blocks after native endpoint corrections. Geometry remains PARTIAL on ten listed fine-segmentation pages. All other retained fields have explicit source mapping abstentions.\n');print(json.dumps({'sha256':sha,'verified':len(verified),'abstained':len(abstained),'unfinished_pages':unfinished,'errors':errors}))
