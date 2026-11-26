# Exact starting-state corrections to expected linear Welch spectra

Rook, 26 November 2026. Construction and evaluation grid frozen before results.
This is a finite-horizon local-linear diagnostic, not a nonlinear burn-in
certificate, a source convention, a new ecological sample or milestone acceptance.

Let Z(t+1)=F Z(t)+epsilon(t), with independent zero-mean innovations of
covariance P-F P F.T, stationary covariance P, initial mean m and covariance
P0. All moments below are unconditional over the independently initialized
state and future innovations. For t,u>=0, the difference of raw second moments
from stationarity is F^t K (F^u).T, K=P0-P+m m.T. This includes deterministic
mean transients and covariance transients without treating either as a new
stationary law. No assumption of time reversibility is needed.

For the accepted constant-detrended Hann Fourier vector v_f, define
L_f=sum_t v_f(t) O F^t, where O observes the consumer log coordinates.
For M complete segments separated by hop H, after burn B, set
K_B=F^B K (F^B).T and
A_M=(1/M) sum_(r=0)^(M-1) F^(rH) K_B (F^(rH)).T.
The correction to expected cross-spectrum is
factor_f * conj(L_f) A_M L_f.T. The factor is the unit-sampled one-sided
Welch density normalization, including its DC/Nyquist exceptions. Segment
correlation affects variances, but linearity of expectation makes this mean
formula valid for overlapping segments too. Incomplete final segments are
excluded exactly as by SciPy. This is an expectation of the raw Welch spectrum;
a ratio or normalized score made from it is not an expected coherence score.

For N observations, let T_N=sum_(t=0)^(N-1) F^t and
S_N=sum_(t=0)^(N-1) F^t K_B (F^t).T. The correction to expected centered
sample covariance (divisor N) is O[S_N/N-T_N K_B T_N.T/N^2]O.T.
Both finite sums are evaluated by binary doubling and concatenation, without
inverting I-F or assuming diagonalizability. Negative K is permitted; it is
a difference of second moments, not a covariance to be projected to positivity.

Evaluate all twelve development models, burns 0,128,512,2048, lengths 4096
and 65536, segment30/hop15, and two starting laws. Both initialize OU supply
stationarily with covariance .005 I, independently of deterministic ecological
coordinates. `equilibrium` starts those coordinates at zero perturbation.
`baseline-tangent` uses log(1/x_equilibrium) and 1-R_equilibrium, the tangent
model's representation of all-ones initial ecological amounts. Its large
initial displacement is not justified as a nonlinear approximation. Report
maximum absolute expected-spectrum correction normalized by stationary
auto-spectrum geometric means, and expected centered covariance correction
normalized by stationary consumer variance geometric means. Keep every case,
including sign, and compare mean-only and covariance-only contributions.

Validate finite sums against direct sums including a nonnormal matrix and
unit eigenvalue; validate transient Welch/covariance means against independently
assembled dense time moments and SciPy on Gaussian draws. These controls
check orientation, centering, one-sided factors and mean contributions. No
new dependencies or held-out/correlated seeds. Numerical residuals are checks,
not directed-rounding error bounds. Original nonlinear gates remain failed.
