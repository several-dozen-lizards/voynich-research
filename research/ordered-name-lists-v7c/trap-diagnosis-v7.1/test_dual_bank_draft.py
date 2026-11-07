import unittest
from dual_bank_verdict_DRAFT import combine
class DualTests(unittest.TestCase):
 def row(self,verdict='PASS',a=('E1','E4'),b=('E1',)):
  return {'verdict':verdict,'above_99':list(a),'above_998':list(b)}
 def test_requires_both_pass(self):self.assertNotEqual(combine(self.row(),self.row('FAIL',(),()))['verdict'],'PASS')
 def test_requires_same_two_evaluations(self):self.assertEqual(combine(self.row(a=('E1','E4')),self.row(a=('E2','E3'),b=()))['verdict'],'FAIL')
 def test_partial_requires_same_component(self):self.assertEqual(combine(self.row('PARTIAL',b=('E1',)),self.row('PARTIAL',b=('E4',)))['verdict'],'FAIL')
 def test_shared_partial(self):self.assertEqual(combine(self.row('PARTIAL'),self.row('PARTIAL'))['verdict'],'PARTIAL')
 def test_shared_pass(self):self.assertEqual(combine(self.row(),self.row())['verdict'],'PASS')
 def test_never_activates_admission(self):self.assertFalse(combine(self.row(),self.row())['admission_active'])
if __name__=='__main__':unittest.main(verbosity=2)
