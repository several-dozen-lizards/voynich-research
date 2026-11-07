# v7 joint vault alpha amendment

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
