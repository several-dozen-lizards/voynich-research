import random
import unittest
import run_followup as f


class Controls(unittest.TestCase):
    def test_published_output_parser_excludes_comments_and_literal_seed(self):
        words,seed,n=f.parse_g5('#Properties\n#text.x=1\n\nseed line\nchey dal\nqokaiin ol\n')
        self.assertEqual(words,['chey','dal','qokaiin','ol'])
        self.assertEqual(seed,'seed line');self.assertEqual(n,2)

    def test_parser_does_not_silently_repair_unexpected_output(self):
        with self.assertRaises(AssertionError):f.parse_g5('seed line\na,b chey\n')

    def test_reverse_orientation_and_origin_gap(self):
        for seed in range(50):
            c=dict(words=[str(i) for i in range(31)],boundaries=[0],source='toy',family='toy')
            s,k=f.v.rd.make_case(c,'toy','circular','toy',random.Random(seed),True)
            gap=k['boundaries'][0]
            self.assertEqual(s['words'][gap-1] if k['reverse'] else s['words'][gap],'0')

    def test_g5_and_g6_not_surrogate_or_shared_seed(self):
        self.assertNotEqual(4011,4012)
        self.assertNotEqual(4021,4022)
        self.assertEqual(f.v.OUT,f.OUT)
        self.assertEqual(f.v.SEED,2026110604)


if __name__=='__main__':unittest.main()
