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

## Milestone-3 pilot: python3 finite_record.py

```
Frozen: R=24 tracks x N in (1000, 4000, 16000), seed base 424242, substeps=20/exposure
      N  true wins  median gap (rad)  median rel. sigma err
   1000   21/24                0.199                  0.109
   4000   24/24                0.250                  0.035
  16000   24/24                0.268                  0.026
```

## Completeness + real-eigenvalue: python3 completeness_general.py && python3 real_eigenvalue.py

```
[ok] eigenbasis Sigma_m matches augmented-exponential route (max abs err 3.50e-11, m in [-6,6])
[ok] parity 0: R is quadratic in m (rel err 1.36e-12; A2=35.201691)
[ok] parity 0: leading coefficient nonzero 
  parity 0: real roots ['-0.2819', '-0.0000']
[ok] parity 1: R is quadratic in m (rel err 6.20e-13; A2=-0.369865)
[ok] parity 1: leading coefficient nonzero 
  parity 1: real roots ['-0.1721', '-3.5505']
  integer roots of R over all m: [0]
[ok] only the true branch m=0 has R(m)=0 over all integers 
FAILED: none — all checks passed
frozen real-eigenvalue example: sigma = 0.071014
[ok] dissipates despite symmetric drift 
[ok] primary log recovers A (eigenvalues 0.5731, 0.2202; max err 2.66e-15)
[ok] exp(log Phi) = Phi (max err 1.11e-16)
[ok] Sigma, Dm, ell^2, sigma all reconstructed (sigma_rec 0.071014)
[ok] negative eigenvalue refused, not silently logged 
FAILED: none — all checks passed
```

## Ratio scan: python3 ratio_scan.py

```
 eps/Delta   compatible (all m)   nearest rival |residual|
       1/4                  [1]                     0.0313
       1/3                  [1]                     0.0023
       2/5                  [1]                     0.0045
       1/2                  [1]                     0.2742
       3/4                  [1]                     0.0642
         1                  [1]                     0.3062
```

## Section 11 loopholes: python3 real_logs.py && python3 singular_cases.py && python3 completeness_rational.py

[ok] distinct positive: unique real log recovers A (max err 2.7e-15)
[ok] no real logarithm: mixed signs (a negative eigenvalue has no conjugation-closed branch)
[ok] no real logarithm: both negative distinct (a negative eigenvalue has no conjugation-closed branch)
[ok] no real logarithm: negative Jordan block (single Jordan block on a negative eigenvalue)
[ok] defective positive: unique real log recovers A and fits (max err 8.9e-16)
[ok] scalar negative (beta=pi truth): Phi is scalar (Phi00=-0.3679, offdiag 8.7e-19)
[ok] scalar negative (beta=pi truth): true drift passes compatibility (sigma 24.7708)
[ok] scalar negative (beta=pi truth): every scanned family member is a real log of Phi (exp(A_c Delta) = Phi asserted on the grid)
[ok] scalar negative (beta=pi truth): only the true drift passes on grid (12 passes; min rival symmetry residual 0.0120)
[ok] scalar positive (beta=2pi truth): Phi is scalar (Phi00=+0.3679, offdiag 2.8e-17)
[ok] scalar positive (beta=2pi truth): true drift passes compatibility (sigma 99.0831)
[ok] scalar positive (beta=2pi truth): every scanned family member is a real log of Phi (exp(A_c Delta) = Phi asserted on the grid)
[ok] scalar positive (beta=2pi truth): only the true drift passes on grid (12 passes; min rival symmetry residual 0.0419)
FAILED: none — all checks passed
[ok] det(UW) = f(mu1) f(mu2) and |f| closed form (max err 4.4e-16, incl. a defective A)
[ok] all branch candidates m in [-60,60] have nonsingular U_m W_m (min |f(mu_m)| 2.770e-06; > 0 for all m by Re mu < 0)
[ok] seeded sweep of stable drifts: det Gamma_1 never 0 (min |det Gamma_1| 7.768e-04 over the sweep)
[ok] near-singular regime is conditioning, not singularity (|f| 2.60e-06 at kappa*eps=0.0225, omega*eps=2pi; |det Gamma_1| 6.01e-08 > 0)
[ok] manufactured singular Gamma_1 is refused with a reason 
FAILED: none — all checks passed
[ok] eps/Delta=1/3: eigenbasis R matches direct route (max err 3.5e-12, period 3 residue classes)
[ok] class 0 mod 3: R quadratic, A2 != 0 (rel err 4.5e-12, A2=35.20169)
[ok] class 1 mod 3: R quadratic, A2 != 0 (rel err 1.0e-12, A2=0.25529)
[ok] class 2 mod 3: R quadratic, A2 != 0 (rel err 1.9e-12, A2=-0.74332)
[ok] eps/Delta=1/3: only integer root of R over all m is the truth (integer roots [0])
[ok] irrational rho: R changes sign at arbitrarily large m (15278 sign changes up to m=20000, last at m=19999)
[ok] irrational rho: |R(m)|/m^2 arbitrarily small for large m (min over m>10000 is 1.62e-05 at m=17524; no finite window)
  absolute min |R| by window: 1-100: 3.7, 100-1000: 113.2, 1000-5000: 5238.3
  reading: symmetry alone admits no finite candidate list and no
  uniform (relative) margin at irrational eps/Delta; absolute
  residuals here still grow (~m), because the golden ratio is
  badly approximable -- the finite-window question at fixed
  absolute tolerance is Diophantine in rho, not settled here;
  exact large-m roots would be codimension-one coincidences, not
  excluded by finiteness -- recorded as the honest remainder.
FAILED: none — all checks passed

## Tests: python3 -m pytest -q
25 passed

## Milestone 3a branch sets: python3 branch_sets.py

Frozen s8 design: R=24, N in (1000, 4000, 16000), seed base 424242; true branch m=1, sigma=30.42
N=1000: (true-branch estimated ell2 < 0 in 4/24)
  [phase-only]       tau=0.01 (tau=0.0100 rad): coverage 21/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]       tau=0.03 (tau=0.0300 rad): coverage 21/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]        tau=0.1 (tau=0.1000 rad): coverage 23/24, median set size 1 (max 2), median rel. sigma spread 0.000
  [phase-only] tau=1.0/sqrt(N) (tau=0.0316 rad): coverage 21/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only] tau=3.0/sqrt(N) (tau=0.0949 rad): coverage 23/24, median set size 1 (max 2), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.01 (tau=0.0100 rad): coverage 17/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.03 (tau=0.0300 rad): coverage 17/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]        tau=0.1 (tau=0.1000 rad): coverage 19/24, median set size 1 (max 2), median rel. sigma spread 0.000
  [ell2>=0] tau=1.0/sqrt(N) (tau=0.0316 rad): coverage 17/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0] tau=3.0/sqrt(N) (tau=0.0949 rad): coverage 19/24, median set size 1 (max 2), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.01 (tau=0.0100 rad): coverage 19/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.03 (tau=0.0300 rad): coverage 19/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]        tau=0.1 (tau=0.1000 rad): coverage 21/24, median set size 1 (max 2), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=1.0/sqrt(N) (tau=0.0316 rad): coverage 19/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=3.0/sqrt(N) (tau=0.0949 rad): coverage 21/24, median set size 1 (max 2), median rel. sigma spread 0.000
N=4000: (true-branch estimated ell2 < 0 in 4/24)
  [phase-only]       tau=0.01 (tau=0.0100 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]       tau=0.03 (tau=0.0300 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]        tau=0.1 (tau=0.1000 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only] tau=1.0/sqrt(N) (tau=0.0158 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only] tau=3.0/sqrt(N) (tau=0.0474 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.01 (tau=0.0100 rad): coverage 20/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.03 (tau=0.0300 rad): coverage 20/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]        tau=0.1 (tau=0.1000 rad): coverage 20/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0] tau=1.0/sqrt(N) (tau=0.0158 rad): coverage 20/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0] tau=3.0/sqrt(N) (tau=0.0474 rad): coverage 20/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.01 (tau=0.0100 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.03 (tau=0.0300 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]        tau=0.1 (tau=0.1000 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=1.0/sqrt(N) (tau=0.0158 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=3.0/sqrt(N) (tau=0.0474 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
N=16000: (true-branch estimated ell2 < 0 in 0/24)
  [phase-only]       tau=0.01 (tau=0.0100 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]       tau=0.03 (tau=0.0300 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only]        tau=0.1 (tau=0.1000 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only] tau=1.0/sqrt(N) (tau=0.0079 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [phase-only] tau=3.0/sqrt(N) (tau=0.0237 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.01 (tau=0.0100 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]       tau=0.03 (tau=0.0300 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0]        tau=0.1 (tau=0.1000 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0] tau=1.0/sqrt(N) (tau=0.0079 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=0] tau=3.0/sqrt(N) (tau=0.0237 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.01 (tau=0.0100 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]       tau=0.03 (tau=0.0300 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02]        tau=0.1 (tau=0.1000 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=1.0/sqrt(N) (tau=0.0079 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000
  [ell2>=-0.02] tau=3.0/sqrt(N) (tau=0.0237 rad): coverage 24/24, median set size 1 (max 1), median rel. sigma spread 0.000

## Milestone 3b two exposures: python3 two_exposures.py

Population level:
eps/Delta=0.333: nearest rival m=11 |residual|=0.0023 rad; tau=0.01 set = [1]
eps/Delta=0.500: nearest rival m=0 |residual|=0.2742 rad; tau=0.01 set = [1]
intersection of tau=0.01 sets: [1]
combined margin (min over rivals of max residual): 0.2742 rad
Finite records:
N=1000:
  tau=0.03: eps/Delta=1/3 [coverage 9/24, median size 1 (max 5)]; 1/2 [coverage 13/24, median size 1 (max 2)]; intersection [coverage 6/24, median size 0 (max 1)], empty 14/24; joint-max [coverage 12/24, median size 1 (max 1)], empty 7/24
  tau=0.1: eps/Delta=1/3 [coverage 13/24, median size 2 (max 10)]; 1/2 [coverage 14/24, median size 1 (max 2)]; intersection [coverage 9/24, median size 1 (max 1)], empty 10/24; joint-max [coverage 12/24, median size 1 (max 2)], empty 7/24
N=4000:
  tau=0.03: eps/Delta=1/3 [coverage 16/24, median size 1 (max 7)]; 1/2 [coverage 21/24, median size 1 (max 2)]; intersection [coverage 15/24, median size 1 (max 1)], empty 8/24; joint-max [coverage 18/24, median size 1 (max 2)], empty 3/24
  tau=0.1: eps/Delta=1/3 [coverage 21/24, median size 2 (max 10)]; 1/2 [coverage 21/24, median size 1 (max 2)]; intersection [coverage 18/24, median size 1 (max 2)], empty 6/24; joint-max [coverage 18/24, median size 1 (max 2)], empty 3/24
N=16000:
  tau=0.03: eps/Delta=1/3 [coverage 24/24, median size 1 (max 5)]; 1/2 [coverage 24/24, median size 1 (max 1)]; intersection [coverage 24/24, median size 1 (max 1)], empty 0/24; joint-max [coverage 24/24, median size 1 (max 1)], empty 0/24
  tau=0.1: eps/Delta=1/3 [coverage 24/24, median size 1 (max 8)]; 1/2 [coverage 24/24, median size 1 (max 1)]; intersection [coverage 24/24, median size 1 (max 1)], empty 0/24; joint-max [coverage 24/24, median size 1 (max 1)], empty 0/24

## Milestone 3c unknown mean: python3 unknown_mean.py

true centre 0:
  N= 1000  raw (assumes 0): true wins 21/24, median rel. sigma err 0.109, median kappa err -0.020
  N= 1000         demeaned: true wins 21/24, median rel. sigma err 0.108, median kappa err -0.019
  N= 4000  raw (assumes 0): true wins 24/24, median rel. sigma err 0.035, median kappa err +0.007
  N= 4000         demeaned: true wins 24/24, median rel. sigma err 0.035, median kappa err +0.008
  N=16000  raw (assumes 0): true wins 24/24, median rel. sigma err 0.026, median kappa err -0.010
  N=16000         demeaned: true wins 24/24, median rel. sigma err 0.026, median kappa err -0.010
centre offset (0.7+0.4j):
  N= 1000  raw (assumes 0): estimator refused all 24 replicates (|phi| outside (0,1))
  N= 1000         demeaned: true wins 21/24, median rel. sigma err 0.108, median kappa err -0.019
  N= 4000  raw (assumes 0): estimator refused all 24 replicates (|phi| outside (0,1))
  N= 4000         demeaned: true wins 24/24, median rel. sigma err 0.035, median kappa err +0.008
  N=16000  raw (assumes 0): estimator refused all 24 replicates (|phi| outside (0,1))
  N=16000         demeaned: true wins 24/24, median rel. sigma err 0.026, median kappa err -0.010

## Milestone 3d equal frames: python3 equal_frames.py

Equal total frames T=2N; R=24; true m=1, sigma=30.42
T=1000:
            2N @ 1/2: true wins 17/24 (24 usable), median rel. sigma err 0.149
            2N @ 1/3: true wins  7/24 (24 usable), median rel. sigma err 2.262
   N @ 1/3 + N @ 1/2: true wins 16/24 (24 usable), median rel. sigma err 0.245
T=4000:
            2N @ 1/2: true wins 24/24 (24 usable), median rel. sigma err 0.054
            2N @ 1/3: true wins 13/24 (24 usable), median rel. sigma err 0.079
   N @ 1/3 + N @ 1/2: true wins 22/24 (24 usable), median rel. sigma err 0.048
T=16000:
            2N @ 1/2: true wins 24/24 (24 usable), median rel. sigma err 0.026
            2N @ 1/3: true wins 18/24 (24 usable), median rel. sigma err 0.036
   N @ 1/3 + N @ 1/2: true wins 24/24 (24 usable), median rel. sigma err 0.052

## Milestone 3e tolerance calibration: python3 tolerance_calibration.py

Frozen s8 design (eps/Delta=1/2): delta method gives sd(R)*sqrt(N) = 3.9353 rad, sd(ell2)*sqrt(N) = 2.2089
  N= 1000: tau_95 = 0.2439 rad, ell2 slack_95 = 0.1369 (s12 guessed slack 0.02 at every N)
  N= 4000: tau_95 = 0.1220 rad, ell2 slack_95 = 0.0685 (s12 guessed slack 0.02 at every N)
  N=16000: tau_95 = 0.0610 rad, ell2 slack_95 = 0.0342 (s12 guessed slack 0.02 at every N)
[ok] delta-method sd(R) matches Monte Carlo (MC 0.1264 vs delta 0.1244, 48 fresh seeds at N=1000; MC mean R +0.0130)
[ok] delta-method sd(ell2) matches Monte Carlo (MC 0.0646 vs delta 0.0699; MC mean ell2 0.0186 vs population 0.04 -- the trapezoid simulator biases ell2 low, shared by all of milestone 3)

Calibrated branch sets on s8 seeds (R=24, seed base 424242, branches [-5, 5]):
  N= 1000 tau=0.2439 slack=0.1369: coverage phase-only 24/24, with calibrated ell2 slack 24/24; median set size 2 (max 4), median rel. sigma spread 0.573
  N= 4000 tau=0.1220 slack=0.0685: coverage phase-only 24/24, with calibrated ell2 slack 24/24; median set size 1 (max 1), median rel. sigma spread 0.000
  N=16000 tau=0.0610 slack=0.0342: coverage phase-only 24/24, with calibrated ell2 slack 24/24; median set size 1 (max 1), median rel. sigma spread 0.000

Two exposures (eps/Delta in {1/3, 1/2}, branches [-15, 15], R=24 independent pairs):
  exposure 1 eps/Delta=0.333: sd(R)*sqrt(N) = 4.1262 rad
  exposure 2 eps/Delta=0.500: sd(R)*sqrt(N) = 3.9353 rad
  N= 1000 per exposure: derived chi2 absolute coverage 22/24 (empty 0, median size 2); chi2 relative-to-best coverage 23/24; joint-max tau=0.03 coverage 12/24 (empty 7); per-exposure taus 0.256/0.244 rad
  N= 4000 per exposure: derived chi2 absolute coverage 21/24 (empty 2, median size 1); chi2 relative-to-best coverage 23/24; joint-max tau=0.03 coverage 18/24 (empty 3); per-exposure taus 0.128/0.122 rad
  N=16000 per exposure: derived chi2 absolute coverage 21/24 (empty 3, median size 1); chi2 relative-to-best coverage 24/24; joint-max tau=0.03 coverage 24/24 (empty 0); per-exposure taus 0.064/0.061 rad

FAILED: none -- all checks passed

## Tests after s16: python3 -m pytest -q
32 passed in 0.69s

## Milestone 3f bootstrap calibration: python3 bootstrap_calibration.py (about 2 minutes)

Parametric bootstrap (B=24) on s8 seeds (R=24, seed base 424242); bootstrap seed base 555000; branches [-5, 5]
  N= 1000: bootstrap coverage 24/24 (24 usable, plug-in winner wrong in 3); median set size 2 (max 4), median rel. sigma spread 0.241; median tau_boot/tau_population 0.94 (tau_population 0.2439 rad, s16 coverage 24/24)
[ok] N=1000: bootstrap tau tracks population tau (median ratio 0.94)
  N= 4000: bootstrap coverage 24/24 (24 usable, plug-in winner wrong in 0); median set size 1 (max 1), median rel. sigma spread 0.000; median tau_boot/tau_population 0.93 (tau_population 0.1220 rad, s16 coverage 24/24)
[ok] N=4000: bootstrap tau tracks population tau (median ratio 0.93)
  N=16000: bootstrap coverage 24/24 (24 usable, plug-in winner wrong in 0); median set size 1 (max 1), median rel. sigma spread 0.000; median tau_boot/tau_population 0.96 (tau_population 0.0610 rad, s16 coverage 24/24)
[ok] N=16000: bootstrap tau tracks population tau (median ratio 0.96)

FAILED: none -- all checks passed

## Tests after s17: python3 -m pytest -q
34 passed in 0.87s

## Milestone 3g general finite records: python3 general_finite_record.py

Frozen general example: true m=0, population R(0) = -6.94e-17, nearest rival |R| = 0.5758 in m in [-5, 5]; sigma = 4.7704
Delta method: sd(R)*sqrt(N) = 6.1938
  N= 1000: tau_95 = 0.3839
  N= 4000: tau_95 = 0.1919
  N=16000: tau_95 = 0.0960
[ok] delta-method sd(R) matches Monte Carlo (general case) (MC 0.1984 vs delta 0.1959, 48/48 usable, MC mean R +0.0359)

Calibrated symmetry-residual sets (R=24, seed base 424242, branches [-5, 5]):
  N= 1000 tau=0.3839: coverage 24/24 (24 usable), true branch wins 22/24, median set size 2 (max 2)
  N= 4000 tau=0.1919: coverage 24/24 (24 usable), true branch wins 23/24, median set size 1 (max 2)
  N=16000 tau=0.0960: coverage 24/24 (24 usable), true branch wins 24/24, median set size 1 (max 2)

FAILED: none -- all checks passed

## Tests after s18: python3 -m pytest -q
37 passed in 1.42s

## Milestones 3g-3h general finite records + eligibility slacks (extended script, supersedes the s18-only run above): python3 general_finite_record.py

Frozen general example: true m=0, population R(0) = -6.94e-17, nearest rival |R| = 0.5758 in m in [-5, 5]; sigma = 4.7704
Delta method: sd(R)*sqrt(N) = 6.1938
  N= 1000: tau_95 = 0.3839
  N= 4000: tau_95 = 0.1919
  N=16000: tau_95 = 0.0960
[ok] delta-method sd(R) matches Monte Carlo (general case) (MC 0.1984 vs delta 0.1959, 48/48 usable, MC mean R +0.0359)

Calibrated symmetry-residual sets (R=24, seed base 424242, branches [-5, 5]):
  N= 1000 tau=0.3839: coverage 24/24 (24 usable), true branch wins 22/24, median set size 2 (max 2)
  N= 4000 tau=0.1919: coverage 24/24 (24 usable), true branch wins 23/24, median set size 1 (max 2)
  N=16000 tau=0.0960: coverage 24/24 (24 usable), true branch wins 24/24, median set size 1 (max 2)

Eligibility slacks (delta method at true branch):
  off: population +0.0000, sd*sqrt(N) = 2.4409
  eq_ell: population +0.0000, sd*sqrt(N) = 3.4383
  ell: population +0.0300, sd*sqrt(N) = 1.6128
  lam_S: population +0.7361, sd*sqrt(N) = 3.5840
  lam_D: population +0.4394, sd*sqrt(N) = 4.1263
[ok] delta sd(off) matches Monte Carlo (MC 0.0751 vs delta 0.0772; MC mean -0.0110 vs population +0.0000)
[ok] delta sd(eq_ell) matches Monte Carlo (MC 0.1296 vs delta 0.1087; MC mean +0.0049 vs population +0.0000)
[ok] delta sd(ell) matches Monte Carlo (MC 0.0464 vs delta 0.0510; MC mean +0.0201 vs population +0.0300)
[ok] delta sd(lam_S) matches Monte Carlo (MC 0.0780 vs delta 0.1133; MC mean +0.7104 vs population +0.7361)
[ok] delta sd(lam_D) matches Monte Carlo (MC 0.1183 vs delta 0.1305; MC mean +0.4345 vs population +0.4394)

Hard eligibility vs calibrated slacks (same replicates):
  N= 1000: hard sign-filters delete the true branch in 9/24 replicates; coverage hard 15/24, per-condition 95% slacks 21/24, Bonferroni 99% slacks 22/24 (symmetry-only 24/24; median set size 1)
  N= 4000: hard sign-filters delete the true branch in 5/24 replicates; coverage hard 19/24, per-condition 95% slacks 20/24, Bonferroni 99% slacks 24/24 (symmetry-only 24/24; median set size 1)
  N=16000: hard sign-filters delete the true branch in 0/24 replicates; coverage hard 24/24, per-condition 95% slacks 21/24, Bonferroni 99% slacks 23/24 (symmetry-only 24/24; median set size 1)

FAILED: none -- all checks passed

## Tests after s19: python3 -m pytest -q
38 passed in 1.51s

## Milestone 3i (2026-11-24): python3 general_bootstrap.py

Seeds: films SEED0=424242 scheme of s8/s18 (seed = 424242 + 1000*N + r);
bootstrap films seed base 777000 (+ 1000*N + 100*r + b). B=24, branches
[-5, 5]. Runtime 2m26s on the recording machine.

```
Parametric bootstrap, general case (B=24) on s18 seeds (R=24, seed base 424242); bootstrap seed base 777000; branches [-5, 5]; true m=0
  N= 1000: bootstrap coverage 22/24 (22 usable, 2 unfittable, plug-in winner wrong in 0); median set size 1 (max 3); median tau_boot/tau_population 1.04 (tau_population 0.3839, s18 coverage 24/24)
[ok] N=1000: bootstrap tau tracks population tau (general) (median ratio 1.04)
  N= 4000: bootstrap coverage 23/24 (23 usable, 1 unfittable, plug-in winner wrong in 0); median set size 1 (max 2); median tau_boot/tau_population 0.97 (tau_population 0.1919, s18 coverage 24/24)
[ok] N=4000: bootstrap tau tracks population tau (general) (median ratio 0.97)
  N=16000: bootstrap coverage 24/24 (24 usable, 0 unfittable, plug-in winner wrong in 0); median set size 1 (max 2); median tau_boot/tau_population 0.99 (tau_population 0.0960, s18 coverage 24/24)
[ok] N=16000: bootstrap tau tracks population tau (general) (median ratio 0.99)

FAILED: none -- all checks passed
```

## Tests after s20: python3 -m pytest -q
40 passed in 2.74s (verify_blurred.py and verify_general.py: FAILED: none)

## Milestone 3j (2026-11-24): python3 general_trapezoid_bias.py

Seeds: base 246000 (arm A + sub*1000 + r; arm B + N + r). Runtime 18s.

```
Bias anatomy, frozen general example (seed base 246000)
Arm A: sub sweep at N=2000, R=24
  sub= 10: max mean Gamma entry error +0.00619, mean R +0.0246 +- 0.0280 (+0.18 sd)
  sub= 20: max mean Gamma entry error +0.00624, mean R +0.0495 +- 0.0198 (+0.36 sd)
  sub= 40: max mean Gamma entry error +0.00833, mean R +0.0242 +- 0.0329 (+0.17 sd)
  sub= 80: max mean Gamma entry error +0.00498, mean R +0.0158 +- 0.0278 (+0.11 sd)
Arm B: N sweep at sub=20
  N= 1000 R=96: max mean Gamma entry error +0.00630, mean R +0.0037 +- 0.0219 (+0.02 sd)
  N= 4000 R=48: max mean Gamma entry error +0.00476, mean R -0.0038 +- 0.0149 (-0.04 sd)
  N=16000 R=48: max mean Gamma entry error +0.00186, mean R +0.0016 +- 0.0058 (+0.03 sd)
  N-independent bias of s18's apparent size (+0.036) would sit 5.9 standard errors from the N=16000 mean
[ok] no N-independent bias of s18's apparent size at N=16000 (|mean| + 2se = 0.0133 < 0.036)

FAILED: none -- all checks passed
```

## Tests after s21: python3 -m pytest -q
41 passed in 6.66s (verify_blurred.py and verify_general.py: FAILED: none)

## s22 scalar-Phi search: python3 scalar_phi_search.py
(s22-s24 landed by rebase of rejected contribution cb9860eb commit
a8d78c8 onto the tree after s21, renumbered from the candidate's
s20-s22; script outputs below re-verified on this tree.)
[ok] pi/mixed: truth control J~0, other branches separated (J_true=3.0e-32, min other-branch J=4.763e+01 at beta=+9.425)
[ok] 2pi/mixed: truth control J~0, other branches separated (J_true=3.1e-32, min other-branch J=4.534e-02 at beta=+0.000)
[ok] pi/isotropic: truth control J~0, other branches separated (J_true=3.1e-33, min other-branch J=7.606e+01 at beta=+9.425)
[ok] 2pi/isotropic: truth control J~0, other branches separated (J_true=1.3e-32, min other-branch J=3.754e-02 at beta=+0.000)
[ok] pi/aniso stretched truth: truth control J~0, other branches separated (J_true=2.5e-31, min other-branch J=4.980e+01 at beta=+9.425)
[ok] 3pi/rotated: truth control J~0, other branches separated (J_true=1.6e-32, min other-branch J=2.691e-03 at beta=+3.142)
[ok] 2pi/short shutter: truth control J~0, other branches separated (J_true=5.2e-32, min other-branch J=1.084e-03 at beta=+0.000)
[ok] pi/full shutter: truth control J~0, other branches separated (J_true=8.4e-32, min other-branch J=1.027e+02 at beta=+9.425)
[ok] no compatible other-branch rival in sweep (all minima > 1e-4) (smallest other-branch minimum 1.084e-03)
FAILED: none -- all checks passed


## s23 alpha=0 is empty: python3 alpha_zero.py
[ok] frozen general: formula (1) matches definition (|diff| 3.5e-18)
[ok] frozen general: factorization (3) Shat bracket = Sigma bracket (|diff| 1.1e-16)
[ok] frozen general: alpha*d0/i real and nonzero, adjugate bracket > 0 (t=+1.8252, bracket=0.8083, |alpha|=0.3657)
[ok] isotropic: alpha*d0/i real and nonzero, adjugate bracket > 0 (t=+2.0000, bracket=1.0000, |alpha|=0.3851)
[ok] random sweep (200 truths): t != 0 and bracket > 0 throughout (min |t| 0.2015, min bracket 0.0900)
[ok] random sweep: formula (1) matches definition (max |diff| 1.5e-14)
FAILED: none -- all checks passed


## s24 Diophantine windows: python3 diophantine_windows.py
[ok] golden (sqrt5-1)/2, badly approximable: min |R(m)|/m bounded below (min 0.1553 at m=92549)
[ok] sqrt2-1, badly approximable: min |R(m)|/m bounded below (min 0.2024 at m=20674)
[ok] engineered [0;9,11,1000,7,3]: min |R(m)|/m collapses (min 0.0049 at m=169777)
FAILED: none -- all checks passed

## Tests after s22-s24: python3 -m pytest -q
48 passed

## Milestone 3k s25 (2026-11-24): python3 window_constant.py

Runtime ~5s. Full output:

```
[ok] golden [0;1,1,...]: R = m^2 h + m h1 + h0 exact (rel err vs eigen 6.4e-13 for m<=1000, h-level err 8.1e-09 at m~1e5, abs err vs direct 4.3e-12; alpha=0.1094+1.7928j, a=r^rho=0.5895)
[ok] golden [0;1,1,...]: h has exactly two zeros, both simple (psi* = ['0.01574', '3.37656'], h' = ['366.3831', '-1.6746'])
[ok] sqrt2-1 [0;2,2,...]: R = m^2 h + m h1 + h0 exact (rel err vs eigen 1.7e-13 for m<=1000, h-level err 8.1e-09 at m~1e5, abs err vs direct 1.4e-12; alpha=0.0495+1.8113j, a=r^rho=0.7018)
[ok] sqrt2-1 [0;2,2,...]: h has exactly two zeros, both simple (psi* = ['0.00479', '3.29720'], h' = ['552.3639', '-0.5274'])
[ok] engineered [0;9,11,1000,7,3]: R = m^2 h + m h1 + h0 exact (rel err vs eigen 3.4e-13 for m<=1000, h-level err 4.4e-10 at m~1e5, abs err vs direct 2.4e-15; alpha=0.0035+1.8242j, a=r^rho=0.9102)
[ok] engineered [0;9,11,1000,7,3]: h has exactly two zeros, both simple (psi* = ['0.00009', '3.18254'], h' = ['2094.9785', '-0.0102'])
[ok] golden [0;1,1,...]: s24 control min|R(m)|/m over m<=200000 (got 0.1553 at m=92549, s24 0.1553)
[ok] golden [0;1,1,...]: derived bound B <= brute min on [M0,M], B > 0 (M0=1000, B=0.12315, brute=0.15526 at m=92549, ratio 1.26; brute below M0: 0.31229 at m=12)
    psi*=0.0157 gamma=0.89274 xi*=-0.0112 2pi|h'|=2302.0527 (per eps^2: 7440.56) D_j=0.04209 at m=70339 B_near=95.02932 pred~96.89231
    psi*=3.3766 gamma=0.42763 xi*=-0.1656 2pi|h'|=10.5219 (per eps^2: 34.01) D_j=0.01476 at m=92549 B_near=0.12315 pred~0.15525
    convergents q_k<=200000: 27; argmin m=92549 in block [q_k=75025, q_next=121393) (next partial quotient 1)
[ok] sqrt2-1 [0;2,2,...]: s24 control min|R(m)|/m over m<=200000 (got 0.2024 at m=20674, s24 0.2024)
[ok] sqrt2-1 [0;2,2,...]: derived bound B <= brute min on [M0,M], B > 0 (M0=1505, B=0.18941, brute=0.20239 at m=20674, ratio 1.07; brute below M0: 0.65422 at m=1073)
    psi*=0.0048 gamma=0.92719 xi*=-0.0076 2pi|h'|=3470.6050 (per eps^2: 24973.05) D_j=0.12908 at m=81593 B_near=442.78618 pred~447.98874
    psi*=3.2972 gamma=0.45120 xi*=-0.2457 2pi|h'|=3.3134 (per eps^2: 23.84) D_j=0.06108 at m=20674 B_near=0.18941 pred~0.20239
    convergents q_k<=200000: 15; argmin m=20674 in block [q_k=13860, q_next=33461) (next partial quotient 2)
[ok] engineered [0;9,11,1000,7,3]: s24 control min|R(m)|/m over m<=200000 (got 0.0049 at m=169777, s24 0.0049)
[ok] engineered [0;9,11,1000,7,3]: derived bound B <= brute min on [M0,M], B > 0 (M0=80356, B=0.00471, brute=0.00494 at m=169777, ratio 1.05; brute below M0: 0.00577 at m=69668)
    psi*=0.0001 gamma=0.98048 xi*=-0.0020 2pi|h'|=13163.1380 (per eps^2: 1343037.86) D_j=0.33525 at m=104827 B_near=4084.93164 pred~4412.94396
    psi*=3.1825 gamma=0.48698 xi*=-0.9214 2pi|h'|=0.0642 (per eps^2: 6.55) D_j=0.07691 at m=169777 B_near=0.00471 pred~0.00494
    convergents q_k<=200000: 4; argmin m=169777 in block [q_k=100009, q_next=700163) (next partial quotient 7)
  golden [0;1,1,...]: D_j(M) search: M=10000: 0.03096, M=200000: 0.01476, M=1000000: 0.01476  (saturation would mean xi* off the limit set Xi_j)
  sqrt2-1 [0;2,2,...]: D_j(M) search: M=10000: 0.19742, M=200000: 0.06108, M=1000000: 0.06056  (saturation would mean xi* off the limit set Xi_j)
  engineered [0;9,11,1000,7,3]: D_j(M) search: M=10000: 0.18067, M=200000: 0.07691, M=1000000: 0.07691  (saturation would mean xi* off the limit set Xi_j)
[ok] golden: homogeneous CF bound m||m rho|| >= 1/(A+2) (min over m<=200000 is 0.3820, bound 0.3333, A=1)
[ok] sqrt2-1: homogeneous CF bound m||m rho|| >= 1/(A+2) (min over m<=200000 is 0.3431, bound 0.2500, A=2)
[ok] quotient swap: engineered 1000 -> 1s lowers the minimum ([0;9,11,1,...] 0.00139 at 190394 < engineered 0.00494 at 169777)
[ok] quotient swap: inserting 1000 into golden raises the minimum ([0;1x6,1000,1...] 0.69339 at 33360 > golden 0.15526 at 92549)
  reading: no closed c(partial quotients) orders these minima;
  the arithmetic factor is dist(xi*, Xi) for the truth's own
  gamma (its Ostrowski position), times eps^2 geometry in h'.
[ok] parameter level: rotating arg alpha zeroes R(m0) exactly (m0=1000, t*=1.0391, R=3.58e-09; so no c(rho) uniform over (alpha, theta, r) exists)
[ok] in-model family: a genuine truth with |R(m)|/m ~ 0 at golden rho (A=[[-0.6,-w],[w,-1.2]], w*=2.90000151, m=96, |R|/m=1.10e-11, r=0.4449<1, theta=2.5960)
FAILED: none -- all checks passed
```

## Tests after s25: python3 -m pytest -q
tests re-verified on the merged s22-s24+s25 tree in the s26 slice below

## Milestone 3l s26: python3 ostrowski_liminf.py
(Ostrowski digits of gamma at golden rho and sqrt(2)-1; s25 merged onto s22-s24 as base in the same landing.)
[ok] golden: delta_k = (-1)^k rho^(k+1) exact in Q(sqrt5), rho^2 + 1 rho = 1 
[ok] golden: integer Ostrowski digits legal and reconstruct m<q_10 
[ok] sqrt2-1: delta_k = (-1)^k rho^(k+1) exact in Q(sqrt2), rho^2 + 2 rho = 1 
[ok] sqrt2-1: integer Ostrowski digits legal and reconstruct m<q_10 
[ok] golden: mpmath gamma/xi*/2pi|h'| agree with s25 floats (active 2pi|h'| = 10.5219)
[ok] golden/active: gamma digits (pred vs brute, series, stable) (e=1, c[0:24]=010101001001001010101000)
[ok] golden/active: xi_m via S-decomposition = direct (worst 3.6e-86)
[ok] golden/active: |S_m| < 1/2 for J(m) >= 4 (no wrap) (2*tail bound = 0.2918)
[ok] golden/active: xi_(A_K) = -A_K R_K 
    golden/active: prefix record lows K=2:0.355995, K=4:0.343624, K=6:0.030961, K=21:0.026981, K=25:0.014756, K=363:0.007503 | DFS best 0.056402
[ok] golden/inactive: gamma digits (pred vs brute, series, stable) (e=1, c[0:24]=000100100010010010100101)
[ok] golden/inactive: xi_m via S-decomposition = direct (worst 2.2e-85)
[ok] golden/inactive: |S_m| < 1/2 for J(m) >= 4 (no wrap) (2*tail bound = 0.2918)
[ok] golden/inactive: xi_(A_K) = -A_K R_K 
    golden/inactive: prefix record lows K=4:0.104706, K=7:0.055871, K=24:0.042089, K=72:0.038001, K=163:0.007909, K=227:0.002990 | DFS: none within filter
[ok] sqrt2-1: mpmath gamma/xi*/2pi|h'| agree with s25 floats (active 2pi|h'| = 3.3134)
[ok] sqrt2-1/active: gamma digits (pred vs brute, series, stable) (e=0, c[0:24]=101101001011100201000102)
[ok] sqrt2-1/active: xi_m via S-decomposition = direct (worst 4.1e-160)
[ok] sqrt2-1/active: |S_m| < 1/2 for J(m) >= 3 (no wrap) (2*tail bound = 0.1421)
[ok] sqrt2-1/active: xi_(A_K) = -A_K R_K 
    sqrt2-1/active: prefix record lows K=2:0.208731, K=9:0.197424, K=12:0.061082, K=30:0.014807, K=97:0.009272, K=204:0.005877, K=209:0.005323, K=268:0.001558 | DFS best 0.029675
[ok] sqrt2-1/inactive: gamma digits (pred vs brute, series, stable) (e=1, c[0:24]=011020210000010200001020)
[ok] sqrt2-1/inactive: xi_m via S-decomposition = direct (worst 4.2e-160)
[ok] sqrt2-1/inactive: |S_m| < 1/2 for J(m) >= 3 (no wrap) (2*tail bound = 0.1421)
[ok] sqrt2-1/inactive: xi_(A_K) = -A_K R_K 
    sqrt2-1/inactive: prefix record lows K=2:0.189940, K=3:0.186296, K=8:0.012349, K=16:0.005583, K=47:0.001503 | DFS: none within filter
[ok] golden active: dist upper bound (prefix K=25 is s25's 0.01476) (dist <= 0.007503, s25 scan 0.01476)
[ok] sqrt2-1 active: dist upper bound (s25 scan was 0.06056) (dist <= 0.001558, s25 scan 0.06056)
    golden: liminf |R(m)|/m <= 10.5219 * 0.007503 = 0.078941 (active zero); inactive term <= 6.883
    sqrt2-1: liminf |R(m)|/m <= 3.3134 * 0.001558 = 0.005162 (active zero); inactive term <= 5.215
[ok] golden: liminf |R(m)|/m <= 0.0789 (s25 scan-level 0.1553 refuted) 
[ok] sqrt2-1: liminf |R(m)|/m <= 0.00517 (s25 scan-level 0.2024 refuted) 
[ok] golden: all-windows Xi brackets xi* within 0.005 (bracket width 0.00063; window-only positivity proofs are impossible)
[ok] sqrt2-1: all-windows Xi brackets xi* within 0.005 (bracket width 0.00049; window-only positivity proofs are impossible)

FAILED: none -- all checks passed

## Tests after s26: python3 -m pytest -q
61 passed in 2.82s (55 after s25 merge + 6 new in test_ostrowski_liminf.py)

## Milestone 3l s27: python3 scalar_phi_proof.py
[ok] truth setup: Phi = e^alpha I (scalar), alpha recovered (err 4.6e-71)
[ok] truth control: residuals vanish at the true drift (max 4.5e-72)
[ok] signed residuals are A + B cos(2phi) + C sin(2phi) exactly (worst fit err 6.3e-68)
[ok] beta=0 rival: single drift with J = 1.084e-3 > 0 (J = 0.001084, s22 search value)
[ok] same branch 2pi: det M = (w-2) S(w), S quadratic, S(-2)=0 (fit rel err 1.7e-69, max|resid| at t=0 0.0701)
[ok] same branch 2pi: only admissible root w*=2.1621447 gives t=+-0.2 and recovers the true drift (drift err 6.3e-68, phi* 0.3 vs true 0.3 mod pi/2 twin)
[ok] rival 4pi: det M = (w-2) S(w), S quadratic, S(-2)=0 (fit rel err 5.5e-69, max|resid| at t=0 0.156)
[ok] rival 4pi: w* = 1.0291307 < 2, so det M(t) != 0 for all real t != 0: no rival on this branch (discriminant 5.73e-5; other root w=-2)
[ok] rival 6pi: det M = (w-2) S(w), S quadratic, S(-2)=0 (fit rel err 1.1e-68, max|resid| at t=0 0.291)
[ok] rival 6pi: w* = 0.62511728 < 2, so det M(t) != 0 for all real t != 0: no rival on this branch (discriminant 0.00277; other root w=-2)

FAILED: none -- all checks passed

## Tests after s27: python3 -m pytest -q
66 passed (61 after s26 + 5 new in test_scalar_phi_proof.py)
