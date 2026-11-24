"""Monotone age-depth chronology generator and joint calibration-curve inference.

Implements:
1. Subdivision-invariant monotone Gamma-increment age-depth paths
   (Haslett & Parnell, 2008, JRSS-C) with piecewise-linear interpolation.
2. Shared calibration-curve Gaussian process / offset component across two
   sediment archives, separated from archive-specific dating measurement noise.
3. Strict public observation export (`PublicChronologyObservation`) omitting all
   latent truth, paired with an explicitly labelled `OracleChronologyTruth`.
4. Exact closed-form Gaussian-limit solver and prior Importance Sampling verifier
   for small cases.
5. Exact Metropolis-within-Gibbs joint chronology sampler (with joint ridge
   proposals and split-Rhat diagnostics) preserving cross-archive pairing, plus
   retained failure baselines: shuffled-marginal ensembles, unconstrained
   non-monotone fits, and calibration-ignored fits.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import random
import statistics
from typing import Any


# ---------------------------------------------------------------------------
# Small-matrix linear algebra (standard library only)
# ---------------------------------------------------------------------------


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    chol = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            total = matrix[i][j]
            for k in range(j):
                total -= chol[i][k] * chol[j][k]
            if i == j:
                if total <= 0.0:
                    raise ValueError(f"Matrix is not positive definite at index {i}: {total}")
                chol[i][j] = math.sqrt(total)
            else:
                chol[i][j] = total / chol[j][j]
    return chol


def _solve_lower(chol: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(chol)
    out = [0.0] * n
    for i in range(n):
        total = rhs[i]
        for k in range(i):
            total -= chol[i][k] * out[k]
        out[i] = total / chol[i][i]
    return out


def _solve_upper_t(chol: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(chol)
    out = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = rhs[i]
        for k in range(i + 1, n):
            total -= chol[k][i] * out[k]
        out[i] = total / chol[i][i]
    return out


def _solve_spd_chol(chol: list[list[float]], rhs: list[float]) -> list[float]:
    return _solve_upper_t(chol, _solve_lower(chol, rhs))


def _invert_spd(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    chol = _cholesky(matrix)
    cols: list[list[float]] = []
    for j in range(n):
        unit = [0.0] * n
        unit[j] = 1.0
        cols.append(_solve_spd_chol(chol, unit))
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def _sample_mvn_chol(chol: list[list[float]], rng: random.Random) -> list[float]:
    n = len(chol)
    z = [rng.gauss(0.0, 1.0) for _ in range(n)]
    return [sum(chol[i][k] * z[k] for k in range(i + 1)) for i in range(n)]


def _sample_mvn_precision(
    precision: list[list[float]],
    canonical: list[float],
    rng: random.Random,
) -> list[float]:
    chol = _cholesky(precision)
    mean = _solve_spd_chol(chol, canonical)
    z = [rng.gauss(0.0, 1.0) for _ in range(len(precision))]
    noise = _solve_upper_t(chol, z)
    return [mean[i] + noise[i] for i in range(len(precision))]


def _dot(a: list[float] | tuple[float, ...], b: list[float] | tuple[float, ...]) -> float:
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Specifications & Public / Oracle Data Contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArchivePriorSpec:
    name: str
    node_depths: tuple[float, ...]
    dated_depths: tuple[float, ...]
    query_depth: float
    mean_surface_age: float
    sd_surface_age: float
    mean_sed_rate: float
    kappa: float
    measurement_sds: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if len(self.node_depths) < 2:
            raise ValueError("node_depths must contain at least 2 depths")
        for i in range(1, len(self.node_depths)):
            if self.node_depths[i] <= self.node_depths[i - 1]:
                raise ValueError("node_depths must be strictly increasing")
        if self.mean_sed_rate <= 0.0 or self.kappa <= 0.0:
            raise ValueError("mean_sed_rate and kappa must be positive")
        if self.sd_surface_age < 0.0:
            raise ValueError("sd_surface_age must be non-negative")
        z_min, z_max = self.node_depths[0], self.node_depths[-1]
        if not (z_min <= self.query_depth <= z_max):
            raise ValueError("query_depth must lie within node_depths range")
        for z in self.dated_depths:
            if not (z_min <= z <= z_max):
                raise ValueError(f"dated depth {z} outside node_depths range")
        if self.measurement_sds and len(self.measurement_sds) != len(self.dated_depths):
            raise ValueError("measurement_sds length must match dated_depths")
        for sd in self.measurement_sds:
            if sd <= 0.0:
                raise ValueError("measurement_sds must be strictly positive")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "node_depths": list(self.node_depths),
            "dated_depths": list(self.dated_depths),
            "query_depth": self.query_depth,
            "mean_surface_age": self.mean_surface_age,
            "sd_surface_age": self.sd_surface_age,
            "mean_sed_rate": self.mean_sed_rate,
            "kappa": self.kappa,
            "measurement_sds": list(self.measurement_sds),
        }


@dataclass(frozen=True)
class CalibrationPriorSpec:
    knot_ages: tuple[float, ...]
    sd: float
    corr_length: float
    nugget: float = 1e-6

    def __post_init__(self) -> None:
        if not self.knot_ages:
            raise ValueError("knot_ages must be non-empty")
        for i in range(1, len(self.knot_ages)):
            if self.knot_ages[i] <= self.knot_ages[i - 1]:
                raise ValueError("knot_ages must be strictly increasing")
        if self.sd < 0.0 or self.corr_length <= 0.0 or self.nugget <= 0.0:
            raise ValueError("invalid calibration prior hyperparameters")

    def covariance_matrix(self) -> list[list[float]]:
        m = len(self.knot_ages)
        var = self.sd * self.sd
        cov = [[0.0] * m for _ in range(m)]
        for i in range(m):
            for j in range(m):
                dist = abs(self.knot_ages[i] - self.knot_ages[j])
                val = var * math.exp(-dist / self.corr_length)
                if i == j:
                    val += self.nugget
                cov[i][j] = val
        return cov

    def precision_matrix(self) -> list[list[float]]:
        return _invert_spd(self.covariance_matrix())

    def basis_weights(self, age: float) -> list[float]:
        m = len(self.knot_ages)
        weights = [0.0] * m
        if m == 1 or age <= self.knot_ages[0]:
            weights[0] = 1.0
            return weights
        if age >= self.knot_ages[-1]:
            weights[-1] = 1.0
            return weights
        for i in range(m - 1):
            t0, t1 = self.knot_ages[i], self.knot_ages[i + 1]
            if t0 <= age <= t1:
                frac = (age - t0) / (t1 - t0)
                weights[i] = 1.0 - frac
                weights[i + 1] = frac
                return weights
        weights[-1] = 1.0
        return weights

    def evaluate(self, age: float, w: list[float] | tuple[float, ...]) -> float:
        return _dot(self.basis_weights(age), w)

    def to_dict(self) -> dict[str, Any]:
        return {
            "knot_ages": list(self.knot_ages),
            "sd": self.sd,
            "corr_length": self.corr_length,
            "nugget": self.nugget,
        }


@dataclass(frozen=True)
class PairedChronologySpec:
    archive_a: ArchivePriorSpec
    archive_b: ArchivePriorSpec
    calibration: CalibrationPriorSpec

    @classmethod
    def default_two_archive(cls) -> PairedChronologySpec:
        return cls(
            archive_a=ArchivePriorSpec(
                name="archive_a",
                node_depths=(0.0, 8.0, 18.0, 30.0),
                dated_depths=(0.0, 8.0, 18.0, 30.0),
                query_depth=13.0,
                mean_surface_age=500.0,
                sd_surface_age=50.0,
                mean_sed_rate=45.0,
                kappa=0.8,
                measurement_sds=(35.0, 35.0, 35.0, 35.0),
            ),
            archive_b=ArchivePriorSpec(
                name="archive_b",
                node_depths=(0.0, 6.0, 14.0, 24.0),
                dated_depths=(0.0, 6.0, 14.0, 24.0),
                query_depth=10.0,
                mean_surface_age=520.0,
                sd_surface_age=50.0,
                mean_sed_rate=55.0,
                kappa=0.8,
                measurement_sds=(35.0, 35.0, 35.0, 35.0),
            ),
            calibration=CalibrationPriorSpec(
                knot_ages=(200.0, 800.0, 1400.0, 2000.0, 2600.0),
                sd=85.0,
                corr_length=900.0,
                nugget=1e-6,
            ),
        )


@dataclass(frozen=True)
class ArchiveObservation:
    prior: ArchivePriorSpec
    observed_dates: tuple[float, ...]
    measurement_sds: tuple[float, ...]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "prior": self.prior.to_dict(),
            "observed_dates": list(self.observed_dates),
            "measurement_sds": list(self.measurement_sds),
        }


@dataclass(frozen=True)
class PublicChronologyObservation:
    """Observation payload exposed to inference; contains zero latent truth."""

    archive_a: ArchiveObservation
    archive_b: ArchiveObservation
    calibration_prior: CalibrationPriorSpec

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "archive_a": self.archive_a.to_public_dict(),
            "archive_b": self.archive_b.to_public_dict(),
            "calibration_prior": self.calibration_prior.to_dict(),
        }


@dataclass(frozen=True)
class OracleChronologyTruth:
    """Explicitly labelled oracle ground truth; never passed to inference."""

    node_ages_a: tuple[float, ...]
    node_ages_b: tuple[float, ...]
    calibration_w: tuple[float, ...]
    event_age_a: float
    event_age_b: float

    @property
    def delta_ab(self) -> float:
        return self.event_age_a - self.event_age_b


# ---------------------------------------------------------------------------
# Age-Depth Path & Forward Simulation
# ---------------------------------------------------------------------------


def _interp_weights(node_depths: tuple[float, ...], depth: float) -> tuple[int, int, float]:
    if depth <= node_depths[0]:
        return (0, 0, 0.0)
    if depth >= node_depths[-1]:
        last = len(node_depths) - 1
        return (last, last, 0.0)
    for i in range(len(node_depths) - 1):
        z0, z1 = node_depths[i], node_depths[i + 1]
        if z0 <= depth <= z1:
            if z1 == z0:
                return (i, i, 0.0)
            return (i, i + 1, (depth - z0) / (z1 - z0))
    last = len(node_depths) - 1
    return (last, last, 0.0)


@dataclass(frozen=True)
class AgeDepthPath:
    node_depths: tuple[float, ...]
    node_ages: tuple[float, ...]

    def age_at(self, depth: float) -> float:
        i0, i1, frac = _interp_weights(self.node_depths, depth)
        if i0 == i1:
            return self.node_ages[i0]
        return (1.0 - frac) * self.node_ages[i0] + frac * self.node_ages[i1]


def simulate_gamma_increment_path(spec: ArchivePriorSpec, rng: random.Random) -> AgeDepthPath:
    a0 = (
        spec.mean_surface_age + spec.sd_surface_age * rng.gauss(0.0, 1.0)
        if spec.sd_surface_age > 0.0
        else spec.mean_surface_age
    )
    ages = [a0]
    scale = spec.mean_sed_rate / spec.kappa
    for i in range(1, len(spec.node_depths)):
        dz = spec.node_depths[i] - spec.node_depths[i - 1]
        alpha = spec.kappa * dz
        inc = rng.gammavariate(alpha, scale)
        # Guard only against IEEE-754 underflow for extremely small alpha.
        if inc <= 0.0:
            inc = 1e-12
        ages.append(ages[-1] + inc)
    return AgeDepthPath(node_depths=spec.node_depths, node_ages=tuple(ages))


def _simulate_archive_dates(
    path: AgeDepthPath,
    spec: ArchivePriorSpec,
    cal_spec: CalibrationPriorSpec,
    w: list[float] | tuple[float, ...],
    rng: random.Random,
) -> ArchiveObservation:
    sds = spec.measurement_sds or tuple(30.0 for _ in spec.dated_depths)
    obs_dates: list[float] = []
    for z, sd in zip(spec.dated_depths, sds):
        true_age = path.age_at(z)
        cal_shift = cal_spec.evaluate(true_age, w)
        obs_dates.append(true_age + cal_shift + sd * rng.gauss(0.0, 1.0))
    return ArchiveObservation(
        prior=spec,
        observed_dates=tuple(obs_dates),
        measurement_sds=sds,
    )


def simulate_paired_chronology(
    spec: PairedChronologySpec,
    rng: random.Random,
) -> tuple[PublicChronologyObservation, OracleChronologyTruth]:
    path_a = simulate_gamma_increment_path(spec.archive_a, rng)
    path_b = simulate_gamma_increment_path(spec.archive_b, rng)
    cal_chol = _cholesky(spec.calibration.covariance_matrix())
    w_true = _sample_mvn_chol(cal_chol, rng)

    obs_a = _simulate_archive_dates(path_a, spec.archive_a, spec.calibration, w_true, rng)
    obs_b = _simulate_archive_dates(path_b, spec.archive_b, spec.calibration, w_true, rng)
    public_obs = PublicChronologyObservation(
        archive_a=obs_a,
        archive_b=obs_b,
        calibration_prior=spec.calibration,
    )
    oracle = OracleChronologyTruth(
        node_ages_a=path_a.node_ages,
        node_ages_b=path_b.node_ages,
        calibration_w=tuple(w_true),
        event_age_a=path_a.age_at(spec.archive_a.query_depth),
        event_age_b=path_b.age_at(spec.archive_b.query_depth),
    )
    return public_obs, oracle


# ---------------------------------------------------------------------------
# Summaries, Diagnostics, and Statistical Helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChronologyPosteriorSummary:
    samples_a: tuple[float, ...]
    samples_b: tuple[float, ...]
    mean_a: float
    sd_a: float
    mean_b: float
    sd_b: float
    cov_ab: float
    mean_delta: float
    sd_delta: float
    prob_a_older_than_b: float
    max_rhat: float
    reversal_count_a: int = 0
    reversal_count_b: int = 0
    ess: float | None = None

    def interval_a(self, level: float = 0.90) -> tuple[float, float]:
        return _central_interval(self.samples_a, level)

    def interval_b(self, level: float = 0.90) -> tuple[float, float]:
        return _central_interval(self.samples_b, level)

    def interval_delta(self, level: float = 0.90) -> tuple[float, float]:
        deltas = [a - b for a, b in zip(self.samples_a, self.samples_b)]
        return _central_interval(deltas, level)


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        raise ValueError("cannot take quantile of empty sequence")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return (1.0 - frac) * sorted_vals[lo] + frac * sorted_vals[hi]


def _central_interval(vals: tuple[float, ...] | list[float], level: float = 0.90) -> tuple[float, float]:
    alpha = 0.5 * (1.0 - level)
    s = sorted(vals)
    return (_quantile(s, alpha), _quantile(s, 1.0 - alpha))


def empirical_pit(samples: tuple[float, ...] | list[float], target: float) -> float:
    if not samples:
        raise ValueError("empty samples")
    less = sum(1 for x in samples if x < target)
    equal = sum(1 for x in samples if x == target)
    return (less + 0.5 * equal) / len(samples)


def ks_uniform_statistic(values: list[float]) -> float:
    if not values:
        raise ValueError("empty values")
    s = sorted(values)
    n = len(s)
    best = 0.0
    for i, x in enumerate(s):
        x_clamped = min(1.0, max(0.0, x))
        d_plus = (i + 1) / n - x_clamped
        d_minus = x_clamped - i / n
        best = max(best, d_plus, d_minus)
    return best


def _split_rhat(chains: list[list[float]]) -> float:
    subchains: list[list[float]] = []
    for ch in chains:
        half = len(ch) // 2
        if half < 2:
            return 1.0
        subchains.append(ch[:half])
        subchains.append(ch[half : 2 * half])
    m = len(subchains)
    n = len(subchains[0])
    means = [statistics.mean(sc) for sc in subchains]
    vars_ = [statistics.variance(sc) for sc in subchains]
    w_var = statistics.mean(vars_)
    b_var = n * statistics.variance(means)
    if w_var <= 1e-18:
        return 1.0 if b_var <= 1e-18 else float("inf")
    var_hat = ((n - 1.0) / n) * w_var + (1.0 / n) * b_var
    return math.sqrt(var_hat / w_var)


def _summarize_samples(
    chains_a: list[list[float]],
    chains_b: list[list[float]],
    reversal_a: int = 0,
    reversal_b: int = 0,
) -> ChronologyPosteriorSummary:
    sa = [x for ch in chains_a for x in ch]
    sb = [x for ch in chains_b for x in ch]
    deltas = [a - b for a, b in zip(sa, sb)]
    chains_d = [[a - b for a, b in zip(ca, cb)] for ca, cb in zip(chains_a, chains_b)]
    ma = statistics.mean(sa)
    mb = statistics.mean(sb)
    cov_ab = sum((a - ma) * (b - mb) for a, b in zip(sa, sb)) / (len(sa) - 1)
    max_rhat = max(_split_rhat(chains_a), _split_rhat(chains_b), _split_rhat(chains_d))
    return ChronologyPosteriorSummary(
        samples_a=tuple(sa),
        samples_b=tuple(sb),
        mean_a=ma,
        sd_a=statistics.stdev(sa),
        mean_b=mb,
        sd_b=statistics.stdev(sb),
        cov_ab=cov_ab,
        mean_delta=statistics.mean(deltas),
        sd_delta=statistics.stdev(deltas),
        prob_a_older_than_b=sum(1 for a, b in zip(sa, sb) if a > b) / len(sa),
        max_rhat=max_rhat,
        reversal_count_a=reversal_a,
        reversal_count_b=reversal_b,
    )


def shuffle_paired_ensemble(
    summary: ChronologyPosteriorSummary,
    rng: random.Random,
) -> ChronologyPosteriorSummary:
    """Destroy cross-archive pairing by permuting Archive B samples independently."""
    sb = list(summary.samples_b)
    rng.shuffle(sb)
    sa = list(summary.samples_a)
    deltas = [a - b for a, b in zip(sa, sb)]
    ma = statistics.mean(sa)
    mb = statistics.mean(sb)
    cov_ab = sum((a - ma) * (b - mb) for a, b in zip(sa, sb)) / (len(sa) - 1)
    return ChronologyPosteriorSummary(
        samples_a=tuple(sa),
        samples_b=tuple(sb),
        mean_a=ma,
        sd_a=statistics.stdev(sa),
        mean_b=mb,
        sd_b=statistics.stdev(sb),
        cov_ab=cov_ab,
        mean_delta=statistics.mean(deltas),
        sd_delta=statistics.stdev(deltas),
        prob_a_older_than_b=sum(1 for a, b in zip(sa, sb) if a > b) / len(sa),
        max_rhat=summary.max_rhat,
        reversal_count_a=summary.reversal_count_a,
        reversal_count_b=summary.reversal_count_b,
    )


# ---------------------------------------------------------------------------
# Exact Closed-Form Gaussian Limit & Importance Sampling Verifiers
# ---------------------------------------------------------------------------


def _archive_linear_design(
    prior: ArchivePriorSpec,
    depth: float,
    offset: int,
    total_dim: int,
) -> list[float]:
    vec = [0.0] * total_dim
    vec[offset] = 1.0  # a_0
    i0, i1, frac = _interp_weights(prior.node_depths, depth)
    # node_ages[i] = a_0 + sum_{k=1..i} inc_k
    for k in range(1, i0 + 1):
        vec[offset + k] = 1.0
    if i1 > i0:
        vec[offset + i1] = frac
    return vec


def analytic_gaussian_limit_posterior(
    obs: PublicChronologyObservation,
) -> ChronologyPosteriorSummary:
    """Closed-form posterior in the Gaussian accumulation + constant-offset limit."""
    pa = obs.archive_a.prior
    pb = obs.archive_b.prior
    na = len(pa.node_depths)  # 1 surface + (na - 1) increments
    nb = len(pb.node_depths)
    dim = na + nb + 1  # last index is constant shared offset w_0

    prior_mean = [0.0] * dim
    prior_prec = [[0.0] * dim for _ in range(dim)]

    def _init_archive_prior(prior: ArchivePriorSpec, off: int) -> None:
        prior_mean[off] = prior.mean_surface_age
        prior_prec[off][off] = 1.0 / max(prior.sd_surface_age**2, 1e-12)
        for i in range(1, len(prior.node_depths)):
            dz = prior.node_depths[i] - prior.node_depths[i - 1]
            prior_mean[off + i] = prior.mean_sed_rate * dz
            var_inc = (prior.mean_sed_rate**2 / prior.kappa) * dz
            prior_prec[off + i][off + i] = 1.0 / var_inc

    _init_archive_prior(pa, 0)
    _init_archive_prior(pb, na)

    cal_cov = obs.calibration_prior.covariance_matrix()
    w0_var = cal_cov[0][0]
    prior_mean[dim - 1] = 0.0
    prior_prec[dim - 1][dim - 1] = 1.0 / max(w0_var, 1e-12)

    q_post = [row[:] for row in prior_prec]
    h_post = [prior_prec[i][i] * prior_mean[i] for i in range(dim)]

    def _add_archive_obs(arch: ArchiveObservation, off: int) -> None:
        for z, y, sd in zip(arch.prior.dated_depths, arch.observed_dates, arch.measurement_sds):
            row = _archive_linear_design(arch.prior, z, off, dim)
            row[dim - 1] = 1.0
            inv_v = 1.0 / (sd * sd)
            for i in range(dim):
                if row[i] == 0.0:
                    continue
                h_post[i] += inv_v * y * row[i]
                for j in range(dim):
                    if row[j] != 0.0:
                        q_post[i][j] += inv_v * row[i] * row[j]

    _add_archive_obs(obs.archive_a, 0)
    _add_archive_obs(obs.archive_b, na)

    cov_post = _invert_spd(q_post)
    chol_q = _cholesky(q_post)
    mean_post = _solve_spd_chol(chol_q, h_post)

    qa = _archive_linear_design(pa, pa.query_depth, 0, dim)
    qb = _archive_linear_design(pb, pb.query_depth, na, dim)
    mean_a = _dot(qa, mean_post)
    mean_b = _dot(qb, mean_post)

    def _quad(u: list[float], v: list[float]) -> float:
        return sum(u[i] * cov_post[i][j] * v[j] for i in range(dim) for j in range(dim))

    var_a = _quad(qa, qa)
    var_b = _quad(qb, qb)
    cov_ab = _quad(qa, qb)
    var_delta = var_a + var_b - 2.0 * cov_ab
    mean_delta = mean_a - mean_b
    sd_delta = math.sqrt(max(var_delta, 1e-18))
    prob_older = 0.5 * (1.0 + math.erf(mean_delta / (sd_delta * math.sqrt(2.0))))
    return ChronologyPosteriorSummary(
        samples_a=(),
        samples_b=(),
        mean_a=mean_a,
        sd_a=math.sqrt(max(var_a, 1e-18)),
        mean_b=mean_b,
        sd_b=math.sqrt(max(var_b, 1e-18)),
        cov_ab=cov_ab,
        mean_delta=mean_delta,
        sd_delta=sd_delta,
        prob_a_older_than_b=prob_older,
        max_rhat=1.0,
    )


def _archive_log_lik(
    ages: list[float],
    arch: ArchiveObservation,
    cal_spec: CalibrationPriorSpec,
    w: list[float],
    dated_weights: list[tuple[int, int, float]],
) -> float:
    ll = 0.0
    for (i0, i1, frac), y, sd in zip(dated_weights, arch.observed_dates, arch.measurement_sds):
        age = ages[i0] if i0 == i1 else (1.0 - frac) * ages[i0] + frac * ages[i1]
        pred = age + cal_spec.evaluate(age, w)
        z = (y - pred) / sd
        ll -= 0.5 * z * z
    return ll


def _gamma_log_density(x: float, alpha: float, beta: float) -> float:
    return alpha * math.log(beta) - math.lgamma(alpha) + (alpha - 1.0) * math.log(x) - beta * x


def _archive_node_ages_log_prior(ages: list[float], spec: ArchivePriorSpec) -> float:
    lp = 0.0
    if spec.sd_surface_age > 0.0:
        z0 = (ages[0] - spec.mean_surface_age) / spec.sd_surface_age
        lp -= 0.5 * z0 * z0
    beta = spec.kappa / spec.mean_sed_rate
    for i in range(1, len(ages)):
        inc = ages[i] - ages[i - 1]
        if inc <= 0.0:
            return -float("inf")
        dz = spec.node_depths[i] - spec.node_depths[i - 1]
        lp += _gamma_log_density(inc, spec.kappa * dz, beta)
    return lp


def importance_sample_small_case(
    obs: PublicChronologyObservation,
    n_draws: int,
    rng: random.Random,
) -> ChronologyPosteriorSummary:
    """Independent joint importance sampler in node-age + calibration space."""
    pa = obs.archive_a.prior
    pb = obs.archive_b.prior
    cal = obs.calibration_prior
    cal_cov = cal.covariance_matrix()
    cal_chol = _cholesky(cal_cov)
    q_cal = cal.precision_matrix()
    dw_a = [_interp_weights(pa.node_depths, z) for z in pa.dated_depths]
    dw_b = [_interp_weights(pb.node_depths, z) for z in pb.dated_depths]

    def _node_targets(arch: ArchiveObservation) -> tuple[list[float], list[float]]:
        spec = arch.prior
        depth_to_obs = {z: (y, sd) for z, y, sd in zip(spec.dated_depths, arch.observed_dates, arch.measurement_sds)}
        centers: list[float] = []
        sds: list[float] = []
        for z in spec.node_depths:
            if z in depth_to_obs:
                y, sd = depth_to_obs[z]
                centers.append(y)
                sds.append(1.25 * sd)
            else:
                centers.append(spec.mean_surface_age + spec.mean_sed_rate * (z - spec.node_depths[0]))
                sds.append(max(50.0, spec.sd_surface_age))
        return centers, sds

    ca, sda = _node_targets(obs.archive_a)
    cb, sdb = _node_targets(obs.archive_b)
    cal_scale = 1.25

    qa_vals: list[float] = []
    qb_vals: list[float] = []
    log_ws: list[float] = []
    for _ in range(n_draws):
        w_raw = _sample_mvn_chol(cal_chol, rng)
        w = [cal_scale * x for x in w_raw]
        lq_w = _cal_log_prior(w, q_cal) / (cal_scale * cal_scale)

        ages_a: list[float] = []
        lq_a = 0.0
        for y_c, sd_p in zip(ca, sda):
            mu = y_c - cal.evaluate(y_c, w)
            age = mu + sd_p * rng.gauss(0.0, 1.0)
            ages_a.append(age)
            lq_a -= 0.5 * ((age - mu) / sd_p) ** 2

        ages_b: list[float] = []
        lq_b = 0.0
        for y_c, sd_p in zip(cb, sdb):
            mu = y_c - cal.evaluate(y_c, w)
            age = mu + sd_p * rng.gauss(0.0, 1.0)
            ages_b.append(age)
            lq_b -= 0.5 * ((age - mu) / sd_p) ** 2

        lp_a = _archive_node_ages_log_prior(ages_a, pa)
        lp_b = _archive_node_ages_log_prior(ages_b, pb)
        if not math.isfinite(lp_a) or not math.isfinite(lp_b):
            continue

        log_target = (
            lp_a
            + lp_b
            + _cal_log_prior(w, q_cal)
            + _archive_log_lik(ages_a, obs.archive_a, cal, w, dw_a)
            + _archive_log_lik(ages_b, obs.archive_b, cal, w, dw_b)
        )
        qa_vals.append(AgeDepthPath(pa.node_depths, tuple(ages_a)).age_at(pa.query_depth))
        qb_vals.append(AgeDepthPath(pb.node_depths, tuple(ages_b)).age_at(pb.query_depth))
        log_ws.append(log_target - (lq_w + lq_a + lq_b))

    if not log_ws:
        raise RuntimeError("importance sampler produced zero monotone draws")
    max_lw = max(log_ws)
    raw = [math.exp(lw - max_lw) for lw in log_ws]
    tot = sum(raw)
    wts = [r / tot for r in raw]
    ess = 1.0 / sum(w * w for w in wts)

    ma = sum(w * x for w, x in zip(wts, qa_vals))
    mb = sum(w * x for w, x in zip(wts, qb_vals))
    va = sum(w * (x - ma) ** 2 for w, x in zip(wts, qa_vals))
    vb = sum(w * (x - mb) ** 2 for w, x in zip(wts, qb_vals))
    cov_ab = sum(w * (a - ma) * (b - mb) for w, a, b in zip(wts, qa_vals, qb_vals))
    deltas = [a - b for a, b in zip(qa_vals, qb_vals)]
    md = sum(w * d for w, d in zip(wts, deltas))
    vd = sum(w * (d - md) ** 2 for w, d in zip(wts, deltas))
    prob_older = sum(w for w, d in zip(wts, deltas) if d > 0.0)
    return ChronologyPosteriorSummary(
        samples_a=(),
        samples_b=(),
        mean_a=ma,
        sd_a=math.sqrt(max(va, 1e-18)),
        mean_b=mb,
        sd_b=math.sqrt(max(vb, 1e-18)),
        cov_ab=cov_ab,
        mean_delta=md,
        sd_delta=math.sqrt(max(vd, 1e-18)),
        prob_a_older_than_b=prob_older,
        max_rhat=1.0,
        ess=ess,
    )


# ---------------------------------------------------------------------------
# Joint Metropolis-within-Gibbs Monotone Chronology Sampler
# ---------------------------------------------------------------------------


def _gamma_log_prior_from_log_inc(u: float, alpha: float, beta: float) -> float:
    # u = log(inc); includes +u Jacobian from d(inc)/du = inc.
    return alpha * u - beta * math.exp(u)


def _archive_log_prior(
    a0: float,
    log_incs: list[float],
    spec: ArchivePriorSpec,
) -> float:
    lp = 0.0
    if spec.sd_surface_age > 0.0:
        z0 = (a0 - spec.mean_surface_age) / spec.sd_surface_age
        lp -= 0.5 * z0 * z0
    beta = spec.kappa / spec.mean_sed_rate
    for i, u in enumerate(log_incs):
        dz = spec.node_depths[i + 1] - spec.node_depths[i]
        alpha = spec.kappa * dz
        lp += _gamma_log_prior_from_log_inc(u, alpha, beta)
    return lp


def _ages_from_log_incs(a0: float, log_incs: list[float]) -> list[float]:
    ages = [a0]
    for u in log_incs:
        ages.append(ages[-1] + math.exp(u))
    return ages


def _gibbs_sample_single_archive_cal(
    ages: list[float],
    arch: ArchiveObservation,
    dws: list[tuple[int, int, float]],
    cal: CalibrationPriorSpec,
    q_cal: list[list[float]],
    rng: random.Random,
) -> list[float]:
    m = len(cal.knot_ages)
    q_post = [row[:] for row in q_cal]
    h_post = [0.0] * m
    for (i0, i1, frac), y, sd in zip(dws, arch.observed_dates, arch.measurement_sds):
        age = ages[i0] if i0 == i1 else (1.0 - frac) * ages[i0] + frac * ages[i1]
        b = cal.basis_weights(age)
        inv_v = 1.0 / (sd * sd)
        resid = y - age
        for p in range(m):
            if b[p] == 0.0:
                continue
            h_post[p] += inv_v * resid * b[p]
            for q in range(m):
                if b[q] != 0.0:
                    q_post[p][q] += inv_v * b[p] * b[q]
    return _sample_mvn_precision(q_post, h_post, rng)


def _gibbs_sample_calibration(
    ages_a: list[float],
    ages_b: list[float],
    obs: PublicChronologyObservation,
    dw_a: list[tuple[int, int, float]],
    dw_b: list[tuple[int, int, float]],
    q_cal: list[list[float]],
    rng: random.Random,
) -> list[float]:
    cal = obs.calibration_prior
    m = len(cal.knot_ages)
    q_post = [row[:] for row in q_cal]
    h_post = [0.0] * m

    def _accum(ages: list[float], arch: ArchiveObservation, dws: list[tuple[int, int, float]]) -> None:
        for (i0, i1, frac), y, sd in zip(dws, arch.observed_dates, arch.measurement_sds):
            age = ages[i0] if i0 == i1 else (1.0 - frac) * ages[i0] + frac * ages[i1]
            b = cal.basis_weights(age)
            inv_v = 1.0 / (sd * sd)
            resid = y - age
            for p in range(m):
                if b[p] == 0.0:
                    continue
                h_post[p] += inv_v * resid * b[p]
                for q in range(m):
                    if b[q] != 0.0:
                        q_post[p][q] += inv_v * b[p] * b[q]

    _accum(ages_a, obs.archive_a, dw_a)
    _accum(ages_b, obs.archive_b, dw_b)
    return _sample_mvn_precision(q_post, h_post, rng)


def _cal_log_prior(w: list[float], q_cal: list[list[float]]) -> float:
    total = 0.0
    for i, wi in enumerate(w):
        for j, wj in enumerate(w):
            total += wi * q_cal[i][j] * wj
    return -0.5 * total


def _init_archive_state(arch: ArchiveObservation) -> tuple[float, list[float]]:
    prior = arch.prior
    a0 = prior.mean_surface_age
    if arch.observed_dates:
        # Rough initial alignment shifted toward earliest observed date minus prior depth age
        z0 = prior.dated_depths[0]
        a0 = arch.observed_dates[0] - prior.mean_sed_rate * (z0 - prior.node_depths[0])
    log_incs = [
        math.log(max(1e-6, prior.mean_sed_rate * (prior.node_depths[i + 1] - prior.node_depths[i])))
        for i in range(len(prior.node_depths) - 1)
    ]
    return a0, log_incs


def _run_single_chain(
    obs: PublicChronologyObservation,
    rng: random.Random,
    n_burnin: int,
    n_samples: int,
    calibration_mode: str,
) -> tuple[list[float], list[float], int, int]:
    pa = obs.archive_a.prior
    pb = obs.archive_b.prior
    cal = obs.calibration_prior
    q_cal = cal.precision_matrix()
    dw_a = [_interp_weights(pa.node_depths, z) for z in pa.dated_depths]
    dw_b = [_interp_weights(pb.node_depths, z) for z in pb.dated_depths]
    qa_w = _interp_weights(pa.node_depths, pa.query_depth)
    qb_w = _interp_weights(pb.node_depths, pb.query_depth)

    a0_a, u_a = _init_archive_state(obs.archive_a)
    a0_b, u_b = _init_archive_state(obs.archive_b)
    # Jitter initial chain starts for robust Rhat diagnostics
    if pa.sd_surface_age > 0.0:
        a0_a += 0.35 * pa.sd_surface_age * rng.gauss(0.0, 1.0)
    if pb.sd_surface_age > 0.0:
        a0_b += 0.35 * pb.sd_surface_age * rng.gauss(0.0, 1.0)
    u_a = [ui + 0.1 * rng.gauss(0.0, 1.0) for ui in u_a]
    u_b = [ui + 0.1 * rng.gauss(0.0, 1.0) for ui in u_b]

    ages_a = _ages_from_log_incs(a0_a, u_a)
    ages_b = _ages_from_log_incs(a0_b, u_b)
    w_a = [0.0] * len(cal.knot_ages)
    w_b = [0.0] * len(cal.knot_ages)

    step_a0_a = max(5.0, 0.4 * pa.sd_surface_age)
    step_a0_b = max(5.0, 0.4 * pb.sd_surface_age)
    step_u_a = [0.25] * len(u_a)
    step_u_b = [0.25] * len(u_b)
    step_ridge = max(5.0, 0.5 * cal.sd)

    adapt_end = int(0.6 * n_burnin)
    samples_a: list[float] = []
    samples_b: list[float] = []
    rev_a = 0
    rev_b = 0

    def _eval_query(ages: list[float], qw: tuple[int, int, float]) -> float:
        i0, i1, frac = qw
        return ages[i0] if i0 == i1 else (1.0 - frac) * ages[i0] + frac * ages[i1]

    def _update_archive(
        a0: float,
        u: list[float],
        ages: list[float],
        arch: ArchiveObservation,
        dws: list[tuple[int, int, float]],
        w_cur: list[float],
        step_a0: float,
        step_u: list[float],
        adapt: bool,
    ) -> tuple[float, list[float], list[float], float]:
        spec = arch.prior
        cur_lp = _archive_log_prior(a0, u, spec) + _archive_log_lik(ages, arch, cal, w_cur, dws)

        # 1. Surface age rigid shift (moves entire age-depth curve)
        if spec.sd_surface_age > 0.0:
            prop_a0 = a0 + step_a0 * rng.gauss(0.0, 1.0)
            prop_ages = _ages_from_log_incs(prop_a0, u)
            prop_lp = _archive_log_prior(prop_a0, u, spec) + _archive_log_lik(prop_ages, arch, cal, w_cur, dws)
            acc = math.log(max(rng.random(), 1e-300)) < (prop_lp - cur_lp)
            if acc:
                a0, ages, cur_lp = prop_a0, prop_ages, prop_lp
            if adapt:
                step_a0 *= 1.03 if acc else 0.985

        # 2. Single log-increment proposals
        for idx in range(len(u)):
            prop_u = u[:]
            prop_u[idx] += step_u[idx] * rng.gauss(0.0, 1.0)
            prop_ages = _ages_from_log_incs(a0, prop_u)
            prop_lp = _archive_log_prior(a0, prop_u, spec) + _archive_log_lik(prop_ages, arch, cal, w_cur, dws)
            acc = math.log(max(rng.random(), 1e-300)) < (prop_lp - cur_lp)
            if acc:
                u, ages, cur_lp = prop_u, prop_ages, prop_lp
            if adapt:
                step_u[idx] *= 1.03 if acc else 0.985

        # 3. Interior knot-age swaps (shifts node i without moving deeper nodes)
        for idx in range(len(u) - 1):
            inc1 = math.exp(u[idx])
            inc2 = math.exp(u[idx + 1])
            scale_k = 0.35 * min(inc1, inc2)
            delta = scale_k * rng.gauss(0.0, 1.0)
            ninc1 = inc1 + delta
            ninc2 = inc2 - delta
            if ninc1 <= 0.0 or ninc2 <= 0.0:
                continue
            prop_u = u[:]
            prop_u[idx] = math.log(ninc1)
            prop_u[idx + 1] = math.log(ninc2)
            prop_ages = _ages_from_log_incs(a0, prop_u)
            prop_lp = _archive_log_prior(a0, prop_u, spec) + _archive_log_lik(prop_ages, arch, cal, w_cur, dws)
            if math.log(max(rng.random(), 1e-300)) < (prop_lp - cur_lp):
                u, ages, cur_lp = prop_u, prop_ages, prop_lp

        return a0, u, ages, step_a0

    total_iters = n_burnin + n_samples
    for it in range(total_iters):
        adapt = it < adapt_end

        if calibration_mode == "joint":
            w_shared = _gibbs_sample_calibration(ages_a, ages_b, obs, dw_a, dw_b, q_cal, rng)
            w_a = w_shared
            w_b = w_shared
        elif calibration_mode == "independent":
            w_a = _gibbs_sample_single_archive_cal(ages_a, obs.archive_a, dw_a, cal, q_cal, rng)
            w_b = _gibbs_sample_single_archive_cal(ages_b, obs.archive_b, dw_b, cal, q_cal, rng)
        elif calibration_mode == "ignored":
            w_a = [0.0] * len(cal.knot_ages)
            w_b = w_a
        else:
            raise ValueError(f"Unknown calibration_mode: {calibration_mode}")

        a0_a, u_a, ages_a, step_a0_a = _update_archive(
            a0_a, u_a, ages_a, obs.archive_a, dw_a, w_a, step_a0_a, step_u_a, adapt
        )
        a0_b, u_b, ages_b, step_a0_b = _update_archive(
            a0_b, u_b, ages_b, obs.archive_b, dw_b, w_b, step_a0_b, step_u_b, adapt
        )

        # Joint calibration-ridge shift: (a_A + delta, a_B + delta, w - delta)
        if calibration_mode == "joint" and cal.sd > 0.0 and pa.sd_surface_age > 0.0 and pb.sd_surface_age > 0.0:
            delta = step_ridge * rng.gauss(0.0, 1.0)
            prop_a0_a = a0_a + delta
            prop_a0_b = a0_b + delta
            prop_ages_a = [x + delta for x in ages_a]
            prop_ages_b = [x + delta for x in ages_b]
            prop_w = [wi - delta for wi in w_a]

            cur_total = (
                _archive_log_prior(a0_a, u_a, pa)
                + _archive_log_prior(a0_b, u_b, pb)
                + _cal_log_prior(w_a, q_cal)
                + _archive_log_lik(ages_a, obs.archive_a, cal, w_a, dw_a)
                + _archive_log_lik(ages_b, obs.archive_b, cal, w_a, dw_b)
            )
            prop_total = (
                _archive_log_prior(prop_a0_a, u_a, pa)
                + _archive_log_prior(prop_a0_b, u_b, pb)
                + _cal_log_prior(prop_w, q_cal)
                + _archive_log_lik(prop_ages_a, obs.archive_a, cal, prop_w, dw_a)
                + _archive_log_lik(prop_ages_b, obs.archive_b, cal, prop_w, dw_b)
            )
            acc = math.log(max(rng.random(), 1e-300)) < (prop_total - cur_total)
            if acc:
                a0_a, a0_b = prop_a0_a, prop_a0_b
                ages_a, ages_b = prop_ages_a, prop_ages_b
                w_a = prop_w
                w_b = prop_w
            if adapt:
                step_ridge *= 1.03 if acc else 0.985

        if it >= n_burnin:
            if any(ages_a[i] <= ages_a[i - 1] for i in range(1, len(ages_a))):
                rev_a += 1
            if any(ages_b[i] <= ages_b[i - 1] for i in range(1, len(ages_b))):
                rev_b += 1
            samples_a.append(_eval_query(ages_a, qa_w))
            samples_b.append(_eval_query(ages_b, qb_w))

    return samples_a, samples_b, rev_a, rev_b


def infer_joint_chronology(
    obs: PublicChronologyObservation,
    rng: random.Random,
    n_chains: int = 4,
    n_burnin: int = 600,
    n_samples_per_chain: int = 800,
    calibration_mode: str = "joint",
) -> ChronologyPosteriorSummary:
    """Infer paired joint chronology posterior from PublicChronologyObservation only."""
    chains_a: list[list[float]] = []
    chains_b: list[list[float]] = []
    rev_a = 0
    rev_b = 0
    for _ in range(n_chains):
        sa, sb, ra, rb = _run_single_chain(
            obs=obs,
            rng=random.Random(rng.randrange(0, 2**31 - 1)),
            n_burnin=n_burnin,
            n_samples=n_samples_per_chain,
            calibration_mode=calibration_mode,
        )
        chains_a.append(sa)
        chains_b.append(sb)
        rev_a += ra
        rev_b += rb
    return _summarize_samples(chains_a, chains_b, reversal_a=rev_a, reversal_b=rev_b)


# ---------------------------------------------------------------------------
# Retained Non-Monotone Baseline & SBC Calibration Benchmark
# ---------------------------------------------------------------------------


def fit_unconstrained_nonmonotone(arch: ArchiveObservation) -> list[float]:
    """Unconstrained per-depth posterior mean ignoring monotonicity (retains reversals)."""
    prior = arch.prior
    out: list[float] = []
    for z, y, sd in zip(prior.dated_depths, arch.observed_dates, arch.measurement_sds):
        prior_m = prior.mean_surface_age + prior.mean_sed_rate * (z - prior.node_depths[0])
        prior_v = max(prior.sd_surface_age**2 + (prior.mean_sed_rate**2 / prior.kappa) * max(z - prior.node_depths[0], 1e-6), 1.0)
        obs_v = sd * sd
        post_prec = 1.0 / prior_v + 1.0 / obs_v
        post_mean = (prior_m / prior_v + y / obs_v) / post_prec
        out.append(post_mean)
    return out


@dataclass(frozen=True)
class CalibrationBenchmarkReport:
    n_trials: int
    joint_cov90_a: float
    joint_cov90_b: float
    joint_cov90_delta: float
    joint_ks_a: float
    joint_ks_delta: float
    joint_mean_width90_delta: float
    joint_order_brier: float
    shuffled_cov90_delta: float
    shuffled_ks_delta: float
    shuffled_mean_width90_delta: float
    shuffled_order_brier: float
    independent_cal_cov90_a: float
    independent_cal_cov90_delta: float
    independent_cal_mean_width90_delta: float
    independent_cal_order_brier: float
    ignored_cal_cov90_a: float
    ignored_cal_cov90_delta: float


def run_calibration_and_failure_benchmark(
    n_trials: int = 80,
    seed: int = 20261124,
) -> CalibrationBenchmarkReport:
    """Prior-predictive SBC/PIT under the model's own law plus retained failure modes."""
    spec = PairedChronologySpec.default_two_archive()
    rng = random.Random(seed)

    pits_a: list[float] = []
    pits_d_joint: list[float] = []
    pits_d_shuf: list[float] = []
    cov90_a = cov90_b = cov90_d_joint = cov90_d_shuf = 0
    cov90_a_ind = cov90_d_ind = 0
    cov90_a_ign = cov90_d_ign = 0
    widths_joint: list[float] = []
    widths_shuf: list[float] = []
    widths_ind: list[float] = []
    brier_joint: list[float] = []
    brier_shuf: list[float] = []
    brier_ind: list[float] = []

    for _ in range(n_trials):
        obs, truth = simulate_paired_chronology(spec, rng)
        joint = infer_joint_chronology(
            obs,
            rng=rng,
            n_chains=2,
            n_burnin=450,
            n_samples_per_chain=550,
            calibration_mode="joint",
        )
        shuf = shuffle_paired_ensemble(joint, rng)
        ind = infer_joint_chronology(
            obs,
            rng=rng,
            n_chains=2,
            n_burnin=400,
            n_samples_per_chain=450,
            calibration_mode="independent",
        )
        ign = infer_joint_chronology(
            obs,
            rng=rng,
            n_chains=2,
            n_burnin=400,
            n_samples_per_chain=450,
            calibration_mode="ignored",
        )

        lo_a, hi_a = joint.interval_a(0.90)
        lo_b, hi_b = joint.interval_b(0.90)
        lo_dj, hi_dj = joint.interval_delta(0.90)
        lo_ds, hi_ds = shuf.interval_delta(0.90)
        lo_an, hi_an = ind.interval_a(0.90)
        lo_dn, hi_dn = ind.interval_delta(0.90)
        lo_ai, hi_ai = ign.interval_a(0.90)
        lo_di, hi_di = ign.interval_delta(0.90)

        if lo_a <= truth.event_age_a <= hi_a:
            cov90_a += 1
        if lo_b <= truth.event_age_b <= hi_b:
            cov90_b += 1
        if lo_dj <= truth.delta_ab <= hi_dj:
            cov90_d_joint += 1
        if lo_ds <= truth.delta_ab <= hi_ds:
            cov90_d_shuf += 1
        if lo_an <= truth.event_age_a <= hi_an:
            cov90_a_ind += 1
        if lo_dn <= truth.delta_ab <= hi_dn:
            cov90_d_ind += 1
        if lo_ai <= truth.event_age_a <= hi_ai:
            cov90_a_ign += 1
        if lo_di <= truth.delta_ab <= hi_di:
            cov90_d_ign += 1

        widths_joint.append(hi_dj - lo_dj)
        widths_shuf.append(hi_ds - lo_ds)
        widths_ind.append(hi_dn - lo_dn)

        pits_a.append(empirical_pit(joint.samples_a, truth.event_age_a))
        joint_deltas = [a - b for a, b in zip(joint.samples_a, joint.samples_b)]
        shuf_deltas = [a - b for a, b in zip(shuf.samples_a, shuf.samples_b)]
        pits_d_joint.append(empirical_pit(joint_deltas, truth.delta_ab))
        pits_d_shuf.append(empirical_pit(shuf_deltas, truth.delta_ab))

        y_order = 1.0 if truth.event_age_a > truth.event_age_b else 0.0
        brier_joint.append((joint.prob_a_older_than_b - y_order) ** 2)
        brier_shuf.append((shuf.prob_a_older_than_b - y_order) ** 2)
        brier_ind.append((ind.prob_a_older_than_b - y_order) ** 2)

    return CalibrationBenchmarkReport(
        n_trials=n_trials,
        joint_cov90_a=cov90_a / n_trials,
        joint_cov90_b=cov90_b / n_trials,
        joint_cov90_delta=cov90_d_joint / n_trials,
        joint_ks_a=ks_uniform_statistic(pits_a),
        joint_ks_delta=ks_uniform_statistic(pits_d_joint),
        joint_mean_width90_delta=statistics.mean(widths_joint),
        joint_order_brier=statistics.mean(brier_joint),
        shuffled_cov90_delta=cov90_d_shuf / n_trials,
        shuffled_ks_delta=ks_uniform_statistic(pits_d_shuf),
        shuffled_mean_width90_delta=statistics.mean(widths_shuf),
        shuffled_order_brier=statistics.mean(brier_shuf),
        independent_cal_cov90_a=cov90_a_ind / n_trials,
        independent_cal_cov90_delta=cov90_d_ind / n_trials,
        independent_cal_mean_width90_delta=statistics.mean(widths_ind),
        independent_cal_order_brier=statistics.mean(brier_ind),
        ignored_cal_cov90_a=cov90_a_ign / n_trials,
        ignored_cal_cov90_delta=cov90_d_ign / n_trials,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Monotone sediment chronology verification CLI")
    parser.add_argument("--trials", type=int, default=80, help="Prior-predictive calibration trials")
    parser.add_argument("--seed", type=int, default=20261124, help="PRNG seed")
    args = parser.parse_args()

    spec = PairedChronologySpec.default_two_archive()
    obs, truth = simulate_paired_chronology(spec, random.Random(args.seed))
    ens = infer_joint_chronology(obs, random.Random(args.seed + 1))
    shuf = shuffle_paired_ensemble(ens, random.Random(args.seed + 2))
    report = run_calibration_and_failure_benchmark(n_trials=args.trials, seed=args.seed)

    out = {
        "single_case": {
            "max_rhat": round(ens.max_rhat, 4),
            "joint_cov_ab": round(ens.cov_ab, 2),
            "joint_sd_delta": round(ens.sd_delta, 2),
            "shuffled_sd_delta": round(shuf.sd_delta, 2),
            "reversal_count": ens.reversal_count_a + ens.reversal_count_b,
            "oracle_delta_ab": round(truth.delta_ab, 2),
        },
        "sbc_benchmark": {
            "n_trials": report.n_trials,
            "joint_cov90_a": round(report.joint_cov90_a, 4),
            "joint_cov90_b": round(report.joint_cov90_b, 4),
            "joint_cov90_delta": round(report.joint_cov90_delta, 4),
            "joint_ks_a": round(report.joint_ks_a, 4),
            "joint_ks_delta": round(report.joint_ks_delta, 4),
            "joint_mean_width90_delta": round(report.joint_mean_width90_delta, 2),
            "joint_order_brier": round(report.joint_order_brier, 4),
            "shuffled_cov90_delta": round(report.shuffled_cov90_delta, 4),
            "shuffled_ks_delta": round(report.shuffled_ks_delta, 4),
            "shuffled_mean_width90_delta": round(report.shuffled_mean_width90_delta, 2),
            "shuffled_order_brier": round(report.shuffled_order_brier, 4),
            "independent_cal_cov90_a": round(report.independent_cal_cov90_a, 4),
            "independent_cal_cov90_delta": round(report.independent_cal_cov90_delta, 4),
            "independent_cal_mean_width90_delta": round(report.independent_cal_mean_width90_delta, 2),
            "independent_cal_order_brier": round(report.independent_cal_order_brier, 4),
            "ignored_cal_cov90_a": round(report.ignored_cal_cov90_a, 4),
            "ignored_cal_cov90_delta": round(report.ignored_cal_cov90_delta, 4),
        },
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
