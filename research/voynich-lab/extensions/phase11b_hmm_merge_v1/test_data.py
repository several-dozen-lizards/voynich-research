import unittest
import data as d
import hmm as h

class AlignmentTests(unittest.TestCase):
    def test_per_letter_recovery(self):
        # Two glyphs per source letter, one decoded state per glyph chunk.
        z=h.np.array([0,0,1,1,0,0])
        oracle=dict(unit=h.np.arange(6),instance=h.np.array([0,0,1,1,2,2]),true=h.np.array([2,4,2]))
        r=d.recovery(z,oracle,2)
        self.assertEqual(r['many_to_one_accuracy'],1.)
        self.assertEqual(r['v_measure'],1.)
    def test_collapsed_chunk_cannot_recover_all_letters(self):
        z=h.np.array([0])
        oracle=dict(unit=h.np.array([0,0]),instance=h.np.array([0,1]),true=h.np.array([2,4]))
        r=d.recovery(z,oracle,1)
        self.assertEqual(r['many_to_one_accuracy'],.5)
        self.assertEqual(r['v_measure'],0.)
    def test_missing_is_incorrect(self):
        oracle=dict(unit=h.np.array([0]),instance=h.np.array([0]),true=h.np.array([2,4]))
        r=d.recovery(h.np.array([0]),oracle,1)
        self.assertEqual(r['many_to_one_accuracy'],.5)
        self.assertEqual(r['deleted_instances'],1)
    def test_prefix_alignment(self):
        rows=[dict(text_eva='ab cd ef',labels=list(range(8)),group='0')]
        clipped,n=d.truncate(rows,.5)
        self.assertEqual(n,1); self.assertEqual(clipped[0]['text_eva'],'ab')
        self.assertEqual(len(clipped[0]['labels']),2)

if __name__=='__main__': unittest.main()
