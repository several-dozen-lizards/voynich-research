from pathlib import Path
import json
import math
import random
import tempfile
import unittest
from unittest.mock import patch
import core
from GENERATORS import generate, FAMILIES
from held import score, ClaimLocked, require_freeze
from abc_smc import run as smc, SimulationBudgetExceeded
from abc_rf import model_choice
import numpy as np
from scipy.stats import norm


class SandboxTests(unittest.TestCase):
    def test_token_barriers_and_readings(self):
        self.assertEqual(core.tokens('a.sh!edy.*.chedy.dar- #hi'), ['a', 'shedy', None, 'chedy', 'dar'])
        self.assertEqual(core.tokens('a.shedy,chedy.dar='), ['a', 'shedy', 'chedy', 'dar'])
        self.assertNotEqual(core.tokens('or.aiin'), core.tokens('oraiin'))

    def test_exclusion_precedes_tokenization(self):
        with tempfile.TemporaryDirectory() as folder:
            source, meta = Path(folder)/'test.evt', Path(folder)/'hands.csv'
            source.write_text('<f72v1.P.1;H>SECRET\n<f1r.P.1;H>a.*.b=\n<f1r.P.1;F>ab.b=', encoding='latin1')
            meta.write_text('Folio,Section,Scribe,Language\nf1r,Botanical,1,A\nf72v1,Zodiac,1,A\n', encoding='utf-8')
            original = core.tokens
            def checked(text):
                self.assertNotIn('SECRET', text)
                return original(text)
            with patch('core.tokens', checked):
                rows, manifest = core.load_evt(source, meta, verify_hashes=False)
            self.assertEqual(len(rows), 2)
            self.assertEqual(len(core.panels(rows)), 2)
            self.assertEqual(manifest['excluded_reserved_rows_by_reading'], {'H': 1})
            self.assertEqual(rows[0]['tokens'], ['a', None, 'b'])

    def test_source_mismatch_aborts(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'source'
            p.write_text('changed')
            with self.assertRaises(ValueError): core.load_evt(p, p)

    def test_generators_reproducible_nonempty(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                args = dict(source='recipe herba et eius sucus bonus est'.split(), line_lengths=(4, 6, 3, 7))
                result = generate(family, {}, 51, **args)
                self.assertEqual(result, generate(family, {}, 51, **args))
                self.assertEqual([len(line) for line in result['lines']], [4, 6, 3, 7])
                self.assertTrue(all(word for line in result['lines'] for word in line))

    def test_abbreviation_marks_are_units(self):
        result = generate('G2', {'abbreviation_probability': 1}, 1, source=['bonus'], line_lengths=(2,))
        self.assertEqual(result['lines'][0][0], ['b', 'o', 'n', '<SUP9>'])

    def test_verbose_expansion(self):
        plain = generate('G1', {}, 1, source=['abcdef'], line_lengths=(2,))
        verbose = generate('G4', {'null_probability': 1}, 1, source=['abcdef'], line_lengths=(2,))
        word=verbose['lines'][0][0]
        self.assertGreater(len(word), len(plain['lines'][0][0]))
        self.assertEqual(verbose['max_expansion'],3)

    def test_eva_group_segmentation_inventory_and_widths(self):
        self.assertEqual(core.eva_atoms('qockheeshy'), ['q','o','ckh','e','e','sh','y'])
        inventory=core.group_inventory(['qockheeshy','chedy','shedy','qokedy','qockheer']*20)
        self.assertNotIn('h', inventory['counts'])
        self.assertTrue(all(1<=len(core.eva_atoms(g))<=3 for g in inventory['counts']))
        source=[['x','y'],['x','z']]*20
        receipt=core.group_rank_mapping(source,inventory,required_widths={'x':1,'y':1,'z':1})
        self.assertTrue(all(len(core.eva_atoms(g))==1 for g in receipt['mapping'].values()))
        rendered=core.render_groups(source,receipt)
        self.assertEqual(rendered['words'], [''.join(g) for g in rendered['mapped_unit_groups']])
        with self.assertRaises(ValueError):core.render_groups([['UNSEEN']],receipt)

    def test_grille_independent_coordinate_oracle(self):
        table=[[f'p{r}{b}' if c==0 else f'm{r}{b}' if c==1 else f's{r}{b}' for b in range(3) for c in range(3)] for r in range(8)]
        result=generate('G6',{'table':table,'grille_offsets':[0,1,-1]},13,line_lengths=(5,4))
        for draw in result['draws']:
            self.assertEqual(draw['word'], ''.join(table[r][c] for r,c in draw['coordinates']))
            self.assertTrue(all(0<=r<8 and 0<=c<9 for r,c in draw['coordinates']))

    def test_copy_lineage_causal_and_windowed(self):
        result = generate('G5', {'window_lines': 2, 'mutation_probability': 0}, 9, line_lengths=(6,)*15)
        for event in result['lineage']:
            if event['parent_line'] is not None:
                self.assertTrue(1 <= event['line'] - event['parent_line'] <= 2)
                parent = ''.join(result['lines'][event['parent_line']][event['parent_word']])
                self.assertEqual(parent, event['parent'])
                self.assertEqual(event['child'], event['parent'])

    def test_mapping_deterministic_and_injective(self):
        source, target = ['abc', 'abd', 'adc'], ['xyz', 'xyw', 'xwz']
        receipt = core.rank_mapping(source, target)
        self.assertTrue(receipt['collision_free'])
        self.assertEqual(receipt, core.rank_mapping(source, target))
        mapped = core.apply_mapping(source, receipt)
        self.assertEqual(list(map(len, mapped)), list(map(len, source)))
        with self.assertRaises(ValueError): core.rank_mapping(['abc', 'def'], ['xy'])

    def test_fit_by_hand(self):
        result = core.fit_summary([['ab', 'ab'], ['aa', 'a']], alphabet=['a', 'b'])
        self.assertAlmostEqual(result['glyph:a'], 5/7)
        self.assertEqual(result['word_length:1'], .25)
        self.assertEqual(result['line_words:2'], 1)
        self.assertAlmostEqual(result['position:a:initial'], 3/5)
        self.assertEqual(result['type_growth:1.0'], 3/4)
        # Three internal transitions: a->b twice, a->a once.
        expected = -(2/3*math.log2(2/3) + 1/3*math.log2(1/3))
        self.assertAlmostEqual(result['bigram_conditional_entropy'], expected)

    def test_zero_bootstrap_variance_never_epsilon_rescued(self):
        reference = dict(target={'x': 1., 'y': 2.}, bootstrap_sd={'x': 0., 'y': .5})
        self.assertEqual(core.fit_distance({'x': 1., 'y': 3.}, reference), 2.)
        self.assertTrue(math.isinf(core.fit_distance({'x': 1.1, 'y': 3.}, reference)))

    def test_claim_lock_absent_incomplete_and_tampered(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(ClaimLocked): score(root, 'H6', [])
            core.save(root/'FREEZE.json', {})
            with self.assertRaises(ClaimLocked): score(root, 'H1', [])
            files = {}
            for name in ('PROTOCOL.json', 'MAPPING.json', 'held.py', 'core.py', 'GENERATORS/__init__.py'):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('original')
                files[name] = core.sha(path)
            core.save(root/'FREEZE.json', dict(tier='claim', definitions_complete=True, files=files))
            self.assertTrue(require_freeze(root)['definitions_complete'])
            (root/'core.py').write_text('tampered')
            with self.assertRaises(ClaimLocked): score(root, 'H1', [])

    def test_smc_recovers_planted_location_and_weights(self):
        # Known scalar mechanism, not a manuscript-family recovery gate.
        def distance(theta, seed):
            return abs(theta[0] - .7)
        result = smc(distance, [[0, 1]], [.2, .05], particles=80, seed=8, max_simulations=10000)
        generation = result['generations'][-1]
        self.assertTrue(all(.65 <= row[0] <= .75 for row in generation['parameters']))
        self.assertAlmostEqual(sum(generation['weights']), 1)
        old = result['generations'][0]
        sd = math.sqrt(generation['covariance'][0][0])
        raw = [1/sum(w*norm.pdf(row[0], loc=parent[0], scale=sd) for w, parent in zip(old['weights'], old['parameters'])) for row in generation['parameters']]
        np.testing.assert_allclose(np.array(raw)/sum(raw), generation['weights'], rtol=1e-10)
        self.assertEqual(result, smc(distance, [[0, 1]], [.2, .05], particles=80, seed=8, max_simulations=10000))
        with self.assertRaises(SimulationBudgetExceeded):
            smc(lambda t, s: 10, [[0, 1]], [.1], particles=2, max_simulations=5)

    def test_rf_selected_probability_and_unavailable_family_probabilities(self):
        rng = np.random.default_rng(1)
        X = np.r_[rng.normal(-10, .1, (100, 2)), rng.normal(10, .1, (100, 2))]
        result = model_choice(X, ['left']*100+['right']*100, [-10, -10], trees=80)
        self.assertEqual(result['selected_family'], 'left')
        self.assertGreater(result['selected_model_posterior_probability_approximation'], .95)
        self.assertIsNone(result['all_family_posterior_probabilities'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
