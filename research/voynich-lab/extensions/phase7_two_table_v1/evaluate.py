from common import *
def overlap(a,b):
    va,vb=set(a['vocab']),set(b['vocab']);shared=va&vb
    return dict(A_types=len(va),B_types=len(vb),shared_types=len(shared),type_Jaccard=len(shared)/len(va|vb) if va|vb else None,A_token_coverage_by_B=sum(v for k,v in a['vocab'].items() if k in vb)/a['words'],B_token_coverage_by_A=sum(v for k,v in b['vocab'].items() if k in va)/b['words'])
def main():
    verify_registration();freeze=json.loads((R/'TABLES_FROZEN.json').read_text());assert freeze['registration_sha256']==sha(R/'REGISTRATION.json');assert all(sha(R/p)==h for p,h in freeze['files'].items())
    assert not (R/'HELD_OUT_EVALUATED.json').exists(),'Held-out evaluation already complete'
    # Only now open the target content outside training pages.
    target=typed(read(LAB/'data/voynich/ZL_running.csv'));sp=split();meta=metadata();assert [x['line_id'] for x in meta]==[x['line_id'] for x in target]
    for x,y in zip(meta,target):assert x['word_slots']==len(y['text_eva'].split())
    chosen=freeze['chosen'];datasets={};receipts=[]
    for family in ['C1','C2','C9']:
        for seed in SEEDS:
            cache={c['id']:generated(family,c,seed) for c in chosen[family].values()};byid={key:{r['line_id']:r for r in value[0]} for key,value in cache.items()}
            for arm in ['two','single']:
                name=family+'_'+arm;rows=[]
                for x in meta:
                    label=x['currier_lang'] if arm=='two' and x['currier_lang'] in ['A','B'] else 'pooled';setting=chosen[family][label]['id'];row=byid[setting][x['line_id']];rows.append({**row,'corpus':'P7_'+name,'metadata_origin':'borrowed_ZL_layout_and_page_labels'})
                assert all(len(r['text_eva'].split())==x['word_slots'] for r,x in zip(rows,meta));table(R/'data'/name/f's{seed}.csv',rows);datasets[name,seed]=rows
                for page in dict.fromkeys(x['folio'] for x in meta):
                    x=next(r for r in meta if r['folio']==page);label=x['currier_lang'] if arm=='two' and x['currier_lang'] in ['A','B'] else 'pooled';cid=chosen[family][label]['id'];receipt=next(r for r in cache[cid][1] if r['page']==page);receipts.append(dict(arm=name,**receipt))
    table(R/'ENCODING_RECEIPTS.csv',receipts);out=[];over=[];details={};targets={};differences=[]
    for part in ['train','validation','test']:
        for label in ['A','B','pooled']:targets[part,label]=fingerprint(choose_rows([r for r in target if sp[r['folio']]==part],label))
    frozen_train=json.loads((R/'TRAINING_TARGET_FINGERPRINTS.json').read_text())
    assert all(targets['train',label]['h2']==frozen_train[label]['h2'] for label in ['A','B','pooled'])
    for (name,seed),rows in [(('ZL',1729),target)]+list(datasets.items()):
        for part in ['train','validation','test']:
            fps={}
            for label in ['A','B','pooled']:
                fp=fingerprint(choose_rows([r for r in rows if sp[r['folio']]==part],label));fps[label]=fp;t=targets[part,label]
                details[f'{name}:s{seed}:{part}:{label}']=fp
                out.append(dict(corpus=name,seed=seed,split=part,subset=label,**{k:v for k,v in fp.items() if k not in ['hist','vocab']},word_length_mean=sum(int(k)*v for k,v in fp['hist'].items())/fp['words'],h2_distance=abs(fp['h2']-t['h2']),word_length_W1=w1(fp['hist'],t['hist']),identical_difference=fp['identical']-t['identical'],edit1_difference=fp['edit1']-t['edit1']))
            over.append(dict(corpus=name,seed=seed,split=part,**overlap(fps['A'],fps['B'])))
            differences.append(dict(corpus=name,seed=seed,split=part,h2_A_minus_B=fps['A']['h2']-fps['B']['h2'],word_length_W1_A_B=w1(fps['A']['hist'],fps['B']['hist']),identical_A_minus_B=fps['A']['identical']-fps['B']['identical'],edit1_A_minus_B=fps['A']['edit1']-fps['B']['edit1']))
        print('evaluated frozen encoder',name,seed,flush=True)
    table(R/'fingerprints.csv',out);table(R/'vocabulary_overlap.csv',over);table(R/'A_B_differences.csv',differences);dump(R/'fingerprint_details.json',details)
    dump(R/'HELD_OUT_EVALUATED.json',dict(status='COMPLETE',tables_freeze_sha256=sha(R/'TABLES_FROZEN.json'),target_hash=sha(LAB/'data/voynich/ZL_running.csv'),generated_corpora=6,encoder_seeds=SEEDS,files={str(p.relative_to(R)):sha(p) for p in list((R/'data').rglob('*.csv'))+[R/'fingerprints.csv',R/'vocabulary_overlap.csv',R/'A_B_differences.csv',R/'fingerprint_details.json',R/'ENCODING_RECEIPTS.csv']}))
    print('Held-out fingerprint evaluation COMPLETE; table settings unchanged.')
if __name__=='__main__':main()
