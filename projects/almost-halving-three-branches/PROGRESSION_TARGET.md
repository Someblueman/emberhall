# The divisible arithmetic-progression subfamily

Rook, 21 November 2026. The attempt to cover every arithmetic progression
gives the following exact, two-parameter result:

> For all integers `q>=2` and `d>=1`, the tree with arm lengths
> `((q+1)d, qd, (q-1)d)` has disjoint homometric sets of size
> `floor((3qd+1)/2)`, the largest size allowed by disjointness.

This covers every arithmetic-progression triple whose middle arm is a
multiple of the spacing. It does **not** cover all `T(b+d,b,b-d)`: the
remaining nondivisible cases need further work. Priority remains provisional.

## Run it

From the [Emberhall repository](https://github.com/Someblueman/emberhall),
using Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/progression_target.py 7 10
```

The two arguments are q and d. This recorded run produced two sets of size
105 on `(80,70,60)`, target 104, with only the longest tip omitted.
The command emits all selected vertices and distance multiplicities;
`--summary` omits those lists. Its output can be passed to the existing
`published_cases.py --check -` command. `--prove` checks the two new
identities in three independent Laurent variables, not sampled lengths.

## The two cases already available

If q is even, omit the longest tip. The retained lengths are
`((q+1)d-1,qd,(q-1)d)`. The published block construction has width d,
odd quotient q+1 and remainder zero, so it partitions this entire subtree.
Its size is `3qd/2=floor((3qd+1)/2)`.

If q and d are both odd, use the full partition from
[PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md). It has size
`(3qd+1)/2`. That proof covers arbitrary odd q,d, not only fixed ratios.

It remains to handle odd q and even d. The construction below is new to
the project and closes this remaining parity case for every quotient.

## Odd q and even d

Write `d=2h`, `N=2q-2` and omit the longest tip. The retained lengths are
`((2q+2)h-1, 2qh, (2q-2)h)`. Give the centre sign +1.
On each arm, block j has interior depths `jh+p`, `1<=p<h`; the word
assigned to a block repeats from p=1. Boundaries have depths jh, with
j=1..2q+1 on arm 1, 1..2q on arm 2 and 1..N on arm 3.
Take positive signs for one set and negative signs for the other.

For **even h**:

| Arm | Interior words in order | Boundary signs |
|---|---|---|
| 1 | two `-+`, then N copies of `--`, then two `+-` | one `+`, then 2q copies of `-` |
| 2 | 2q copies of `+-` | 2q copies of `-` |
| 3 | N copies of `++` | N copies of `+` |

For **odd h**:

| Arm | Interior words in order | Boundary signs |
|---|---|---|
| 1 | `-+ -- +-`, then q-2 pairs of identical constant words alternating `++ ++`, `-- --`, starting and ending with `++ ++`, then `+- -- -+` | repeat `--++` and truncate to 2q+1 signs |
| 2 | `+-`, then N copies of `++`, then `-+` | q copies of `+-` |
| 3 | N copies of `--` | q-1 copies of `-+` |

There are exactly the stated numbers of blocks and boundaries. Empty
interiors at h=1 cause no problem. For even h, the three arm sign sums are
`-Nh-1, 0, Nh`. For odd h, they are `-1, N(h-1), -N(h-1)`.
Including the centre, each total is zero. All `6qh` retained vertices
therefore split into two sets of size `3qh=3qd/2`.

## Exact distance proof

Use the full-shell Q from NEXT_FAMILY.md on the retained subtree. Put
`r=z^h`, `s=r^N`; initially treat z,r,s as independent Laurent variables.
The endpoint monomials are `A_1=sr^4/z`, `A_2=sr^2`, `A_3=s`.
Write `D=1-z^2`, `U=(z-r)(1+z)`, and

```
E=-(z+r)(1-z) for even h,
E= (r-z)(1-z) for odd h.
```

Then U is D times a constant-positive block interior; E is D times a
`-+` block interior. Negation handles `--` and `+-`. A boundary sign at
jh contributes `+/- D*r^j`. This gives every S_i by finite geometric sums.

The following cleared numerators make those sums independently checkable.
Let `G=1-sr^2`, `C=1-s`. For even h set `H=1-r` and `Y_i=H*D*S_i`:

```
Y_1 = H*E*(1+r)*G - U*r^2*C + D*(H*r-r^2*G),
Y_2 = -(E+D*r)*G,
Y_3 = (U+D*r)*C.
```

For odd h set `H=1-r^4`, `V_+=1+r+r^2+r^3`,
`V_-=1-r+r^2-r^3`, `J=1-r^2`, and again `Y_i=H*D*S_i`:

```
Y_1 = H*(E*J*(1-sr)-U*(r+sr^2))
      + U*r*(1+r)*(r^2+s)*J
      + D*(-r*(1+r)*C*J+s*(-r-r^2+r^3)*H),
Y_2 = H*E*(sr-1) + U*r*C*V_+ + D*r*G*V_-,
Y_3 = -C*(U*V_+ + D*r*V_-).
```

For example, the alternating pairs in the odd-h middle run sum to
`U*r*(1+r)*(r^2+s)/(1+r^2)` because q-2 is odd. Its boundary string sums
to `-r*(1+r)*(1-s)/(1+r^2)+s*(-r-r^2+r^3)`.
These identities derive Y_1 directly, rather than fitting sampled outputs.

Use a star for simultaneous inversion of z,r,s. With `K=1-A_1-A_2-A_3`,
direct integer coefficient collection gives

```
D*H*K + sum_i Y_i*(1-sum_(j!=i) A_j) - eta*sum_i A_i*Y_i* = 0,
eta=z^2*r for even h, and eta=z^2*r^4 for odd h.
```

Indeed `(DH)*=DH/eta`, so the displayed expression is precisely DHQ.
The ring has no zero divisors and DH is nonzero; hence Q=0.
The signed-shell identity then proves equal distance multiplicities.
This is a proof for arbitrary odd q and even d. Combined with the first
two cases it proves the proposition for every q>=2,d>=1.

## A rigorous failure of the simpler prefix prescription

The broader search first tried only the longest tip when b is even, and
only the two longest tips when b is odd. The latter choice cannot work
when `b=3 mod 4` and d is even: its retained lengths are all odd, and the
two bipartition classes have sizes `(3b-3)/2` and `(3b+1)/2`, both odd.

In any bipartite graph, let a selected set of size m have parity imbalance
delta. The alternating sum of its distance profile is `(delta^2-m)/2`.
Thus equally sized homometric parts in a full partition must have equal
or opposite imbalances. Equal imbalances require both bipartition classes
to have even sizes; opposite imbalances require equal class sizes.
Neither holds for the retained tree above. This excludes **every** full
partition of that particular two-tip prefix, not every permitted pair in
the original tree.

It is emphatically not a counterexample to the target. For example, for
every `b=3 mod 4`, `d=b-1`, the original tree `(2b-1,b,1)` has two disjoint
paths of size `(3b-1)/2`, meeting the target, despite this failed prefix.

Bounded discovery check: the original prefix prescription was tested for
b=2..30 (435 cases); its 49 failures occurred in the parity class just
proved impossible. Changing those cases to omit one longest and one
shortest tip produced verified candidate pairs for b=2..60 (1,770 cases).
Each candidate was checked by exact distance counts. These finite outcomes
suggest a broader route; they do not prove the target for all progressions.
The discovery solver is not needed by the delivered standard-library code.

The remaining task is a proof for nondivisible middle lengths, such as
`b=5t,d=2t`, together with the already required independent reconstruction
and priority review. No full-milestone completion is claimed here.
