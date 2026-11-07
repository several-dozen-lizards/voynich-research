"""Authored controls only; no calibration or manuscript outcomes loaded."""
import math
import random
import unittest
from collections import Counter
import run_v2 as v


class Controls(unittest.TestCase):
    def test_direction_both_signals_reverse_word_order(self):
        words=['cham','qody','sheol','daiin']
        word=Counter(zip(words,words[1:]))
        glyph=Counter((v.rd.units(a)[-1],v.rd.units(b)[0]) for a,b in zip(words,words[1:]))
        for sig,model in [('word',word),('glyph',glyph)]:
            a=v.dscore(words,model,sig)[0];b=v.dscore(list(reversed(words)),model,sig)[0]
            self.assertAlmostEqual(a,-b)
            self.assertGreater(a,0)
            self.assertAlmostEqual(v.dscore(words[1:]+words[:1],model,sig)[0],a)

    def test_two_word_cycle_and_unseen_tie(self):
        for sig in ['word','glyph']:
            self.assertEqual(v.dscore(['a','b'],Counter({('a','b'):8}),sig)[0],0)
            self.assertEqual(v.dscore(['a'],Counter(),sig)[0],0)

    def test_unknown_barrier_no_promoted_neighbors(self):
        c=Counter({('a','b'):100})
        self.assertEqual(v.dscore(['a','\ufffd','b'],c,'word')[1],1/3)
        # Only b→a is an actual cyclic edge; a→b is not promoted across the barrier.
        expected=-math.log(100.5/.5)/3
        self.assertAlmostEqual(v.dscore(['a','\ufffd','b'],c,'word')[0],expected)
        data={'train':[[{'words':['a','\ufffd','b']}]]}
        self.assertEqual(v.fit_models(data)['word'],Counter())

    def test_complete_paragraph_requires_both_boundaries(self):
        def line(i,start=False,end=False):
            return dict(id=str(i),folio='f1r',family='1',index=i,start=start,end=end,words=['a']*12)
        good=[line(0,True),line(1,end=True)]
        self.assertEqual(len(v.complete_paragraphs(good)),1)
        self.assertEqual(v.complete_paragraphs([line(0),line(1,end=True)]),[])
        self.assertEqual(v.complete_paragraphs([line(0,True),line(2,end=True)]),[])

    def test_peak_zero_plateau_and_circular_separation(self):
        self.assertEqual(v.seam_counts([0]*10,1),0)
        self.assertEqual(v.seam_counts([2,2,0,0,0,0,0,0,0,2],1),1)
        self.assertEqual(v.seam_counts([3,0,3,0,0,0,0,0,0,0],1),1)
        self.assertEqual(v.seam_counts([3,0,0,0,3,0,0,0,0,0],1),2)

    def test_shared_signal_generation_seed(self):
        a=v.OUT/'D/ZL/word';b=v.OUT/'D/ZL/glyph'
        self.assertEqual(v.shared_namespace(a),v.shared_namespace(b))

    def test_lossless_latin_display_inverse_does_not_mask_letter_z(self):
        inverse={v:k for k,v in {'w':'x','x':'y','y':'z','z':'\ufffd'}.items()}
        text='xyz\ufffd'
        decoded=''.join(inverse.get(c,c) for c in text)
        self.assertEqual(decoded,'wxyz')
        self.assertFalse(v.badword(decoded))

    def test_family_block_boundary_breaks_paragraph(self):
        a=dict(id='a',folio='f1r',family='block1',index=0,start=True,end=False,words=['a']*12)
        b=dict(id='b',folio='f1r',family='block2',index=1,start=False,end=True,words=['a']*12)
        self.assertEqual(v.complete_paragraphs([a,b]),[])

    def test_pooled_family_aggregation(self):
        words=[['a','b','c']]*8
        c=Counter({('a','b'):10,('b','c'):10,('c','a'):10})
        result=v.pooled_stat(words,[str(i) for i in range(8)],c,'word',42)
        self.assertEqual(result['weighted_call'],1)
        self.assertEqual(result['unweighted_call'],1)
        onefamily=v.pooled_stat(words,['same']*8,c,'word',42)
        self.assertEqual(onefamily['weighted_call'],0)

    def test_sealed_transform_known_gap(self):
        for seed in range(20):
            c=dict(words=[str(i) for i in range(23)],boundaries=[0],source='toy',family='toy')
            s,k=v.transform(c,'toy',random.Random(seed))
            w=s['words'];gap=k['boundaries'][0]
            self.assertEqual(w[gap-1] if k['reverse'] else w[gap],'0')


if __name__=='__main__':unittest.main()
