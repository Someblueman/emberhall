# Wider starting sets on five stubborn triples: all five settle, and the width was not the point

Lupin, November 2026. Task `sable-broader-support-20261124`.
[FRESH_TRIPLES_EXACT_SWEEP.md](FRESH_TRIPLES_EXACT_SWEEP.md) left five
menu-shortfall triples with no witness on the tip/small-pool supports
at the default caps: `(70,60,40)`, `(100,80,50)`, `(71,57,39)`,
`(97,73,53)`, `(80,70,50)`. This run tried each twice: the small pool
as shipped, then a stated broader pool with honoured time caps.
**All five now have BFS-verified witnesses at target size**, listed
below. The honest reading, checked after the fact: no winning support
needed the broader pool — every one was already in the small pool.
What bound the earlier sweep was the free-bit caps (40 for the tip
support, 22 for pool supports), not the choice of starting sets.

## Phase A — small pool, as shipped

Run from this directory, one command per triple, 60 s cap each
(none came close; the caps inside the tool bind first):

```sh
timeout 60 python3 exact_completion.py A B C --out witness_A_B_C.json
```

| Lengths | Target | Supports | Obstructed | Inconclusive | Time |
|---|---:|---:|---:|---:|---:|
| 70,60,40 | 84 | 286 | 140 | 146 | 0.58 s |
| 100,80,50 | 114 | 286 | 142 | 144 | 1.08 s |
| 71,57,39 | 83 | 78 | 26 | 52 | 0.26 s |
| 97,73,53 | 111 | 78 | 22 | 56 | 0.42 s |
| 80,70,50 | 99 | 286 | 31 | 255 | 1.50 s |

Every run exited 1 (`no_witness_on_tried_supports`,
`all_omissions_obstructed: false`), reproducing the earlier sweep.
No witness file was written in this phase.

## Phase B — the rim-4 pool

The broader pool, named **rim-4**: the centre, depths 1–4 on each
arm, and the last four vertices of each arm (depths
`n, n-1, n-2, n-3`). It contains the small pool (centre, tips,
penultimates, depths 1–2) and has 25 vertices for these triples:
300 omitted sets where 2 vertices are omitted, 2300 where 3 are.
Supports were tried in a stated order — increasing sum, over the
omitted vertices, of tree distance to the nearest arm tip, ties
lexicographic — so the tip support and near-tip variants come first.
Caps, all honoured: `--max-free 80`, **20 s per support** (SIGALRM;
a support that overruns is counted `timed_out` and skipped),
**300 s per triple**. The driver (appendix, standard library only)
calls the project's own `long_frontier.complete_support` and recounts
any witness with `bfs_verify.verify` before writing it:

```sh
python3 /tmp/broader_sweep.py A B C --proj . --max-free 80 \
    --per-support 20 --per-triple 300 --out witness_A_B_C.json
```

| Lengths | Omitted (witness support) | Size = target | Free bits | Tried | Elapsed |
|---|---|---:|---:|---:|---:|
| 70,60,40 | (1,70), (1,69), (2,60) | 84 | 42 | 3 | 20.08 s |
| 100,80,50 | (2,80), (3,50), (3,49) | 114 | 50 | 10 | 140.99 s |
| 71,57,39 | (1,71), (2,57) | 83 | 46 | 1 | 0.02 s |
| 97,73,53 | (1,97), (2,73) | 111 | 65 | 1 | 1.69 s |
| 80,70,50 | (1,80), (2,70), (3,50) | 99 | 54 | 1 | 16.82 s |

Before its witness, `(70,60,40)` met 1 obstructed and 1 timed-out
support; `(100,80,50)` met 2 obstructed and 7 timed out. Timed-out
supports are inconclusive for that support only; no obstruction is
claimed for any support or triple from a timeout or a cap.

Each written file was then verified independently of the driver:

```text
$ python3 bfs_verify.py witness_70_60_40.json
{"difference": {}, "ok": true, "size": 84}
$ python3 bfs_verify.py witness_100_80_50.json
{"difference": {}, "ok": true, "size": 114}
$ python3 bfs_verify.py witness_71_57_39.json
{"difference": {}, "ok": true, "size": 83}
$ python3 bfs_verify.py witness_97_73_53.json
{"difference": {}, "ok": true, "size": 111}
$ python3 bfs_verify.py witness_80_70_50.json
{"difference": {}, "ok": true, "size": 99}
```

Witness files created by the Phase B commands (all in this
directory): `witness_70_60_40.json`, `witness_100_80_50.json`,
`witness_71_57_39.json`, `witness_97_73_53.json`,
`witness_80_70_50.json`.

## Reading the result

All five triples are settled finitely at target size
`floor((1+a+b+c)/2)-1`. But the wider pool deserves no credit,
checked directly against `exact_completion.supports_in_order`:
every winning omitted set is in the original small pool — three are
the tip support itself (small-pool index 1), and the other two sit
at small-pool indices 68 (`(70,60,40)`) and 124 (`(100,80,50)`).
What kept them out of reach was arithmetic, not geography: the
winning supports carry 42–65 free bits after complementation,
against shipped caps of 40 (tip) and 22 (pool), so the shipped tool
reported each one `inconclusive` in milliseconds and moved on.
Corroborated on the shipped CLI without the driver:

```text
$ python3 exact_completion.py 71 57 39 --max-free 80 --no-pool
{"bfs_ok": true, "free_bits": 46, "lengths": [71, 57, 39],
 "omitted": [[1, 71], [2, 57]], "parity_rank": 119, "size": 83,
 "status": "witness", "supports_tried": 1}
```

Two cautions stay. Enumeration is Gray-order over `2^free`
candidates and stops at the first exact hit, so these times say the
first witness was early in that order; a support with no early
witness is exactly what the 20 s cap abandons, and nothing here
bounds how typical early witnesses are. And the shipped CLI at
raised pool caps has no per-support clock, so for the two
tip-obstructed triples the CLI could still spend unbounded time on
an early pool support — the rim-4 order plus per-support cap is
what reached indices 68/124's equivalents in 3 and 10 tries.
A per-support time cap in `exact_completion.py` itself would make
this a one-command run; that edit is outside this task's ownership.

Finite witnesses settle single triples. The general construction
the milestone asks for is still open; this sweep only removes five
named finite exceptions and identifies the cap, not the pool, as
the binding constraint at this scale.

## Appendix — the Phase B driver, verbatim as run

Saved as `/tmp/broader_sweep.py` in this run; recreate it under any
name and pass `--proj` pointing at this directory.

```python
#!/usr/bin/env python3
"""Broader-pool exact completion for one tripod triple (rim-4 pool).

Reuses long_frontier.complete_support and bfs_verify.verify from the
project directory; adds a wider omitted-vertex pool, a stated support
order, a per-support time cap (SIGALRM) and a per-triple time cap.
Standard library only. Prints one JSON line; exit 0 iff a BFS-verified
witness was found (and written with --out).
"""
import argparse, json, signal, sys, time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
PROJ = Path(sys.argv[sys.argv.index("--proj") + 1]) if "--proj" in sys.argv else Path.cwd()
sys.path.insert(0, str(PROJ))

from bfs_verify import verify
from long_frontier import complete_support
from published_cases import validate_lengths


def target_size(lengths):
    return (1 + sum(lengths)) // 2 - 1


def rim4_pool(lengths):
    pool = [(0, 0)]
    for arm, n in enumerate(lengths, 1):
        pool += [(arm, d) for d in (1, 2, 3, 4) if d <= n]
        pool += [(arm, d) for d in (n, n - 1, n - 2, n - 3) if d >= 1]
    return list(dict.fromkeys(pool))


def tip_distance(lengths, v):
    arm, d = v
    if arm == 0:
        return min(lengths)
    own = lengths[arm - 1] - d
    via_centre = d + min(n for j, n in enumerate(lengths, 1) if j != arm)
    return min(own, via_centre)


class Cap(Exception):
    pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("lengths", nargs=3, type=int)
    p.add_argument("--proj", required=True)
    p.add_argument("--out", type=Path)
    p.add_argument("--max-free", type=int, default=80)
    p.add_argument("--per-support", type=float, default=20.0)
    p.add_argument("--per-triple", type=float, default=300.0)
    a = p.parse_args()
    lengths = validate_lengths(a.lengths)
    k = target_size(lengths)
    omissions = 1 + sum(lengths) - 2 * k
    pool = rim4_pool(lengths)
    supports = sorted(
        combinations(pool, omissions),
        key=lambda c: (sum(tip_distance(lengths, v) for v in c), c))
    signal.signal(signal.SIGALRM, lambda *e: (_ for _ in ()).throw(Cap()))
    counts = {"support_obstructed": 0, "inconclusive": 0, "timed_out": 0}
    start = time.time()
    tried = 0
    for omitted in supports:
        if time.time() - start > a.per_triple:
            break
        tried += 1
        signal.setitimer(signal.ITIMER_REAL, a.per_support)
        try:
            r = complete_support(lengths, list(omitted), a.max_free)
        except Cap:
            counts["timed_out"] += 1
            continue
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if r.get("status") == "witness":
            payload = {"lengths": list(lengths),
                       "left": [list(v) for v in r["left"]],
                       "right": [list(v) for v in r["right"]]}
            bfs = verify(payload)
            assert bfs.get("ok") and bfs.get("size") == k, bfs
            if a.out:
                a.out.write_text(json.dumps(payload, indent=1) + "\n")
            print(json.dumps({
                "lengths": list(lengths), "status": "witness", "size": k,
                "target": k, "omitted": [list(v) for v in omitted],
                "free_bits": r.get("free_bits_after_complement"),
                "parity_rank": r.get("independent_parity_rows"),
                "supports_tried": tried, "supports_total": len(supports),
                "counts": counts, "elapsed_s": round(time.time() - start, 2),
                "bfs_ok": True, "wrote": str(a.out) if a.out else None},
                sort_keys=True))
            return 0
        if r.get("status") in counts:
            counts[r["status"]] += 1
    print(json.dumps({
        "lengths": list(lengths), "status": "inconclusive", "size": k,
        "target": k, "supports_tried": tried,
        "supports_total": len(supports), "counts": counts,
        "elapsed_s": round(time.time() - start, 2),
        "all_omissions_obstructed": False}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```
