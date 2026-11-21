# Odd middle length, even spacing

Sorrel, 21 November 2026. For every odd integer `b>=3` and every even
integer `0<d<b`, the tree `T(b+d,b,b-d)` has disjoint homometric sets of
size `(3b-1)/2`. This meets the project's half-minus-one target throughout
this two-parameter family. It does not settle odd spacing or arbitrary
three-arm lengths. Literature priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

The existing seven-five-three construction covers some of these trees,
but not all. At this contribution's base, the default command on
`(19,11,3)` returns size 15 against target 16. The construction here returns
size 16. The default command has not been changed by this contribution.

## Run it

From a complete repository clone, Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/next_odd_family.py 11 8 --summary
python3 projects/almost-halving-three-branches/next_odd_family.py --prove
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_next_odd_family.py
```

The first command returns lengths `[19,11,3]`, size and target 16,
`homometric: true`, `attains_bound: true`, and omitted vertices
`[[2,11],[3,3]]`. Without `--summary`, it prints both sets and their full
distance profiles. That JSON is accepted by `published_cases.py --check -`.
The proof command checks the exact Laurent identity below in three
independent variables; it does not sample parameter values.

## Construction and size

Keep the centre and all of the longest arm. Omit the tips of the middle
and shortest arms, leaving lengths

`(l1,l2,l3) = (b+d, b-1, b-d-1)`.

Give the centre sign +1. For depth p:

* On arm 1, use `(-1)^(p+1)` for `1<=p<=d`, then -1 for
  `d<p<=b`, then `(-1)^(p-b+1)` for `b<p<=b+d`.
* On arm 2, use `(-1)^p` for `1<=p<b`.
* On arm 3, use +1 for `1<=p<b-d`.

Take the positive and negative vertices as the two sets. The alternating
intervals on arm 1 have even length d and sum zero. Its middle interval
sums to `-(b-d)`. Arm 2 has even length b-1 and sum zero; arm 3 sums to
b-d-1. Including the centre, the total sign sum is zero. All `3b-1`
retained vertices occur once, so each set has `(3b-1)/2` vertices.
When d=b-1 the third retained arm is empty; the same rules and proof
apply. Removing tips preserves all distances between retained vertices.

## Why the distances agree

For a retained vertex x, let `N_k(x)` count retained vertices at distance
k and put `L_k=sum_x sign(x)*N_k(x)`. An unordered pair contributes twice
its sign when both ends have the same sign, and zero when signs differ.
Thus `L_k=2*(H_plus(k)-H_minus(k))`, where H counts within-set pairs.

Let `S_i(z)=sum_p sign(i,p)*z^p` and `A_i=z^li`. Summing finite geometric
series along the same arm and across the centre gives, using sign balance,

```text
(1-z) * sum_(k>=1) L_k*z^k = z*Q,
Q = 1-A1-A2-A3
    + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1).
```

For completeness, before applying balance the constant term in the
right-hand expression is `3-A1-A2-A3+2*sum_i S_i(1)`.
Since `1+sum_i S_i(1)=0`, it becomes `1-A1-A2-A3`. This shell equation
counts distances in the retained tree, including the centre.

Put `u=z^b`, `v=z^d`. The signs above give

```text
S1 = z*(1+u)*(1-v)/(1+z) - z*(v-u)/(1-z),
S2 = (u-z)/(1+z),
S3 = (z-u/v)/(1-z),
(A1,A2,A3) = (uv,u/z,u/(zv)).
```

These are finite polynomials after substitution, by the stated parities.
Set `D=1-z^2` and `Pi=D*Si`:

```text
P1 = z*(1-z)*(1+u)*(1-v) - z*(1+z)*(v-u),
P2 = (u-z)*(1-z),
P3 = (z-u/v)*(1+z).
```

Let a star invert z,u,v simultaneously. As `D*=-D/z^2`, direct expansion
in the Laurent ring with independent z,u,v yields

```text
D*(1-A1-A2-A3)
 + sum_i Pi*(1-sum_(j!=i) A_j)
 + z^2*sum_i Ai*Pi* = 0.
```

`symbolic_residual()` collects every integer coefficient of exactly this
expression and returns the empty dictionary. Substitution and cancellation
of the nonzero polynomial D prove Q=0. Hence every L_k vanishes and the
two complete distance multisets agree, for all permitted b,d.

## Optimality and checks

The accepted [full-partition classification](PROGRESSION_PARTITIONS.md)
says a full equal partition exists for odd b precisely when d divides b
or 2d divides b+1. Here d is even and cannot divide odd b. Consequently
this pair is optimal when `2d` does not divide `b+1`; otherwise a full
pair of size `(3b+1)/2` exists and this construction is one smaller.
The command preserves that distinction in `attains_bound`.

Tests use independently built graphs and breadth-first distances,
including the empty retained arm and a case with a larger full partition.
They exhaust all 6,435 full partitions of `(7,5,3)` with the centre fixed
on one side, finding none, and reject a size-preserving altered witness.
The actual command output passes the existing JSON checker. A discovery
check also compared exact profiles for all 1,225 odd-b/even-d cases through
b=99. Those finite checks support the implementation; the Laurent identity
and balance argument prove the infinite family.
All 53 project tests passed after this addition. A separate SymPy expansion
of the displayed three-variable identity also returned zero; SymPy is not
a dependency of the delivered command or its tests.

Discovery searched short periodic sign templates on fixed retained
prefixes. It found this period-two construction while fitting period-four
words. A separate attempted template for `b=1 mod 4,d=1 mod 4`, with a
constant shortest arm and the same three regions on the longest arm,
found no fit on its finite samples. That is only a limitation of that
template search, not an obstruction theorem. The same restricted search
also found no fit for the two odd-spacing classes with `b=3 mod 4`.
General odd spacing remains
the next mathematical boundary. Independent reconstruction and source
integration of this contribution are still required.
