import copy,sys,unittest
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).parent;ROOT=P.parents[1]
sys.path.insert(0,str(P));sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'))
import custody,harness
class Tier(unittest.TestCase):
 def setUp(self):
  self.rows=[dict(id='a',folio='f1r',reading='H',custody='unknown'),dict(id='b',folio='f2r',reading='H',custody='unknown'),dict(id='v',folio='f73r',reading='H',custody='unknown')];self.ex=dict(record_ids=['a'],source_manifest_sha256='0'*64)
 def test_unknown_allowed_without_retagging(self):
  original=copy.deepcopy(self.rows);z=custody.select(self.rows,self.ex,'H');self.assertEqual([r['id'] for r in z['rows']],['b']);self.assertEqual(z['rows'][0]['custody'],'unknown');self.assertEqual(self.rows,original)
 def test_vault_excluded(self):self.assertEqual(custody.select(self.rows,self.ex,'H')['excluded'][-1]['reason'],'VAULT CLOSED')
 def test_prospective_still_rejects_unknown(self):
  with self.assertRaises(harness.NotTestable):harness.custody_check({'built_on':[]},[],[self.rows[1]])
 def test_example_unresolved_blocks(self):
  with self.assertRaises(custody.NotTestable):custody.select(self.rows,dict(self.ex,unresolved=True),'H')
 def test_no_provenance_blocks(self):
  with self.assertRaises(custody.NotTestable):custody.select(self.rows,{},'H')
 def test_reading_substitution_blocks(self):
  with self.assertRaises(custody.NotTestable):custody.select(self.rows,self.ex,'F')
 def test_unqualified_fail_not_falsification(self):self.assertTrue(custody.interpret('FAIL',False).startswith('NOT TESTABLE'))
 def test_pass_weak(self):self.assertIn('PROSPECTIVE FOLLOW-UP',custody.interpret('PASS',True))
if __name__=='__main__':unittest.main()
