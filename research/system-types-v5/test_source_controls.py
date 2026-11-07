from pathlib import Path
import unittest,json,unicodedata as U
from collections import Counter
from source_controls import diplomatic_slots,recover_units,plain_words,ROOT,ABBREVIATION_SIGNS
from recovery_design import summarize_labels,require_recovery_release,RecoveryLocked,FAMILIES

class SourceControlsTests(unittest.TestCase):
    def test_actual_written_units_not_expanded(self):
        raw='p\u0303ꝰ ⁊ ℥ \uf2da .a.'
        slots=diplomatic_slots(raw)
        self.assertEqual([recover_units(s['units']) for s in slots],['p\u0303ꝰ','⁊','℥','\uf2da','a'])
        self.assertIn('GLYPH:U+2125',slots[2]['units'])
        self.assertIn('GLYPH:U+F2DA',slots[3]['units'])

    def test_unknown_and_hyphen_barriers(self):
        slots=diplomatic_slots('bonus [damaged] mal- herba')
        self.assertEqual([s['units'] is None for s in slots],[False,True,True,False])

    def test_unicode_diacritics_preserved(self):
        self.assertEqual(plain_words('più řě ſſ'),['più','řě','ſſ'])

    def test_full_source_nonpunctuation_coverage(self):
        rows=json.loads((ROOT/'REAL-LATIN-ROWS.json').read_text())
        for row in rows:
            expected=Counter(c for c in U.normalize('NFD',row['raw'].lower()) if not c.isspace() and (U.category(c)[0]!='P' or c in ABBREVIATION_SIGNS))
            actual=Counter(c for s in row['slots'] if s['units'] is not None for c in recover_units(s['units']))
            self.assertEqual(expected,actual,(row['manuscript'],row['line']))

    def test_source_partitions_no_shared_units(self):
        splits=json.loads((ROOT/'LANGUAGE-SOURCE-SPLITS.json').read_text())
        for language,parts in splits.items():
            sets=[set(p['units']) for p in parts.values()]
            for i,a in enumerate(sets):
                for b in sets[i+1:]:self.assertFalse(a&b,language)

    def test_recovery_survival_is_not_discrimination(self):
        records=[dict(trial=i,true_family='G2',regime='interior' if i<80 else 'boundary',decisions={f:'SURVIVES' for f in FAMILIES}) for i in range(100)]
        outcome=summarize_labels(records)
        self.assertTrue(outcome['survival_gate']);self.assertFalse(outcome['discrimination_gate']);self.assertFalse(outcome['interpretation_allowed'])
        for row in records:
            row['decisions'].update({f:'ELIMINATED' for f in ('G4','G5','G6')})
        self.assertTrue(summarize_labels(records)['interpretation_allowed'])
        records[0]['decisions']['G1']='BUDGET_EXHAUSTED'
        self.assertFalse(summarize_labels(records)['interpretation_allowed'])

    def test_full_recovery_locked_with_missing_H3(self):
        with self.assertRaises(RecoveryLocked):require_recovery_release()

if __name__=='__main__':unittest.main(verbosity=2)
