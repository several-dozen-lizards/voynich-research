"""Parameterized synthetic controls, not authenticated medieval writing systems.

C4: suffix contraction, initial per/pro/prae sigla, suspension.
C5: top-frequency Latin words (learned from C1 only) become eight reused sigla;
other words use C4's abbreviated stem/ending mechanism.
C6: C5 plus fixed Latin planet/zodiac terms mapped to the same eight mark classes.
C7: seeded injective fixed letter->1..3-symbol code groups (not prefix-free).
C8: simplified self-citation: copy one of the previous window words, then optionally
substitute/insert/delete one symbol; no claim of reproducing Timm/Schinner's software.
C9: simplified prefix/middle/suffix table with seeded shuffled cyclic cells and a
coprime stride grille; no claim of reproducing Rugg's historical construction.

All stochastic choices use the supplied random.Random instance. No parameter is
fitted to Voynich metrics. C4-C6 aggressiveness is swept only in Phase 5.
Eight marks are intentionally reused by position (as ambiguous shorthand can be).
"""
from collections import Counter
import math

SIGLA = [chr(0xe100+i) for i in range(8)]
ENDINGS = ['orum','arum','rum','us','um','que','is','ae']
INITIALS = ['per','pro','prae']
ASTRO = ['sol','solis','luna','lunae','mercurius','venus','mars','iuppiter','saturnus',
         'aries','taurus','gemini','cancer','leo','virgo','libra','scorpius','sagittarius','capricornus','aquarius','pisces']

def abbreviation(word, rng, aggressiveness):
    if rng.random() >= aggressiveness:
        return word
    for i, prefix in enumerate(INITIALS):
        if word.startswith(prefix) and len(word)>len(prefix):
            return SIGLA[i]+word[len(prefix):]
    for i, suffix in enumerate(ENDINGS):
        if word.endswith(suffix) and len(word)>len(suffix)+1:
            return word[:-len(suffix)]+SIGLA[i]
    if len(word)>4:
        return word[:max(2,math.ceil(len(word)*0.55))]+SIGLA[7]
    return word

def encode(words, mode, rng, config):
    a = config['encoder_aggressiveness']
    if mode in ['C4','C5','C6']:
        common = {w:SIGLA[i] for i,(w,_) in enumerate(sorted(Counter(words).items(), key=lambda x:(-x[1],x[0]))[:8])}
        astro = {w:SIGLA[i%8] for i,w in enumerate(ASTRO)}
        out = []
        for w in words:
            if mode=='C6' and w in astro and rng.random()<a:
                out.append(astro[w])
            elif mode in ['C5','C6'] and w in common and rng.random()<a:
                out.append(common[w])
            else:
                out.append(abbreviation(w,rng,a))
        return out, dict(aggressiveness=a, common_sigla=common if mode!='C4' else {}, astro_sigla=astro if mode=='C6' else {})
    if mode=='C7':
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        used, code = set(), {}
        for c in sorted(set(''.join(words))):
            while True:
                group = ''.join(rng.choices(alphabet,k=rng.randint(1,3)))
                if group not in used:
                    break
            used.add(group)
            code[c]=group
        return [''.join(code[c] for c in w) for w in words], dict(codebook=code)
    raise ValueError(mode)

def self_citation(n, rng, config):
    alphabet='abcdefghiklmnopqrstuvxyz'
    recent=['daiin','chol','shedy','qokedy']
    out=[]
    for _ in range(n):
        w=rng.choice(recent[-config['copy_window']:])
        if rng.random()<config['copy_mutation_probability']:
            pos=rng.randrange(len(w)); op=rng.randrange(3)
            if op==0:
                w=w[:pos]+rng.choice(alphabet)+w[pos+1:]
            elif op==1 and len(w)<18:
                w=w[:pos]+rng.choice(alphabet)+w[pos:]
            elif op==2 and len(w)>1:
                w=w[:pos]+w[pos+1:]
        recent.append(w);out.append(w)
    return out,dict(initial_words=recent[:4],window=config['copy_window'],mutation_probability=config['copy_mutation_probability'])

def grille(n,rng,config):
    tables=[['','q','o','ch','sh','d','y','s'],['a','e','ee','ai','ii','o','ch','ck'],['l','r','n','dy','in','y','s','m']]
    cells=[a+b+c for a in tables[0] for b in tables[1] for c in tables[2]]
    rng.shuffle(cells)
    stride=config['grille_stride']
    if math.gcd(stride,len(cells))!=1:
        raise ValueError('Grille stride must be coprime to table size')
    offset=rng.randrange(len(cells))
    return [cells[(offset+i*stride)%len(cells)] for i in range(n)],dict(tables=tables,stride=stride,offset=offset,period=len(cells),cell_order=cells)

def expansive(words,rng,config,sequence_length=3,slot_rigidity=.5):
    """C12: decompose EVERY atomic C5 shorthand symbol into fixed stroke sequences.

    Source characters including abbreviation marks are treated as atomic signs.
    Sequence length is fixed per setting. Rigidity fixes floor(r*(L-1)) slots
    to a shared stroke; each remaining slot has an independent permutation of
    the sign inventory. Every designated variable slot actually varies across
    signs. One variable slot always remains; no sign collisions.
    The alphabet is C5's own sign inventory, used here as abstract strokes.
    This is a synthetic decomposition test, not a historical shorthand claim.
    """
    if sequence_length<2 or not 0<=slot_rigidity<=1:
        raise ValueError('C12 requires length>=2 and 0<=rigidity<=1')
    shorthand,meta=encode(words,'C5',rng,config)
    signs=sorted(set(''.join(shorthand)))
    strokes=signs[:];rng.shuffle(strokes)
    fixed=int(slot_rigidity*(sequence_length-1))
    slots=list(range(sequence_length));rng.shuffle(slots)
    shared=set(slots[:fixed]);variable=[i for i in range(sequence_length) if i not in shared]
    permutations={}
    for slot in variable:
        order=list(range(len(signs)));rng.shuffle(order);permutations[slot]=order
    code={}
    for index,sign in enumerate(signs):
        sequence=[strokes[0]]*sequence_length
        for slot in variable:sequence[slot]=strokes[permutations[slot][index]]
        code[sign]=''.join(sequence)
    assert len(set(code.values()))==len(signs)
    return [''.join(code[c] for c in w) for w in shorthand],dict(
        **meta,sequence_length=sequence_length,slot_rigidity=slot_rigidity,
        shared_slots=sorted(shared),codebook=code,all_signs_decomposed=True)
