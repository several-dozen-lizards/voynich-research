import unittest
import run_k123 as k

class Engineering(unittest.TestCase):
    def test_first_alternative_and_offsets(self):
        s=k.literal('<%>ab.[c,d:xx],ef.gh<$>')
        self.assertEqual(s,'ab.c,d,ef.gh')
        a=k.tokens(s,'split');b=k.tokens(s,'join')
        self.assertEqual([x['word'] for x in a],['ab','c','d','ef','gh'])
        self.assertEqual([x['word'] for x in b],['ab','cdef','gh'])
        self.assertTrue(all(s[x['start']:x['end']].replace(',','')==x['word'] for x in a+b))
    def test_barriers_remain(self):
        for raw in ['ab,<->,cd','ab,?,cd','ab,@123;,cd','ab,%cd']:
            s=k.literal(raw)
            self.assertIn('\ufffd',s)
            self.assertNotIn('abcd',[x['word'] for x in k.tokens(s,'join')])
    def test_no_gap_or_paragraph_bridge(self):
        def line(n,group=0):
            return dict(id=f'f1r.{n}',folio='f1r',family='1',index=n,paragraph_group=group,start=False,end=False,literal='ab.cd',scribe='1',variety='A')
        self.assertEqual(len(k.make_runs([line(1),line(3)])),2)
        self.assertEqual(len(k.make_runs([line(1),line(2,1)])),2)
        self.assertEqual(len(k.make_runs([line(1),line(2)])),1)
    def test_reversal_all_models(self):
        models,meta,_=k.j.models_for([['ab','cd','ef','gh','ad']]*3)
        w=['ab','ef','cd','gh']
        for key,m in models.items():
            self.assertAlmostEqual(k.j.pair_score(w,m,*key,meta),-k.j.pair_score(list(reversed(w)),m,*key,meta))
    def test_adjustment_indices(self):
        import math
        self.assertEqual(math.floor(2000*.025/7),7)
        self.assertEqual(math.ceil(2000*(1-.025/7))-1,1992)

if __name__=='__main__':unittest.main()
