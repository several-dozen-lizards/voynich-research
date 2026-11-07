"""Small authored engineering fixtures only; not Phase0 power/calibration trials."""
import random
import unittest
from collections import Counter
import jx_phase0 as j


class Mechanics(unittest.TestCase):
    def test_render_and_mechanism_class_receipts(self):
        for mode in ['ZERO','REG','PROG','SS','EE','ORDER']:
            ws=j.toy(mode,12,random.Random(19))
            self.assertEqual(len(ws),12)
            self.assertTrue(all(j.units(w)==tuple(w) for w in ws))
            if mode=='REG':self.assertTrue(all(j.ALPHA.index(a[-1])//2==j.ALPHA.index(b[0])//2 for a,b in zip(ws,ws[1:])))
            if mode=='PROG':self.assertTrue(all(j.ALPHA.index(a[-1])//2==j.ALPHA.index(b[0])//2 for a,b in zip(ws,ws[1:])))

    def test_all_position_scores_reverse_word_order(self):
        train=[['ab','df','gl','ad','bf','ga']]*4
        models,meta,_=j.models_for(train)
        words=['ab','df','gl','ad']
        for key,model in models.items():
            a=j.pair_score(words,model,*key,meta)
            b=j.pair_score(list(reversed(words)),model,*key,meta)
            self.assertAlmostEqual(a,-b)

    def test_two_word_cycles_cancel(self):
        train=[['ab','df','gl']]
        models,meta,_=j.models_for(train)
        for key,model in models.items():self.assertAlmostEqual(j.pair_score(['ab','df'],model,*key,meta),0)

    def test_common_category_k_has_observed_tail(self):
        k,maps,diag=j.maps_for([['ab','cd','ef','ag']], 'codepoints')
        self.assertEqual(k,2)
        self.assertTrue(all(d['OTHER_mass']>0 for d in diag))

    def test_holm_and_finite_resolution(self):
        self.assertEqual(j.holm([.004,.009]),[True,True])
        self.assertEqual(j.holm([.006,.2]),[False,False])
        self.assertEqual(j.holm([.001,.5]),[True,False])
        self.assertEqual(j.holm([None,.001]),[False,False])

    def test_jsd_analytic_endpoints(self):
        np=j.np
        self.assertAlmostEqual(float(j.jsd_counts(np.array([2.,0.]),np.array([0.,2.]))),1)
        self.assertAlmostEqual(float(j.jsd_counts(np.array([2.,2.]),np.array([4.,4.]))),0)

    def test_synthetic_rewrite_does_not_empty_words_or_cross_block(self):
        result,log=j.rewrite(['am','dat','ea','a'],random.Random(1))
        self.assertEqual(result[0],'an')
        self.assertEqual(result[-1],'a')
        self.assertTrue(all(result))
        self.assertTrue(all(x['index']<3 for x in log))


if __name__=='__main__':unittest.main()
