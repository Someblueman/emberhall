# What a Reversible Floating-Point Sum Must Remember

A collision for one published addition rule, and a complete trace of its
matrix inverse. [Read the proof and its limits](proof.md).

With p-bit binary words, the rule sends 2^p different valid accumulators to
one output even when the addend is known. An inverse given only that output
and addend needs p bits to distinguish these predecessors. In a two-by-two
matrix example, the printed subtraction sweep leaves `(-2^-163, 0)` instead
of zero in one cell. Retaining the original matrices permits replay, so this
is **not** a storage lower bound for every input-retaining algorithm.

This tests the formulas in section 2.4.1 and Algorithm 4 of
[Dwarka's paper](https://doi.org/10.1016/j.suscom.2025.101261).
It is a candidate result awaiting independent reconstruction. Priority and
the behavior of the inaccessible supplementary implementation remain open.

## Run it

With Python 3.10 or later, from the repository root:

```sh
python3 projects/reversible-sum/check.py
```

To obtain the repository first:

```sh
git clone https://github.com/Someblueman/emberhall.git
cd emberhall
python3 projects/reversible-sum/check.py
```

Only the Python standard library is needed. The command requires a binary64
Python float for its native comparison. It prints every forward and reverse
accumulator update, both words of each product and result, and the value each
reverse step should restore. [The complete recorded run](recorded-output.txt)
was made on 20 November 2026 with Python 3.13.2. Its opening is:

```text
Exact model: all 2040 family members checked for p=3..10.
Binary64 model: 106 boundary/power samples share (1, 2^-54).
Native binary64: all sampled outputs, unit products and trace steps agree.
```

The table ends with these two reverse steps at cell (0,0):

| t | Computed pair | Required pair |
|---:|---|---|
| 1 | (0,0) | (2^-163,0) |
| 0 | (-2^-163,0) | (0,0) |

The command also checks an exactly reversible zero case, replay from retained
matrices and recovery with a saved predecessor index. The precision-independent
result comes from the proof, not extrapolation from these computations.

Run the eight focused checks with:

```sh
python3 -m unittest discover -s projects/reversible-sum -p 'test_*.py' -v
```

The [exact arithmetic model](arithmetic.py) rounds rational values to binary
words and refuses nonrepresentable primitive residuals. The [native path](native.py)
uses separate floating-point error-free transforms. Neither is intended as
a production arithmetic library.
