#!/usr/bin/env python3
"""Gaussian regime boundaries and a sediment estimand counterexample.

Independent implementation of the conjugate segmentation law described by
Qiang & Ruggieri (2023), section 2. Not their software or a real-core fit.
No external packages. See CHANGE_POINT.md for priors and endpoint conventions.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction
import json
import hashlib
import math
import random


NEG_INF = -math.inf


def logsum(values):
    values = tuple(values)
    top = max(values, default=NEG_INF)
    return top if top == NEG_INF else top + math.log(math.fsum(math.exp(v-top) for v in values))


@dataclass(frozen=True)
class Prior:
    precision: tuple[float, ...] = (0.01, 0.01)
    degrees: float = 1.0
    variance: float = 1.0
    min_length: int = 5
    max_changes: int = 3

    def __post_init__(self):
        if len(self.precision) not in (1, 2):
            raise ValueError('constant or linear model required')
        if any(not math.isfinite(v) or v <= 0 for v in (*self.precision, self.degrees, self.variance)):
            raise ValueError('positive finite prior parameters required')
        if not math.isfinite(self.degrees*self.variance):
            raise ValueError('prior variance scale product must be finite')
        if type(self.min_length) is not int or self.min_length < 1:
            raise ValueError('positive integer minimum length required')
        if type(self.max_changes) is not int or self.max_changes < 0:
            raise ValueError('nonnegative integer maximum changes required')


class SegmentEvidence:
    """O(1) conjugate log evidence for each nonempty half-open segment.

    sigma^2 ~ InverseGamma(v0/2, v0*s0^2/2), beta|sigma^2 ~
    Normal(0, sigma^2 * diag(1/k0)). Independent segment parameters.
    """
    def __init__(self, x, y, prior):
        if not x or len(x) != len(y) or any(not math.isfinite(v) for v in (*x, *y)):
            raise ValueError('equal nonempty finite coordinate arrays required')
        if any(a >= b for a, b in zip(x, x[1:])):
            raise ValueError('strictly increasing coordinates required')
        self.n, self.prior = len(y), prior
        self.prefix = [[0.0] for _ in range(5)]
        for t, v in zip(x, y):
            for column, value in zip(self.prefix, (t, t*t, v, t*v, v*v)):
                column.append(column[-1] + value)
        if any(not math.isfinite(v) for column in self.prefix for v in column):
            raise ValueError('coordinate products overflow; rescale input')

    def __call__(self, left, right):
        if not 0 <= left < right <= self.n:
            raise ValueError('nonempty segment within data required')
        n = right-left
        sx, sxx, sy, sxy, syy = (p[right]-p[left] for p in self.prefix)
        k = self.prior.precision
        a = n+k[0]
        if len(k) == 1:
            logdet, quadratic = math.log(a), sy*sy/a
        else:
            # Cholesky/Schur form avoids subtracting two large products.
            schur = sxx+k[1]-sx*sx/a
            if schur <= 0:
                raise ArithmeticError('loss of positive definiteness; rescale coordinates')
            logdet = math.log(a)+math.log(schur)
            quadratic = sy*sy/a + (sxy-sx*sy/a)**2/schur
        residual = syy-quadratic
        if residual < -1e-9*max(1, syy):
            raise ArithmeticError('negative residual from floating point cancellation')
        residual = max(0.0, residual)
        a0 = self.prior.degrees/2
        b0 = self.prior.degrees*self.prior.variance/2
        an, bn = a0+n/2, b0+residual/2
        return (-n/2*math.log(2*math.pi)
                + (sum(math.log(v) for v in k)-logdet)/2
                + a0*math.log(b0)-an*math.log(bn)
                + math.lgamma(an)-math.lgamma(a0))


def partition_count(n, segments, minimum):
    """Compositions of n into segments of at least minimum observations."""
    spare = n-segments*minimum
    return math.comb(spare+segments-1, segments-1) if spare >= 0 else 0


@dataclass(frozen=True)
class Segmentation:
    count_probabilities: tuple[float, ...]
    boundary_probabilities: tuple[float, ...]
    one_change_probabilities: tuple[float, ...]

    @property
    def expected_changes(self):
        return math.fsum(k*p for k, p in enumerate(self.count_probabilities))


def segment_posterior(x, y, prior=Prior()):
    """Exact forward/backward sum, uniform K and uniform admissible partitions.

    Boundary b lies between observations b-1 and b. Entries 0 and n are
    always zero. Inclusion probabilities sum to E[K], not to one.
    One-change probabilities condition on K=1 and sum to one if allowed.
    """
    evidence = SegmentEvidence(x, y, prior)
    n, d, max_s = len(y), prior.min_length, prior.max_changes+1
    if max_s*d > n or n > 1000 or max_s*n*n > 20_000_000:
        raise ValueError('segments must fit; at most 1000 observations and 20 million DP work units')
    logs = {(a, b): evidence(a, b) for a in range(n) for b in range(a+d, n+1)}
    forward = [[NEG_INF]*(n+1) for _ in range(max_s+1)]
    backward = [[NEG_INF]*(n+1) for _ in range(max_s+1)]
    forward[0][0] = backward[0][n] = 0.0
    for s in range(1, max_s+1):
        for b in range(s*d, n+1):
            forward[s][b] = logsum(forward[s-1][a]+logs[a, b]
                                   for a in range((s-1)*d, b-d+1))
        for a in range(n-s*d, -1, -1):
            backward[s][a] = logsum(logs[a, b]+backward[s-1][b]
                                    for b in range(a+d, n-(s-1)*d+1))
    # Uniform K factor cancels. Correct for the count of valid partitions.
    prior_logs = [-math.log(partition_count(n, s, d)) for s in range(1, max_s+1)]
    joint = [forward[s][n]+prior_logs[s-1] for s in range(1, max_s+1)]
    normalizer = logsum(joint)
    count_p = tuple(math.exp(v-normalizer) for v in joint)
    boundary_p = [0.0]*(n+1)
    for b in range(d, n-d+1):
        boundary_p[b] = math.exp(logsum(
            forward[l][b]+backward[s-l][b]+prior_logs[s-1]
            for s in range(2, max_s+1) for l in range(1, s))-normalizer)
    one_p = [0.0]*(n+1)
    if max_s >= 2:
        for b in range(d, n-d+1):
            one_p[b] = math.exp(logs[0, b]+logs[b, n]-forward[2][n])
    return Segmentation(count_p, tuple(boundary_p), tuple(one_p))


def interval(values, probabilities, mass=0.9):
    """Equal-tail interval for a normalized discrete distribution."""
    if (not values or len(values) != len(probabilities) or not 0 < mass < 1
            or any(not math.isfinite(p) or p < 0 for p in probabilities)
            or abs(math.fsum(probabilities)-1) > 1e-8):
        raise ValueError('normalized distribution and mass in (0,1) required')
    def q(p):
        total = 0.0
        for value, weight in zip(values, probabilities):
            total += weight
            if total >= p:
                return value
        return values[-1]
    return (q((1-mass)/2), q((1+mass)/2))


def mixing_counterexample(event=0.0, mixing=200.0):
    """Analytic locations: latent step, half-height, and support kink."""
    if not all(math.isfinite(v) for v in (event, mixing)) or mixing <= 0:
        raise ValueError('finite event and positive mixing time required')
    return {'latent_event': event,
            'half_height': event+mixing*(1-math.log(2)),
            'support_kink': event+mixing,
            'mean_slope_at_event': -math.exp(-1)/mixing,
            'mean_curvature_at_event': -math.exp(-1)/mixing**2}


def response_moments(left, right):
    """Integrals of q, u*q, q^2 in dimensionless u=(f-tau)/h.

    q=1-exp(u-1) for u<1 and zero otherwise. This is a new analytic
    calculation for the counterexample, not a published inference method.
    """
    if not math.isfinite(left+right) or left >= right:
        raise ValueError('finite increasing interval required')
    upper = min(right, 1.)
    if left >= upper:
        return (0., 0., 0.)
    def primitive(u):
        e = math.exp(u-1)
        return (u-e, u*u/2-(u-1)*e, u-2*e+e*e/2)
    a, b = primitive(left), primitive(upper)
    return tuple(v-u for u, v in zip(a, b))


def population_segment_loss(left, right, linear=True):
    """Integrated squared error of the best line/constant against exact q."""
    length = right-left
    iq, ixq, iq2 = response_moments(left, right)
    projected = iq*iq/length
    if linear:
        projected += (ixq-(left+right)*iq/2)**2/(length**3/12)
    loss = iq2-projected
    if loss < -1e-9:
        raise ArithmeticError('loss cancellation; enlarge or rescale interval')
    return max(0., loss)


def population_window_scan(left=-4., right=3., cells=4000, linear=True):
    """Exhaustive finite candidate grid, NOT a certified continuous optimum.

    Domain units are h from tau. Every segment must occupy at least 1% of
    the window. Known noiseless response removes random and dating error.
    """
    if type(cells) is not int or not 100 <= cells <= 100000:
        raise ValueError('100..100000 candidate cells required')
    if not -20 <= left < right <= 20:
        raise ValueError('dimensionless window must be within [-20,20]')
    margin = max(1, math.ceil(cells/100))
    losses = []
    for i in range(margin, cells-margin+1):
        b = left+(right-left)*i/cells
        loss = population_segment_loss(left, b, linear)+population_segment_loss(b, right, linear)
        losses.append((loss, b))
    loss, boundary = min(losses)
    return {'window_in_mixing_units': [left, right], 'cells': cells,
            'candidate_spacing_in_mixing_units': (right-left)/cells,
            'linear': linear, 'best_grid_boundary_in_mixing_units': boundary,
            'integrated_squared_error_in_mixing_units': loss}


@dataclass(frozen=True)
class RationalInterval:
    """Minimal exact rational enclosures used only for the proof certificate."""
    low: Fraction
    high: Fraction

    def __post_init__(self):
        object.__setattr__(self, 'low', Fraction(self.low))
        object.__setattr__(self, 'high', Fraction(self.high))
        if self.low > self.high:
            raise ValueError('increasing interval endpoints required')

    @staticmethod
    def exact(value):
        return RationalInterval(Fraction(value), Fraction(value))

    def __add__(self, other):
        if not isinstance(other, RationalInterval):
            other = self.exact(other)
        return RationalInterval(self.low+other.low, self.high+other.high)

    __radd__ = __add__

    def __neg__(self):
        return RationalInterval(-self.high, -self.low)

    def __sub__(self, other):
        return self+-other if isinstance(other, RationalInterval) else self+-self.exact(other)

    def __mul__(self, other):
        if not isinstance(other, RationalInterval):
            other = self.exact(other)
        products = tuple(a*b for a in (self.low, self.high) for b in (other.low, other.high))
        return RationalInterval(min(products), max(products))

    __rmul__ = __mul__

    def __truediv__(self, other):
        if not isinstance(other, RationalInterval):
            other = self.exact(other)
        if other.low <= 0 <= other.high:
            raise ZeroDivisionError('interval includes zero')
        return self*RationalInterval(1/other.high, 1/other.low)

    def rounded_outward(self, bits=128):
        """Keep exact enclosure while bounding denominator growth."""
        denominator = 2**bits
        low = (self.low*denominator).__floor__()
        high = (self.high*denominator).__ceil__()
        return RationalInterval(Fraction(low, denominator), Fraction(high, denominator))


def exp_negative_enclosure(value, terms=80):
    """Enclose exp(-value), value >= 0, using Taylor and a geometric tail.

    For S_N=sum_{j=0}^N x^j/j!, the remaining positive terms are bounded
    above by t_(N+1)/(1-x/(N+2)). Invert the positive bounds for exp(-x).
    """
    value = Fraction(value)
    if value < 0 or type(terms) is not int or terms < 1 or value >= terms+2:
        raise ValueError('nonnegative argument below terms+2 required')
    term, total = Fraction(1), Fraction(1)
    for j in range(1, terms+1):
        term *= value/j
        total += term
    upper = total+(term*value/(terms+1))/(1-value/(terms+2))
    return RationalInterval(1/upper, 1/total)


def log_enclosure(value, terms=100):
    """Positive interval logarithm via log(z)=2*atanh((z-1)/(z+1))."""
    value = value.rounded_outward()
    if value.low <= 0 or type(terms) is not int or terms < 1:
        raise ValueError('positive interval and positive term count required')
    def point(z):
        t = (z-1)/(z+1)
        if abs(t) > Fraction(9, 10):
            raise ValueError('log argument too far from one for this certificate')
        total = sum((t**(2*j+1)/Fraction(2*j+1) for j in range(terms)), Fraction(0))*2
        tail = 2*abs(t)**(2*terms+1)/((2*terms+1)*(1-t*t))
        return total-tail, total+tail
    return RationalInterval(point(value.low)[0], point(value.high)[1])


def certified_mismatch():
    """Exact rational certificate: latent tau is NOT the best linear split.

    Compare population losses at b=0 and b=1/2, window [-4,3], tau=0,
    h=1. A strict improving candidate disproves optimality at tau; it does
    not require finding or claiming the global minimizer.
    """
    def primitive(u):
        e = exp_negative_enclosure(1-u)
        return (RationalInterval.exact(u)-e,
                RationalInterval.exact(u*u/2)-(u-1)*e,
                RationalInterval.exact(u)-2*e+e*e/2)
    def moments(left, right):
        left, right = Fraction(left), Fraction(right)
        if left >= 1:
            return (RationalInterval.exact(0),)*3
        a, b = primitive(left), primitive(min(right, Fraction(1)))
        return tuple(v-u for u, v in zip(a, b))
    def loss(left, right):
        left, right = Fraction(left), Fraction(right)
        iq, ixq, iq2 = moments(left, right)
        length = right-left
        cov = ixq-(left+right)*iq/2
        return iq2-iq*iq/length-cov*cov/(length**3/12)
    true_split = loss(-4, 0)+loss(0, 3)
    alternative = loss(-4, Fraction(1, 2))+loss(Fraction(1, 2), 3)
    gap = true_split-alternative
    if gap.low <= 0:
        raise ArithmeticError('certificate failed: strict improvement not proved')
    def binomial_profile_loss(left, right):
        left, right = Fraction(left), Fraction(right)
        iq, _, iq2 = moments(left, right)
        length = right-left
        # p=.1+.8q, Var(Y/16)=p(1-p)/16.
        # Projection residual for mean p is .8^2 times that for q.
        variance = (Fraction(9, 100)*length+Fraction(16, 25)*(iq-iq2))/16
        variance += Fraction(16, 25)*loss(left, right)
        # Divide by the constant old-regime variance; constants cancel.
        relative = variance/(length*Fraction(9, 1600))
        return length*log_enclosure(relative)
    binomial_gap = (binomial_profile_loss(-4, 0)+binomial_profile_loss(0, 3)
                    -binomial_profile_loss(-4, Fraction(1, 2))
                    -binomial_profile_loss(Fraction(1, 2), 3))
    if binomial_gap.low <= 0:
        raise ArithmeticError('binomial Gaussian-profile certificate failed')
    return {'claim': 'b=1/2 has strictly less integrated squared line-fit error than b=tau=0',
            'window': [-4, 3], 'mixing': 1, 'latent_event': 0,
            'alternative_boundary': .5, 'exact_rational_positive_gap_verified': True,
            'gap_display_only': [float(gap.low), float(gap.high)],
            'binomial_gaussian_profile_positive_gap_verified': True,
            'binomial_gaussian_profile_gap_display_only': [float(binomial_gap.low), float(binomial_gap.high)],
            'exponential_taylor_terms': 80}


def published_simulation(seed=20261124):
    """Reproduce section 3.1's white-noise constant-law control, one draw.

    Not a reproduction of the paper's aggregate table or a climate dataset.
    variance hyperprior uses sample variance, as specified there (empirical Bayes).
    """
    rng = random.Random(seed)
    x = tuple(range(1, 201))
    y = tuple(1+rng.gauss(0, 1) for _ in x)
    mean = math.fsum(y)/len(y)
    variance = math.fsum((v-mean)**2 for v in y)/(len(y)-1)
    prior = Prior((.01,), 1, variance, 5, 20)
    fit = segment_posterior(x, y, prior)
    return {'kind': 'published simulation law; new Python draw; empirical Bayes',
            'seed': seed, 'n': len(y), 'sample_variance': variance,
            'input_sha256': hashlib.sha256(json.dumps([x, y], separators=(',', ':')).encode()).hexdigest(),
            'prior': prior.__dict__, 'p_zero_changes': fit.count_probabilities[0],
            'expected_changes': fit.expected_changes,
            'count_probabilities': fit.count_probabilities}


def draw_prior(x, prior, truth_rng, noise_rng):
    """Independent generative path: uniform count, stars/bars, actual parameters."""
    n, d = len(x), prior.min_length
    if (prior.max_changes+1)*d > n:
        raise ValueError('all prior counts must be feasible')
    k = truth_rng.randrange(prior.max_changes+1)
    spare = n-(k+1)*d
    bars = (-1,)+tuple(sorted(truth_rng.sample(range(spare+k), k)))+(spare+k,)
    lengths = tuple(b-a-1+d for a, b in zip(bars, bars[1:]))
    cuts, y, cursor = [], [], 0
    for size in lengths:
        variance = 1/truth_rng.gammavariate(prior.degrees/2, 2/(prior.degrees*prior.variance))
        beta = tuple(truth_rng.gauss(0, math.sqrt(variance/p)) for p in prior.precision)
        for t in x[cursor:cursor+size]:
            mean = beta[0]+(beta[1]*t if len(beta) == 2 else 0.)
            y.append(mean+noise_rng.gauss(0, math.sqrt(variance)))
        cursor += size
        cuts.append(cursor)
    return tuple(cuts[:-1]), tuple(y)


def calibration(trials=1000, seed=914073):
    """Own-law count calibration plus a prior-only negative control.

    Fixed priors here, not the empirical variance used by the published
    simulation. Diagnostic groups depend only on observations. All seeds are
    development seeds. No held-out result or event-time calibration is claimed.
    """
    if type(trials) is not int or not 1 <= trials <= 10000:
        raise ValueError('trials must be an integer from 1 to 10000')
    prior = Prior((.1,), 4, 1, 4, 2)
    x = tuple(range(24))
    truth_rng, noise_rng, pit_rng = (random.Random(seed+i) for i in range(3))
    location_rng = random.Random(seed+3)
    location_pits = []
    pits = {method: {'all': [], 'small_range': [], 'large_range': []}
            for method in ('posterior', 'prior_only')}
    information, coverage, masses = [], [], []
    for _ in range(trials):
        cuts, y = draw_prior(x, prior, truth_rng, noise_rng)
        fit = segment_posterior(x, y, prior)
        k, u = len(cuts), pit_rng.random()
        if k == 1:
            b = cuts[0]
            conditional = fit.one_change_probabilities
            location_pits.append(math.fsum(conditional[:b])+location_rng.random()*conditional[b])
        group = 'small_range' if max(y)-min(y) < 8 else 'large_range'
        for method, p in (('posterior', fit.count_probabilities), ('prior_only', (1/3,)*3)):
            value = math.fsum(p[:k])+u*p[k]
            pits[method]['all'].append(value)
            pits[method][group].append(value)
        p = fit.count_probabilities
        information.append(math.fsum(v*math.log(v*3) for v in p if v))
        lo, hi = interval((0, 1, 2), p)
        coverage.append(lo <= k <= hi)
        masses.append(math.fsum(p[lo:hi+1]))
    diagnostics = {}
    for method, groups in pits.items():
        diagnostics[method] = {}
        for group, values in groups.items():
            n = len(values)
            ordered = sorted(values)
            ks = max((max((i+1)/n-u, u-i/n) for i, u in enumerate(ordered)), default=None)
            diagnostics[method][group] = {'n': n, 'ks': ks,
                'individual_99_percent_dkw_band': math.sqrt(math.log(200)/(2*n)) if n else None}
    ordered = sorted(location_pits)
    n_location = len(ordered)
    location_ks = max((max((i+1)/n_location-u, u-i/n_location)
                       for i, u in enumerate(ordered)), default=None)
    return {'kind': 'own fixed-prior count calibration, development only',
            'trials': trials, 'seed': seed, 'prior': prior.__dict__,
            'group_rule': 'observed range < 8 versus >= 8',
            'diagnostics': diagnostics,
            'one_change_location_conditional_calibration': {'n': n_location,
                'ks': location_ks,
                'individual_99_percent_dkw_band': math.sqrt(math.log(200)/(2*n_location)) if n_location else None},
            'count_interval_coverage': sum(coverage)/trials,
            'count_interval_mean_posterior_mass': math.fsum(masses)/trials,
            'mean_count_information_nats': math.fsum(information)/trials}


@dataclass(frozen=True)
class ExactUnmixedPosterior:
    """Rational piecewise-uniform posterior, uniform event prior, zero mixing."""
    edges: tuple[Fraction, ...]
    masses: tuple[Fraction, ...]

    def cdf(self, age):
        age, total = Fraction(age), Fraction(0)
        for left, right, mass in zip(self.edges, self.edges[1:], self.masses):
            if age <= left:
                break
            total += mass*min(Fraction(1), (age-left)/(right-left))
        return float(total)

    def quantile(self, probability):
        probability, total = Fraction(str(probability)), Fraction(0)
        if not 0 <= probability <= 1:
            raise ValueError('probability must be in [0,1]')
        for left, right, mass in zip(self.edges, self.edges[1:], self.masses):
            if total+mass >= probability:
                return float(left+(right-left)*(probability-total)/mass)
            total += mass
        return float(self.edges[-1])


def exact_unmixed_posterior(focal_ages, counts, specimens, lower=-100, upper=100):
    """Independent exact comparator for p_old=1/10, p_young=9/10.

    Repeated binomial coefficients cancel. No time grid or quadrature is
    used: likelihood is constant between consecutive observed focal ages.
    """
    if (type(specimens) is not int or specimens < 1 or not focal_ages
            or len(counts) != len(focal_ages)
            or any(type(k) is not int or not 0 <= k <= specimens for k in counts)
            or any(not math.isfinite(v) for v in (*focal_ages, lower, upper))
            or any(a >= b for a, b in zip(focal_ages, focal_ages[1:])) or lower >= upper):
        raise ValueError('finite ordered ages, valid counts and increasing bounds required')
    focal = tuple(Fraction(v) for v in focal_ages)
    edges = tuple(sorted({Fraction(lower), Fraction(upper)}|
                         {v for v in focal if lower < v < upper}))
    weights = []
    for left, right in zip(edges, edges[1:]):
        midpoint, weight = (left+right)/2, right-left
        for f, k in zip(focal, counts):
            p = Fraction(9 if f <= midpoint else 1, 10)
            weight *= p**k*(1-p)**(specimens-k)
        weights.append(weight)
    normalizer = sum(weights, Fraction(0))
    return ExactUnmixedPosterior(edges, tuple(w/normalizer for w in weights))


class GaussianOneEventInference:
    """Explicit unmixed Gaussian working model for one latent boundary tau.

    K is FIXED to one, tau is uniform in physical time, and latent regimes
    have independent linear coefficients and variance with Prior's law.
    Observed proportions are assumed Gaussian at their known focal ages.
    Both Gaussian noise and absence of mixing are misspecifications for the
    foundation generator. This restricted countermodel is not Khider's full
    multiple-break procedure, nor its unidentified transition-window rule.
    """
    def __init__(self, focal_ages, prior=Prior((.01, .01), 1, .01, 4, 1), lower=-100., upper=100.):
        if prior.max_changes != 1:
            raise ValueError('this working model fixes exactly one event')
        # Validate coordinates without seeing any observations or truth.
        SegmentEvidence(focal_ages, (0.,)*len(focal_ages), prior)
        if not math.isfinite(lower+upper) or lower >= upper:
            raise ValueError('finite increasing event prior bounds required')
        self.focal_ages, self.prior = tuple(focal_ages), prior
        self.edges = tuple(sorted({lower, upper}|{f for f in focal_ages if lower < f < upper}))
        self.cuts = tuple(bisect_right(focal_ages, (a+b)/2)
                          for a, b in zip(self.edges, self.edges[1:]))
        if any(min(cut, len(focal_ages)-cut) < prior.min_length for cut in self.cuts):
            raise ValueError('event prior reaches an inadmissible end segment; do not silently truncate it')

    def fit(self, obs):
        if (obs.focal_ages != self.focal_ages or type(obs.specimens) is not int or obs.specimens < 1
                or len(obs.positive_counts) != len(self.focal_ages)
                or any(type(k) is not int or not 0 <= k <= obs.specimens for k in obs.positive_counts)):
            raise ValueError('observed counts must match the declared sampling design')
        y = tuple(k/obs.specimens for k in obs.positive_counts)
        return self.fit_values(y)

    def fit_values(self, y):
        """Also accept actual real Gaussian observations for own-law checks."""
        from continuous import Density
        if len(y) != len(self.focal_ages) or any(not math.isfinite(v) for v in y):
            raise ValueError('one finite response per focal age required')
        evidence = SegmentEvidence(self.focal_ages, y, self.prior)
        logs = tuple(evidence(0, cut)+evidence(cut, len(y))+math.log(b-a)
                     for cut, a, b in zip(self.cuts, self.edges, self.edges[1:]))
        normalizer = logsum(logs)
        return Density(self.edges, tuple(math.exp(v-normalizer) for v in logs))


def gaussian_event_calibration(trials=2000, seed=672419):
    """Prior-predictive continuous-time check for the declared Gaussian model.

    Irregular focal ages and partially intersected end gaps exercise the
    physical-time prior. Generator draws parameters and Gaussian errors;
    inference marginalizes them and receives only observed response values.
    """
    if type(trials) is not int or not 1 <= trials <= 10000:
        raise ValueError('trials must be an integer from 1 to 10000')
    x = (-3., -2., -1.5, -.8, -.2, 0., .4, .9, 1.2, 1.6, 2., 3.)
    prior = Prior((.2, .2), 4, 1, 3, 1)
    model = GaussianOneEventInference(x, prior, -1., 1.)
    truth_rng, noise_rng = random.Random(seed), random.Random(seed+1)
    pits, coverage, widths = [], [], []
    for _ in range(trials):
        event = truth_rng.uniform(-1, 1)
        regimes = []
        for _side in range(2):
            variance = 1/truth_rng.gammavariate(prior.degrees/2, 2/(prior.degrees*prior.variance))
            beta = tuple(truth_rng.gauss(0, math.sqrt(variance/k)) for k in prior.precision)
            regimes.append((variance, beta))
        y = []
        for focal in x:
            variance, beta = regimes[int(focal > event)]
            y.append(beta[0]+beta[1]*focal+noise_rng.gauss(0, math.sqrt(variance)))
        density = model.fit_values(tuple(y))
        lo, hi = density.quantile(.05), density.quantile(.95)
        pits.append(density.cdf(event))
        coverage.append(lo <= event <= hi)
        widths.append(hi-lo)
    ordered = sorted(pits)
    ks = max(max((i+1)/trials-u, u-i/trials) for i, u in enumerate(ordered))
    return {'kind': 'Gaussian one-event own fixed-prior law; development',
            'trials': trials, 'seed': seed, 'focal_ages': x, 'event_prior': [-1, 1],
            'prior': prior.__dict__, 'pit_ks': ks,
            'individual_99_percent_dkw_band': math.sqrt(math.log(200)/(2*trials)),
            'coverage_90': sum(coverage)/trials, 'mean_width': math.fsum(widths)/trials}


def foundation_comparison(seed=20261124):
    """Same specimens, two different estimands; descriptive comparison only."""
    from baseline import Design, simulate
    from continuous import ContinuousInference
    design = Design()
    obs = simulate(design, 0.0, 75.0, random.Random(seed))
    latent = ContinuousInference(design, step=.0625).fit(obs)
    unmixed_design = Design(mixing_times=(0.,))
    unmixed = ContinuousInference(unmixed_design, step=.0625).fit(obs)
    exact_unmixed = exact_unmixed_posterior(obs.focal_ages, obs.positive_counts, obs.specimens)
    gaussian_event = GaussianOneEventInference(design.focal_ages).fit(obs)
    x = obs.focal_ages
    y = tuple(k/obs.specimens for k in obs.positive_counts)
    # These priors and units are explicit development choices, not Khider's.
    prior = Prior((.01, .01), 1, .01, 4, 2)
    fit = segment_posterior(x, y, prior)
    boundary_labels = tuple(x[0] if b == 0 else x[-1] if b == len(x)
                            else (x[b-1]+x[b])/2 for b in range(len(x)+1))
    return {'kind': 'same data, mismatched estimands; known chronology oracle',
            'seed': seed, 'truth_for_evaluation_only': {'event': 0, 'mixing': 75},
            'focal_ages': x, 'positive_counts': obs.positive_counts,
            'specimens': obs.specimens, 'gaussian_prior': prior.__dict__,
            'latent_event_interval_90': [latent.quantile(.05), latent.quantile(.95)],
            'unmixed_event_interval_90_same_tau_estimand': [unmixed.quantile(.05), unmixed.quantile(.95)],
            'exact_rational_unmixed_interval_90': [exact_unmixed.quantile(.05), exact_unmixed.quantile(.95)],
            'gaussian_one_event_working_model_interval_90': [gaussian_event.quantile(.05), gaussian_event.quantile(.95)],
            'gaussian_count_probabilities': fit.count_probabilities,
            'gaussian_boundary_inclusion': fit.boundary_probabilities,
            'boundary_midpoint_labels': boundary_labels,
            'gaussian_one_change_interval_90_conditional_on_k1':
                interval(boundary_labels, fit.one_change_probabilities),
            'warning': 'Boundary midpoints are labels, not a posterior for latent event time.'}


def matched_event_calibration(trials=2000, seed=20261124, step=.0625):
    """Compare two models of the SAME latent tau on the SAME specimens.

    This supplies a precise rescope prototype: continuous uniform tau and
    the foundation's actual finite mixing prior versus assumed zero mixing.
    It is not the published Gaussian segmentation method. Known chronology
    is an oracle in both fits. The latter model is deliberately misspecified.
    """
    from baseline import Design, ks_uniform, simulate
    from continuous import ContinuousInference
    if type(trials) is not int or not 1 <= trials <= 10000:
        raise ValueError('trials must be an integer from 1 to 10000')
    design = Design()
    models = {'observation_aware': ContinuousInference(design, step=step),
              'assume_no_mixing': ContinuousInference(Design(mixing_times=(0.,)), step=step),
              'gaussian_one_event_working_model': GaussianOneEventInference(design.focal_ages)}
    truth_rng, specimen_rng = random.Random(seed), random.Random(seed+1)
    records = {name: [] for name in models}
    max_unmixed_endpoint_discrepancy = 0.
    for _ in range(trials):
        event, mixing = truth_rng.uniform(-100, 100), truth_rng.choice(design.mixing_times)
        obs = simulate(design, event, mixing, specimen_rng)
        for name, model in models.items():
            density = model.fit(obs)
            lo, hi = density.quantile(.05), density.quantile(.95)
            records[name].append((density.cdf(event), lo <= event <= hi, hi-lo, mixing))
            if name == 'assume_no_mixing':
                exact = exact_unmixed_posterior(obs.focal_ages, obs.positive_counts, obs.specimens)
                max_unmixed_endpoint_discrepancy = max(max_unmixed_endpoint_discrepancy,
                    abs(lo-exact.quantile(.05)), abs(hi-exact.quantile(.95)))
    result = {}
    for name, rows in records.items():
        groups = {}
        for group, subset in [('all', rows)]+[(f'true_mixing_{h:g}', [r for r in rows if r[3] == h])
                                              for h in design.mixing_times]:
            n = len(subset)
            groups[group] = {'n': n,
                'pit_ks': ks_uniform([r[0] for r in subset]) if n else None,
                'individual_99_percent_dkw_band': math.sqrt(math.log(200)/(2*n)) if n and group == 'all' else None,
                'coverage_90': sum(r[1] for r in subset)/n if n else None,
                'mean_width': math.fsum(r[2] for r in subset)/n if n else None}
        result[name] = groups
    differences = [int(a[1])-int(b[1]) for a, b in
                   zip(records['observation_aware'], records['assume_no_mixing'])]
    difference_mean = math.fsum(differences)/trials
    difference_se = (math.sqrt(math.fsum((v-difference_mean)**2 for v in differences)
                              /(trials*(trials-1))) if trials > 1 else None)
    return {'kind': 'same latent-event estimand; known chronology oracle; development',
            'trials': trials, 'seed': seed, 'maximum_cell_width': step,
            'truth': 'tau Uniform[-100,100], h Uniform{0,25,75}; independent material specimens',
            'gaussian_working_prior': models['gaussian_one_event_working_model'].prior.__dict__,
            'paired_coverage_difference': difference_mean,
            'paired_coverage_difference_monte_carlo_se': difference_se,
            'max_unmixed_endpoint_discrepancy_vs_exact_rational': max_unmixed_endpoint_discrepancy,
            'warning': 'Only marginal observation-aware own-law PIT has a uniform target; mixing strata are robustness diagnostics.',
            'models': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261124)
    parser.add_argument('--foundation', action='store_true', help='also compare with foundation modules')
    parser.add_argument('--calibration', type=int, default=0, metavar='TRIALS',
                        help='also verify own fixed-prior count law')
    parser.add_argument('--event-trials', type=int, default=0, metavar='TRIALS',
                        help='compare common latent-event estimand, requires foundation')
    parser.add_argument('--event-step', type=float, default=.0625)
    parser.add_argument('--gaussian-event-trials', type=int, default=0, metavar='TRIALS',
                        help='also verify the Gaussian single-event model under its own law')
    args = parser.parse_args()
    result = {'counterexample': mixing_counterexample(),
              'certified_mismatch': certified_mismatch(),
              'published_simulation': published_simulation(args.seed),
              'population_window_scans': [population_window_scan(a, b, linear=linear)
                  for a, b in ((-4., 3.), (-1., 3.), (-4., .75)) for linear in (False, True)]}
    if args.foundation:
        result['foundation_comparison'] = foundation_comparison(args.seed)
    if args.calibration:
        result['calibration'] = calibration(args.calibration)
    if args.event_trials:
        result['matched_event_calibration'] = matched_event_calibration(args.event_trials, args.seed, args.event_step)
    if args.gaussian_event_trials:
        result['gaussian_event_calibration'] = gaussian_event_calibration(args.gaussian_event_trials)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
