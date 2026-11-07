"""Select controls and freeze every candidate/input byte BEFORE any scoring."""
from pathlib import Path
from collections import defaultdict
import csv,json,hashlib,shutil,random,math
from preserve import R,OLD,sha
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
def order(tag,identifier):return hashlib.sha256(('KH-v2-qualification-20261026:'+tag+':'+str(identifier)).encode()).hexdigest()
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    assert not (R/'REGISTRATION.json').exists(),'Registration is write-once'
    banks={};selection={}
    for arm in ['tanakh','medieval']:
        data=json.loads((R/'inputs'/f'{arm}.json').read_text());training={tuple(s) for s in data['train']};seen=set();eligible=[]
        for i,s in enumerate(data['test']):
            ss=tuple(s)
            if 4<=len(s)<=32 and ss not in training and ss not in seen:eligible.append((i,s));seen.add(ss)
        eligible.sort(key=lambda x:order(arm,x[0]));assert len(eligible)>=640
        selected=eligible[:640];docs=[]
        for di in range(80):
            bank='calibration' if di<40 else 'confirmation';part=selected[di*8:(di+1)*8];doc=f'HEB-{di:03d}'
            rows=[dict(line_id=f'{doc}.{i}',text_eva=' '.join(ws)) for i,ws in part]
            docs.append(dict(family='Hebrew',arm=arm,bank=bank,document=doc,rows=rows,test_segment_ids=[i for i,ws in part],size_mismatch=False))
        banks[arm]=docs;selection[arm]=dict(eligible=len(eligible),selected_test_ids=[i for i,s in selected],exact_training_overlap=0,exact_selected_duplicates=0)
    nulls=[]
    for family in ['C1','C9','C17']:
        for version in ['clean','noise']:
            shutil.copyfile(OLD/'prepared'/f'{family}-{version}.csv',R/'inputs'/f'{family}-{version}.csv')
        clean=read(R/'inputs'/f'{family}-clean.csv');noisy={r['line_id']:r for r in read(R/'inputs'/f'{family}-noise.csv')};bydoc=defaultdict(list)
        for row in clean:
            if row['text_eva'].strip():bydoc[row['folio']].append(row)
        ids=[d for d,rows in bydoc.items() if family=='C17' or len(rows)>=8];ids.sort(key=lambda d:order(family,d))
        if family!='C17':assert len(ids)>=40;ids=ids[:40]
        else:assert len(ids)==38
        split=len(ids)//2
        for i,doc in enumerate(ids):
            rows=bydoc[doc] if family=='C17' else bydoc[doc][:8]
            cleanrows=[dict(line_id=r['line_id'],text_eva=r['text_eva']) for r in rows]
            noiserows=[dict(line_id=r['line_id'],text_eva=noisy[r['line_id']]['text_eva']) for r in rows]
            nulls.append(dict(family=family,document=doc,bank='calibration' if i<split else 'confirmation',clean=cleanrows,noise=noiserows,size_mismatch=family=='C17',word_namespace='writer-local' if family=='C17' else 'source-global'))
    dump(R/'inputs/banks.json',dict(hebrew=banks,nulls=nulls,selection=selection))
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_QUALIFICATION',candidate='single-UNKNOWN-normalized-context-wordslot-rank-v2',files={p.relative_to(R).as_posix():sha(p) for p in list((R/'inputs').glob('*'))+list(R.glob('*.py'))+[R/'PROTOCOL.md'] if p.is_file()},sources_allowed=['Hebrew','C1','C9','C17'],ZL='CLOSED',actual_C11='CLOSED',variants=24,retune=False,search_restarts=0))
    print(json.dumps(dict(hebrew_documents={a:len(v) for a,v in banks.items()},null_documents=len(nulls),C17_writers=38,registered=True)))
if __name__=='__main__':main()
