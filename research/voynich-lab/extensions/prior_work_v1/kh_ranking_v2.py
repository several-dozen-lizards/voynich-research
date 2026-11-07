"""Declared rank-only amendment of C16-KH v1; no decoding/key/model refit.

The human explicitly selected existing v1 decoded lines and the original LM.
This does not incorporate the separate concurrent scorer-repair project.
"""
import gzip,types,math,secrets,zipfile,statistics
from collections import Counter,defaultdict
from .common import *
KH=ROOT.parent/'c16-kh'
OUT=EXT/'c16_kh_ranking_v2'

def original():
    module=types.ModuleType('preserved_kh_v1')
    exec(compile((KH/'core.py').read_text(encoding='utf-8'),str(KH/'core.py'),'exec'),module.__dict__)
    return module

def rank_score(lm,decoded,minimum=.6):
    words=decoded.split() if isinstance(decoded,str) else list(decoded);known=sum(w!='<UNK>' for w in words)
    if not words or known/len(words)<minimum:return dict(eligible=False,known=known,words=len(words),known_fraction=known/max(1,len(words)),score_v2=None)
    a=b='<s>';value=0.
    for word in words:
        if word!='<UNK>':value+=lm.logp(a,b,word)
        # Unknown targets are excluded from the mean, NOT removed from history.
        a,b=b,word
    return dict(eligible=True,known=known,words=len(words),known_fraction=known/len(words),score_v2=value/known)

def mechanical_qualification(core):
    lm=core.LM([['a','b','c']]*100)
    assert not rank_score(lm,['<UNK>']*5)['eligible']
    assert not rank_score(lm,['a','<UNK>','<UNK>'])['eligible']
    assert rank_score(lm,['a','b','c','<UNK>','<UNK>'])['eligible']
    actual=rank_score(lm,['a','<UNK>','b']);expected=(lm.logp('<s>','<s>','a')+lm.logp('a','<UNK>','b'))/2
    assert abs(actual['score_v2']-expected)<1e-12
    assert not rank_score(lm,[])['eligible']
    return dict(status='PASS',checks=['all-unknown rejected','coverage threshold inclusive at60%','unknown targets omitted','original unknown history retained','BOS/EOS omitted from word mean','empty line rejected'])

def input_paths():
    paths=[KH/'core.py',KH/'REGISTRATION.json',KH/'STATUS.json',KH/'linewise-max-scores.csv',KH/'best-variant-scores.csv',KH/'sealed/key.zip']
    for arm in ['tanakh','medieval']:
        paths.append(KH/f'prepared/{arm}.json')
        paths.extend((KH/f'results/{arm}').glob('*-lines.jsonl.gz'))
    return paths

def run():
    for directory in ['report','blind','sealed','results']:(OUT/directory).mkdir(parents=True,exist_ok=True)
    registration=OUT/'REGISTRATION.json'
    if registration.exists():reg=json.loads(registration.read_text())
    else:
        reg=dict(status='FROZEN_BEFORE_RANKING',amendment='post-failure rank-only v2',source='existing v1 decoded lines and original LM, explicitly chosen by human',
            rules=json.loads((EXT/'phase6_additions.json').read_text())['C16_KH_ranking_v2'],code_sha256=sha(Path(__file__)),
            inputs={str(p.relative_to(ROOT.parent)):sha(p) for p in input_paths()},sealed_v1_key_not_opened=True)
        dump(registration,reg)
    assert sha(Path(__file__))==reg['code_sha256']
    core=original();qualification=mechanical_qualification(core);dump(OUT/'report/MECHANICAL_QUALIFICATION.json',qualification)
    variants=[core.variant_id(v) for v in core.VARIANTS];rank={v:i for i,v in enumerate(variants)}
    all_summary=[];global_best=[];linewise=[];heldout=[];comparisons=[];all_best={}
    for arm in ['tanakh','medieval']:
        source=json.loads((KH/f'prepared/{arm}.json').read_text());lm=core.LM(source['train'])
        # Calibration occurs before manuscript ranking. It is not a refit.
        positive=[]
        for sequence in source['test']:
            decoded=[w if w in lm.u else core.UNK for w in sequence];score=rank_score(lm,decoded)
            if score['eligible']:positive.append(score['score_v2'])
        heldout.append(dict(arm=arm,source='heldout_Hebrew',lines=len(source['test']),eligible_lines=len(positive),eligible_fraction=len(positive)/len(source['test']),mean_known_logp=statistics.mean(positive) if positive else None,
            interpretation='mechanical eligibility/calibration; no repaired LM or key-search claim'))
        sources=[(name,version) for name in ['C1','C9','C11','C17','ZL'] for version in (['clean'] if name=='ZL' else ['clean','noise'])]
        for source_name,version in sources:
            name=source_name+'-'+version;file=OUT/f'results/{arm}-{name}.json'
            if file.exists():result=json.loads(file.read_text());best=result['best'];summary=result['summary']
            else:
                scores=defaultdict(list);totals=Counter();best={};known_totals=Counter();word_totals=Counter()
                with gzip.open(KH/f'results/{arm}/{name}-lines.jsonl.gz','rt',encoding='utf-8') as stream:
                    for line in stream:
                        r=json.loads(line);value=rank_score(lm,r['decoded']);assert value['words']==r['words'];v=r['variant'];totals[v]+=1
                        known_totals[v]+=value['known'];word_totals[v]+=value['words']
                        if not value['eligible']:continue
                        row={**r,**value,'score_v1':r['score']};scores[v].append(row);identity=r['identity']
                        if identity not in best or (row['score_v2'],-rank[v])>(best[identity]['score_v2'],-rank[best[identity]['variant']]):best[identity]=row
                        if len(lm.cache)>300000:lm.cache.clear()
                n=100 if source_name=='ZL' else 25;summary=[]
                for v in variants:
                    top=sorted(scores[v],key=lambda r:(-r['score_v2'],r['identity']))[:n]
                    summary.append(dict(arm=arm,source=source_name,version=version,variant=v,all_lines=totals[v],eligible_lines=len(scores[v]),
                        eligible_fraction=len(scores[v])/max(1,totals[v]),known_tokens=known_totals[v],all_tokens=word_totals[v],target_n=n,actual_n=len(top),
                        top_n_score=statistics.mean(r['score_v2'] for r in top) if top else None,
                        top25_score=statistics.mean(r['score_v2'] for r in top[:25]) if top else None,size_mismatch=source_name=='C17'))
                best=sorted(best.values(),key=lambda r:(-r['score_v2'],rank[r['variant']],r['identity']))
                result=dict(best=best,summary=summary);dump(file,result)
            all_summary.extend(summary);all_best[arm,source_name,version]=best
            eligible=[r for r in summary if r['actual_n']]
            if eligible:
                chosen=max(eligible,key=lambda r:(r['top_n_score'],-rank[r['variant']]))
                global_best.append(dict(**chosen,selection='global best variant among24; eligible only'))
            n=100 if source_name=='ZL' else 25;top=best[:n]
            linewise.append(dict(arm=arm,source=source_name,version=version,eligible_identities=len(best),target_n=n,actual_n=len(top),
                mean_known_logp=statistics.mean(r['score_v2'] for r in top) if top else None,mean_words=statistics.mean(r['words'] for r in top) if top else None,
                minimum_known_fraction=min((r['known_fraction'] for r in top),default=None),unknown_fraction=sum(r['words']-r['known'] for r in top)/sum(r['words'] for r in top) if top else None,
                one_word_items=sum(r['words']==1 for r in top),approximate_column_items=sum(r['approximate_column'] for r in top),size_mismatch=source_name=='C17'))
            table(OUT/'report/variant_source_scores_v2.csv',all_summary);table(OUT/'report/linewise_max_scores_v2.csv',linewise)
            progress('C16-KH known-token ranking v2',arm=arm,source=source_name,version=version,eligible=len(best))
        del lm
    table(OUT/'report/global_best_variant_v2.csv',global_best);table(OUT/'report/heldout_Hebrew_calibration.csv',heldout)
    with (KH/'linewise-max-scores.csv').open(encoding='utf-8-sig',newline='') as f:v1=list(csv.DictReader(f))
    side=[]
    for row in linewise:
        previous=next(r for r in v1 if (r['arm'],r['source'],r['version'])==(row['arm'],row['source'],row['version']))
        side.append(dict(**row,v1_selected_n=previous['n'],v1_unknown_fraction=previous['unknown_fraction'],v1_mean_score=previous['linewise_max_score'],
            score_scale_warning='v1 includes UNK/EOS; v2 averages known words only; raw score magnitudes are not directly comparable'))
    table(OUT/'report/v1_v2_side_by_side.csv',side)
    for arm in ['tanakh','medieval']:
        z=all_best[arm,'ZL','clean']
        for source_name in ['C1','C9','C11','C17']:
            for version in ['clean','noise']:
                null=all_best[arm,source_name,version];n=min(25,len(z),len(null))
                comparisons.append(dict(arm=arm,null=source_name,version=version,equal_n=n,ZL_score=statistics.mean(r['score_v2'] for r in z[:n]) if n else None,
                    null_score=statistics.mean(r['score_v2'] for r in null[:n]) if n else None,calibrated_p_value='NOT_ESTIMATED',size_mismatch=source_name=='C17'))
    table(OUT/'report/max_statistic_comparisons_v2.csv',comparisons)
    export(all_best)
    drift=[p for p,h in reg['inputs'].items() if sha(ROOT.parent/p)!=h];assert not drift
    dump(OUT/'report/VERIFICATION.json',dict(status='PASS',v1_input_drift=drift,unknown_rule_test='PASS',minimum_coverage=.6,
        no_key_refits=True,original_LM_retained=True,variants=24,source_versions_per_arm=9,arms=2,sealed_v1_key_opened=False,self_ratings=0))

def export(all_best):
    if (OUT/'sealed/key.zip').exists():return
    chosen=[];deficits=[]
    for source,n in [('ZL',100),('C1',25),('C9',25),('C11',25),('C17',25)]:
        rs=all_best['tanakh',source,'clean'][:n];chosen.extend(rs)
        if len(rs)<n:deficits.append(dict(source=source,target=n,eligible_selected=len(rs)))
    random.SystemRandom().shuffle(chosen);ratings=[];key=[]
    for r in chosen:
        item='KH2-'+secrets.token_hex(6);ratings.append(dict(item_id=item,decoded_line=r['decoded'],coherence_0_4='',grammaticality_0_4='',comments=''));key.append(dict(item_id=item,**r))
    if ratings:
        table(OUT/'blind/ratings.csv',ratings);dump(OUT/'blind/ratings.json',ratings)
    else:(OUT/'blind/ratings.csv').write_text('item_id,decoded_line,coherence_0_4,grammaticality_0_4,comments\n',encoding='utf-8');dump(OUT/'blind/ratings.json',[])
    with zipfile.ZipFile(OUT/'sealed/key.zip','w',zipfile.ZIP_DEFLATED) as z:z.writestr('key.json',json.dumps(key,ensure_ascii=True,indent=2))
    instructions=(KH/'blind/INSTRUCTIONS.txt').read_text(encoding='utf-8');(OUT/'blind/INSTRUCTIONS.txt').write_text(instructions,encoding='utf-8')
    with zipfile.ZipFile(OUT/'blind/rater-only.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ['ratings.csv','ratings.json','INSTRUCTIONS.txt']:z.write(OUT/'blind'/name,name)
    dump(OUT/'report/EXPORT_RECEIPT.json',dict(status='COMPLETE' if len(chosen)==200 else 'PARTIAL_INSUFFICIENT_ELIGIBLE' if chosen else 'NO_ELIGIBLE_ITEMS',items=len(chosen),target_items=200,deficits=deficits,selected_counts=dict(Counter(r['source'] for r in chosen)),
        all_items_meet_coverage=all(r['known_fraction']>=.6 for r in chosen),all_unknown_items=0,
        duplicate_decoded_strings=len(chosen)-len({r['decoded'] for r in chosen}),ratings_sha256=sha(OUT/'blind/ratings.csv'),key_sha256=sha(OUT/'sealed/key.zip'),
        ratings_entered=0,key_opened_for_QA=False,source_and_variant_stripped=True))
if __name__=='__main__':run()
