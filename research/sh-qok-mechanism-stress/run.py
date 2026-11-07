from pathlib import Path
import json, hashlib, types, sys
import numpy as np

R=Path(__file__).resolve().parent
SOURCE=R.parent/'sh-qok-ending-qualification-reed-v94/run.py'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x): (R/name).write_text(json.dumps(x,indent=2),encoding='utf-8')
if sys.argv[1]=='freeze':
    save('PROTOCOL.json',dict(scope='Synthetic mechanism stress test only; no manuscript data read or rescored.',trials=100,permutations=999,seeds='950000 + regime_index*1000 + trial; permutation seed adds 500000',regimes=['page_preferences','interior_position','junction_spelling','repeated_phrase'],construction='8 pages x 6 lines x 10 tokens. Page preferences: independent tokens with correlated page sh and qok prevalence. Interior position: sh occupies slot2 and qok slot3, ch slot6 and dar slot7, regardless of word identity; endpoints fixed. Junction spelling: random qok placement, spell preceding chedy as shedy if next is qok. Repeated phrase: insert shedy qokam and chedy dar at randomly chosen nonoverlapping interior slots. No grammar in any generator.',statistic='Unchanged v94 ending_family and exact_body, both whole_line and fixed_endpoints nulls. Bonferroni16 retained. Store every trial, including failures.',criteria='For each view/null: page_preferences false-flag Wilson95 upper bound <=.10; junction_spelling and repeated_phrase detection Wilson95 lower bound >=.80. Interior_position is an adversarial diagnostic: rejection demonstrates lack of specificity to adjacency beyond interior positional structure; no requirement that it pass. These are finite authored controls, not universal qualification.',interpretation='Junction and phrase detections are genuine dependence, not false positives for association. They refute interpreting rejection as uniquely grammar. Interior-position flags show endpoint fixing is insufficient for this positional confound. No fresh manuscript holdout available; do not rescore or choose a revised test here.'))
    save('FREEZE.json',{str(p):digest(p) for p in [Path(__file__),SOURCE,R/'PROTOCOL.json']})
    print('Frozen before synthetic trials.');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items(): assert digest(Path(p))==h
# Load definitions only: the source's command-line branches cannot execute.
source=SOURCE.read_text(encoding='utf-8').split("if sys.argv[1]=='freeze':")[0]
m=types.ModuleType('frozen_v94');m.__file__=str(SOURCE);exec(compile(source,str(SOURCE),'exec'),m.__dict__)
def generate(kind,rng):
    rows=[]
    for page in range(8):
        rate=.15+.7*page/7
        for line in range(6):
            words=[]
            for j in range(10):
                u=rng.random()
                words.append(('shedy' if rng.random()<rate else 'chedy') if u<.4 else ('qokam' if rng.random()<rate else 'dar'))
            if kind=='interior_position':
                words=['a','shedy','qokam','ol','ar','chedy','dar','ol','ar','z']
            elif kind=='junction_spelling':
                words=['chedy' if rng.random()<.5 else ('qokam' if rng.random()<.5 else 'dar') for _ in range(10)]
                words=[('shedy' if j<9 and words[j+1]=='qokam' else w) if w=='chedy' else w for j,w in enumerate(words)]
            elif kind=='repeated_phrase':
                words=['a']+[str(rng.choice(['ol','ar','dar'])) for _ in range(8)]+['z']
                a,b=rng.choice([1,3,5,7],size=2,replace=False)
                words[a:a+2]=['shedy','qokam'];words[b:b+2]=['chedy','dar']
            rows.append(dict(page=str(page),tokens=words))
    return rows
records=[];views=['ending_family','exact_body']
for ki,kind in enumerate(['page_preferences','interior_position','junction_spelling','repeated_phrase']):
    for trial in range(100):
        seed=950000+ki*1000+trial;p=m.encode(generate(kind,np.random.default_rng(seed)))
        for mi,mode in enumerate(['whole_line','fixed_endpoints']):
            null,_=m.simulate(p,mode,999,seed+500000+mi*100000,views)
            for view in views:
                t,_=m.score(p['original'],p,view);pv=min(1.,16*(1+int(np.sum(null[view]>=t-1e-12)))/1000)
                records.append(dict(regime=kind,trial=trial,seed=seed,view=view,null=mode,T=t,p_adjusted=pv,flag=pv<=.05))
    save('TRIALS.json',records);print(kind,'complete',flush=True)
def wilson(k,n):
    z=1.959963984540054;c=(k/n+z*z/(2*n))/(1+z*z/n);w=z*((k/n*(1-k/n)/n+z*z/(4*n*n))**.5)/(1+z*z/n)
    return [c-w,c+w]
summary=[]
for kind in ['page_preferences','interior_position','junction_spelling','repeated_phrase']:
    for mode in ['whole_line','fixed_endpoints']:
        for view in views:
            rr=[r for r in records if r['regime']==kind and r['null']==mode and r['view']==view];k=sum(r['flag'] for r in rr);ci=wilson(k,len(rr))
            gate=ci[1]<=.10 if kind=='page_preferences' else (ci[0]>=.80 if kind in ['junction_spelling','repeated_phrase'] else None)
            summary.append(dict(regime=kind,null=mode,view=view,flags=k,trials=len(rr),wilson95=ci,gate=gate))
save('SUMMARY.json',summary);save('VERIFICATION.json',dict(frozen_hashes_unchanged=all(digest(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),records=len(records),manuscript_read=False))
print(json.dumps(summary,indent=2))
