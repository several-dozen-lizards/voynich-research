"""Staged, disjoint nonrecycling family allocation. Never enables vault execution.

Hybrid accounting is a NEW explicit amendment, not a claim that a family is one
LORD++ discovery. Its operational admission/review remains activation-blocking.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,sys
from loop import Store, require, GateError, writejson, filehash, utc, lord_level

FAMILY='v7-joint'
ALPHA=.005

def allocate_state(state, evidence, authority):
    s=copy.deepcopy(state);b=s['budget']
    require(s['mode']=='STAGED' and not s['cycles'],'Family reservation requires inactive pre-run epoch')
    existing=b.get('family_envelopes',{}).get(FAMILY)
    if existing:
        require(existing['alpha']==ALPHA,'Conflicting existing envelope')
        return s
    require(not b['tests'] and not b['freezes'] and not any(e['tier']=='claim' for e in s['entries']),
            'Cannot rebase an already-tested statistical epoch')
    require(not b.get('family_envelopes'),'This amendment reserves exactly one declared family')
    require(b['method']=='LORD++' and b['fdr_target']==.05 and b['w0']==.025 and b['alpha_wealth']==.025,
            'Unexpected starting budget; do not silently rebase')
    b.update(method='DISJOINT_NONRECYCLING_FAMILY_FWER_PLUS_LORD++',project_fdr_target=.05,
        initial_project_wealth=.025,family_fwer_reserved=ALPHA,fdr_target=.045,w0=.020,alpha_wealth=.020)
    b['family_envelopes']={FAMILY:dict(alpha=ALPHA,status='RESERVED_NO_VAULT_AUTHORIZATION',
        ledger_reserved=True,refund_allowed=False,earns_online_wealth=False,online_test_slots=0,
        hypothesis_ids=['B','C-FULL','C-STEM','C-SUF','C-MRK'],B_alpha=.0025,C_pool=.0025,
        C2_selection=None,C_arm_cases={'2':.00125,'3':.005/6,'4':.000625},
        selection_rule='C2 decides optional S*/M* arms before qualification/vault outcomes. Split C_pool over C2-eligible arms; subsequent failed qualification does not redistribute.',
        unspent_rule='No candidate, ineligible or unqualified shares remain unused permanently; no refund, no rescue, no online reward.',
        authority=authority,evidence=evidence,reserved_utc=utc())}
    s['control']['family_error_control_review_required']=True
    s['control']['family_claim_admission_ready']=False
    require(abs(b['family_fwer_reserved']+b['fdr_target']-b['project_fdr_target'])<1e-15,'Global target mismatch')
    require(abs(b['alpha_wealth']+ALPHA-b['initial_project_wealth'])<1e-15,'Initial-wealth conservation failed')
    return s

AMENDMENT='''# v7 joint vault alpha amendment

Re accepted the proposed nominal family cap alpha_V=0.005 in the current chat ("Let's do that"). This amendment resolves the previously identified family/stream and refund conflicts. It does not authorize a vault run, activate the autonomous loop, claim complete custody, or certify statistical validity.

## Explicit global error-control change

The originally proposed single LORD++ stream is amended, before any registered claim test, to disjoint error budgets:

- v7 B/C family: nonrecycling familywise error allowance 0.005.
- Remaining online claims: LORD++ FDR target 0.045, initial wealth 0.020, gamma(t)=1/[t(t+1)].
- The original nominal project FDR target remains 0.05; original initial wealth 0.025 is partitioned into 0.005 permanently reserved and 0.020 online wealth. The next online single-test level becomes 0.010.
- Vault-arm discoveries never earn online wealth. They are not counted as one LORD++ test or as several recycled online rejections.

For a valid vault family FWER bound and a valid remaining-stream FDR bound, pointwise FDP_total <= I(any false vault claim) + FDP_online. Taking expectations gives FDR_total <= 0.005 + 0.045 = 0.05. This decomposition does not require independence between those two budgets, but the online procedure still needs its own assumptions, and every family p-value must be valid conditional on development/selection. Budget arithmetic does not fix invalid p-values or exposed holdouts. This is not FWER control over the whole project.

Sources for the remaining LORD++ stream: https://arxiv.org/abs/1710.00499 and https://dsrobertson.github.io/onlineFDR/articles/theory.html . The disjoint-budget inequality above is an explicit mathematical argument for this amendment, not an assertion that the source paper describes this project-specific hybrid.

## Closed family and fixed shares

B receives 0.0025. C has a total pool of 0.0025. C-FULL and C-STEM are always C2-eligible; C-SUF is eligible only if C2 finds S*, C-MRK only if C2 finds M*.

| Eligible C arms after C2 | Alpha per arm |
|---|---:|
| 2 | 0.00125 |
| 3 | 0.0008333333333333334 |
| 4 | 0.000625 |

C2 selection is fixed before qualification and before vault outcomes. Later qualification failure does not reduce the divisor and does not increase another share. B NO CANDIDATE, excluded optional arms and failed qualification never return alpha to either pool. This explicitly supersedes the refund sentences of the supplied declaration; no other hypothesis, custody or scoring-order rule is changed.

H/F remain separate and never count as two independent discoveries. A both-reading claim must meet the allocated arm threshold under its frozen complete test; any different reading/sign multiplicity requires predeclared internal control within that arm. No test may borrow an unused share. Repeated looks, extra candidates or new arms require a new approved budget, not a reset of this family.

## Locks retained

Custody, candidate freezes, real-support qualification, independent skeptic review, the joint B/C order and once-only rules, and Re's separate written vault execution OK all remain required. Historical source collection before the declaration remains recorded as a timing exception. No reserved sign was read for this amendment.

The controller remains STAGED. The hybrid method must receive its methodological review, and family claim-admission code must be qualified, before activation. Recording a reserved envelope does not bypass those locks. The computational/model-call caps remain unset.
'''

def reserve(root):
    store=Store(root);root=store.root
    directory=root/'budget-amendments'/'v7-joint-alpha-005'
    target=root.parent/'ordered-name-lists-v7c'
    with store.lock():
        state,head,seq=store.load();store.audit(state)
        directory.mkdir(parents=True,exist_ok=True)
        amendment=directory/'AMENDMENT.md'
        if amendment.exists():require(amendment.read_text(encoding='utf-8')==AMENDMENT,'Existing amendment changed')
        else:amendment.write_text(AMENDMENT,encoding='utf-8')
        for name in ('BUDGET.json','JOINT-DECLARATION-FREEZE.json'):
            backup=directory/('v7-before-'+name)
            if not backup.exists():backup.write_bytes((target/name).read_bytes())
        for name in ('BUDGET.json','CONTROL.json','LEDGER.json'):
            backup=directory/('loop-before-'+name)
            if not backup.exists():backup.write_bytes((root/name).read_bytes())
        evidence={str(amendment):filehash(amendment)}
        store.evidence(evidence)
        new=allocate_state(state,evidence,'Re: Let\'s do that; acceptance of proposed alpha_V=.005 reconciliation, with vault closed and loop inactive.')
        if FAMILY not in state['budget'].get('family_envelopes',{}):
            store.commit(new,'reserve_nonrecycling_v7_family_alpha',head,seq)
        current,newhead,_=store.load()
        old_budget=json.loads((directory/'v7-before-BUDGET.json').read_text())
        old_freeze=json.loads((directory/'v7-before-JOINT-DECLARATION-FREEZE.json').read_text())
        budget=old_budget|dict(status='RESERVED_NONRECYCLING_NO_VAULT_AUTHORIZATION',alpha_V=ALPHA,
            recommended_alpha_V=ALPHA,authorised_by='Re accepted proposal in this chat',utc=utc(),
            global_ledger=str(root/'EVENTS.jsonl'),global_ledger_head=newhead,
            amendment=str(amendment),amendment_sha256=filehash(amendment),spend=ALPHA,
            no_refund=True,no_reallocation=True,vault_tests_run=0,
            allocations=dict(B=.0025,C_pool=.0025,C_two_arms_each=.00125,C_three_arms_each=.005/6,C_four_arms_each=.000625),
            method_review_pending=True,family_claim_admission_pending=True)
        freeze=old_freeze|dict(status='ALPHA_AMENDED_AND_RESERVED_VAULT_CLOSED',alpha_V=ALPHA,
            global_ledger=str(root/'EVENTS.jsonl'),budget_spend=ALPHA,amendment_sha256=filehash(amendment),
            prior_freeze_preserved=str(directory/'v7-before-JOINT-DECLARATION-FREEZE.json'),
            locks=[x for x in old_freeze['locks'] if x!='global budget unallocated']+
                ['hybrid error-control methodological review pending','family claim-admission path not qualified'])
        writejson(target/'BUDGET.json',budget);writejson(target/'JOINT-DECLARATION-FREEZE.json',freeze)
        writejson(target/'ALPHA-V-AMENDMENT.json',dict(alpha_V=ALPHA,source=str(amendment),sha256=filehash(amendment),
            vault_execution_authorised=False,loop_active=False,no_refund=True,global_ledger_head=newhead))
        receipt=dict(status='RESERVED_WITH_EXECUTION_LOCKS',alpha_V=ALPHA,online_FDR_target=current['budget']['fdr_target'],
            online_initial_wealth=current['budget']['w0'],next_online_alpha=lord_level(current['budget']),
            project_FDR_target=.05,loop_mode=current['mode'],vault_execution_authorised=False,
            previous_head=head,new_head=newhead,amendment_sha256=filehash(amendment))
        writejson(directory/'RECEIPT.json',receipt)
        return receipt

if __name__=='__main__':
    print(json.dumps(reserve(Path(__file__).resolve().parent),indent=2))
