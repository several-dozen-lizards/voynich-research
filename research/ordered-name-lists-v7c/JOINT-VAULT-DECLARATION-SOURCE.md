# v7 joint vault declaration: Parts B and C on the reserved zodiac signs

**Written:** 25 Oct 2026 (Reed, for Re). **Freeze and hash this before any Part B or Part C sandbox work begins.**

## Reserved material

| Sign | Folio |
|---|---|
| Virgo | f72v2 |
| Libra | f72v1 |
| Scorpio | f73r |
| Sagittarius | f73v |

Readings H and F are kept separate. **Custody** is per v7 Part B §B1 (`ZODIAC/CUSTODY.md`) and must be completed first. Any sign graded `exposed-to-progression` (for B) or `exposed-to-sequence-or-alignment` (for C) is descriptive only for that hypothesis.

## Hypotheses declared to use the vault (complete list; nothing else may use it)

| ID | Hypothesis | Spec |
|---|---|---|
| **B** | The zodiac label forms encode figure order numerically | v7 Part B §B3–B6 |
| **C-FULL** | Ordered name list, full names | v7 Part C §C3 |
| **C-STEM** | Ordered name list, theophoric suffix removed | v7 Part C §C3 |
| **C-SUF** | Suffix written as Voynich ending S\* | v7 Part C §C3 (runs only if C2 finds S\*) |
| **C-MRK** | Name-class marker M\* standing in for the theophoric element | v7 Part C §C3 (runs only if C2 finds M\*) |

## Error budget (fixed now)

- The total vault α is drawn from the global online budget (ORCHESTRATOR §4) at the moment this declaration is frozen. Call it **α_V**.
- **B gets α_V / 2.**
- **C gets α_V / 2,** split equally across the C arms that are still eligible after C2:
  - NO MARKER → C-FULL and C-STEM, α_V / 4 each;
  - one marker found → three arms, α_V / 6 each;
  - both found → four arms, α_V / 8 each.
- **If B returns NO CANDIDATE** (B3 stop rule), its half is **not** reassigned. It's returned to the global budget, so nothing gets rescued after the fact.
- **The same holds for C arms** that fail qualification or are eliminated at C2.

## Order and once-only rule

1. Both B and C finish their sandbox, freeze and qualification steps **before either vault run**.
2. The vault runs execute **in one session**, in the order **B, then C arms in table order.** Each result is written to the ledger before the next one runs.
3. Each reserved sign × reading is scored **once per hypothesis.** No re-runs. A crash is resumed from saved checkpoints only, never re-scored.
4. **Re's written OK in the ledger is required** before step 2.

## What this prevents

Whichever part runs first would otherwise spend the vault, and the second would be testing on exposed material. Declaring both now, with fixed shares, keeps the reserved signs a single, honestly used held-out set.
