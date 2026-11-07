"""Engineering checks on invented data only; no empirical control measurements."""
import unittest
import run as p

class InstrumentTests(unittest.TestCase):
    def test_lossless(self):
        train=['qokchdy','cheey','foobar','ckheeeiii','abcabc']*6
        for method in p.METHODS:
            tok=p.Tokenizer(method,train)
            for word in train+['unseenΩ','sh','cfh','eeee']:
                self.assertEqual(''.join(tok.word(word)),word)
            self.assertEqual(tok.word('ckheeeiii'),('ckh','eee','iii')) if method=='T-Z' else None
            tok.word.cache_clear()
    def test_heldout_does_not_fit(self):
        tok=p.Tokenizer('T-MDL',['abcabc']*8)
        before=list(tok.merges)
        tok.word('zzzzzz')
        self.assertEqual(before,tok.merges)
        tok.word.cache_clear()
    def test_metric_notation(self):
        m=p.metrics([tuple('ab')]*20)
        self.assertAlmostEqual(m['h1'],1.)
        self.assertAlmostEqual(m['h2'],0.)
        self.assertAlmostEqual(m['positional_entropy'],0.)
    def test_merge_deterministic(self):
        words=[tuple('abc'),tuple('abd')]*10
        self.assertEqual(p.merge_fit(words),p.merge_fit(words))
    def test_boundary_no_space_credit(self):
        tok=p.Tokenizer('T-Z',['chch'])
        b=p.boundary(['chch'],[[0,0,1,1]],tok)
        self.assertEqual(b['f1'],1.)
        self.assertEqual(b['observable'],1)
        tok.word.cache_clear()
    def test_noise_truth_and_determinism(self):
        text='ab cd ef'; ids=[0,0,None,1,1,None,2,2]
        a=p.noise(text,ids,p.rng(1,'invented'))
        self.assertEqual(a,p.noise(text,ids,p.rng(1,'invented')))
        self.assertTrue(all(len(w)==len(t) for w,t in zip(*a)))
    def test_split_group_separation(self):
        rows=[dict(text_eva='ab cd',group=str(i//2)) for i in range(20)]
        _,_,_,s=p.split_noise(rows,1)
        self.assertFalse(set(s['train_groups'])&set(s['test_groups']))
    def test_literal_anchor(self):
        m=p.metrics([tuple('abab')]*20)
        b=p.band([m]*20)
        self.assertTrue(p.inside(m,b))
        broken=dict(m,h1=999.)
        self.assertFalse(p.inside(broken,b))

if __name__=='__main__': unittest.main()
