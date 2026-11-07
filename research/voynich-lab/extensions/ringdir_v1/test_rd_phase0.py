"""Authored engineering controls; never load manuscript words or fit calibration data."""
import math
import random
import unittest
from collections import Counter

import rd_phase0 as rd


class Mechanics(unittest.TestCase):
    def test_closed_pair_cancellation_and_open_path(self):
        c = Counter({('a','b'): 8})
        self.assertAlmostEqual(rd.direction(['a','b'], c, 'circular')[0], 0)
        self.assertGreater(rd.direction(['a','b'], c, 'radial')[0], 0)
        self.assertEqual(rd.direction(['a'], c, 'radial'), (0.,0.))

    def test_closed_reversal_antisymmetry(self):
        c = Counter({('a','b'): 8, ('b','c'): 4, ('c','a'): 2})
        for kind in ['radial','circular']:
            a = rd.direction(['a','b','c'], c, kind)[0]
            b = rd.direction(['c','b','a'], c, kind)[0]
            self.assertAlmostEqual(a, -b)
            self.assertGreater(a, 0)

    def test_unseen_pair_and_tie(self):
        self.assertEqual(rd.direction(['new','word','here'], Counter(), 'circular')[0], 0)
        self.assertEqual(rd.sign(0), 0)
        self.assertEqual(rd.sign(1e-13), 0)

    def test_split_family(self):
        self.assertEqual(rd.family('f72r1'), rd.family('f72v3'))
        self.assertEqual(rd.family('fRos'), rd.family('f86v4'))
        self.assertNotEqual(rd.family('f12r'), rd.family('f13r'))

    def test_true_gap_coordinates_for_all_reversals_rotations(self):
        # Recover all authored original forward-oriented boundaries after each transform.
        words, boundaries, n = ['a','b','c','d','e','f'], [0,3], 6
        for reverse in [False, True]:
            for rotation in range(n):
                seq = list(reversed(words)) if reverse else words[:]
                seq = seq[rotation:]+seq[:rotation]
                gaps = [((n-b if reverse else b)-rotation)%n for b in boundaries]
                for b, gap in zip(boundaries,gaps):
                    oriented_pair = (seq[gap],seq[gap-1]) if reverse else (seq[gap-1],seq[gap])
                    self.assertEqual(oriented_pair, (words[b-1],words[b]))

    def test_boundary_null_chance_union(self):
        self.assertEqual(len(rd.window_union([0],3)),3)
        self.assertEqual(len(rd.window_union([0,3],6)),6)
        self.assertEqual(len(rd.window_union([0,10],20)),10)

    def test_partial_line_cannot_make_wrap_boundary(self):
        run = [[dict(id='x', family='x', scribe='',section='',words=['a']*4),
                dict(id='y', family='x', scribe='',section='',words=['b']*4)]]
        c = rd.candidates(run,6)[0]
        self.assertEqual(c['boundaries'],[4])
        c = rd.candidates(run,8)[0]
        self.assertEqual(c['boundaries'],[0,4])

    def test_units_preserve_multicharacter_rendering(self):
        self.assertEqual(rd.units('qochaiin'), ['qo','ch','aiin'])
        u = rd.units('hc')
        self.assertEqual(list(reversed(list(reversed(u)))), u)
        # Serializing and reparsing a reversed unit list can merge h+c into ch.
        self.assertNotEqual(rd.units(''.join(reversed(u))), list(reversed(u)))

    def test_independent_joint_ratio(self):
        c = Counter({('a','b'):3, ('b','a'):1})
        expected = math.log(3.5)-math.log(1.5)
        self.assertAlmostEqual(rd.direction(['a','b'], c, 'radial')[0], expected)

    def test_group_bootstrap_and_support_do_not_inflate_repeats(self):
        rows = [dict(family='f', source='line',n=10,x=1)]*100
        self.assertEqual(rd.support(rows),(1,1))
        self.assertEqual(rd.bootstrap(rows,'x',5),[1.,1.])


if __name__ == '__main__':
    unittest.main()
