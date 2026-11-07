from pathlib import Path
import json, hashlib, unicodedata, re, csv

R=Path(__file__).resolve().parent
E=R.parent
OLD=E/'phase9_month_annotations_v1'
TARGET=OLD/'targets/later_month_annotations_v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,obj):
    p=R/name
    if p.exists(): raise RuntimeError('WRITE_ONCE: '+name)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def letters(text):
    text=unicodedata.normalize('NFD',text)
    text=''.join(c for c in text if unicodedata.category(c)!='Mn')
    for a,b in {'æ':'ae','Æ':'ae','œ':'oe','Œ':'oe','ð':'d','Ð':'d','þ':'th','Þ':'th','ł':'l','Ł':'l','ß':'ss','ø':'o','Ø':'o','ſ':'s'}.items(): text=text.replace(a,b)
    text=''.join(c for c in text if c.isalpha()).lower()
    assert all('a'<=c<='z' for c in text)
    return text
def pos(i,n): return 'B' if i==0 else 'E' if i==n-1 else 'M'

# Bounded source transcription ledger. Alternatives are retained, never selected.
Z='https://www.voynich.nu/writing.html'
N='https://philipneal.net/voynichsources/marginalia/'
rows=[
 ('f1v_green','f1v','second left green leaf',['g'],'single-letter colour suggestion'),
 ('f1v_yellow','f1v','lowest yellow leaf right of stem',['J'],'uncertain ink and letter'),
 ('f2v_note','f2v','above second paragraph',['fo','fa'],'disputed reading; possible folio marker'),
 ('f4r_stem','f4r','lower stem',['rot'],'published colour-note reading'),
 ('f4r_flower','f4r','right flower',['F'],'isolated capital'),
 ('f7r_root','f7r','left half of root',['rot'],'probable reading under paint'),
 ('f9v_top','f9v','top petal of top-left flower',['por'],'tentative reading'),
 ('f9v_left','f9v','lower-left petal',['p'],'tentative isolated letter'),
 ('f9v_right','f9v','lower-right petal',['r'],'tentative isolated letter'),
 ('f9v_g','f9v','right of top-right flower',['g'],'isolated colour-note suggestion'),
 ('f20r_root','f20r','top of root',['p','r'],'disputed letter'),
 ('f29r_root','f29r','upper root',['r'],'isolated colour-note suggestion'),
 ('f32r_p','f32r','bottom-right flower, first mark',['p'],'fragment; possible following character untranscribed'),
 ('f32r_other','f32r','bottom-right flower, other mark',['v','r'],'disputed isolated mark; no concatenation'),
 ('f39v_B','f39v','bottom-right leaf white space',['B'],'isolated capital'),
 ('f99v_root','f99v','fourth root of third row',['p','r'],'disputed letter'),
 ('f66r_Z','f66r','lower marginal Latin-letter fragment',['der Mussdel','Musmel'],'competing published readings; neither generally accepted'),
]
items=[dict(id=i,folio=f,locator=l,readings=rs,uncertainty=u,source=Z) for i,f,l,rs,u in rows]
items += [
 dict(id='f66r_N',folio='f66r',locator='lower marginal Latin-letter fragment',readings=['der mvs del'],uncertainty='another reading of SAME locus as f66r_Z; not independent',source=N),
 dict(id='f116v_N',folio='f116v',locator='short Roman-letter marginal fragment',readings=['pox leber'],uncertainty='published reading, not adjudicated gold; rest of mixed-script page excluded',source=N)
]
assert len({x['id'] for x in items})==len(items)
used={x['folio'] for x in read(TARGET/'TARGET_INPUT.json')['items']}
assert not used.intersection(x['folio'] for x in items)
models=[m for m in read(TARGET/'OBSERVED.json')['models'] if m['language']=='Occitan' and m['family'] in ['mono','position']]
assert len(models)==2
before={str(p.relative_to(E)):sha(p) for folder in [OLD,E/'phase8_alignment_v1'] for p in folder.rglob('*') if p.is_file()}
put('PRESERVATION_BEFORE.json',before)
put('INPUT.json',dict(items=items,excluded_fit_folios=sorted(used),source_access='Zandbergen live page; Neal search-result extract, direct page timed out twice',native_tracks='CLOSED',gold_plaintext=None))
put('FROZEN_MAPS.json',models)
put('REGISTRATION.json',dict(files={n:sha(R/n) for n in ['PROTOCOL.md','check.py','INPUT.json','FROZEN_MAPS.json','PRESERVATION_BEFORE.json']},old_witness_sha256=sha(TARGET/'OBSERVED.json'),status='SEALED_BEFORE_MAP_APPLICATION',new_fits=0))

outputs=[]
for item in items:
 for reading in item['readings']:
  words=[letters(w) for w in reading.split()]
  assert words and all(words)
  for model in models:
   inv={(g,c):p for g,p,c in model['mapping']}
   assert len(inv)==len(model['mapping'])
   decoded=[]; token_records=[]
   for word in words:
    out=''.join(inv.get(('A' if model['family']=='mono' else pos(i,len(word)),c),'?') for i,c in enumerate(word))
    decoded.append(out)
    token_records.append(dict(input=word,output=out,known=len(out)-out.count('?'),total=len(out)))
   outputs.append(dict(id=item['id'],folio=item['folio'],reading=reading,family=model['family'],output=' '.join(decoded),known=sum(x['known'] for x in token_records),total=sum(x['total'] for x in token_records),tokens=token_records))
put('RESULTS.json',outputs)
with (R/'RESULTS.csv').open('x',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['id','folio','reading','family','output','known','total']);w.writeheader();w.writerows({k:v for k,v in o.items() if k!='tokens'} for o in outputs)

# Separate verification traverses the SAVED forward assignments without inverses.
checks=0
for o in outputs:
 m=next(m for m in models if m['family']==o['family'])
 for t in o['tokens']:
  for i,(c,result) in enumerate(zip(t['input'],t['output'])):
   group='A' if o['family']=='mono' else ('B' if i==0 else ('E' if i+1==len(t['input']) else 'M'))
   matches=[p for g,p,enc in m['mapping'] if g==group and enc==c]
   assert result==(matches[0] if matches else '?')
   checks+=1
reg=read(R/'REGISTRATION.json')
assert all(sha(R/n)==h for n,h in reg['files'].items())
drift=[p for p,h in before.items() if not (E/p).is_file() or sha(E/p)!=h]
assert not drift
summary={}
for family in ['mono','position']:
 ts=[t for o in outputs if o['family']==family for t in o['tokens']]
 summary[family]=dict(reading_alternative_rows=sum(o['family']==family for o in outputs),token_occurrences_including_alternatives=len(ts),fully_mapped=sum(t['known']==t['total'] for t in ts),fully_mapped_multi_letter=sum(t['known']==t['total'] and t['total']>1 for t in ts),partly_mapped=sum(0<t['known']<t['total'] for t in ts),unmapped=sum(t['known']==0 for t in ts))
put('VERIFICATION.json',dict(status='PASS',letter_checks=checks,old_files_checked=len(before),old_file_drift=drift,registration_unchanged=True,summary=summary,new_fits=0,native_tracks='CLOSED',translation_accuracy='NOT_ESTIMABLE',phase8_status=read(E/'phase8_alignment_v1/QUALIFICATION.json')['status'],receipt_defect=read(OLD/'RECEIPT_DEVIATION.json')['status']))
print(json.dumps(summary,indent=2))
for o in outputs:
 if any(t['total']>1 for t in o['tokens']): print(o['folio'],o['reading'],o['family'],o['output'],str(o['known'])+'/'+str(o['total']))
