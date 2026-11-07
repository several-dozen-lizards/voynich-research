RETROSPECTIVE — all material exposed or uncertified (v100/v102).

V2 passed calibration in both readings. The qualified manuscript test detected no within-scribe heterogeneity: H rawp=.8343, F rawp=.7097, conservative Holm2p=1 for both. This is not evidence of constant strength: planted+.12 power is only38.0%–43.0%, and the descriptive τ² intervals are broad.

| Reading | Largest required-null upper bound | Previously failing section-baseline control | Planted-positive power range |
|---|---|---|---|
| H | 2.188% | 112/10000=1.120%, CI[0.826%,1.480%] | 38.5%–43.0% |
| F | 2.077% | 145/10000=1.450%, CI[1.112%,1.853%] | 38.0%–40.6% |

All required-null upper bounds are below2.5% under these authored controls, stronger than the frozen5% practical-tolerance requirement. No nominal alarms occurred. These statements concern this qualification run, not universal nominal calibration.

The old failure has an analytic explanation as well as the saved simulation diagnosis. For a binomial margin with n=1, the R1 half-count plug-in variance product is always.1875. True Bernoulli variance is.24 at p=.40 and.25 at p=.50, but.09 at p=.10. Thus the same regularizer understates uncertainty for high baselines while overstating it for rare baselines. The exact expected R1 variance ratios below reproduce the observed control pattern.

| Context | H expected R1 variance / true variance | F expected R1 variance / true variance |
|---|---|---|
| C1 | 1.1445 | 1.1459 |
| C2 | 0.8438 | 0.8442 |
| C3 | 0.9823 | 0.9789 |
| C4 | 1.0164 | 1.0165 |
| C5 | 0.8839 | 0.8867 |

The generating variances are known in the old synthetic control. Substituting them brought chi-square rejection rates to2.44% H/2.16% F, whereas changing only the reference with the old working variance left3.78% H/3.38% F. Re-labeling also produced somewhat lower critical values, but reference replacement alone was insufficient. This diagnostic uses old outcomes, not fresh qualification; V2 qualification uses independent new coordinates.

Context effects remain the original aggregate MH contrasts. The supplemental table below uses the original descriptive bootstrap CIs unchanged; it is not another set of section tests.

| Context | H effect [original descriptive95% CI], points | F effect [original descriptive95% CI], points |
|---|---|---|
| C1 | +9.800 [+4.813,+15.263] | +8.734 [+4.185,+13.622] |
| C2 | +5.012 [-2.216,+13.862] | +5.710 [-0.296,+12.563] |
| C3 | +7.414 [+2.807,+10.921] | +7.898 [+4.380,+11.453] |
| C4 | +10.469 [+6.594,+14.388] | +9.853 [+6.258,+13.590] |
| C5 | +10.346 [+4.785,+17.914] | +4.298 [-0.203,+15.126] |

For both readings, working-model τ² estimates are zero and I² estimates are zero. The Q-profile upper bounds permit between-context standard deviations up to approximately 6.27 points H and 8.88 points F. The scientific strength-variation question therefore remains unresolved; zero point estimates do not establish homogeneity.

No earlier result was rewritten: original B-Q2 and R1 remain unqualified. The larger-of-two-variances rule was frozen before fresh support/controls, and no controls or thresholds were revised after results.

V2 fixed-baseline replacement. All prior attempts and their statuses remain unchanged. Qualification was frozen and completed before any V2 manuscript statistic; failed/inconclusive readings remain unscored.

The R1 diagnosis identified variance bias: the old tiny-margin working variance was~16% too small in C2 and~11–12% too small in C5 under the failed unequal-baseline null. Its fixed chi-square flags were189H/169F per5000, versus122H/108F with known generating variances. Simply switching reference was insufficient. DIAGNOSIS.json retains all context ratios and observed/reference quantiles. This was exploratory diagnosis of old controls, not fresh qualification.

V2 keeps raw MH effects. It estimates baseline uncertainty within each fixed context and prefix, using squared event-coefficient weights and effective sample size. It takes the larger of that pooled binomial variance and leverage-adjusted folio HC3 variance. Context membership is fixed; no baseline relabeling occurs. Chi-square3 is an approximate Gaussian working-model reference, not an exact finite-sample binary/clustered theorem. Fresh real-support qualification tests the approximation.

| Reading | Qualification | Manuscript status | Adjusted p |
|---|---|---|---|
| H | QUALIFIED CALIBRATION | NO DETECTION | 1 |
| F | QUALIFIED CALIBRATION | NO DETECTION | 1 |

| Reading | Scenario | Flags/N | Simultaneous exact interval | Decision | Nominal alarm |
|---|---|---|---|---|---|
| H | homogeneous_null | 133/10000 | [1.007%, 1.718%] | CERTIFIED BELOW TOLERANCE | False |
| H | homogeneous_positive | 124/10000 | [0.929%, 1.616%] | CERTIFIED BELOW TOLERANCE | False |
| H | scribe_baseline_homogeneous | 121/10000 | [0.903%, 1.582%] | CERTIFIED BELOW TOLERANCE | False |
| H | section_baseline_homogeneous | 112/10000 | [0.826%, 1.480%] | CERTIFIED BELOW TOLERANCE | False |
| H | available_homogeneous | 65/10000 | [0.432%, 0.935%] | CERTIFIED BELOW TOLERANCE | False |
| H | folio_baseline_homogeneous | 81/10000 | [0.563%, 1.122%] | CERTIFIED BELOW TOLERANCE | False |
| H | stratum_baseline_homogeneous | 63/10000 | [0.416%, 0.911%] | CERTIFIED BELOW TOLERANCE | False |
| H | folio_effect_homogeneous | 175/10000 | [1.376%, 2.188%] | CERTIFIED BELOW TOLERANCE | False |
| H | heterogeneous_positive | 859/2000 | [39.574%, 46.372%] | DESCRIPTIVE POWER | False |
| H | available_heterogeneous_positive | 843/2000 | [38.785%, 45.567%] | DESCRIPTIVE POWER | False |
| H | section_baseline_heterogeneous_positive | 769/2000 | [35.147%, 41.829%] | DESCRIPTIVE POWER | False |
| F | homogeneous_null | 125/10000 | [0.938%, 1.627%] | CERTIFIED BELOW TOLERANCE | False |
| F | homogeneous_positive | 132/10000 | [0.998%, 1.707%] | CERTIFIED BELOW TOLERANCE | False |
| F | scribe_baseline_homogeneous | 127/10000 | [0.955%, 1.650%] | CERTIFIED BELOW TOLERANCE | False |
| F | section_baseline_homogeneous | 145/10000 | [1.112%, 1.853%] | CERTIFIED BELOW TOLERANCE | False |
| F | available_homogeneous | 77/10000 | [0.530%, 1.076%] | CERTIFIED BELOW TOLERANCE | False |
| F | folio_baseline_homogeneous | 80/10000 | [0.555%, 1.111%] | CERTIFIED BELOW TOLERANCE | False |
| F | stratum_baseline_homogeneous | 76/10000 | [0.522%, 1.064%] | CERTIFIED BELOW TOLERANCE | False |
| F | folio_effect_homogeneous | 165/10000 | [1.288%, 2.077%] | CERTIFIED BELOW TOLERANCE | False |
| F | heterogeneous_positive | 813/2000 | [37.308%, 44.054%] | DESCRIPTIVE POWER | False |
| F | available_heterogeneous_positive | 779/2000 | [35.638%, 42.335%] | DESCRIPTIVE POWER | False |
| F | section_baseline_heterogeneous_positive | 760/2000 | [34.706%, 41.373%] | DESCRIPTIVE POWER | False |

Fixed qualification:8 nulls×10,000 and3 positives×2,000 per supported reading,172,000 total if both supported. Twenty-two simultaneous exact Clopper–Pearson intervals, full denominators retained. Required-null U≤5% and no L>2.5% nominal alarm; failures and intervals spanning5% remain blocked/inconclusive. No alarm is not proof of exact nominal size. Power is descriptive under the original B-Q2 rule. No extension, retuning, seed replacement or old/new pooling occurred.

H: T=0.863046, df3, rawp=0.834335, conservative Holm2p=1, NO DETECTION.
H working-model descriptive random effects, separate scribe means: {'tau2': 0.0, 'Q_profile95': [0.0, 0.003932702988223262], 'I2': 0, 'df': 3, 'working_model_descriptive': True}.
H context raw effects (points): [9.800306224130944, 5.012127283317723, 7.414414073284736, 10.468907487606053, 10.34605043569637]; pooled variances=[0.0006382278090921458, 0.0012403316143210366, 0.0018961572185187893, 0.000363785322719763, 0.002528746260029076]; HC3=[0.0007716262224071826, 0.0020386616090132008, 0.0005156493346993943, 0.0004195895753273445, 0.001517818047733902]; used=[0.0007716262224071826, 0.0020386616090132008, 0.0018961572185187893, 0.0004195895753273445, 0.002528746260029076].

F: T=1.38241, df3, rawp=0.709664, conservative Holm2p=1, NO DETECTION.
F working-model descriptive random effects, separate scribe means: {'tau2': 0.0, 'Q_profile95': [0.0, 0.007893709660410286], 'I2': 0, 'df': 3, 'working_model_descriptive': True}.
F context raw effects (points): [8.73382401489621, 5.710128801840731, 7.898008609870229, 9.852948890345862, 4.29809056509173]; pooled variances=[0.000652614218367836, 0.0012185093909665306, 0.0022123914462482196, 0.0003552730399077141, 0.0028602824083488825]; HC3=[0.000687005435759344, 0.0014539889219858718, 0.0005160623142813206, 0.00037177859137142385, 0.0009442019870657713]; used=[0.000687005435759344, 0.0014539889219858718, 0.0022123914462482196, 0.00037177859137142385, 0.0028602824083488825].

Holm2 per reading retains a conservative inactive historical B-Q1 slotp1; historical B-Q1 tests and families remain unchanged. H/F are alternate readings and were never pooled. Uniform outcome configurations are non-estimable, not negative evidence. There is no inner permutation/Monte Carlo uncertainty in V2 p-values.

NO DETECTION does not establish a uniform-strength rule. Read power and τ² intervals: weak sensitivity or broad intervals leave heterogeneity unresolved. C1/C4 were selected for large earlier effects, and all material is exposed. No new scribe2-only sensitivity tests were transported into qualified status.

The pooled estimate uses squared-coefficient-weighted rates; the half-count/effective-N correction is a regularized working estimate, not an exact Bayesian posterior for weighted observations. The Jensen statement concerns the true baseline, not guaranteed coverage of the plug-in. HC3 protection and a maximum of variances are safeguards, not a universal theorem. See [statsmodels HC3 documentation](https://www.statsmodels.org/v0.13.5/generated/statsmodels.regression.linear_model.RegressionResults.HC3_se.html), [R weighted covariance correction](https://stat.ethz.ch/CRAN/doc/manuals/r-patched/packages/stats/refman/stats.html), and [primary permutation research](https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests).

Controls retain the five R1 nulls including physically availability-preserving equal aggregate effects. Added nulls vary folio/stratum baselines and include correlated folio-level effect fluctuations with equal context expectations. Positives include unequal-baseline heterogeneity. These authored controls cover specific relationships at the actual support; arbitrary text dependence or nuisance structures are not proven calibrated. No semantics, sounds, glyph merges, causal explanation or prospective confirmation follows.

Prior non-cache files and phase hashes were checked before and after. Original manuscript raw context effects replayed where scoring was permitted. ENGINEERING.json and POSTRUN-AUDIT.json retain independent scalar checks, boundary fixtures and old zero-case replays. No raw EVT or reserved zodiac material was opened.
