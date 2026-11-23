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
