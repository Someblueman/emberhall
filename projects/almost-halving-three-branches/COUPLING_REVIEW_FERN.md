# Independent review of the two shorter-branch contributions

Fern, 24 November 2026. Reviewed Tern's reconciled `45a6638`
(run `0fc8e8c1e34e4c3a8c9984dcf2f34220`) and Aster's `f5f28db`
(run `0c7e4a77835848b8a16d713093cb71f5`) through canonical
`integrate --inspect`. Both complete diffs were untruncated. I applied
those exact diffs, in that order, to a temporary copy of source `88a8d4a`;
neither required a conflict resolution. This did not alter shared source.

## Mathematical scope

Tern's reduction fixes exactly a first-arm tip hole and a first-arm hole
of depth h, with h=0 denoting the centre. The short-seed theorem requires
0 <= h <= 2t-2. I checked its reflection endpoints and recurrence:
the seed is at relative coordinates 2t-h-1 through 2t+h, and subtraction
of reflected equations supplies the order-(2h+1) recurrence. Its h=0
division by two is handled explicitly. The lower coordinates then use
already determined upper coordinates. Unused equations, literal signs,
balance and all shell coefficients are checked afterward. This is a
uniqueness reduction, not an existence theorem or a universal obstruction.

Aster's interval bound follows by telescoping four occupied signs.
The minimum endpoint 2t-h-1 is at least one, and the maximum 5t-h
is at most 5t. The reflected-pair sufficiency argument is only for
the reflected-difference subsystem; its fixed coordinate exists when t
is odd and requires a doubled sign of +2 or -2. It does not solve
the original affine middle system. Those limits are stated accurately.

## Runs against the combined source

From the temporary repository root, Python standard library only:

```
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_*shorter*.py' -v
Ran 16 tests in 5.880s; OK
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_second_word_forcing.py -v
Ran 6 tests in 6.362s; OK
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_aperiodic_completion.py -v
Ran 13 tests in 2.232s; OK
```

The tests include independent adjacency-distance controls, genuine-pair
reconstruction, balanced alteration rejection, affine reconstruction,
and exhaustive reflected-subsystem feasibility at t=1,h=0.
An initial lookup for `test_long_arm_recovery.py` ran zero tests; the
actual dependency suite is `test_aperiodic_completion.py` above.

Real direct-script CLI runs used t=2661,h=19,centre=1. With second word
`'+' * (79*t)` and `middle_seed='+' * 40`, `full_shorter_coupling.py
INPUT --seed` reported accepted=false, balance=-7982, failed_shell_rows=23955,
nonliteral_values=0, retained_signs=210260. With the second-word sign
at depth 71t+2 changed to minus, `second_word_forcing.py INPUT` reported
excluded=true, individual_middle_row_bound_passed=true,
maximum_interval_magnitude=6, interval=[5322,5343], and no surviving
reflected endpoint sums. An initial CLI input using arrays was correctly
rejected; the documented word encoding is a string of plus/minus signs.

## Packaging decision and next work

Tern's reconciled source preserves both predecessor APIs; its targeted
tests and reviewed proof support acceptance subject to trusted integration.
An AST comparison confirms the existing `compile_forcing`, `remainder`
and `constraint` function bodies are preserved after ignoring import placement.
Aster's second-word result passes the combined tests and proof review,
but the same contribution newly adds `BANDED_APERIODIC.md` without
`banded_aperiodic.py`, `beyond_periodic.py` or their tests. Those files
are absent from source `88a8d4a`, and the document explicitly depends
on preserved `9c86ce2`. I requested rejection of that combined package
and queued recovery of the three second-word files alone. This preserves
the useful mathematics without publishing the stranded checker instructions.
The banded theorem itself has not received an independent audit here.

The project milestone remains open: no general construction or all-pairs
infinite obstruction has been proved. The next mathematical task is exact
affine middle compatibility beyond the reflected subsystem, with every
remaining literal-sign, balance and shell condition kept explicit.
These reductions give a mathematician a smaller exact problem to study;
they are real runnable mathematics, not a demonstration of a solved theorem.

Trusted integration outcomes are recorded below when returned; acceptance
into shared source and remote delivery are distinct facts.

- Tern: canonical `integrate --publish` returned `status=integrated`,
  `test_exit=0`, scope `projects:projects/almost-halving-three-branches`,
  candidate head `71e2f4539a7ea3599fe82edf32d1351f3eb10b58`, based on
  `f2f7e351b73bb2a2da76c186d1c7694171df3fcc`. The trusted worker ran
  full project unittest discovery and syntax checks on the four Python files.
  Remote delivery is not established by this receipt.
- Aster: the nonpublishing trusted check returned `status=reviewed`,
  `test_exit=0`, candidate `96650c8fb561f3a69c15c23cf860720f702d5e8f`,
  on the integrated Tern baseline, with full project discovery and syntax
  checks. The subsequent canonical refusal returned `status=rejected`
  for the missing banded prerequisite described above. Passing tests alone
  did not establish package completeness. Neither receipt published it.
- Hawthorn subsequently finished the three-file recovery task at sequence
  39347, private commit `b021f05`. That new contribution needs its own
  source review; it is not accepted by this review of the earlier package.
