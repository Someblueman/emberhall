# The three-reaction example has no nonconstant periodic orbit

For positive `a,b,c`, consider

```text
x' = a x² - b x y + c y
y' = 2 a x² - b x y
```

This is the explicit open example in the conclusion of
[Banaji, Boros and Hofbauer (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10953466/).
Our [proof](proof.md) excludes every nonconstant periodic orbit in the
nonnegative quadrant, and extends the result to a coefficient `m>=2` in
place of the second equation's `2`. It uses a polynomial boundary function
to put any hypothetical orbit inside a simply connected domain, then applies
the Bendixson–Dulac criterion there.

**Status:** complete author argument and exact checker, awaiting independent
mathematical review. A bounded 2024–2026 literature audit found no prior
resolution of this example; priority is provisional. The proof records
the sources, sections checked and access failures. This is not a claim to
settle all three-reaction networks or to prove global convergence.

From the root of a clone of this repository, with Python 3.10 or later:

```sh
python3 projects/three-reaction-no-cycle/check.py
```

No packages, network access, numerical solver or symbolic algebra system
are needed. The program multiplies sparse polynomials with rational
coefficients, differentiates them and checks that residuals vanish exactly.
The normalization uses Laurent monomials for the nonzero scaling factors.
The orbit, sign and topology arguments are in the document; the program
does not replace them.

To deliberately change the coefficient of `-uv` in the second normalized
equation from one to two while retaining the proposed certificate:

```sh
python3 projects/three-reaction-no-cycle/check.py --altered-coefficient
```

That command must print a nonzero-residual failure and exit with status 1.
The normal command also performs this negative control internally.

Tests:

```sh
python3 -m unittest discover -s projects/three-reaction-no-cycle -p 'test_*.py' -v
```

## Recorded run

Author run on 18 November 2026. The command above exited 0 and printed:

```text
PASS x scaling
PASS y scaling
PASS H = 2(u-1) - f
PASS u=1 points right
PASS H at u=1
PASS m=2 Dulac identity
PASS m=2 positive decomposition
PASS equilibrium f
PASS equilibrium g
PASS equilibrium H
PASS symbolic m Dulac identity
PASS m>=2 positive extension
PASS negative control rejected (y loss coefficient 1 -> 2)
Exact algebra passed. Domain and orbit arguments are in proof.md.
```

The deliberately altered command exited 1 and printed:

```text
FAIL altered m=2 Dulac identity: nonzero residual (3 terms)
```

The test command ran eight tests and returned `OK`. These exercise exact
rational arithmetic, symbolic substitution, the certificate, the explicit
damaged residual `u*(alpha*u²-2*u+2)`, selected boundary values and both real
commands with and without Python's `-O` flag. Rational boundary samples
are regression checks; the all-parameter sign argument is in the proof.
