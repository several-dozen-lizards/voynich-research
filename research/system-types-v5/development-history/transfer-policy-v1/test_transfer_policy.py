from dataclasses import asdict
from unittest.mock import patch
import unittest
from core import group_inventory,canonical_hash
from transfer_policy import (fit_development_codebook,transfer_slots,source_runs,sample_window,SourceSupportError)
from GENERATORS import generate
from registry import produce

class TransferPolicyTests(unittest.TestCase):
    def inventory(self):return group_inventory(['qokedy','chedy','shedy','qockheer']*20)

    def book(self):return fit_development_codebook([['a','b'],['a','c']]*20,self.inventory(),'development')

    def test_fitting_reserves_or_calibration_is_rejected(self):
        for scope in ('reserve','calibration','primary-representation',''):
            with self.assertRaises(SourceSupportError):fit_development_codebook([['a']],self.inventory(),scope)

    def test_unknown_words_keep_slots_and_do_not_promote_neighbors(self):
        book=self.book();view=transfer_slots([['a'],['a','NEW'],['b']],book)
        self.assertEqual(len(view['tokens']),3);self.assertIsNone(view['tokens'][1])
        self.assertEqual(view['events'][0]['slot'],1)
        self.assertEqual(view['primary_transfer_status'],'NOT_ESTIMABLE_FULL_TRANSFER')
        self.assertIsNone(transfer_slots([None,['a']],book)['tokens'][0])

    def test_transfer_never_calls_mapping_estimator(self):
        book=self.book();before=canonical_hash(asdict(book))
        with patch('transfer_policy.group_rank_mapping',side_effect=AssertionError('reserve fit attempted')):
            transfer_slots([['a'],['UNSEEN']],book)
            transfer_slots([['UNSEEN']]*100,book)
        self.assertEqual(canonical_hash(asdict(book)),before)
        mutated=book.mapping;mutated['UNSEEN']='q'
        self.assertNotIn('UNSEEN',book.mapping)

    def test_work_boundaries_cannot_be_stitched(self):
        units=[dict(unit='work1',words=['a','b']),dict(unit='work2',words=['c','d'])]
        runs=source_runs(units,['work1','work2'],'Occitan')
        self.assertEqual(len(runs),2)
        with self.assertRaises(SourceSupportError):sample_window(runs,3,1)

    def test_source_gaps_cannot_be_bridged(self):
        units=[dict(unit=x,words=[x]) for x in ('chapter1','chapter2','chapter3')]
        runs=source_runs(units,['chapter1','chapter3'],'Latin')
        with self.assertRaises(SourceSupportError):sample_window(runs,2,1)

    def test_each_eligible_start_and_final_position(self):
        runs=[dict(work='small',units=['s'],tokens=['x','y']),dict(work='big',units=['b'],tokens=['a','b','c','d','e'])]
        for start in range(3):
            with patch('transfer_policy.random.Random') as cls:
                cls.return_value.randrange.return_value=start
                result=sample_window(runs,3,999)
                cls.return_value.randrange.assert_called_once_with(3)
                self.assertEqual(result['start'],start)
                self.assertEqual(result['tokens'],['a','b','c','d','e'][start:start+3])

    def test_original_unknown_slots_count_toward_source_budget(self):
        runs=[dict(work='w',units=['u'],tokens=['a','b','c','d'])]
        # Four known target words plus one original unknown still require five positions.
        with self.assertRaises(SourceSupportError):sample_window(runs,5,1)

    def test_registry_rejects_short_source_before_generator(self):
        with patch('registry.generate',side_effect=AssertionError('generator was invoked')):
            with self.assertRaisesRegex(ValueError,'SOURCE_TOO_SHORT'):
                produce('G1',{},1,source_words=['ab']*4,inventory=self.inventory(),line_lengths=[5])

    def test_registry_rejects_wrap_override(self):
        with self.assertRaisesRegex(ValueError,'wrapping'):
            produce('G1',{'allow_source_wrap':True},1,source_words=['ab']*5,inventory=self.inventory(),line_lengths=[4])

    def test_all_bounded_generator_seeds_use_contiguous_source(self):
        source=['alpha','beta','gamma','delta','epsilon','zeta','eta','theta']
        for seed in range(100):
            result=generate('G1',{'allow_source_wrap':False},seed,source=source,line_lengths=[3,2])
            emitted=[''.join(w) for line in result['lines'] for w in line]
            start=result['source_offset']
            self.assertEqual(emitted,source[start:start+5]);self.assertEqual(result['source_wraps'],0)
            self.assertLessEqual(start+5,len(source))

    def test_exact_source_budget_uses_each_position_once(self):
        result=generate('G1',{'allow_source_wrap':False},3,source=['a','b','c'],line_lengths=[3])
        self.assertEqual(result['source_offset'],0)
        self.assertEqual(result['source_wraps'],0)
        with self.assertRaisesRegex(ValueError,'SOURCE_TOO_SHORT'):
            generate('G1',{'allow_source_wrap':False},3,source=['a','b'],line_lengths=[3])

if __name__=='__main__':unittest.main(verbosity=2)
