# Recorded run (milestone 1)

Commands run 2026-11-23 in this directory, Python 3.13.2, standard library only.

## python3 blurred_tracks.py

```
Frozen example: kappa=1, omega=3.9, D=1 (s=1), Delta=1, eps=0.5, ell^2=0.04
True dissipation sigma = 2 omega^2/kappa = 30.420000
  gamma_0 = +1.3654518813 +0.0000000000i
  gamma_1 = -0.4532838837 -0.3005538693i
  gamma_2 = +0.0450073398 +0.1949522206i
  gamma_3 = +0.0373063812 -0.0634506099i
  gamma_4 = -0.0260168349 +0.0075057636i
Recovered phi = -0.2670555704 -0.2530150303i, kappa = 1.0000000000
Branches m in [-200, 200]: compatible = [1]
  m=1: omega=3.9000000000  s=1.0000000000  ell^2=0.0400000000  sigma=30.420000
Nearest excluded branch by phase: m=0, |phase residual|=0.274177 rad, sigma would be 11.359
Branches excluded by ell^2 < 0 alone: 399 of 401
```

## python3 verify_blurred.py

```
[ok] quadrature vs closed form, k=0..3 (max abs err 2.26e-07)
  all-integer phase candidates: [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
    m=-8: phase residual -4.82e-01, ell^2 -0.540600, sigma 5543.764
    m=-7: phase residual +5.45e-01, ell^2 -0.179794, sigma 4299.516
    m=-6: phase residual -4.71e-01, ell^2 -0.533665, sigma 3213.181
    m=-5: phase residual +5.61e-01, ell^2 -0.183749, sigma 2284.760
    m=-4: phase residual -4.48e-01, ell^2 -0.520116, sigma 1514.252
    m=-3: phase residual +5.96e-01, ell^2 -0.191826, sigma 901.659
    m=-2: phase residual -3.87e-01, ell^2 -0.482049, sigma 446.978
    m=-1: phase residual +7.32e-01, ell^2 -0.215814, sigma 150.212
    m=0: phase residual +2.74e-01, ell^2 +0.056947, sigma 11.359
    m=1: phase residual +2.26e-07, ell^2 +0.040000, sigma 30.420
    m=2: phase residual -7.16e-01, ell^2 -0.654534, sigma 207.395
    m=3: phase residual +3.81e-01, ell^2 -0.130275, sigma 542.283
    m=4: phase residual -6.08e-01, ell^2 -0.607356, sigma 1035.085
    m=5: phase residual +4.33e-01, ell^2 -0.147801, sigma 1685.800
    m=6: phase residual -5.77e-01, ell^2 -0.591929, sigma 2494.429
    m=7: phase residual +4.54e-01, ell^2 -0.154307, sigma 3460.972
[ok] exactly one compatible branch (true m=1) (compatible: [1])
[ok] Monte Carlo vs closed form, k=0..2 (abs errs ['0.0045', '0.0114', '0.0030'], N=30000 frames)
[ok] dissipation via simulated current velocity (MC 30.81 vs exact 30.42)
[ok] equilibrium control: only m=0, sigma=0 
[ok] vanishing exposure: F, Z -> 1 (|F-1|=1.35e-08, |Z-1|=3.33e-05 at eps=1e-4)
[ok] point-sampling near-degeneracy at eps=1e-4 (all branches nearly pass phase) (max |residual| 4.19e-08 for m in -3..3)
FAILED: none — all checks passed
```

## python3 -m pytest -q test_blurred_tracks.py

```
..........                                                               [100%]
10 passed in 0.01s
```

## Milestone 2: python3 verify_general.py

```
[ok] quadrature vs augmented-exponential formulas (max abs err 2.13e-07)
[ok] isotropic special case matches milestone 1 (max abs err 8.88e-16; sigma 30.420000 vs 30.42)
[ok] propagator recovered as Gamma_2 Gamma_1^{-1} (max abs err 2.22e-16)
  compatible branches in [-60, 60]: [(0, 0.03000000000000036, 4.770381836945305)]
  smallest symmetry residual among excluded: 0.576 (m=-3)
[ok] only true branch compatible in window 
  NOTE: |m| > 60 tail and real-eigenvalue logarithms are open; see DERIVATION.md section 7.
FAILED: none — all checks passed
```

## python3 -m pytest -q (both test files)

```
................                                                         [100%]
16 passed in 0.01s
```
