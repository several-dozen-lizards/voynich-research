import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('c2',Path(__file__).parent.parent/'C2_pretest.py');c2=importlib.util.module_from_spec(spec);spec.loader.exec_module(c2)
class C2Tests(unittest.TestCase):
 def row(self,i,u,ring='R1',folio='f70v1',labelset='zodiac',reading='H'):
  return {'id':str(i),'units':list(u) if u is not None else None,'ring':ring,'folio':folio,'set':labelset,'reading':reading,'section':'zodiac' if labelset=='zodiac' else 'other'}
 def test_exact_pairs_and_page_identity(self):
  rr=[self.row(1,'a'),self.row(2,'a'),self.row(3,'b',folio='f71r'),self.row(4,'b',folio='f71r')]
  f=lambda u:u[-1];v=c2.share(rr,f,'a');self.assertEqual((v['numerator'],v['denominator']),(2,4));x=c2.cross_ring(rr,f,'a');self.assertEqual((x['numerator'],x['denominator']),(0,8))
 def test_positive_and_missing_reading(self):
  rr=[self.row(i,'a') for i in range(4)]+[self.row(i+10,'a' if i<2 else 'b',labelset='star') for i in range(10)]
  r=c2.compute(rr,[{'kind':'ending','width':1}]);self.assertGreater(r['readings']['H']['S_star']['constancy_ratio'],2);self.assertIsNone(r['readings']['F']['S_star'])
 def test_vault_denied(self):
  with self.assertRaises(ValueError):c2.compute([self.row(1,'a',folio='f73v')],[{'kind':'ending','width':1}])
 def test_zero_baseline_not_infinite_evidence(self):
  rr=[self.row(i,'a') for i in range(4)]+[self.row(i+10,'b',labelset='star') for i in range(4)]
  r=c2.compute(rr,[{'kind':'ending','width':1}]);self.assertIsNone(r['readings']['H']['S_star'])
 def test_no_input_read_before_gates(self):
  with self.assertRaises((RuntimeError,FileNotFoundError)):c2.run(Path(__file__).parent.parent,'DOES_NOT_EXIST','NO_PLAN')
 def test_unknowns_reported(self):
  rr=[self.row(1,None)];r=c2.compute(rr,[{'kind':'ending','width':1}]);self.assertEqual(r['readings']['H']['coverage']['excluded_unknown_or_empty'],1)
if __name__=='__main__':unittest.main(verbosity=2)
