from pathlib import Path
import unittest
from registry import produce
from core import group_inventory
from published_g5 import run_published
from held import score,ClaimLocked

class RegistryTests(unittest.TestCase):
    def test_G1_integrated_map(self):
        inventory=group_inventory(['qokedy','chedy','shedy','qockheer']*20)
        out=produce('G1',{},8,source_words=['ab','ac'],inventory=inventory,line_lengths=[3,4])
        self.assertEqual([len(line) for line in out['lines']],[3,4])
        self.assertEqual([w for line in out['lines'] for w in line],[''.join(g) for g in out['mapped_unit_groups']])

    def test_G5_published_entry_and_native_layout(self):
        with self.assertRaises(ValueError):produce('G5',{},19,line_lengths=[4]*5)
        out=produce('G5',{},19,line_count=20)
        self.assertTrue(out['published_source'])
        self.assertEqual(len(out['lines']),19)
        self.assertTrue(out['seed_line_excluded'])

    def test_G5_corpus_table_option_rejected(self):
        with self.assertRaises(ValueError):run_published('forbidden',overrides={'method.canFollow':'voynich'})

    def test_held_still_locked(self):
        with self.assertRaises(ClaimLocked):score(Path(__file__).resolve().parent,'H3',[])

if __name__=='__main__':unittest.main(verbosity=2)
