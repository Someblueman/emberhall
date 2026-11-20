# Reconstructing the published tripod cases

Mica, 20 November 2026. This is an admission document, **not a proof of the
project's half-minus-one target**. The formulas below are proved for arbitrary
lengths within their stated domains. Tests check their implementation only.

## Sources and priority

The principal source is Axenovich–Özkahya,
[On homometric sets in graphs](https://ajc.maths.uq.edu.au/pdf/55/ajc_v55_p175.pdf),
Australasian Journal of Combinatorics 55 (2013), 175–187: Construction 13
(p. 179), Constructions 15–16 (pp. 181–182), and Theorem 8 (p. 177).
The [December 2012 author manuscript](https://web.cs.hacettepe.edu.tr/~ozkahya/pub/homsets.pdf)
has the same extracted block endpoint. The older
[arXiv version](https://arxiv.org/html/1203.1158) numbers these constructions
9, 11, 12 and labels the block arm differently. Do not mix those labels.
The journal states a roughly five-twelfths bound for three legs and special
half-size cases, with a general warning that floors/ceilings are sometimes omitted.

Priority refresh on 20 November 2026:

* Fulek–Mitrović, [Homometric sets in trees](https://arxiv.org/html/1302.1386v2),
  Sections 2–4, improves general-tree and haircomb lower bounds. Its limitation
  concerns a restricted construction, not all homometric pairs.
* Anu–Lakshmanan, [Homometric Number of a Graph and Some Related Concepts](https://doi.org/10.1007/978-3-319-64419-6_4),
  checked in the [author-uploaded text](https://www.researchgate.net/publication/319138539_Homometric_Number_of_a_Graph_and_Some_Related_Concepts),
  treats products, powers, regular graphs and related parameters.
* Lakshmanan–Menon–Anu, [Homometric Number of Graphs](https://ijritcc.org/index.php/ijritcc/article/download/1148/1148),
  concerns graph operations and weak homometry; weak distance **sets** do not
  establish equality of multiplicities.
* The relevant [Oberwolfach report](https://publications.mfo.de/bitstream/handle/mfo/3349/OWR_2013_18.pdf?isAllowed=y&sequence=1),
  printed p. 1119, poses a general-graph asymptotic problem, not this tripod bound.

None of these opened results resolves the proposed target. Searches for
“homometric sets” with trees, spiders, three legs and later dates found no
resolution. This is **provisional priority**, not proof of novelty. The cited
[twins survey](https://wwwalt.math.kit.edu/iag6/~axenovich/media/twins-survey1.pdf)
timed out (its alternate URL redirects to the author's homepage).
Anu's thesis, *A study on two graph parameters: double Roman domination
number and homometric number*, is now located in the
[university reader](https://mgutheses.in/page/authors_view.php?q=T+3952&word=):
chapter 6 is named “Homometric number”, but its links returned the same
contents page, not readable chapter text. The
[Shodhganga record](https://shodhganga.inflibnet.ac.in/handle/10603/370098)
was inaccessible. That chapter remains unchecked. No theorem may be
advertised as new until those gaps are addressed. Publication dates above are
from the papers, not the search engine's crawl dates.

## Conventions

Let the centre be `o=(0,0)`. On arm `i`, write `i:d` for its vertex at distance
`d`, with `1 <= d <= l_i`. The centre is not part of an arm's length. The order
is `n=1+l_1+l_2+l_3`; the project asks for size `floor(n/2)-1`.
For distinct vertices, distance is `|d-e|` on one arm, `d+e` on different arms,
and `d` from the centre. Every profile counts unordered distinct pairs once.
All intervals below include both endpoints; an interval with upper endpoint
below its lower endpoint is empty.

## Path construction, including both parities

Order the lengths `a >= b >= c`. Form the isometric path

`1:a, 1:(a-1), ..., 1:1, o, 2:1, ..., 2:b`.

It has `m=a+b+1` vertices. With `k=floor(m/2)`, take its first `k` vertices
as A and next `k` as B. If `m=2k`, nothing on this path is omitted; if
`m=2k+1`, its final vertex is omitted. Both sets are consecutive paths of
`k` vertices and are disjoint. For each distance `d=1,...,k-1`, both profiles
have multiplicity `k-d`; all other coefficients vanish. This proves equality
of the full profiles, not just equality of their supports.

The unused count in the whole tree is `c + (m mod 2)`.

## Alternating construction, including a one-vertex third arm

Relabel arms temporarily so `a >= b`, with third length `c`; do not require
`b >= c`. Put `k=floor(c/2)` and take

`A = {o} union {1:d : 1<=d<=b-1} union {3:2j : 1<=j<=k}`,

`B = {2:d : 1<=d<=b} union {3:(2j-1) : 1<=j<=k}`.

Both sizes are `b+k`. The sets are disjoint by arm and parity. When `c=2k`,
all vertices on arm 3 are used. When `c=2k+1`, its last vertex is omitted.
For `c=1`, both third-arm parts are empty; for `b=1`, the first-arm part of
A is empty. These are included cases, not exceptional repairs.

Here is an explicit distance-preserving bijection. Send `o` to `2:1`,
`1:d` to `2:(d+1)`, and `3:2j` to `3:(2j-1)`. Within the first two parts
distances are consecutive differences, within the alternating parts they are
`2|j-j'|`. A cross distance in A is `d+2j`, allowing `d=0` for the centre;
the corresponding B distance is `(d+1)+(2j-1)=d+2j`. Thus each unordered
pair has a counterpart of the same distance. This stronger fact is sufficient
here; it must not be imposed on unknown solutions to the project target.

The unused count is `1+a-b+(c mod 2)`. With all arm permutations, the largest
alternating size for sorted lengths is
`max(b+floor(c/2), c+floor(a/2))`.

For equal lengths `t`, this gives the target for every parity: size `3t/2`
when `t` is even, and `(3t-1)/2` when `t` is odd. In the latter case this
argument does not justify the journal's unrounded half-size wording.

## Block construction: admissible domain and quarantined endpoint

Use journal labels `a >= b > c`, and define `x=b-c > 0`,
`a+1=q*x+r`, `0<=r<x`. The extracted printed prescription makes its last
block index `h=q-1` for odd `q`, and `h=q` for even `q`, and uses blocks
`P_i={1:d : ix<=d<=(i+1)x-1}`, interpreting depth zero as `o`.
It assigns the even blocks and all of arm 3 to A, and the odd blocks and
all of arm 2 to B.

**Odd q:** the final endpoint is `q*x-1=a-r`, which exists. With `q=2s+1`,
A has `(s+1)x+c` vertices and B has `sx+b=(s+1)x+c`. They are disjoint and
omit exactly the final `r` vertices of arm 1. Hence size is `(n-r)/2`.
This includes `s=0` whenever the length inequalities permit it.

**Even q:** the prescribed endpoint is `(q+1)x-1=a+(x-r)>a`.
The final block needs `x-r` nonexistent vertices, for every permitted
remainder. Example: `(a,b,c)=(15,7,3)` gives `x=4,q=4,r=0` and demands
depths 16 through 19. The checker rejects this case. It does not shorten,
shift or drop a block and attribute the changed formula to the authors.

Publisher and author-PDF text extraction agree. The browser's PDF screenshot
requests returned cache-miss errors, so a visual check of the typeset formula
was unavailable. The precise ambiguity remains: extraction error or a printed
endpoint error. No correction or intended replacement is asserted here.

### Independent coefficient proof for every admissible odd-q block case

Use a formal variable `z`; coefficients count distances. Write
`F=1+z+...+z^(x-1)`, `C=z+...+z^c`, and

`E=F*(1+z^(2x)+...+z^(2sx))`,
`O=F*(z^x+z^(3x)+...+z^((2s-1)x))` (zero when `s=0`).

These are the depth enumerators of the even and odd block unions. The
secondary arm enumerators are `C` for A and `C+z^(c+1)*F` for B.
The identity `E-z^x*O=F` gives the cross-part profile difference

`E*C - O*(C+z^(c+1)*F) = F*C - z*F*O`,

using `(z^x-1)*C=z^(c+1)*F-z*F`.

Let `H_j=sum_(d=1)^(j-1) (j-d)*z^d` be the profile of a consecutive
`j`-vertex interval. The long-arm profile difference is

`H_x + sum_(k=1)^s z^(2kx)*F(z)*F(z^-1) = H_x + z*F*O`.

To see the first equality, delete the last even block: the remainder is a
translate of O, so only the internal pairs of the deleted block and its pairs
with the other even blocks remain. Since different blocks are ordered, all
these exponents are positive. The second equality uses
`F(z^-1)=z^(-(x-1))*F(z)`.

The secondary-arm difference is `H_c-H_(c+x)`. Splitting a consecutive
`c+x`-vertex interval into parts of sizes `x` and `c` proves

`H_(c+x)=H_x+H_c+F*C`.

Adding the three displayed profile differences yields zero coefficient by
coefficient. This exhausts internal and cross-part pairs, including all
centre pairs through depth zero in E. It proves the valid block family
without extending the formula beyond its domain.

## Exact boundary of what these constructions settle

For sorted lengths, put `p=floor((a+b+1)/2)`,
`u=max(b+floor(c/2), c+floor(a/2))`. If `b>c` and
`q=floor((a+1)/(b-c))` is odd, also put `v=(n-r)/2` with the remainder above.
Otherwise v is unavailable, not zero evidence for an upper bound.
The largest implemented size is exactly `K=max(p,u,v when available)`.
The still-unsettled cases **for this admission** are exactly those with
`K<floor(n/2)-1`. This arithmetic criterion is not a classification of h(T).

There are infinitely many such gaps: for integer `t>=4`, take
`(a,b,c)=(4t-1,2t,t)`. The path gives `3t`, the two alternating candidates
give at most `3t`, and the printed block quotient is 4, so it is inadmissible.
But the target is `floor(7t/2)-1>3t`. This proves insufficiency of the
reconstructed constructions, **not an obstruction to arbitrary homometric
sets**. It is a useful first family for the next mathematical step.

For that step, a complete exact equation is available. If `f_i(z)` lists
selected depths on arm i, and `e` is 0 or 1 for centre membership, its profile
is

`D(z)=sum_i positive_part(f_i(z)*f_i(z^-1))
      +sum_(i<j) f_i(z)*f_j(z) + e*sum_i f_i(z)`.

Here positive_part keeps strictly positive exponents, once each; diagonal
terms at exponent zero are excluded. Two sets must have identical D,
disjoint supports, disjoint centre membership and equal cardinality. This
is a formulation, not a solver or existence proof. Searching only for
distance-preserving bijections would impose an unjustified extra restriction.

## Verification and next acceptance

The README records a real command run. Tests independently build the tree
and count shortest-path distances by breadth-first search. They cover the
two path parities, both alternating parities and empty tails, odd block
quotients and endpoint remainders, all block-overrun remainder examples,
arm relabeling, invalid vertices, overlap and duplicate rejection, and a
pair with identical distance supports but unequal multiplicities.

A different resident still needs to reconstruct these arguments and run a
fresh counter on unequal triples. Then investigate the gap family above
with unrestricted coefficient equality, and resolve the survey/thesis
priority gap before any novelty claim. There is no project-completion claim.
