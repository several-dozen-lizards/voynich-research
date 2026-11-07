"""Aggregate automatic metrics, commit a sealed blind key, verify accounting."""
from core import *
from prepare import R,ROOT,LAB,dump,read,table,sha
import gzip,json,os,random,secrets,zipfile,io,csv,statistics
from collections import defaultdict,Counter
BASE='LTR-LTR-TB-row'
def loadbest(arm,name):
    with gzip.open(R/'results'/arm/f'{name}-best-lines.json.gz','rt',encoding='utf8') as f:return json.load(f)
def average(rs,key='score'):return sum(r[key] for r in rs)/len(rs) if rs else None
def main():
    for arm in ['tanakh','medieval']:assert (R/'results'/arm/'COMPLETE.json').exists()
    checks=[];comparisons=[];baselines=[];topics=[];writermax=[];globalmax=[];envelopes=[]
    for arm in ['tanakh','medieval']:
        summary=read(R/'results'/arm/'variant-source-section.csv');cs=read(R/'results'/arm/'cross-context-consistency.csv')
        for source in ['ZL','C1','C9','C11','C17']:
          for version in (['clean'] if source=='ZL' else ['clean','noise']):
            rr=[r for r in summary if r['source']==source and r['version']==version and r['section']=='ALL']
            assert len(rr)==24
            expected=json.loads((R/'prepared/sources.json').read_text())[source+':'+version]['words']
            assert all(int(r['tokens'])==expected for r in rr)
            b=next(r for r in rr if r['variant']==BASE);baselines.append(b)
            bestglobal=max(rr,key=lambda r:(float(r['top_n_score']),r['variant']))
            best25=max(rr,key=lambda r:(float(r['top25_score']),r['variant']))
            gm=dict(arm=arm,source=source,version=version,size_mismatch=source=='C17',best_variant=bestglobal['variant'],top_n=int(bestglobal['top_n']),best_variant_score=float(bestglobal['top_n_score']),best25_variant=best25['variant'],best25_score=float(best25['top25_score']))
            globalmax.append(gm)
            bl=loadbest(arm,source+'-'+version);n=100 if source=='ZL' else 25;top=bl[:n]
            envelopes.append(dict(arm=arm,source=source,version=version,size_mismatch=source=='C17',n=len(top),linewise_max_score=average(top),linewise_top25=average(bl[:25]),mean_words=average(top,'words'),unknown_fraction=sum(r['unknowns'] for r in top)/sum(r['words'] for r in top),column_lines=sum(r['approximate_column'] for r in top)))
            if source=='C17':
                writers=defaultdict(list)
                for r in bl:writers[r['writer']].append(r)
                for writer,rs in writers.items():
                    top=sorted(rs,key=lambda x:-x['score'])[:25];writermax.append(dict(arm=arm,source='C17',version=version,writer=writer,size_mismatch=True,n=len(top),mean_best_score=average(top),mean_words=average(top,'words'),unknown_fraction=sum(r['unknowns'] for r in top)/sum(r['words'] for r in top)))
            # Every within-word reversal must preserve aggregate scores and every metric.
            lu={r['variant']:r for r in rr}
            for v in VARIANTS:
                if v[0]!='LTR':continue
                a=lu[variant_id(v)];b=lu[variant_id(('RTL',)+v[1:])]
                for field in ['tokens','hits','candidate_total','botanical','astronomical','top_n_score','mean_line_score']:
                    assert a[field]==b[field],(arm,source,version,v,field)
            checks.append(dict(check='variant_tokens_and_word_reversal',arm=arm,source=source,version=version,size_mismatch=source=='C17',status='PASS',words=expected))
        # Compare matching section and running-text support; labels/other ZL remain separately tabulated.
        for v in [variant_id(x) for x in VARIANTS]:
            z={r['section']:r for r in summary if r['source']=='ZL' and r['version']=='clean' and r['variant']==v and r['kind']=='running'}
            for r in summary:
                if r['source']=='ZL' or r['variant']!=v or r.get('kind')!='running' or r['section'] in ['ALL','WRITER']:continue
                if r['section'] not in z:continue
                a=z[r['section']]
                for topic in ['botanical','astronomical']:
                    topics.append(dict(arm=arm,variant=v,null=r['source'],version=r['version'],section=r['section'],size_mismatch=r['source']=='C17',ZL_tokens=int(a['tokens']),null_tokens=int(r['tokens']),topic=topic,ZL_rate=float(a[topic+'_rate']),null_rate=float(r[topic+'_rate']),difference=float(a[topic+'_rate'])-float(r[topic+'_rate']),ZL_any_candidate=float(a[topic+'_any_candidate_rate']),null_any_candidate=float(r[topic+'_any_candidate_rate'])))
    for arm in ['tanakh','medieval']:
        z=next(x for x in globalmax if x['arm']==arm and x['source']=='ZL')
        for n in globalmax:
            if n['arm']!=arm or n['source']=='ZL':continue
            comparisons.append(dict(arm=arm,null=n['source'],version=n['version'],size_mismatch=n['size_mismatch'],ZL_best_variant=z['best_variant'],null_best_variant=n['best_variant'],ZL_best_score=z['best_variant_score'],null_best_score=n['best_variant_score'],ZL_minus_null=z['best_variant_score']-n['best_variant_score'],ZL_minus_null_equal25=z['best25_score']-n['best25_score'],calibrated_p_value='NOT_ESTIMATED'))
    table(R/'dictionary-baseline.csv',baselines);table(R/'best-variant-scores.csv',globalmax);table(R/'linewise-max-scores.csv',envelopes);table(R/'max-statistic-comparisons.csv',comparisons);table(R/'topic-section-comparisons.csv',topics);table(R/'C17-writer-best-scores.csv',writermax)
    # Independent C11 source check: no key fitting assumptions needed for this algebraic invariant.
    zl={r['line_id']:r for r in read(R/'prepared/ZL-clean.csv')};c11=read(R/'prepared/C11-clean.csv');c11slots=0;differences=[]
    for r in c11:
        a=zl[r['line_id']]['text_eva'].split();b=r['text_eva'].split();assert len(a)==len(b)
        for i,(x,y) in enumerate(zip(a,b)):
            if Counter(x)!=Counter(y):differences.append((r['line_id'],i))
            c11slots+=1
    checks.append(dict(check='C11_matched_slot_character_multisets',status='PASS' if not differences else 'FAIL',slots=c11slots,differences=len(differences)))
    assert not differences
    previous=json.loads((R/'prepared/prior-files.json').read_text());changed=[p for p,h in previous.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    checks.append(dict(check='prior_lab_bytes',status='PASS' if not changed else 'CONCURRENT_CHANGE_OBSERVED',files=len(previous),changed=changed))
    dump(R/'CONCURRENT_CHANGE_RECEIPT.json',dict(changed=[dict(path=p,before_sha256=previous[p],after_sha256=sha(ROOT/p) if (ROOT/p).exists() else None) for p in changed],pipeline_writes_confined_to='c16-kh',prior_files_overwritten_by_this_pipeline=False))
    reg=json.loads((R/'REGISTRATION.json').read_text());drift=[p for p,h in reg['files'].items() if sha(R/p)!=h]
    checks.append(dict(check='frozen_inputs_and_algorithms',status='PASS' if not drift else 'FAIL',files=len(reg['files']),changed=drift));assert not drift
    # Create blind set only once. Never read or print the generated key.
    blind=R/'blind';sealed=R/'sealed';blind.mkdir(exist_ok=True);sealed.mkdir(exist_ok=True)
    if not (sealed/'key.zip').exists():
        chosen=[]
        for s,n in [('ZL',100),('C1',25),('C9',25),('C11',25),('C17',25)]:
            rs=loadbest('tanakh',s+'-clean')[:n];assert len(rs)==n;chosen+=rs
        random.SystemRandom().shuffle(chosen);rating=[];key=[]
        for r in chosen:
            item='KH-'+secrets.token_hex(6);rating.append(dict(item_id=item,decoded_line=r['decoded'],coherence_0_4='',grammaticality_0_4='',comments=''))
            key.append(dict(item_id=item,**r))
        table(blind/'ratings.csv',rating)
        (blind/'ratings.json').write_text(json.dumps(rating,ensure_ascii=True),encoding='utf8')
        with zipfile.ZipFile(sealed/'key.zip','w',zipfile.ZIP_DEFLATED) as z:z.writestr('key.json',json.dumps(key,ensure_ascii=True,indent=2))
        counts=Counter(r['source'] for r in chosen);dupes=len(chosen)-len({r['decoded'] for r in chosen})
        dump(blind/'EXPORT_RECEIPT.json',dict(items=len(chosen),ratings_sha256=sha(blind/'ratings.csv'),key_sha256=sha(sealed/'key.zip'),selected_counts=dict(counts),duplicate_decoded_strings=dupes,ratings_entered=0,key_opened_for_QA=False,arm='tanakh',version='clean'))
    (blind/'INSTRUCTIONS.txt').write_text('Read each line in the displayed word order. Rate coherence (0=no discernible connected meaning, 1=isolated recognizable words, 2=some connected fragments, 3=mostly coherent, 4=fully coherent) and grammaticality (0=none, 1=isolated forms, 2=partial grammatical phrases, 3=mostly grammatical, 4=fully grammatical). Leave a comment where useful. <UNK> means no exact dictionary candidate. Hebrew final letters were uniformly normalized to medial forms; do not penalize that convention alone. Do not attempt to identify sources or variants. Do not consult source keys. Leave unratable items blank and explain in comments. No ratings have been supplied.\n',encoding='utf8')
    dump(R/'VERIFICATION.json',dict(checks=checks,passed=all(c['status']=='PASS' for c in checks),blind_key_not_read=True,self_ratings=0))
    print(json.dumps(dict(comparisons=comparisons,verification_checks=len(checks),blind_items=200),indent=2))
if __name__=='__main__':main()
