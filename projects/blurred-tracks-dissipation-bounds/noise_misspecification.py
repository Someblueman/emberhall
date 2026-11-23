#!/usr/bin/env python3
"""White localization noise beyond isotropy and Gaussianity.

Run: python3 noise_misspecification.py [--reps 24 --frames 4000 --boot 80]
Known zero mean, independent noise at each frame, non-overlapping exposures.

Proof. Y_t=Xbar_t+eta_t, E eta=0, Cov eta=Q, with eta independent
of X and across t. Thus Gamma_Y(k)=Gamma_Xbar(k)+1[k=0]Q.
Consequently Phi=Gamma(2)Gamma(1)^-1, every available logarithm A_m,
Sigma_m=eps^2(U_m W_m)^-1 Phi^-1 Gamma(1), and its antisymmetric
residual R(m) are unchanged. At the true branch, subtracting the latent
zero-lag covariance leaves Q, so eq_ell=Q00-Q11 and off=Q01. These
are model failures of isotropic-noise gates, not drift failures.

For non-Gaussian iid localization noise the fourth cumulant contribution
to covariance of lag products is nonzero only when all four noise times
coincide. It therefore affects only the zero-lag/zero-lag block of the
moment covariance. The gradient of R has exactly zero zero-lag entries:
Gaussian Isserlis remains the correct first-order variance for R even
under these heavy tails. No universal bootstrap improvement for R is
claimed. The zero-lag gates can need a fourth-moment correction.

The experiment reports marginal coverage of population R, eq_ell, off,
not simultaneous confidence or coverage of dissipation bounds. The moving
block bootstrap resamples consecutive *lag-product vectors*, so artificial
frame joins never become lag pairs. All unavailable fits count as misses;
bootstrap failures are printed, never turned into zero-width intervals.
Gaussian Isserlis uses the true second moments (oracle comparison), while
bootstrap uses observed moments. Both are first-order approximations.
Latent exposure integration samples the exact joint Gaussian endpoint and
integral (up to matrix floating-point error); nonlinear finite-record bias
remains. Monte Carlo rates are
descriptive, with binomial Wilson intervals, not calibrated guarantees.

Recorded 23 November 2026: default command, all six designs/laws had 24/24
usable fits and bootstraps; true symmetry eligibility was 21..24/24 versus
3..6/24 after isotropic-noise gates. FAILED: none; project pytest: 92 passed.
Stress command: --noise-scale 8 --reps 96 --boot 120 (N=4000, block=16).
For blink noise, isotropic eq_ell/off coverage was Isserlis 84/78 of 96,
fourth-moment oracle 89/88, block bootstrap 93/90. General eq_ell/off was
80/84, 92/90, 92/89 respectively. Symmetry coverage (not positivity-gated)
was isotropic 87/92 and general 86/89 for Isserlis/block. Only 94/96 films
had usable bootstraps in each blink arm; these failures count as misses.
All extra isotropic gates rejected the true branch in the six stress arms.
These measured improvements do not establish nominal coverage, and even
Gaussian noise showed finite-record undercoverage in this stronger design.
"""
from __future__ import annotations

import argparse
import math
import random
import statistics

from general_finite_record import (COORDS, branch_quantities_general,
    moment_covariance_real, pack, simulate_general_frames, unpack)
from general_tracks import (FROZEN_GENERAL, GeneralVortex, add, branch_drifts,
    expm, int_exp, inverse2, matmul, scale, transpose)

KEYS = ('R', 'eq_ell', 'off')
NOISE = [[0.25, 0.08], [0.08, 0.06]]  # determinant +.0086
Z = 1.959963984540054


def covariance_factor(Q):
    """Validate finite symmetric positive semidefinite 2x2 Q, without repair."""
    if len(Q) != 2 or any(len(row) != 2 for row in Q):
        raise ValueError('noise covariance must be 2 by 2')
    a, b, c, d = (float(Q[0][0]), float(Q[0][1]),
                   float(Q[1][0]), float(Q[1][1]))
    if not all(map(math.isfinite, (a, b, c, d))) or b != c:
        raise ValueError('noise covariance must be finite and symmetric')
    if a < 0 or d < 0 or a*d-b*b < 0:
        raise ValueError('noise covariance must be positive semidefinite')
    if a == 0:
        return [[0., 0.], [0., math.sqrt(d)]]
    l = math.sqrt(a)
    return [[l, 0.], [b/l, math.sqrt(max(0., (a*d-b*b)/a))]]


class NoisyMoments:
    def __init__(self, motion, Q):
        covariance_factor(Q)
        self.motion, self.Q = motion, [list(row) for row in Q]

    def observed_cov_matrix(self, Delta, eps, ell2, k):
        G = self.motion.observed_cov_matrix(Delta, eps, 0., k)
        return add(G, self.Q) if k == 0 else G


def branch_state(Gs, Delta, eps, m):
    """Expose the algebraic quantities whose noise invariance is asserted."""
    Phi = matmul(Gs[2], inverse2(Gs[1]))
    A = dict(branch_drifts(Phi, Delta, [m]))[m]
    UW = matmul(int_exp(A, eps), int_exp(scale(A, -1), eps))
    S = scale(matmul(inverse2(UW), matmul(inverse2(Phi), Gs[1])), eps**2)
    return Phi, A, S, S[0][1]-S[1][0]


def designs():
    f = FROZEN_GENERAL
    return {'isotropic': (GeneralVortex([[-1., -1.4], [1.4, -1.]],
                                        [[1., 0.], [0., 1.]]), .9, .45),
            'general': (GeneralVortex(f['A'], f['Dm']), f['Delta'], f['eps'])}


def noise_draw(rng, L, kind):
    z = [rng.gauss(0, 1), rng.gauss(0, 1)]
    if kind == 'student-t5':
        # One common chi-square scale: multivariate t5, covariance I.
        multiplier = math.sqrt(3. / rng.gammavariate(2.5, 2.))
    elif kind == 'blink-2pct':
        # Exactly 2% probability, amplitude 10, normalized covariance I.
        multiplier = (10. if rng.random() < .02 else 1.) / math.sqrt(2.98)
    elif kind == 'gaussian':
        multiplier = 1.
    else:
        raise ValueError('unknown noise law')
    return [multiplier*(L[i][0]*z[0]+L[i][1]*z[1]) for i in range(2)]


def cholesky(M):
    """Small strictly positive definite covariance, with no eigenvalue clamp."""
    n = len(M)
    L = [[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            value = M[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
            if i == j:
                if not math.isfinite(value) or value <= 0:
                    raise ValueError('joint motion covariance is not positive definite')
                L[i][j] = math.sqrt(value)
            else:
                L[i][j] = value/L[j][j]
    return L


def exposure_transition(motion, eps):
    """Return E, U, Cov[(x_end, integral)|x_start].

    E=exp(A eps), U=integral exp(A s) ds. Stationarity gives
    Cov(x_end,I)=U Sigma, Cov(I)=eps^2 Gamma_latent(0).
    Subtract Cov(E x_start,U x_start) to condition on x_start.
    This handles non-normal A: cross-covariance order is essential.
    """
    S = motion.Sigma
    E, U = expm(scale(motion.A, eps)), int_exp(motion.A, eps)
    end = add(S, matmul(matmul(E, S), transpose(E)), -1.)
    integ = add(scale(motion.observed_cov_matrix(eps, eps, 0., 0), eps**2),
                matmul(matmul(U, S), transpose(U)), -1.)
    cross = add(matmul(U, S), matmul(matmul(E, S), transpose(U)), -1.)
    joint = [[0.]*4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            joint[i][j] = .5*(end[i][j]+end[j][i])
            joint[i+2][j+2] = .5*(integ[i][j]+integ[j][i])
            joint[i][j+2] = joint[j+2][i] = cross[i][j]
    return E, U, joint


def simulate_latent_exact(motion, Delta, eps, n, seed):
    if not 0 < eps <= Delta or n < 1:
        raise ValueError('require positive N and 0 < exposure <= frame interval')
    rng = random.Random(seed)
    E, U, joint = exposure_transition(motion, eps)
    L = cholesky(joint)
    L0 = cholesky(motion.Sigma)
    gap = Delta-eps
    Eg = expm(scale(motion.A, gap))
    Qg = add(motion.Sigma, matmul(matmul(Eg, motion.Sigma), transpose(Eg)), -1.)
    Lg = cholesky(Qg) if gap else None

    def mv(M, x):
        return [sum(a*b for a, b in zip(row, x)) for row in M]

    def draw(L):
        return mv(L, [rng.gauss(0., 1.) for _ in L])

    x = draw(L0)
    frames = []
    for _ in range(n):
        error = draw(L)
        integ, end = mv(U, x), mv(E, x)
        frames.append([(integ[i]+error[i+2])/eps for i in range(2)])
        x = [end[i]+error[i] for i in range(2)]
        if gap:
            xg, innovation = mv(Eg, x), draw(Lg)
            x = [xg[i]+innovation[i] for i in range(2)]
    return frames


def simulate(motion, Delta, eps, Q, n, seed, kind='gaussian', sub=None):
    L = covariance_factor(Q)
    frames = (simulate_latent_exact(motion, Delta, eps, n, seed) if sub is None
              else simulate_general_frames(motion, Delta, eps, 0., n, seed, sub=sub))
    rng = random.Random(seed + 8100000)
    return [[x+e for x, e in zip(frame, noise_draw(rng, L, kind))]
            for frame in frames]


def lag_products(frames):
    if len(frames) < 4:
        raise ValueError('at least four frames required')
    return [[frames[t+k][i]*frames[t][j] for k, i, j in COORDS]
            for t in range(len(frames)-2)]


def average(rows):
    return [sum(row[j] for row in rows)/len(rows) for j in range(len(rows[0]))]


def quantities(x, Delta, eps):
    return branch_quantities_general(*unpack(x), Delta, eps, 0)


def gradients(x, Delta, eps):
    out = {key: [] for key in KEYS}
    for j in range(len(x)):
        h = 1e-6*max(1., abs(x[j]))
        xp, xm = list(x), list(x)
        xp[j] += h
        xm[j] -= h
        qp, qm = quantities(xp, Delta, eps), quantities(xm, Delta, eps)
        if qp is None or qm is None:
            raise ValueError('unavailable finite-difference branch')
        for key in KEYS:
            out[key].append((qp[key]-qm[key])/(2*h))
    return out


def isserlis_sds(motion, Delta, eps, Q):
    model = NoisyMoments(motion, Q)
    Gs = [model.observed_cov_matrix(Delta, eps, 0, k) for k in range(3)]
    grad = gradients(pack(Gs), Delta, eps)
    S = moment_covariance_real(model, Delta, eps, 0.)
    return {key: math.sqrt(max(0., sum(v[a]*S[a][b]*v[b]
            for a in range(len(v)) for b in range(len(v)))))
            for key, v in grad.items()}


def scale_fourth_moment(kind):
    """E[s^4] when eta=s L z, E[s^2]=1, z standard Gaussian."""
    return {'gaussian': 1., 'student-t5': 3.,
            'blink-2pct': (.98+.02*10**4)/2.98**2}[kind]


def cumulant_variances(Q, kind):
    """Extra N*variance beyond Isserlis, for the three true-branch gates.

    Cum(eta_i,eta_j,eta_p,eta_q)=(E[s^4]-1) times the three
    covariance pairings. Gradient eq_ell=(1,0,-1), off=(0,1,0).
    Cross terms with latent Gaussian motion have zero fourth cumulant.
    """
    a, b, d = Q[0][0], Q[0][1], Q[1][1]
    excess = scale_fourth_moment(kind)-1
    return {'R': 0., 'eq_ell': excess*(3*a*a+3*d*d-2*a*d-4*b*b),
            'off': excess*(a*d+2*b*b)}


def block_bootstrap(rows, Delta, eps, block, B, seed):
    """Circular moving-block bootstrap of valid lag products; nonlinear refits.

    None denotes insufficient usable replicates. A successful result includes
    usable and attempted counts. At least 80% and at least eight must survive.
    """
    n = len(rows)
    if not 1 <= block <= n or B < 8:
        raise ValueError('require 1 <= block <= sample size and B >= 8')
    rng = random.Random(seed)
    samples = {key: [] for key in KEYS}
    # Prefix sums make each sampled block O(number of moments), not O(block).
    doubled = rows + rows
    prefixes = [[0.]*len(rows[0])]
    for row in doubled:
        prefixes.append([a+b for a, b in zip(prefixes[-1], row)])
    for _ in range(B):
        total = [0.]*len(rows[0])
        used = 0
        while used < n:
            start = rng.randrange(n)
            length = min(block, n-used)
            total = [a+hi-lo for a, hi, lo in
                     zip(total, prefixes[start+length], prefixes[start])]
            used += length
        q = quantities([a/n for a in total], Delta, eps)
        if q is not None and all(math.isfinite(q[key]) for key in KEYS):
            for key in KEYS:
                samples[key].append(q[key])
    usable = len(samples['R'])
    if usable < max(8, math.ceil(.8*B)):
        return None
    sds = {key: statistics.stdev(values) for key, values in samples.items()}
    if not all(math.isfinite(s) and s > 0 for s in sds.values()):
        return None
    return {'sds': sds, 'usable': usable, 'attempted': B}


def experiment(motion, Delta, eps, Q, kind, n=4000, reps=24, B=80,
               seed=440100, block=None):
    block = block or max(4, round(n**(1/3)))
    oracle = isserlis_sds(motion, Delta, eps, Q)
    population = quantities(pack([NoisyMoments(motion, Q).observed_cov_matrix(
        Delta, eps, 0., k) for k in range(3)]), Delta, eps)
    correction = cumulant_variances(Q, kind)
    counts = {method: dict.fromkeys(KEYS, 0)
              for method in ('isserlis', 'fourth-moment oracle', 'block')}
    fits = bootfits = survivors = gates = 0
    for r in range(reps):
        rows = lag_products(simulate(motion, Delta, eps, Q, n, seed+r, kind))
        q = quantities(average(rows), Delta, eps)
        if q is None:
            continue
        fits += 1
        boot = block_bootstrap(rows, Delta, eps, block, B, seed+100000+r)
        if boot is not None:
            bootfits += 1
        sd = {key: oracle[key]/math.sqrt(len(rows)) for key in KEYS}
        # Marginal true-branch symmetry set vs extra s19 isotropic-noise gates.
        symmetry = (abs(q['R']) <= Z*sd['R'] and q['lam_S'] > 0
                    and q['lam_D'] > 0)
        survivors += symmetry
        gates += symmetry and all(abs(q[key]) <= Z*sd[key]
                                  for key in ('eq_ell', 'off'))
        for key in KEYS:
            error = abs(q[key]-population[key])
            counts['isserlis'][key] += error <= Z*sd[key]
            counts['fourth-moment oracle'][key] += error <= Z*math.sqrt(
                (oracle[key]**2+correction[key])/len(rows))
            counts['block'][key] += (boot is not None and
                                    error <= Z*boot['sds'][key])
    return dict(counts=counts, reps=reps, fits=fits, bootfits=bootfits,
                symmetry=survivors, isotropic_gates=gates, block=block)


def population_checks():
    failures = []
    for name, (g, Delta, eps) in designs().items():
        clean = [g.observed_cov_matrix(Delta, eps, 0., k) for k in range(3)]
        for Q in (NOISE, [[0., 0.], [0., .3]], [[.2, -.1], [-.1, .05]]):
            model = NoisyMoments(g, Q)
            noisy = [model.observed_cov_matrix(Delta, eps, 0., k) for k in range(3)]
            for m in range(-2, 3):
                if branch_state(clean, Delta, eps, m) != branch_state(noisy, Delta, eps, m):
                    failures.append(name+' invariance')
            q = quantities(pack(noisy), Delta, eps)
            if abs(q['eq_ell']-(Q[0][0]-Q[1][1])) > 1e-10 or abs(q['off']-Q[0][1]) > 1e-10:
                failures.append(name+' zero-lag identity')
            grad = gradients(pack(noisy), Delta, eps)['R']
            if any(abs(v) > 1e-10 for v in grad[:3]):
                failures.append(name+' fourth-cumulant support')
    return failures


def coverage_interval(successes, trials):
    """Wilson 95% interval for the Monte Carlo success probability."""
    if trials < 1 or not 0 <= successes <= trials:
        raise ValueError('invalid binomial counts')
    p = successes/trials
    denominator = 1+Z**2/trials
    center = (p+Z**2/(2*trials))/denominator
    half = Z*math.sqrt(p*(1-p)/trials+Z**2/(4*trials**2))/denominator
    return max(0., center-half), min(1., center+half)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reps', type=int, default=24)
    parser.add_argument('--frames', type=int, default=4000)
    parser.add_argument('--boot', type=int, default=80)
    parser.add_argument('--noise-scale', type=float, default=1.,
                        help='multiply the declared covariance by this factor')
    parser.add_argument('--block', type=int, default=None,
                        help='circular block length (default round(N**(1/3)))')
    args = parser.parse_args()
    if args.reps < 2 or args.frames < 100 or args.boot < 8:
        parser.error('require reps >= 2, frames >= 100, boot >= 8')
    if not math.isfinite(args.noise_scale) or args.noise_scale <= 0:
        parser.error('noise scale must be finite and positive')
    if args.block is not None and not 1 <= args.block <= args.frames-2:
        parser.error('block length must lie between 1 and N-2')
    failures = population_checks()
    Q = scale(NOISE, args.noise_scale)
    print('White-noise population invariance; t5 and 2% blink, covariance', Q)
    print('Marginal 95% normal intervals; known mean; failures count as misses.')
    print('Brackets give 95% Wilson intervals for Monte Carlo coverage probabilities.')
    print(f'N={args.frames}, reps={args.reps}, B={args.boot}; exact exposure; seeds=440100+r')
    for name, (g, Delta, eps) in designs().items():
        for law in ('gaussian', 'student-t5', 'blink-2pct'):
            result = experiment(g, Delta, eps, Q, law, args.frames,
                                args.reps, args.boot, block=args.block)
            print(f'{name}/{law}: fits={result["fits"]}/{args.reps}, '
                  f'bootstrap={result["bootfits"]}/{args.reps}, block={result["block"]}; '
                  f'symmetry={result["symmetry"]}, +isotropic gates={result["isotropic_gates"]}')
            for method, counts in result['counts'].items():
                pieces = []
                for key, v in counts.items():
                    low, high = coverage_interval(v, args.reps)
                    pieces.append(f'{key}={v}/{args.reps} [{low:.3f},{high:.3f}]')
                summary = ', '.join(pieces)
                print(' ', method, summary)
            if result['fits'] == 0 or result['bootfits'] == 0:
                failures.append(name+'/'+law+' no usable fits')
            if law == 'gaussian' and result['isotropic_gates'] >= result['symmetry']:
                print('  NOTE: this finite design did not distinguish the extra gates')
    print('FAILED:', ', '.join(failures) if failures else 'none')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
