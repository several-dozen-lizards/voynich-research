"""Independent count-vector audit, without inspecting semantic text."""
from prepare import R,read,dump,sha
import json,gzip,collections,itertools,math
def signature(w):return tuple(sorted(collections.Counter(w).items()))
def main():
    checks=[];audited=0
    for arm in ['tanakh','medieval']:
        seqs=json.loads((R/'prepared'/f'{arm}.json').read_text())['train'];vocab={w for s in seqs for w in s};lex=collections.defaultdict(set)
        for w in vocab:lex[signature(w)].add(w)
        for source in ['ZL','C1','C9','C11','C17']:
          for version in (['clean'] if source=='ZL' else ['clean','noise']):
            count=0
            with gzip.open(R/'results'/arm/f'{source}-{version}-tokens.jsonl.gz','rt',encoding='utf8') as f:
                for raw in f:
                    r=json.loads(raw);expected=lex[signature(r['mapped_alphagram'])]
                    assert expected==set(r['candidates'])
                    assert len(expected)==r['candidate_count']
                    assert (r['selected'] in expected) if expected else r['selected']=='<UNK>'
                    count+=1
                    if count==1000:break
            checks.append(dict(arm=arm,source=source,version=version,size_mismatch=source=='C17',audit='independent_count_vector_candidates',tokens=count,status='PASS'));audited+=count
        keys=list((R/'results'/arm/'keys').glob('*.json'))
        for kp in keys:
            k=json.loads(kp.read_text())['key'];assert len(k)==len(set(k.values()))
        checks.append(dict(arm=arm,audit='all_keys_injective',keys=len(keys),status='PASS'))
    # Independent brute force on physical-context pair logic, including unknowns and same-line repeats.
    from run import consistency
    groups={'x':[('p1','l1','a'),('p1','l1','b'),('p1','l2','a'),('p2','l3','a'),('p2','l3','<UNK>')],'y':[('p1','l1','<UNK>'),('p2','l2','<UNK>')]}
    pairs=[(a,b) for obs in groups.values() for a,b in itertools.combinations(obs,2) if a[:2]!=b[:2]]
    known=[(a,b) for a,b in pairs if a[2]!='<UNK>' and b[2]!='<UNK>'];cross=[(a,b) for a,b in pairs if a[0]!=b[0]];within=[(a,b) for a,b in pairs if a[0]==b[0]];r=consistency(groups)
    for ps,nkey,rkey in [(pairs,'pairs','pair_agreement'),(known,'known_pairs','known_pair_agreement'),(cross,'cross_page_pairs','cross_page_agreement'),(within,'within_key_pairs','within_key_agreement')]:
        assert len(ps)==r[nkey];assert math.isclose(sum(a[2]==b[2] for a,b in ps)/len(ps),r[rkey])
    checks.append(dict(audit='independent_context_pairs',status='PASS'))
    dump(R/'INDEPENDENT_VERIFICATION.json',dict(checks=checks,audited_tokens=audited,passed=True,no_semantic_rating=True));print(json.dumps(dict(checks=len(checks),tokens=audited,status='PASS')))
if __name__=='__main__':main()
