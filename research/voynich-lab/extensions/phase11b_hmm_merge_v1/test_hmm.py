import itertools
import math
import unittest
import hmm as h
from scipy.special import gammaln

class HMMTests(unittest.TestCase):
    def fixture(self):
        return h.np.array([0,1,0],dtype=h.np.int64),h.np.array([True,False,False]),h.np.array([.6,.4]),h.np.array([[.8,.2],[.3,.7]]),h.np.array([[.7,.3],[.2,.8]])
    def test_forward_and_viterbi_exhaustive(self):
        x,start,pi,A,B=self.fixture(); candidates=[]
        for z in itertools.product(range(2),repeat=3):
            v=pi[z[0]]*B[z[0],x[0]]
            for t in range(1,3): v*=A[z[t-1],z[t]]*B[z[t],x[t]]
            candidates.append((v,z))
        self.assertAlmostEqual(h.forward(x,start,pi,A,B)[2],math.log(sum(v for v,z in candidates)))
        self.assertEqual(tuple(h.viterbi(x,start,pi,A,B)),max(candidates)[1])
    def test_group_reset(self):
        x,s,pi,A,B=self.fixture(); s[:]=True
        self.assertAlmostEqual(h.forward(x,s,pi,A,B)[2],sum(math.log(pi@B[:,v]) for v in x))
    def test_em_monotonic(self):
        x=h.np.tile(h.np.array([0,0,1,1,2],dtype=h.np.int64),100)
        start=h.np.zeros(len(x),dtype=h.np.bool_); start[0]=True
        *_,trace=h.em(x,start,3,3,12,20)
        tr=trace[h.np.isfinite(trace)]
        self.assertTrue(h.np.all(h.np.diff(tr)>=-1.e-7))
    def test_gibbs_conditional_exact(self):
        x=h.np.array([0,1,0,1],dtype=h.np.int64); s=h.np.array([True,False,False,False]); z=h.np.array([0,0,0,1],dtype=h.np.int64)
        def row_marginal(counts,a):
            return gammaln(len(counts)*a)-gammaln(sum(counts)+len(counts)*a)+sum(gammaln(v+a)-gammaln(a) for v in counts)
        for t in range(4):
            cp,ca,cb=h.counts(x,s,z,2,2)
            cb[z[t],x[t]]-=1
            if s[t]: cp[z[t]]-=1
            else: ca[z[t-1],z[t]]-=1
            if t+1<len(x): ca[z[t],z[t+1]]-=1
            actual=h.conditional(t,x,s,z,cp,ca,cb)
            scores=[]
            for k in range(2):
                zz=z.copy(); zz[t]=k; pp,aa,bb=h.counts(x,s,zz,2,2)
                scores.append(row_marginal(pp,.5)+sum(row_marginal(row,.5) for row in aa)+sum(row_marginal(row,.5) for row in bb))
            expected=h.np.exp(scores-h.np.max(scores)); expected/=expected.sum()
            h.np.testing.assert_allclose(actual,expected,rtol=1.e-12,atol=1.e-12)
    def test_gibbs_finite(self):
        x,s,pi,A,B=self.fixture()
        pi,A,B,ll,_,_=h.gibbs(x,s,2,2,12,20,10,10)
        self.assertTrue(h.np.isfinite(ll)); h.np.testing.assert_allclose(A.sum(axis=1),1.)

if __name__=='__main__': unittest.main()
