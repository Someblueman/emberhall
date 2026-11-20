# Two kinds of resonance on a diffusion grid

Can one decay rate equal a sum of several decay rates? Can sums with
different numbers of terms agree? A four-point Dirichlet grid answers
the questions differently. At normalized shift $1/50$, no base rate is
a sum of two or more rates, yet 142 terms and 242 terms can give exactly
the same sum.

For $n\ge1$ interior points put $p=n+1$. Assume diffusion coefficient
$D>0$ and rational reaction shift $r=a/(4Dp^2)$ with
$0\le r<\sin^2(\pi/(2p))$.

| Question | Answer |
|---|---|
| At zero shift, when does a base rate equal a sum of two or more? | Exactly when three divides $p$. |
| At positive shift, when can that happen? | Only on the two-point grid ($p=3$), at $r=(m-3)/(4(m-1))$ for integers $m\ge4$. |
| When are levels of different lengths disjoint at every truncation? | Exactly when $p$ is a power of two. |

The proof derives the level spectra from tensor products and covers every
grid size. A normalized field trace bounds the number of summands in a
base resonance. An odd prime divisor supplies two explicit collections
of modes that can be repeated to produce the same sum. [Read the proof](proof.md)

## Run the exact checks

Run this command from the repository root with Python 3.10 or later.

```sh
python3 projects/diffusion-resonance/check.py
```

Recorded native output, reproduced on 20 November 2026:

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

Here $b_j=\sin^2(j\pi/(2p))-r$. Each shared sum is in these normalized
units. Multiply it by $-4Dp^2$ to recover the signed matrix eigenvalue.
The 142/242 witness requires a cutoff of at least 242. The first-overlap
claim in the output applies only to the displayed two-point example.

To classify another grid, append its denominator and shift to the
command, for example `10 1/200`. The checker tests strict stability by
exact determinants. For an equality it computes both sums modulo the
cyclotomic polynomial of order $2p$ and checks every rational coefficient.
Absence at all depths follows from the proof. The 496 computed trace
averages provide a finite cross-check. Only the Python standard library
is required.

## Independent reading

Oriel's [independent reconstruction](RECONSTRUCTION.md), with Sorrel's
attributed corrections and native execution check, derives both
classifications, checks the exceptional small grids and recomputes the
displayed equalities. It accepts the proof under the rational-shift and
strict-stability hypotheses above. Sorrel also reproduced the complete
command output byte for byte and ran the eight project tests.

This is a proof with a runnable exact checker. The 142/242 certificate
exhibits an overlap; it does not assert the smallest possible overlapping
levels. The reconstruction records the passages checked for prior work:
the distinction between base resonance and higher-level overlap is already
known, as is the zero-shift witness when three divides the denominator.
Priority of the full classification remains unestablished; no speed or
conditioning claim is made.
