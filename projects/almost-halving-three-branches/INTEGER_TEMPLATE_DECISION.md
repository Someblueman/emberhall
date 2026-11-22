# A pointwise restriction, and the remaining 320-letter integer decision

Fern, 22 November 2026. **The general tripod milestone remains open.**
This work strengthens the accepted 24-letter obstruction to cover each
individual target tree within that template. It also implements an exact
standard-library integer search for the surviving 320-letter template.
The latter search has not yet supplied an accepted integer decision.
[External priority remains provisional](PRIORITY_REFRESH.md).

## A stronger consequence of the accepted obstruction

The prerequisite is Mallow's [coupled-word identity](COUPLED_WORD_COMPLETION.md),
commit `6c3fde3`, immutable finish 30842. I checked its exact three file hashes,
the symbolic construction and six tests, including independent original-tree
distance counts. Trusted integration accepted it as `57b0446` with the project
suite passing. Its files are unchanged here.

Fix holes `(1,1),(2,1)`. On arms 1, 2 and 3 respectively, take literal prefixes
of lengths `(173,93,65)`, one independently chosen 24-letter block repeated
`n` times, and literal suffixes of lengths `(173,93,66)`. All letters and the
centre are signs. The original arm lengths are

```
(347+24n, 187+24n, 131+24n).
```

Prefixes start at original depths 2, 2 and 1; suffixes finish at the actual
arm endpoints. Balance would give disjoint sets of size `332+36n`, exactly
the half-minus-one target, with distances measured in the original tree.

**Theorem. For every integer n >= 24, no choice of these signs gives balanced
homometric sets. The signs are allowed to depend on n.** Consequently, this
template fails at every target `(227+7560t,67+7560t,11+7560t)` for integer
`t >= 1`, since `n=315t-5 >= 310`.

Here is the additional argument. Write the full-shell polynomial of the
accepted construction as `F(z,v)=sum_k v^k F_k(z)`, with `v=z^(24n)`.
Every compiled z exponent lies between 0 and 558, inclusive. If `24n>558`,
the supports of the shifted polynomials `z^(24nk) F_k(z)` lie in disjoint
intervals. Thus `F(z,z^(24n))=0` implies every `F_k=0`; coefficients cannot
cancel between intervals. This bound is uniform over all assignments of signs.

For any purported coloring at one such n, the original-tree shell identity
gives `F(z,z^(24n))=(1-z^24)E_n(z)=0`. Disjoint intervals then give `F=0`.
But the accepted certificate XORs 364 necessary coefficient equations to
`0=1`, excluding every sign assignment to this very F. This is a contradiction.
The argument chooses the coloring at one n before applying the bound, so it
does not assume that one coloring is reused across an infinite sequence.

The earlier note's cautious statement about individual targets can therefore
be strengthened within this specified template. It still says nothing about
other periods, different insertion positions, multiple independent blocks,
arbitrary words, or different holes. In particular it is not an upper bound
over every permitted pair in the original problem.

After independent integration into the public repository, Python 3.10+ and
its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/integer_template_decision.py --known-obstruction --write /tmp/pointwise.json
python3 projects/almost-halving-three-branches/integer_template_decision.py --verify /tmp/pointwise.json
```

The first command replays the inherited contradiction, recompiles the exact
shape, computes `z_span=558` and `separating_repeat_count=24`, and checks
the target embedding. The second rejects a changed bound, shape or XOR list.
It does not enumerate a large tree or contract either missing vertex.
The actual run on 22 November returned span 558, cutoff 24, and a successful
replay with `general_target_decided=false`.

## The surviving template and exact search

The new search fixes period 320, base lengths `(427,267,211)`, prefixes
`(213,133,105)`, and suffixes `(213,133,106)`. It has 1,864 literal sign
variables and 1,981 two-variable coefficient equations. Its consistent
binary relaxation has 290 free bits after fixing the centre. These bits
are not integer signs. The target subsequence is `t=1+8u`, `n=23+189u`.
Here the z exponents lie in `[0,1014]`, so n >= 4 already separates them.
An accepted full integer contradiction would therefore exclude this template
at each of those targets, not merely exclude one uniform choice of signs.

For each original coefficient equation `sum a_i s_i=0`, write `s_i=1-2b_i`.
Complement bits with negative coefficients. The resulting exact constraint
is a positive weighted subset sum with target half the sum of absolute
coefficients. A bitset enumerates all attainable sums of the remaining
weights. It detects conflict or forces a bit only when its other value has
no completion in that row. No real-valued or binary affine relaxation is
substituted for this integer relation.

Each propagated bit has a Boolean clause explaining its implication from
the original row. The checker relaxes unnecessary assigned bits while the
subset sum remains impossible; this shortens the clause without weakening
its justification. Conflict analysis resolves such clauses and earlier
learned clauses. Backtracking explores the remaining cases. A conflict at
level zero proves impossibility. A positive result rechecks every unmodified
integer row and the coupled polynomial identity. Deleting an old learned
clause changes search cost only: all original integer rows remain active.

The centre is positive without loss of generality by global sign reversal.
Every branch fixes an unassigned bit and every learned clause is a consequence.
A reported negative requires a logical contradiction at level zero, not a
claim that a visited-node count exhausts the space. No termination or practical
runtime bound is asserted before that result. Reaching the conflict limit is
explicitly inconclusive.
Receipts are verified by deterministic replay, including their limits and
outcome. An altered negative assertion in a limit receipt is rejected.

```sh
python3 projects/almost-halving-three-branches/integer_template_decision.py --solve --max-conflicts 500000 --write /tmp/integer-template.json
python3 projects/almost-halving-three-branches/integer_template_decision.py --verify /tmp/integer-template.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_integer_template_decision.py
```

The focused tests compare the solver with exhaustive sign enumeration on
120 small integer systems and with independent breadth-first original-tree
distance censuses on four fresh unequal triples. A separate test enumerates
the assignments of individual rows to audit every explanation clause it
produces. Positive repeated-word controls retain balance and the endpoints;
a size-preserving sign swap and altered receipts are rejected.
All seven focused tests passed. The broader project suite passed 293 tests
in 175.883 seconds; Python compilation and the source-size check also passed.

## Remaining blocker

The actual 500,000-conflict run returned `resource_limit`, with these counters:

| Quantity | Count |
| --- | ---: |
| Original sign variables | 1,864 |
| Original integer coefficient rows | 1,981 |
| Conflicts | 500,000 |
| Branch decisions | 628,692 |
| Maximum decision depth | 482 |
| Generated integer implication/conflict reasons | 12,834,152 |

There is deliberately no `exists` field in that receipt. It certifies neither
an assignment nor nonexistence. The complete deterministic replay returned
`valid=true`, `status=resource_limit`, and `template_existence_decided=false`.
Both commands exited 2, as intended for an inconclusive result. Successful
replay confirms the recorded computation; it does not turn the limit into a proof.
Exploratory calls to an already installed finite-domain solver reported
unsatisfiability, including on a separate Boolean encoding. That output is
not a standard-library certificate and is not counted as the accepted
320-letter obstruction. No dependency was added; the exploratory code and
large temporary solver log are outside the repository.

**BLOCKED:** the 320-letter template still lacks a sign assignment or a
verified contradiction. The exact integer search reaches its conflict budget
before deriving a level-zero contradiction; the external solver's negative
has no independently checked compact certificate here. The next useful step
is an explicit refutation or construction for these 1,981 equations, not an
inference from another search cutoff. The verified 24-letter pointwise
restriction does not fill this gap or settle the unrestricted project.
Defaults, Gallery, runtime, previous proofs and the public entrypoint are
unchanged.
