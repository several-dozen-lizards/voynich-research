"""Pure synthetic budget conservation tests; no real allocations."""
import copy,unittest
from family_budget import allocate_state,ALPHA,FAMILY
from loop import GateError,lord_level,Store,digest,filehash,writejson
from pathlib import Path
import tempfile
class FamilyBudgetTests(unittest.TestCase):
    def state(self):return dict(mode='STAGED',cycles=[],entries=[],control={},budget=dict(method='LORD++',fdr_target=.05,w0=.025,alpha_wealth=.025,tests=[],freezes=[]))
    def test_conservation_and_next_level(self):
        original=self.state();s=allocate_state(original,{'fake':'hash'},'synthetic')
        self.assertEqual(original['budget']['alpha_wealth'],.025)
        b=s['budget'];self.assertAlmostEqual(b['fdr_target']+ALPHA,.05);self.assertAlmostEqual(b['w0']+ALPHA,.025)
        self.assertAlmostEqual(lord_level(b),.010)
        self.assertTrue(s['control']['family_error_control_review_required'])
        self.assertFalse(s['control']['family_claim_admission_ready'])
    def test_duplicate_does_not_spend_again(self):
        s=allocate_state(self.state(),{'fake':'hash'},'synthetic')
        self.assertEqual(s,allocate_state(s,{'fake':'hash'},'synthetic'))
    def test_active_or_used_epoch_rejected(self):
        for field in ('active','tests','freezes','claim'):
            s=self.state()
            if field=='active':s['mode']='ACTIVE'
            if field=='tests':s['budget']['tests']=[{}]
            if field=='freezes':s['budget']['freezes']=['time']
            if field=='claim':s['entries']=[{'tier':'claim'}]
            with self.assertRaises(GateError):allocate_state(s,{'fake':'hash'},'synthetic')
    def test_shares_never_exceed_envelope(self):
        f=allocate_state(self.state(),{'fake':'hash'},'synthetic')['budget']['family_envelopes'][FAMILY]
        for n,alpha in f['C_arm_cases'].items():self.assertAlmostEqual(int(n)*alpha+f['B_alpha'],ALPHA)
        self.assertFalse(f['refund_allowed']);self.assertFalse(f['earns_online_wealth']);self.assertEqual(f['online_test_slots'],0)
    def test_activation_blocks_even_if_other_setup_is_marked_ready(self):
        base=Path(__file__).resolve().parent/'.test-runs';base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as tmp:
            store=Store(tmp);store.initialize([])
            proof=Path(tmp)/'fake.json';writejson(proof,{'synthetic':True});ev={str(proof):filehash(proof)}
            s,h,n=store.load();s=allocate_state(s,ev,'synthetic')
            s['control']['isolation']={'evidence':ev};s['vault']['status']='SEALED';s['budget']['configuration']='RE_APPROVED'
            store.commit(s,'SYNTHETIC_BLOCKED_ACTIVATION',h,n)
            q=dict(statistical_review=ev,historical_look_counts_certified=True)
            store.apply('approve',dict(id='test-approval',actor='Re',written_ok='synthetic fixture only',action='activate',target='loop',request_sha256=digest(q),evidence=ev))
            with self.assertRaisesRegex(GateError,'methodological review'):store.apply('activate',dict(q,approval_id='test-approval'))
            self.assertEqual(store.load()[0]['mode'],'STAGED')
    def test_unqualified_family_admission_is_a_separate_activation_lock(self):
        s=allocate_state(self.state(),{'fake':'hash'},'synthetic')
        s['control']['family_error_control_review_required']=False
        self.assertFalse(s['control']['family_claim_admission_ready'])
if __name__=='__main__':unittest.main(verbosity=2)
