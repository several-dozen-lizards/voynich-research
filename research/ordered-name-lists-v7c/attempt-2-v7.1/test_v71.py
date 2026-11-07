import unittest,math,json,copy,random
from pathlib import Path
from verdict_v71 import *
class V71Tests(unittest.TestCase):
 def setUp(self):
  self.k=json.loads((Path(__file__).parent.parent/'HARNESS/KNOWN-KEY.json').read_text())
 def score(self,e1=1,e3=1,e4=1):
  return {'E1':{'kind':'rate','value':e1,'success':int(e1*100),'n':100},'E2':{'kind':'rate','value':None,'success':0,'n':0},'E3':{'kind':'bits','value':e3,'n':1000},'E4':{'kind':'bits','value':e4,'n':1000},'E5':{'kind':'rate','value':None,'success':0,'n':0}}
 def test_matching_not_crossed(self):
  real=self.score();bank=[self.score(0,0,0)]*1000
  controls={'C1-word':[self.score(0,0,100)]*1000,'C1-glyph':[self.score(0,100,0)]*1000,'C2':[self.score(0,0,0)]*1000}
  self.assertEqual(verdict(self.k,real,bank,controls)['verdict'],'PASS')
 def test_95_distribution_not_point(self):
  bank=[self.score(0,0,0)]*1000;controls={'C1-word':[self.score(0,2,0)]*1000,'C1-glyph':bank,'C2':bank}
  self.assertIn('E3:C1-word',verdict(self.k,self.score(),bank,controls)['failed_controls'])
 def test_partial_bonferroni(self):
  # Five null exceedances => p6/1001 below.01, above.002: no corrected PARTIAL.
  obs=self.score(0,1,0);bank=[self.score(0,0,0)]*995+[self.score(0,2,0)]*5
  z=verdict(self.k,obs,bank,{});self.assertEqual(z['above_99'],['E3']);self.assertEqual(z['verdict'],'FAIL')
 def test_cp_zero(self):self.assertAlmostEqual(clopper_upper(0,200),1-.05**(1/200),places=12)
 def test_cp_gate_examples(self):self.assertLess(clopper_upper(1,200),.03);self.assertGreater(clopper_upper(2,200),.03)
 def test_cp_monotone(self):self.assertLess(clopper_upper(1,200),clopper_upper(2,200))
 def test_nearest_rank_ties(self):self.assertEqual(percentile(list(range(1000)),.95),949)
 def test_missing_control_no_pass(self):self.assertNotEqual(verdict(self.k,self.score(),[self.score(0,0,0)]*1000,{})['verdict'],'PASS')
 def test_reserved_rejection_preserved(self):
  with self.assertRaises(NotTestable):custody_check(self.k,[],[{'id':'x','folio':'f73v','custody':'demonstrated_unbuilt'}])
 def test_complexity_unchanged(self):self.assertAlmostEqual(complexity(self.k),140.31275182609167)
 def test_control_minimum(self):
  with self.assertRaises(NotTestable):verdict(self.k,self.score(),[self.score()]*999,{})
if __name__=='__main__':unittest.main(verbosity=2)
