import unittest,itertools,math
from core import *
class Tests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(hebrew('מֶלֶךְ <sup>42</sup> אב<i class="footnote">תוכן</i>'),['מלכ','אב'])
    def test_decoder_exhaustive(self):
        m=Model([['אב','גד','בא'],['בא','גד','אב']]*30+[['אב','בא','גד']]*5)
        key={x:x for x in HEB};words=['בא','דג','אב'];mapped,cs,out,score=m.decode(words,key)
        opts=list(itertools.product(*cs));best=max(m.lm.score(list(x)) for x in opts)
        self.assertAlmostEqual(score,best);self.assertTrue(all(0<=math.exp(m.lm.logp(*x))<=1 for x in [('אב','בא','גד'),(BOS,BOS,'אב')]))
    def test_all_variants_conserve(self):
        rs=[dict(text_eva='ab c',line_id='1'),dict(text_eva='dd e f',line_id='2')]
        expected=sorted(['ab','c','dd','e','f'])
        for v in VARIANTS:
            obs=[t['word'][::-1] if v[0]=='RTL' else t['word'] for u in traverse(rs,v) for t in u]
            self.assertEqual(sorted(obs),expected)
    def test_anagram_invariance(self):
        m=Model([['אב','גד','בא']]*20+[['בא','גד','אב']]*10);key={x:x for x in HEB}
        a=m.decode(['אב','גד','בא'],key);b=m.decode(['בא','דג','אב'],key)
        self.assertEqual(a[1:],b[1:])
    def test_known_key_fitter(self):
        seqs=[['אב','גד','בא'],['בא','גד','אב']]*30+[['אב','אב','גד']]*10
        m=Model(seqs);enc={'א':'x','ב':'y','ג':'z','ד':'q'}
        cipher=[[''.join(enc[c] for c in w) for w in s] for s in seqs]
        key,receipt=fit(cipher,m)
        self.assertTrue(all(alpha(''.join(key[c] for c in w)) in m.lex for s in cipher for w in s))
        self.assertGreaterEqual(receipt['objective'],receipt['initial_objective'])
if __name__=='__main__':unittest.main()
