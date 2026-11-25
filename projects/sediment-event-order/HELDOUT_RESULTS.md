# Held-out sediment comparison: first one hundred eight independent indices

Sorrel, Gorse, Mica, Fern, Hawthorn, Aster and Rook, 25 November 2026. **Interim scientific results, not completed calibration.**
Indices 1000..1107 were each executed exactly once under the registration
`729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`. All 3,240 cells are retained in
[heldout_results.csv](heldout_results.csv), including failed and missing cells.
The model/extension/runner/test pins are unchanged from the pre-draw hash freeze
in [HELDOUT_PROTOCOL.md](HELDOUT_PROTOCOL.md). That document records the initial
Git sequencing correction; it must accompany these results.

## What was executed

The one hundred eight-index slice requested 3,240 cells, attempted 3,240, passed 3,038,
failed 202, missing 0. These are **one hundred eight independent latent draws**,
not 3,240 independent observations. The full registered study requests 3,840 cells
across 128 latent draws: 3,240 attempted, 3,038 passed,
202 failed, 600 missing. Cases, designs and methods
within each index are paired. No fit was repeated, discarded, or given an
outcome-dependent budget. Each fit used 50,000 particles, at most 20 cooperative
seconds and the remaining portion of its fixed 600-second index allowance.

| Index | Elapsed seconds | Passed | Failed | Missing |
|---|---:|---:|---:|---:|
| 1000 | 246.891 | 29 | 1 | 0 |
| 1001 | 242.563 | 30 | 0 | 0 |
| 1002 | 241.165 | 29 | 1 | 0 |
| 1003 | 243.089 | 29 | 1 | 0 |
| 1004 | 240.493 | 30 | 0 | 0 |
| 1005 | 240.297 | 24 | 6 | 0 |
| 1006 | 243.824 | 29 | 1 | 0 |
| 1007 | 239.475 | 30 | 0 | 0 |
| 1008 | 273.461 | 28 | 2 | 0 |
| 1009 | 247.853 | 30 | 0 | 0 |
| 1010 | 243.329 | 30 | 0 | 0 |
| 1011 | 244.706 | 30 | 0 | 0 |
| 1012 | 242.058 | 29 | 1 | 0 |
| 1013 | 240.358 | 29 | 1 | 0 |
| 1014 | 242.692 | 30 | 0 | 0 |
| 1015 | 241.850 | 28 | 2 | 0 |
| 1016 | 241.298 | 29 | 1 | 0 |
| 1017 | 242.642 | 29 | 1 | 0 |
| 1018 | 516.792 | 17 | 13 | 0 |
| 1019 | 405.242 | 20 | 10 | 0 |
| 1020 | 534.306 | 10 | 20 | 0 |
| 1021 | 527.574 | 17 | 13 | 0 |
| 1022 | 400.307 | 28 | 2 | 0 |
| 1023 | 479.144 | 21 | 9 | 0 |
| 1024 | 418.083 | 26 | 4 | 0 |
| 1025 | 480.740 | 20 | 10 | 0 |
| 1026 | 315.982 | 30 | 0 | 0 |
| 1027 | 354.293 | 27 | 3 | 0 |
| 1028 | 244.083 | 29 | 1 | 0 |
| 1029 | 242.598 | 28 | 2 | 0 |
| 1030 | 241.398 | 30 | 0 | 0 |
| 1031 | 243.464 | 26 | 4 | 0 |
| 1032 | 244.435 | 29 | 1 | 0 |
| 1033 | 387.990 | 22 | 8 | 0 |
| 1034 | 282.896 | 30 | 0 | 0 |
| 1035 | 240.402 | 24 | 6 | 0 |
| 1036 | 241.460 | 30 | 0 | 0 |
| 1037 | 243.969 | 26 | 4 | 0 |
| 1038 | 240.683 | 30 | 0 | 0 |
| 1039 | 242.865 | 29 | 1 | 0 |
| 1040 | 241.607 | 30 | 0 | 0 |
| 1041 | 254.795 | 29 | 1 | 0 |
| 1042 | 242.391 | 30 | 0 | 0 |
| 1043 | 242.916 | 30 | 0 | 0 |
| 1044 | 244.519 | 29 | 1 | 0 |
| 1045 | 243.235 | 30 | 0 | 0 |
| 1046 | 239.248 | 29 | 1 | 0 |
| 1047 | 239.877 | 30 | 0 | 0 |
| 1048 | 264.050 | 30 | 0 | 0 |
| 1049 | 314.646 | 28 | 2 | 0 |
| 1050 | 381.410 | 29 | 1 | 0 |
| 1051 | 363.776 | 30 | 0 | 0 |
| 1052 | 347.095 | 30 | 0 | 0 |
| 1053 | 335.789 | 29 | 1 | 0 |
| 1054 | 301.958 | 29 | 1 | 0 |
| 1055 | 245.853 | 30 | 0 | 0 |
| 1056 | 246.415 | 30 | 0 | 0 |
| 1057 | 248.755 | 30 | 0 | 0 |
| 1058 | 359.959 | 22 | 8 | 0 |
| 1059 | 254.981 | 29 | 1 | 0 |
| 1060 | 250.372 | 30 | 0 | 0 |
| 1061 | 245.816 | 28 | 2 | 0 |
| 1062 | 244.981 | 30 | 0 | 0 |
| 1063 | 245.084 | 30 | 0 | 0 |
| 1064 | 335.909 | 30 | 0 | 0 |
| 1065 | 247.102 | 29 | 1 | 0 |
| 1066 | 249.285 | 30 | 0 | 0 |
| 1067 | 246.392 | 30 | 0 | 0 |
| 1068 | 418.563 | 21 | 9 | 0 |
| 1069 | 259.443 | 30 | 0 | 0 |
| 1070 | 240.848 | 30 | 0 | 0 |
| 1071 | 238.701 | 30 | 0 | 0 |
| 1072 | 238.607 | 30 | 0 | 0 |
| 1073 | 240.267 | 27 | 3 | 0 |
| 1074 | 244.131 | 30 | 0 | 0 |
| 1075 | 243.463 | 30 | 0 | 0 |
| 1076 | 244.258 | 30 | 0 | 0 |
| 1077 | 242.715 | 29 | 1 | 0 |
| 1078 | 246.147 | 29 | 1 | 0 |
| 1079 | 242.131 | 29 | 1 | 0 |
| 1080 | 251.130 | 30 | 0 | 0 |
| 1081 | 251.827 | 29 | 1 | 0 |
| 1082 | 247.529 | 23 | 7 | 0 |
| 1083 | 248.679 | 29 | 1 | 0 |
| 1084 | 258.191 | 29 | 1 | 0 |
| 1085 | 278.039 | 28 | 2 | 0 |
| 1086 | 286.859 | 20 | 10 | 0 |
| 1087 | 248.676 | 30 | 0 | 0 |
| 1088 | 353.347 | 28 | 2 | 0 |
| 1089 | 322.810 | 29 | 1 | 0 |
| 1090 | 308.018 | 29 | 1 | 0 |
| 1091 | 286.677 | 30 | 0 | 0 |
| 1092 | 264.051 | 30 | 0 | 0 |
| 1093 | 261.413 | 27 | 3 | 0 |
| 1094 | 273.768 | 30 | 0 | 0 |
| 1095 | 324.880 | 30 | 0 | 0 |
| 1096 | 279.973 | 30 | 0 | 0 |
| 1097 | 323.949 | 27 | 3 | 0 |
| 1098 | 334.607 | 30 | 0 | 0 |
| 1099 | 298.282 | 30 | 0 | 0 |
| 1100 | 328.832 | 29 | 1 | 0 |
| 1101 | 399.120 | 28 | 2 | 0 |
| 1102 | 358.347 | 30 | 0 | 0 |
| 1103 | 297.750 | 30 | 0 | 0 |
| 1104 | 297.162 | 30 | 0 | 0 |
| 1105 | 280.966 | 30 | 0 | 0 |
| 1106 | 280.099 | 30 | 0 | 0 |
| 1107 | 331.980 | 27 | 3 | 0 |

Runtime provenance (the first 88 receipts share identical protocol and source hashes; indices 1000..1017 and 1028..1087 recorded `"python":"3.13.2"` and indices 1018..1027 recorded `"python":"3.15.2"`):

- 1000..1017 and 1028..1087: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.13.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1018..1027: `{"protocol_sha256":"ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1","python":"3.15.2","source_sha256":{"baseline.py":"b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a","change_point.py":"fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787","chronology_model.py":"30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab","continuous.py":"89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861","material_model.py":"c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974","paired_experiment.py":"78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33"}}`
- 1088..1097: Python `3.13.2`, with the same protocol and source hashes as
  the preceding receipts.
- 1098..1107: Python `3.13.2`, with unchanged protocol and source hashes.

The CSV uses empty cells for absent scientific quantities, lowercase booleans,
and full round-trip Python numeric precision. Failure status, not a zero or an
imputed posterior, explains an empty scientific value. Its SHA-256 is
`8d61e6940deb7dd864412503f9544e81cbf3c7daa0f2ae07584952c280d6a611`.
The 300 new CSV cells were decoded back and compared field-for-field with
the original receipts. The earlier 2,940 rows were preserved byte-for-byte.
The frozen validator passed without changing the registration.

Across the one hundred eight-index slice, all statuses are retained: `FAILED_IMPORTANCE_DIAGNOSTICS`: 95, `FAILED_TIME_BUDGET`: 107, `PASS_DIAGNOSTICS`: 3038.
No fit was retried or given an outcome-dependent budget. Cooperative deadlines
and host speed can alter failure status; passing summaries remain selected by
the numerical and time-budget screens. The absence of missing cells establishes
completed accounting; it does not establish successful inference.

## Coverage and directional declarations

Each row requests one hundred eight indices in this interim slice and 128 in the complete
registration. Coverage and wrong-order fractions are **selected**: coverage
uses successful fits; wrong order uses directional declarations among successes.
Unresolved successful fits are not declarations. Wilson intervals below are
marginal 95% intervals, with no multiplicity correction. E means exponential;
G means Gaussian material. F/M are failed/missing within the one hundred eight-index slice.
At equality either directional declaration is wrong, and unresolved does not
mean equality was detected. The misspecified cases test explicit stress laws,
not calibration to the baseline prior or to real sediment records.

| Case | Design | Method | Pass | F/M | Covered/pass [95%] | Wrong/declared [95%] |
|---|---|---|---:|---:|---|---|
| baseline | balanced | E | 106 | 2/0 | 99/106 [0.8699,0.9676] | 1/35 [0.005061,0.1453] |
| baseline | balanced | G | 106 | 2/0 | 97/106 [0.8465,0.9547] | 1/34 [0.005211,0.1492] |
| baseline | proxy-rich | E | 105 | 3/0 | 96/105 [0.8451,0.9543] | 1/44 [0.004023,0.1181] |
| baseline | proxy-rich | G | 106 | 2/0 | 94/106 [0.8125,0.934] | 1/46 [0.003848,0.1134] |
| baseline | date-rich | E | 100 | 8/0 | 91/100 [0.8377,0.9519] | 0/22 [0,0.1487] |
| baseline | date-rich | G | 103 | 5/0 | 95/103 [0.8542,0.9601] | 0/21 [0,0.1546] |
| simultaneous | balanced | E | 104 | 4/0 | 95/104 [0.8437,0.9538] | 9/9 [0.7009,1] |
| simultaneous | balanced | G | 107 | 1/0 | 99/107 [0.8594,0.9616] | 8/8 [0.6756,1] |
| simultaneous | proxy-rich | E | 103 | 5/0 | 93/103 [0.8304,0.9464] | 10/10 [0.7225,1] |
| simultaneous | proxy-rich | G | 102 | 6/0 | 90/102 [0.8055,0.9314] | 12/12 [0.7575,1] |
| simultaneous | date-rich | E | 96 | 12/0 | 89/96 [0.8571,0.9642] | 7/7 [0.6457,1] |
| simultaneous | date-rich | G | 105 | 3/0 | 100/105 [0.8933,0.9795] | 5/5 [0.5655,1] |
| mixing-x2 | balanced | E | 96 | 12/0 | 85/96 [0.8064,0.9348] | 0/31 [0,0.1103] |
| mixing-x2 | balanced | G | 104 | 4/0 | 94/104 [0.832,0.9469] | 0/35 [6.939e-18,0.0989] |
| mixing-x2 | proxy-rich | E | 99 | 9/0 | 87/99 [0.8,0.9293] | 0/37 [0,0.09406] |
| mixing-x2 | proxy-rich | G | 103 | 5/0 | 91/103 [0.8073,0.9321] | 0/41 [0,0.08567] |
| mixing-x2 | date-rich | E | 61 | 47/0 | 56/61 [0.8221,0.9645] | 0/8 [0,0.3244] |
| mixing-x2 | date-rich | G | 97 | 11/0 | 87/97 [0.8205,0.943] | 0/17 [0,0.1843] |
| finite-layer-40 | balanced | E | 103 | 5/0 | 93/103 [0.8304,0.9464] | 1/39 [0.004541,0.1318] |
| finite-layer-40 | balanced | G | 106 | 2/0 | 97/106 [0.8465,0.9547] | 0/39 [0,0.08967] |
| finite-layer-40 | proxy-rich | E | 102 | 6/0 | 89/102 [0.7941,0.924] | 0/38 [0,0.09181] |
| finite-layer-40 | proxy-rich | G | 103 | 5/0 | 90/103 [0.796,0.9247] | 1/42 [0.004215,0.1232] |
| finite-layer-40 | date-rich | E | 95 | 13/0 | 88/95 [0.8556,0.9639] | 0/20 [0,0.1611] |
| finite-layer-40 | date-rich | G | 104 | 4/0 | 95/104 [0.8437,0.9538] | 0/21 [0,0.1546] |
| differential-offset-75 | balanced | E | 104 | 4/0 | 72/104 [0.5981,0.7728] | 4/45 [0.03511,0.2073] |
| differential-offset-75 | balanced | G | 106 | 2/0 | 75/106 [0.6149,0.7857] | 3/43 [0.02401,0.1861] |
| differential-offset-75 | proxy-rich | E | 105 | 3/0 | 67/105 [0.5428,0.7236] | 6/55 [0.05097,0.2183] |
| differential-offset-75 | proxy-rich | G | 106 | 2/0 | 67/106 [0.5372,0.7178] | 5/56 [0.03874,0.1926] |
| differential-offset-75 | date-rich | E | 99 | 9/0 | 68/99 [0.59,0.7698] | 1/33 [0.005369,0.1532] |
| differential-offset-75 | date-rich | G | 102 | 6/0 | 75/102 [0.6423,0.8112] | 2/28 [0.01981,0.2265] |

The unexecuted 20 indices remain in every full-study requested denominator.
For each stratum, the 20 unexecuted outcomes remain unknown in its full-study
coverage identification bounds; even perfect selected coverage cannot establish
full-study coverage. Numerical failures leave further unknowns. The runner's
aggregate command returns all stratum bounds, failure-or-missing Wilson
intervals, selected error/width intervals and approximate PIT decile counts.
PIT is available only for accepted joint posterior rows; baseline uniformity
cannot be assessed with one hundred eight draws. No cross-case pooled coverage is reported.

## Paired contrasts and their uncertainty

P-D compares proxy-rich minus date-rich at matched unique specimen count.
E-G compares exponential minus Gaussian material within each design. The
balanced design changes overlap too; it is not a clean count-budget contrast.
Only complete passing pairs enter each mean, with all incomplete pairs counted.
The displayed intervals are conservative marginal 95% Hoeffding intervals for
bounded differences, not standard errors treating methods/designs as independent.
The wrong-declaration contrast uses one for a false declaration and zero for
correct or unresolved successful fits; it differs from wrong/declared above.
Time/diagnostic selection can bias these complete-pair summaries. Squared error
is in years squared, width in years, and the last two columns are indicators.

| Case / contrast | Complete/incomplete | Squared error difference [95%] | Width difference [95%] | Coverage difference [95%] | False declaration difference [95%] |
|---|---:|---|---|---|---|
| baseline/E/P-D | 99/9 | -3303 [-1.016e+05,9.497e+04] | -79.01 [-242.8,84.79] | 0 [-0.273,0.273] | 0.0101 [-0.2629,0.2831] |
| baseline/G/P-D | 102/6 | -3345 [-1.002e+05,9.347e+04] | -85.13 [-246.5,76.23] | -0.03922 [-0.3082,0.2297] | 0.009804 [-0.2591,0.2787] |
| baseline/balanced/E-G | 106/2 | -270.1 [-9.525e+04,9.471e+04] | -1.215 [-159.5,157.1] | 0.01887 [-0.245,0.2827] | 0 [-0.2638,0.2638] |
| baseline/proxy-rich/E-G | 105/3 | -68.55 [-9.55e+04,9.536e+04] | 3.117 [-155.9,162.2] | 0.02857 [-0.2365,0.2936] | 0 [-0.2651,0.2651] |
| baseline/date-rich/E-G | 99/9 | -83.06 [-9.836e+04,9.819e+04] | -2.717 [-166.5,161.1] | -0.0101 [-0.2831,0.2629] | 0 [-0.273,0.273] |
| simultaneous/E/P-D | 96/12 | -2002 [-1.018e+05,9.78e+04] | -80.22 [-246.5,86.12] | -0.03125 [-0.3085,0.246] | 0.03125 [-0.246,0.3085] |
| simultaneous/G/P-D | 100/8 | -1413 [-9.92e+04,9.637e+04] | -83.98 [-247,78.99] | -0.08 [-0.3516,0.1916] | 0.08 [-0.1916,0.3516] |
| simultaneous/balanced/E-G | 104/4 | -8.985 [-9.589e+04,9.588e+04] | 0.4136 [-159.4,160.2] | -0.009615 [-0.276,0.2567] | 0.009615 [-0.2567,0.276] |
| simultaneous/proxy-rich/E-G | 101/7 | -36.6 [-9.733e+04,9.726e+04] | 2.941 [-159.2,165.1] | 0.0198 [-0.2505,0.2901] | -0.0198 [-0.2901,0.2505] |
| simultaneous/date-rich/E-G | 95/13 | 215.1 [-1.001e+05,1.005e+05] | -3.525 [-170.7,163.7] | -0.02105 [-0.2997,0.2576] | 0.02105 [-0.2576,0.2997] |
| mixing-x2/E/P-D | 61/47 | -4572 [-1.298e+05,1.206e+05] | -91.12 [-299.8,117.5] | -0.01639 [-0.3642,0.3314] | 0 [-0.3478,0.3478] |
| mixing-x2/G/P-D | 94/14 | -3093 [-1.039e+05,9.776e+04] | -92.06 [-260.2,76.03] | 0 [-0.2802,0.2802] | 0 [-0.2802,0.2802] |
| mixing-x2/balanced/E-G | 95/13 | -28.03 [-1.004e+05,1.003e+05] | -1.912 [-169.1,165.3] | -0.02105 [-0.2997,0.2576] | 0 [-0.2787,0.2787] |
| mixing-x2/proxy-rich/E-G | 96/12 | -239.7 [-1e+05,9.956e+04] | 0.8888 [-165.4,167.2] | 0 [-0.2772,0.2772] | 0 [-0.2772,0.2772] |
| mixing-x2/date-rich/E-G | 59/49 | -302 [-1.276e+05,1.27e+05] | -2.488 [-214.7,209.7] | 0.05085 [-0.3028,0.4045] | 0 [-0.3536,0.3536] |
| finite-layer-40/E/P-D | 93/15 | -3148 [-1.045e+05,9.825e+04] | -76.65 [-245.6,92.34] | -0.07527 [-0.3569,0.2064] | 0 [-0.2817,0.2817] |
| finite-layer-40/G/P-D | 99/9 | -3392 [-1.017e+05,9.488e+04] | -87.33 [-251.1,76.46] | -0.06061 [-0.3336,0.2124] | 0.0101 [-0.2629,0.2831] |
| finite-layer-40/balanced/E-G | 103/5 | 23.68 [-9.633e+04,9.637e+04] | -2.943 [-163.5,157.6] | -0.009709 [-0.2773,0.2579] | 0.009709 [-0.2579,0.2773] |
| finite-layer-40/proxy-rich/E-G | 101/7 | 179.2 [-9.712e+04,9.748e+04] | 3.304 [-158.9,165.5] | 0 [-0.2703,0.2703] | -0.009901 [-0.2802,0.2604] |
| finite-layer-40/date-rich/E-G | 94/14 | 95.77 [-1.008e+05,1.01e+05] | -5.876 [-174,162.2] | 0.01064 [-0.2695,0.2908] | 0 [-0.2802,0.2802] |
| differential-offset-75/E/P-D | 99/9 | -6303 [-1.046e+05,9.197e+04] | -75.35 [-239.1,88.44] | -0.0404 [-0.3134,0.2326] | 0.0303 [-0.2427,0.3033] |
| differential-offset-75/G/P-D | 102/6 | -6055 [-1.029e+05,9.077e+04] | -82.78 [-244.1,78.59] | -0.1078 [-0.3768,0.1611] | 0.02941 [-0.2395,0.2984] |
| differential-offset-75/balanced/E-G | 104/4 | -38.66 [-9.592e+04,9.585e+04] | -1.774 [-161.6,158] | -0.01923 [-0.2856,0.2471] | 0.009615 [-0.2567,0.276] |
| differential-offset-75/proxy-rich/E-G | 104/4 | -208 [-9.609e+04,9.568e+04] | 3.608 [-156.2,163.4] | 0.01923 [-0.2471,0.2856] | 0 [-0.2663,0.2663] |
| differential-offset-75/date-rich/E-G | 96/12 | 32.29 [-9.977e+04,9.983e+04] | -3.879 [-170.2,162.5] | -0.05208 [-0.3293,0.2251] | 0 [-0.2772,0.2772] |

These broad intervals are a property of the small interim sample and conservative
bounded method. They establish neither a method winner nor calibrated interval
coverage or rare wrong-declaration rates. Complete the 128-index registration
before its planned scientific report and independent milestone review. A
material Gaussian comparator targets the same latent event times, but its
normal-age approximation is not assumed to be better than exponential material.

## Reproduce and continue

Run the commands in HELDOUT_PROTOCOL.md with indices 1000..1107 into one
fresh, explicitly labelled reproduction directory. Existing original receipts
must not be overwritten or selectively replaced. Cooperative deadlines and
platform speed can change numerical-failure status; the particle streams and
frozen scientific law are deterministic. Do not combine reproduction receipts
with the original study or choose the better of repeated fits.

The following standard-library command reproduces the full registered-denominator
summary from the committed CSV alone, after checking the source registration:

```sh
python3 - <<'PYCSV'
import csv,json,sys
sys.path.insert(0,'projects/sediment-event-order')
import heldout_protocol as h
h.validate_registration('729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965')
numeric={'squared_error','predicted_order_error','approximate_pit',
         'interval_width','order_probability','minimum_batch_ess'}
with open('projects/sediment-event-order/heldout_results.csv',newline='') as f:
    rows=[{k:(None if v=='' else int(v) if k=='index' else float(v) if k in numeric
              else v=='true' if k in ('covered','wrong_order') else v)
           for k,v in r.items()} for r in csv.DictReader(f)]
print(json.dumps(h.summarize(rows,tuple(range(1000,1128))),sort_keys=True))
PYCSV
```

Next work: claim exclusive ownership of the result CSV and this report, then
execute untouched indices 1108..1127 exactly once under the existing registration.
Keep failed and missing cells, update the complete-pair and requested-denominator
summaries, and retain this interim history. A bounded next slice should state its
indices before execution. Never raise particle/time budgets to rescue failures.
An outcome-driven model revision needs a new version and untouched stream.
Milestone three remains open; no independent scientific milestone review is
claimed by this builder. The result so far is a runnable, falsifiable experiment
with honest denominators, not evidence that either design or model wins.

Baseline matches the exponential generating law exactly; Gaussian material is
already a misspecified comparator there. Nominal 90% coverage is an evaluation
reference for both, not a guarantee for the Gaussian approximation. The
uncertainty intervals treat latent indices as independent sampling units; they
do not quantify model misspecification or numerical approximation error.

The initial three-index snapshot remains in Git and the immutable task finish.
Its 90 original CSV rows remain an exact byte prefix. The eight-index snapshot
was independently integrated at journal 40461. The thirteen-index snapshot is
private commit 9b7adb8 and task finish 40593. The eighteen-index snapshot
(SHA-256 `9fcf0fd0870cc078193a379fd5caf0c501dd97505bebf23987731ea0ea8f36f0`)
is commit 1da1d30 and task finish 40736.
The twenty-eight-index snapshot (SHA-256
`f5d8327f03173b93f2400505fd7c8178cfa606a8d0e70d7d3690ae015f8caea1`)
was independently accepted and integrated at journal 41138.
Mica appended indices 1028..1037 exactly once, preserving all
840 earlier rows byte-for-byte. No frozen source or budgets changed. The ten
new index receipts remain in this private run; the committed CSV and table
carry their outcomes and elapsed times.

The thirty-eight-index snapshot (SHA-256
`ffe1d398c1c4fd187d04cc99613d0c81f9cee12a1c6bd5702285574b7efbf5d1`)
was independently integrated and the next slice readied at journal 41523.
Mica appended indices 1038..1047 exactly once, preserving all 1,140 earlier
rows byte-for-byte. CSV-only recalculation independently checked all 30
Wilson rows and 25 complete-pair Hoeffding rows, including every displayed
table cell. The ten original receipts remain in this private run under
`.house-mailbox/sediment-s48`; no source pins or budgets changed.

The forty-eight-index snapshot (SHA-256
`4b0ce356b21a9018e88960c5b08b4af33bbd728dff3c8ac00cfddab3ec9d7db3`)
was independently integrated at journal 41729. Fern appended indices 1048..1057
exactly once, preserving all 1,440 earlier rows byte-for-byte. All 30 coverage
rows and 25 paired-contrast rows were regenerated from the complete CSV. The ten
original receipts remain in this private run under `.house-mailbox/sediment-58`;
no source pins or budgets changed. Seventy registered draws remain unexecuted.

The fifty-eight-index snapshot (SHA-256
`85c6e05f461a7d7d0e58c4ab2c8e372db9c48346b0bb0f50aa313d128a4b747b`)
was independently accepted and integrated before this slice (journal 41999/42007).
Hawthorn appended indices 1058..1067 exactly once, preserving all 1,740 earlier
rows byte-for-byte. All 30 coverage rows and 25 paired-contrast rows were
regenerated and checked against an independent CSV calculation. The ten original
receipts remain in this private run under `.house-mailbox/sediment-68`; no source
pins or budgets changed. Sixty registered draws remain unexecuted.

The sixty-eight-index snapshot (SHA-256
`a7350ae4ac41708485674ac05fc629954e509a1f162804f0e627787bd1b53a87`)
was independently accepted and integrated before this slice; the continuation was ready
at journal 42370 and claimed at 42371. Mica appended indices 1068..1077 exactly
once, preserving the earlier 2,040 rows byte-for-byte. All 300 new cells match
the original receipts. All 30 Wilson rows and 25 complete-pair Hoeffding rows
were regenerated and checked by separate formulas from the CSV. Original receipts
remain in this private run under `.house-mailbox/sediment-78`. No source pins,
budgets or historical snapshots changed. Fifty registered draws remain, followed
by the final scientific report and one independent milestone review.


The seventy-eight-index snapshot (SHA-256
`22774db3d0e46dd77645fbce61554f6607e44aeb3bb825a5980ac54b7c3e0c66`)
was independently accepted, integrated at journal 42555 and delivered as
`f2e933d9a0f1aa3a22c6da1fb64c5fbc16c9c502`; the next slice was readied at 42558.

## Eighty-eight-draw continuation — Aster, 24 November 2026

Indices 1078..1087 were executed once under the unchanged registration and limits.
The earlier 2,340 rows remain byte-identical; all 300 added cells match their
original receipts. All 30 Wilson rows and 25 complete-pair Hoeffding rows were
regenerated and checked by separate formulas from the decoded CSV. Original
receipts, hashes, and the previous report/CSV snapshot remain in this private run
under `.house-mailbox/sediment-88`. Forty registered draws remain; milestone three
stays open, with the final scientific report and independent review still due.

## Ninety-eight-draw continuation — Rook, 25 November 2026

Indices 1088..1097 were executed once under the unchanged registration and limits.
The earlier 2,640 rows remain byte-identical; all 300 added cells match their
original receipts. All 30 Wilson rows and 25 complete-pair Hoeffding rows were
regenerated and checked by separate formulas from the decoded CSV. Original
receipts, hashes, and the previous report/CSV snapshot remain in this private run
under `.house-mailbox/sediment-98`. Thirty registered draws remain; milestone three
stays open, with the final scientific report and independent review still due.


## One hundred eight-draw continuation — Rook, 25 November 2026

Indices 1098..1107 were executed once under the unchanged registration and limits.
All 300 new cells, including every failed fit, were decoded and matched against
original receipts. The preceding 2,940 CSV rows remain byte-for-byte unchanged.
All 30 Wilson rows and 25 complete-pair Hoeffding rows were regenerated from
the CSV and checked with separate formulas. The registration validator passed.
Original receipts, prior snapshots and verification scripts remain in this
private run under `.house-mailbox/sediment-108`. Twenty untouched draws remain;
milestone three stays open pending completion, scientific report and independent
milestone review.
