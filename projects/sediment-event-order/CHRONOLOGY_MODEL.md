# Monotone Age-Depth Chronologies and Shared Calibration Ensembles

This module implements the monotone sediment age-depth forward simulator, shared-vs-independent calibration-curve separation, and joint Bayesian chronology sampler for `sediment-event-order-calibration` (`great-choice-20261124-pippin`). It uses only the Python standard library and touches only `chronology_model.py`, `test_chronology_model.py`, and `CHRONOLOGY_MODEL.md`.

## Model Specification

1. **Monotone Gamma-Increment Age-Depth Process** (Haslett & Parnell, 2008, *JRSS-C*):
   For an archive with strictly increasing depth nodes $z_0 < z_1 < \dots < z_K$:
   - Surface age $a_0 \sim \mathcal{N}(\mu_0, \sigma_0^2)$.
   - Strictly positive depth-interval age increments:
     $$\Delta a_i = a_i - a_{i-1} \sim \text{Gamma}\!\left(\alpha_i = \kappa\,\Delta z_i,\; \text{rate } \beta = \frac{\kappa}{\bar{s}}\right), \quad \Delta z_i = z_i - z_{i-1} > 0,$$
     with piecewise-linear interpolation between nodes. Because $\Delta a_i > 0$, age reversals cannot occur anywhere on $[z_0, z_K]$, and sharing rate $\beta$ across intervals preserves exact subdivision invariance ($\Delta a' + \Delta a'' \stackrel{d}{=} \Delta a$).

2. **Separated Shared Calibration Component & Independent Dating Noise**:
   Observed dates $y_{k,j}$ in archives $k \in \{A, B\}$ share a piecewise-linear Gaussian-process calibration offset $c(a; \mathbf{w}) = \mathbf{b}(a)^\top \mathbf{w}$ with $\mathbf{w} \sim \mathcal{N}(\mathbf{0}, \Sigma_{\text{cal}})$, plus independent dating errors $\epsilon_{k,j} \sim \mathcal{N}(0, \sigma_{k,j}^2)$:
   $$y_{k,j} = a_k(z_{k,j}) + c(a_k(z_{k,j}); \mathbf{w}) + \epsilon_{k,j}.$$

3. **Public Observation vs. Oracle Boundary**:
   - `PublicChronologyObservation.to_public_dict()` exports only `archive_a`, `archive_b` (depths, observed dates, measurement SDs, declared priors), and `calibration_prior`. It omits true node ages, true calibration realizations $\mathbf{w}$, true query ages, and true $\Delta_{AB}$.
   - `OracleChronologyTruth` is explicitly labelled and used only in evaluation diagnostics.

4. **Joint Metropolis-within-Gibbs Inference**:
   - Exact multivariate Gaussian Gibbs updates for $\mathbf{w} \mid a_A, a_B, y$.
   - Log-increment MH proposals ($u_i = \log \Delta a_i$ with exact Jacobian), interior knot-age swaps, and joint calibration-ridge moves $(a_A + \delta, a_B + \delta, \mathbf{w} - \delta \mathbf{1})$ so chains mix across the strong $(a, \mathbf{w})$ ridge.
   - Multi-chain split-$\hat{R}$ reported across `a_A`, `a_B`, and `delta = a_A - a_B`.

## Verification & Recorded Run

Commands executed (standard library only):

```sh
python3 -m unittest discover -s projects/sediment-event-order -p "test_chronology_model.py" -v
python3 projects/sediment-event-order/chronology_model.py --trials 80 --seed 20261124
```

Results observed:
- **Unit tests**: 8/8 tests passed in 32.169s (`test_chronology_model.py`), covering:
  - Strict monotonicity across 100 random paths (`TestMonotoneGammaProcess.test_strict_monotonicity_across_many_draws`).
  - Exact subdivision invariance of Gamma-process mean ($800$) and variance ($64000$) between coarse and refined depth grids (`test_subdivision_invariance_moments`).
  - Public observation export excluding all oracle truth fields (`test_public_export_excludes_oracle_truth`).
  - Closed-form trivariate/linearized Gaussian limit posterior (`analytic_gaussian_limit_posterior`) matching MCMC (`max_rhat < 1.05`) in `mean_a`, `mean_b`, `sd_a`, `sd_b`, `cov_ab`, and `sd_delta`, plus variance inflation upon shuffling (`test_exact_gaussian_limit_closed_form_matches_mcmc`).
  - Independent joint Importance Sampling (`importance_sample_small_case`) matching MCMC on a non-Gaussian (`kappa = 0.8`) curved-calibration case (`test_nonlinear_gamma_small_case_matches_importance_sampling`).
  - Prior-predictive SBC/PIT and retained failure assertions (`test_prior_predictive_sbc_and_failure_comparisons`, `test_unconstrained_nonmonotone_exhibits_age_reversals`).

- **Recorded CLI output** (`--trials 80 --seed 20261124`):
  - Single case: `max_rhat = 1.0175`, `joint_cov_ab = 1836.17`, `joint_sd_delta = 33.7`, `shuffled_sd_delta = 69.7`, `reversal_count = 0`, `oracle_delta_ab = -78.13`.
  - 80-trial SBC benchmark (`default_two_archive`):
    - **Joint paired monotone (`joint`)**: `cov90_a = 0.825` (`KS = 0.0964`), `cov90_b = 0.8625`, `cov90_delta = 0.875` (`KS = 0.0991`), mean 90% width `123.86`, ordering Brier `0.0251`.
    - **Shuffled-marginal ensemble (`shuffled`)**: `cov90_delta = 0.9875` (`KS = 0.1686`), mean 90% width `251.6` (2.03x wider), ordering Brier `0.0304`.
    - **Independent-calibration misattribution (`independent_cal`)**: marginal `cov90_a = 0.85` looks calibrated, yet `cov90_delta = 0.9875`, mean 90% width `276.02` (2.23x wider), ordering Brier `0.0458`.
    - **Ignored calibration (`ignored_cal`)**: marginal `cov90_a = 0.475` severely under-covers nominal 90%.

## Retained Failure Modes & Scope Limits

1. **Marginal shuffling** preserves single-core uncertainty while destroying positive cross-archive covariance, doubling $\Delta_{AB}$ interval width and over-covering $\Delta_{AB}$ (98.75% vs nominal 90%).
2. **Independent-calibration misattribution** achieves nominal single-core coverage (85%) while inflating $\Delta_{AB}$ width by 2.23x and degrading ordering Brier score from `0.0251` to `0.0458`.
3. **Unconstrained per-depth estimation** (`fit_unconstrained_nonmonotone`) produces frequent age inversions when date spacing is small relative to measurement noise (verified >= 15/25 seeds), whereas monotone Gamma-increment inference has 0 reversals.
4. **Ignoring shared calibration** collapses marginal 90% coverage from `0.825` to `0.475`.
5. **Scope**: Synthetic chronology forward model and inference module only; not yet coupled to the sediment bioturbation/material-ancestry proxy likelihood or real IntCal lookup tables, and does not claim Milestone 1/2 completion.
