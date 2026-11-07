import math,unittest
from arithmetic_reference import SyntheticTable as T,SyntheticFixture as F,mh_reference,availability_reference

def fixture(*rows):return F('synthetic',tuple(T(str(i),*r) for i,r in enumerate(rows)))

class ArithmeticTests(unittest.TestCase):
    def test_hand_calculated_single_table(self):
        r=mh_reference(fixture((8,2,4,6)));self.assertEqual(r['exact_or'],['6','1']);self.assertAlmostEqual(r['log_or'],math.log(6))
    def test_stratification_can_reverse_aggregate_direction(self):
        r=mh_reference(fixture((81,6,234,36),(192,71,55,25)))
        pooled=mh_reference(fixture((273,77,289,61)))
        self.assertGreater(r['log_or'],0);self.assertLess(pooled['log_or'],0)
    def test_exposure_swap_negates_log_effect(self):
        a=mh_reference(fixture((8,2,4,6),(3,8,4,9)))['log_or'];b=mh_reference(fixture((4,6,8,2),(4,9,3,8)))['log_or']
        self.assertAlmostEqual(a,-b)
    def test_common_count_scaling_and_stratum_order_preserve_effect(self):
        a=mh_reference(fixture((8,2,4,6),(3,8,4,9)));b=mh_reference(fixture((30,80,40,90),(80,20,40,60)))
        self.assertEqual(a['exact_or'],b['exact_or'])
    def test_empty_and_constant_margin_strata_do_not_invent_support(self):
        r=mh_reference(fixture((0,0,0,0),(1,2,0,0),(3,0,4,0)))
        self.assertEqual(r['status'],'NO_INFORMATION');self.assertIsNone(r['log_or']);self.assertEqual(r['informative_strata'],0)
        self.assertEqual([x['status'] for x in r['strata']],['EMPTY','NO_EXPOSURE_CONTRAST','NO_OUTCOME_VARIATION'])
    def test_zero_cells_do_not_automatically_destroy_pooled_support(self):
        r=mh_reference(fixture((0,3,4,0),(5,0,0,6)))
        self.assertEqual(r['status'],'FINITE');self.assertEqual(r['informative_strata'],2)
    def test_separation_retains_extended_results_without_half_counts(self):
        self.assertEqual(mh_reference(fixture((4,0,0,5)))['status'],'POSITIVE_INFINITY')
        self.assertEqual(mh_reference(fixture((0,4,5,0)))['status'],'NEGATIVE_INFINITY')
    def test_invalid_counts_duplicate_strata_and_scientific_inputs_rejected(self):
        for n in (-1,.5,True):
            with self.assertRaises(ValueError):T('s',n,1,1,1)
        with self.assertRaises(ValueError):F('s',(T('same',1,1,1,1),T('same',1,1,1,1)))
        with self.assertRaises(TypeError):mh_reference([['manuscript','words']])
        with self.assertRaises(ValueError):F('s',(),provenance='generator_output')
    def test_near_unity_effect_does_not_round_to_null(self):
        n=10**100;r=mh_reference(fixture((n+1,n,1,1)))
        self.assertEqual(r['status'],'FINITE');self.assertGreater(r['log_or'],0);self.assertAlmostEqual(r['log_or']/1e-100,1)
    def test_unrepresentable_nonnull_effect_is_not_reported_as_zero(self):
        n=10**400;r=mh_reference(fixture((n+1,n,1,1)))
        self.assertEqual(r['status'],'NUMERIC_RANGE');self.assertIsNone(r['log_or'])
    def test_exact_null_h2_denominator_remains_undefined(self):
        r=availability_reference(fixture((10,10,10,10)),fixture((4,1,1,1)))
        self.assertEqual(r['ratio_status'],'ZERO_AGGREGATE_LOG_EFFECT');self.assertIsNone(r['log_effect_ratio']);self.assertAlmostEqual(r['log_effect_difference_diagnostic'],math.log(4))
    def test_literal_log_ratio_is_not_ratio_of_odds_ratios(self):
        r=availability_reference(fixture((10,10,5,10)),fixture((4,1,1,2)))
        self.assertAlmostEqual(r['log_effect_ratio'],3);self.assertNotEqual(r['log_effect_ratio'],4)
        self.assertAlmostEqual(r['log_effect_difference_diagnostic'],math.log(4))
    def test_availability_subset_constraint(self):
        with self.assertRaises(ValueError):availability_reference(fixture((1,1,1,1)),fixture((2,1,1,1)))
        with self.assertRaises(ValueError):availability_reference(F('a',(T('page1',3,3,3,3),)),F('b',(T('page2',1,1,1,1),)))
    def test_h2_separation_does_not_get_finite_ratio(self):
        r=availability_reference(fixture((10,10,5,10)),fixture((4,0,0,1)))
        self.assertEqual(r['ratio_status'],'NONFINITE_OR_UNSUPPORTED_EFFECT');self.assertIsNone(r['log_effect_ratio'])
    def test_tiny_opposite_effects_keep_direction_reversal(self):
        n=10**200;r=availability_reference(fixture((n,n+1,1,1)),fixture((n-1,n-2,1,1)))
        self.assertEqual(r['interpretation'],'DIRECTION_REVERSAL');self.assertLess(r['log_effect_ratio'],0)
    def test_h2_ratio_orientation_invariance_and_difference_sign(self):
        a=availability_reference(fixture((10,10,5,10)),fixture((4,1,1,2)))
        b=availability_reference(fixture((5,10,10,10)),fixture((1,2,4,1)))
        self.assertAlmostEqual(a['log_effect_ratio'],b['log_effect_ratio'])
        self.assertAlmostEqual(a['log_effect_difference_diagnostic'],-b['log_effect_difference_diagnostic'])

if __name__=='__main__':unittest.main(verbosity=2)
