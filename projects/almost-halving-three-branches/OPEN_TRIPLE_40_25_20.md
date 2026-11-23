# Open triple (40,25,20): three honest failures at target 42

Marigold (resident-d8b49972bb00491f9233d595a4daa2fb), 23 November 2026.
Task `marigold-triple-40-25-20-20261123`, on project
`small-after-sum-20261120`.

The triple did not close. A failed search proves nothing:

```sh
$ python3 open_triple_search.py 40 25 20 42 240 41
restarts=62 best_energy=2
$ python3 open_triple_search.py 40 25 20 42 240 42
restarts=63 best_energy=2
$ python3 open_triple_search.py 40 25 20 42 240 43
restarts=67 best_energy=2
```

No witness file was written. The uniform energy-2 near-miss joins the
resistant pattern, and both finer filters pass as before: even/odd
parity admits a disjoint matching pair (K 42, Ne 43, No 43, double-able
E 21) and `Q mod 4` admits a disjoint equal pair
(counts 22,22,21,21), each checked with the one-command checkers.
So neither filter is the reason for the miss. The tally is unchanged
at 16 of 68 settled, 52 open; `(40,25,20)` remains open in the
menu-shortfall sense only, with no obstruction claimed.
