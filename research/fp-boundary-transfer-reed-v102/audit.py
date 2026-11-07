from pathlib import Path
import ast, collections, csv, hashlib, html, json, math, re
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parent
P=R.parent
OLD=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40')
LAY=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout')
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x): (R/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

inputs=[P/'frequency-atlas-v48/rows.json',LAY/'data/text16e6.original.evt',
    LAY/'predictions-initial.json',LAY/'frozen-rule-initial.json',
    OLD/'voynich-registration-v39/FULL-REGISTRATION.json',
    OLD/'voynich-registration-v39/CORRECTIONS.json',
    OLD/'voynich-alignment-v31/boundaries.json',
    OLD/'voynich-alignment-v37/geometry.json',
    OLD/'voynich-alignment-v37/unwrap.png',OLD/'voynich-blocks-v29/f57v.jpg',
    OLD/'voynich-matched-family-v26/f57v-slots.json',R/'PROTOCOL.json']
before={str(p):sha(p) for p in inputs}
save('INPUT-FREEZE.json',before)

# Same structural paragraph convention as v73, without importing its executable driver.
flags={};prev={};raws={}
for line in (LAY/'data/text16e6.original.evt').read_text(encoding='latin1').splitlines():
    m=re.match(r'^<(f\d+[rv]\d*)\.(P[^.]*)\.([^;]+);([HF])>\s*(.*)',line)
    if not m: continue
    page,place,num,tr,text=m.groups();loc=f'{page}.{place}.{num}'
    clean=re.sub(r'\{[^}]*\}','',text.split('#')[0]).strip();pr=prev.get((tr,page))
    if num=='1': opening=True
    elif pr and pr['end']=='=': opening=True
    elif pr and pr['end']=='-' and pr['place']==place: opening=False
    else: opening=None
    flags[(tr,loc)]=opening;raws[(tr,loc)]=text
    prev[(tr,page)]={'end':clean[-1:] if clean[-1:] in ['=','-'] else None,'place':place}

events=[];excluded=collections.Counter()
for tr,page,section,hand,lang,fmt,loc,words in load(P/'frequency-atlas-v48/rows.json'):
    if fmt!='P': continue
    opening=flags.get((tr,loc))
    if opening is None: excluded[tr+'_ambiguous_lines']+=1; continue
    for i,w in enumerate(words):
        if w is None: excluded[tr+'_unknown_slots']+=1; continue
        category=('paragraph_first' if opening else 'continuation_first') if i==0 else ('opening_line_other' if opening else 'continuation_other')
        firstgal=next(iter(re.findall('[ktfp]',w)),None)
        events.append(dict(tr=tr,page=page,section=section,hand=hand,language=lang,loc=loc,
            index=i,n=len(words),word=w,category=category,opening=opening,
            split='test' if int(hashlib.sha256(('voynich-layout-v1:'+re.match(r'f(\d+)',page)[1]).encode()).hexdigest(),16)%5==0 else 'train',
            initial=w[0],first_gallows=firstgal,
            paired_structure=flags.get(('F' if tr=='H' else 'H',loc))==opening))
save('PROSE-EVENTS.json',events)

cats=['paragraph_first','continuation_first','opening_line_other','continuation_other']
def count(es):
    n=len(es);d={'opportunities':n}
    for c in ['f','p','r','k','t']:
        a=sum(x['initial']==c for x in es);b=sum(c in x['word'] for x in es)
        d[c]={'initial':a,'initial_rate':a/n if n else None,'anywhere_tokens':b,'anywhere_rate':b/n if n else None,
              'first_gallows':sum(x['first_gallows']==c for x in es)}
    d['fp_initial']=d['f']['initial']+d['p']['initial']
    d['p_share_initial_fp']=d['p']['initial']/d['fp_initial'] if d['fp_initial'] else None
    d['cfh_tokens']=sum('cfh' in x['word'] for x in es)
    d['cph_tokens']=sum('cph' in x['word'] for x in es)
    return d

summaries={}
for mode in ['main','all_lengths','shared_structure']:
    es=[x for x in events if (mode=='all_lengths' or x['n']>=2) and (mode!='shared_structure' or x['paired_structure'])]
    summaries[mode]={tr:{c:count([x for x in es if x['tr']==tr and x['category']==c]) for c in cats} for tr in ['H','F']}
save('PROSE-COUNTS.json',summaries)
strata=[]
for key in sorted({(x['tr'],x['hand'],x['language'],x['section'],x['split']) for x in events}):
    es=[x for x in events if (x['tr'],x['hand'],x['language'],x['section'],x['split'])==key and x['n']>=2]
    strata.append({'stratum':key,'categories':{c:count([x for x in es if x['category']==c]) for c in cats}})
save('STRATIFIED-COUNTS.json',strata)

# Same exact remaining word body, hand, Currier variety, section, and allocation.
# Each cell keeps the full 2x2 table, including single-form/zero cells.
matched=[];pool=[]
contrasts=[('paragraph_first','continuation_first'),('paragraph_first','opening_line_other'),('continuation_first','continuation_other')]
for tr in ['H','F']:
    for a,b in contrasts:
        cells=collections.defaultdict(lambda:collections.Counter())
        for x in events:
            if x['tr']!=tr or x['n']<2 or x['initial'] not in ['f','p'] or x['category'] not in [a,b]:continue
            k=(x['word'][1:],x['hand'],x['language'],x['section'],x['split'])
            cells[k][(x['category'],x['initial'])]+=1
        num=den=0.;eligible=0;direction=collections.Counter();counts=collections.Counter()
        for key,c in sorted(cells.items()):
            ap,af,bp,bf=[c[(pos,ch)] for pos,ch in [(a,'p'),(a,'f'),(b,'p'),(b,'f')]]
            supported=(ap+af)>0 and (bp+bf)>0 and (ap+bp)>0 and (af+bf)>0
            matched.append({'tr':tr,'contrast':[a,b],'stratum_body':key,'counts':{'a_p':ap,'a_f':af,'b_p':bp,'b_f':bf},'informative':supported})
            if supported:
                n=ap+af+bp+bf;num+=ap*bf/n;den+=af*bp/n;eligible+=1
                direction['p_more_at_a' if ap*bf>af*bp else 'p_less_at_a' if ap*bf<af*bp else 'equal']+=1
                counts.update({'a_p':ap,'a_f':af,'b_p':bp,'b_f':bf})
        pool.append({'tr':tr,'contrast':[a,b],'informative_cells':eligible,'direction':dict(direction),'pooled_informative_counts':dict(counts),'MH_odds_p_vs_f_at_a':num/den if den else 'infinite' if num else None,'MH_numerator':num,'MH_denominator':den,'status':'Descriptive retrospective conditional association; no significance test, no heldout performance claim.'})
save('MATCHED-FP-CELLS.json',matched);save('MATCHED-FP-SUMMARY.json',pool)

pr=load(LAY/'predictions-initial.json')
rep={}
for name,pred in [('line_first',[x for x in pr if x['edge_start']]),('other',[x for x in pr if not x['edge_start']])]:
    rep[name]={'p':sum(x['word'].startswith('p') for x in pred),'total':len(pred)}
save('PR-DENOMINATOR-AUDIT.json',rep)
lookup={(x['tr'],x['loc'],x['index']):x for x in events}
rep['structural_decomposition']=dict(collections.Counter(
    (lookup.get(('H',x['loc'],x['pos']),{}).get('category','excluded')+'_'+x['word'][0])
    for x in pr))
save('PR-DENOMINATOR-AUDIT.json',rep)

g=load(OLD/'voynich-alignment-v37/geometry.json'); slots=load(OLD/'voynich-matched-family-v26/f57v-slots.json')
# Manual broad ink neighborhoods from R2 native-resolution strip; no equal spacing.
intervals=[[510,590],[1780,1865],[3000,3075],[4050,4135]]
geometry=[]
for i,(lo,hi) in enumerate(intervals):
    anchor=g['anchors'][i];mid=(lo+hi)/2
    geometry.append({'cycle':i+1,'slot':9,'reading':{tr:slots[tr]['cycles'][i][8] for tr in ['H','U','V']},
        'previous_two':{tr:slots[tr]['cycles'][i][6:8] for tr in ['H','U','V']},
        'following':{tr:slots[tr]['cycles'][i][9] for tr in ['H','U','V']},
        'x_interval_manual': [lo,hi],'manual_extra_uncertainty_px':20,
        'angle_clockwise_north_nominal':(g['start_angle']+mid*360/4800)%360,
        'degrees_after_own_o_ray_nominal':(mid-anchor['unwrapped_x'])*360/4800,
        'eight_transcription_units_after_o':True,'independent_R2_divider':None,
        'local_visual_assessment':'No local radial divider or spoke crossing visible before/through slot9. Neighboring signs occupy same uninterrupted annular band.',
        'precision':'Approximate visual neighborhoods, not independent expert annotation; ray locations were defined from o glyphs.'})
save('R2-SLOT9-GEOMETRY.json',geometry)
im=Image.open(OLD/'voynich-alignment-v37/unwrap.png').convert('RGB');out=Image.new('RGB',(1350,4*245),'#f8f5ed');d=ImageDraw.Draw(out)
for i,row in enumerate(geometry):
    left=max(0,int(g['anchors'][i]['unwrapped_x'])-55);right=min(4800,left+1250)
    crop=im.crop((left,120,right,335));out.paste(crop,(80,i*245+25))
    dr=ImageDraw.Draw(out)
    lo,hi=row['x_interval_manual'];dr.rectangle((80+lo-left,i*245+55,80+hi-left,i*245+205),outline='#ba2632',width=3)
    ax=80+g['anchors'][i]['unwrapped_x']-left;dr.line((ax,i*245+25,ax,i*245+240),fill='#196377',width=2)
    dr.text((8,i*245+7),f"Cycle {i+1}: {row['reading']['H']} | blue: o ray; red: slot9 neighborhood",fill='#222222')
out.save(R/'R2-slot9-comparison.png')
atlas=load(P/'frequency-atlas-v48/rows.json')
atlas_by_loc={(x[0],x[6]):x[7] for x in atlas if x[5]=='P'}
verification={'input_hashes_unchanged':all(sha(Path(p))==h for p,h in before.items()),
    'slot9_HUV_agree':all(len(set(x['reading'].values()))==1 for x in geometry),
    'four_readings':[x['reading']['H'] for x in geometry],
    'v39_registered_rings':sorted({x['ring'] for x in load(OLD/'voynich-registration-v39/FULL-REGISTRATION.json')['records']}),
    'v31_R2_record':[x for x in load(OLD/'voynich-alignment-v31/boundaries.json')['bands'] if x['id']=='f57v.R2'],
    'pr_saved_prediction_denominators':rep,'prose_exclusions':dict(excluded),
    'original_slots_preserved':all(atlas_by_loc[(x['tr'],x['loc'])][x['index']]==x['word'] for x in events),
    'no_unknown_slot_promoted':all(not any(y['category'].endswith('first') for y in events if y['tr']==tr and y['loc']==loc) for (tr,loc),ws in atlas_by_loc.items() if ws and ws[0] is None),
    'rate_denominators':'Readable original slots; first words compared with readable first words. Main excludes <2-slot lines.',
    'limits':'Descriptive cohort audit; alternate transcriptions dependent; no new independent dividers; no heldout transfer test.'}
save('VERIFICATION.json',verification)
print(json.dumps({'counts':summaries['main'],'matched':pool,'geometry':geometry,'verification':verification},indent=2))
