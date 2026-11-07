"""Build source-only inventory. Never manufacture geometry or object votes."""
from common import *
from collections import Counter, defaultdict
from datetime import datetime, timezone
import shutil

def disposition(unit):
    code=unit['code']; desc=next((s for s in unit['comments'] if s.strip()),'')
    explicit_include={'f70v2.C','f71v.S2','f77r.N','f83r.X','f83r.Z'}
    explicit_exclude={'f57v.R3','f68v3.B','f86v3.Q'}
    if unit['unit'] in explicit_include: return 'INCLUDE',desc
    if unit['unit'] in explicit_exclude: return 'EXCLUDE_CONTINUOUS_TEXT',desc
    if code.startswith('P') or re.search(r'paragraph|paragr|plain text only|text on right hand',desc,re.I):
        return 'EXCLUDE_PARAGRAPH',desc
    if re.search(r'label|title|caption|single words|letters|symbols',desc,re.I):
        return 'INCLUDE',desc
    # Pharma row labels described as rows of plants, not always with the word label.
    if unit['unit'] in {'f100v.T','f100v.M','f100v.B'}: return 'INCLUDE',desc
    if re.search(r'radial|spokes',desc,re.I): return 'INCLUDE',desc
    if re.search(r'circular|circle.*text|ring.*text|text.*ring|band of text|text.*circle|circle.*line|circles of text',desc,re.I):
        return 'EXCLUDE_CONTINUOUS_CIRCULAR',desc
    if code.startswith('L'): return 'INCLUDE',desc
    return 'REVIEW_TYPE',desc

def main():
    if (ROOT/'OUTCOME-JOIN.json').exists(): raise RuntimeError('Build cannot overwrite a joined dataset')
    if (ROOT/'LABEL-REGISTRATION.json').exists() and any(r['status']=='REGISTERED' for r in load(ROOT/'LABEL-REGISTRATION.json')['rows']):
        raise RuntimeError('Build cannot overwrite accepted geometry; create a versioned revision')
    if any((ROOT/f'RATER-{r}.csv').exists() and read_csv(ROOT/f'RATER-{r}.csv') for r in ['A','B','C']):
        raise RuntimeError('Build cannot overwrite a study with actual votes')
    units,rows=source(); decisions={k:disposition(v) for k,v in units.items()}
    native=load(PROJECT/'image-context-v4/registration/registrar-only/PAGES.json')
    pages={p['folio']:p for p in native}
    unitrows=[]
    for key,u in units.items():
        rr=[r for r in rows if r['unit']==key]
        if not rr: continue
        status,desc=decisions[key]
        unitrows.append(dict(unit=key,code=u['code'],description=desc,status=status,
                             reserved=rr[0]['page'] in RESERVED,section=rr[0]['section'],
                             all_reading_loci=len({r['locus'] for r in rr}),
                             H=sum(r['reading']=='H' for r in rr),F=sum(r['reading']=='F' for r in rr),
                             source_line=u['source_line']))
    write_csv(ROOT/'UNIT-TYPE-AUDIT.csv',list(unitrows[0]),unitrows)
    selected=[r for r in rows if decisions.get(r['unit'],('REVIEW_TYPE',))[0]=='INCLUDE' and r['page'] not in RESERVED]
    groups=defaultdict(list)
    for r in selected: groups[r['locus']].append(r)
    inventory=[]; registration=[]; features=[]; locator=[]
    for loc,rr in sorted(groups.items()):
        r=rr[0]; task='V6-'+digest(loc)[:16]; image=pages.get(r['page'])
        readings={x['reading']:x for x in rr}
        assert len(readings)==len(rr),loc
        inventory.append(dict(task_id=task,locus=loc,page=r['page'],folio=r['folio'],unit=r['unit'],
                              code=r['code'],section=r['section'],scribe=r['scribe'],
                              available_readings=''.join(sorted(readings)),H_raw=readings.get('H',{}).get('raw',''),
                              F_raw=readings.get('F',{}).get('raw',''),image_ready=bool(image)))
        status='UNREGISTERED_PENDING_INDEPENDENT_REVIEW' if image else 'UNREGISTERED_IMAGE_PANEL'
        registration.append(dict(task_id=task,locus=loc,page=r['page'],status=status,bbox=None,
                                 source_image_sha256=None,registrar_id=None,blind_attestation=None))
        locator.append(dict(task_id=task,locus=loc,page=r['page'],unit=r['unit'],line=r['line'],
                            status=status,reading_presence=''.join(sorted(readings))))
        for reading in ['H','F']:
            if reading not in readings: continue
            x=readings[reading]; words=x['words']; usable=bool(words) and all(words)
            fd=feature_dict(''.join(words)) if usable else None
            features.append(dict(task_id=task,locus=loc,reading=reading,word_count=len(words),
                                 eva='.'.join(w or '?' for w in words),eligible=usable,
                                 feature_unit='concatenated EVA code characters; explicit word count retained',
                                 features=json.dumps(fd,sort_keys=True) if fd else '',
                                 word_shape_template_class='',template_status='UNRESOLVED_PROJECT_DEFINITION'))
    write_csv(ROOT/'LABEL-INVENTORY.csv',list(inventory[0]),inventory)
    write_csv(ROOT/'FEATURES.csv',list(features[0]),features)
    save(ROOT/'LABEL-REGISTRATION.json',dict(status='NO_ACCEPTED_LABEL_GEOMETRY',rows=registration))
    write_csv(ROOT/'DROPPED-LABELS.csv',['task_id','locus','page','reason'],
              [dict(task_id=x['task_id'],locus=x['locus'],page=x['page'],reason=x['status']) for x in registration])
    for name in ['A','B','C']:
        path=ROOT/f'RATER-{name}.csv'
        if not path.exists(): write_csv(path,['task_id','class','rater_id','family','response_sha256'],[])
    write_csv(ROOT/'LABEL-OBJECTS.csv',['task_id','locus','class','A','B','C','adjudication'],[])
    save(ROOT/'registrar-only/LOCI.json',locator)
    save(ROOT/'registrar-only/PAGES.json',[
        dict(page=p,**{k:v for k,v in pages[p].items() if k!='folio'},
             source_image=str((PROJECT/'image-context-v4/registration/registrar-only'/pages[p]['image']).resolve()),
             source_sha256=sha(PROJECT/'image-context-v4/registration/registrar-only'/pages[p]['image']))
        for p in sorted({r['page'] for r in selected}) if p in pages])
    # No object hints, transcript bodies, section/scribe metadata or results enter registrar input.
    save(ROOT/'registrar-only/REGISTRATION-TEMPLATE.json',dict(registrar_id='',outcome_blind=False,
        object_categories_unseen=False,picture_ratings_unseen=False,rows=[]))
    (ROOT/'registrar-only/README.txt').write_text(
        'Independent registrar only. Read LOCI.json and PAGES.json; inspect the native source pixels. '
        'Map each exact locus to a native [x,y,width,height] writing box by source order/position. '
        'No nearest-line guesses or acceptance by count alone. Preserve multiline label grouping. '
        'Do not inspect the parent directory. If uncertain, leave the locus UNREGISTERED. '
        'Submit REGISTRATION-TEMPLATE.json with rows {task_id,bbox,source_image_sha256,review_note}. '
        'All three blindness attestations and registrar_id are required. '
        'Descriptions and object categories are intentionally absent.\n',encoding='utf-8')
    counts=Counter((r['section'],r['code'],r['reading']) for r in selected)
    write_csv(ROOT/'TYPE-COUNTS.csv',['section','code','reading','loci'],
              [dict(section=s,code=c,reading=t,loci=n) for (s,c,t),n in sorted(counts.items())])
    t2_pairs(rows, selected)
    save(ROOT/'SOURCE-MANIFEST.json',dict(sources={str(p):sha(p) for p in [EVT,DATA/'Davis-hands.original.csv',
        PROJECT/'image-context-rater-v1/research-only/legacy-candidate-text-audit.json']},
        physical_loci=len(inventory),by_reading=dict(Counter(r['reading'] for r in selected)),
        HF_reading_loci=len(features),image_ready_loci=sum(bool(r['image_ready']) for r in inventory),
        type_review_units=[r['unit'] for r in unitrows if r['status']=='REVIEW_TYPE' and not r['reserved']],
        unavailable_panels=sorted({r['page'] for r in selected if r['page'] not in pages}),
        reserved=sorted(RESERVED),generated_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(dict(loci=len(inventory),HF_features=len(features),type_reviews=sum(x['status']=='REVIEW_TYPE' for x in unitrows))))

def distance_one(a,b):
    if abs(len(a)-len(b))>1: return False
    if a==b: return True
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b): a,b=b,a
    return any(a==b[:i]+b[i+1:] for i in range(len(b)))

def t2_pairs(allrows,selected):
    old=load(PROJECT/'image-context-rater-v1/research-only/legacy-candidate-text-audit.json')
    known={(r['source_page'],r['word'],target) for r in old for target in r['supplied_targets']}
    out=[]
    # Exact distance search indexed by word length; all matches retained, no judgment selection.
    for reading in ['H','F']:
        herbal=defaultdict(list)
        for r in allrows:
            if r['reading']==reading and r['section']=='Botanical' and r['page'] not in RESERVED:
                for i,w in enumerate(r['words']):
                    if w: herbal[w].append((r,i))
        bylen=defaultdict(list)
        for w in herbal: bylen[len(w)].append(w)
        for r in selected:
            if r['reading']!=reading or r['section']!='Recipes': continue
            for i,w in enumerate(r['words']):
                if not w: continue
                matches=[w] if w in herbal else []
                if len(w)>=5:
                    matches+=sorted(v for n in [len(w)-1,len(w),len(w)+1] for v in bylen[n]
                                    if v!=w and len(v)>=5 and distance_one(w,v))
                for v in matches:
                    perpage=defaultdict(list)
                    for h,j in herbal[v]: perpage[h['page']].append((h,j))
                    for page,occ in perpage.items():
                        h=occ[0][0]
                        previous=(r['page'],w,page) in known
                        out.append(dict(pair_id='P6-'+digest('|'.join([reading,r['locus'],str(i),v,page]))[:16],
                            reading=reading,pharma_locus=r['locus'],word_slot=i,pharma_word=w,
                            herbal_page=page,herbal_word=v,match='EXACT' if w==v else 'EDIT1',
                            herbal_occurrences=json.dumps([dict(locus=x['locus'],slot=j) for x,j in occ]),
                            herbal_scribe=h['scribe'],previously_seen=previous,
                            exposure_status='PREVIOUS_NINE' if previous else 'NOT_IN_NINE_LEDGER_NOT_PROVEN_UNSEEN'))
    write_csv(ROOT/'T2-MATCHED-PAIRS.csv',list(out[0]) if out else ['pair_id'],out)
    save(ROOT/'PREVIOUS-NINE.json',dict(source='image-context-rater-v1/research-only/legacy-candidate-text-audit.json',records=old,
        caution='Nine candidate words expand to eleven supplied page pairs; f90v2 may not be Botanical. Fresh primary requires broader exposure audit, not merely absence from this list.'))

if __name__=='__main__': main()
