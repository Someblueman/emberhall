# A reference for the estimator as well as the dynamics

`linear_reference.py` checks continuous local-linear covariance two ways.
`linear_welch.py` adds a distinct limiting prediction: an infinitely long
stationary **local-linear** record, analyzed using our fixed 30-sample Hann
segments, constant detrending and one-sided Welch normalization. It does not
assume that the nonlinear finite record has reached this limit.

For the augmented consumer/resource/OU state Z, write dZ = A Z dt + D dW.
The stationary covariance P solves A P + P A.T + D D.T = 0. At unit sampling,
F = exp(A); lag covariances are F^l P. Restrict to log-consumer coordinates
and normalize by their stationary deviations to get K(l).
For samples t,u within one segment, their cross-covariance is K(t-u) when
t >= u, and K(u-t).T otherwise. Call this block matrix C.

Let w be the periodic Hann window and v_f(t) = w(t) exp(-2 pi i f t).
Constant detrending before windowing replaces v_f by v_f - mean(v_f).
The expected cross-periodogram is the quadratic form conj(v_f).T C v_f,
divided by sum(w²), with interior positive frequencies doubled. This directly
retains the estimator's window, detrending and endpoint conventions. There is
no frequency-grid refinement error in this finite-segment calculation.

With infinitely many stationary segments, the Welch spectral estimate tends
to this expectation. We apply the same integrated magnitude and coherence
functionals, then separately score overlap ranking, pair labels and the
single-linkage closure. A ratio of expected spectra is not the expectation
of a finite-record coherence estimator; the finite-sample ratio bias remains.
The model is linearized at a deterministic equilibrium and receives continuous
OU forcing. Nonlinear effects, finite record length and interpolated input
can all separate our simulation from these predictions.

Independent checks cover exact white-noise Hann/detrend normalization, a
40,000-record Monte Carlo comparison against SciPy's periodograms, and bounded
model scores. The white-noise DC power is one third, the first interior bin
five thirds, ordinary interior bins two, and Nyquist one, in the unit-variance,
unit-sampling convention. This catches incorrect DC removal and doubling.

For reconstructed communities 4–15, the mean limiting overlap Spearman scores
are 0.91142 (correlation), 0.83713 (absolute correlation), 0.93524 (cross-power)
and 0.95966 (coherence). All limiting single-linkage guild AUCs are one.
Consequently the reconstructed parameters do not establish that equal-time
correlation fails, or that coherence alone succeeds. These are a model/estimator
reference, not the published values. Keep this result even if it weakens the
project's motivating expectation. The new finite nonlinear records must be
reported on their own terms.

Replay:

```
python3 projects/when-nutrients-arrive-together/linear_welch.py \
  --output /tmp/nutrient-linear-welch.json
```

A coloured delayed-signal control now checks the complex cross-spectrum against
an independently generated filter process. [LINEAR_CALIBRATION.md](LINEAR_CALIBRATION.md)
compares the prediction against 48 exactly sampled stationary linear paths and
quantifies finite-record error without OU interpolation or ODE stepping.
