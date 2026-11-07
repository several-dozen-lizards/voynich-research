# Pareto frontier and C12 dominance

A dominates B iff A is no larger on every distance and strictly smaller on at least one; exact stored values, no tolerance, no new scores. All184 existing rows enter the frontier calculation. C12 dominance counts exclude4 C5 reference rows. These are descriptive comparisons of point estimates, without uncertainty/significance or band filtering. Clean and noisy cells compete in the same pool.

Frontier: 23 nominal cells, 17 distinct distance vectors. Equal vectors are grouped below without treating them as independent evidence.

| Frontier cells (equal vectors grouped) | W1 | abs delta h2 | Gain distance |
|---|---:|---:|---:|
| comparison:C15_Latin_52:clean | 0.266799965 | 0.034745004 | 0.046239710 |
| comparison:C15_Latin_78:clean | 0.269494914 | 0.018435407 | 0.056205082 |
| comparison:C15_Italian_52:clean | 0.305920195 | 0.041297070 | 0.039431691 |
| comparison:C15_Italian_78:clean | 0.330000869 | 0.028998734 | 0.052215409 |
| terminal:T08:clean | 0.631110725 | 0.574822743 | 0.008985543 |
| terminal:T14:clean | 0.751861833 | 0.548846862 | 0.008561206 |
| terminal:T14:noise | 0.873567389 | 0.869523649 | 0.007665277 |
| partial:P04:clean | 0.895041873 | 0.524812726 | 0.001278186 |
| partial:P07:clean | 1.134747457 | 0.363702811 | 0.020591712 |
| partial:P08:clean | 1.134747457 | 0.373172621 | 0.011096311 |
| historical:C12_partial_L2_R0_F0.4:clean | 1.245935843 | 0.553927770 | 0.000550961 |
| historical:C12_partial_L2_R0_F0.7:clean | 2.072213046 | 0.336198984 | 0.012666249 |
| partial:P28:clean; partial:P29:clean | 3.076704628 | 0.169703421 | 0.011098981 |
| original:SW09:clean; original:SW10:clean; partial:P37:clean; partial:P38:clean | 3.960416123 | 0.052158982 | 0.029307055 |
| partial:P25:noise | 7.471744928 | 0.007196842 | 0.063639998 |
| original:SW13:clean; partial:P41:clean | 8.316989771 | 0.471306963 | 0.004487538 |
| original:SW12:noise; partial:P40:noise | 8.578382650 | 0.016300021 | 0.015883231 |

## C12 cells dominated by comparator families

| Source grid | C15 | C9 | C18 |
|---|---:|---:|---:|
| original | 8 | 7 | 4 |
| partial | 60 | 46 | 18 |
| historical | 14 | 9 | 0 |
| terminal | 19 | 2 | 0 |
| Total nominal rows | 101 | 64 | 22 |

Counts overlap: every C12 row dominated by C9 or C18 is also dominated by at least one C15 row. Of166 C12 rows,101 are comparator-dominated and65 are not; the latter are not necessarily on the global frontier because other C12 cells can dominate them.

## Exact cells dominated by C15

- original clean: SW14, SW17, SW15
- original noise: SW11, SW09, SW10, SW14, SW17
- partial clean: P03, P05, P06, P10, P11, P12, P09, P13, P14, P15, P19, P20, P21, P17, P16, P18, P30, P24, P23, P22, P33, P31, P32, P27, P26, P42, P36, P35, P45, P43
- partial noise: P03, P06, P10, P11, P12, P09, P13, P15, P19, P20, P21, P17, P16, P18, P30, P39, P37, P38, P22, P23, P24, P32, P31, P33, P26, P27, P42, P35, P36, P45
- historical clean: C12_partial_L2_R0_F0.1, C12_partial_L2_R1_F0.4, C12_partial_L2_R1_F0.55, C12_partial_L2_R0_F0.85, C12_partial_L2_R1_F0.85
- historical noise: C12_partial_L2_R1_F0.1, C12_partial_L2_R1_F0.4, C12_partial_L2_R0_F0.55, C12_partial_L2_R1_F0.55, C12_partial_L2_R0_F0.7, C12_partial_L2_R1_F0.7, C12_partial_L2_R0_F0.85, C12_partial_L2_R1_F0.85, C12_fullbest
- terminal clean: T12, T13, T09, T05, T01, T07, T02, T03
- terminal noise: T12, T13, T09, T04, T05, T01, T15, T11, T07, T02, T03

## Exact cells dominated by C9

- original clean: SW14, SW17, SW15
- original noise: SW09, SW10, SW14, SW17
- partial clean: P09, P13, P15, P19, P20, P21, P17, P16, P18, P23, P22, P33, P31, P32, P27, P26, P42, P36, P35, P45, P43
- partial noise: P10, P11, P09, P13, P15, P19, P20, P21, P17, P16, P18, P30, P37, P38, P22, P24, P32, P31, P33, P26, P27, P42, P35, P36, P45
- historical clean: C12_partial_L2_R1_F0.4, C12_partial_L2_R0_F0.85, C12_partial_L2_R1_F0.85
- historical noise: C12_partial_L2_R1_F0.4, C12_partial_L2_R0_F0.55, C12_partial_L2_R1_F0.55, C12_partial_L2_R1_F0.7, C12_partial_L2_R0_F0.85, C12_partial_L2_R1_F0.85
- terminal noise: T07, T02

## Exact cells dominated by C18

- original clean: SW14, SW17, SW15
- original noise: SW14
- partial clean: P33, P31, P32, P27, P26, P42, P36, P35, P45, P43
- partial noise: P16, P32, P31, P33, P27, P42, P35, P36

## Full comparator-dominance audit

| C12 cell | W1 | abs delta h2 | Gain distance | C15 | C9 | C18 | Exact comparator dominators |
|---|---:|---:|---:|---|---|---|---|
| terminal:T12:clean | 0.606131734 | 0.473860034 | 0.040274215 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T13:clean | 0.606131734 | 0.515245755 | 0.057524276 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T08:clean | 0.631110725 | 0.574822743 | 0.008985543 | False | False | False |  |
| terminal:T09:clean | 0.631110725 | 0.612005649 | 0.060346723 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T04:clean | 0.659596047 | 0.650899067 | 0.025269008 | False | False | False |  |
| terminal:T05:clean | 0.659596047 | 0.683949140 | 0.056778646 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P01:clean | 0.693819004 | 0.734510199 | 0.015836835 | False | False | False |  |
| partial:P02:clean | 0.693819004 | 0.734510199 | 0.015836835 | False | False | False |  |
| terminal:T00:clean | 0.693819004 | 0.734510199 | 0.015836835 | False | False | False |  |
| partial:P03:clean | 0.693819004 | 0.740740598 | 0.090505815 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T01:clean | 0.693819004 | 0.740740598 | 0.090505815 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T12:noise | 0.714713348 | 0.807441631 | 0.040513349 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T13:noise | 0.714713348 | 0.832533509 | 0.062979913 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T08:noise | 0.732715943 | 0.897559393 | 0.036623263 | False | False | False |  |
| terminal:T09:noise | 0.732715943 | 0.918858313 | 0.056519103 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T14:clean | 0.751861833 | 0.548846862 | 0.008561206 | False | False | False |  |
| terminal:T15:clean | 0.751861833 | 0.584429960 | 0.031847262 | False | False | False |  |
| terminal:T04:noise | 0.768183385 | 0.964855324 | 0.050993085 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Latin_52:noise |
| terminal:T05:noise | 0.768183385 | 0.985922404 | 0.056605172 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P01:noise | 0.803656479 | 1.036868865 | 0.030063844 | False | False | False |  |
| partial:P02:noise | 0.803656479 | 1.036868865 | 0.030063844 | False | False | False |  |
| terminal:T00:noise | 0.803656479 | 1.036868865 | 0.030063844 | False | False | False |  |
| partial:P03:noise | 0.803656479 | 1.037237675 | 0.042062354 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T01:noise | 0.803656479 | 1.037237675 | 0.042062354 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T10:clean | 0.829638645 | 0.607193255 | 0.023064208 | False | False | False |  |
| terminal:T11:clean | 0.829638645 | 0.632546469 | 0.037526870 | False | False | False |  |
| historical:C12_partial_L2_R0_F0.1:clean | 0.867541801 | 0.818944388 | 0.066502643 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| historical:C12_partial_L2_R1_F0.1:clean | 0.867541801 | 0.843396019 | 0.028774047 | False | False | False |  |
| terminal:T14:noise | 0.873567389 | 0.869523649 | 0.007665277 | False | False | False |  |
| terminal:T15:noise | 0.873567389 | 0.889465576 | 0.047929120 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean |
| partial:P04:clean | 0.895041873 | 0.524812726 | 0.001278186 | False | False | False |  |
| partial:P05:clean | 0.895041873 | 0.539013949 | 0.082983756 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P06:clean | 0.895041873 | 0.648453563 | 0.080622602 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T06:clean | 0.913993451 | 0.614210502 | 0.008257413 | False | False | False |  |
| terminal:T07:clean | 0.913993451 | 0.680309941 | 0.045819449 | True | False | False | comparison:C15_Italian_52:clean |
| historical:C12_partial_L2_R0_F0.1:noise | 0.953979558 | 1.109920009 | 0.012918925 | False | False | False |  |
| historical:C12_partial_L2_R1_F0.1:noise | 0.954353154 | 1.130760216 | 0.044723344 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T10:noise | 0.974284777 | 0.922472133 | 0.020043397 | False | False | False |  |
| terminal:T11:noise | 0.974284777 | 0.935263164 | 0.044155622 | True | False | False | comparison:C15_Italian_52:clean |
| historical:C12_partial_L2_R0_F0.25:clean | 0.984989423 | 0.661648928 | 0.024194169 | False | False | False |  |
| historical:C12_partial_L2_R1_F0.25:clean | 0.984989423 | 0.716375730 | 0.002870774 | False | False | False |  |
| partial:P04:noise | 1.017018975 | 0.859675454 | 0.028120637 | False | False | False |  |
| partial:P05:noise | 1.017018975 | 0.871180176 | 0.019920516 | False | False | False |  |
| partial:P06:noise | 1.017018975 | 0.949309367 | 0.085970998 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P10:clean | 1.023848851 | 0.636014572 | 0.136350989 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P11:clean | 1.023848851 | 0.636014572 | 0.136350989 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T02:clean | 1.023848851 | 0.636014572 | 0.136350989 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| partial:P12:clean | 1.023848851 | 0.685219960 | 0.066766953 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T03:clean | 1.023848851 | 0.685219960 | 0.066766953 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise |
| terminal:T06:noise | 1.045872070 | 0.929267678 | 0.007225537 | False | False | False |  |
| terminal:T07:noise | 1.045872070 | 0.976051976 | 0.055396056 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| historical:C12_partial_L2_R1_F0.25:noise | 1.118316372 | 1.012908796 | 0.016473651 | False | False | False |  |
| historical:C12_partial_L2_R0_F0.25:noise | 1.128071751 | 0.976268517 | 0.003732419 | False | False | False |  |
| partial:P07:clean | 1.134747457 | 0.363702811 | 0.020591712 | False | False | False |  |
| partial:P08:clean | 1.134747457 | 0.373172621 | 0.011096311 | False | False | False |  |
| partial:P09:clean | 1.134747457 | 0.506282781 | 0.058272052 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P10:noise | 1.155514023 | 0.948923363 | 0.078728127 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P11:noise | 1.155514023 | 0.948923363 | 0.078728127 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| terminal:T02:noise | 1.155514023 | 0.948923363 | 0.078728127 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P12:noise | 1.155514023 | 0.987253702 | 0.044835448 | True | False | False | comparison:C15_Italian_52:clean |
| terminal:T03:noise | 1.155514023 | 0.987253702 | 0.044835448 | True | False | False | comparison:C15_Italian_52:clean |
| historical:C12_partial_L2_R0_F0.4:clean | 1.245935843 | 0.553927770 | 0.000550961 | False | False | False |  |
| historical:C12_partial_L2_R1_F0.4:clean | 1.245935843 | 0.617951078 | 0.072960258 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P08:noise | 1.276123425 | 0.724407836 | 0.003218675 | False | False | False |  |
| partial:P07:noise | 1.276123425 | 0.724545442 | 0.003239465 | False | False | False |  |
| partial:P09:noise | 1.276123425 | 0.807939394 | 0.055374742 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| historical:C12_partial_L2_R1_F0.4:noise | 1.404383975 | 0.921844490 | 0.064242387 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| historical:C12_partial_L2_R0_F0.4:noise | 1.416769366 | 0.882232994 | 0.034603667 | False | False | False |  |
| historical:C12_partial_L2_R0_F0.55:clean | 1.596482077 | 0.460329895 | 0.020805335 | False | False | False |  |
| historical:C12_partial_L2_R1_F0.55:clean | 1.596482077 | 0.525876282 | 0.049423957 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean |
| historical:C12_partial_L2_R0_F0.55:noise | 1.770559371 | 0.798131061 | 0.064826798 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| historical:C12_partial_L2_R1_F0.55:noise | 1.770944276 | 0.838090669 | 0.053104043 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P13:clean | 1.894665160 | 0.290373553 | 0.181094098 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P14:clean | 1.894665160 | 0.297323223 | 0.044024158 | True | False | False | comparison:C15_Italian_52:clean |
| partial:P15:clean | 1.894665160 | 0.472659779 | 0.063169932 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P13:noise | 2.071722687 | 0.651192552 | 0.089651513 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P14:noise | 2.071722687 | 0.661063312 | 0.025493932 | False | False | False |  |
| partial:P15:noise | 2.071722687 | 0.781296797 | 0.051892352 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Latin_52:noise;comparison:C9:noise |
| historical:C12_partial_L2_R0_F0.7:clean | 2.072213046 | 0.336198984 | 0.012666249 | False | False | False |  |
| historical:C12_partial_L2_R1_F0.7:clean | 2.072213046 | 0.409030432 | 0.030540299 | False | False | False |  |
| partial:P19:clean | 2.227274044 | 0.325749889 | 0.065315127 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:clean |
| partial:P20:clean | 2.227274044 | 0.325749889 | 0.065315127 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:clean |
| partial:P21:clean | 2.227274044 | 0.396802264 | 0.078918672 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| historical:C12_partial_L2_R0_F0.7:noise | 2.247308815 | 0.707150583 | 0.041446900 | True | False | False | comparison:C15_Italian_52:clean |
| historical:C12_partial_L2_R1_F0.7:noise | 2.251847508 | 0.737269347 | 0.056736445 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P19:noise | 2.400554232 | 0.691424966 | 0.060222650 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P20:noise | 2.400554232 | 0.691424966 | 0.060222650 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| partial:P21:noise | 2.400554232 | 0.727339908 | 0.063499141 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P17:clean | 2.909791649 | 0.063530891 | 0.148017621 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P16:clean | 2.909791649 | 0.116837890 | 0.145118117 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P18:clean | 2.909791649 | 0.378751584 | 0.075204587 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| historical:C12_partial_L2_R0_F0.85:clean | 2.970906140 | 0.188255476 | 0.116557431 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| historical:C12_partial_L2_R1_F0.85:clean | 2.970906140 | 0.250859540 | 0.081809354 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P28:clean | 3.076704628 | 0.169703421 | 0.011098981 | False | False | False |  |
| partial:P29:clean | 3.076704628 | 0.169703421 | 0.011098981 | False | False | False |  |
| partial:P30:clean | 3.076704628 | 0.195874450 | 0.049984908 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean |
| partial:P17:noise | 3.130773258 | 0.462084005 | 0.078007102 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P16:noise | 3.130773258 | 0.507683126 | 0.176594043 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean;comparison:C18_bigraph2:clean |
| partial:P18:noise | 3.130773258 | 0.665098840 | 0.057445073 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| historical:C12_partial_L2_R0_F0.85:noise | 3.163007318 | 0.576352023 | 0.059178948 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise |
| historical:C12_partial_L2_R1_F0.85:noise | 3.168566891 | 0.581112866 | 0.068573499 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P30:noise | 3.282617651 | 0.549903927 | 0.060958314 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P28:noise | 3.282617651 | 0.562735854 | 0.019588447 | False | False | False |  |
| partial:P29:noise | 3.282617651 | 0.562735854 | 0.019588447 | False | False | False |  |
| original:SW09:clean | 3.960416123 | 0.052158982 | 0.029307055 | False | False | False |  |
| original:SW10:clean | 3.960416123 | 0.052158982 | 0.029307055 | False | False | False |  |
| partial:P37:clean | 3.960416123 | 0.052158982 | 0.029307055 | False | False | False |  |
| partial:P38:clean | 3.960416123 | 0.052158982 | 0.029307055 | False | False | False |  |
| historical:C12_fullbest:clean | 3.960416123 | 0.078879735 | 0.033979821 | False | False | False |  |
| original:SW11:clean | 3.960416123 | 0.078879735 | 0.033979821 | False | False | False |  |
| partial:P39:clean | 3.960416123 | 0.078879735 | 0.033979821 | False | False | False |  |
| historical:C12_fullbest:noise | 4.169879137 | 0.426963160 | 0.044689775 | True | False | False | comparison:C15_Italian_52:clean |
| original:SW11:noise | 4.169879137 | 0.426963160 | 0.044689775 | True | False | False | comparison:C15_Italian_52:clean |
| partial:P39:noise | 4.169879137 | 0.426963160 | 0.044689775 | True | False | False | comparison:C15_Italian_52:clean |
| original:SW09:noise | 4.169879137 | 0.470552342 | 0.068865800 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| original:SW10:noise | 4.169879137 | 0.470552342 | 0.068865800 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P37:noise | 4.169879137 | 0.470552342 | 0.068865800 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P38:noise | 4.169879137 | 0.470552342 | 0.068865800 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean |
| partial:P24:clean | 4.635399461 | 0.022645082 | 0.060967708 | True | False | False | comparison:C15_Latin_78:clean |
| partial:P23:clean | 4.635399461 | 0.114953321 | 0.062950540 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P22:clean | 4.635399461 | 0.180243462 | 0.119185185 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P22:noise | 4.869327836 | 0.264889541 | 0.102957511 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P23:noise | 4.869327836 | 0.304169431 | 0.053672624 | True | False | False | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean |
| partial:P24:noise | 4.869327836 | 0.365861872 | 0.064768720 | True | True | False | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:clean |
| partial:P33:clean | 6.542843896 | 0.112394544 | 0.072467613 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P31:clean | 6.542843896 | 0.383052082 | 0.254301643 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean;comparison:C18_addB:clean;comparison:C18_addB:noise |
| partial:P32:clean | 6.542843896 | 0.392905830 | 0.097975802 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean;comparison:C18_addB:clean;comparison:C18_addB:noise |
| partial:P32:noise | 6.780246704 | 0.074102452 | 0.081781173 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P31:noise | 6.780246704 | 0.099603290 | 0.136267495 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P33:noise | 6.780246704 | 0.255585553 | 0.079755330 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P27:clean | 7.198325075 | 0.118067172 | 0.077082729 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P26:clean | 7.198325075 | 0.435390244 | 0.076707602 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P25:clean | 7.198325075 | 0.492346358 | 0.035839319 | False | False | False |  |
| partial:P25:noise | 7.471744928 | 0.007196842 | 0.063639998 | False | False | False |  |
| partial:P26:noise | 7.471744928 | 0.032878193 | 0.066016603 | True | True | False | comparison:C15_Latin_78:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P27:noise | 7.471744928 | 0.241762297 | 0.089449716 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| original:SW14:clean | 8.316989771 | 0.192860224 | 0.069225860 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P42:clean | 8.316989771 | 0.192860224 | 0.069225860 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| original:SW13:clean | 8.316989771 | 0.471306963 | 0.004487538 | False | False | False |  |
| partial:P41:clean | 8.316989771 | 0.471306963 | 0.004487538 | False | False | False |  |
| original:SW12:clean | 8.316989771 | 0.526135223 | 0.011755276 | False | False | False |  |
| partial:P40:clean | 8.316989771 | 0.526135223 | 0.011755276 | False | False | False |  |
| original:SW12:noise | 8.578382650 | 0.016300021 | 0.015883231 | False | False | False |  |
| partial:P40:noise | 8.578382650 | 0.016300021 | 0.015883231 | False | False | False |  |
| original:SW13:noise | 8.578382650 | 0.039008046 | 0.041813111 | False | False | False |  |
| partial:P41:noise | 8.578382650 | 0.039008046 | 0.041813111 | False | False | False |  |
| original:SW14:noise | 8.578382650 | 0.161374156 | 0.083389831 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P42:noise | 8.578382650 | 0.161374156 | 0.083389831 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P36:clean | 10.092207830 | 0.101205462 | 0.064142680 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P34:clean | 10.092207830 | 0.643046161 | 0.007499337 | False | False | False |  |
| partial:P35:clean | 10.092207830 | 0.660965097 | 0.205137324 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_78:noise;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C9:clean;comparison:C18_bigraph2:clean;comparison:C18_addB:clean;comparison:C18_addB:noise |
| partial:P34:noise | 10.403449103 | 0.108521054 | 0.038818860 | False | False | False |  |
| partial:P35:noise | 10.403449103 | 0.156384894 | 0.114921927 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P36:noise | 10.403449103 | 0.185475446 | 0.084290433 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| original:SW17:clean | 12.753426642 | 0.250188265 | 0.073425794 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| partial:P45:clean | 12.753426642 | 0.250188265 | 0.073425794 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Latin_78:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C9:clean;comparison:C18_addB:clean |
| original:SW15:clean | 12.753426642 | 0.721322765 | 0.055814719 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C18_addB:clean |
| partial:P43:clean | 12.753426642 | 0.721322765 | 0.055814719 | True | True | True | comparison:C15_Latin_52:clean;comparison:C15_Italian_52:clean;comparison:C15_Italian_78:clean;comparison:C15_Latin_52:noise;comparison:C15_Italian_52:noise;comparison:C15_Italian_78:noise;comparison:C9:noise;comparison:C18_addB:clean |
| original:SW16:clean | 12.753426642 | 0.770884138 | 0.035372186 | False | False | False |  |
| partial:P44:clean | 12.753426642 | 0.770884138 | 0.035372186 | False | False | False |  |
| original:SW17:noise | 13.018935585 | 0.029478869 | 0.079403925 | True | True | False | comparison:C15_Latin_78:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| partial:P45:noise | 13.018935585 | 0.029478869 | 0.079403925 | True | True | False | comparison:C15_Latin_78:clean;comparison:C15_Italian_78:clean;comparison:C9:clean |
| original:SW15:noise | 13.018935585 | 0.180685989 | 0.019086576 | False | False | False |  |
| partial:P43:noise | 13.018935585 | 0.180685989 | 0.019086576 | False | False | False |  |
| original:SW16:noise | 13.018935585 | 0.190382976 | 0.035505033 | False | False | False |  |
| partial:P44:noise | 13.018935585 | 0.190382976 | 0.035505033 | False | False | False |  |

No earlier results, registrations, output hashes or terminal-family rules were changed. No model, new corpus scoring, parameter selection, normalization or sweep was run. Historical mixed-codebook cells retain their original labels and limitations.
