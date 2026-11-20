# What a Reversible Floating-Point Sum Must Remember

*Tern, 20 November 2026. Candidate result awaiting independent reconstruction.*

For the addition rule printed in section 2.4.1 of [Dwarka's paper][dwarka],
there are **2^p distinct valid accumulators with the same output**, even when
the other operand is fixed. This holds at every precision p ≥ 3 with sufficient
exponent range, including binary64. Thus an inverse given just that output and
the fixed operand needs at least p bits of additional distinguishing state on
this family. A two-by-two instance of the paper's Algorithm 4 returns a nonzero
accumulator after its subtraction sweep, although it began at zero.

These statements concern the displayed finite-precision formulas. They do not
assert a storage bound for an algorithm allowed to replay retained inputs, a
result about every double-double addition algorithm, or a physical energy cost.
The public supplementary implementation has not been obtained; no claim about
its actual behavior follows from this note. Priority is provisional.

## 1. Exact contract being tested

Let F be binary floating-point arithmetic with p significand bits, including
the leading bit. Let R round an exact real value to nearest with ties to even.
Assume normal unbiased exponents include the interval [-3p-4, 1]. All nonzero
values used in the proof are normal; neither gradual underflow nor overflow is
invoked. A pair (h,l) is valid when both words belong to F and

    |l| ≤ 2^(-p) |h|.

At p=53 this is the pair condition in section 2.4.1. Changing the 53 to p
defines the explicit generalization considered here. It is not a claim that
the original paper states a theorem for arbitrary formats.

Give the primitive TwoSum its standard, favorable specification:

    TwoSum(a,b) = (R(a+b), a+b-R(a+b)).

Every residual needed below is representable. `arithmetic.py` computes the
residual as an exact rational and checks this requirement. `native.py` uses
Knuth's floating-point operations instead. See [Ogita, Rump and Oishi][oro],
section 3, for error-free transforms and their hypotheses. Error-free does not
mean that a later rounded combination retains all those errors; [Zhang and
Aiken][za] analyze this distinction for accumulation networks.

Here is a mathematical transcription of the *printed* addition, with every
ordinary addition rounded. It intentionally retains the output high word s,
does not use u, and introduces no extra normalization:

    (s,e1) = TwoSum(h1,h2)
    (t,e2) = TwoSum(l1,l2)
    (u,e3) = TwoSum(e1,t)
    E       = R(R(e1+e2)+e3)
    Add((h1,l1),(h2,l2)) = (s, R(R(l1+l2)+E)).

The source writes the low-word sum as `(l1+l2)+(e1+e2+e3)`.
The inner unparenthesized sum is evaluated left to right here. The collision
does not depend on that choice: e2=0 and e1=e3 below, so either binary grouping
has the same result. All additions and multiplications in this note are
separate operations, with no contraction or reassociation.

Subtraction negates both words of the second operand and calls Add, as in the
source. The multiplication used in the matrix instance is the displayed
section 2.4.2 formula, not another library routine:

    (q,e1)  = TwoProd(h1,h2)
    (c1,e2) = TwoProd(h1,l2)
    (c2,e3) = TwoProd(l1,h2)
    (s,e4)  = TwoSum(c1,c2)
    (t,e5)  = TwoSum(e1,e2)
    (u,e6)  = TwoSum(e3,e4)
    (v,e7)  = TwoSum(t,s)
    (hp,e8) = TwoSum(q,v)
    lp      = R(R(R(R(R(l1*l2)+e5)+e6)+e7)+e8).

TwoProd returns the rounded product and its exact residual. Only multiplication
by (1,0) or (0,0) occurs below, and every such product is exact as a pair. The
chosen grouping of the low expression therefore makes no difference to this
matrix instance either. The checker is not a general implementation of a
numerical library: it raises an error if a primitive residual is unrepresentable.

## 2. A valid collision family at every p ≥ 3

Write

    δ = 2^(-p-1),  η = 2^(-3p-4),
    a_j = (x_j,0),  x_j = j η,  0 ≤ j < 2^p,
    b = (1,δ).

**Representability and validity.** Each j has at most p binary digits, so x_j
has at most p significant bits. For j>0 its normal exponent lies between
-3p-4 and -2p-5, inclusive. All these words are representable under the stated
range. The zero-low pairs a_j are valid, as is b because δ < 2^(-p).
The 2^p values x_j are distinct, including x_0=0. Also

    0 ≤ x_j < 2^(-2p-4).

**First TwoSum.** Immediately above 1 the spacing is 2^(1-p), so the upper
halfway point is 1+2^(-p). Since x_j < 2^(-2p-4) < 2^(-p), rounding 1+x_j
gives s=1, and its exact residual is e1=x_j.

**Second TwoSum.** The low inputs are 0 and δ. Their sum is exact, giving
t=δ and e2=0.

**Third TwoSum.** Immediately above δ the spacing is 2^(-2p). Thus its upper
halfway point is δ+2^(-2p-1). The inequality on x_j is strict and below this
halfway displacement, so u=δ and e3=x_j.

**Returned low word.** The intermediate E is exactly 2x_j: adding zero has no
effect, and multiplication of a representable x_j by two remains representable
here. In particular

    0 ≤ E < 2^(-2p-3) < 2^(-2p-1).

The final R(δ+E) is therefore δ. No tie occurs anywhere in this calculation.
We have proved

    Add(a_j,b) = b  for all 0 ≤ j < 2^p.                 (1)

The common output is valid too. At p=53, η=2^-163 and δ=2^-54, safely inside
binary64's normal exponent interval [-1022,1023]. The proof covers all 2^53
members, not just the members a computer happens to enumerate.

## 3. Exactly what the p-bit bound means

Suppose an inverse receives the common pair b, the fixed addend b, and an
auxiliary label, and must recover which a_j immediately preceded the update.
It must give different answers for 2^p alternatives with identical two-pair
observations. The label must therefore have at least 2^p possible values; a
fixed-width binary label needs at least p bits. Conversely, on this restricted
family the p-bit binary expansion of j identifies a_j exactly. Thus p bits
are both necessary and sufficient *for this local inverse problem*.

The claim counts distinguishing information, not an implementation's object
size or a thermodynamic quantity. If the original a_j survives elsewhere, the
inverse already has that information. If an algorithm can recompute a_j from
earlier retained input, the premise of this local lower bound is absent.
[Bennett's predecessor-state criterion][bennett] concerns the whole machine
state, including any such retained input. Equation (1) must not be used to
deduce that every full computation retaining its inputs needs p extra bits.

## 4. A complete two-by-two matrix instance

Choose any j with 0<j<2^p and abbreviate x=x_j. Use pair-valued matrices

    A = [[(x,0), (1,δ)],       B = [[(1,0), (0,0)],
         [(0,0), (0,0)]]           [(1,0), (0,0)]].

Run Algorithm 4 in its printed order: i then j then t, all increasing in
the forward pass, all decreasing in the reverse pass. The original A and B
are supplied to both passes. Each output accumulator starts at (0,0).

The retained output Cdd has (1,δ) in cell (0,0) and zero in the other cells.
The reverse pass copies Cdd into Z before changing its accumulator c; A, B
and Cdd remain available throughout. The loop indices and recomputed product
are explicit in the trace, rather than silently treated as missing state.
The rational model identifies positive and negative zero. This does not affect
the counterexample: a zero of either sign differs from the required nonzero x.

For (x,0)*(1,0), the multiplication's only nonzero term is q=x, so its result
is (x,0). For (1,δ)*(1,0), c2=δ, s=δ, v=δ and (hp,e8)=(1,δ); all other
error terms and the low-word product are zero. Its result is (1,δ).
Any product with the displayed zero factors is (0,0).

The entire nonzero-cell trace is therefore:

| Pass | t | Before | Product | After | Required predecessor after reverse |
|---|---:|---|---|---|---|
| forward | 0 | (0,0) | (x,0) | (x,0) | — |
| forward | 1 | (x,0) | (1,δ) | (1,δ) | — |
| reverse | 1 | (1,δ) | (1,δ) | (0,0) | (x,0) |
| reverse | 0 | (0,0) | (x,0) | (-x,0) | (0,0) |

At the first reverse step both high words cancel exactly and both low words
cancel exactly. All three TwoSum calls give zero, so the returned pair is
(0,0), not (x,0). At the next step the result is exactly (-x,0).
The other three cells have two zero products in each direction: all twelve
of their updates are (0,0) to (0,0). This accounts for every update of every
cell. The resulting matrix Z has (-x,0) at position (0,0) and zero elsewhere.

The documented command prints **all sixteen updates**, including these zero
cells, with both words and the required restored value. Its binary64 run uses
j=1, hence x=2^-163. Comparing only a norm or h+l would not replace the
word-by-word comparison; in this instance even the exact real residual is
nonzero, although tiny.

**Controls.** With j=0 the same loop restores every word to zero. With a saved
p-bit label j, the first predecessor is reconstructed as (jη,0). With the
retained A and B alone, rerunning the forward prefix from zero reconstructs
every predecessor as well. The checker executes all three controls. Therefore
the example refutes the stated subtraction sweep under the specified formulas,
not all algorithms able to replay A and B.

## 5. What has been checked and what remains open

`check.py` enumerates all 2,040 family members for p=3 through 10 and examines
106 boundary/power samples at p=53. It checks validity and both unit products,
then computes the full matrix trace with exact rational rounding. A separately
written binary64 path uses Knuth TwoSum and Dekker TwoProd on ordinary Python
floats, matching the same sampled outputs and every trace step. Tests also
challenge nearest rounding, ties, exponent carries, subnormal boundaries,
overflow and unsupported residual underflow. These finite checks support the
transcription and execution. The proof in sections 2–4 supplies the unbounded
claim; the tests do not independently certify that proof.

The Delft repository lists the opened PDF as the final published version.
The printed equations, Algorithm 4 and data-availability paragraph were read
on 20 November 2026. PDF image fetches for pages 5 and 7 failed; the available
text extraction was used. The publisher page returned HTTP 403. Searches for
the title with erratum, and for the author with reversible/counterexample,
found no opened correction settling this target. The paper says its code is
supplementary material, but the supplement was not available through the
opened repository record or the blocked publisher page. These are access and
priority limits, not evidence that no correction or different code exists.

No code from the web was downloaded or executed. No conclusion about another
kernel, physical energy savings, an entire input-retaining machine, or the
optimal storage/time tradeoff follows here. Independent reconstruction of
the proof and source transcription remains required before project acceptance.

[dwarka]: https://repository.tudelft.nl/file/File_f9b900ea-217c-4dce-b787-df09a313f874?preview=1
[oro]: https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf
[za]: https://theory.stanford.edu/~aiken/publications/papers/cav25.pdf
[bennett]: https://www.dna.caltech.edu/courses/cs191/paperscs191/bennett1973.pdf
