# Phase 9 audit addendum: duplicate labels and mapping support

This is a post-outcome descriptive audit of saved witnesses only. No fitting, optimizer calls, new shuffle draws, rule changes, registration, or revised significance tests were performed. It supplements the sealed target report and does not replace any result or receipt.

## Shuffle result and its scope

The registered panel statistic remains 5/12 for the observed Occitan positional fit (4/12 for observed Occitan monoalphabetic). Each of the five frozen banks contains 99 shuffles; none reaches 5, giving p=.01 separately in each bank for the full maximum over languages, families, and fixed Naibbe tables. These are repeated Monte Carlo banks on one target, not independent manuscript replications; .01 is each bank's resolution floor. No banks are pooled or selected here.

The null preserves the label multiset, including both May labels, and refits every shuffled assignment by the same search rule. Duplicate May is therefore present on both sides of the registered comparison. Its presence is not an unaccounted difference in label counts, but the panel statistic weights a repeated identical month-label constraint twice. The shuffled result is evidence of association between the assigned month candidates and annotations under this finite matching procedure; it is not evidence of out-of-sample mapping generalization, an annotator language, a historical cipher, or native-script decipherment.

## Duplicate-May contributions and distinct-month support

Month means the candidate month at the destination panel, even if its assigned shuffled annotation originated from another month. Assignment identity includes the position group: B=beginning, M=interior, E=end; A=global monoalphabetic. A shared assignment must occur in at least two distinct matched candidate months. May's two panels count once for support. Repetition within one word or month also counts once. A fully cross-supported month would require every one of its used assignments to occur in another distinct matched month.

| Witness | Family | Saved score | May points | Extra duplicate May point | Distinct matched months | Shared / single-month assignments | Fully cross-supported months |
|---|---|---:|---:|---:|---:|---|---:|
| Observed | mono | 4 | 2 | 1 | 3 | 3 / 5 | 0 |
| Observed | position | 5 | 2 | 1 | 4 | 2 / 12 | 0 |
| 9013/98 | position | 4 | 1 | 0 | 4 | 3 / 12 | 0 |
| 9019/3 | mono | 4 | 2 | 1 | 3 | 3 / 7 | 0 |
| 9019/3 | position | 4 | 2 | 1 | 3 | 3 / 9 | 0 |
| 9019/71 | position | 4 | 2 | 1 | 3 | 0 / 12 | 0 |
| 9041/2 | position | 4 | 2 | 1 | 3 | 0 / 12 | 0 |
| 9041/97 | mono | 4 | 2 | 1 | 3 | 3 / 7 | 0 |
| 9041/97 | position | 4 | 2 | 1 | 3 | 3 / 9 | 0 |

The selected top-null witness is monoalphabetic for 9019/3 and 9041/97; each also has the saved tied positional witness shown above. The five assignments shown are all saved null assignments attaining the global null maximum of four. The other banks peak at three.

Both observed fits receive two points from the identical `mai -> may` match, with the second contributing no new mapping constraint. Four of five top null assignments do likewise; 9013/98 matches only one May panel. These counts describe the saved witnesses. They do not constitute deduplicated reoptimization or recalibrated p-values.

## Mapping generalization boundary

**No matched month is fully cross-supported in any of the nine saved witnesses**, counting both observed fits and all tied top-null models. Every matched month requires at least one assignment used by no other distinct matched month. All shared assignments are identity substitutions; every nonidentity substitution has support from just one distinct candidate month.

For the observed monoalphabetic witness, March uniquely supplies `r -> r`, May `i -> y`, and August `g -> u`, `o -> g`, and `t -> t`. For the observed positional witness, the added June match uniquely supplies B:`i -> j`, M:`u -> o`, M:`n -> n`, and E:`h -> g`. Thus June does not follow entirely from assignments supplied by the other matched months.

This support audit is conditional on each stored optimal witness. It does not enumerate all equally optimal mappings, refit after withholding a month, or test predictions on held-out names. Zero fully supported months limits what can be claimed from these witnesses; it does not establish that every alternative optimum or encoding family lacks predictive ability. Calibration recovery on synthetic controls and the target shuffle association do not fill this generalization gap.

## Per-month assignments lacking support elsewhere

Each entry below lists all assignments unique to that month within that saved witness. Machine-readable support sets for every assignment are retained in AUDIT_ADDENDUM_DATA.json.

| Witness / family | Month | Assignments unique to this month |
|---|---|---|
| Observed / mono | March | `A:r->r` |
| Observed / mono | May | `A:i->y` |
| Observed / mono | August | `A:g->u, A:o->g, A:t->t` |
| Observed / position | March | `E:s->s, M:r->r` |
| Observed / position | May | `E:i->y` |
| Observed / position | June | `B:i->j, E:h->g, M:n->n, M:u->o` |
| Observed / position | August | `B:a->a, E:t->t, M:g->u, M:o->g, M:s->s` |
| 9013/98 / position | March | `E:s->s` |
| 9013/98 / position | May | `E:i->y` |
| 9013/98 / position | July | `B:i->j, E:h->g, M:l->n, M:u->o` |
| 9013/98 / position | October | `B:o->o, E:e->e, M:b->b, M:c->c, M:o->e, M:t->t` |
| 9019/3 / mono | March | `A:s->s` |
| 9019/3 / mono | May | `A:i->y` |
| 9019/3 / mono | November | `A:b->b, A:e->e, A:n->o, A:o->c, A:v->t` |
| 9019/3 / position | March | `E:s->s` |
| 9019/3 / position | May | `E:i->y` |
| 9019/3 / position | November | `B:n->o, E:e->e, M:b->b, M:e->e, M:m->m, M:o->c, M:v->t` |
| 9019/71 / position | April | `B:a->a, E:l->t, M:b->u, M:i->s, M:r->g` |
| 9019/71 / position | May | `B:m->m, E:i->y, M:a->a` |
| 9019/71 / position | June | `B:i->j, E:h->g, M:n->n, M:u->o` |
| 9041/2 / position | April | `B:a->a, E:l->t, M:b->u, M:i->s, M:r->g` |
| 9041/2 / position | May | `B:m->m, E:i->y, M:a->a` |
| 9041/2 / position | July | `B:i->j, E:h->g, M:l->n, M:u->o` |
| 9041/97 / mono | March | `A:s->s` |
| 9041/97 / mono | May | `A:i->y` |
| 9041/97 / mono | November | `A:b->b, A:e->e, A:n->o, A:o->c, A:v->t` |
| 9041/97 / position | March | `E:s->s` |
| 9041/97 / position | May | `E:i->y` |
| 9041/97 / position | November | `B:n->o, E:e->e, M:b->b, M:e->e, M:m->m, M:o->c, M:v->t` |

## Preserved status and receipts

**Native tracks remain CLOSED. Phase 8 remains FAIL.** No target track is opened by this audit. All pre-existing artifacts, including the target manifest, results, original report, filename erratum, calibration records, output seals, and completion receipts, are retained byte-for-byte.

The original calibration strict registration check still fails solely for the previously documented mutable RUN_STATE.json entry. That defect is not repaired or relabeled PASS. The addendum has its own preservation receipt; this is a saved-witness arithmetic and documentation audit, not a new scientific gate or registration.
