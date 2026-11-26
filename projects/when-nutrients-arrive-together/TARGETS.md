# Trait overlap and interaction are different targets

Rook, 26 November 2026. This derives a distinction within our reconstructed
equations; it does not change the accepted scoring target. SOURCE_AUDIT.md
records the related publication and the limits of that comparison.

Write r for uptake and G for uptake times yield. At fixed supply K, the
quasistatic resource branch is

```
a(x) = .5 + r.T x
R(x) = K / a(x)
f(log x) = G R(x) - .3.
```

Division is componentwise. Differentiating at a positive state gives

```
J_quasistatic = -G diag(R/a) r.T diag(x).
H_quasistatic = G diag(1/a).
```

The first matrix differentiates consumer log growth with respect to log
abundances. The second differentiates it with respect to resource supply.
The first is also the Schur complement of the resource block in our
accepted full Jacobian: 0 - G (-diag(a))^-1
(-diag(R) r.T diag(x)). Thus it is a zero-frequency elimination, not an
assertion that resources are fast in the actual experiment. Our accepted
finite-frequency transfer remains the full 36-state resolvent with colored
OU input; this static reduction does not replace it.

Neither of these matrices is generally G G.T. The latter is the symmetric
gain-trait overlap used as the fifteen-edge ranking target. Pair-label AUC
instead targets membership in the imposed two diet groups; single-linkage
guild AUC targets the connectivity filtration's ability to separate those
labels. These three targets remain distinct even if all classify perfectly
in a particular record. In particular, a high overlap score does not mean
the complete directional interaction Jacobian was inferred.

The formulas are checked by centered differences of the eliminated
nonlinear resource branch and independently by the full-Jacobian Schur
complement, for all twelve existing development communities. No new drive,
community, held-out outcome or ecological sampling uncertainty enters.
The check uses log-coordinate step 1e-5; its discrepancy is a finite-difference
diagnostic, not a rigorous derivative error bound.
Maximum Schur-complement disagreement is 5.56e-17; maximum centered-difference
disagreement is 4.74e-12 across the twelve communities.

Replay with the existing project imports available on PYTHONPATH:

```python
import numpy as np
from reference import community
from linear_reference import equilibrium, linear_system
base = np.r_[np.ones(24), np.full(6, 3.)]
for seed in range(4, 16):
    r, G, _ = community(seed)
    x, R = equilibrium(r, G, base)
    a = .5 + r.T @ x
    analytic = -(G * (R/a)) @ (r.T*x)
    full, _ = linear_system(r, G, x, R)
    schur = -G @ np.linalg.solve(full[6:, 6:], full[6:, :6])
    f = lambda z: G @ (base/(.5+r.T@np.exp(z))) - .3
    h = 1e-5; basis = np.eye(6)*h
    difference = np.column_stack([(f(np.log(x)+e)-f(np.log(x)-e))/(2*h)
                                  for e in basis])
    print(seed, np.max(np.abs(analytic-schur)),
          np.max(np.abs(analytic-difference)))
```

## An exact continuous-frequency asymptote

The existing local-linear transfer has full Jacobian J and supply injection
B=[0;I]. Expand its resolvent in powers of 1/(iw). The consumer block of B
is zero; the consumer block of JB is G. Therefore

```
H(w) = [(iw I-J)^-1 B]_consumer = G/(iw)^2 + O(|w|^-3).
S_x(w) = H(w) H(w)* A^2 omega/(omega^2+w^2).
lim_(|w|->infinity) w^6 S_x(w)/(A^2 omega) = G G.T.
```

Here A=.1 is the OU amplitude and omega=1 its decay rate. This concerns
the **linearized log-abundance** spectrum, not a proved nonlinear spectral
limit. The full resource dynamics are retained; no fast-resource reduction
or cancellation theorem is imported. If every row of G is nonzero, its
population magnitude-squared coherence consequently tends to

```
coherence_ij(infinity) = (G G.T)_ij^2 / [(G G.T)_ii (G G.T)_jj].
```

This is squared normalized gain overlap, whereas our ranking target uses
the unnormalized dot product. The two need not have the same ordering
when consumer gain norms differ. Also, our cross-power estimator first
standardizes each log-abundance trajectory; its spectral amplitude has
additional species variance factors. The asymptote does not prove that
finite-band integrated coherence or standardized cross-power must rank the
raw overlap perfectly, even with an arbitrarily long record.

Unit-spaced observations have Nyquist angular frequency pi. The infinite-
frequency continuous-spectrum result is **not** a property of the last
observed Welch bin: sampled spectra include aliases. The lemma is a
transfer-normalization and target-interpretation check, not a new estimator,
a claim of access to these frequencies, or authorization to change sampling.

An analytical diagnostic over all twelve existing development equilibria
gives these maxima (ordinary floating point, not rigorous error bounds):

| Angular frequency | Relative norm error in scaled spectrum | Maximum coherence-limit error |
|---:|---:|---:|
| 10 | .35256 | .08516 |
| 100 | .00568 | .00118 |
| 1000 | .00005719 | .00001189 |

No new ecological community or stochastic path is sampled. The algebra
establishes the limiting statement; these three checks only verify its
implementation against the accepted spectrum function. Run after the
previous replay block:

```python
from linear_reference import spectrum
for w in (10., 100., 1000.):
    errors, coherence_errors = [], []
    for seed in range(4, 16):
        r, G, _ = community(seed)
        x, R = equilibrium(r, G, base)
        J, B = linear_system(r, G, x, R)
        S = spectrum(w, J, B)
        target = G @ G.T
        errors.append(np.linalg.norm(S*w**6/.01-target)/np.linalg.norm(target))
        actual = abs(S)**2/np.outer(S.diagonal().real, S.diagonal().real)
        limit = target**2/np.outer(target.diagonal(), target.diagonal())
        coherence_errors.append(abs(actual-limit).max())
    print(w, max(errors), max(coherence_errors))
```

Next scientific work should decide which trait geometry is wanted while
preserving original raw-overlap scores for comparison. A normalized overlap
analysis would be an explicitly new target, not a correction of failed
raw-overlap results or an explanation established by this lemma alone.

As a post-hoc **trait-only** diagnostic, Spearman agreement of raw overlap
with the squared normalized overlap across the existing communities 4–15
has mean .97558 and minimum .925 (community 14). For community 9 it is
.96786. These are twelve known trait geometries, not new community draws
or independent uncertainty about a population. They are also not ceilings
on integrated-coherence performance: a finite-band statistic may rank raw
overlap more accurately than its infinite-frequency limit does. This
calculation alone does not explain the selected record-length change.

```python
from scipy.stats import spearmanr
from reference import PAIRS
agreement = []
for seed in range(4, 16):
    _, G, _ = community(seed)
    Q = G @ G.T
    normalized = Q**2 / np.outer(Q.diagonal(), Q.diagonal())
    value = spearmanr(Q[PAIRS], normalized[PAIRS]).statistic
    agreement.append(value)
    print(seed, value)
print('mean/minimum', np.mean(agreement), min(agreement))
```
