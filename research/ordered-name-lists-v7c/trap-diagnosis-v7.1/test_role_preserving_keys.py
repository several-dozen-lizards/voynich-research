import unittest,copy,random,json,sys
from pathlib import Path
from collections import Counter
from role_preserving_keys import *
P=Path(__file__).parent;sys.path.insert(0,str(P.parent/'HARNESS'));from harness import complexity
class RoleTests(unittest.TestCase):
 def setUp(self):self.k=json.loads((P.parent/'attempt-2-v7.1/TRAP-H-KEY.json').read_text())
 def test_inactive_defaults_do_not_move_to_fallback(self):
  for seed in range(20):
   z=random_role_key(self.k,random.Random(seed));self.assertEqual(Counter(z['map'][u] for u in z['units'] if not role_signature(z,u)),Counter('abcdefghijklmnopqrstuvwxyz'))
 def test_all_requested_frequencies_and_complexity(self):
  for seed in range(20):
   z=random_role_key(self.k,random.Random(seed));self.assertTrue(invariants(self.k,z));self.assertEqual(Counter(z['map'].values()),Counter(self.k['map'].values()));self.assertEqual(Counter(r['value'] for r in z['rules']),Counter(r['value'] for r in self.k['rules']));self.assertEqual(complexity(z),complexity(self.k))
 def test_labels_not_used(self):
  renamed=copy.deepcopy(self.k);rename={u:'unit'+str(i) for i,u in enumerate(self.k['units'])};renamed['units']=[rename[u] for u in self.k['units']];renamed['map']={rename[u]:v for u,v in self.k['map'].items()}
  for r in renamed['rules']:r['unit']=rename[r['unit']]
  a=random_role_key(self.k,random.Random(44));b=random_role_key(renamed,random.Random(44));self.assertEqual([a['map'][u] for u in self.k['units']],[b['map'][rename[u]] for u in self.k['units']]);self.assertEqual([r['value'] for r in a['rules']],[r['value'] for r in b['rules']])
 def test_source_key_immutable(self):
  old=copy.deepcopy(self.k);random_role_key(self.k,random.Random(3));self.assertEqual(old,self.k)
 def test_determinism(self):self.assertEqual(random_role_key(self.k,random.Random(4)),random_role_key(self.k,random.Random(4)))
 def test_known_cipher_remains_randomized(self):
  k=json.loads((P.parent/'HARNESS/KNOWN-KEY.json').read_text());z=random_role_key(k,random.Random(3));self.assertNotEqual(z['map'],k['map']);self.assertEqual(complexity(z),complexity(k))
if __name__=='__main__':unittest.main(verbosity=2)
