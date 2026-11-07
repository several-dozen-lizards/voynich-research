"""Known-text engineering qualification. No Voynich inputs are allowed here.
Actual manuscript flexible-key trap and published-v5 C2 controls remain separate gates.
"""
import copy,json,math,random,statistics,time
from pathlib import Path
from harness import *
P=Path(__file__).parent

def save(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def chunks(words,n=12): return [words[i:i+n] for i in range(0,len(words),n)]
def enc(w): return [('INIT_A' if i==0 and c=='a' else 'u'+c) for i,c in enumerate(w)]
def rows(units,prefix,custody):
    return [{'id':prefix+'-'+str(i),'folio':prefix,'custody':custody,'section':'herbal','class':'HERBAL','words':[enc(w) for w in ws]} for i,ws in enumerate(chunks(units))]

def summary_from_bank(k,train,held,target,lexicons,controls,bank):
    obs=raw_scores(k,train,held,target,lexicons); gain=0;above=[];metrics={}
    for e in EIDS:
        v=obs[e]['value'];vv=[z[e]['value'] for z in bank]
        if v is None or any(x is None for x in vv):continue
        med=statistics.median(vv);tail=(1+sum(x>=v for x in vv))/(len(vv)+1)
        if obs[e]['kind']=='rate':
            nn=obs[e]['n'];bits=signed_binomial_bits(obs[e]['success'],nn,(med*nn+.5)/(nn+1))
        else:bits=(v-med)*obs[e]['n']
        gain+=bits
        if tail<=.01:above.append(e)
        metrics[e]={'value':v,'median':med,'mc_p':tail,'gain_bits':bits}
    cs={name:raw_scores(k,train,x,target,lexicons) for name,x in controls.items()}
    gate=all(obs[e]['value'] is not None and c[e]['value'] is not None and obs[e]['value']>c[e]['value'] for c in cs.values() for e in ('E3','E4'))
    coh=gain-complexity(k)
    return {'verdict':'PASS' if coh>0 and len(above)>=2 and gate else 'PARTIAL' if above else 'FAIL','coherence_bits':coh,'K_bits':complexity(k),'above_99':above,'control_gate':gate,'metrics':metrics}

def main():
    start=time.time();src=json.loads((P/'latin-development-only.json').read_text(encoding='utf8'))
    def take(lo,hi):return [w for u in src if lo<=int(u['unit'].split('-')[1])<=hi for w in u['words'] if w.isascii() and w.isalpha()]
    target_words=take(1,16); train_words=take(17,30);held_words=take(31,46)
    # Fixed first 120 lines each bounds computational cost, with no fitted starts or retry.
    train=rows(train_words,'known-train','built')[:120];held=rows(held_words,'known-held','demonstrated_unbuilt')[:100]
    target=chunks(target_words);lexicons={'HERBAL':sorted(set(target_words))}
    alphabet=list('abcdefghijklmnopqrstuvwxyz')
    k={'id':'known-Latin-context-key','units':['u'+a for a in alphabet]+['INIT_A'],'map':{'u'+a:a for a in alphabet},'rules':[{'unit':'INIT_A','when':{'position':'first'},'value':'a','source':'issued synthetic cipher'}], 'target':{'system':'edited Latin herbal known-cipher engineering control','alphabet':alphabet,'resources':['Macer development chapters1-16; pinned local source manifest']},'built_on':[r['id'] for r in train],'provenance':{'u'+a:'issued synthetic cipher' for a in alphabet},'value_inventory':alphabet,'condition_inventory':[{'position':'first'},{'position':'last'},{'position':'interior'},{'position':'single'}],'process_evidence':'key issued by encoder; no optimisation on known-held; same-work control, not a new historical-language validation'}
    k['map']['INIT_A']='a'; k['provenance']['INIT_A']='issued synthetic first-position allograph'
    # Rule is operative: out-of-context INIT_A maps a too, so change default to z.
    # Single-letter a receives no context rule in this encoder; use a second explicit single rule.
    k['map']['INIT_A']='z'; k['rules'].append({'unit':'INIT_A','when':{'position':'single'},'value':'a','source':'issued single-unit allograph'})
    save('KNOWN-KEY.json',k)
    controls={'C1-word':shuffle_lines(held,random.Random(801)),'C1-glyph':shuffle_glyphs(held,random.Random(802)),'C2':shuffle_lines(held,random.Random(803))}
    plan={'status':'FROZEN_BEFORE_SCORING','seed':714,'baseline_keys':1000,'negative_proposals':100,'negative_seed':987,'positive':'issued fixed substitution plus initial-a context allograph','near_miss':'first round(20% map entries) chosen by seed991; each wrong value cyclic shifted alphabet','source':'existing Macer development chapters1-46 only; already exposed source, engineering control','partitions':{'target_LM_lexicon':'chapters1-16','cipher_train':'chapters17-30 first120 12-word lines','cipher_held':'chapters31-46 first100 12-word lines'},'input_sha256':digest({'key':k,'train':train,'held':held,'target':target,'lexicons':lexicons,'controls':controls}),'C2_limitation':'word-shuffled surrogate only; not all v5/v6 generator families; actual C2 qualification remains incomplete','trap_limitation':'no actual Voynich training-key optimisation in this run; required actual flexible-key trap remains unrun','gates':{'true_key':'PASS','random_proposals':'at least99% must FAIL; PARTIAL is retained and is not FAIL'},'manuscript_access':False}
    save('QUALIFICATION-PLAN.json',plan);save('KNOWN-CIPHER-DATA.json',{'train':train,'held':held,'target':target,'lexicons':lexicons,'controls':controls})
    print('Frozen known-text engineering plan',flush=True)
    result=evaluate(k,train,held,target,lexicons,controls,n_random=1000)
    save('KNOWN-POSITIVE-FULL.json',result);bank=result['C3_raw']
    positive=summary_from_bank(k,train,held,target,lexicons,controls,bank)
    corrupt=copy.deepcopy(k);rng=random.Random(991);selected=rng.sample(list(k['map']),round(.2*len(k['map'])))
    for u in selected:
        v=corrupt['map'][u];corrupt['map'][u]=alphabet[(alphabet.index(v)+1)%len(alphabet)]
    # Changed value frequencies require a fresh equal-complexity bank, not reuse of true bank.
    near=evaluate(corrupt,train,held,target,lexicons,controls,n_random=1000,seed=715);save('NEAR-MISS-FULL.json',near)
    print('Positive and near-miss complete',flush=True)
    negatives=[];rng=random.Random(987)
    for i in range(100):
        rk=random_key(k,rng);z=summary_from_bank(rk,train,held,target,lexicons,controls,bank);z['index']=i;z['key_sha256']=digest(rk);negatives.append(z)
        if i%20==19:print('Negative proposals',i+1,flush=True)
    save('NEGATIVE-PROPOSALS.json',negatives)
    tally=dict(Counter(x['verdict'] for x in negatives));failrate=tally.get('FAIL',0)/len(negatives)
    result={'status':'NOT_QUALIFIED_FOR_REAL_KEYS','known_text_positive':positive,'near_miss':{'verdict':near['single_reading_verdict'],'coherence_bits':near['coherence_bits'],'above_99':near['above_99'],'corrupted_entries':selected},'negative_tally':tally,'negative_fail_rate':failrate,'engineering_gates':{'positive_pass':positive['verdict']=='PASS','negative_FAIL_rate_at_least_99pct':failrate>=.99},'unrun':['actual Voynich flexible-key trap','C2 controls from all required v5/v6 generator families','independent noisy H/F positive','full E2 and numeral E5 qualification','published mechanical keys','all manuscript and vault evaluations'],'seconds':time.time()-start,'plan_sha256':digest(plan)}
    save('QUALIFICATION.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':main()
