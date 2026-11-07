from common import *
from collections import Counter
import math,random
from src.phase3 import load_words,layout,relabel,rng_for
from src.encoders import encode,expansive,SIGLA
from src.noise import inject
def encode_partial(words,cfg,s):
    rd=rng_for(1729,'C5' if s['mode']=='C5_external' else 'C12');base,meta=encode(words,'C5',rd,cfg);signs=sorted(set(''.join(base)));counts=Counter(''.join(base));ranked=sorted(signs,key=lambda c:hashlib.sha256(('C12-partial-type-order-1729:'+c).encode()).hexdigest())
    if s['mode']=='sigla_only':selected=sorted(set(SIGLA)&set(signs))
    elif s['fraction']==0:selected=[]
    else:selected=sorted(ranked[:math.floor(s['fraction']*len(signs))])
    code={c:c for c in signs};m=len(selected);l=s['sequence_length'];shared=set();permutations={}
    if m:
        strokes=selected[:];rd.shuffle(strokes)
        slots=list(range(l));rd.shuffle(slots);shared=set(slots[:int(s['slot_rigidity']*(l-1))])
        for slot in range(l):
            if slot not in shared:order=list(range(m));rd.shuffle(order);permutations[slot]=order
        for i,c in enumerate(selected):code[c]=''.join(strokes[0] if slot in shared else strokes[permutations[slot][i]] for slot in range(l))
    result=[''.join(code[c] for c in w) for w in base];expanded=sum(counts[c] for c in selected);chars=sum(map(len,base))
    assert len(set(code.values()))==len(signs)
    assert all(not b.startswith(a) for x,a in code.items() for y,b in code.items() if x!=y)
    inv={v:k for k,v in code.items()};stroke=set(selected)
    for before,after in zip(base,result):
        rebuilt=[];i=0
        while i<len(after):
            width=l if after[i] in stroke else 1;rebuilt.append(inv[after[i:i+width]]);i+=width
        assert ''.join(rebuilt)==before
    assert sum(map(len,result))==chars+(l-1)*expanded
    cardinalities=[len({code[c][slot] for c in selected}) for slot in range(l)] if m else []
    if m:assert all(n==(1 if slot in shared else m) for slot,n in enumerate(cardinalities))
    if s['mode']=='full':
        original,_=expansive(words,rng_for(1729,'C12'),cfg,l,s['slot_rigidity']);assert original==result
    return result,dict(base_metadata=meta,codebook=code,sign_order=ranked,selected=selected,source_types=len(signs),selected_types=m,type_fraction=m/len(signs),base_characters=chars,expanded_occurrences=expanded,occurrence_fraction=expanded/chars,shared_slots=sorted(shared),slot_cardinalities=cardinalities,permutations=permutations,engineering_checks='PASS',roundtrip_words=len(base))
def main():
    assert not (R/'REGISTRATION.json').exists();assert not (R/'DATA_READY.json').exists()
    cfg=json.loads((I/'configs/phase3.json').read_text());cfg['encoder_aggressiveness']=.65;words,_=load_words(cfg['source_slices']['C1'],34509);template=typed(read(R/'reference/C1-layout.csv'));rates=json.loads((R/'reference/noise_model.json').read_text())['rates'];manifest=[];endpoints=[]
    for s in final_settings():
        cfg['encoder_aggressiveness']=s['aggressiveness'];out,meta=encode_partial(words,cfg,s);rows=layout(out,template,'C12_partial');rows,mapping=relabel(rows);alphabet=set(''.join(r['text_eva'].replace(' ','') for r in rows));rd=rng_for(1729,('C5' if s['mode']=='C5_external' else 'C12')+':noise');noisy=[];ops=Counter()
        for r in rows:
            text,o,raw=inject(r['text_eva'],rates,alphabet,rd);ops.update(o);noisy.append(dict(r,text_eva=text))
        folder=R/'data'/s['setting'];dump(folder/'encoder.json',dict(setting=s,metadata=meta,relabel_mapping=mapping,noise_operations=dict(ops)))
        for version,rs in [('clean',rows),('noise',noisy)]:
            assert version!='clean' or sum(len(r['text_eva'].split()) for r in rs)==34509
            table(folder/f'{version}.csv',rs);words_n=sum(len(r['text_eva'].split()) for r in rs);chars=sum(len(r['text_eva'].replace(' ','')) for r in rs)
            if s['old_reference']:
                old=typed(read(R/'reference'/s['old_reference']/f'{version}.csv'))
                for a,b in zip(rs,old):assert all(a[k]==b[k] for k in ['text_eva','line_id','folio','is_para_start'])
                assert len(rs)==len(old);endpoints.append(dict(setting=s['setting'],reference=s['old_reference'],version=version,rows=len(rs),status='PASS'))
            manifest.append(dict(**s,version=version,words=words_n,characters=chars,alphabet_size=len(set(''.join(r['text_eva'].replace(' ','') for r in rs))),source_types=meta['source_types'],selected_types=meta['selected_types'],type_fraction=meta['type_fraction'],occurrence_fraction=meta['occurrence_fraction'],character_expansion=chars/meta['base_characters'],data_sha256=sha(folder/f'{version}.csv')))
        print('generated',s['setting'],s['mode'],flush=True)
    for s in settings():
        if s['role']=='terminal':continue
        for version in ['clean','noise']:
            path=R/'data'/s['setting']/f'{version}.csv';rs=typed(read(path))
            manifest.append({**s,'version':version,'words':sum(len(r['text_eva'].split()) for r in rs),'characters':sum(len(r['text_eva'].replace(' ','')) for r in rs),'data_sha256':sha(path)})
    table(R/'DATA_MANIFEST.csv',manifest);dump(R/'ENGINEERING.json',dict(status='PASS',settings=len(final_settings()),terminal_version_cells=32,total_measured_cells=len(manifest),imported_frozen_cells=40,endpoints=endpoints,roundtrip_words_checked=34509*len(final_settings()),terminal_prefix_free=True,terminal_slot_cardinality_checks=True,terminal_accounting=True,legacy_codebook_not_repaired=True))
    dump(R/'DATA_READY.json',dict(status='ENGINEERING_PASS_BEFORE_METRICS',files={str(p.relative_to(R)):sha(p) for p in (R/'data').rglob('*') if p.is_file()},metrics_computed=False,neural_jobs_started=0))
    print(json.dumps(dict(settings=len(settings()),version_cells=len(manifest),endpoint_checks=len(endpoints))))
if __name__=='__main__':main()
