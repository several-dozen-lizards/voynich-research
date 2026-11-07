import unittest,copy,json,random,sys,importlib.util
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P.parent/'HARNESS'));sys.path.insert(0,str(P.parent/'attempt-2-v7.1'))
from harness import complexity,digest
from source_first_controls import build_control,validate_source
from role_preserving_keys import random_role_key,invariants
from dual_bank_verdict import combine
import worker_v72
spec=importlib.util.spec_from_file_location('reference_original',P.parent/'HARNESS/harness.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def read(p):return json.loads(p.read_text())
class V72Tests(unittest.TestCase):
 def test_worker_exact_original_scores(self):
  for prefix,base in [('known',P.parent/'HARNESS'),('trap',P.parent/'attempt-2-v7.1')]:
   if prefix=='known':d=read(base/'KNOWN-CIPHER-DATA.json');k=read(base/'KNOWN-KEY.json')
   else:d=read(base/'TRAP-H-DATA.json');k=read(base/'TRAP-H-KEY.json')
   ctx={n:d[n] for n in ('train','held','target','lexicons')};ctx['alphabet']=k['target']['alphabet'];worker_v72.init(ctx)
   for seed in range(5):
    z=ref.random_key(k,random.Random(seed));self.assertEqual(worker_v72.score_one((seed,z))['scores'],ref.raw_scores(z,d['train'],d['held'],d['target'],d['lexicons']))
 def test_role_frequency_and_complexity(self):
  k=read(P/'KNOWN-KEY.json')
  for i in range(20):z=random_role_key(k,random.Random(i));self.assertTrue(invariants(k,z));self.assertEqual(complexity(z),complexity(k))
 def test_dual_gate_requires_shared_components(self):
  a={'verdict':'PASS','above_99':['E1','E4'],'above_998':['E1']};b={'verdict':'PASS','above_99':['E2','E3'],'above_998':['E4']};self.assertEqual(combine(a,b)['verdict'],'FAIL')
 def test_noise_tokenizer_contract(self):
  k=read(P/'KNOWN-KEY.json')
  for view in ('H','F'):self.assertTrue(validate_source(read(P/('NOISY-'+view+'-DATA.json'))['held'],k,'known_initial_a'))
 def test_native_joint_support_before_fit(self):
  c=read(P/'TRAP-COHORT.json')
  for part in ('train','held'):
   h=c['readings']['H'][part];f=c['readings']['F'][part];self.assertEqual(len(h),40);self.assertEqual([r['locus'] for r in h],[r['locus'] for r in f]);self.assertTrue(all(all(w is not None for w in r['tokens']) for r in h+f))
 def test_old_whole_word_shuffle_fixed(self):
  k={'units':list('abcd')+['WORD:abcd'],'map':{c:c for c in 'abcd'}|{'WORD:abcd':'herba'}};r=[{'id':'x','raw_words':['abcd'],'words':[['WORD:abcd']]}];o,receipt=build_control(r,k,'training_whole_word','C1-glyph',1);self.assertEqual(o[0]['words'],[list('acbd')])
if __name__=='__main__':unittest.main(verbosity=2)
