from pathlib import Path
import json,tempfile,unittest
from unittest.mock import patch
from core import sha,save,group_inventory
from source_contract import load_development_corpus,produce_from_development,DevelopmentCorpus
from transfer_policy import SourceSupportError

class SourceContractTests(unittest.TestCase):
    def fixture(self,root):
        save(root/'LATIN-SOURCE-UNITS.json',[dict(unit='chapter1',words=['ab','ac']*4),dict(unit='chapter2',words=['RESERVE_POISON']*30)])
        save(root/'LANGUAGE-SOURCE-SPLITS.json',{'Latin':{'development':{'units':['chapter1']},'reserve':{'units':['chapter2']}}})
        save(root/'SOURCE-COVERAGE-PLAN.json',{'files':{p:sha(root/p) for p in ('LATIN-SOURCE-UNITS.json','LANGUAGE-SOURCE-SPLITS.json')}})

    def test_only_development_positions_reach_generator(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root);corpus=load_development_corpus(root,'Latin')
            self.assertNotIn('RESERVE_POISON',repr(corpus))
            inv=group_inventory(['qokedy','chedy','shedy','qockheer']*20)
            result=produce_from_development('G1',{},5,corpus=corpus,inventory=inv,line_lengths=[3,4])
            self.assertEqual(result['source_receipt']['partition'],'development')
            self.assertEqual(result['source_receipt']['source_wraps'],0)
            self.assertEqual(result['source_receipt']['source_units'],['chapter1'])

    def test_no_reserve_loader_or_source_start_override(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root)
            with self.assertRaises(SourceSupportError):load_development_corpus(root,'Latin',partition='reserve')
            corpus=load_development_corpus(root,'Latin')
            with self.assertRaises(SourceSupportError):produce_from_development('G1',{'source_start':2},1,corpus=corpus,line_lengths=[3])

    def test_source_file_drift_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root);(root/'LATIN-SOURCE-UNITS.json').write_text('[]')
            with self.assertRaises(SourceSupportError):load_development_corpus(root,'Latin')

    def test_aggregate_size_cannot_override_work_boundary(self):
        corpus=DevelopmentCorpus('Occitan',(('work1',('u1',),('ab','ac')),('work2',('u2',),('ab','ac'))),'fixture')
        with patch('source_contract.produce',side_effect=AssertionError('generator invoked')):
            with self.assertRaises(SourceSupportError):produce_from_development('G1',{},1,corpus=corpus,line_lengths=[3])

if __name__=='__main__':unittest.main(verbosity=2)
