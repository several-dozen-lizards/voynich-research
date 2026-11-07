import sys
import unittest
import random
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.metrics import conditional,mi,measure
from src.noise import alignment_ops,inject
from src.parse_ivtff import parse,edit_distance
from src.tokenize import tokenize_line,train_bpe
from src.phase3 import ROOT,load_words,ordinary,splits,rng_for
from src.encoders import encode,self_citation,grille
import json

class Phase3Tests(unittest.TestCase):
    def test_label_does_not_destroy_paragraph(self):
        rows=parse(ROOT/'data/raw/ZL3b-n.txt','ZL')
        byid={r['line_id']:r for r in rows}
        self.assertEqual(byid['f11v.6']['line_index_in_paragraph'],4)
        self.assertEqual(byid['f49v.4']['line_index_in_paragraph'],1)
        self.assertIsNone(byid['f49v.3']['line_index_in_paragraph'])
        self.assertIsNone(byid['f68r1.5']['line_index_in_paragraph'])
        config=json.loads((ROOT/'configs/phase3.json').read_text())
        self.assertTrue(all(r['line_index_in_paragraph'] is not None for r in rows if ordinary(r,config)))

    def test_tokenizer_greedy_and_no_cross_word(self):
        self.assertEqual(tokenize_line('aiin cthy','T2',['ii','iin','aiin','cth']),['aiin',' ','cth','y'])
        merges=train_bpe(['abc']*10+['de']*2,2)
        self.assertEqual(merges,[('a','b'),('ab','c')])
        self.assertEqual(tokenize_line('abc abc','T2',merges=merges),['abc',' ','abc'])
        self.assertEqual(tokenize_line('ab cd','T3'),['ab','cd'])

    def test_entropy_known_processes_and_no_locus_bridge(self):
        value,support=conditional([list('abababab')],1)
        self.assertEqual(value,0)
        self.assertEqual(support,7)
        self.assertEqual(conditional([['a'],['b']],1),(None,0))
        self.assertAlmostEqual(mi(Counter({('a',0):10,('b',1):10})),1)
        self.assertAlmostEqual(mi(Counter({('a',0):10,('a',1):10,('b',0):10,('b',1):10})),0)

    def test_traceback_matches_exact_distance(self):
        rng=random.Random(117)
        for _ in range(100):
            a=''.join(rng.choices('abc ',k=rng.randrange(30)))
            b=''.join(rng.choices('abc ',k=rng.randrange(30)))
            ops,dist=alignment_ops(a,b)
            self.assertEqual(sum(ops.values()),dist)
            self.assertEqual(dist,edit_distance(a,b))
        self.assertEqual(alignment_ops('ab','ac')[0],Counter(substitution=1))
        self.assertEqual(alignment_ops('a','ab')[0],Counter(insertion=1))

    def test_noise_rates_and_determinism(self):
        text='ab '*30000
        rates=dict(substitution=.02,insertion=.01,deletion=.01)
        a,ops,raw=inject(text,rates,'ab',random.Random(81))
        self.assertEqual((a,ops,raw),inject(text,rates,'ab',random.Random(81)))
        for op,rate in rates.items():self.assertLess(abs(ops[op]/len(text)-rate),.003)

    def test_sources_long_enough_and_encoders_seeded(self):
        config=json.loads((ROOT/'configs/phase3.json').read_text())
        sources={c:load_words(spec,34509)[0] for c,spec in config['source_slices'].items()}
        for mode in ['C4','C5','C6','C7']:
            a,meta=encode(sources['C1'][:300],mode,rng_for(1729,mode),config)
            self.assertEqual((a,meta),encode(sources['C1'][:300],mode,rng_for(1729,mode),config))
            self.assertEqual(len(a),300)
            self.assertTrue(all(w and ' ' not in w for w in a))
        for fn in [self_citation,grille]:
            self.assertEqual(fn(100,random.Random(1729),config),fn(100,random.Random(1729),config))

if __name__=='__main__':unittest.main()
