import unittest,copy
from source_control_adapter import make_control,tokenize
class SourceControlTests(unittest.TestCase):
 def setUp(self):
  letters=list('abcd');self.key={'units':letters+['WORD:abcd'],'map':{c:c for c in letters}|{'WORD:abcd':'herba'}}
 def test_whole_word_unit_is_actually_disrupted(self):
  rows=[{'raw_words':['abcd']}];z=make_control(rows,self.key,'training_whole_word','C1-glyph',1)
  self.assertEqual(z[0]['control_raw_words'],['acbd']);self.assertEqual(z[0]['words'],[list('acbd')])
 def test_unit_inventory_not_refitted(self):
  original=copy.deepcopy(self.key);make_control([{'raw_words':['abcd']}],self.key,'training_whole_word','C1-glyph',1);self.assertEqual(original,self.key)
 def test_unknown_barrier_retained(self):
  z=make_control([{'raw_words':['ab',None,'cd']}],self.key,'training_whole_word','C1-word',1);self.assertIsNone(z[0]['words'][1]);self.assertEqual(z[0]['control_raw_words'],['ab',None,'cd'])
 def test_no_raw_input_rejected(self):
  with self.assertRaises(ValueError):make_control([{'words':[['WORD:abcd']]}],self.key,'training_whole_word','C1-glyph',1)
 def test_outside_inventory_abstains(self):self.assertIsNone(tokenize('xyz',self.key,'training_whole_word'))
 def test_source_unchanged(self):
  r=[{'raw_words':['abcd']}];make_control(r,self.key,'training_whole_word','C1-glyph',1);self.assertEqual(r,[{'raw_words':['abcd']}])
if __name__=='__main__':unittest.main(verbosity=2)
