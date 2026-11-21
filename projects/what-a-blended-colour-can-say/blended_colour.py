"""Exact rational finite-palette weighted-average colour model and LP bound solver.

Models linear 3-channel colour averaging:
    y = sum_i p_i * c_i,   p >= 0,   sum_i p_i = 1
over a finite palette C = (c_1, ..., c_n) in Q^{3 x n}, and computes exact
sharp probability bounds [P_min(E), P_max(E)] for any event E subseteq {0..n-1}
with primal extremal distributions and dual hyperplane certificates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Iterable, Sequence


RgbRational = tuple[Fraction, Fraction, Fraction]
QuadRational = tuple[Fraction, Fraction, Fraction, Fraction]


class InfeasibleColourError(ValueError):
    """Raised when a target colour lies outside the convex hull of the palette."""


@dataclass(frozen=True)
class Palette:
    """Finite ordered palette with exact rational channel coordinates in [0, 1]^3."""

    name: str
    labels: tuple[str, ...]
    values: tuple[Fraction, ...]
    colours: tuple[RgbRational, ...]
    description: str = ""

    def __post_init__(self) -> None:
        n = len(self.colours)
        if n == 0:
            raise ValueError("Palette must contain at least one colour")
        if len(self.labels) != n or len(self.values) != n:
            raise ValueError("Palette labels, values, and colours must have equal length")
        for idx, rgb in enumerate(self.colours):
            if len(rgb) != 3:
                raise ValueError(f"Colour {idx} must have 3 channels")
            for ch in rgb:
                if not isinstance(ch, Fraction):
                    raise TypeError("Palette coordinates must be fractions.Fraction")
                if not (Fraction(0) <= ch <= Fraction(1)):
                    raise ValueError(f"Channel coordinate {ch} out of [0, 1]")

    @property
    def size(self) -> int:
        return len(self.colours)

    def hex_colours(self) -> tuple[str, ...]:
        return tuple(rgb_to_hex(c) for c in self.colours)


@dataclass(frozen=True)
class BoundCertificate:
    """Exact primal-dual optimality certificate for P_min(E) and P_max(E)."""

    event_indices: tuple[int, ...]
    p_min: Fraction
    p_max: Fraction
    witness_min: tuple[Fraction, ...]
    witness_max: tuple[Fraction, ...]
    dual_min: QuadRational
    dual_max: QuadRational
    status: str

    def to_dict(self) -> dict:
        return {
            "event_indices": list(self.event_indices),
            "p_min": _frac_str(self.p_min),
            "p_max": _frac_str(self.p_max),
            "witness_min": [_frac_str(x) for x in self.witness_min],
            "witness_max": [_frac_str(x) for x in self.witness_max],
            "dual_min": [_frac_str(x) for x in self.dual_min],
            "dual_max": [_frac_str(x) for x in self.dual_max],
            "status": self.status,
        }


def _frac_str(val: Fraction) -> str:
    return str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"


def rgb_to_hex(rgb: Sequence[Fraction]) -> str:
    """Encode declared linear-light coordinates as half-up, 8-bit sRGB."""
    from display_colour import encode_rgb, hex_rgb
    return hex_rgb(encode_rgb(rgb, "srgb8"))


def certificate_from_dict(data: dict) -> BoundCertificate:
    return BoundCertificate(
        event_indices=tuple(int(i) for i in data["event_indices"]),
        p_min=Fraction(data["p_min"]),
        p_max=Fraction(data["p_max"]),
        witness_min=tuple(Fraction(x) for x in data["witness_min"]),
        witness_max=tuple(Fraction(x) for x in data["witness_max"]),
        dual_min=tuple(Fraction(x) for x in data["dual_min"]),  # type: ignore[arg-type]
        dual_max=tuple(Fraction(x) for x in data["dual_max"]),  # type: ignore[arg-type]
        status=str(data["status"]),
    )


def blend_colour(palette: Palette, weights: Sequence[Fraction]) -> RgbRational:
    """Compute exact weighted-average RGB colour for a probability vector."""
    if len(weights) != palette.size:
        raise ValueError(f"Expected {palette.size} weights, got {len(weights)}")
    norm = [Fraction(w) for w in weights]
    if any(w < 0 for w in norm):
        raise ValueError("Weights must be non-negative")
    if sum(norm) != Fraction(1):
        raise ValueError(f"Weights must sum to 1, got {sum(norm)}")
    r = sum(w * c[0] for w, c in zip(norm, palette.colours))
    g = sum(w * c[1] for w, c in zip(norm, palette.colours))
    b = sum(w * c[2] for w, c in zip(norm, palette.colours))
    return (r, g, b)


def _constraint_matrix(palette: Palette) -> list[list[Fraction]]:
    """Build 4 x n affine constraint matrix: [1^T; R; G; B]."""
    n = palette.size
    return [
        [Fraction(1) for _ in range(n)],
        [c[0] for c in palette.colours],
        [c[1] for c in palette.colours],
        [c[2] for c in palette.colours],
    ]


def _rref(matrix: list[list[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    """Exact rational reduced row echelon form returning (rref_matrix, pivot_cols)."""
    m = len(matrix)
    n = len(matrix[0]) if m else 0
    mat = [row[:] for row in matrix]
    pivots: list[int] = []
    r = 0
    for col in range(n):
        if r >= m:
            break
        pivot = next((i for i in range(r, m) if mat[i][col] != 0), None)
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        scale = mat[r][col]
        mat[r] = [v / scale for v in mat[r]]
        for i in range(m):
            if i != r and mat[i][col] != 0:
                factor = mat[i][col]
                mat[i] = [mat[i][j] - factor * mat[r][j] for j in range(n)]
        pivots.append(col)
        r += 1
    return mat, pivots


def nullspace_basis(palette: Palette) -> list[tuple[Fraction, ...]]:
    """Return an exact rational basis of ker([1^T; R; G; B])."""
    mat = _constraint_matrix(palette)
    rref, pivots = _rref(mat)
    n = palette.size
    pivot_set = set(pivots)
    basis: list[tuple[Fraction, ...]] = []
    for free_col in range(n):
        if free_col in pivot_set:
            continue
        vec = [Fraction(0) for _ in range(n)]
        vec[free_col] = Fraction(1)
        for row_idx, pcol in enumerate(pivots):
            vec[pcol] = -rref[row_idx][free_col]
        basis.append(tuple(vec))
    return basis


def nullspace_dimension(palette: Palette) -> int:
    return len(nullspace_basis(palette))


def _independent_rows(
    matrix: list[list[Fraction]], rhs: list[Fraction]
) -> tuple[list[int], list[list[Fraction]], list[Fraction]]:
    """Verify affine consistency of A p = rhs and select linearly independent rows."""
    m = len(matrix)
    n = len(matrix[0])
    aug = [matrix[i] + [rhs[i]] for i in range(m)]
    rref_aug, piv_aug = _rref(aug)
    if n in piv_aug:
        raise InfeasibleColourError("Target colour lies outside the affine span of the palette")
    # Find row basis via RREF of A^T.
    a_t = [[matrix[i][j] for i in range(m)] for j in range(n)]
    _, row_pivots = _rref(a_t)
    a_red = [matrix[i][:] for i in row_pivots]
    b_red = [rhs[i] for i in row_pivots]
    return row_pivots, a_red, b_red


def _invert_square(mat: list[list[Fraction]]) -> list[list[Fraction]]:
    k = len(mat)
    aug = [mat[i][:] + [Fraction(1 if i == j else 0) for j in range(k)] for i in range(k)]
    rref, pivots = _rref(aug)
    if len(pivots) != k or pivots != list(range(k)):
        raise ValueError("Singular basis matrix")
    return [row[k:] for row in rref]


def _simplex_minimize(
    a_eq: list[list[Fraction]], b_eq: list[Fraction], costs: list[Fraction]
) -> tuple[Fraction, list[Fraction], list[Fraction]]:
    """Exact two-phase rational simplex minimizing c^T x s.t. A x = b, x >= 0.

    Uses Bland's rule to guarantee finite termination with zero rounding error.
    Returns (optimal_value, primal_x, dual_y) where y^T A <= c^T and y^T b == c^T x.
    """
    m = len(a_eq)
    n = len(a_eq[0])
    a = [row[:] for row in a_eq]
    b = b_eq[:]
    for i in range(m):
        if b[i] < 0:
            b[i] = -b[i]
            a[i] = [-v for v in a[i]]

    # Phase I: artificial variables n .. n + m - 1.
    total_vars = n + m
    tableau = [
        a[i][:] + [Fraction(1 if i == j else 0) for j in range(m)] + [b[i]]
        for i in range(m)
    ]
    basis = [n + i for i in range(m)]

    def pivot(row: int, col: int) -> None:
        piv = tableau[row][col]
        tableau[row] = [v / piv for v in tableau[row]]
        for i in range(m):
            if i != row and tableau[i][col] != 0:
                factor = tableau[i][col]
                tableau[i] = [tableau[i][j] - factor * tableau[row][j] for j in range(len(tableau[i]))]
        basis[row] = col

    def run_simplex(obj: list[Fraction], active_cols: int) -> None:
        while True:
            # Dual multipliers y^T = c_B^T B^{-1} -> reduced costs r_j = obj[j] - sum_i obj[basis[i]] * tableau[i][j]
            entering = None
            for j in range(active_cols):
                if j in basis:
                    continue
                rc = obj[j] - sum(obj[basis[i]] * tableau[i][j] for i in range(m))
                if rc < 0:
                    entering = j
                    break  # Bland's rule: smallest index
            if entering is None:
                return
            leaving = None
            best_ratio: Fraction | None = None
            for i in range(m):
                entry = tableau[i][entering]
                if entry > 0:
                    ratio = tableau[i][-1] / entry
                    if best_ratio is None or ratio < best_ratio or (
                        ratio == best_ratio and basis[i] < basis[leaving]  # type: ignore[index]
                    ):
                        best_ratio = ratio
                        leaving = i
            if leaving is None:
                raise ValueError("Unbounded LP encountered on simplex")
            pivot(leaving, entering)

    phase1_obj = [Fraction(0)] * n + [Fraction(1)] * m
    run_simplex(phase1_obj, total_vars)
    phase1_val = sum(phase1_obj[basis[i]] * tableau[i][-1] for i in range(m))
    if phase1_val > 0:
        raise InfeasibleColourError("Target colour lies outside the convex hull of the palette")

    # Drive any zero-valued artificial variables out of the basis.
    for row_idx in range(m):
        if basis[row_idx] >= n:
            rep = next((j for j in range(n) if j not in basis and tableau[row_idx][j] != 0), None)
            if rep is None:
                raise ValueError("Unexpected dependent row during basis cleanup")
            pivot(row_idx, rep)

    # Drop artificial columns for Phase II.
    tableau = [row[:n] + [row[-1]] for row in tableau]
    run_simplex(costs, n)

    x = [Fraction(0) for _ in range(n)]
    for i, var_idx in enumerate(basis):
        x[var_idx] = tableau[i][-1]
    opt_val = sum(costs[j] * x[j] for j in range(n))

    # Compute exact dual vector y^T = c_B^T A_B^{-1} directly from original A_eq.
    a_b = [[a_eq[i][basis[j]] for j in range(m)] for i in range(m)]
    inv_a_b = _invert_square(a_b)
    c_b = [costs[basis[i]] for i in range(m)]
    dual_y = [sum(c_b[k] * inv_a_b[k][i] for k in range(m)) for i in range(m)]
    return opt_val, x, dual_y


def solve_event_bounds(
    palette: Palette, target_rgb: RgbRational, event_indices: Iterable[int]
) -> BoundCertificate:
    """Compute exact sharp [P_min, P_max] bounds and primal-dual certificates."""
    ev = tuple(sorted(set(int(i) for i in event_indices)))
    if not ev:
        raise ValueError("Event must contain at least one palette index")
    if any(i < 0 or i >= palette.size for i in ev):
        raise ValueError("Event index out of range")
    if len(target_rgb) != 3:
        raise ValueError("target_rgb must have 3 channels")
    target = tuple(Fraction(x) for x in target_rgb)

    a_full = _constraint_matrix(palette)
    b_full = [Fraction(1), target[0], target[1], target[2]]
    row_indices, a_red, b_red = _independent_rows(a_full, b_full)

    costs_min = [Fraction(1 if i in ev else 0) for i in range(palette.size)]
    costs_max = [-c for c in costs_min]

    p_min, w_min, y_min_red = _simplex_minimize(a_red, b_red, costs_min)
    neg_p_max, w_max, y_max_red = _simplex_minimize(a_red, b_red, costs_max)
    p_max = -neg_p_max

    dual_min = [Fraction(0)] * 4
    dual_max = [Fraction(0)] * 4
    for pos, ridx in enumerate(row_indices):
        dual_min[ridx] = y_min_red[pos]
        dual_max[ridx] = -y_max_red[pos]

    if p_min == p_max:
        status = "EXACT"
    elif p_min == Fraction(0) and p_max == Fraction(1):
        status = "UNIDENTIFIABLE"
    else:
        status = "BOUNDED"

    return BoundCertificate(
        event_indices=ev,
        p_min=p_min,
        p_max=p_max,
        witness_min=tuple(w_min),
        witness_max=tuple(w_max),
        dual_min=tuple(dual_min),  # type: ignore[arg-type]
        dual_max=tuple(dual_max),  # type: ignore[arg-type]
        status=status,
    )


def verify_certificate(
    palette: Palette,
    target_rgb: RgbRational,
    event_indices: Iterable[int],
    cert: BoundCertificate,
) -> None:
    """Independently verify primal feasibility, dual feasibility, and zero duality gap."""
    ev = tuple(sorted(set(int(i) for i in event_indices)))
    if cert.event_indices != ev:
        raise ValueError("Certificate event_indices mismatch")
    target = tuple(Fraction(x) for x in target_rgb)

    for label, witness, claimed_val in (
        ("min", cert.witness_min, cert.p_min),
        ("max", cert.witness_max, cert.p_max),
    ):
        if len(witness) != palette.size:
            raise ValueError(f"{label} witness length mismatch")
        if any(w < 0 for w in witness):
            raise ValueError(f"{label} witness has negative probability")
        if sum(witness) != Fraction(1):
            raise ValueError(f"{label} witness does not sum to 1")
        blended = blend_colour(palette, witness)
        if blended != target:
            raise ValueError(f"{label} witness blends to {blended}, expected {target}")
        ev_prob = sum(witness[i] for i in ev)
        if ev_prob != claimed_val:
            raise ValueError(f"{label} witness event prob {ev_prob} != {claimed_val}")

    # Dual checks over every palette colour c_i and target y.
    for i, c in enumerate(palette.colours):
        indicator = Fraction(1 if i in ev else 0)
        lhs_min = cert.dual_min[0] + cert.dual_min[1] * c[0] + cert.dual_min[2] * c[1] + cert.dual_min[3] * c[2]
        if lhs_min > indicator:
            raise ValueError(f"dual_min infeasible at stop {i}: {lhs_min} > {indicator}")
        lhs_max = cert.dual_max[0] + cert.dual_max[1] * c[0] + cert.dual_max[2] * c[1] + cert.dual_max[3] * c[2]
        if lhs_max < indicator:
            raise ValueError(f"dual_max infeasible at stop {i}: {lhs_max} < {indicator}")

    gap_min = cert.dual_min[0] + cert.dual_min[1] * target[0] + cert.dual_min[2] * target[1] + cert.dual_min[3] * target[2]
    if gap_min != cert.p_min:
        raise ValueError(f"Non-zero lower duality gap: {gap_min} != {cert.p_min}")
    gap_max = cert.dual_max[0] + cert.dual_max[1] * target[0] + cert.dual_max[2] * target[1] + cert.dual_max[3] * target[2]
    if gap_max != cert.p_max:
        raise ValueError(f"Non-zero upper duality gap: {gap_max} != {cert.p_max}")

    expected_status = (
        "EXACT"
        if cert.p_min == cert.p_max
        else "UNIDENTIFIABLE"
        if cert.p_min == Fraction(0) and cert.p_max == Fraction(1)
        else "BOUNDED"
    )
    if cert.status != expected_status:
        raise ValueError(f"Certificate status {cert.status} != {expected_status}")


def builtin_palettes() -> dict[str, Palette]:
    """Return the three Milestone 1 reference palettes."""
    two_colour = Palette(
        name="two_colour_diverging",
        labels=("Low (0)", "High (1)"),
        values=(Fraction(0), Fraction(1)),
        colours=(
            (Fraction(1, 8), Fraction(1, 4), Fraction(3, 4)),
            (Fraction(7, 8), Fraction(3, 8), Fraction(1, 8)),
        ),
        description="Two-stop diverging palette; 0-D nullspace so every blend is uniquely invertible.",
    )

    c_low = (Fraction(15, 16), Fraction(15, 16), Fraction(7, 8))
    c_high = (Fraction(1, 16), Fraction(5, 16), Fraction(3, 8))
    ramp_colours = tuple(
        tuple((1 - Fraction(k, 4)) * a + Fraction(k, 4) * b for a, b in zip(c_low, c_high))
        for k in range(5)
    )
    five_ramp = Palette(
        name="five_colour_ramp",
        labels=("L1", "L2", "L3", "L4", "L5"),
        values=(Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5)),
        colours=ramp_colours,  # type: ignore[arg-type]
        description="Five-stop 1D collinear linear ramp; 3-D nullspace creates severe ambiguity.",
    )

    c1 = (Fraction(1, 10), Fraction(1, 5), Fraction(4, 5))
    c2 = (Fraction(1, 5), Fraction(7, 10), Fraction(4, 5))
    c4 = (Fraction(9, 10), Fraction(2, 5), Fraction(1, 5))
    c5 = (Fraction(7, 10), Fraction(1, 10), Fraction(1, 2))
    c3 = tuple(
        Fraction(1, 5) * a + Fraction(2, 5) * b + Fraction(3, 10) * d + Fraction(1, 10) * e
        for a, b, d, e in zip(c1, c2, c4, c5)
    )
    five_tetra = Palette(
        name="five_colour_tetra_3d",
        labels=("L1 Very Low", "L2 Low", "L3 Medium", "L4 High", "L5 Very High"),
        values=(Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5)),
        colours=(c1, c2, c3, c4, c5),  # type: ignore[arg-type]
        description=(
            "Five-stop non-coplanar 3D palette with c3 inside conv(c1,c2,c4,c5); "
            "1-D nullspace gives tight outer-face bounds and an exact Radon witness at c3."
        ),
    )

    return {
        two_colour.name: two_colour,
        five_ramp.name: five_ramp,
        five_tetra.name: five_tetra,
    }


def showcase_witnesses() -> list[dict]:
    """Curated, checked swatches demonstrating exact, bounded, and unidentifiable regimes."""
    palettes = builtin_palettes()
    p2 = palettes["two_colour_diverging"]
    p5_3d = palettes["five_colour_tetra_3d"]
    p5_1d = palettes["five_colour_ramp"]

    specs = [
        {
            "id": "S1",
            "title": "2-Colour Blend (1:3)",
            "subtitle": "Unique binary mix",
            "palette": p2.name,
            "event_label": "P(High)",
            "event_indices": (1,),
            "weights": (Fraction(1, 4), Fraction(3, 4)),
            "held_out": False,
        },
        {
            "id": "S2",
            "title": "3D Outer Face Mix",
            "subtitle": "On conv(L1, L2, L4) facet",
            "palette": p5_3d.name,
            "event_label": "P(Level >= 4)",
            "event_indices": (3, 4),
            "weights": (Fraction(1, 5), Fraction(1, 5), Fraction(0), Fraction(3, 5), Fraction(0)),
            "held_out": False,
        },
        {
            "id": "S3",
            "title": "3D Near-Outer Blend",
            "subtitle": "Tight 10pp interval",
            "palette": p5_3d.name,
            "event_label": "P(Level >= 4)",
            "event_indices": (3, 4),
            "weights": (Fraction(1, 4), Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(0)),
            "held_out": False,
        },
        {
            "id": "S4",
            "title": "3D Pure Stop L3 (Tail)",
            "subtitle": "Up to 40% high risk",
            "palette": p5_3d.name,
            "event_label": "P(Level >= 4)",
            "event_indices": (3, 4),
            "weights": (Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
            "held_out": False,
        },
        {
            "id": "S5",
            "title": "1D Ramp Midpoint",
            "subtitle": "Collinear ramp widens bound",
            "palette": p5_1d.name,
            "event_label": "P(Level >= 4)",
            "event_indices": (3, 4),
            "weights": (Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
            "held_out": False,
        },
        {
            "id": "S6",
            "title": "Held-Out: Stop L3 (Mid)",
            "subtitle": "Exact L3 unidentifiable",
            "palette": p5_3d.name,
            "event_label": "P(Level = 3)",
            "event_indices": (2,),
            "weights": (Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
            "held_out": True,
        },
    ]

    out = []
    for sp in specs:
        pal = palettes[sp["palette"]]
        rgb = blend_colour(pal, sp["weights"])
        cert = solve_event_bounds(pal, rgb, sp["event_indices"])
        verify_certificate(pal, rgb, sp["event_indices"], cert)
        out.append(
            {
                "id": sp["id"],
                "title": sp["title"],
                "subtitle": sp["subtitle"],
                "palette": pal.name,
                "event_label": sp["event_label"],
                "event_indices": list(sp["event_indices"]),
                "weights": [_frac_str(w) for w in sp["weights"]],
                "rgb": [_frac_str(c) for c in rgb],
                "hex": rgb_to_hex(rgb),
                "held_out": sp["held_out"],
                "certificate": cert.to_dict(),
            }
        )
    return out


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify finite-palette colour-blending witnesses.")
    parser.add_argument("--json", action="store_true", help="Print verified showcase witnesses as JSON.")
    args = parser.parse_args(argv)

    witnesses = showcase_witnesses()
    if args.json:
        print(json.dumps({"swatches": witnesses}, indent=2))
    else:
        for item in witnesses:
            cert = item["certificate"]
            print(
                f"{item['id']} [{item['palette']}] {item['hex']} {item['event_label']} -> "
                f"[{cert['p_min']}, {cert['p_max']}] ({cert['status']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
