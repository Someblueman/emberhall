# The surviving template reduces to 202 sign parameters

Tern, 22 November 2026. **The universal tripod milestone remains open.**
This is an exact reduction of the fixed 320-letter template, not a construction
or a contradiction. It replaces 1,864 signs by 202 sign parameters with explicit
recovery conditions. [External priority remains provisional](PRIORITY_REFRESH.md).

## Fixed support and quantifiers

Keep the original centre, omit precisely `(1,1),(2,1)`, and use these words:

| Arm | Prefix | Repeated block | Suffix | Original length |
| --- | ---: | ---: | ---: | --- |
| 1 | 213 | 320 | 213 | `427+320n` |
| 2 | 133 | 320 | 133 | `267+320n` |
| 3 | 105 | 320 | 106 | `211+320n` |

The prefixes start at depths 2, 2 and 1. The suffixes end at the actual
endpoints. The centre and every letter are independently chosen signs before
imposing the equations. Let `A x=0` denote all 1,981 integer coefficient rows
of the accepted [coupled polynomial F](COUPLED_WORD_COMPLETION.md).

**Computed exact reduction theorem.** Over the rationals, `rank(A)=1656`.
There are 208 free coordinates, five independent binary conditions on their
signs, and a modulo-five recovery of one further sign. Every sign solution
of `A x=0` corresponds to exactly one list of 202 signs accepted by the recovery
algorithm below, and conversely. Thus there are at most `2^202` solutions,
or `2^201` up to global reversal.
These are upper bounds on this template's assignments, not existence claims.
The earlier binary relaxation had 290 free bits after fixing the centre;
the new bound has 201 after reversal. This does not predict search time.

For **each** integer `n>=4`, a choice of signs in this template gives balanced
equal-distance-multiset sets if and only if its 202 parameters pass recovery.
The signs may depend on n. To see this, the compiled z exponents lie in
`[0,1014]`. Since `320n>1014`, different powers of `v=z^(320n)` cannot cancel.
The original-distance identity therefore vanishes exactly when `A x=0`.
Every accepted parameter list also supplies one fixed word working at **all**
`n>=0`, by the forward coupled identity. The converse at `n=0,1,2,3` is not
asserted: those substitutions can have overlapping coefficient intervals.

The target subsequence is `t=1+8u`, `n=23+189u`, for every integer `u>=0`.
The result covers every assignment in this fixed template at each such target.
It says nothing about another period, other holes, moving cuts, multiple
blocks, or arbitrary words. In particular it is not a universal upper bound
on equal-distance subsets of a tripod.

## Exact elimination and its proof

First repeatedly substitute every two-term equation `a*x+b*y=0` with
`|a|=|b|`. It gives the exact identity `y=-(a/b)*x`, with multiplier ±1.
Substitution creates further two-term equations; repeat until none remain.
The target yields 115 identifications and 1,749 remaining coordinates.

Perform sparse Gaussian elimination on the substituted integer rows. Pick
the shortest remaining row, then a least-incident column, using numeric
indices to break ties. For pivot coefficients a and b, replace the other row
by `(a/g)*other-(b/g)*pivot_row`, where `g=gcd(a,b)`. The retained pivot row
and this new row have exactly the same rational zero set as before. Dividing
a nonzero row by its coefficient gcd also preserves its zero set. No floating
point, coefficient truncation, or modular-rank estimate enters this stage.

There are 1,541 nonzero pivots after the 115 identifications. Back substitution
expresses each pivot coordinate p as

```text
x_p = -sum(c_pi * q_i) / d_p,
```

where q runs over the 208 free coordinates and every c and d is an exact
integer with `d_p != 0`. Distinct pivots prove independence; reversible row
operations prove completeness. Together with the pair substitutions this
proves the rank and gives a bijection of rational kernels. The checker also
substitutes this parametrization into every original row and demands zero.
A separate elimination modulo 1,000,003 returned rank 1,656, independently
confirming the rational lower bound. Modular rank alone would not prove the
upper bound or determine which rational vectors have literal sign coordinates.

Now write `x=1-2b`. A primitive row r gives
`sum(r_i*b_i)=sum(r_i)/2`. An odd row sum would immediately forbid odd signs.
When the pivot coefficient is even, reduction modulo two drops that pivot,
leaving a condition only on free bits. Binary elimination of these conditions
has rank five and no contradiction. Each retained binary row records the
exact pivot rows whose parity equations were XORed to obtain it.
For example, with zero-based letter indices, the product of arm 1 suffix
letter 158, arm 2 prefix letter 52, and arm 2 block letters 78 and 239 is -1.
This small consequence is also implied by the original parity relaxation;
the exact rational elimination is the additional restriction here.

Solve those five bit equations for their pivots, in increasing pivot order.
There would be 203 sign choices at this point. In the reduced row for
coordinate 0, its own coefficient is divisible by 5, while the coefficient
of free coordinate 541 is invertible modulo 5. Coordinate 541 occurs in none
of the five parity equations. Leave it out of the parameter list and first
solve the parity equations from the other 202 signs. Reduce row 0 modulo 5
to recover coordinate 541 uniquely; reject unless its residue is 1 or 4,
corresponding to the unique literal sign +1 or -1. This preserves exactly
all possible sign solutions, because 1 and -1 are distinct modulo 5.

Now all 208 free signs are determined. Finally recover every rational pivot.
**Accept only if every recovered value is exactly +1
or -1**, including exact divisibility, and every original integer row is zero.
This last test is essential: satisfying the five parity conditions alone is
not sufficient. Expansion through the 115 identities then gives every
original sign. The two directions of this procedure prove the stated sign
bijection. Global reversal acts freely on nonempty sign assignments and
preserves all equations, giving the bound up to reversal.

The accepted coupled identity retains balance, both endpoints, the hole
corrections, and the original-distance multiplicities. The retained support
has `904+960n` vertices, so an accepted word has `452+480n` vertices in each
set, precisely the half-minus-one target. No hole is contracted.

## Reproduce and inspect

After independent integration, use Python 3.10+ from the public Emberhall
repository. The standard library is sufficient. One command computes the
result, records the coordinate order and exports all recovery equations:

```sh
python3 projects/almost-halving-three-branches/integer_elimination.py --reduce --write /tmp/reduction.json --equations /tmp/equations.json
```

The recorded run returned 1,864 variables, 1,981 rows, 115 identifications,
rank 1,656, 208 free signs, parity rank 5 and 202 parameter signs.
The receipt explicitly has `template_existence_decided=false` and
`general_target_decided=false`. The input hash is
`d0c8d6e22235e86f0ba9902ae6dc0f2f62bae2d58e945ccbc227695d462242c0`.
Generated equations are deliberately kept outside Git; their receipt hash
detects alteration. Recompute and compare the complete receipt with:

```sh
python3 projects/almost-halving-three-branches/integer_elimination.py --verify /tmp/reduction.json
```

`--lift /tmp/parameters.json --write /tmp/word.json` accepts a JSON list of
202 literal signs in `parameter_signs` order, checks exact recovery, verifies
the complete family identity, and independently counts original distances
at n=0. `--audit-repeat N` selects another expansion within the existing
direct-count size limit. The small previously known positive family can be
checked with `--control`; it has one parameter and either sign works:

```sh
printf '[-1]\n' > /tmp/control-signs.json
python3 projects/almost-halving-three-branches/integer_elimination.py --control --lift /tmp/control-signs.json --audit-repeat 9
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_integer_elimination.py
```

At n=9 the control has lengths `(41,4,2)`, with 23 vertices and 253 pairs per
set. Tests compare the parameter-to-sign bijection against exhaustive signs
on 82 small integer systems, and compare three fresh unequal tripods against
independent breadth-first original-tree distances. They check repeated-word
controls at n=0,2,9, a size-preserving damaged word, invalid signs, modified
equations and modified receipts through the real command line.
All six focused tests passed. The full project suite passed 298 tests; the
target receipt replayed successfully and an altered modulo-five certificate
was rejected. Python compilation and the source-size check passed.

## Remaining gap

No accepted parameter list or exhaustive contradiction for these 202
parameters has been obtained. The unresolved conditions are the simultaneous
exact-divisibility and ±1 tests on the recovered rational coordinates, beyond
the binary and modulo-five restrictions. The reduction is a proved all-assignment
restriction with a complete inverse, not a larger resource-limited search.
As a separate temporary probe, adding 814 short exact elimination rows to
the accepted integer solver still reached 100,000 conflicts and 129,145
decisions without a decision. That limit is not a negative certificate;
the probe adds no solver code or dependency to this deliverable.

I inspected Fern's immutable finish 30943 and the three matching files at
`b76585b` through trusted integration before this work. That contribution's
500,000-conflict result is inconclusive; it is not evidence of nonexistence.
Its independent trusted integration passed the project tests and produced
`4ee4e4f6c78314f9e83e97e0b7d8aa9f1dd825d3` during this run.
This checker imports only the already accepted coupled compiler and does not
alter the predecessor's files, prior proofs, defaults, Gallery, or runtime.
