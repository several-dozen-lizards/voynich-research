import copy,importlib.util,itertools,json,math,sys,unittest
from pathlib import Path
P=Path(__file__).parent;ROOT=P.parent
sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'))
import harness

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('t1',P/'T1-freeze/methods.py');a=module('adapters',P/'adapters/adapters.py')
def row(f,label,events,n=60,bin='normal'):
 c=dict.fromkeys(m.CLASSES,0);c['open:qok']=events;c['open:other']=n-events;c['end:other']=n
 return dict(id=f+':'+label+':'+bin,folio=f,reading='H',length_bin=bin,label=label,n=n,counts=c)
def balanced():return [row('toy'+str(f),lab,6 if lab in ('FG','VE') else 3) for f in range(8) for lab in m.LABELS]
def geo():
 return [dict(id=f'{b}{i}',folio='f70v2',reading='H',band=b,position=i,label_span=None if i==1 else [['toy',i]],order_source='geometry-only') for b,n in [('a',3),('b',2)] for i in range(n)]
class T1(unittest.TestCase):
 def test_seed_domains_frozen(self):
  self.assertEqual(m.derived_seed(810251,'H','open:qok'),m.derived_seed(810251,'H','open:qok'));self.assertNotEqual(m.derived_seed(810251,'H','open:qok'),m.derived_seed(810251,'F','open:qok'))
 def test_actual_10000_bootstrap_draws(self):
  rs=balanced()
  for r in rs:r['counts']['open:qok']=3;r['counts']['open:other']=57
  z=m.equivalence(rs,'open:qok');self.assertTrue(z['equivalent']);self.assertEqual(z['maximum_absolute_bound'],0);self.assertEqual(len(z['pairs']),15);self.assertEqual(z['draws'],10000)
 def test_rate_not_odds(self):self.assertAlmostEqual(m.rate_ratio(balanced())['logRR'],math.log(2))
 def test_swapping_reverses(self):self.assertAlmostEqual(m.rate_ratio(balanced(),left=('PL','NO'),right=('FG','VE'))['logRR'],-math.log(2))
 def test_unknown_initial_not_promoted(self):
  r=dict(id='toy',folio='toy',reading='H',label='FG',length_bin='normal',words=[None,'qokain',None,'otedy']);z=m.count_line(r)
  self.assertEqual((z['n'],z['unknown'],z['counts']['open:qok']),(2,1,1))
 def test_classes_priority(self):
  self.assertEqual(m.classify('qokaiin'),('open:qok','end:a'));self.assertEqual(m.classify('qody'),('open:qo','end:y'));self.assertEqual(m.classify('otol'),('open:ot','end:ol/or'));self.assertEqual(m.classify('chey'),('open:ch','end:y'))
 def test_readings_never_pool(self):
  rs=balanced();rs[0]['reading']='F'
  with self.assertRaises(m.NotEstimable):m.rate_ratio(rs)
 def test_reserved_rejected(self):
  rs=balanced();rs[0]['folio']='f73r'
  with self.assertRaises(m.NotEstimable):m.rate_ratio(rs)
 def test_support_failure(self):
  with self.assertRaises(m.NotEstimable):m.rate_ratio([r for r in balanced() if r['folio']!='toy0'])
 def test_zero_not_smoothed(self):
  rs=balanced()
  for r in rs:r['counts']['open:qok']=0;r['counts']['open:other']=r['n']
  with self.assertRaises(m.NotEstimable):m.rate_ratio(rs)
 def test_dominant_weight(self):
  rs=balanced()
  for r in rs:
   if r['folio']=='toy0':r['n']*=100;r['counts']={k:v*100 for k,v in r['counts'].items()}
  with self.assertRaises(m.NotEstimable):m.rate_ratio(rs)
 def test_shuffle_whole_lines_unrestricted_bins(self):
  import numpy as np
  rs=[row('toy','FG',6,bin='short'),row('toy','PL',3)]
  zs=[m.permute(rs,np.random.default_rng(i)) for i in range(20)]
  self.assertTrue(any(z[0]['label']=='PL' for z in zs));self.assertEqual(rs[0]['label'],'FG')
  for z in zs:
   self.assertEqual(sorted(r['label'] for r in z),['FG','PL']);self.assertEqual([r['counts'] for r in z],[r['counts'] for r in rs])
 def test_cmh_matches_manual_2label(self):
  rs=[r for r in balanced() if r['label'] in ('FG','PL')];got=m.cmh(rs,'open:qok')['statistic']
  # Per folio: A=(6,3), exposures=(60,60); d=(1.5,-1.5).
  variance=9*111/(120*119)*(60-30)
  self.assertAlmostEqual(got,(8*1.5)**2/(8*variance))
 def test_cmh_label_renaming(self):
  rs=balanced();zs=copy.deepcopy(rs);rename=dict(zip(m.LABELS,m.LABELS[::-1]))
  for z in zs:z['label']=rename[z['label']]
  self.assertAlmostEqual(m.cmh(rs,'open:qok')['statistic'],m.cmh(zs,'open:qok')['statistic'])
 def test_holm_full_family(self):
  self.assertEqual(m.holm([.001]+[.5]*16)[0],.017)
  with self.assertRaises(ValueError):m.holm([.001])
 def test_nonsignificance_is_not_equivalence(self):self.assertEqual(m.classify_both(.2,.3,{},{}),'unresolved')
 def test_both_readings_for_sensitive(self):self.assertEqual(m.classify_both(.001,.2,{},{}),'unresolved')
 def test_missing_pairs_unresolved(self):self.assertEqual(m.equivalence([r for r in balanced() if r['label']!='CE'],'open:qok')['status'],'UNRESOLVED')
 def test_actual_10000_permutations(self):
  # Identical rates at every line make every valid shuffle equal to observed.
  rs=balanced()
  for r in rs:r['counts']['open:qok']=3;r['counts']['open:other']=57
  z=m.permutation_test(rs);self.assertEqual(z.get('draws'),10000);self.assertEqual(z['p'],1.)
class Adapters(unittest.TestCase):
 def test_ambiguous_tokenizer_abstains(self):self.assertIsNone(a.tokenize_unique('ch',['c','h','ch']))
 def test_unique_roundtrip(self):
  z=a.tokenize_unique('qokain',['qok','ain']);self.assertEqual(z,['qok','ain']);self.assertEqual(''.join(z),'qokain')
 def test_unknown_tokenizer_barrier(self):self.assertIsNone(a.tokenize_unique('qok?',['qok','ain']))
 def test_span_boundaries_and_qualified_decoder(self):
  rows=[dict(id='toy',folio='toy',reading='H',words=[['a'],['b']])];key=dict(map={'a':'red','b':'root'},rules=[])
  self.assertEqual(a.decode_span(rows,[['toy',0],['toy',1]],key,harness.decode_word),'red root')
 def test_span_unknown_stays_in_denominator(self):
  rows=[dict(id='toy',folio='toy',reading='H',words=[['a'],None])];key=dict(map={'a':'red'},rules=[])
  z=a.e2_spans(rows,[dict(id='p',a=[['toy',0],['toy',1]],b=[['toy',0]])],key,harness.decode_word)
  self.assertEqual((z['success'],z['n'],z['unknown']),(0,1,1))
 def test_duplicate_span_rejected(self):
  rows=[dict(id='toy',folio='toy',reading='H',words=[['a']])]
  with self.assertRaises(a.NotAdmitted):a.decode_span(rows,[['toy',0],['toy',0]],{},harness.decode_word)
 def test_vault_adapter_rejected(self):
  rs=geo();rs[0]['folio']='f72v1'
  with self.assertRaises(a.NotAdmitted):list(a.alignments(rs,1000))
 def test_exact_decimal_sum(self):self.assertTrue(a.numeric_check(['0.1','0.2'],'sum','0.3'))
 def test_large_integer_not_rounded(self):self.assertFalse(a.numeric_check(['9007199254740993'],'sum','9007199254740992'))
 def test_float_rejected(self):
  with self.assertRaises(a.NotAdmitted):a.numeric_check([.1,.2],'sum','.3')
 def test_undecodable_number_false(self):self.assertFalse(a.numeric_check([None,'2'],'sum','2'))
 def test_all_rotations_directions_bandorders(self):
  rs=geo();zs=list(a.alignments(rs,1000));self.assertEqual(len(zs),48)
  # Independent brute-force oracle: 24 unique cyclic/reflection orders of 3+2 figures.
  got={tuple(z['ids']) for z in zs};expected=set()
  for aa in itertools.permutations(('a0','a1','a2')):
   for bb in itertools.permutations(('b0','b1')):expected.add(aa+bb);expected.add(bb+aa)
  self.assertEqual(got,expected)
  for z in zs:self.assertEqual(set(z['ids']),{r['id'] for r in rs})
 def test_no_search_truncation(self):
  with self.assertRaises(a.NotAdmitted):list(a.alignments(geo(),47))
 def test_geometry_order_cannot_use_text(self):
  rs=geo();rs[0]['order_source']='label-content'
  with self.assertRaises(a.NotAdmitted):list(a.alignments(rs,1000))
 def test_missing_slot_not_compacted(self):
  rs=geo();self.assertIsNone(rs[1]['label_span']);self.assertTrue(all('a1' in z['ids'] for z in a.alignments(rs,1000)))
 def test_duplicate_positions_rejected(self):
  rs=geo();rs[1]['position']=0
  with self.assertRaises(a.NotAdmitted):list(a.alignments(rs,1000))
 def test_real_and_null_use_same_search(self):
  rs=geo();z=a.search_null(rs,[copy.deepcopy(rs)]*3,lambda _:lambda ids:ids.index('a0'),1000)
  self.assertEqual(z['p'],1);self.assertEqual(z['observed']['evaluated'],48);self.assertTrue(all(n['evaluated']==48 for n in z['null']))
 def test_null_same_count_wrong_geometry_rejected(self):
  rs=geo();zs=copy.deepcopy(rs);zs[0]['id']='replacement'
  with self.assertRaises(a.NotAdmitted):a.search_null(rs,[zs],lambda _:lambda ids:0,1000)
 def test_missing_reading_no_substitution(self):
  rs=geo();rs[0]['reading']='U'
  with self.assertRaises(a.NotAdmitted):list(a.alignments(rs,1000))
 def test_list_gap_and_seal(self):
  p=dict(id='toy',source='synthetic',source_sha256='0'*64,date_latest=1400,eligible_by_1440=True,slots=['a',None,'b'],normalization='identity',variant_id='v1');p['freeze_sha256']=a.digest(p)
  self.assertEqual(a.list_variant(p),('a',None,'b'));p['slots'][1]='new'
  with self.assertRaises(a.NotAdmitted):a.list_variant(p)
 def test_late_list_rejected(self):
  with self.assertRaises(a.NotAdmitted):a.list_variant(dict(id='x',source='x',source_sha256='0'*64,date_latest=1500,eligible_by_1440=True,slots=['a'],normalization='identity',variant_id='v1',freeze_sha256='0'*64))
 def test_no_caller_release_bypass(self):
  with self.assertRaises(a.NotAdmitted):a.require_scientific_release({'qualified':True,'vault':True})
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]);result=unittest.TextTestRunner(verbosity=1).run(suite)
 out=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=[str(x) for x in result.failures],errors=[str(x) for x in result.errors],scope='Synthetic engineering checks only; no ratings/text join, no real B/C or published-key score',scientific_qualification=False)
 (P/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 sys.exit(not result.wasSuccessful())
