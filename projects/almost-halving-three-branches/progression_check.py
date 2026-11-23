"""An independent check of the classification of evenly spaced arms.

[PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md) proves that
T(b+d, b, b-d) has a partition of *all* its vertices into two equal homometric
sets if and only if

    b is odd, and either d divides b or 2d divides b+1.              (1)

The project checked that classification with its own enumeration of balanced
partitions.  This checks it with a different method: the exhaustive
profile-group search in `small_triples.py`, which finds the exact optimum of
each tree rather than only deciding whether a full partition exists.  Two
things follow that the enumeration does not give directly.  The exact optimum
is known for every case, and the negative cases - where (1) predicts that no
full partition exists - can be checked for attainability of the target as well.

Standard library only; Python 3.10+.

One command, from a clone of Emberhall at the repository root::

    python3 projects/almost-halving-three-branches/progression_check.py --middle 5

It prints one line per (b, d) case and a final verdict, and exits non-zero if
any case disagrees with (1) or if the target is not attained.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import small_triples  # noqa: E402  the exhaustive census this check reuses


def predicts_full_partition(b: int, d: int) -> bool:
    """Condition (1) of PROGRESSION_PARTITIONS.md."""
    if b % 2 == 0:
        return False
    return b % d == 0 or (b + 1) % (2 * d) == 0


def full_partition_size(b: int) -> int:
    """The size each side would have in a partition of all 3b+1 vertices."""
    return (1 + 3 * b) // 2


def case(b: int, d: int) -> dict:
    """Everything the check knows about one (b, d) case."""
    lengths = (b + d, b, b - d)
    best = small_triples.optimum(*lengths)
    goal = small_triples.target(*lengths)
    half = full_partition_size(b)
    predicted = predicts_full_partition(b, d)
    # A partition of all 3b+1 vertices into two equal sets needs 3b+1 to be
    # even, so only an odd b can have one; then it must reach (3b+1)/2.
    observed = (b % 2 == 1) and best == half
    return {
        "b": b, "d": d, "lengths": lengths, "optimum": best, "target": goal,
        "full_size": half, "predicted": predicted, "observed": observed,
        "target_attained": best >= goal,
        "bound_attained_exactly": (not predicted) and best == goal,
    }


def check_case(row: dict) -> tuple[bool, str]:
    """The checks one case must pass, and the reason for any failure."""
    if row["predicted"] != row["observed"]:
        return False, (f"the classification says a full partition "
                       f"{'exists' if row['predicted'] else 'does not exist'}, "
                       f"the exhaustive search disagrees")
    if not row["target_attained"]:
        return False, f"the target {row['target']} was not attained"
    if row["b"] % 2 == 1 and not row["predicted"] and not row["bound_attained_exactly"]:
        return False, (f"the upper bound {row['target']} is not attained exactly "
                       f"(the optimum is {row['optimum']})")
    return True, "agrees"


def cases(middle: int):
    """Every (b, d) with 2 <= b <= middle and 1 <= d < b."""
    for b in range(2, middle + 1):
        for d in range(1, b):
            yield b, d


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--middle", type=int, default=5,
                        help="check every middle arm b <= MIDDLE (default 5)")
    args = parser.parse_args(argv)
    if args.middle < 2:
        parser.error("--middle must be at least 2")
    ok = True
    count = 0
    for b, d in cases(args.middle):
        row = case(b, d)
        passed, detail = check_case(row)
        ok = ok and passed
        count += 1
        print(f"b={row['b']} d={row['d']} lengths={row['lengths'][0]},{row['lengths'][1]},"
              f"{row['lengths'][2]} optimum={row['optimum']} target={row['target']} "
              f"full_size={row['full_size']} classification="
              f"{'full' if row['predicted'] else 'no full'} observed="
              f"{'full' if row['observed'] else 'no full'} "
              f"target_attained={'yes' if row['target_attained'] else 'no'} "
              f"{'PASS' if passed else 'FAIL: ' + detail}")
    print(f"CHECK {'PASSED' if ok else 'FAILED'} over {count} cases")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
