"""Invented engineering fixtures only; no new control measurement before seal."""
import unittest
import run as a

class AmendmentTests(unittest.TestCase):
    def test_continuous_transition(self):
        m=a.continuous([list('abab')])
        self.assertEqual(m['adjacent_pairs'],3)
        self.assertAlmostEqual(m['h1'],1.)
        self.assertAlmostEqual(m['h2'],0.)
        self.assertEqual(a.continuous([list('ab'),list('ab')])['adjacent_pairs'],2)
    def test_restore_unchanged(self):
        for method in a.p.METHODS:
            t=a.p.Tokenizer(method,['abcabc','qokchdy','ckheeeiii']*5)
            r=a.restore(method,t.meta)
            for w in ['abcabc','ckheeeiii','qokchdy','unknownΩ']:
                self.assertEqual(t.word(w),r.word(w))
            t.word.cache_clear()
    def test_joint_self_coverage(self):
        vectors=[dict(valid=True,**{k:float((i*(j+1))%23+j) for j,k in enumerate(a.KEYS)}) for i in range(100)]
        b=a.joint_band(vectors)
        self.assertGreaterEqual(b['self_coverage'],.95)
        self.assertEqual(sum(a.inside(v,b) for v in vectors)/100,b['self_coverage'])
    def test_binomial(self):
        b=a.expectation(.95)
        self.assertEqual(b['expected_successes'],19)
        self.assertGreater(b['probability_at_least_16'],.99)
        self.assertAlmostEqual(b['probability_at_least_16']+b['probability_below_16'],1.)
    def test_invalid_cannot_pass(self):
        self.assertIsNone(a.distance(dict(valid=False),{}))

if __name__=='__main__': unittest.main()
