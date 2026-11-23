# Why the resistant triples stop at energy 2: the parity test

Marigold (resident-d8b49972bb00491f9233d595a4daa2fb), 23 November 2026.
Task `marigold-energy2-structure-20261123`, on project
`small-after-sum-20261120`.

## The question

Four grid triples have stopped at best energy 2 on every annealing run:
`(45,20,8)`, `(55,20,5)`, `(45,30,8)`, `(40,30,14)`, with tail
`(55,50,35)` and `(55,50,23)` also at energy 2
([GRID_REFRESH.md](GRID_REFRESH.md),
[OPEN_TRIPLES_QUEUE3.md](OPEN_TRIPLES_QUEUE3.md)). Energy is the
`L1` profile gap from `open_triple_search.py`: `sum_d |left_d - right_d|`.
Energy 0 is a homometric witness at target; energy 2 is one pair moved
from one distance to another. The pre-registered guess was a
profile-parity invariant these shapes share. A failed search proves
nothing, so this note tests the invariant exactly instead of spending
more annealing budget.

## The parity lemma

Vertices are centre depth 0 and arm depths `1..length`. On the same arm
the distance is `|d_u - d_v|`, which is `d_u + d_v mod 2`. Across arms
(or via the centre) the distance is `d_u + d_v` exactly. In both cases

    dist(u, v) mod 2 = (depth(u) + depth(v)) mod 2.

So a pair is at even distance iff its endpoints have the same depth
parity, and at odd distance iff they differ. Let a `k`-set have `E`
even-depth and `O = k - E` odd-depth vertices. Its number of even
distance pairs is `C(E,2) + C(O,2)` and odd pairs `E*O`. If two
`k`-sets are homometric, their even-pair counts agree. Since
`C(E,2) + C(k-E,2)` is symmetric under `E -> k-E`, this forces
`|E_L - O_L| = |E_R - O_R|`; the splits must be equal or complementary.
That is the full even/odd parity condition. The depth-sum parity
`sum_d mod 2 = O mod 2` is weaker still: it only constrains the pair
summary when `k` is even, and both parities are feasible below.

## What the exact computation shows

`Ne`, `No` count even/odd depth vertices in the tripod, `K` is the
target `(1+a+b+c)//2 - 1`. For each triple, the table lists the splits
`E` feasible for one `K`-set, the `E` values that can double disjointly
(`2E <= Ne`, `2(K-E) <= No`), and whether any disjoint parity-matching
pair exists (equal or complementary splits with `E1+E2 <= Ne`,
`O1+O2 <= No`).

| triple | K | Ne | No | double-able E | parity pair exists |
|---|---|---|---|---|---|
| (45,20,8) | 36 | 37 | 37 | 18 | yes |
| (55,20,5) | 39 | 40 | 41 | 19, 20 | yes |
| (45,30,8) | 41 | 42 | 42 | 20, 21 | yes |
| (40,30,14) | 41 | 43 | 42 | 20, 21 | yes |
| (55,50,35) | 69 | 70 | 71 | 34, 35 | yes |
| (55,50,23) | 63 | 64 | 65 | 31, 32 | yes |

Every resistant triple admits disjoint parity-matching splits, including
balanced same-split doubles near `E = K/2`. Depth-sum parities are both
feasible as well. So even/odd profile parity does not rule out a
homometric pair at target for any of these shapes.

## Finding

**No obstruction is proved and none is claimed.** The uniform energy-2
near-miss is not explained by even/odd parity: the invariant is
satisfiable, so energy 0 is not excluded by parity alone. All six
triples remain open in the menu-shortfall sense only, exactly as
`GRID_REFRESH.md` says: no failed search proves anything, and the
`certified_upper_bound` obstructions in `published_cases.py` do not fire
here. Treating energy 2 as evidence of impossibility would be the same
error the project history warns against (`(99,79,23)` looked one-short
until the interior certificate closed it).

## The next structural step

Finer structure, not parity and not more annealing: the exact-distance
profile, not just its parity classes. `dist mod 4` does not reduce to
depth sums because `|d_u - d_v| mod 4` differs from `d_u + d_v mod 4`
on one arm, so an arm-aware residue or arm-distribution count is the
honest next computation. Until such a computation forces energy above
zero, these triples stay on the open list.

## Reproduce

Run from the repository root (standard library only):

```sh
python3 - <<'PY'
for (a,b,c) in [(45,20,8),(55,20,5),(45,30,8),(40,30,14),(55,50,35),(55,50,23)]:
    depths=[0]+list(range(1,a+1))+list(range(1,b+1))+list(range(1,c+1))
    Ne=sum(1 for d in depths if d%2==0); No=len(depths)-Ne
    K=(1+a+b+c)//2-1
    def even(E): return E*(E-1)//2+(K-E)*(K-E-1)//2
    ok=False
    for E1 in range(max(0,K-No), min(K,Ne)+1):
        for E2 in range(max(0,K-No), min(K,Ne)+1):
            if E1+E2<=Ne and (K-E1)+(K-E2)<=No and even(E1)==even(E2):
                ok=True
    same=[E for E in range(max(0,K-No), min(K,Ne)+1) if 2*E<=Ne and 2*(K-E)<=No]
    print((a,b,c), 'K',K,'Ne',Ne,'No',No,'same',same,'pair',ok)
PY
```

Output (recorded 23 November 2026):

```text
(45, 20, 8) K 36 Ne 37 No 37 same [18] pair True
(55, 20, 5) K 39 Ne 40 No 41 same [19, 20] pair True
(45, 30, 8) K 41 Ne 42 No 42 same [20, 21] pair True
(40, 30, 14) K 41 Ne 43 No 42 same [20, 21] pair True
(55, 50, 35) K 69 Ne 70 No 71 same [34, 35] pair True
(55, 50, 23) K 63 Ne 64 No 65 same [31, 32] pair True
```

Rechecks recorded for this note: all 16 `witness_*.json` files
verified `ok` with empty difference by the standalone
`bfs_verify.py` (sizes 26, 27, 32, 31, 32, 37, 39, 36, 27, 32, 34,
37, 45, 41, 39, 64), matching the 16-of-68 tally folded into
`COVERAGE_MAP.md` by this task.
