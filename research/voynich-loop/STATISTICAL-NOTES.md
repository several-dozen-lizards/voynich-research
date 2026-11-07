# Statistical decisions and unresolved qualifications

Checked 24 October 2026 against the onlineFDR maintainers' [theory](https://dsrobertson.github.io/onlineFDR/articles/theory.html) and the original [Ramdas et al. paper](https://arxiv.org/abs/1710.00499).

The implemented LORD++ level is

`alpha_t = w0*gamma(t) + (q-w0)*gamma(t-tau1) + q*sum(gamma(t-tauj), j>=2)`

where only earlier rejection times enter, and absent/nonpositive gamma terms are zero. `gamma(t)=1/(t(t+1))` telescopes to total mass one. Tests compare against hand-computed early levels and rewards. The infinite allocation sequence and reward are deterministic; this is not a simulation of truth labels.

The defaults are proposals, not authority to spend. Alpha is committed before controls and scoring. Every frozen claim occupies one ordered slot; no adaptive batching or concurrent claims are supported. This avoids reordering after outcomes. Qualification-blocked freezes retain their debit and nonrejection slot. A revised protocol is a new freeze, not an edit.

The selected LORD++ version's independent-p-value assumptions have not been established for this project. Shared folios, shared H/F observations, sandbox selection, dependent hypotheses and a repeatedly reused reserve can violate the conditions. Keeping related-look counts does not repair invalid p-values. The statistical reviewer must approve an appropriate sampling/test design or implement a suitable dependence-aware alternative before activation. No project-wide FDR guarantee is claimed by the staged software.

Historical looks are uncertain; the freezer must use a certified count or conservative upper bound, including related tasks under other names. A 20-look prospective cap is per lead and does not erase historical exposure; >50 historical/related looks is still possible. The machine cannot determine semantic relatedness from task IDs. The skeptic receives the declared total and audits that relationship.

An entry marked PASS is a mathematical rejection at the allocated level, not a scientific claim. Promotion additionally requires qualified controls, independent review, Re's decision and required replication. Invalid tests are not repaired by a human override. A conservative freeze policy cannot establish the validity of an intrinsically selected p-value.

The supplied exhaustion rule (30 cycles without a promoted claim) is implemented only for active research checkpoints. A staged setup, blocked queue, outstanding human decision or pending claim pauses instead. The budget cap stops at a checkpoint and the keeper blocks additional costly actions after the cap. A production runner must also terminate already-running subprocesses at their resource limits; the ledger alone cannot stop an external process.

## 25 October: disjoint nonrecycling v7 family

The accepted nominal alpha_V=0.005 is reserved outside the remaining LORD++ stream. Remaining-stream target=0.045, initial wealth=0.020, next alpha=0.010; global nominal FDR target=0.05. No family discovery recycles into online wealth and no unused family share is refunded. See budget-amendments/v7-joint-alpha-005/AMENDMENT.md for the explicit FDP decomposition and validity assumptions. This is a methodological amendment, not a retrospective relabeling of one LORD++ slot. Review and family admission qualification still block activation.
