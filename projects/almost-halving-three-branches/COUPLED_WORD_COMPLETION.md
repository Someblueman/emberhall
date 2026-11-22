# Coupling repeated words to both endpoints

Mallow, 22 November 2026. **The requested target construction or unrestricted
obstruction was not obtained. The project milestone remains open.** This
attempt gives an exact, family-wide certificate test and a global contradiction
for one natural middle-word template. It does not decide arbitrary words on
`T(227+7560t,67+7560t,11+7560t)`. Everything here fixes the holes `(1,1),(2,1)`;
other supports are untouched. [External priority remains provisional](PRIORITY_REFRESH.md).

## What was attempted

I inspected Hawthorn's three files at `c7cd1c1` and immutable finish 30671
(run `a37add0f91ee4cc5a70eae6d8d28d439`), including the exact integer joins.
Their node limit is not a negative. Rather than enlarging it, this attempt
couples complete endpoint words through an identity in two independent
variables. The middle words may repeat; the endpoint words remain independent
unknown signs. A contradiction must involve that entire identity.

The new checker accepts arms made of literal segments and repeated segments.
All repeated blocks have one positive length `p`, and every block is repeated
`n` times. Multiple, separated blocks on an arm are supported. Each arm starts
at original depth 2, 2, or 1 respectively. The centre is a separate literal
sign. Block letters are signs, never averaged or treated as real variables.
The base lengths are strictly decreasing and the growth rates nonincreasing,
so every nonnegative repetition count remains a valid ordered triple.

## Exact coupling theorem

Let `v` stand for `z^(pn)`, and let `D=1-z^p`. Before a segment, let `d` be
its first depth when `n=0`, and `r` the number of earlier repeated segments.
A literal word with polynomial `L(z)` contributes `D z^d v^r L(z)` to the
numerator `N_i`. A repeated block `B(z)` contributes
`z^d v^r (1-v) B(z)`. Literal letters advance `d`; a repeated segment advances
`r`. Thus the actual arm polynomial is exactly `N_i(z,z^(pn))/D`.
If arm i has base length `a_i` and `r_i` repeated blocks, its endpoint monomial
is `z^a_i v^r_i`. A star inverts both independent variables.

With `K=z+z^-1-z^-2`, form the following **integer** polynomial:

```text
F = s D (2z-1-sum_i z^a_i v^r_i)
  + (K-z^a_2 v^r_2-z^a_3 v^r_3) N_1
  + (K-z^a_1 v^r_1-z^a_3 v^r_3) N_2
  + (2z-1-z^a_1 v^r_1-z^a_2 v^r_2) N_3
  + sum_i z^(a_i+p) v^r_i N_i* .
```

The positive sign on the last line is essential:
`D(z^-1)=-z^-p D(z)`. Substitution gives precisely `D E_n`, where `E_n` is
the accepted full shell polynomial, with every original-distance coefficient,
constant term, reversed arm and hole correction retained. Its identity is
`E_n=2(1-z)(D_plus-D_minus)/z-2S`. Therefore:

**The words give balanced homometric sets for every n>=0 if and only if F=0
as a polynomial in the independent variables z,v.** The forward implication
also holds if the words work on any unbounded subsequence of n.

For necessity, let W be the difference between the largest and smallest z
exponents in the compiled polynomial rows. When `pn>W`, terms with distinct
v exponents occupy disjoint intervals after substitution. Consequently
`F(z,z^(pn))=0` forces every coefficient of F to vanish. Sufficiency follows
by substitution and cancellation of the nonzero polynomial D. This also
proves a finite check principle: one correctly counted expansion at any
`n>W/p` certifies the entire fixed template. The program reports a sufficient
`separating_repeat_count`, but checks the smaller symbolic identity directly.
A few small successful expansions without this bound would not be a proof.

Vanishing at z=1 enforces balance through E, not an extra assumed condition.
Exactly two original vertices are omitted; equal parts therefore have the
required half-minus-one size. No edge is contracted. This theorem concerns
specified repeated words; it does not prove that every solution has this form.

## A global failed template on the target family

Consider every possible choice of these signs, with one common repetition
count n and independently chosen words at every position:

| Arm | Prefix length | Block length | Suffix length | Original length |
|---|---:|---:|---:|---|
| 1 | 173 | 24 | 173 | 347+24n |
| 2 | 93 | 24 | 93 | 187+24n |
| 3 | 65 | 24 | 66 | 131+24n |

The target lengths occur at `n=315t-5`, for every t>=1. Compiling F gives
736 sign variables and 933 nonzero coefficient equations. Write each sign
as `1-2b`. For a row with coefficients A, its necessary binary equation is
`sum (A_i mod 2)b_i = (sum A_i)/2 mod 2`; all row sums are even here.
Exact elimination finds **364 rows whose XOR is 0=1**. The checker retains
their indices and independently XORs the original rows to verify the
contradiction. No row relation was truncated, no affine feasibility was
called integer feasibility, and no search limit is involved.

It follows that no choice of these fixed prefixes, blocks and suffixes works
for every target t. This includes choices that might only claim the
subsequence `n=315t-5`: necessity above still applies. It does **not** say an
individual target has no word, nor that another block length, moving endpoint
word, multiple blocks, or arbitrary colouring fails. This restricted negative
is not the assignment's acceptance result.

A second exploratory shape inserted two independent 160-letter blocks on
each arm of the actual base target, at folded depths 1024 from the two ends.
The compiled system has 23,944 signs and 16,867 integer rows. Its global
binary relaxation is consistent with 7,410 free bits. This computation only
checks a necessary relaxation; it is not a saved positive word. A single
320-letter middle block with base lengths `(427,267,211)` likewise has a
consistent binary relaxation, with 290 free bits after fixing the centre.
That template contains the target subsequence `t=1+8u` at repetitions
`n=23+189u`. Neither finite template received a complete integer decision.
These probes do not justify extrapolating the 24-letter contradiction to
arbitrary periods or multiple blocks.

## Reproduce and independent controls

From the complete public [Emberhall repository](https://github.com/Someblueman/emberhall),
Python 3.10+ and its standard library suffice after integration:

```sh
python3 projects/almost-halving-three-branches/coupled_word_completion.py --control --audit-repeat 7 --write /tmp/coupled-positive.json
python3 projects/almost-halving-three-branches/coupled_word_completion.py --verify /tmp/coupled-positive.json --audit-repeat 23
python3 projects/almost-halving-three-branches/coupled_word_completion.py --target-template --write /tmp/coupled-negative.json
python3 projects/almost-halving-three-branches/coupled_word_completion.py --verify /tmp/coupled-negative.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_coupled_word_completion.py
```

The positive control is the **previously known** family `(5+4n,4,2)` from
[WORD_REALIZABILITY.md](WORD_REALIZABILITY.md): centre +, first arm
`(--++)^(n+1)`, second arm `---`, third arm `++`. It is not a new target
construction. At n=7 the real direct-distance run gives `(33,4,2)`, size 19,
target 19 and 171 unordered pairs on each side. At n=23 it gives `(97,4,2)`,
size 51 and 1275 pairs. The counter enumerates pairs of original vertices
using their arm/depth distances; it does not use F to count distances.

Six tests compare every substituted coefficient with independently built
breadth-first tree distances on arbitrary signs, including two separated
blocks and n=0,1,3. They count the positive family at four parameters, reject
a template whose base word passes but whose next expansion fails, replay the
364-row contradiction, and reject a size-preserving sign swap and changed certificate rows
through the actual command line. No existing proof, default, Gallery or runtime
file changes. The large audit is explicitly bounded before word expansion.

**BLOCKED:** the target still needs a full integer solution connecting both
endpoints, or an obstruction covering every permitted colouring and support.
A global contradiction for the single-block template does not supply either.
The symbolic checker can certify a proposed multi-block construction, but
neither its existence nor completeness of that construction class is proved.
