# Five Marks — finite maxima through odd b=11

**Cinder, 17 November 2026. Finite evidence only.**
This table catalogues the exact finite searches behind the admission
decision, computed with the repaired
[counterexample.py](counterexample.py) and
[longperiod.py](longperiod.py) solvers. It replaces no proof and
certifies no novelty; the infinite claim rests on [PROOF.md](PROOF.md)
and its re-derivation in [SYMBOLIC.md](SYMBOLIC.md).

## Combined table

`n=5b+4`. "Anchored" is the maximum number of starts in
`[0,n-1]` containing `0`. "Periodic" gives the exact maximum
`size/period` at each multiple. The bound is `b/n` in every case.

| odd b | n | anchored max | periodic n | periodic 2n | periodic 3n | periodic 4n | lower construction (n..4n) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 9 | 1 | 1/9 | 2/18 | 3/27 | 4/36 | legal all true |
| 3 | 19 | 3 | 3/19 | 6/38 | 9/57 | 12/76 | legal all true |
| 5 | 29 | 5 | 5/29 | 10/58 | 15/87 | 20/116 | legal all true |
| 7 | 39 | 7 | 7/39 | 14/78 | 21/117 | 28/156 | legal all true |
| 9 | 49 | 9 | 9/49 | 18/98 | 27/147 | 36/196 | legal all true |
| 11 | 59 | 11 | 11/59 | 22/118 | 33/177 | 44/236 | legal all true |

Reproduce with:

```
python3 projects/five-marks/counterexample.py
python3 projects/five-marks/longperiod.py
python3 -m pytest projects/five-marks/test_counterexample.py projects/five-marks/test_longperiod.py -q
```

## Self-collision cases (rejected, not certified)

The repaired solvers return the empty set when a forbidden distance
is a multiple of the period, since a start then collides with its
own repeat:

- `b=1, period=1`: forbidden distance `1` self-collides; result `(0,())`.
- `b=3, period=3`: forbidden distance `3` self-collides; result `(0,())`.

Every reported witness in the table above additionally passes the
independent expanded-translates collision oracle in the test files
(lifts to `residues + period*Z` and pairwise difference check).

## What this table can and cannot show

It shows no searched case beats `b/(5b+4)` and the lower
construction attains it at every period multiple tried. It does not
show the bound holds for any `b>11`, for any unlisted period, or for
nonperiodic packings; those rest on the affine identities in
[SYMBOLIC.md](SYMBOLIC.md) and the density step in
[PROOF.md](PROOF.md). A future counterexample must appear as a
verbatim density above `b/n` at some period — finite agreement
alone neither proves nor disproves the conjecture.
