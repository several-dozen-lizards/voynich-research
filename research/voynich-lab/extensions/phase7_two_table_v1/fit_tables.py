from common import *
def main():
    verify_registration();assert not (R/'TABLES_FROZEN.json').exists()
    train=target_train();target={label:fingerprint(choose_rows(train,label)) for label in ['A','B','pooled']};dump(R/'TRAINING_TARGET_FINGERPRINTS.json',target);all_losses=[];chosen={};scales={}
    for family in ['C1','C2','C9']:
        candidates_=candidates() if family!='C9' else json.loads((R/'C9_CANDIDATES.json').read_text());values=[]
        for candidate in candidates_:
            file=R/'fit_cache'/family/(candidate['id']+'.json')
            if file.exists():current=json.loads(file.read_text())
            else:
                seedmetrics=[]
                for seed in SEEDS:
                    rows,_=generated(family,candidate,seed,only_train=True);assert all(split()[r['folio']]=='train' for r in rows)
                    for label in ['A','B','pooled']:
                        fp=fingerprint(choose_rows(rows,label));seedmetrics.append(dict(seed=seed,label=label,h2=fp['h2'],W1=w1(fp['hist'],target[label]['hist']),identical=fp['identical'],edit1=fp['edit1']))
                current=dict(candidate=candidate,seedmetrics=seedmetrics);dump(file,current)
            values.append(current)
            print('fit training only',family,candidate['id'],flush=True)
        chosen[family]={};scales[family]={}
        for label in ['A','B','pooled']:
            avgs=[]
            for value in values:
                ms=[m for m in value['seedmetrics'] if m['label']==label];avgs.append(dict(candidate=value['candidate'],**{k:statistics.mean(m[k] for m in ms) for k in ['h2','W1','identical','edit1']}))
            scale={k:statistics.stdev(m[k] for m in avgs) or 1. for k in ['h2','W1','identical','edit1']};scales[family][label]=scale
            losses=[]
            for m in avgs:
                distances={k:(m[k] if k=='W1' else abs(m[k]-target[label][k])) for k in scale};loss=statistics.mean((distances[k]/scale[k])**2 for k in scale)
                row=dict(family=family,target=label,candidate=m['candidate']['id'],loss=loss,**{k:m[k] for k in scale},**{'scale_'+k:v for k,v in scale.items()});losses.append(row);all_losses.append(row)
            best=min(losses,key=lambda x:(x['loss'],x['candidate']));chosen[family][label]=next(v['candidate'] for v in values if v['candidate']['id']==best['candidate'])
    table(R/'TRAINING_SEARCH.csv',all_losses);dump(R/'TRAINING_SCALES.json',scales);dump(R/'CHOSEN_TABLES.json',chosen)
    paths=[R/'TRAINING_TARGET_FINGERPRINTS.json',R/'TRAINING_SEARCH.csv',R/'TRAINING_SCALES.json',R/'CHOSEN_TABLES.json']+list((R/'fit_cache').rglob('*.json'))
    dump(R/'TABLES_FROZEN.json',dict(status='FROZEN_BEFORE_HELD_OUT_EVALUATION',registration_sha256=sha(R/'REGISTRATION.json'),files={str(p.relative_to(R)):sha(p) for p in paths},training_pages_only=True,held_out_fingerprints_computed=False,chosen=chosen))
    print('TABLES FROZEN',json.dumps(chosen),flush=True)
if __name__=='__main__':main()
