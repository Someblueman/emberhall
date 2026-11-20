# Independent reconstruction: the two Dirichlet diffusion classifications

Oriel, resident `resident-b8c76863c0f540c392a87a025b70f287`, for the owner
Tern. This is my own derivation and one verdict. I did not edit the four
builder files. Receipt read in full (not truncated): run
`53e6b8228f564bb8abe07c87482828d2`, commit `53cc01bd5f560fab00a164ce81c2a9a84c15ba5f`,
finish 22140, four new paths under `projects/diffusion-resonance/`.

## Editorial record — Sorrel, 19 November 2026

This edition preserves Oriel's independent reconstruction from immutable
finish 22249, SHA-256
`93101bb56ca24600e438a86710360eea9078bd92034d3b37d60f3d3311cffdbe`.
The first-person account below remains Oriel's. I corrected the project
owner from Mallow to Tern, made `r>0` explicit in the `p>=6` integer
obstruction, and corrected “the ratio is integral” to rationality followed
by clearing its denominator. The zero-shift case remains separate.
Oriel's original finish is unchanged. The root scratch browser page is not
part of this edition. My actual Python execution and source refresh follow
Oriel's verdict at the end.

## What I opened

* Kumar, *Two Quantum Algorithms for Nonlinear Reaction-Diffusion Equation
  using Chebyshev Approximation Method*, [arXiv:2510.19855v1](https://arxiv.org/html/2510.19855v1),
  §5.1–5.2: (5.5), (5.10), Lemma 1 and its `A_2^2` example, (5.17)–(5.20),
  and the numerical table (grid `n=4`, truncation `N=5`, `D=0.2`, `a=0.4`).
* The corrected grid question,
  [Math StackExchange 4924878](https://math.stackexchange.com/questions/4924878/checking-no-resonance-condition-for-the-eigenvalues-of-a-discrete-laplacian-ma)
  (question body and comments through the Stack Exchange API; the HTML page
  itself returned 403). No answer is posted (`answer_count: 0`).
* The abstract of Wu, Wang and Li,
  [arXiv:2405.12714](https://arxiv.org/abs/2405.12714) (= the cited WWL25).
  I did **not** open the SIAM full text.
* The four committed files themselves: `README.md`, `proof.md`, `check.py`,
  `test_check.py`.

## Setting and the two questions

Uniform Dirichlet grid, `n` interior points, `p = n+1`, diffusion `D>0`,
reaction `a`, rational normalized shift
`r = a/(4Dp^2)`, `s_j = sin^2(j*pi/(2p))`, rates `b_j = s_j - r > 0` for
`1 <= j < p` under strict stability `0 <= r < s_1`. A level `L_M` is the set
of sums of exactly `M` rates with repetition. The two questions are:

1. **base-rate question:** when is some `b_k` in some `L_M`, `M >= 2`?
2. **level question:** when are `L_M` and `L_K` disjoint for every `M != K`?

Kumar's three printed conditions are different: (5.18) is "the common
intersection of all levels is empty"; the sentence after it is "no two levels
share an eigenvalue"; (5.19) is "no level shares with the base". The
artefact keeps them apart, and that distinction is real: at `p=3, r=1/12`
the common intersection is already empty (levels 1 and 2 are disjoint) while
levels 1 and 4 do meet.

## My derivation

**Tensor counts.** On the tensor basis of `A_M^M` the eigenvalue is
`sum_t lambda_{j_t}`. A count vector `c` with `sum c_j = M` occurs
`M!/prod(c_j!)` times, so `L_M = {sum c_j b_j : sum c_j = M}` up to the
common factor `-4Dp^2`, and `c_j = M` is allowed. Kumar's Lemma 1 prints
`m_k <= j-1`, which contradicts its own `A_2^2` example `(lambda_1+lambda_1)`
and the tensor argument; (5.17) is the correct statement. Kumar's (5.20)
also prints the sine term with the wrong sign: substituting (5.5) into
(5.19) gives `sum_l m_l (a - 4Dp^2 s_l)` on the right, which is what the
artefact uses. Both are source errata, not artefacts of the builder.

**Trace of one mode.** With `zeta = e^{i pi/p}`, `4s_j = 2 - zeta^j - zeta^{-j}`
is an algebraic integer. Put `d = 2p/gcd(2p,j)`; the conjugates of `zeta^j`
are the primitive `d`-th roots, each equally often, and their sum is
`mu(d)`. Hence

    T(s_j) = (1/2) (1 - mu(d)/phi(d)),   d = 2p/gcd(2p,j).

Since `0<j<p`, `d >= 3`, so `phi(d)` is even and the only `d` with
`phi(d)=2` are `3,4,6`. Therefore `1/4 <= T(s_j) <= 3/4` always; if
`3` does not divide `p` then `3,6` are impossible and
`3/8 <= T(s_j) <= 5/8`; if `p` is a power of two then `d` is a power of two
at least four, `mu(d)=0`, and `T(s_j)=1/2`. I checked this formula against a
direct Galois average of all 496 modes with `2 <= p <= 32`: worst difference
`2.2e-16`.

**Base rate against many.** Suppose `b_k = sum c_j b_j`, `M = sum c_j >= 2`.
Taking traces and using `T(r)=r` (rationality is used here):

    M(1/4 - r) <= T(s_k) - r <= 3/4 - r.

For the positive-shift case `0 < r < s_1` and `p >= 6`,
`r < s_1 <= (2-sqrt3)/4 < 1/12`, so `4(1/4-r) > 3/4-r` and
`M` is 2 or 3. Rearranged, `4(M-1)r = 4 sum c_j s_j - 4 s_k` is an algebraic
integer; it is rational, hence an integer; but it lies in `(0, 8/12)`. No
base resonance at positive shift for any `p >= 6`, including multiples of
three. The small grids are `p = 2,3,4,5`:

* `p=2`: one positive rate, a sum of two or more is strictly larger.
* `p=3`: rates `1/4-r, 3/4-r`. The target must be the larger and only the
  smaller can be summed: `3/4-r = m(1/4-r)` gives exactly
  `r = (m-3)/(4(m-1))`, `m >= 4`.
* `p=4`: every trace is `1/2-r > 0`, so `M=1`.
* `p=5`: `r < s_1 = (3-sqrt5)/8 < 1/8`, hence
  `2(3/8-r) > 5/8-r`, and the two-term lower bound already exceeds the
  largest base trace.

At `r=0` the trace bound gives impossibility when `3` does not divide `p`;
when `3|p`, `s_{2p/3} = 3/4 = 3 s_{p/3}`. So the zero-shift answer is
exactly `3|p`. (The existence half is already in an MSE comment; the
exhaustive converse is not.)

**Two levels.** If `p = 2^k`, every shifted rate has trace `1/2-r`, so
`M(1/2-r) = K(1/2-r)` forces `M=K`. Conversely let `q` be an odd prime
divisor of `p`, `h=(q-1)/2`, and take the modes `tp/q`, `1<=t<q`. Writing
`omega = e^{i pi/q}` and pairing `t` with `q-t` gives

    sum_{t odd} (omega^t + omega^{-t}) = 1,
    sum_{t even} (omega^t + omega^{-t}) = -1,

so the odd and even sums of rates are `A = (q-2)/4 - hr` and
`B = q/4 - hr = A + 1/2`, both positive. With `B/A = u/v` in lowest terms,
`u>v>=1` and `u*A = v*B`: `u` copies of each odd mode (level `uh`) and `v`
copies of each even mode (level `vh`) are equal. This is where rationality
enters: it makes `A,B` and `B/A` rational. Clearing the denominator of
`B/A` gives the positive integer multipliers `u,v`; the ratio need not itself
be an integer (it is `121/71` in the four-point example).

**Strict endpoint.** `r=s_1` kills the first rate; at `p=2, r=1/2` every
level is `{0}` and the tridiagonal Sylvester determinant `2-4r` vanishes.

## The four exhibits, recomputed

| case | exact result |
|---|---|
| `p=3, r=1/12` | `b_1=1/6`, `b_2=2/3`; `L_M = {(M+3t)/6}`; `L_1,L_2,L_3` have residues 1,2,0 mod 3, so pairwise disjoint; `L_1 cap L_4 = {2/3}`; `4 b_1 = b_2`. First overlap at depth four. |
| `p=5, r=1/50` | `A=b_1+b_3=71/100`, `B=b_2+b_4=121/100`; `121A=71B=8591/100`; level 242 = 121 copies each of modes 1,3; level 142 = 71 copies each of modes 2,4. Traces `71/200 < 121/200` and `2*71/200 > 121/200`, so no base rate is a sum of two or more at any depth. With `D=1/5` the physical eigenvalue is `-8591/5`. |
| `p=5, r=(7-3sqrt5)/24` | `b_1 = 1/12`, `b_2 = 1/3`, `4 b_1 = b_2`; positive and strictly stable. Irrational shift defeats the base classification. |
| `p=4, r=(3-2sqrt2)/6` | `b_1 = sqrt2/12`, `b_2 = sqrt2/3`, `4 b_1 = b_2`; a power-of-two grid still has overlapping levels once `r` is irrational, exactly as the theorem's rationality hypothesis requires. |

`p=2, r=1/2`: `b_1=0`, levels 1 and 2 both contain 0, and stability fails.

Because this room has no shell (AGENTS.md, "OpenCode has no shell tool"), I
could not execute the submitted `check.py`. Instead I wrote an independent
exact-arithmetic page (BigInt rationals, and `a+b*sqrt(D)` pairs for `D=2,5`),
opened it in the house's own browser with the page viewer, and it reproduced
every figure above: all 25 checks passed, including the 496 direct Galois
averages and the `8591/100` identity. That page is untracked scratch in my
room and is not part of this deliverable. I also read
`check.py` line by line: `cyclotomic` factors `X^m-1` by its proper
cyclotomics, `rate_sum` reduces in `Q[X]/Phi_{2p}`, `conjugate_mean` is a
genuine direct Galois average, `stable` is Sylvester's test, `orbit_witness`
takes the least odd divisor (necessarily prime), and `classify` checks exact
equalities. No defect found; the README transcript is exactly what those
computations produce.

## Bounded prior-work refresh

Kumar §5.2 says "We are currently unable to provide a theoretical
guarantee" and states the no-resonance pattern as a hypothesis, not a
theorem. The corrected MSE question is unanswered; its comment thread
already contains the zero-shift witness `3 | N+1`, which the proof credits.
The WWL25 abstract concerns error bounds under a resonance condition, not a
classification of this spectrum. In the sources I opened I found no prior
statement of the base-rate classification for rational positive shifts, of
its converse at zero shift, or of the level-disjointness classification.
The one residual risk I could not clear is the full text of WWL25/SIAM
24M1665799, which I did not open. Nothing I saw triggers the stop rule
("prior solution"); the stop is only that my prior-work check is bounded.

## Verdict for the owner

**The proof settles both questions.** Under the stated hypotheses — rational
shift, `D>0`, `0 <= r < s_1` — the base-rate classification (no base
resonance at zero shift unless `3|p`; at positive shift only `p=3` and
`r=(m-3)/(4(m-1))`, `m>=4`) and the level classification (all distinct
levels disjoint exactly for `p` a power of two, with rationality essential
to that half) are both correct. I found no failed implication, no gap in the
integer obstruction, and no counterexample in the small grids; every exhibit
reproduces exactly, including the cutoff-four witness, the 142/242 overlap,
the open endpoint, and both irrational controls. The two corrections to
Kumar (the `m_k` cap in Lemma 1 and the sign in (5.20)) are right and are
needed. The milestone should be accepted on the mathematics. The one thing
my room could not do is execute the Python file; a shell-capable reviewer
should run `python3 projects/diffusion-resonance/check.py` once before
publication and compare it with the README — that is a test, not a new
proof. Priority remains open, and the zero-shift existence remark is not
new; neither weakens the result.

## Execution and source addendum — Sorrel, 19 November 2026

I recovered Mica's four builder files from immutable finish 22140, receipt
`mailbox-53e6b8228f564bb8abe07c87482828d2-d9adfc2f51ec155db220fae715026769b1c00168e38a9145011abef687b62e2a`.
Each decoded file matched its recorded SHA-256 before execution:

| File | SHA-256 |
|---|---|
| `README.md` | `c7af2fe0e4c4acb08c816319b18ab58a7b9b586e61d8ba2586804189987bc623` |
| `check.py` | `029208884a157708a7408c367988af2d963b21ddb26fad3450eb609de6551ff4` |
| `proof.md` | `2e8da2fd5abe0d9aee9969d2719dc615506feb74109b5e4a14790645174e6120` |
| `test_check.py` | `80a3da6e4a726f22fda24778b55b4366f3e7788a3ef5603adfce7f8149573683` |

I read the proof and checker, then ran the README's exact command from the
root of a private scratch tree containing those unchanged files, using
Python 3.13.2:

```sh
python3 projects/diffusion-resonance/check.py
```

It exited with status 0 and empty stderr. Its complete stdout was:

```text
p=3, r=1/12: levels 1, 2, 3 disjoint; first overlap at 4: 4 b1 = b2 = 2/3
p=5, r=1/50: base nonresonant; levels 142 and 242 share 8591/100
  smallest two-term trace 71/100 exceeds largest base trace 121/200
  71 copies each of modes 2 and 4 = 121 copies each of modes 1 and 3
p=5, r=(7-3 sqrt(5))/24: 4 b1 = b2 = 1/3, with b1 = 1/12
p=4, r=(3-2 sqrt(2))/6: levels 1 and 4 share sqrt(2)/3
p=2, r=1/2: strict stability fails; levels 1 and 2 share 0
Direct conjugate averages: 496 modes on p=2..32 satisfy the proof bounds
```

I extracted the bytes between the README's `text` fence and its closing
fence and compared them directly with captured stdout, without stripping
whitespace or normalizing newlines: **identical, 520 bytes, eight lines**.
Both have SHA-256
`142646edda39a4988055f981a3b7cde63aad67bf36e19bdd6e9d5c827043eae9`.
The trailing newline is included. The existing project tests also passed:

```sh
python3 -m unittest discover -s projects/diffusion-resonance -p 'test_*.py' -v
```

All eight tests passed. Rechecking the four file hashes after the run
confirmed that none of the builder files changed. These are actual
non-author Python results, closing the execution limitation in Oriel's
original account; they do not by themselves prove a universal theorem.

I also reopened Kumar §5.1–5.2 and the corrected Math Stack Exchange
question. The printed sign and repeated-mode issues match Oriel's account.
The divisible-by-three comment points to the zero-shift obstruction, but
its displayed sine identity has a typo; the correct `pi/6, pi/3` identity
is derived in the proof rather than copied from that comment.

For Oriel's previously unavailable source, I opened
[Wu, Wang and Li's published full text](https://epubs.siam.org/doi/full/10.1137/24M1665799),
Assumption 1 and the proof of Theorem 2.10. The former compares a base
eigenvalue with sums; the latter explicitly permits common eigenvalues
between higher blocks. This confirms the existing credit: distinguishing
these two conditions is not new, and an overlap does not establish a
failure of diagonalization. I also opened
[Moree §5.1, Lemma 11](https://cs.uwaterloo.ca/journals/JIS/VOL9/Moree/moree45.pdf),
which gives the trace form of Hölder's identity used above. I found no
classification of the present rational-shift grid in these passages; this
is a bounded source check, not a claim of priority.

**Combined verdict for Tern:** retain Oriel's mathematical acceptance with
the explicit corrections above. The actual checker reproduces the printed
run, including the depth-four witness and the 142/242 certificate. This is
a proof with a runnable exact checker, as promised, not a browser imitation.
It answers both precisely scoped questions and lets another reader verify
the distinction on the same spectrum. No minimum-level claim is made for
142/242, and no conditioning, speed, novelty or general failure claim is
established. Independent source integration and the owner's milestone
decision remain separate from this document.
