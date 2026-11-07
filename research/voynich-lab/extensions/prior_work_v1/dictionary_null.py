"""Frozen dictionary-hit calibration; never language/semantic evidence."""
import unicodedata,statistics
from collections import Counter,defaultdict
from .common import *
FINAL=str.maketrans('\u05da\u05dd\u05df\u05e3\u05e5','\u05db\u05de\u05e0\u05e4\u05e6')
def normalize(word,language,remove_vowels):
    s=unicodedata.normalize('NFD',word.casefold()).translate(FINAL)
    if language=='Latin':s=''.join(c for c in s if 'a'<=c<='z')
    else:s=''.join(c for c in s if '\u05d0'<=c<='\u05ea' or '\u05b0'<=c<='\u05bc' or c in '\u05c1\u05c2\u05c7')
    if remove_vowels:
        if language=='Latin':s=''.join(c for c in s if c not in 'aeiou')
        else:s=''.join(c for c in s if not ('\u05b0'<=c<='\u05bb' or c=='\u05c7'))
    return s
def signature(word,language,fill=False):
    if fill:
        word=''.join(c for c in word if c not in 'aeiou') if language=='Latin' else ''.join(c for c in word if '\u05d0'<=c<='\u05ea')
    return ''.join(sorted(word))
def dictionary(path,language,removed,fill):
    indices=defaultdict(set)
    for word in path.read_text(encoding='utf-8-sig').split():
        norm=normalize(word,language,removed);key=signature(norm,language,fill)
        if key:indices[key].add(word)
    return indices
def evaluate(counts,indices,language,removed,fill,mapping=None):
    accum={b:dict(tokens=0,types=0,hits=0,type_hits=0,candidates=0,unique_hits=0,unsupported=0) for b in ['ALL','1','2','3-5','6+']}
    for word,frequency in counts.items():
        unsupported=mapping is not None and any(c not in mapping for c in word)
        mapped=''.join(mapping.get(c,'\ufffd') for c in word) if mapping is not None else word
        normal=normalize(mapped,language,removed);key=signature(normal,language,fill)
        # Reject unsupported/empty input, never turn normalization loss into a hit.
        unsupported=unsupported or '\ufffd' in mapped
        candidates=0 if unsupported or not key or word=='\u2205' else len(indices.get(key,()))
        length=len(normal);bucket='1' if length<=1 else '2' if length==2 else '3-5' if length<=5 else '6+'
        for b in ['ALL',bucket]:
            a=accum[b];a['tokens']+=frequency;a['types']+=1;a['hits']+=frequency*(candidates>0);a['type_hits']+=candidates>0
            a['candidates']+=frequency*candidates;a['unique_hits']+=frequency*(candidates==1);a['unsupported']+=frequency*unsupported
    return [dict(length_stratum=b,**a,hit_rate=a['hits']/a['tokens'] if a['tokens'] else None,
        type_hit_rate=a['type_hits']/a['types'] if a['types'] else None,mean_candidate_count=a['candidates']/a['tokens'] if a['tokens'] else None,
        unique_candidate_rate=a['unique_hits']/a['tokens'] if a['tokens'] else None) for b,a in accum.items()]
def run():
    registration=dict(phase6_config_sha256=sha(EXT/'config.json'),code_sha256=sha(Path(__file__)),
        dictionaries={str(p.relative_to(ROOT)):sha(p) for p in (EXT/'dictionaries').glob('*.txt')},
        normalization='NFD; final Hebrew forms fold uniformly; ASCII Latin; same target normalization on every query and dictionary',
        permutations=100,selection='no mapping chosen; all map scores and distribution retained')
    dump(EXT/'runs/DICTIONARY_FREEZE.json',registration);output=[]
    for language in ['Latin','Hebrew']:
        path=EXT/('dictionaries/Latin_independent.txt' if language=='Latin' else 'dictionaries/Hebrew_heldout.txt')
        for removed in [False,True]:
            variant='novowels' if removed else 'vowels';name=f'C16_{language}_{variant}'
            positive=rows(EXT/f'data/{name}/native.csv');counts=Counter(w for r in positive for w in r['text_eva'].split())
            inverse={v:k for k,v in registry()[name+'_noise']['symbol_mapping'].items()}
            positive_noisy=corpus(name+'_noise')
            noisy_counts=Counter(''.join(inverse.get(c,'\ufffd') for c in word) for r in positive_noisy for word in r['text_eva'].split())
            target_alphabet=sorted(set(''.join(normalize(w,language,removed) for w in path.read_text(encoding='utf-8-sig').split())))
            for fill in [False,True]:
                indices=dictionary(path,language,removed,fill);kind='vowel_fill' if fill else 'exact_anagram'
                for version,current in [('clean',counts),('noise',noisy_counts)]:
                    for result in evaluate(current,indices,language,removed,fill):output.append(dict(corpus=name+'_'+version,target_language=language,target_variant=variant,method=kind,mapping='native',**result))
                for null in ['C9','C11']:
                    clean=corpus(null+'_clean');source_alphabet=sorted(set(''.join(r['text_eva'].replace(' ','') for r in clean))-{'\ufffd'})
                    for version in ['clean','noise']:
                        current=corpus(null+'_'+version);null_counts=Counter(w for r in current for w in r['text_eva'].split())
                        maps=[('identity',{c:c for c in source_alphabet})] if language=='Latin' else []
                        for i in range(100):
                            target=target_alphabet[:];rng_for(1729,language+variant+':map:'+str(i)).shuffle(target)
                            maps.append((f'permutation_{i:03d}',dict(zip(source_alphabet,target))))
                        for label,mapping in maps:
                            for result in evaluate(null_counts,indices,language,removed,fill,mapping):
                                output.append(dict(corpus=null+'_'+version,target_language=language,target_variant=variant,method=kind,mapping=label,**result))
            progress('dictionary null calibration',language=language,variant=variant)
    table(EXT/'report/C16_dictionary_hits.csv',output);summary=[]
    keys=sorted({(r['corpus'],r['target_language'],r['target_variant'],r['method']) for r in output})
    for key in keys:
        rs=[r for r in output if (r['corpus'],r['target_language'],r['target_variant'],r['method'])==key and r['length_stratum']=='ALL' and r['mapping'].startswith('permutation_')]
        if not rs:continue
        values=sorted(r['hit_rate'] for r in rs);summary.append(dict(corpus=key[0],target_language=key[1],target_variant=key[2],method=key[3],maps=len(rs),
            mean_hit_rate=statistics.mean(values),sd_hit_rate=statistics.stdev(values),p95_hit_rate=values[94],maximum_hit_rate=max(values)))
    table(EXT/'report/C16_dictionary_null_summary.csv',summary)
if __name__=='__main__':run()
