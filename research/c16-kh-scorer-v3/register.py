from preserve import R,V2,V1,sha,dump
from pathlib import Path
from collections import defaultdict,Counter
import json,csv,hashlib,random,shutil,sys,math
def order(tag,x):return hashlib.sha256(('KH-v3-fresh-20261026:'+tag+':'+str(x)).encode()).hexdigest()
def rng(tag):return random.Random(int(order('rng',tag)[:16],16))
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def noise(text,rates,alphabet,rd):
    symbols=sorted(set(alphabet)|{' '});out=[];ops=Counter();s,i,d=(rates[k] for k in ['substitution','insertion','deletion'])
    for c in text:
        x=rd.random()
        if x<s:out.append(rd.choice([a for a in symbols if a!=c]));ops['substitution']+=1
        elif x<s+d:ops['deletion']+=1
        elif x<s+d+i:out.extend([rd.choice(symbols),c]);ops['insertion']+=1
        else:out.append(c)
    return ' '.join(''.join(out).split()),dict(ops)
def main():
    assert not (R/'REGISTRATION.json').exists(),'Write-once freeze'
    inputs=R/'inputs';v2=json.loads((inputs/'v2-banks.json').read_text());banks={};fresh={}
    for arm in ['tanakh','medieval']:
        data=json.loads((inputs/f'{arm}.json').read_text());excluded={i for d in v2['hebrew'][arm] for i in d['test_segment_ids']};oldstrings={tuple(r['text_eva'].split()) for d in v2['hebrew'][arm] for r in d['rows']};train={tuple(s) for s in data['train']};seen=set();eligible=[]
        for i,s in enumerate(data['test']):
            if i in excluded or len(s)<4:continue
            n=min(32,len(s));offset=rng(f'{arm}:parent:{i}').randrange(len(s)-n+1);ws=s[offset:offset+n];t=tuple(ws)
            if t in train or t in oldstrings or t in seen:continue
            seen.add(t);eligible.append(dict(parent=i,offset=offset,end=offset+n,words=ws,parent_words=len(s)))
        eligible.sort(key=lambda x:order(arm,x['parent']));assert len(eligible)>=640
        selected=eligible[:640];docs=[]
        for di in range(80):
            part=selected[di*8:(di+1)*8];doc=f'V3-{arm}-{di:03d}'
            docs.append(dict(family='Hebrew',arm=arm,bank='calibration' if di<40 else 'confirmation',document=doc,rows=[dict(line_id=f'{doc}.{j}',text_eva=' '.join(p['words'])) for j,p in enumerate(part)],parents=[{k:v for k,v in p.items() if k!='words'} for p in part]))
        assert not ({p['parent'] for p in selected}&excluded)
        banks[arm]=docs;fresh[arm]=dict(eligible_unused_parents=len(eligible),selected=640,v2_parent_overlap=0,exact_v2_string_overlap=0,exact_training_segment_overlap=0,duplicate_windows=0,train_sha256=hashlib.sha256(json.dumps(data['train'],ensure_ascii=True).encode()).hexdigest())
    shutil.copyfile(V2/'inputs/C1-clean.csv',inputs/'C1-clean.csv')
    shutil.copyfile(R.parent/'voynich-lab/src/encoders/__init__.py',inputs/'c9_generator.py')
    noise_path=R.parent/'voynich-lab/report/noise_model.json';prior=json.loads((V1/'prepared/prior-files.json').read_text());assert sha(noise_path)==prior['voynich-lab\\report\\noise_model.json']
    shutil.copyfile(noise_path,inputs/'noise_model.json');sys.path.insert(0,str(inputs));from c9_generator import grille
    rates=json.loads((inputs/'noise_model.json').read_text())['rates'];oldC1={d['document'] for d in v2['nulls'] if d['family']=='C1'};by=defaultdict(list)
    for r in read(inputs/'C1-clean.csv'):
        if r['text_eva'].strip():by[r['folio']].append(r)
    ids=sorted((p for p,rs in by.items() if len(rs)>=8 and p not in oldC1),key=lambda p:order('C1',p));assert len(ids)>=40
    external=[]
    for i,p in enumerate(ids[:40]):
        rows=[dict(line_id=r['line_id'],text_eva=r['text_eva']) for r in by[p][:8]];alphabet=set(''.join(r['text_eva'].replace(' ','') for r in rows));rd=rng(f'C1-noise:{p}');noisy=[];ops=Counter()
        for r in rows:s,o=noise(r['text_eva'],rates,alphabet,rd);ops.update(o);noisy.append(dict(r,text_eva=s))
        external.append(dict(family='C1',document=p,bank='calibration' if i<20 else 'confirmation',clean=rows,noise=noisy,provenance='v2-unselected pages; v1 aggregate exposure',v2_document_overlap=False,noise_operations=dict(ops)))
    for arm,docs in banks.items():
        chosen=[d for d in docs if d['bank']=='calibration'][:20]+[d for d in docs if d['bank']=='confirmation'][:20]
        for i,d in enumerate(chosen):
            n=sum(len(r['text_eva'].split()) for r in d['rows']);words,meta=grille(n,rng(f'C9:{arm}:{i}'),dict(grille_stride=7));native=sorted(set(''.join(words)));mapping=dict(zip(native,'abcdefghijklmnopqrstuvxyz'));words=[''.join(mapping[c] for c in w) for w in words];rows=[];pos=0
            for j,r in enumerate(d['rows']):k=len(r['text_eva'].split());rows.append(dict(line_id=f'C9-{arm}-{i}.{j}',text_eva=' '.join(words[pos:pos+k])));pos+=k
            rd=rng(f'C9-noise:{arm}:{i}');noisy=[];ops=Counter();alphabet=set(mapping.values())
            for r in rows:s,o=noise(r['text_eva'],rates,alphabet,rd);ops.update(o);noisy.append(dict(r,text_eva=s))
            external.append(dict(family='C9',arm=arm,document=f'C9-{arm}-{i}',bank=d['bank'],clean=rows,noise=noisy,provenance='fresh generator draw; fixed schematic grille',generation=meta,symbol_mapping=mapping,noise_operations=dict(ops)))
    dump(inputs/'banks.json',dict(hebrew=banks,external=external,freshness=fresh,C17=dict(status='UNAVAILABLE',fresh_writers=0,old_writers=38,user_confirmed_no_new_source=True),ZL='CLOSED',actual_C11='CLOSED'))
    assert all((R/n).exists() for n in ['corrected.py','qualify.py','finalize.py','PROTOCOL.md'])
    files={p.relative_to(R).as_posix():sha(p) for p in list(inputs.glob('*'))+list(R.glob('*.py'))+[R/'PROTOCOL.md'] if p.is_file()}
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_V3_SCORES',candidate='EOS-prefix-counter-only-v3',files=files,scorer_search_decoder_separate=True,external_C17='UNAVAILABLE',ZL='CLOSED',actual_C11='CLOSED',variants=24,retune=False,freshness=fresh))
    print(json.dumps(dict(registered=True,freshness=fresh,external_C17='UNAVAILABLE',external_documents=len(external)),indent=2))
if __name__=='__main__':main()
