import sys,copy,unittest,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).parent;ROOT=P.parents[1]
sys.path.insert(0,str(P));from admit import admit;import harness
class Schema(unittest.TestCase):
 def setUp(self):
  self.key=json.loads((ROOT/'ordered-name-lists-v7c/attempt-3-v7.2/KNOWN-KEY.json').read_text());self.key['process_evidence']=None
  self.row=dict(id='r',folio='f1r',reading='H',custody='unknown');self.examples=dict(source_manifest_sha256='0'*64,record_ids=[])
 def test_unknown_process_now_admitted_truthfully(self):
  original=copy.deepcopy(self.key);z=admit(self.key,[self.row],self.examples,'H','primary-test-source');self.assertEqual(self.key,original);self.assertFalse(z['key']['process_evidence']['independent_holdout_claim']);self.assertEqual(z['cohort']['rows'][0]['custody'],'unknown');self.assertEqual(harness.complexity(z['key']),harness.complexity(dict(self.key,process_evidence='schema-only complexity reference')))
 def test_prospective_rule_not_relaxed(self):
  with self.assertRaises(harness.NotTestable):harness.validate_key(self.key)
if __name__=='__main__':unittest.main()
