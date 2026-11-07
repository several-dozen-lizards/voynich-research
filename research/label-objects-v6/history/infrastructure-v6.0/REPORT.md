# Label-to-object dataset v6 — infrastructure checkpoint

Built on 24 October 2026. Object ratings, label geometry and claim tests remain uncompleted.

The source ledger contains **1,062 candidate EVT loci** across all available readings.
H/F have **1,076 separate reading rows**. There are 323 loci on
currently available exact single-page canvases; other loci retain explicit panel-registration exclusions.
Every unit type was audited, including lowercase pharma codes and letters/titles/radial inscriptions.
Reserved Virgo, Libra, Scorpio and Sagittarius folios are excluded. No word was assigned a meaning.

**The planned pharma H/F headline cannot be estimated from this EVT.** Pharma is named
“Recipes” in Davis metadata: H has 230 rows; F has only 2, of which 1 is fully readable.
The threshold requires at least two classes of 30 labels each. This source-level upper bound
does not depend on object judgments. Other sections still need registration and actual ratings.

T2 has 5,086 mechanically matched candidate records, including repeated words and pages.
These are not 5,086 independent pairs. The earlier nine records contain eleven supplied
source/target page pairs; these are flagged. Other earlier visual/text exposures remain to be
audited before a primary fresh subset can be certified. No image-choice trials have been run.

## What is built

* Source-linked locus inventory, unit decisions, counts per section/type/reading, and H/F feature ledger.
* Header-only registrar input with native canvas hashes; no object descriptions or transcription bodies.
* Geometry validator, fixed-context crop/thumbnail packet builder, independent-vote validator,
  pre-adjudication kappa gate and guarded join.
* Nested physical-folio CV engine, training-only feature preprocessing, peer-page baseline,
  within-page permutation pipeline and per-reading Holm correction. No manuscript run.
* Exact candidate-match list and preserved prior-nine evidence.
* Multilingual historical comparator search with access/coverage limits in HISTORICAL-COMPARATORS.md.

## What remains

The claim freeze is deliberately marked INCOMPLETE: the existing word-shape class definition
has not been found; T2 needs a frozen independent-trial schedule and primary-reading convention.
The historical catalogues do not supply a word-shape class inventory. No new feature has been
passed off as an existing one.

All labels are currently UNREGISTERED. The v4 geometry is paragraph geometry and is not reused.
An independent registrar must inspect source images and submit writing boxes; unavailable
foldout panels require exact native-canvas registration. Two independent raters then receive
only anonymous image stimuli plus MANUAL.md. Models must use fresh plain API calls, without
tools or agent harness; different families or a human are required. No compatible two-family
rater setup was established in this session. Empty RATER files are templates, not observations.

The four-way collapse retains only paired votes within CELESTIAL/PLANT/VESSEL/FIGURE-WATER;
ROSETTE/ANIMAL/OTHER/NONE/UNCLEAR remain in the full-class gate. Exclusions are reported.
Actual scientific controls, including repeated power and confound-null qualification, are outstanding.
T2 also needs independently attached drawing crops and complete writing masks before rating.

## Reproduce and continue

`python build.py` rebuilds source infrastructure only while no outcome join exists.
`python verify.py` verifies engineering and boundaries; it is not a power study.
`python workflow.py geometry independent-registration.json` validates supplied blind geometry.
`python workflow.py packet` creates image-only rater stimuli for accepted boxes.
`python workflow.py agreement` computes actual independent A/B agreement.
`python workflow.py join` and `python t1.py` refuse incomplete claim freezes and missing gates.

The current FREEZE.json is an infrastructure hash seal. It is **not** a completed claim preregistration.
Do not flip the status flag manually. Resolve definitions, implement/qualify the remaining protocol,
then issue a versioned claim freeze before joining any object outcomes. Previous research folders
and v4 owners are untouched.

A T1 association can support referential information but does not identify meanings or exclude
all scribal/register explanations. A T2 similarity preference does not establish species identity.
An unestimable result is not evidence against naming labels.
