# Independent reconstruction of the ten-chore path result

Aster, 19 November 2026. This report and `reconstruction.py` are the two
files owned by task `ten-chores-reconstruction`. I wrote the original exploratory
research note, but not Rook's project certificate or proof. The reconstruction
below was implemented and run before opening that certificate's source. It
imports no project code. Independence here means a separate implementation and
mathematical reconstruction, not a second human or a claim of independent
discovery of the research idea.

## Claim and source reading

Three people have arbitrary nonnegative monotone costs on subsets of at most
ten chores, with cost zero for the empty set. There is a complete assignment
with adjacent chores assigned to different people such that, for each ordered
pair of people, deleting at most one chore from the first person's bundle
makes its cost no larger than the second bundle's cost, both measured by the
first person. No additivity, positivity, genericity or identical-cost assumption
is needed. This is an existence result, not a fast value-oracle allocation
algorithm, and not the unrestricted-length path conjecture.
An arbitrary real-valued monotone cost can be normalized by subtracting its
empty-set value; this changes neither comparison, so the same conclusion holds.

I opened the following primary sources in this run:

* [Equbal et al., *Fair Allocation under Conflict Constraints*, v1](https://arxiv.org/html/2605.09930v1),
  definitions in Section 2 and the scope of the path result. Chores use
  nonincreasing utility, so cost is its negative. Completeness and maximality
  are different definitions; every complete allocation is maximal. Conversely,
  on a path an unassigned vertex has at most two neighbours, leaving one of
  three labels available, so a maximal allocation is complete.
* [Dupré la Tour, *Balanced Fair Division for Three Agents under General
  Valuations and Laminar Constraints*, v1](https://arxiv.org/html/2608.09437v1),
  Section 3, Lemmas 1–2 and Theorem 5. The transfer theorem requires a finite
  connected simply connected complex of partitions, cyclic label symmetry and
  pairwise loss/gain of at most one item per bundle within each simplex. It
  supplies one deletion on each side for general utilities. For utilities
  `v_i=-c_i`, retaining the other bundle only makes the cost inequality easier;
  hence its conclusion gives precisely chore EF1. The path is not a laminar
  constraint and no laminar corollary is invoked.
* [Igarashi, Manurangsi and Yoneda, *Dividing Conflicting Items Fairly*,
  v1](https://arxiv.org/html/2506.14149v1), Theorem 11 and Section 5.
  I transcribed the seven-item graph and its identical monotone function as a
  discriminating negative control, with vertices relabelled from 1–7 to 0–6.
* [Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf),
  Propositions 1A.2, 1.26 and 1.33 (printed pages 84, 50, 61): the graph
  presentation relative to a tree, triangle attaching relations, and lifting
  a map from a simply connected complex to the real-line cover of a circle.

## A direct reconstruction of the monotone transfer

Here is my specialization of the transfer argument, including its logical
bridge rather than treating the cited theorem as a solver.

For bundle `S`, put `d_i(S)=min_{T subset S, |S\T|<=1} c_i(T)`. For a partition
`P`, let `D_i(P)` be the labels `r` with
`d_i(P_r) <= min_s c_i(P_s)`. A distinct representative for each of the three
sets assigns all three bundles and gives every required EF1 comparison.

For a simplex `sigma`, intersect these sets over its vertices. The intersection
for each person is nonempty: choose `(P*,r*)` minimizing `c_i(P_r)` over every
vertex and label in the simplex. For any vertex `Q`, the intersection
`C=P*_{r*} intersect Q_{r*}` deletes at most one item from `Q_{r*}`. Monotonicity
and minimality give

```
d_i(Q_{r*}) <= c_i(C) <= c_i(P*_{r*}) <= min_s c_i(Q_s).
```

Thus `r*` is acceptable throughout the simplex. These intersection sets shrink
on larger simplices and rotate when the labels rotate; the agents do not rotate.

Suppose no vertex has a distinct representative system. For each simplex take
the Minkowski average of the three probability simplices on its acceptable-label
sets. This convex set excludes `b=(1/3,1/3,1/3)`: membership would give a
doubly stochastic fractional assignment supported on those sets, hence Hall's
inequalities, hence distinct representatives at every constituent vertex.

At the subdivision vertex corresponding to `sigma`, average the three uniform
probability distributions on its acceptable sets. Extend affinely on chains of
simplices. Along a chain all these points lie in the convex set for its smallest
simplex, so the resulting continuous map avoids `b`. Uniform distributions make
the map equivariant. Radial projection gives an equivariant map to the circle
in the plane of coordinate sum zero, with label rotation acting by 120 degrees.

Such a map cannot exist for a connected simply connected finite complex.
Lift it to a continuous real-valued function `F`, where the circle is `R/Z`.
For a generator `tau` of label rotation, equivariance says
`F(tau x)-F(x)=1/3+k(x)` (or the negative angle if orientation is reversed).
The integer `k(x)` is constant by connectedness. Applying this identity three
times gives `0=1+3k`, impossible. The lift exists by simple connectivity and
local path connectivity of a finite complex. This contradiction produces the
distinct representatives and the fair allocation. No freeness of the domain
action is presumed, and no numerical valuation sample substitutes for this
universal argument.

## Finite topology and independently generated relations

Vertices are **all** labelled proper 3-colourings of the path, including unused
colours. The script enumerates pairs of disjoint independent sets and checks
that their complement is independent. Edges are exactly pairs of partitions
whose corresponding set differences each have size at most one. A second,
different enumeration chooses at most one departing item per colour and an
injective list of different target colours; its edge set must agree exactly.
This allows simultaneous exchanges and three-cycles, not just moving a single
item globally. Triangles are all triples of mutually adjacent vertices.

Use the two-dimensional complex containing these vertices, edges and filled
triangles. It is finite and 1-close by definition. The script checks cyclic
invariance of the entire vertex, edge and triangle sets. That is enough for
transfer; higher-dimensional cliques are unnecessary. Equivalently one can use
the full flag complex, whose fundamental group is unchanged by its higher cells.

A depth-first spanning tree certifies connectedness. Each other oriented edge
is a generator. For `a<b<c` the triangle boundary is the ordered signed word
`e_ab e_bc e_ac^-1`, with tree edges set to identity. In the producer, each
successful elimination rewrites every affected word, retaining order. A
separate replay starts from the original boundaries and follows signed
substitution chains. It requires the eliminated generator to occur exactly
once in the current reduced relation, requires a live replacement, and checks
that the proposed substitution makes that word freely trivial. It trusts none
of the producer's rewritten words or residual counts.

Only adjacent inverse cancellation and cyclic conjugation are allowed.
`x y x^-1 y^-1` is retained, and `x x=1` cannot eliminate `x`. There is no
abelianization, rank test or external group solver. Each successful substitution
is a consequence of an actual filled triangle and earlier consequences. If all
generators disappear, all graph loops are trivial in the fundamental group of
the complex, which establishes simple connectivity.

## Recorded independent run

Command: `python3 projects/fair-ten-chores/reconstruction.py`

| Items | Vertices | Edges | Triangles | Verified eliminations |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | 0 | 0 |
| 1 | 3 | 3 | 1 | 1 |
| 2 | 6 | 15 | 20 | 10 |
| 3 | 12 | 42 | 68 | 31 |
| 4 | 24 | 105 | 150 | 82 |
| 5 | 48 | 273 | 456 | 226 |
| 6 | 96 | 666 | 1,200 | 571 |
| 7 | 192 | 1,614 | 3,234 | 1,423 |
| 8 | 384 | 3,816 | 8,316 | 3,433 |
| 9 | 768 | 8,928 | 21,228 | 8,161 |
| 10 | 1,536 | 20,616 | 53,004 | 19,081 |

Every row leaves zero surviving generators. Shorter paths are checked directly,
not inferred from a possibly invalid topological restriction. At zero chores
the single vertex is a point. All-zero costs pass for every enumerated vertex,
including empty bundles; ties use weak inequalities. The proof covers arbitrary
cost tables, not just these boundary checks.

Removing an assignment, changing the edge list, flipping one boundary letter,
and reversing a nontrivial signed substitution are all rejected. Reversing an
entire boundary with all signs inverted and order reversed is mathematically
equivalent, although this certificate format fixes one canonical orientation.
That harmless mathematical change must not be called a counterexample.

The published graph gives 42 vertices, 114 edges and 78 triangles. My tree and
reduction order leave 20 generators and fail the complete-certificate check.
Direct enumeration gives zero chore-EF1 assignments under the published cost,
whose monotonicity is also checked on all 128 subsets. Residual generator counts
can differ with the tree and heuristic; failure to eliminate does **not** prove
that the group is nontrivial. The independent EF1 failure is the distinguishing
mathematical control.

## Author comparison and assessment

The reconstruction above first ran successfully in 1.364 seconds on this host.
After that run, I inspected the stopped author contribution
`18a10d1bf3d5cf3f7027d267c19d928d3469ee02` through the fixed source reader.
The checker and proof hashes matched the immutable task finish at sequence
21000:

```
check.py  087aa97fa7e0b9b5256de03599dc17c140e3fbb22d3ad0e0b6501a647a37fc98
proof.md  852dd9d6d36bb95aaf8c1c981adbc93db020d11698ec9ae08c67bc523cb5fb29
```

I ran the exact checker to write its JSON certificate, then read that JSON with
`reconstruction.py --author-certificate`. Every assignment and edge agreed;
the independent verifier replayed all 19,081 signed deductions from the author's
different breadth-first tree. The author uses an even narrower valid rule:
each triangle has exactly one edge not yet proved trivial. No identifications
between two live generators are needed in that certificate.

Reproduce the cross-check after both contributions are integrated:

```sh
python3 projects/fair-ten-chores/check.py --write-certificate /tmp/ten-chores.json
python3 projects/fair-ten-chores/reconstruction.py --author-certificate /tmp/ten-chores.json
```

The combined reconstruction and cross-check took 1.512 seconds on this host.
The independent reader also refused the author's JSON with a missing
assignment, a changed edge list, and one reversed triangle edge. The author's
own negative control leaves 42 unproved generators, compared with my 20 after
additional legal reductions and a different tree. Both correctly refuse it;
this is an algorithm-dependent remainder, not a contradictory group invariant.

I checked the author's normalization, the common conflict constraint under
bundle permutation, every hypothesis of Theorem 5, and its dummy-item reduction.
The reduction extends costs by `c'_i(S)=c_i(S intersect M)`. Restricting the
extended allocation and each deletion witness to `M` preserves the inequalities,
feasibility and completeness, including `M` empty. This agrees with my direct
checks of all smaller complexes.

Targeted searches on 19 November for the heterogeneous monotone path problem,
the ten-item bound and citations of the transfer preprint found no prior
resolution. The strong-colourability work found concerns common preferences;
connected-bundle path results impose a different constraint. This is a bounded
priority screen, not proof that no earlier result exists.

**Finding:** the certificate settles the stated bounded theorem, subject to the
cited mathematical foundations. Another mind can reproduce and inspect the
finite proof; it is a mathematical result in its promised form, not a visual
demonstration. No discrepancy requiring a mathematical repair was found. Source
integration, publication and the owner's milestone decision remain separate.
