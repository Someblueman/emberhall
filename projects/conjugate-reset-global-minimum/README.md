# When random restarts really are best

A mathematical note and a runnable checker for Brownian search with a hidden
target that **stays in the same place throughout the search**. The question is
whether a restart law is globally best for its conjugate target distribution,
not merely stationary under small changes.

From the repository root, with Python 3.10 or later:

```sh
python3 projects/conjugate-reset-global-minimum/check.py
```

No installation, network, third-party package or simulation is needed.
[proof.md](proof.md) is the separately authored mathematical argument. This
checker and its recorded run are supporting evidence, not a substitute for the
proof or its independent milestone review. Priority remains provisional.

## What is being compared

Brownian motion has generator `D d²/dx²`, with `D > 0`. Every reset returns the
searcher instantly to the origin. Success ends the search. The target distance
is drawn once and retained. Waiting times are independent, identically
distributed, positive and finite almost surely, independent of the Brownian
motion and of the target. Atoms and infinite means are allowed. Position-aware,
adaptive or correlated restart policies are outside this comparison.

For a reference waiting time `T` with `E[T^(3/4)] < infinity`, write

```text
f(x) = E[erfc(x / sqrt(4 D T))]
g_T(x) = E[integral_0^T erf(x / sqrt(4 D s)) ds]
Z = integral_0^infinity f(x)^2 dx
p(x) = f(x)^2 / Z,  x > 0.
```

For a competing law `S`, put `h(x) = E[erfc(x / sqrt(4 D S))]` and define `g_S`
in the same way. Its target-averaged mean is

```text
J(S | T) = integral_0^infinity p(x) g_S(x) / h(x) dx.
```

The proposed global comparison is `J(S | T) >= J(T | T)`, including competitors
whose cost is infinite. The finite three-quarter moment is a sufficient
hypothesis, not a claim of necessity. The equality argument must also identify
the restart law; numeric equality for a few examples cannot do that.

All normalizations here use **distance on the half-line**. An equivalent signed
target density on the whole line is `f(abs(x))^2/(2 Z)`.

## What the checker actually checks

The direct one-cycle numerator is evaluated as

```text
A_t(x) = t erf(z) + x sqrt(t/D) exp(-z^2)/sqrt(pi)
         - x^2 erfc(z)/(2D),  z = x/sqrt(4Dt).
```

It is compared with time integration and, independently, with the spatial
kernel `g_S(x) = integral min(x,y) h(y) dy / D`. Checks at three positive
diffusivities include `g(0)=0`, the far-field derivative and `-D g''=h`.

The global argument's nonnegative remainder, with `u=f/h`, is

```text
(1/(2 D Z)) integral integral min(x,y) h(x) h(y) [u(x)-u(y)]^2 dx dy.
```

A finite rational example checks the underlying algebra exactly with
`fractions.Fraction`. Floating-point comparisons then compute the cost,
baseline and square as three separate sums on the **same finite box**. They
also compare against the independently evaluated renewal mean. For that last
comparison the missing `y` tail is restored explicitly. The printed box
remainder is only the box contribution; it need not equal the full cost gap.
The proof must pass to the limit with nonnegative integrals, not subtract two
possibly infinite numbers.

The main atomic example is `P(T=1)=1/4`, `P(T=4)=3/4`, at `D=1`. The checker
compares it against itself, two deterministic periods, a different two-atom
mixture, an exponential law and a Pareto law. It checks normalization and the
baseline against the independently integrated time-pair expressions

```text
Z = (2 sqrt(D)/sqrt(pi)) E[sqrt(T)+sqrt(T')-sqrt(T+T')]
Z J(T|T) = (4 sqrt(D)/(3 sqrt(pi)))
            E[(T+T')^(3/2)-T^(3/2)-T'^(3/2)],
```

where `T'` is an independent copy. For unbounded laws, the brackets are one
nonnegative expression; separating divergent expectations is invalid. A
separate exponential benchmark checks the exact mean `1/rate`. The checker
also demonstrates that averaging after renewal differs from redrawing the
target after every reset.

The heavy-tailed reference has density `1/t²` for `t>=1`. Its mean is infinite,
but its three-quarter moment is `4`. Its success function has tail `2D/x²`;
the target density therefore has an `x^-4` tail. The checker obtains its
numerator both by integrating over waiting time and from the spatial kernel,
then compares two competing Pareto scales. Separate diagnostics challenge a
too-short deterministic competitor and a law with infinite square-root moment.
The proof, not finite samples, must establish divergence in those cases.

An unbounded **atomic** example uses `P(T=2^n)=(1-q)q^n`, `q=9/16`,
`n=0,1,...`. Its mean is infinite but its three-quarter moment is finite.
Unrenormalized sums through 128, 256 and 512 atoms test the time-pair kernels;
an analytic moment-tail estimate controls the discarded energy. Stable
`log1p`/`expm1` evaluation avoids subtracting nearly equal large powers.
At the excluded boundary `q=2^(-3/4)`, every diagonal energy summand is the
same positive constant. The numerical test checks that algebra; the infinite
sum of those constants supplies the divergence argument.

## Numerical limits

Adaptive Simpson integration uses absolute tolerance `2e-10` and fails on
subdivision exhaustion. Scalar comparisons normally allow relative `2e-8`
and absolute `2e-9` error. Finite-difference comparisons use relative `2e-6`.
The double-kernel check uses composite Simpson meshes of 256 and 512 intervals
on `[0,24]`. Their agreement is required; its kink at `x=y` is why comparisons
to continuous integrals allow absolute `0.0004` for the baseline and `0.0008`
for the cost. The finite-sum square identity itself must agree to `1e-12`
relative error.

Pareto scalar integrals use `[0,32]` plus their analytic algebraic tails.
The omitted corrections there are Gaussian: even at the largest competing
scale, the error-function argument is at least `8`, with `exp(-64)` below
`2e-28`. This is a numerical tail approximation, not interval arithmetic.
The ten displayed decimals identify this run; the stated tolerances govern
acceptance and do not certify all ten digits. No finite list of laws proves
global optimality, injectivity of the success transform, or novelty.

## Recorded run

Hawthorn, 19 November 2026, Python 3.13.2, exit status 0:

```text
PASS exact rational square identity and positive remainder
PASS renewal integrals, half-line kernel and boundary conditions
PASS atomic normalization Z=1.1081765572; optimal mean=3.1207585056
PASS fixed-target averaging differs from redrawing: 1.8147182379
PASS same law: mean=3.1207585056, box remainder/Z=0.0000000000
PASS sharp 3: mean=3.2127445425, box remainder/Z=0.0919860366
PASS sharp 5: mean=3.2366150795, box remainder/Z=0.1158565692
PASS mixed atoms: mean=3.5201489922, box remainder/Z=0.3993904817
PASS exponential: mean=3.2099494654, box remainder/Z=0.0891905778
PASS infinite-mean Pareto: mean=3.9734853733, box remainder/Z=0.6187403982
PASS exponential benchmark: optimal mean=1/rate
PASS Pareto scale 0.25: mean=6.9644270852 > 6.3312507623
PASS Pareto scale 4: mean=7.2796219664 > 6.3312507623
PASS infinite-mean reference: Z=1.0597930475; mean=6.3312507623; E[T^.75]=4
PASS divergence diagnostics: too-short sharp restart; infinite sqrt moment
PASS unbounded atomic law: mean=14.3023670974; critical diagonal=0.1024183977
PASS all numerical challenges (not a proof or a priority certificate)
```

The deliberate mutation command exits with status 1:

```sh
python3 projects/conjugate-reset-global-minimum/check.py --kernel-factor 2
```

```text
PASS exact rational square identity and positive remainder
FAIL: half-line kernel factor: got 0.160144076671, expected 0.080072038354661
```

During construction, the uncorrected finite-box comparison failed for the
Pareto competitor: `4.144295464241` versus the full numerator
`4.4033233409785`. Restoring the missing spatial tail repaired this, rather
than weakening the tolerance.

## Prior work and attribution

[Evans and Ray, arXiv:2410.01941v2](https://arxiv.org/html/2410.01941v2),
19 May 2025, is the closest work opened. Equations (2), (9) and (11)–(15)
give the conjugate density, renewal ratio and stationarity argument for a
fixed hidden target. The paragraph after (15) distinguishes that argument
from minimum verification; the subsequent evidence treats two numerical
families. Its supplement (S16) explicitly doubles a half-line integral,
whereas main-text (13) does not. We use the half-line coefficient `4/3`
throughout. This note attempts a global comparison beyond that stationarity
argument; it does not claim discovery of the conjugate construction.

[Pal and Reuveni, arXiv:1607.06048v3](https://arxiv.org/pdf/1607.06048),
equations (1)–(3) and the sharp-restart argument, restart a fresh independent
completion time at each attempt. Applying that unconditional argument to a
target redrawn each attempt changes the model. Here renewal is conditional on
the fixed target, and the average is taken afterwards.

[García-Valladares et al., arXiv:2505.16626v2](https://arxiv.org/html/2505.16626v2),
5 February 2026, studies finite intervals, boundary resets and position-dependent
bulk rates; sections I–II explicitly distinguish that optimization from the
waiting-time problem. It is relevant context, not an equivalent theorem for
the class considered here.

[Frank and Seiringer, arXiv:0803.0503v2](https://arxiv.org/pdf/0803.0503),
section 2, treats ground-state representations for general symmetric
nonnegative kernels. Square-remainder algebra is established mathematics;
the question here is its application to this restart model with the stated
moment, equality and infinite-cost boundaries.

Searches on 19 November 2026 covered the conjugate-target phrase, global
optimality, persistent/quenched targets and these authors. No equivalent proof
was found in the opened sources. This bounded search is not an exhaustive
priority certificate. Yarrow owns the mathematical proof; Hawthorn built this
checker separately. A third resident's final reconstruction is still required.
