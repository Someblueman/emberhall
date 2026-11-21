"""Rational primal/dual certificates for an observed RGB box, not just a point."""

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Iterable, Sequence

import blended_colour as bc
from display_colour import observation_box


@dataclass(frozen=True)
class BoxCertificate:
    event_indices: tuple[int, ...]
    p_min: F
    p_max: F
    witness_min: tuple[F, ...]
    witness_max: tuple[F, ...]
    dual_min: tuple[F, ...]
    dual_max: tuple[F, ...]

    def to_dict(self) -> dict:
        return {
            "event_indices": list(self.event_indices),
            "p_min": str(self.p_min), "p_max": str(self.p_max),
            **{key: [str(x) for x in getattr(self, key)] for key in
               ("witness_min", "witness_max", "dual_min", "dual_max")},
        }


def certificate_from_dict(data: dict) -> BoxCertificate:
    return BoxCertificate(
        tuple(data["event_indices"]), F(data["p_min"]), F(data["p_max"]),
        *(tuple(F(x) for x in data[key]) for key in
          ("witness_min", "witness_max", "dual_min", "dual_max")),
    )


def _inputs(palette: bc.Palette, lower: Sequence[F], upper: Sequence[F],
            event_indices: Iterable[int]) -> tuple[tuple[F, ...], tuple[F, ...], tuple[int, ...]]:
    lower, upper = tuple(map(F, lower)), tuple(map(F, upper))
    if len(lower) != 3 or len(upper) != 3 or any(not 0 <= a <= b <= 1 for a, b in zip(lower, upper)):
        raise ValueError("Box must contain three ordered channel intervals in [0, 1]")
    event = tuple(sorted(set(event_indices)))
    if not event or any(type(i) is not int or not 0 <= i < palette.size for i in event):
        raise ValueError("Event must contain valid palette indices")
    return lower, upper, event


def solve_box(palette: bc.Palette, lower: Sequence[F], upper: Sequence[F],
              event_indices: Iterable[int]) -> BoxCertificate:
    """Sharp bounds on the *closed rational box*, possibly an outer approximation."""
    lower, upper, event = _inputs(palette, lower, upper, event_indices)
    n = palette.size
    rows = [[F(1)] * n + [F(0)] * 6]
    for k in range(6):
        sign = 1 if k < 3 else -1
        rows.append([sign * c[k % 3] for c in palette.colours]
                    + [F(int(j == k)) for j in range(6)])
    rhs = [F(1), *upper, *(-x for x in lower)]
    costs = [F(int(i in event)) for i in range(n)] + [F(0)] * 6
    lo, p_lo, d_lo = bc._simplex_minimize(rows, rhs, costs)
    neg_hi, p_hi, d_hi = bc._simplex_minimize(rows, rhs, [-c for c in costs])
    cert = BoxCertificate(event, lo, -neg_hi, tuple(p_lo[:n]), tuple(p_hi[:n]),
                          tuple(d_lo), tuple(-x for x in d_hi))
    verify_box(palette, lower, upper, event, cert)
    return cert


def verify_box(palette: bc.Palette, lower: Sequence[F], upper: Sequence[F],
               event_indices: Iterable[int], cert: BoxCertificate) -> None:
    """Verify using sums and inequalities only; does not invoke the LP solver."""
    lower, upper, event = _inputs(palette, lower, upper, event_indices)
    if cert.event_indices != event or not 0 <= cert.p_min <= cert.p_max <= 1:
        raise ValueError("Certificate event or bound mismatch")
    rhs = (F(1), *upper, *(-x for x in lower))
    for is_min, witness, dual, bound in (
        (True, cert.witness_min, cert.dual_min, cert.p_min),
        (False, cert.witness_max, cert.dual_max, cert.p_max),
    ):
        if len(witness) != palette.size or any(x < 0 for x in witness) or sum(witness) != 1:
            raise ValueError("Invalid primal distribution")
        colour = bc.blend_colour(palette, witness)
        if any(not a <= x <= b for a, x, b in zip(lower, colour, upper)):
            raise ValueError("Primal colour outside observation box")
        if sum(witness[i] for i in event) != bound:
            raise ValueError("Primal objective mismatch")
        if len(dual) != 7 or any((x > 0 if is_min else x < 0) for x in dual[1:]):
            raise ValueError("Invalid dual slack signs or dimension")
        for i, colour in enumerate(palette.colours):
            value = dual[0] + sum((dual[j + 1] - dual[j + 4]) * colour[j] for j in range(3))
            cost = int(i in event)
            if (value > cost if is_min else value < cost):
                raise ValueError("Dual inequality fails at palette stop")
        if sum(x * y for x, y in zip(dual, rhs)) != bound:
            raise ValueError("Nonzero duality gap")


def solve_observation(palette: bc.Palette, rgb: Sequence[int], event_indices: Iterable[int],
                      mode: str = "srgb8") -> BoxCertificate:
    return solve_box(palette, *observation_box(rgb, mode), event_indices)


def verify_observation(palette: bc.Palette, rgb: Sequence[int], event_indices: Iterable[int],
                       cert: BoxCertificate, mode: str = "srgb8") -> None:
    verify_box(palette, *observation_box(rgb, mode), event_indices, cert)
