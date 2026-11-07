"""Validate independently supplied geometry/votes. No API calls or agent raters."""
from common import *
import argparse, math
from collections import Counter

def box_ok(box,w,h):
    return (isinstance(box,list) and len(box)==4 and
            all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in box)
            and box[0]>=0 and box[1]>=0 and box[2]>0 and box[3]>0
            and box[0]+box[2]<=w and box[1]+box[3]<=h)

def import_geometry(path):
    d=load(path)
    if load(ROOT/'PROTOCOL.json').get('version')=='v6.1' and d.get('two_pass_verified') is not True:
        raise ValueError('v6.1 requires independently verified two-pass geometry')
    if not d.get('registrar_id') or not all(d.get(k) is True for k in
            ['outcome_blind','object_categories_unseen','picture_ratings_unseen']):
        raise ValueError('Independent registrar identity and all blindness attestations required')
    known={r['task_id']:r for r in load(ROOT/'LABEL-REGISTRATION.json')['rows']}
    pages={r['page']:r for r in load(ROOT/'registrar-only/PAGES.json')}
    accepted={}
    for row in d['rows']:
        tid=row['task_id']
        if tid not in known or tid in accepted: raise ValueError('Unknown or duplicate task')
        page=pages.get(known[tid]['page'])
        if not page or not box_ok(row['bbox'],page['native_width'],page['native_height']):
            raise ValueError('Missing native canvas or invalid box')
        if row.get('source_image_sha256')!=page['source_sha256'] or sha(page['source_image'])!=page['source_sha256']:
            raise ValueError('Native image hash mismatch')
        if not row.get('review_note'): raise ValueError('Explicit visual review note required')
        if not row.get('physical_label_id'):raise ValueError('Physical-label grouping is required')
        accepted[tid]=dict(known[tid],status='REGISTERED',bbox=row['bbox'],physical_label_id=row['physical_label_id'],single_line=row.get('single_line') is True,
            source_image_sha256=page['source_sha256'],registrar_id=d['registrar_id'],
            blind_attestation={k:d[k] for k in ['outcome_blind','object_categories_unseen','picture_ratings_unseen']})
    # Import is immutable; revisions must preserve originals in a new receipt.
    if any(r['status']=='REGISTERED' for r in known.values()): raise ValueError('Existing geometry requires versioned review; no overwrite')
    save(ROOT/'geometry-receipts'/f'{sha(path)}.json',d)
    result=[accepted.get(t,r) for t,r in known.items()]
    save(ROOT/'LABEL-REGISTRATION.json',dict(status='PARTIAL' if len(accepted)<len(result) else 'COMPLETE',rows=result))
    write_csv(ROOT/'DROPPED-LABELS.csv',['task_id','locus','page','reason'],
        [dict(task_id=r['task_id'],locus=r['locus'],page=r['page'],reason=r['status']) for r in result if r['status']!='REGISTERED'])
    return len(accepted)

def packet():
    from PIL import Image, ImageDraw, ImageOps
    pages={r['page']:r for r in load(ROOT/'registrar-only/PAGES.json')}
    dest=ROOT/'rater-only'; dest.mkdir(exist_ok=True)
    manual=(ROOT/'MANUAL.md').read_text(encoding='utf-8')
    (dest/'MANUAL.md').write_text(manual,encoding='utf-8')
    tasks=[]
    for r in load(ROOT/'LABEL-REGISTRATION.json')['rows']:
        if r['status']!='REGISTERED': continue
        p=pages[r['page']]
        if sha(p['source_image'])!=r['source_image_sha256']: raise ValueError('Changed source image')
        im=Image.open(p['source_image']).convert('RGB'); x,y,w,h=r['bbox']
        # Fixed context extent derives from native writing height, never object category.
        margin=12*h
        bounds=(max(0,int(x-margin)),max(0,int(y-margin)),min(im.width,math.ceil(x+w+margin)),min(im.height,math.ceil(y+h+margin)))
        crop=im.crop(bounds); draw=ImageDraw.Draw(crop)
        draw.rectangle((x-bounds[0],y-bounds[1],x+w-bounds[0],y+h-bounds[1]),outline='#e600cc',width=max(2,round(h*.08)))
        crop.thumbnail((1200,1200)); thumb=im.copy();thumb.thumbnail((320,480))
        canvas=Image.new('RGB',(crop.width+thumb.width+24,max(crop.height,thumb.height)), 'white')
        canvas.paste(crop,(0,0));canvas.paste(thumb,(crop.width+24,0))
        name=r['task_id']+'.png';canvas.save(dest/name)
        tasks.append(dict(task_id=r['task_id'],image=name,image_sha256=sha(dest/name)))
    save(dest/'TASKS.json',tasks)
    save(ROOT/'PACKET-FREEZE.json',dict(tasks=len(tasks),manual_sha256=sha(dest/'MANUAL.md'),tasks_sha256=sha(dest/'TASKS.json'),
        files={r['image']:r['image_sha256'] for r in tasks},
        privacy='Only anonymous task IDs, outlined native context crops, low-resolution thumbnails and manual. No transcript or class key.'))
    return len(tasks)

def validate_votes(rows, allowed):
    by={}
    for r in rows:
        if r['task_id'] not in allowed or r['task_id'] in by: raise ValueError('Unknown or duplicate task vote')
        if r['class'] not in CLASSES: raise ValueError('Invalid object class')
        if not all(r.get(k) for k in ['rater_id','family','response_sha256']): raise ValueError('Missing vote provenance')
        by[r['task_id']]=r
    if set(by)!=set(allowed): raise ValueError('Incomplete vote set: missing votes are not NONE or UNCLEAR')
    if len({(r['rater_id'],r['family']) for r in rows})!=1: raise ValueError('One independent rater identity per file')
    return by

def agreement():
    reg={r['task_id']:r for r in load(ROOT/'LABEL-REGISTRATION.json')['rows'] if r['status']=='REGISTERED'}
    if not reg: return dict(status='NOT_RUN_NO_REGISTERED_LABELS',join_open=False)
    A=validate_votes(read_csv(ROOT/'RATER-A.csv'),reg); B=validate_votes(read_csv(ROOT/'RATER-B.csv'),reg)
    a0,b0=next(iter(A.values())),next(iter(B.values()))
    if a0['rater_id']==b0['rater_id'] or (a0['family']==b0['family'] and a0['family']!='HUMAN'):
        raise ValueError('Independent identities and different model families (or humans) required')
    ids=sorted(reg); full=kappa([A[t]['class'] for t in ids],[B[t]['class'] for t in ids])
    ids4=[t for t in ids if A[t]['class'] in COLLAPSE and B[t]['class'] in COLLAPSE]
    four=kappa([COLLAPSE[A[t]['class']] for t in ids4],[COLLAPSE[B[t]['class']] for t in ids4])
    mode='FULL' if full is not None and full>=.60 else 'FOUR' if four is not None and four>=.60 else None
    return dict(status='RELIABLE' if mode else 'NOT_RELIABLE',join_open=bool(mode),mode=mode,n=len(ids),
        kappa_full=full,kappa_four=four,collapse_n=len(ids4),collapse_excluded=[t for t in ids if t not in set(ids4)],
        confusion_full={a:{b:sum(A[t]['class']==a and B[t]['class']==b for t in ids) for b in CLASSES} for a in CLASSES},
        raw_agreement=sum(A[t]['class']==B[t]['class'] for t in ids)/len(ids),
        missing_policy='No imputation. Undefined kappa cannot pass. Collapse uses paired in-domain votes only.',
        rater_A=a0['rater_id'],rater_B=b0['rater_id'])

def join():
    p=load(ROOT/'PROTOCOL.json')
    if p['claim_freeze_status']!='FROZEN': raise ValueError('Claim protocol not fully frozen')
    if not load(ROOT/'QUALIFICATION.json').get('scientific_gate_passed'):
        raise ValueError('Scientific qualification gate closed; no label–feature outcome join')
    frozen=load(ROOT/'FREEZE.json')
    if any(sha(ROOT/name)!=value for name,value in frozen['hashes'].items()): raise ValueError('Frozen input changed')
    g=agreement();save(ROOT/'AGREEMENT.json',g)
    if not g['join_open']: raise ValueError('Agreement gate closed')
    reg={r['task_id']:r for r in load(ROOT/'LABEL-REGISTRATION.json')['rows'] if r['status']=='REGISTERED'}
    A=validate_votes(read_csv(ROOT/'RATER-A.csv'),reg);B=validate_votes(read_csv(ROOT/'RATER-B.csv'),reg)
    crows=read_csv(ROOT/'RATER-C.csv');C={r['task_id']:r for r in crows}
    if len(C)!=len(crows) or not set(C)<=set(reg): raise ValueError('Unknown or duplicate C vote')
    out=[]
    for t,r in reg.items():
        ca,cb=A[t]['class'],B[t]['class']; chosen=ca; why='A_B_AGREE'
        if ca!=cb:
            c=C.get(t)
            if not c or c['class'] not in CLASSES or not c.get('response_sha256'): raise ValueError('Independent C adjudication missing')
            if c['rater_id'] in [A[t]['rater_id'],B[t]['rater_id']]: raise ValueError('C must be independent')
            chosen=c['class'];why='C_ADJUDICATED'
        if g['mode']=='FOUR': chosen=COLLAPSE.get(chosen,'EXCLUDED_COLLAPSE')
        out.append(dict(task_id=t,locus=r['locus'],**{'class':chosen},A=ca,B=cb,C=C.get(t,{}).get('class',''),adjudication=why))
    write_csv(ROOT/'LABEL-OBJECTS.csv',['task_id','locus','class','A','B','C','adjudication'],out)
    save(ROOT/'OUTCOME-JOIN.json',dict(rows=len(out),objects_sha256=sha(ROOT/'LABEL-OBJECTS.csv'),agreement=g))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('step',choices=['geometry','packet','agreement','join']);ap.add_argument('file',nargs='?');args=ap.parse_args()
    if args.step=='geometry': print(import_geometry(args.file))
    elif args.step=='packet': print(packet())
    elif args.step=='agreement':
        result=agreement();save(ROOT/'AGREEMENT.json',result);print(json.dumps(result))
    elif args.step=='join': join()
