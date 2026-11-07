from common import *
from src.noise import inject
def keys():return json.loads((R/'FIXED_KEYS.json').read_text())['codebooks']
def units(text,rng):
    result=[];i=0
    while i<len(text):
        width=1 if i==len(text)-1 or rng.random()<17/36 else 2;result.append(text[i:i+width]);i+=width
    return result
def main():
    verify();assert not (R/'DATA_READY.json').exists();meta=json.loads((R/'LAYOUT.json').read_text());code=keys();phy=facts();rates=json.loads((R/'noise_model.json').read_text())['rates'];label=known_labels();alpha=set(''.join(v for key in code.values() for v in key.values()));byl=defaultdict(list);by_page=defaultdict(list)
    for r in meta:by_page[r['folio']].append(r);byl[leaf(r['folio'])].append(r)
    intervals={};offset=0
    for page,rs in by_page.items():n=sum(r['word_slots'] for r in rs);intervals[page]=(offset,offset+2*n);offset+=2*n
    jobs=plan('development')+plan('qualification');receipts=[]
    for stage,seeds in [('development',DEV),('qualification',QUAL)]:
        plains={c:(R/'plaintext'/f'{c}_{stage}.txt').read_text(encoding='utf8') for c in ['C1','C2']}
        for seed in seeds:
            normal={};cloned={}
            for family in ['C1','C2']:
                for page,rs in by_page.items():
                    a,b=intervals[page];n=sum(r['word_slots'] for r in rs);parts=units(plains[family][a:b],random.Random(sid(stage,seed,page,'segmentation')));assert len(parts)>=n;normal[family,page]=parts[:n]
                if stage=='qualification':
                    for sheet in sorted({p['sheet'] for p in phy.values()}):
                        leaves=[int(k) for k,p in phy.items() if p['sheet']==sheet and int(k) in byl]
                        if not leaves:continue
                        owner=max(leaves,key=lambda l:sum(r['word_slots'] for r in byl[l]));ps=list(dict.fromkeys(r['folio'] for r in byl[owner]));text=''.join(plains[family][intervals[p][0]:intervals[p][1]] for p in ps);parts=units(text,random.Random(sid(stage,seed,sheet,'physical_clone')))
                        for l in leaves:
                            n=sum(r['word_slots'] for r in byl[l]);assert len(parts)>=n;j=0
                            for page in dict.fromkeys(r['folio'] for r in byl[l]):size=sum(r['word_slots'] for r in by_page[page]);cloned[family,page]=parts[j:j+size];j+=size
            for job in [x for x in jobs if x['stage']==stage and x['seed']==seed]:
                rows=[];operations=Counter();keya=['alpha','beta1'][job['orientation']];keyb=['beta1','alpha'][job['orientation']] if job['condition'].endswith('TWO') else keya;other='C2' if job['base']=='C1' else 'C1';usage=Counter()
                for page,rs in by_page.items():
                    if leaf(page) not in label or rs[0].get('currier_lang') not in ['A','B']:continue
                    partition=label[leaf(page)];family=other if job['condition'].startswith('DIFF') and partition=='B' else job['base'];key=keya if partition=='A' else keyb;source=(cloned if job['fixture'] else normal)[family,page];tokens=[code[key][u] for u in source];assert len(tokens)==sum(r['word_slots'] for r in rs);j=0;usage[key]+=len(tokens)
                    for r in rs:
                        n=r['word_slots'];text=' '.join(tokens[j:j+n]);j+=n
                        if job['view']=='noise':text,op,_=inject(text,rates,alpha,random.Random(sid(stage,seed,r['line_id'],'noise')));operations.update(op)
                        rows.append(dict(folio=page,line_id=r['line_id'],text_eva=text))
                if job['condition'].endswith('TWO'):assert len(usage)==2 and all(n>0 for n in usage.values())
                folder=R/'data'/job['id'];table(folder/'text.csv',rows);dump(folder/'truth.json',dict(job=job,A_key=keya,B_key=keyb,keys_distinct=keya!=keyb,source_base=job['base'],different_plaintexts=job['condition'].startswith('DIFF'),key_token_counts=dict(usage),noise_operations=dict(operations),native_codebook_hashes=json.loads((R/'FIXED_KEYS.json').read_text())['hashes']))
            print('generated fixed-key controls',stage,seed,flush=True)
    dump(R/'DATA_READY.json',dict(status='ALL_FIXED_CONTROLS_GENERATED_BEFORE_SCORING',jobs=jobs,files={str(p.relative_to(R)):sha(p) for p in (R/'data').rglob('*') if p.is_file()},source_page_intervals=intervals))
    print('DATA READY',len(jobs),'datasets; fixed keys and common segmentation; no target text.')
if __name__=='__main__':main()
