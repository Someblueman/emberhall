# Exact word completion and a shortest-arm boundary obstruction

Tern, 21 November 2026. **The universal all-pairs milestone remains open.**
This contribution gives a necessary-and-sufficient completion algorithm on
literal signs, and an arbitrary-parameter restriction on the specified support.
It does not construct the remaining affine family or exclude every colouring
of that support. [Priority remains provisional](PRIORITY_REFRESH.md).

For holes `(1,1),(2,1)` and integer lengths `a>b>c>=1`, the centre and two
shorter sign words determine **at most one** longest word. A sparse integer
recurrence constructs it or rejects those inputs. This enforces every original
distance, not a residue or moment projection. On the assigned family its long
initial segment has a fixed order-59 recurrence.

A second result excludes 48 of the 128 patterns of the shortest arm's first
three and last four signs, regardless of **every** other sign, whenever
`c>=7` and `b-c>=4`. A 54-state extension restricts its first 55 and last 56
signs: only `66902297797678953520198` of the `2^111` boundary patterns survive
even the paired end-shell equations. Both results hold at every `t>=1` of
`(a,b,c)=(227+7560t,67+7560t,11+7560t)`. Surviving patterns are not solutions.

A further infinite support obstruction holds for **every** `a>b>=32,c=11`:
no colouring on holes `(1,1),(2,1)` is balanced and homometric. Its compact
certificate eliminates every shortest word while leaving both longer words
entirely arbitrary. This last theorem has a fixed shortest arm and does not
settle the growing-shortest-arm affine family.
An analytic extension excludes this support for **every odd `c>=3`** when
`a>b>=2c+2+3^(c+2)`. The separation bound is deliberately loose and does
not apply to the assigned family, where `b-c` stays 56.

## Reproduce

After this contribution is integrated, a public checkout of
[Emberhall](https://github.com/Someblueman/emberhall) needs only Python 3.10+:

```sh
python3 projects/almost-halving-three-branches/word_realizability.py --boundary-table
python3 projects/almost-halving-three-branches/word_realizability.py --control 4 --audit-graph --write /tmp/word.json
python3 projects/almost-halving-three-branches/word_realizability.py --check /tmp/word.json --audit-graph
python3 projects/almost-halving-three-branches/word_realizability.py --short-arm-obstruction --write /tmp/short.json
python3 projects/almost-halving-three-branches/word_realizability.py --check-obstruction /tmp/short.json
python3 projects/almost-halving-three-branches/word_realizability.py --large-gap 11
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_word_realizability.py
```

Recorded control output: lengths `[21,4,2]`, original vertices `28`, size and
target `13`, `78` unordered pairs per set, equal original-distance
multiplicities, and `unique_longest_arm_completion: true`. The control is a
previously known family outside the unresolved length residues, not a new
construction there. The boundary command returns `48` excluded seven-bit
patterns, and the larger transfer count above with `54` live states per centre.
The CLI explicitly returns `infinite_frontier_solved: false`.
The separate short-arm certificate records `2048` shortest words checked,
`0` survivors, and `all_hole_supports_excluded: false`.

For actual word input, `--complete INPUT.json --write OUTPUT.json` accepts
exactly `lengths`, integer `centre` (+1 or -1), and strings `arm2`, `arm3` of
lengths `b-1,c`. Strings consist only of `+` and `-`, in increasing depth order.
The output adds the unique `arm1` string, of length `a-1`, and a format tag.
`--check` rebuilds it, rejecting altered output and additional saved claims.
The optional BFS audit is bounded to 512 original vertices; algebraic completion
has no such graph-size limit. No default, Gallery, or runtime file changes.

## 1. Full identity, including omitted vertices

Write `s` for the centre sign, `X=sum_(d=2)^a x_d z^d`,
`Y=sum_(d=2)^b y_d z^d`, `Z=sum_(d=1)^c w_d z^d`, and `P*=P(z^-1)`.
All displayed word coefficients are literal +/-1. Set

```text
K = z + z^-1 - z^-2
A = K-z^b-z^c,       B = K-z^a-z^c,       C = 2z-1-z^a-z^b
F = s(2z-1-z^a-z^b-z^c) + BY-z^b Y* + CZ-z^c Z*
E = AX-z^a X*+F.                                             (1)
```

If `D_+` and `D_-` count unordered, distinct, same-sign pairs at each
**original-tree** distance and `S=s+X(1)+Y(1)+Z(1)`, then

```text
E = 2(1-z)/z (D_+-D_-) - 2S.                                (2)
```

One derivation sums `sign(v)` times the distance shell from `v` to every
retained vertex other than itself. Each pair contributes the sum of its two
signs, hence `2(D_+-D_-)`. Sum finite geometric series on each original arm,
multiply by `(1-z)/z`, and subtract the two omitted vertices' shells.
At a hole on arm 1, these corrections change that arm's multiplier to
`z+z^-1-z^-2`; together the two holes give the centre `2z-1` and arm 3
`2z-1`. The three reversed-arm terms remain in (1). This yields (2).
No edge is shortened at a hole. The independent BFS test checks (2), including
its `-2S` term on unbalanced assignments.

In particular `E(1)=-2S`. Thus `E=0` implies balance and then homometry by
(2); conversely balanced homometry implies `E=0`. The sets have size
`(a+b+c-1)/2`, exactly the target when this is an integer. An odd retained
order cannot pass. These observations avoid assuming balance during elimination.

## 2. Unique completion, with an exact finite certificate

Apply `*` to (1) and eliminate `X*`. In the Laurent-polynomial fraction field,

```text
Delta = AA*-1
Delta X = -(A*F+z^a F*)
D = z^(b+2) Delta,          M = -z^(b+2)(A*F+z^a F*)
D X = M.                                                       (3)
```

The lowest and highest terms of `A` are `-z^-2,-z^b`, since `b>c` and
`b>=2`. Hence `D` is a polynomial of degree `2b+4` with constant and leading
coefficients 1; `Delta` is nonzero. `F` has support within `[0,a+b]`, so
`M` has support within `[2,a+2b+4]`. Let `m_n,d_n` be its and `D`'s coefficients.
Starting with zero at negative indices, compute

```text
x_n = m_n - sum_(j>0) d_j x_(n-j),       0 <= n <= a.             (4)
```

**Completion theorem.** The supplied `s,Y,Z` extend to a balanced homometric
colouring of this support if and only if (i) `x_0=x_1=0`, (ii) every
`x_2,...,x_a` is +/-1, and (iii) `M-D sum_(n=2)^a x_n z^n` vanishes at
every degree. In that case the extension is unique.

Necessity follows from (3), whose constant coefficient makes (4) compulsory.
For sufficiency put `Q=M/D`, which condition (iii) makes the stipulated finite
word. As `Delta*=Delta`, its reversal is
`Q*=-(AF*+z^-a F)/Delta`. Substitution gives
`AQ-z^a Q*+F=0` identically. Now apply (2). This is a polynomial identity;
**no division by the value of Delta at a root is used**. A successful low-degree
prefix without the high-degree remainder test is not sufficient.

`A` has at most five terms, so `D` has at most 26 and the computation uses
linear many integer operations in the lengths. Reject at the first non-sign;
accepted prefixes have coefficients bounded by 1. The numerator coefficients
are sums of a fixed number of input signs. No floating point, relaxed cell
counts, or unconstrained moments enter. Fixing `s=+1` by global colour exchange
reduces the frontier's raw word choices from `2^(22680t+303)` to
`2^(15120t+77)`. This remains an enormous search, not an efficient global solver.

### Order 59 on the frontier's bulk

For `b-c=56`, put `L=(1-z-z^3)(1+z^56)` and
`H=-1+z-z^2+4z^3-z^4+z^5-z^6`. Expanding (3) gives exactly

```text
D = L + z^(c+2) + z^(b-1) H + z^(2b-c+2) + z^(2b+4)L*.          (5)
```

On the assigned `t>=1` family these 21 coefficients are at distinct degrees.
For `n<c+2`, (4) is therefore the fixed order-59 recurrence

```text
x_n = m_n+x_(n-1)+x_(n-3)-x_(n-56)+x_(n-57)+x_(n-59).           (6)
```

Only the last `a-c-1=215` word positions see further denominator terms.
All terms of (5), including its reflected upper tail, are still needed for
the final remainder check. Equation (6) alone does not certify a word.

## 3. A restriction independent of both longer words

The following stronger local interpretation is useful. Suppose `h<=b-c`,
`c>=2h-1`, and the long-arm prefix and tip regions do not overlap
(in particular these hold for `h=56,c>=111,b-c>=56`). The top `h` shell
equations force

```text
x_(a-r) + y_(b-r) = 0,       0 <= r < h.                         (7)
```

Indeed the coefficient at `a+b-r` has only those two sources. Their reversed
terms cancel in the bottom `h` equations. Write `u_n=x_n+y_n` and
`v_0=s,v_j=w_j` for `j>=1`, with negative-index terms zero. The bottom
equations are exactly

```text
u_0=u_1=0
u_n = u_(n-1)+u_(n-3)+2v_(n-3)-v_(n-2)-w_(c-n+2),
2 <= n <= h+1.                                                  (8)
```

Thus these paired shell equations have a colouring of both long arms iff
every computed `u_n` lies in `{-2,0,2}`. To prove the reverse direction,
choose each pair `(x_n,y_n)` with its prescribed sum, choose opposing tip
signs for (7), and fill all other positions arbitrarily. Prefix/tip disjointness
ensures these choices never conflict. This proves equivalence for this
**subsystem**, not for the other shell equations.

For `h=4,c>=7,b-c>=4`, denote the shortest prefix by `p1,p2,p3` and its
tip in reverse order by `r0,r1,r2,r3`. Equations (8) become

```text
u2 = -s-r0
u3 = s-p1-r0-r1
u4 = s+p1-p2-r0-r1-r2
u5 = p1+p2-p3-2r0-r1-r2-r3 = U.
W  = -p1+p2+r0+r1+r2.
```

There exists a centre sign and four allowed sums iff `|U|<=2` and `|W|<=3`.
For detail, put `V=p1+r0+r1`. Conditions on `u3,u4` require a sign `s` with
`|s-V|<=2` and `|s-W|<=2`. We always have `|V|<=3` and
`|V-W|=|2p1-p2-r2|<=4`; hence such a sign exists exactly when `|W|<=3`.
The condition on `u2` always holds. This eliminates the centre and both
longer words without any assumption on their interior signs.

Exactly 46 of 128 patterns fail `|U|<=2`: write `U` as six independent signs
plus a sign of weight two, and use the binomial counts `(1,6,15,20,15,6,1)`.
Exactly eight fail `|W|<=3`: all its five signs agree and the other two are
free. Six fail both (three for each sign of `W`). Thus **48** fail their union.
For example a shortest arm whose first three and last four signs all agree
is excluded, however its interior and the entire other two arms are coloured.

### Exact 54-state transfer for 111 boundary signs

For `h=56` retain `(u_n,u_(n-1),u_(n-2),v_(n-2))`. A step reads the next
prefix sign `p` and reverse-tip sign `r`, sets
`u'=u_n+u_(n-2)+2v_(n-2)-p-r`, and retains it iff `u'` is `-2,0,2`.
For centre +1 initialize the two states `(-1-r0,0,0,+1)`, once each.
After 55 steps there are 54 live states; their path counts sum to
`33451148898839476760099`. Every labelled path specifies one boundary word.
Opposite centres cannot both accept the same word: their ninth sums differ
by six, obtained from (8), exceeding the allowed range width four. Global
sign reversal therefore doubles the count without overlap. Of all `2^111`
disjoint boundary words, exactly `66902297797678953520198` satisfy this
subsystem for some centre. Every other word excludes **all** colourings of
both longer arms and the shortest arm's intervening vertices. This is an
infinite-domain restriction, not a finite census of tree solutions.

## 4. Entire support excluded when c=11 and b>=32

**Theorem.** For every integer `a>b>=32`, the support obtained from
`T(a,b,11)` by omitting `(1,1),(2,1)` has no balanced homometric colouring.
There is no restriction on how either longer arm is coloured.

Assume otherwise. The top 21 shell coefficients force (7) for `0<=r<=20`,
because `b-c>=21`. In the bottom 21 coefficients, the terms of degree `a,b`
still cannot appear, but degree `c=11` can. With `U=X+Y` the exact low equation is

```text
(1-z-z^3+z^13) U
  = z^2(2z-1)(s+Z) - s z^13 - z^2 R3       (mod z^23),          (9)
R3=z^11 Z*.
```

The congruence includes zero coefficients at degrees 0,1 and forces every
`u_n` through `n=22`. Equivalently the recurrence (8) acquires the additional
terms `-u_(n-13)-s*[n=13]`, with shortest-word entries outside depths 1..11
set to zero. For every one of the `2^11=2048` shortest words, with the centre
normalized to + by global sign reversal, a coefficient leaves `{-2,0,2}`
at or before 22. The following is the complete first-failure histogram:

```text
depth:  3   4   5   6   7   8   9  10 11 12 13 14 15 16 17 18 19 20 21 22
words:256 384 464 340 217 110 113 56 40 21 22  5  7  2  4  2  1  1  1  2
```

It sums to 2048. The checker reconstructs the coefficients and histogram
using only integer additions; an independent test performs formal division
of (9) and obtains the same complete histogram. A second test builds original
graph distances at `(39,32,11)`, imposes the top-shell antisymmetry, and checks
all 21 low equations against the graph counter, including the degree-11 term.
The failed coefficient is a sum of two signs, which cannot have that value.
This proves the contradiction for arbitrary `a,b` in the stated domain.
No enumeration of the two unbounded longer words, and no extrapolation from
finite tree cases, is used. Prefix/tip overlap is immaterial here: the forced
low equation is necessary, and no sufficiency from independent assignments
is asserted. This is an obstruction for this support, not for other holes.

### Uniform odd-shortest-arm theorem

For every odd `c>=3`, no colouring of this support is balanced and homometric
when `a>b>=2c+2+3^(c+2)`. Here is an analytic proof rather than an enumeration
of the `2^c` shortest words.

Let `G=1-z-z^3+z^(c+2)` and
`R=z^2(2z-1)(s+Z)-s z^(c+2)-z^2 R3`. Extend the formal quotient `U=R/G`
indefinitely. Its initial coefficients are the compulsory long-arm sums
from the paired end-shell equations, as in (9). We show they cannot all
stay in `{-2,0,2}`.

Suppose they did. After degree `c+3` the recurrence is homogeneous with
integer coefficients and memory `c+2`. A bounded sequence of these finite
states is eventually periodic. Consequently every pole of `U` is a root
of unity. The only possible unit-circle roots of `G` are 1 and the primitive
cube roots (the latter only if `c=2 mod 3`). To check this, write
`1+z^(c+2)=z+z^3` for `|z|=1`. Two chords of the unit circle with the same
midpoint either have the same endpoints or are both diameters. The first
case gives `z=1` or `z^3=1,z^(c+1)=1`. The diameter case requires
`z^2=-1,z^(c+2)=-1`, impossible for odd `c`. All the permitted roots are
simple: `G'(1)=c-2`, and at a primitive cube root it is `c+1-3z^2`.

It follows that `(1-z^3)U` is a polynomial. Its degree is at most four,
since `deg R=c+3` and `deg G=c+2`. Also `u0=u1=0`, so
`U=z^2(A+Bz+Cz^2)/(1-z^3)`, with `A=u2,B=u3,C=u4` in `{-2,0,2}`.
As `R(1)=0` and `G` has a simple zero there, `U` has no pole at 1, hence
`A+B+C=0`. Comparing the lowest and two highest coefficients in
`(1-z^3)R=G z^2(A+Bz+Cz^2)` now gives

```text
A=-s-w_c,      C=-2w_c,      B=-2w_(c-1)+w_c+s.
```

Their sum forces `w_(c-1)=-w_c`; the bound on `B=3w_c+s` forces `s=-w_c`
and `B=2w_c`. But the third low coefficient says
`B=s-w1-w_c-w_(c-1)=s-w1`, requiring `w1=-3w_c`, impossible for a sign.

Finally turn this infinite-sequence contradiction into the stated finite
length bound. There are at most `3^(c+2)` states of `c+2` consecutive
allowed sums. If the sums through degree `c+3+3^(c+2)` all remained allowed,
two states after the forcing ends would coincide and extend periodically
forever, contradicting the preceding argument. Thus a sum fails by that
degree. The top-shell cancellation supplies all the necessary low equations
whenever `b-c>=c+2+3^(c+2)`, which is exactly the displayed bound. This proof
quantifies over every shortest word, centre and both longer words. The
checker merely evaluates the proven bound (`1594347` at `c=11`); the sharper
fixed-11 certificate above replaces it by `32` in that case.

## Provenance, checks, and what remains

Recovered all six artifacts of immutable finish **29561**, run
`e4c753e724c941c587d4ffff0f61eed9`, and all three of finish **29746**, run
`4fd725b041014265a0d39f8f58ed5a68`; verified each SHA256 against its receipt.
The latter's `exact_lifting.py` hash begins `33f2fcf39c421ea2`. Its contribution
was rejected at event 30018 for a missing residue carry in its moment-witness
calculation. This work preserves those artifacts outside the tracked tree,
does not import that code, and does not rely on the disputed numerical claim.

The original full-shell formula and tip cancellation were reconstructed above.
The Phi_3 hypothesis was also checked: when `(a,b,c)=(2,1,2) mod 3`, the
coefficient of `z` in `E mod (z^2+z+1)` is
`3(s-sum chi_3(d) w_d)`; the other two arms cancel. The root in
`(682327803828,682327803829)/10^12` solves `z^3+z-1=0` by strict monotonicity.
For the assigned lengths the first 56 reversed terms cancel. With `rho` the
upper endpoint, a conservative bound on the remaining root expression is
`2rho^56/(1-rho)+3rho^100+6rho^100/(1-rho) < 3.2e-9`, since all lengths exceed
100. These inherited necessary filters are compatible with the new theorem;
neither substitutes for (3)'s exact divisibility.

Twelve focused tests pass: exhaustive independent BFS comparison of the full
completion equivalence on four fresh small unequal triples; unbalanced shell
identities; exact expansion (5); positive controls; malformed/altered
certificates and real CLI rejection; all seven-bit local patterns; every
15-bit transfer boundary; and a constructive 56-shell local witness with a
nonzero full residual; the short-arm obstruction checks just described;
and the odd-length bound's coefficient endpoints and input restrictions.
The local witness explicitly checks that local feasibility
is not being reported as homometry. No independent resident review is claimed.

Remaining: decide which surviving shortest words and middle words pass the
full completion remainder at every `t>=1`, or exclude them all. Other hole
supports in LIFTING_FRONTIER.md also remain. There is no bound on **every**
permitted pair, no new public installation, and no project-complete claim.
