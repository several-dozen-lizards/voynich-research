import copy, itertools, json, math, random, unittest
from pathlib import Path
from harness import *
P=Path(__file__).parent

class HarnessTests(unittest.TestCase):
    def setUp(self):self.k=json.loads((P/'KNOWN-KEY.json').read_text())
    def test_exact_roundtrip_context(self):
        self.assertEqual(decode_word(['INIT_A','ub'],self.k),'ab')
        self.assertEqual(decode_word(['INIT_A'],self.k),'a')
        self.assertEqual(decode_word(['ub','INIT_A'],self.k),'bz')
    def test_unknown_not_promoted(self):
        self.assertIsNone(decode_word(['?'],self.k));self.assertIsNone(decode_word(None,self.k))
    def test_conflicting_context_abstains(self):
        self.k['rules'].append({'unit':'INIT_A','when':{'position':'first'},'value':'e','source':'test'})
        self.assertIsNone(decode_word(['INIT_A','ub'],self.k))
    def test_random_complexity_and_multisets(self):
        for seed in range(40):
            k=random_key(self.k,random.Random(seed))
            self.assertEqual(complexity(k),complexity(self.k));self.assertEqual(Counter(k['map'].values()),Counter(self.k['map'].values()))
            self.assertEqual(Counter(x['value'] for x in k['rules']),Counter(x['value'] for x in self.k['rules']))
            self.assertEqual([x['when'] for x in k['rules']],[x['when'] for x in self.k['rules']])
    def test_custody_fails_closed(self):
        with self.assertRaises(NotTestable):custody_check(self.k,[],[{'id':'new','folio':'f1r','words':[]}])
        with self.assertRaises(NotTestable):custody_check(self.k,[],[{'id':'new','folio':'f72v2','custody':'demonstrated_unbuilt','words':[]}])
        with self.assertRaises(NotTestable):custody_check(self.k,[],[{'id':self.k['built_on'][0],'words':[],'custody':'demonstrated_unbuilt'}])
    def test_no_implicit_key_exposure(self):
        del self.k['process_evidence']
        with self.assertRaises(NotTestable):validate_key(self.k)
    def test_minimum_baseline(self):
        with self.assertRaises(NotTestable):evaluate(self.k,[],[],[],{}, {},n_random=999)
    def test_normalized_distance_independent(self):
        strings=[''.join(z) for n in range(5) for z in itertools.product('ab',repeat=n)]
        for a in strings:
            for b in strings:
                self.assertAlmostEqual(ned(a,b),Levenshtein.normalized_distance(a,b))
                fast=process.extractOne(a,[b],scorer=Levenshtein.normalized_distance,score_cutoff=.25)
                self.assertEqual(fast is not None,ned(a,b)<=.25)
    def test_word_shuffle_barriers(self):
        rows=[{'words':[['a'],['b'],None,['c'],['d']]}];z=shuffle_lines(rows,random.Random(4))
        self.assertIsNone(z[0]['words'][2]);self.assertEqual(Counter(tuple(x) for x in z[0]['words'][:2]),Counter([('a',),('b',)]))
    def test_glyph_position_preserved(self):
        rows=[{'words':[list('abcdef'),None,list('ab')]}];z=shuffle_glyphs(rows,random.Random(7))
        self.assertEqual(z[0]['words'][0][0],'a');self.assertEqual(z[0]['words'][0][-1],'f');self.assertEqual(Counter(z[0]['words'][0]),Counter('abcdef'));self.assertIsNone(z[0]['words'][1])
    def test_rate_bits_finite_at_edges(self):
        self.assertTrue(math.isfinite(signed_binomial_bits(10,10,.5/11)));self.assertLess(signed_binomial_bits(0,10,.5),0)
    def test_paired_requires_both(self):
        self.assertEqual(paired_verdict({'single_reading_verdict':'PASS'},{'single_reading_verdict':'FAIL'}),'PARTIAL')
    def test_unknown_lm_no_favourable_deletion(self):
        lm=LM([['abc','abc']],list('abc'));loss,n,why=lm.loss([['abc',None,'abc']]);self.assertIsNone(loss);self.assertEqual(why,'ambiguous-or-unknown-token')
    def test_e6_context_dependence(self):
        r=[{'id':'x','words':[['INIT_A','ub'],['INIT_A','ub']]}]
        score=raw_scores(self.k,[],r,[['ab']],{})
        self.assertEqual(score['E6']['consistent_types'],1)

if __name__=='__main__':unittest.main(verbosity=2)
