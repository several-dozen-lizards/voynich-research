import json,tempfile,unittest
from pathlib import Path
from source_cut2 import CUT,ROOT,dump,load_cut2_development
from transfer_policy import SourceSupportError,sample_window
from core import sha
from held import score,ClaimLocked

class IndependentCutTests(unittest.TestCase):
    def fixture(self,folder):
        root=Path(folder);dump(root/'SELECTION.json',dict(cut='fixture'))
        dump(root/'SELECTION-SEAL.json',dict(sha256=sha(root/'SELECTION.json')))
        dump(root/'DEVELOPMENT-UNITS.json',[
            dict(language='Latin',work='A',unit='a1',order=1,words=['a']*3),
            dict(language='Latin',work='A',unit='a3',order=3,words=['b']*3),
            dict(language='Latin',work='B',unit='b1',order=1,words=['c']*3),
            dict(language='Latin',work='supplement',unit='inventory-only',order=1,words=['INVENTORY_ONLY']*99,generation_eligible=False)])
        dump(root/'DEVELOPMENT-SEAL.json',dict(files={'DEVELOPMENT-UNITS.json':sha(root/'DEVELOPMENT-UNITS.json')}))
        return root

    def test_rejects_reserve_and_calibration_before_loading(self):
        for part in ('reserve','calibration'):
            with self.assertRaises(SourceSupportError):load_cut2_development('Latin',part,Path('NONEXISTENT'))

    def test_work_and_missing_unit_boundaries_do_not_supply_pooled_length(self):
        with tempfile.TemporaryDirectory() as d:
            corpus=load_cut2_development('Latin',cut=self.fixture(d))
            self.assertEqual([len(r[2]) for r in corpus.runs],[3,3,3])
            with self.assertRaises(SourceSupportError):sample_window([dict(work=w,units=u,tokens=t) for w,u,t in corpus.runs],4,1)

    def test_inventory_supplement_cannot_be_used_for_generation(self):
        with tempfile.TemporaryDirectory() as d:
            corpus=load_cut2_development('Latin',cut=self.fixture(d))
            self.assertNotIn('INVENTORY_ONLY',repr(corpus))

    def test_development_data_drift_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d);(root/'DEVELOPMENT-UNITS.json').write_text('[]')
            with self.assertRaises(SourceSupportError):load_cut2_development('Latin',cut=root)

    def test_registered_jaufre_has_no_line_gap_or_duplicate(self):
        lines=json.loads((CUT/'JAUFRE-LINES.json').read_text())
        self.assertEqual([r['line'] for r in lines],list(range(1,10975)))

    def test_editorially_supplied_czech_forms_remain_barriers(self):
        units=json.loads((CUT/'DEVELOPMENT-UNITS.json').read_text());words=next(u['words'] for u in units if u['language']=='Czech')
        ledger=json.loads((CUT/'CZECH-BARRIERS.json').read_text())
        self.assertTrue(any('<' in e['raw'] for e in ledger))
        self.assertTrue(all(words[e['slot']] is None for e in ledger))

    def test_fresh_reserve_has_identified_blobs_but_no_body_acquisition(self):
        ledger=json.loads((CUT/'FRESH-RESERVE-LEDGER.json').read_text());self.assertEqual(ledger['bodies_parsed'],0)
        self.assertEqual(len(ledger['Latin16195']),2)
        self.assertFalse(any('Latin16195' in str(p) for p in (CUT/'development').rglob('*')))

    def test_new_development_seals_do_not_unlock_held_scores(self):
        for root in (ROOT,CUT):
            self.assertFalse((root/'FREEZE.json').exists())
            with self.assertRaises(ClaimLocked):score(root,'H3',[])

if __name__=='__main__':unittest.main(verbosity=2)
