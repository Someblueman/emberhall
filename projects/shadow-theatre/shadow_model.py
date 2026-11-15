"""Finite-screen 2D shadow-projection model and challenge schema."""

from __future__ import annotations

import json
import math
from typing import Any

MAX_PROPS = 3


def _require_finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    f = float(value)
    if not math.isfinite(f):
        raise ValueError(f"{name} must be finite")
    return f


def validate_scene(
    light: dict[str, Any],
    props: list[dict[str, Any]],
    screen: dict[str, Any],
) -> tuple[dict[str, float], list[dict[str, float]], dict[str, float]]:
    """Validate point light, opaque vertical segments, and finite screen."""
    if not isinstance(light, dict) or not isinstance(screen, dict) or not isinstance(props, list):
        raise ValueError("light, props, and screen must be valid objects/lists")

    sx = _require_finite(screen.get("x"), "screen.x")
    sy_min = _require_finite(screen.get("yMin"), "screen.yMin")
    sy_max = _require_finite(screen.get("yMax"), "screen.yMax")
    if sy_min >= sy_max:
        raise ValueError("Degenerate screen: screen.yMin must be strictly less than screen.yMax")

    lx = _require_finite(light.get("x"), "light.x")
    ly = _require_finite(light.get("y"), "light.y")
    if lx >= sx:
        raise ValueError("Forbidden source position: light.x must be strictly less than screen.x")

    if len(props) > MAX_PROPS:
        raise ValueError(f"Out of domain: at most {MAX_PROPS} props are allowed")

    clean_props: list[dict[str, float]] = []
    for idx, prop in enumerate(props):
        if not isinstance(prop, dict):
            raise ValueError(f"prop[{idx}] must be an object")
        px = _require_finite(prop.get("x"), f"props[{idx}].x")
        py_low = _require_finite(prop.get("yLow"), f"props[{idx}].yLow")
        py_high = _require_finite(prop.get("yHigh"), f"props[{idx}].yHigh")
        if px <= lx or px >= sx:
            raise ValueError(
                f"Forbidden prop position: props[{idx}].x must be strictly between light.x and screen.x"
            )
        if py_low >= py_high:
            raise ValueError(
                f"Degenerate segment: props[{idx}].yLow must be strictly less than props[{idx}].yHigh"
            )
        clean_props.append({"x": px, "yLow": py_low, "yHigh": py_high})

    return (
        {"x": lx, "y": ly},
        clean_props,
        {"x": sx, "yMin": sy_min, "yMax": sy_max},
    )


def compute_shadows(
    light: dict[str, Any],
    props: list[dict[str, Any]],
    screen: dict[str, Any],
) -> dict[str, Any]:
    """Compute clipped, merged shadow intervals on the finite screen."""
    l_clean, p_clean, s_clean = validate_scene(light, props, screen)
    lx, ly = l_clean["x"], l_clean["y"]
    sx, sy_min, sy_max = s_clean["x"], s_clean["yMin"], s_clean["yMax"]

    raw_intervals: list[list[float]] = []
    clipped_intervals: list[list[float]] = []

    for prop in p_clean:
        mag = (sx - lx) / (prop["x"] - lx)
        y_a = ly + mag * (prop["yLow"] - ly)
        y_b = ly + mag * (prop["yHigh"] - ly)
        raw_intervals.append([y_a, y_b])

        c_a = max(y_a, sy_min)
        c_b = min(y_b, sy_max)
        if c_a < c_b:
            clipped_intervals.append([c_a, c_b])

    clipped_intervals.sort(key=lambda iv: (iv[0], iv[1]))
    merged: list[list[float]] = []
    for start, end in clipped_intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    total_length = sum(end - start for start, end in merged)
    return {
        "rawIntervals": raw_intervals,
        "intervals": merged,
        "totalLength": total_length,
    }


def matches_target(
    intervals: list[list[float]],
    target: list[list[float]],
    tolerance: float = 0.5,
) -> bool:
    """Return True if projected intervals match target intervals within tolerance."""
    if len(intervals) != len(target):
        return False
    for (a1, b1), (a2, b2) in zip(intervals, target):
        if abs(a1 - a2) > tolerance or abs(b1 - b2) > tolerance:
            return False
    return True


def export_challenge(challenge: dict[str, Any]) -> str:
    """Serialize a validated challenge to canonical JSON."""
    _validate_challenge(challenge)
    return json.dumps(challenge, sort_keys=True, separators=(",", ":"))


def import_challenge(raw_json: str) -> dict[str, Any]:
    """Parse and validate a challenge JSON string."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid challenge JSON: {exc}") from exc
    _validate_challenge(data)
    return data


def _validate_challenge(challenge: Any) -> None:
    if not isinstance(challenge, dict):
        raise ValueError("Challenge must be a JSON object")
    for key in ("id", "title", "description", "screen", "light", "props", "target"):
        if key not in challenge:
            raise ValueError(f"Missing challenge field: {key}")
    compute_shadows(challenge["light"], challenge["props"], challenge["screen"])
    target = challenge["target"]
    if not isinstance(target, list):
        raise ValueError("Challenge target must be a list of [start, end] pairs")
    for idx, iv in enumerate(target):
        if not isinstance(iv, list) or len(iv) != 2:
            raise ValueError(f"target[{idx}] must be a [start, end] pair")
        a = _require_finite(iv[0], f"target[{idx}][0]")
        b = _require_finite(iv[1], f"target[{idx}][1]")
        if a >= b:
            raise ValueError(f"target[{idx}] must have start < end")


CHALLENGES: list[dict[str, Any]] = [
    {
        "id": "single-gate",
        "title": "1. Single Gate",
        "description": "Position the single prop so its shadow spans [25, 75] on the screen.",
        "screen": {"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        "light": {"x": 0.0, "y": 50.0},
        "props": [{"x": 50.0, "yLow": 40.0, "yHigh": 60.0}],
        "target": [[25.0, 75.0]],
        "tolerance": 0.5,
        "solution": {
            "light": {"x": 0.0, "y": 50.0},
            "props": [{"x": 40.0, "yLow": 40.0, "yHigh": 60.0}],
        },
    },
    {
        "id": "twin-pillars",
        "title": "2. Twin Pillars, One Shadow",
        "description": "Align two props so their shadows touch or overlap into one continuous interval [20, 80].",
        "screen": {"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        "light": {"x": 0.0, "y": 50.0},
        "props": [
            {"x": 50.0, "yLow": 35.0, "yHigh": 50.0},
            {"x": 50.0, "yLow": 55.0, "yHigh": 70.0},
        ],
        "target": [[20.0, 80.0]],
        "tolerance": 0.5,
        "solution": {
            "light": {"x": 0.0, "y": 50.0},
            "props": [
                {"x": 50.0, "yLow": 35.0, "yHigh": 50.0},
                {"x": 50.0, "yLow": 50.0, "yHigh": 65.0},
            ],
        },
    },
    {
        "id": "clipped-horizon",
        "title": "3. Clipped Horizon",
        "description": "Use three props—with at least one clipped by the screen edge—to cast [[10, 40], [70, 100]].",
        "screen": {"x": 100.0, "yMin": 0.0, "yMax": 100.0},
        "light": {"x": 0.0, "y": 50.0},
        "props": [
            {"x": 50.0, "yLow": 30.0, "yHigh": 45.0},
            {"x": 50.0, "yLow": 60.0, "yHigh": 75.0},
            {"x": 50.0, "yLow": 75.0, "yHigh": 90.0},
        ],
        "target": [[10.0, 40.0], [70.0, 100.0]],
        "tolerance": 0.5,
        "solution": {
            "light": {"x": 0.0, "y": 50.0},
            "props": [
                {"x": 50.0, "yLow": 30.0, "yHigh": 45.0},
                {"x": 50.0, "yLow": 60.0, "yHigh": 75.0},
                {"x": 50.0, "yLow": 70.0, "yHigh": 90.0},
            ],
        },
    },
]
