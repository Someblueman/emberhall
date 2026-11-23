"""Independent covariance, noise-law, and resampling regression checks."""
import math
import random
import statistics

import pytest
import noise_misspecification as nm
from general_finite_record import COORDS, pack
from general_tracks import matmul, transpose


@pytest.mark.parametrize('Q', [nm.NOISE, [[0., 0.], [0., .3]],
                               [[.2, -.1], [-.1, .05]], [[0., 0.], [0., 0.]]])
def test_factor_reconstructs_declared_covariance(Q):
    L = nm.covariance_factor(Q)
    recovered = matmul(L, transpose(L))
    for i in range(2):
        for j in range(2):
            assert recovered[i][j] == pytest.approx(Q[i][j], abs=1e-14)


@pytest.mark.parametrize('Q', [[[.25, .08], [.08, .02]],  # old negative determinant
    [[1., .1], [.2, 1.]], [[-1., 0.], [0., 1.]],
    [[0., .1], [.1, 1.]], [[float('nan'), 0.], [0., 1.]],
    [[float('inf'), 0.], [0., 1.]], [[1.]]])
def test_invalid_covariance_rejected_before_simulation(Q):
    with pytest.raises(ValueError):
        nm.covariance_factor(Q)


def test_population_arbitrary_white_noise_invariance():
    assert nm.population_checks() == []
    for g, Delta, eps in nm.designs().values():
        clean = [g.observed_cov_matrix(Delta, eps, 0., k) for k in range(3)]
        model = nm.NoisyMoments(g, nm.NOISE)
        for k in (-5, -2, -1, 1, 2, 5):
            assert model.observed_cov_matrix(Delta, eps, 0., k) == g.observed_cov_matrix(Delta, eps, 0., k)
        noisy = [model.observed_cov_matrix(Delta, eps, 0., k) for k in range(3)]
        for m in range(-3, 4):
            assert nm.branch_state(clean, Delta, eps, m) == nm.branch_state(noisy, Delta, eps, m)
        q = nm.quantities(pack(noisy), Delta, eps)
        assert abs(q['R']) < 1e-12
        assert q['eq_ell'] == pytest.approx(.19, abs=1e-12)
        assert q['off'] == pytest.approx(.08, abs=1e-12)
        assert q['lam_S'] > 0 and q['lam_D'] > 0


@pytest.mark.parametrize('law', ['gaussian', 'student-t5', 'blink-2pct'])
def test_noise_covariance_and_heavy_fourth_moments(law):
    rng = random.Random(4701)
    L = nm.covariance_factor(nm.NOISE)
    draws = [nm.noise_draw(rng, L, law) for _ in range(60000)]
    for i in range(2):
        assert abs(statistics.mean(x[i] for x in draws)) < 4*math.sqrt(nm.NOISE[i][i]/len(draws))
        for j in range(2):
            empirical = statistics.mean(x[i]*x[j] for x in draws)
            c = nm.scale_fourth_moment(law)
            a, b, d = nm.NOISE[i][i], nm.NOISE[i][j], nm.NOISE[j][j]
            se = math.sqrt((c*(a*d+2*b*b)-b*b)/len(draws))
            assert abs(empirical-b) < 4*se
    fourth = statistics.mean(x[0]**4 for x in draws)/nm.NOISE[0][0]**2
    if law == 'gaussian':
        assert 2.8 < fourth < 3.2
    else:
        assert fourth > 5


def test_declared_mixture_and_student_scaling():
    class Witness:
        def gauss(self, *args):
            return 1.
        def random(self):
            return .019
        def gammavariate(self, shape, scale):
            assert (shape, scale) == (2.5, 2.)  # chi-square with five degrees
            return 3.
    I = [[1., 0.], [0., 1.]]
    assert nm.noise_draw(Witness(), I, 'student-t5') == [1., 1.]
    assert nm.noise_draw(Witness(), I, 'blink-2pct') == [10/math.sqrt(2.98)]*2
    with pytest.raises(ValueError):
        nm.noise_draw(Witness(), I, 'other')


def test_lag_products_use_actual_pairs_without_block_seams():
    frames = [[float(t+1), float(10-t)] for t in range(12)]
    rows = nm.lag_products(frames)
    assert len(rows) == 10
    for t, row in enumerate(rows):
        for value, (k, i, j) in zip(row, COORDS):
            assert value == frames[t+k][i]*frames[t][j]


def test_bootstrap_prefix_sums_match_explicit_circular_blocks(monkeypatch):
    rows = [[float(i+j) for j in range(11)] for i in range(17)]
    observed = []
    def fake_quantities(x, *args):
        observed.append(x)
        return dict.fromkeys(nm.KEYS, x[0])
    monkeypatch.setattr(nm, 'quantities', fake_quantities)
    nm.block_bootstrap(rows, .9, .45, block=6, B=8, seed=43)
    rng = random.Random(43)
    for got in observed:
        indices = []
        while len(indices) < len(rows):
            start = rng.randrange(len(rows))
            indices.extend((start+j) % len(rows) for j in range(min(6, len(rows)-len(indices))))
        expected = nm.average([rows[i] for i in indices])
        assert got == pytest.approx(expected)


def test_unavailable_and_collapsed_bootstrap_are_not_zero_width(monkeypatch):
    rows = [[1.]*11 for _ in range(20)]
    monkeypatch.setattr(nm, 'quantities', lambda *args: None)
    assert nm.block_bootstrap(rows, .9, .45, 4, 10, 1) is None
    monkeypatch.setattr(nm, 'quantities', lambda *args: dict.fromkeys(nm.KEYS, 1.))
    assert nm.block_bootstrap(rows, .9, .45, 4, 10, 1) is None
    for block, B in ((0, 10), (21, 10), (4, 7)):
        with pytest.raises(ValueError):
            nm.block_bootstrap(rows, .9, .45, block, B, 1)


def test_fourth_cumulant_cannot_affect_symmetry_first_order_variance():
    # White-noise fourth cumulants have support only on Gamma(0) coordinates.
    for g, Delta, eps in nm.designs().values():
        model = nm.NoisyMoments(g, nm.NOISE)
        x = pack([model.observed_cov_matrix(Delta, eps, 0., k) for k in range(3)])
        gradients = nm.gradients(x, Delta, eps)
        assert gradients['R'][:3] == [0., 0., 0.]
        assert gradients['eq_ell'][:3] == pytest.approx([1., 0., -1.])
        assert gradients['off'][:3] == pytest.approx([0., 1., 0.])


def test_finite_anisotropic_gates_and_bootstrap_smoke():
    # Strong anisotropy makes a model mismatch visible in a finite record.
    for g, Delta, eps in nm.designs().values():
        result = nm.experiment(g, Delta, eps, nm.NOISE, 'gaussian',
                               n=2400, reps=6, B=24, seed=440100)
        assert result['fits'] == 6
        assert result['bootfits'] >= 4
        assert result['symmetry'] >= 3
        assert result['isotropic_gates'] < result['symmetry']
        assert all(0 <= v <= 6 for counts in result['counts'].values() for v in counts.values())


def test_fourth_cumulant_formula_matches_full_tensor_contraction():
    # Independent tensor assembly, including all cross-covariances.
    Q = [[.7, -.12], [-.12, .3]]
    coords = [(0, 0), (0, 1), (1, 1)]
    weights = {'R': [0., 0., 0.], 'eq_ell': [1., 0., -1.],
               'off': [0., 1., 0.]}
    for law in ('gaussian', 'student-t5', 'blink-2pct'):
        c = nm.scale_fourth_moment(law)-1
        tensor = [[c*(Q[i][j]*Q[p][q]+Q[i][p]*Q[j][q]+Q[i][q]*Q[j][p])
                   for p, q in coords] for i, j in coords]
        expected = {key: sum(w[i]*tensor[i][j]*w[j]
                             for i in range(3) for j in range(3))
                    for key, w in weights.items()}
        assert nm.cumulant_variances(Q, law) == pytest.approx(expected)
    assert nm.cumulant_variances(Q, 'blink-2pct')['off'] > nm.cumulant_variances(Q, 'student-t5')['off'] > 0


def test_bootstrap_failure_rates_count_as_coverage_misses(monkeypatch):
    g, Delta, eps = nm.designs()['general']
    monkeypatch.setattr(nm, 'block_bootstrap', lambda *args: None)
    result = nm.experiment(g, Delta, eps, nm.NOISE, 'student-t5',
                           n=200, reps=2, B=8)
    assert result['bootfits'] == 0
    assert result['counts']['block'] == dict.fromkeys(nm.KEYS, 0)


def test_exact_exposure_conditional_covariance_from_independent_ito_integral():
    # Direct integrate 2 H(s) D H(s)^T, with H=(exp(A s), int exp(A u)du).
    # This does not use stationary Sigma or the unconditional subtraction.
    for g, Delta, eps in nm.designs().values():
        _, _, joint = nm.exposure_transition(g, eps)
        direct = [[0.]*4 for _ in range(4)]
        steps = 600
        for t in range(steps+1):
            s = t*eps/steps
            H = nm.expm(nm.scale(g.A, s)) + nm.int_exp(g.A, s)
            integrand = matmul(matmul(H, g.Dm), transpose(H))
            weight = (1 if t in (0, steps) else 2)*eps/steps
            for i in range(4):
                for j in range(4):
                    direct[i][j] += weight*integrand[i][j]
        for i in range(4):
            for j in range(4):
                assert joint[i][j] == pytest.approx(direct[i][j], abs=5e-7)
        L = nm.cholesky(joint)
        for row, expected in zip(matmul(L, transpose(L)), joint):
            assert row == pytest.approx(expected, abs=1e-14)


def test_exact_simulator_population_lags_and_full_exposure_boundary():
    from general_finite_record import empirical_Gamma
    for g, Delta, eps in nm.designs().values():
        for duration in (eps, Delta):
            frames = nm.simulate_latent_exact(g, Delta, duration, 16000, 701)
            for k in range(3):
                got = empirical_Gamma(frames, k)
                expected = g.observed_cov_matrix(Delta, duration, 0., k)
                for row, target in zip(got, expected):
                    assert row == pytest.approx(target, abs=.035)
        for d, e, n in ((Delta, 0., 10), (Delta, Delta+1, 10), (Delta, eps, 0)):
            with pytest.raises(ValueError):
                nm.simulate_latent_exact(g, d, e, n, 1)
