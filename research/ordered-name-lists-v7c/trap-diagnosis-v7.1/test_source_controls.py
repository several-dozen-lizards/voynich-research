import unittest,copy,random,sys,json
from pathlib import Path
from source_controls import *
P=Path(__file__).parent
class SourceTests(unittest.TestCase):
 def setUp(self):
  self.k={'units':list('abcd')+['WORD:abcd'],'map':{c:c for c in 'abcd'}|{'WORD:abcd':'herba'}}
  self.rows=[{'id':'x','folio':'f5r','raw_words':['abcd',None,'ab'],'words':[['WORD:abcd'],None,['a','b']]}]
 def test_whole_word_shuffle_before_tokenization(self):
  out,r=build_control(self.rows,self.k,'training_whole_word','C1-glyph',1);self.assertEqual(out[0]['words'][0],list('acbd'));self.assertEqual(r['changed_raw_words'],1)
 def test_original_tokenization_validated(self):
  x=copy.deepcopy(self.rows);x[0]['words'][0]=list('abcd')
  with self.assertRaises(ValueError):build_control(x,self.k,'training_whole_word','C1-glyph',1)
 def test_native_unknown_never_promoted(self):
  out,r=build_control(self.rows,self.k,'training_whole_word','C1-word',1);self.assertIsNone(out[0]['words'][1]);self.assertEqual(r['native_barriers'],1)
 def test_missing_raw_rejected(self):
  x=copy.deepcopy(self.rows);del x[0]['raw_words']
  with self.assertRaises(ValueError):validate_source(x,self.k,'training_whole_word')
 def test_reserved_rejected(self):
  for f in RESERVED:
   x=copy.deepcopy(self.rows);x[0]['folio']=f
   with self.assertRaises(ValueError):validate_source(x,self.k,'training_whole_word')
 def test_duplicates_rejected(self):
  with self.assertRaises(ValueError):validate_source(self.rows*2,self.k,'training_whole_word')
 def test_no_source_key_mutation(self):
  rr=copy.deepcopy(self.rows);kk=copy.deepcopy(self.k);build_control(self.rows,self.k,'training_whole_word','C1-glyph',1);self.assertEqual(rr,self.rows);self.assertEqual(kk,self.k)
 def test_known_key_controls_match_existing_character_fixture(self):
  sys.path.insert(0,str(P.parent/'HARNESS'));import harness
  d=json.loads((P.parent/'HARNESS/KNOWN-CIPHER-DATA.json').read_text());k=json.loads((P.parent/'HARNESS/KNOWN-KEY.json').read_text())
  rows=copy.deepcopy(d['held'])
  for r in rows:r['raw_words']=[''.join('a' if u=='INIT_A' else u[1:] for u in w) for w in r['words']]
  for kind,seed in [('C1-glyph',802),('C1-word',801)]:
   got,_=build_control(rows,k,'known_initial_a',kind,seed);old=(harness.shuffle_glyphs if kind=='C1-glyph' else harness.shuffle_lines)(rows,random.Random(seed))
   self.assertEqual([r['words'] for r in got],[r['words'] for r in old])
if __name__=='__main__':unittest.main(verbosity=2)
