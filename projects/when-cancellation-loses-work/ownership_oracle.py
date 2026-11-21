"""Ownership checks over observations; no scheduler or cancellation imports."""
from __future__ import annotations

from collections import Counter


def violations(weights: tuple[int, ...], state: dict) -> tuple[str, ...]:
    """Reconstruct ownership and capacity from a snapshot, independently."""
    expected = set(range(len(weights)))
    locations = state["queue"] + state["returned"] + state["live"] + state["completed"] + state["registry"]
    counts = Counter(locations)
    errors = []
    for job in sorted(expected):
        if counts[job] == 0:
            errors.append(f"lost:{job}")
        elif counts[job] != 1:
            errors.append(f"multiple-owners:{job}")
    for job in sorted(set(counts) - expected):
        errors.append(f"unknown-job:{job}")
    held = state["held"]
    if set(held) - expected:
        errors.append("unknown-reservation")
    if any(job not in held for job in state["live"]):
        errors.append("unreserved-live-job")
    for job, weight in held.items():
        if job in expected and weight != weights[job]:
            errors.append(f"wrong-weight:{job}")
        if job not in state["live"] and job not in state["registry"]:
            errors.append(f"stranded:{job}")
    total = sum(held.values())
    if state["free"] < 0 or total > 3 or state["free"] + total != 3:
        errors.append("capacity-accounting")
    if state["terminal"] and (state["live"] or state["registry"] or held):
        errors.append("unsettled-terminal")
    return tuple(errors)
