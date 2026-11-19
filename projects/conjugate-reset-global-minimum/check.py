#!/usr/bin/env python3
"""Numerical challenges to the accompanying proof; Python standard library only.

No simulation, network, or dependencies. Quadrature is floating-point evidence,
not an exact certificate for the theorem. Run --kernel-factor 2 to check that
the direct renewal calculation rejects the full-line/half-line factor error.
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Callable
from fractions import Fraction

Scalar = Callable[[float], float]
SQRT_PI = math.sqrt(math.pi)


def quad(f: Scalar, a: float, b: float, tol: float = 2e-10) -> float:
    """Adaptive Simpson integration, with an explicit failure on exhaustion."""
    if a == b:
        return 0.0
    fa, fm, fb = f(a), f((a + b) / 2), f(b)
    whole = (b - a) * (fa + 4 * fm + fb) / 6

    def split(a, b, fa, fm, fb, whole, eps, depth):
        m = (a + b) / 2
        fl, fr = f((a + m) / 2), f((m + b) / 2)
        left = (m - a) * (fa + 4 * fl + fm) / 6
        right = (b - m) * (fm + 4 * fr + fb) / 6
        error = left + right - whole
        if abs(error) <= 15 * eps:
            return left + right + error / 15
        if depth == 0:
            raise ArithmeticError("quadrature did not converge")
        return split(a, m, fa, fl, fm, left, eps / 2, depth - 1) + split(
            m, b, fm, fr, fb, right, eps / 2, depth - 1
        )

    return split(a, b, fa, fm, fb, whole, tol, 24)


def close(label: str, got: float, want: float, rtol=2e-8, atol=2e-9) -> None:
    if not math.isfinite(got) or not math.isfinite(want):
        raise AssertionError(f"{label}: nonfinite value {got}, {want}")
    if not math.isclose(got, want, rel_tol=rtol, abs_tol=atol):
        raise AssertionError(f"{label}: got {got:.14g}, expected {want:.14g}")


def success(x: float, t: float, d: float) -> float:
    return math.erfc(x / math.sqrt(4 * d * t))


def cycle(x: float, t: float, d: float) -> float:
    """Integral_0^t erf(x/sqrt(4 D s)) ds, evaluated independently of the kernel."""
    z = x / math.sqrt(4 * d * t)
    return t * math.erf(z) + x * math.sqrt(t / d) / SQRT_PI * math.exp(-z * z) - (
        x * x / (2 * d) * math.erfc(z)
    )


def atomic(times: tuple[float, ...], weights: tuple[float, ...], d: float):
    close("atomic weights", sum(weights), 1.0)
    if len(times) != len(weights) or any(t <= 0 for t in times) or min(weights) <= 0:
        raise ValueError("positive atoms and weights required")
    return (
        lambda x: math.fsum(w * success(x, t, d) for t, w in zip(times, weights)),
        lambda x: math.fsum(w * cycle(x, t, d) for t, w in zip(times, weights)),
    )


def exponential(rate: float, d: float):
    a = math.sqrt(rate / d)
    return lambda x: math.exp(-a * x), lambda x: -math.expm1(-a * x) / rate


def pareto_one(x: float, scale: float, d: float) -> tuple[float, float]:
    """T has density scale/t^2 on t>=scale: E[T]=infinity, E[T^.75]<infinity.

    f follows by integrating 2*q*erfc(z*q) on [0,1]. For g, integrate
    the explicit cycle numerator against 2*q dq; only integral erf(u)/u
    remains. Subtract its logarithmic part before quadrature for large z.
    """
    z = x / math.sqrt(4 * d * scale)
    if z == 0:
        return 1.0, 0.0
    if z < 0.03:
        f = 1 - 4 / SQRT_PI * (z / 3 - z**3 / 15 + z**5 / 70 - z**7 / 378)
    else:
        f = math.erfc(z) + math.erf(z) / (2 * z * z) - math.exp(-z * z) / (SQRT_PI * z)
    if z <= 1:
        integral = quad(lambda u: math.erf(u) / u if u else 2 / SQRT_PI, 0, z)
    else:
        integral = PARETO_I1 + math.log(z) - quad(
            lambda u: math.erfc(u) / u, 1, min(z, 12)
        )
    g = scale * (2 * integral + 2 * math.erf(z) - 2 * z * z * f)
    return f, g


PARETO_I1 = quad(lambda u: math.erf(u) / u if u else 2 / SQRT_PI, 0, 1)


def kernel_at(f: Scalar, x: float, upper: float, d: float) -> float:
    return (quad(lambda y: y * f(y), 0, x) + x * quad(f, x, upper)) / d


def box_comparison(f: Scalar, h: Scalar, upper: float, n: int, d: float):
    """Three separately summed expressions on [0,upper]^2, Simpson weights.

    Cost C=integral K h(x)h(y)u(x)^2; baseline B=integral K f(x)f(y);
    remainder R=half integral K h(x)h(y)(u(x)-u(y))^2, u=f/h.
    All use the same finite box. No infinity-infinity or tail cancellation.
    """
    step = upper / n
    xs = [i * step for i in range(n + 1)]
    ws = [step / 3 * (1 if i in (0, n) else 4 if i % 2 else 2) for i in range(n + 1)]
    fs, hs = [f(x) for x in xs], [h(x) for x in xs]
    if min(hs) <= 0:
        raise ArithmeticError("success probability underflow in comparison")
    us = [a / b for a, b in zip(fs, hs)]
    cost_rows, base_rows, remainder_rows = [], [], []
    for i, x in enumerate(xs):
        kernel_row = [min(x, y) * ws[i] * ws[j] / d for j, y in enumerate(xs)]
        cost_rows.append(math.fsum(
            k * hs[i] * hs[j] * us[i] ** 2 for j, k in enumerate(kernel_row)
        ))
        base_rows.append(math.fsum(k * fs[i] * fs[j] for j, k in enumerate(kernel_row)))
        remainder_rows.append(math.fsum(
            kernel_row[j] * hs[i] * hs[j] * (us[i] - us[j]) ** 2
            for j in range(i + 1, n + 1)
        ))
    return tuple(map(math.fsum, (cost_rows, base_rows, remainder_rows)))


def time_pair(s: float, t: float) -> tuple[float, float]:
    """Half-line normalization/energy kernels at D=1, stable for s << t."""
    s, t = min(s, t), max(s, t)
    a = 2/SQRT_PI * (math.sqrt(s) - s/(math.sqrt(t+s) + math.sqrt(t)))
    ratio = s/t
    b = 4/(3*SQRT_PI) * t**1.5 * (
        math.expm1(1.5*math.log1p(ratio)) - ratio**1.5
    )
    return a, b


def dyadic_check() -> None:
    """An unbounded atomic law and the excluded critical-moment boundary."""
    q = 9/16  # P(T=2^n)=(1-q)q^n; E[T]=infinity, E[T^.75]<infinity.
    sums = []
    for count in (128, 256, 512):
        norm, energy = [], []
        for i in range(count):
            for j in range(i, count):
                a, b = time_pair(2.0**i, 2.0**j)
                weight = (1-q)**2 * q**(i+j) * (1 if i == j else 2)
                norm.append(weight*a)
                energy.append(weight*b)
        sums.append((math.fsum(norm), math.fsum(energy)))
    moment = (1-q)/(1-q*2**0.75)
    tail_moment = moment * (q*2**0.75)**256
    energy_bound = time_pair(1, 1)[1] * 2*moment*tail_moment
    close("unbounded atomic normalization", sums[-1][0], sums[-2][0])
    if not 0 <= sums[-1][1]-sums[-2][1] <= energy_bound:
        raise AssertionError("unbounded atomic energy tail exceeded analytic bound")
    close("unbounded atomic energy", sums[-1][1], sums[-2][1], atol=energy_bound)
    # At the critical q, each diagonal energy summand stays positive and equal.
    # This finite check challenges the algebra used in the divergence proof.
    critical = 2**(-0.75)
    diagonal = [(1-critical)**2 * critical**(2*n) * time_pair(2.0**n, 2.0**n)[1]
                for n in (0, 20, 80, 160)]
    for value in diagonal:
        close("critical positive diagonal", value, diagonal[0], rtol=1e-12)
    if diagonal[0] <= 0:
        raise AssertionError("critical diagonal vanished")
    print(f"PASS unbounded atomic law: mean={sums[-1][1]/sums[-1][0]:.10f}; "
          f"critical diagonal={diagonal[0]:.10f}")


def run(kernel_factor: float) -> None:
    # Exact finite-kernel algebra checks, without quadrature or roundoff.
    xs = (Fraction(1), Fraction(2), Fraction(5))
    fs = (Fraction(2, 3), Fraction(1, 2), Fraction(1, 5))
    hs = (Fraction(3, 4), Fraction(2, 5), Fraction(1, 9))
    ws = (Fraction(1, 2), Fraction(2, 3), Fraction(1, 3))
    cost = sum(min(x, y)*ws[i]*ws[j]*fs[i]**2*hs[j]/hs[i]
               for i, x in enumerate(xs) for j, y in enumerate(xs))
    base = sum(min(x, y)*ws[i]*ws[j]*fs[i]*fs[j]
               for i, x in enumerate(xs) for j, y in enumerate(xs))
    remainder = sum(min(x, xs[j])*ws[i]*ws[j]*hs[i]*hs[j]
                    * (fs[i]/hs[i]-fs[j]/hs[j])**2
                    for i, x in enumerate(xs) for j in range(i + 1, len(xs)))
    if cost != base + remainder or remainder <= 0:
        raise AssertionError("exact rational square identity failed")
    print("PASS exact rational square identity and positive remainder", flush=True)

    # First challenge the renewal-to-spatial-kernel reduction directly.
    for d in (0.37, 1.0, 2.5):
        for t in (0.25, 1.0, 4.0):
            for x in (0.0, 0.1, 1.0, 3.0):
                numerical = quad(
                    lambda s: math.erf(x / math.sqrt(4 * d * s)) if s else float(x > 0),
                    0, t,
                )
                close("renewal numerator", cycle(x, t, d), numerical)
                f = lambda y: success(y, t, d)
                spatial = kernel_at(f, x, max(x, 14 * math.sqrt(d * t)), d)
                close("half-line kernel factor", kernel_factor * spatial, numerical)
        f, g = atomic((1.0, 4.0), (0.25, 0.75), d)
        close("success at origin", f(0), 1)
        close("cycle at origin", g(0), 0)
        # Finite-difference boundary equation and slope, not symbolic substitutions.
        x, eps = 1.3 * math.sqrt(d), 0.0002 * math.sqrt(d)
        close("minus D g'' = f", -d * (g(x + eps) - 2*g(x) + g(x - eps)) / eps**2,
              f(x), rtol=2e-6)
        close("far slope", (g(30 * math.sqrt(d)) - g(29 * math.sqrt(d))) / math.sqrt(d), 0)
    print("PASS renewal integrals, half-line kernel and boundary conditions")

    d = 1.0
    times, weights = (1.0, 4.0), (0.25, 0.75)
    f, g = atomic(times, weights, d)
    z = math.fsum(
        a*b * 2*math.sqrt(d)/SQRT_PI * (math.sqrt(t)+math.sqrt(s)-math.sqrt(t+s))
        for t, a in zip(times, weights) for s, b in zip(times, weights)
    )
    numerator = math.fsum(
        a*b * 4*math.sqrt(d)/(3*SQRT_PI) * ((t+s)**1.5-t**1.5-s**1.5)
        for t, a in zip(times, weights) for s, b in zip(times, weights)
    )
    close("atomic normalization", quad(lambda x: f(x)**2, 0, 24), z)
    close("atomic half-line coefficient", quad(lambda x: f(x)*g(x), 0, 24), numerator)
    redrawn = quad(lambda x: f(x)**2*g(x), 0, 24) / quad(lambda x: f(x)**3, 0, 24)
    if abs(redrawn - numerator/z) < 0.1:
        raise AssertionError("persistent target accidentally treated as redrawn")
    print(f"PASS atomic normalization Z={z:.10f}; optimal mean={numerator/z:.10f}")
    print(f"PASS fixed-target averaging differs from redrawing: {redrawn:.10f}")

    competitors = [
        ("same law", (f, g)),
        ("sharp 3", atomic((3.0,), (1.0,), d)),
        ("sharp 5", atomic((5.0,), (1.0,), d)),
        ("mixed atoms", atomic((0.5, 8.0), (0.4, 0.6), d)),
        ("exponential", exponential(0.5, d)),
        ("infinite-mean Pareto", (lambda x: pareto_one(x, 1, d)[0],
                                  lambda x: pareto_one(x, 1, d)[1])),
    ]
    for name, (h, gh) in competitors:
        direct = quad(lambda x: f(x)**2 * gh(x) / h(x), 0, 24)
        coarse = box_comparison(f, h, 24, 256, d)
        cost, base, remainder = box_comparison(f, h, 24, 512, d)
        close(name + " square identity", cost, base + remainder, rtol=1e-12)
        close(name + " baseline", base, numerator, rtol=0, atol=0.0004)
        # The square identity is on the box. The full renewal numerator also
        # includes y>24; this matters greatly even for a small-x target when
        # the competitor is heavy-tailed. g_full-g_box is exactly linear in x.
        missing_slope = gh(1) - kernel_at(h, 1, 24, d)
        tail_correction = missing_slope * quad(lambda x: x*f(x)**2/h(x), 0, 24)
        close(name + " renewal versus spatial", cost + tail_correction, direct,
              rtol=0, atol=0.0008)
        if abs(cost - coarse[0]) > 0.002:
            raise AssertionError(name + " mesh refinement failed")
        if name == "same law":
            close("equality remainder", remainder, 0, atol=0)
        elif remainder <= 0:
            raise AssertionError(name + " strict inequality missing")
        print(f"PASS {name}: mean={direct/z:.10f}, box remainder/Z={remainder/z:.10f}")

    # Independent exponential benchmark: the exact optimal mean is 1/rate.
    ef, eg = exponential(0.7, d)
    ez = quad(lambda x: ef(x)**2, 0, 40)
    close("exponential normalization", ez, 1/(2*math.sqrt(0.7/d)))
    close("exponential mean", quad(lambda x: ef(x)*eg(x), 0, 40)/ez, 1/0.7)
    print("PASS exponential benchmark: optimal mean=1/rate")

    # Unbounded restart law, checked independently by direct integration in q=1/sqrt(t).
    for x in (0.001, 0.1, 1.0, 4.0, 16.0):
        pf, pg = pareto_one(x, 1, d)
        close("Pareto success", pf, quad(lambda q: 2*q*math.erfc(x*q/2), 0, 1))
        direct_g = quad(lambda q: 2*q*cycle(x, 1/(q*q), d) if q else 4*x/SQRT_PI, 0, 1)
        close("Pareto numerator", pg, direct_g)
        # For y>=32, f(y)=2/y^2 up to a Gaussian correction below rounding here.
        kernel_g = kernel_at(lambda y: pareto_one(y, 1, d)[0], x, 32, d) + 2*x/32
        close("Pareto spatial tail", pg, kernel_g, rtol=2e-8)
    pf = lambda x: pareto_one(x, 1, d)[0]
    pg = lambda x: pareto_one(x, 1, d)[1]
    tail_start = 32.0
    tail_constant = pg(tail_start) - 2*math.log(tail_start)
    pz = quad(lambda x: pf(x)**2, 0, tail_start) + 4/(3*tail_start**3)
    pn = quad(lambda x: pf(x)*pg(x), 0, tail_start) + (
        2/tail_start * (2*math.log(tail_start) + tail_constant + 2)
    )
    if not 0 < pz < pn < math.inf:
        raise AssertionError("Pareto finite cost/normalization failed")
    for scale in (0.25, 4.0):
        h = lambda x: pareto_one(x, scale, d)[0]
        gh = lambda x: pareto_one(x, scale, d)[1]
        tail = 2/tail_start * (gh(tail_start)/scale + 2)
        cost = quad(lambda x: pf(x)**2 * gh(x)/h(x), 0, tail_start) + tail
        if cost <= pn:
            raise AssertionError("Pareto competing scale improved baseline")
        print(f"PASS Pareto scale {scale:g}: mean={cost/pz:.10f} > {pn/pz:.10f}")
    close("Pareto tail coefficient", pf(32)*32**2, 2)
    close("Pareto 3/4 moment", quad(lambda u: math.exp(-u/4), 0, 100)
          + 4*math.exp(-25), 4)
    print(f"PASS infinite-mean reference: Z={pz:.10f}; mean={pn/pz:.10f}; E[T^.75]=4")

    # These samples witness the mechanisms, NOT infinity by finite computation.
    sharp_f, sharp_g = atomic((1.0,), (1.0,), d)
    values = [pf(x)**2 * sharp_g(x)/sharp_f(x) for x in (12, 18, 24)]
    if not values[2] > values[1] > values[0] > 1e8:
        raise AssertionError("Gaussian versus power-tail divergence diagnostic failed")
    partials = [quad(lambda u: 0.5*math.exp(-u/2)*cycle(1, math.exp(u), d), 0, cap)
                for cap in (8, 16, 24)]
    close("infinite sqrt-moment growth", partials[2] - partials[1], 8/SQRT_PI,
          rtol=0.0003)
    if not partials[2] > partials[1] > partials[0]:
        raise AssertionError("infinite numerator diagnostic failed")
    print("PASS divergence diagnostics: too-short sharp restart; infinite sqrt moment")
    dyadic_check()
    print("PASS all numerical challenges (not a proof or a priority certificate)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-factor", type=float, default=1.0,
                        help="deliberately alter spatial kernel; 2 must fail")
    args = parser.parse_args()
    try:
        run(args.kernel_factor)
    except (AssertionError, ArithmeticError, ValueError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
