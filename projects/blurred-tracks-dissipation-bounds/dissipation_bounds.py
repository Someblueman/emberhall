#!/usr/bin/env python3
"""Milestone-3 unified certification algorithm and CLI for blurred tracks.

Given observed frame covariances (Gamma_0, Gamma_1, Gamma_2) at one or two
exposures — or a 2D particle track CSV (frame, y1, y2) — this module:

1. Refuses singular / non-stationary Gamma_1 or Phi outside the declared
   stable 2D linear diffusion class (singular_cases).
2. Classifies the propagator Phi = Gamma_2 Gamma_1^{-1} into
   {complex_pair, distinct_real, defective, scalar} (real_logs).
3. Searches compatible continuous-time motions (A, Sigma, Dm, ell^2).
   Complex-log all-m elimination requires explicit exact rational timing;
   irrational/unspecified timing and scalar winding sheets are finite searches.
4. Provides population model-conditional bounds only for complete searches.
   Finite/bootstrap modes calibrate branch diagnostics, not continuous-parameter
   uncertainty: sigma_bounds is withheld and plugin_span is diagnostic only.
   Two-exposure matching currently supports population covariances only.

Standard library only.
"""
from __future__ import annotations

import argparse
import cmath
import csv
from fractions import Fraction
import json
import math
import re
import statistics
import sys

from general_bootstrap import fit_from_covariances
from general_finite_record import (Z975, branch_quantities_general, delta_sds,
                                   empirical_Gamma, simulate_general_frames)
from general_tracks import (FROZEN_GENERAL, GeneralVortex, add, branch_drifts,
                            expm, int_exp, int_exp_weighted, inverse2, matmul,
                            scale, solve_linear, transpose)
from real_logs import classify_phi, family_drift, real_log_candidates
from singular_cases import propagator_from_covariances


def _matrix_max_diff(A, B) -> float:
    return max(abs(A[i][j] - B[i][j]) for i in range(2) for j in range(2))


def _dissipation(A, Sigma, Dm) -> float:
    gv = GeneralVortex.__new__(GeneralVortex)
    gv.A, gv.Sigma, gv.Dm = A, Sigma, Dm
    return gv.dissipation()


def _eig_mags(Phi) -> tuple[float, float]:
    (a, b), (c, d) = Phi
    tr, det = a + d, a * d - b * c
    sq = cmath.sqrt(complex(tr * tr / 4.0 - det))
    return abs(tr / 2.0 + sq), abs(tr / 2.0 - sq)


def _rational_ratio(eps: float, Delta: float, exposure_ratio: Fraction | None):
    """Validate caller-declared exact eps/Delta; never infer it from floats.

    Fraction(1, 3) explicitly declares ideal timing even though its numerical
    evaluation uses floats. A nearby measured ratio is not such a declaration.
    """
    if exposure_ratio is None:
        return None
    if not isinstance(exposure_ratio, Fraction):
        raise ValueError("exposure_ratio must be an explicit fractions.Fraction")
    if not 0 < exposure_ratio <= 1:
        raise ValueError("exposure_ratio must lie in (0, 1]")
    if float(eps) != float(Delta * exposure_ratio):
        raise ValueError("exposure_ratio disagrees with supplied exposure duration")
    return exposure_ratio


def _summary(compatible, *, complete: bool, mode: str) -> dict:
    """Keep searched plug-in values separate from population bounds."""
    sigs = [c["sigma"] for c in compatible if c["sigma"] is not None]
    span = (min(sigs), max(sigs)) if sigs else None
    candidate_status = "none" if not sigs else ("single" if len(sigs) == 1 else "multiple")
    if mode != "population":
        status = "uncertainty_unavailable"
    elif not complete:
        status = "incomplete"
    else:
        status = {"none": "refused", "single": "unique", "multiple": "ambiguous"}[candidate_status]
    return {"status": status, "search_complete": complete,
            "candidate_status": candidate_status, "plugin_span": span,
            "sigma_bounds": span if complete and mode == "population" else None,
            "uncertainty": "population_numerical" if mode == "population" else "unavailable"}


def _refusal(reason: str, **extra) -> dict:
    return {"status": "refused", "reason": reason, "compatible": [],
            "sigma_bounds": None, "plugin_span": None, "search_complete": False,
            "candidate_status": "none", "uncertainty": "unavailable", "caveats": [], **extra}


def _quad_coeffs(ms: list[int], ys: list[float]) -> tuple[float, float, float]:
    def lag(x: float) -> float:
        tot = 0.0
        for i in range(3):
            term = ys[i]
            for j in range(3):
                if i != j:
                    term *= (x - ms[j]) / (ms[i] - ms[j])
            tot += term
        return tot

    a2 = (lag(2.0) - 2.0 * lag(1.0) + lag(0.0)) / 2.0
    a1 = lag(1.0) - lag(0.0) - a2
    return a2, a1, lag(0.0)


def _rational_complex_roots(G0, G1, G2, Delta: float, eps: float, period: int,
                            tol: float, m_window: int) -> tuple[set[int], bool]:
    """Numerical all-m elimination on exact rational residue classes.

    Work in integer k with m = cls + period*k, so rounding never skips a
    distant residue. Enumerate the entire bounded tolerance region. Degenerate
    or impractically wide quadratics fail closed to an incomplete search.
    """
    roots = set(range(-m_window, m_window + 1))
    from general_finite_record import symmetry_residual
    complete = True
    for cls in range(period):
        ys = [symmetry_residual(G0, G1, G2, Delta, eps, cls + period*k)
              for k in (0, 1, 2)]
        if any(y is None or not math.isfinite(y) for y in ys):
            complete = False
            continue
        a2, a1, a0 = _quad_coeffs([0, 1, 2], ys)
        if abs(a2) <= 1e-14 * max(1.0, *(abs(y) for y in ys)):
            # A flat/linear residue needs a separate certified treatment.
            complete = False
            continue
        endpoints = []
        for rhs in (-tol, tol):
            disc = a1*a1 - 4*a2*(a0-rhs)
            if disc >= 0:
                sq = math.sqrt(disc)
                # Stable quadratic roots, including a zero constant term.
                q = -0.5 * (a1 + math.copysign(sq, a1))
                endpoints.extend((q/a2, (a0-rhs)/q) if q else (0.0,))
        if not endpoints:
            continue
        lo, hi = math.floor(min(endpoints))-1, math.ceil(max(endpoints))+1
        if hi-lo > 10000 or max(abs(lo), abs(hi))*period > 10**7:
            complete = False
            continue
        for k in range(lo, hi+1):
            m = cls + period*k
            r = symmetry_residual(G0, G1, G2, Delta, eps, m)
            if r is None or not math.isfinite(r):
                complete = False
            elif abs(r) <= tol*10.0 + 1e-9:
                roots.add(m)
    return roots, complete


def _scalar_compat_residuals(Ac, G0, G1, Phi, eps: float) -> tuple[float, float, float]:
    """Signed compatibility residuals (S_01-S_10, G0_01-P0_01, (G0-P0)_00-(G0-P0)_11)."""
    U = int_exp(Ac, eps)
    W = int_exp(scale(Ac, -1.0), eps)
    S = scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)), eps * eps)
    U2S = matmul(int_exp_weighted(Ac, eps), S)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / (eps * eps))
    return (
        S[0][1] - S[1][0],
        G0[0][1] - P0[0][1],
        (G0[0][0] - P0[0][0]) - (G0[1][1] - P0[1][1]),
    )


def _solve_scalar_sheet(alpha: float, beta_pos: float, G0, G1, Phi, Delta: float, eps: float):
    """Solve s28's 3x3 linear (w,u,v) system for +beta_pos and -beta_pos."""
    def coeffs(t: float):
        fs = [_scalar_compat_residuals(family_drift(alpha, beta_pos, t, phi, Delta),
                                       G0, G1, Phi, eps)
              for phi in (0.0, math.pi / 4.0, math.pi / 2.0)]
        return [
            ((fs[0][i] + fs[2][i]) / 2.0,
             (fs[0][i] - fs[2][i]) / 2.0,
             fs[1][i] - (fs[0][i] + fs[2][i]) / 2.0)
            for i in range(3)
        ]

    t1 = 0.5
    M0, M1 = coeffs(0.0), coeffs(t1)
    w1, sh1 = 2.0 * math.cosh(2.0 * t1), math.sinh(2.0 * t1)
    slope = [(M1[i][0] - M0[i][0]) / (w1 - 2.0) for i in range(3)]
    a0 = [M0[i][0] - 2.0 * slope[i] for i in range(3)]
    bc = [(M1[i][1] / sh1, M1[i][2] / sh1) for i in range(3)]
    L = [[slope[i], bc[i][0], bc[i][1]] for i in range(3)]
    w_star, u_star, v_star = solve_linear(L, [-a0[i] for i in range(3)])
    q_res = u_star * u_star + v_star * v_star - (w_star * w_star - 4.0) / 4.0
    if w_star >= 2.0 - 1e-12:
        return beta_pos, max(w_star, 2.0), u_star, v_star, q_res
    if -w_star >= 2.0 - 1e-12:
        return -beta_pos, max(-w_star, 2.0), -u_star, -v_star, q_res
    return None


def _eval_drift_candidate(label: str, Am, G0, G1, Phi, Delta: float, eps: float):
    U = int_exp(Am, eps)
    W = int_exp(scale(Am, -1.0), eps)
    S = scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)), eps * eps)
    Ss = [[S[0][0], 0.5 * (S[0][1] + S[1][0])],
          [0.5 * (S[0][1] + S[1][0]), S[1][1]]]
    Dm = scale(add(matmul(Am, Ss), matmul(Ss, transpose(Am))), -0.5)
    U2S = matmul(int_exp_weighted(Am, eps), Ss)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / (eps * eps))
    ell_a, ell_b = G0[0][0] - P0[0][0], G0[1][1] - P0[1][1]

    def min_eig(M):
        a, b, d = M[0][0], M[0][1], M[1][1]
        return 0.5 * (a + d) - math.sqrt((0.5 * (a - d)) ** 2 + b * b)

    lam_S, lam_D = min_eig(Ss), min_eig(Dm)
    sig = _dissipation(Am, Ss, Dm) if lam_S > 0.0 and lam_D > 0.0 else None
    return {
        "label": label,
        "A": Am,
        "Sigma": Ss,
        "Dm": Dm,
        "R": S[0][1] - S[1][0],
        "off": G0[0][1] - P0[0][1],
        "eq_ell": ell_a - ell_b,
        "ell": 0.5 * (ell_a + ell_b),
        "lam_S": lam_S,
        "lam_D": lam_D,
        "sigma": sig,
    }


def detrend_frames(frames: list[list[float]], degree: int) -> list[list[float]]:
    """Orthogonal discrete-Legendre polynomial detrending for degrees 0..3."""
    if degree < 0 or degree > 3:
        raise ValueError("detrend degree must be in 0..3")
    n = len(frames)
    if n == 0:
        return []
    tbar = (n - 1) / 2.0
    xs = [t - tbar for t in range(n)]
    basis = [[1.0] * n]
    if degree >= 1:
        basis.append(xs)
    if degree >= 2:
        m2 = sum(x * x for x in xs) / n
        basis.append([x * x - m2 for x in xs])
    if degree >= 3:
        beta = sum(x ** 4 for x in xs) / sum(x * x for x in xs)
        basis.append([x ** 3 - beta * x for x in xs])

    out = [row[:] for row in frames]
    for b in basis:
        bb = sum(v * v for v in b)
        if bb == 0.0:
            continue
        c0 = sum(out[t][0] * b[t] for t in range(n)) / bb
        c1 = sum(out[t][1] * b[t] for t in range(n)) / bb
        for t in range(n):
            out[t][0] -= c0 * b[t]
            out[t][1] -= c1 * b[t]
    return out


def load_csv_track(path: str) -> list[list[float]]:
    """Read consecutive frames at the caller's fixed period Delta.

    Required columns are frame,y1,y2 (additional named columns are allowed).
    Frame labels are nonnegative decimal integers, with any starting label,
    increasing by exactly one per row. Delta is the time between these rows;
    gaps, duplicate labels and reordered rows are rejected, never compressed,
    sorted or interpolated. Missing observations before/after the supplied
    interval cannot be detected without an expected start/end/count.
    At least three finite coordinate pairs are needed for lag-two moments.
    """
    frames = []
    previous = None
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if not {"frame", "y1", "y2"}.issubset(fields):
            raise ValueError("track CSV requires frame,y1,y2 columns")
        if len(fields) != len(set(fields)):
            raise ValueError("track CSV has duplicate column names")
        if any(not name.strip() for name in fields):
            raise ValueError("track CSV has an unnamed column")
        for row in reader:
            line = reader.line_num
            token = (row["frame"] or "").strip()
            if not re.fullmatch(r"[0-9]+", token):
                raise ValueError(f"CSV line {line}: frame must be a nonnegative integer")
            frame = int(token)
            if previous is not None and frame != previous + 1:
                raise ValueError(f"CSV line {line}: frame {frame} must follow {previous} "
                                 "consecutively; missing, duplicate or reordered frames "
                                 "cannot use the fixed frame period")
            if None in row:
                raise ValueError(f"CSV line {line}: too many fields")
            try:
                coordinates = [float(row["y1"]), float(row["y2"])]
            except (TypeError, ValueError) as exc:
                raise ValueError(f"CSV line {line}: y1,y2 must be finite numbers") from exc
            if not all(math.isfinite(x) for x in coordinates):
                raise ValueError(f"CSV line {line}: y1,y2 must be finite numbers")
            frames.append(coordinates)
            previous = frame
    if len(frames) < 3:
        raise ValueError("track CSV needs at least three consecutive frames")
    return frames


def certify_covariances(
    G0, G1, G2, Delta: float, eps: float, *,
    mode: str = "population",
    n_frames: int | None = None,
    m_window: int = 12,
    max_scalar_sheets: int = 5,
    tol: float = 1e-7,
    slack: float = 1e-7,
    bootstrap_reps: int = 24,
    bootstrap_seed: int = 777000,
    exposure_ratio: Fraction | None = None,
) -> dict:
    """Search admissible motions from (G0, G1, G2).

    Population all-m elimination needs exposure_ratio=Fraction(p, q), an
    explicit ideal timing assumption. With unspecified timing or scalar Phi,
    results are incomplete. Finite/bootstrap results supply plug-in branch
    diagnostics only, never a dissipation confidence interval. Tolerances are
    numerical; population bounds are not interval-arithmetic proof enclosures.
    """
    if mode not in ("population", "finite", "bootstrap"):
        raise ValueError("mode must be population, finite or bootstrap")
    if not (0 < eps <= Delta) or not math.isfinite(Delta):
        raise ValueError("require finite 0 < eps <= Delta")
    if not math.isfinite(tol) or tol <= 0 or not math.isfinite(slack) or slack < 0:
        raise ValueError("tol must be positive and slack nonnegative, both finite")
    if m_window < 0 or max_scalar_sheets < 0:
        raise ValueError("search limits must be nonnegative")
    if mode != "population" and (not isinstance(n_frames, int) or n_frames < 3):
        raise ValueError("finite/bootstrap mode requires n_frames >= 3")
    if mode == "bootstrap" and bootstrap_reps < 2:
        raise ValueError("bootstrap mode requires at least two replicates")
    frac = _rational_ratio(eps, Delta, exposure_ratio)
    try:
        Phi = propagator_from_covariances(G1, G2)
    except ValueError as exc:
        return _refusal(str(exc))

    mags = _eig_mags(Phi)
    if max(mags) >= 1.0 or min(mags) <= 0.0:
        return _refusal(f"Phi eigenvalues outside (0, 1): {mags}")

    kind, lams = classify_phi(Phi)
    scale_g = max(1.0, max(abs(G0[i][j]) for i in range(2) for j in range(2)))
    caveats = []
    candidates = []
    complete = False
    if mode != "population":
        caveats.append("Continuous-parameter dissipation uncertainty is unsupported here; plugin_span is not a confidence interval or certified bound.")
        if kind != "complex_pair":
            return _refusal("finite/bootstrap calibration is unsupported for this Phi class",
                            kind=kind, caveats=caveats)

    if kind == "complex_pair":
        if frac is not None and frac.denominator <= 2000 and mode == "population":
            period = frac.denominator // math.gcd(frac.numerator, frac.denominator)
            roots, complete = _rational_complex_roots(G0, G1, G2, Delta, eps,
                                                       period, tol * scale_g, m_window)
            m_list = sorted(roots)
            completeness = (f"all-m rational completeness (eps/Delta={frac}, period {period})"
                            if complete else "incomplete rational residue search")
            if not complete:
                caveats.append("Degenerate, unavailable or excessive residue search; unsearched m remain.")
        else:
            m_list = list(range(-m_window, m_window + 1))
            if frac is None:
                completeness = f"finite window [-{m_window}, {m_window}]"
                caveats.append("No exact rational timing declared: finite-window search cannot exclude unsearched m (including for irrational timing).")
            else:
                completeness = f"finite window [-{m_window}, {m_window}] (declared rational {frac})"
                caveats.append("All-m elimination not used for this mode or denominator; unsearched branches remain.")
        drifts = dict(branch_drifts(Phi, Delta, m_list))
        for m in m_list:
            if m in drifts:
                c = _eval_drift_candidate(f"m={m}", drifts[m], G0, G1, Phi, Delta, eps)
                c["m"] = m
                candidates.append(c)

    elif kind in ("distinct_real", "defective"):
        complete = True
        completeness = f"real-log classification ({kind})"
        rk, payload = real_log_candidates(Phi, Delta)
        if rk == "none":
            return _refusal(payload, kind=kind)
        candidates.append(_eval_drift_candidate("unique_real", payload[0],
                                                G0, G1, Phi, Delta, eps))

    else:  # scalar Phi
        completeness = f"scalar-Phi finite sheet search (|k|<={max_scalar_sheets})"
        caveats.append("Exact reduction within each regular sheet does not exclude unsearched sheets or singular continuous families.")
        lam = lams[0]
        if lam > 0:
            alpha = math.log(lam)
            A0 = family_drift(alpha, 0.0, 0.0, 0.0, Delta)
            candidates.append(_eval_drift_candidate("beta=0", A0, G0, G1, Phi, Delta, eps))
            pos_betas = [2.0 * math.pi * k for k in range(1, max_scalar_sheets + 1)]
        else:
            alpha = math.log(-lam)
            pos_betas = [math.pi * (2 * k + 1) for k in range(0, max_scalar_sheets)]
        for bp in pos_betas:
            try:
                hit = _solve_scalar_sheet(alpha, bp, G0, G1, Phi, Delta, eps)
            except ValueError:
                continue
            if hit is not None:
                b_hit, w_s, u_s, v_s, q_res = hit
                if abs(q_res) <= max(1e-6, tol * scale_g * 100.0):
                    t_s = math.acosh(w_s / 2.0) / 2.0
                    phi_s = math.atan2(v_s, u_s) / 2.0
                    Ac = family_drift(alpha, b_hit, t_s, phi_s, Delta)
                    c = _eval_drift_candidate(f"beta={b_hit/math.pi:+.0f}pi",
                                              Ac, G0, G1, Phi, Delta, eps)
                    c["q_res"] = q_res
                    candidates.append(c)

    # Calibrate tolerances
    if mode in ("finite", "bootstrap") and n_frames is not None and kind == "complex_pair":
        fit = fit_from_covariances(G0, G1, G2, Delta, eps,
                                   [c["m"] for c in candidates if "m" in c])
        if fit is None:
            return _refusal("no positive-definite finite fit in searched window; global compatibility and dissipation uncertainty remain unsupported",
                            kind=kind, caveats=caveats, status="uncertainty_unavailable")
        m_star, _res, fitted = fit
        if mode == "bootstrap":
            rs_boot = []
            for b in range(bootstrap_reps):
                bf = simulate_general_frames(fitted["vortex"], Delta, eps,
                                             fitted["ell2"], n_frames,
                                             seed=bootstrap_seed + b, sub=20)
                bg = [empirical_Gamma(bf, k) for k in (0, 1, 2)]
                q = branch_quantities_general(bg[0], bg[1], bg[2], Delta, eps, m_star)
                if q is not None:
                    rs_boot.append(q["R"])
            if len(rs_boot) < 2:
                return _refusal("too few valid bootstrap replicates for branch calibration",
                                status="uncertainty_unavailable", kind=kind,
                                caveats=caveats + ["Failed bootstrap replicates cannot establish zero calibration error."])
            tau_R = Z975 * statistics.pstdev(rs_boot)
            sds = delta_sds(fitted["vortex"], Delta, eps, fitted["ell2"],
                            ("R", "off", "eq_ell", "ell", "lam_S", "lam_D"), m=m_star)
        else:
            sds = delta_sds(fitted["vortex"], Delta, eps, fitted["ell2"],
                            ("R", "off", "eq_ell", "ell", "lam_S", "lam_D"), m=m_star)
            tau_R = Z975 * sds["R"] / math.sqrt(n_frames)
        # 99% Bonferroni slacks (s19) for auxiliary inequalities
        z99 = 2.5758293035489004
        inv_rn = 1.0 / math.sqrt(n_frames)
        tol_off = z99 * sds["off"] * inv_rn
        tol_eq = z99 * sds["eq_ell"] * inv_rn
        sl_ell = z99 * sds["ell"] * inv_rn
        sl_S = z99 * sds["lam_S"] * inv_rn
        sl_D = z99 * sds["lam_D"] * inv_rn
        elig = [c for c in candidates
                if abs(c["off"]) <= tol_off and abs(c["eq_ell"]) <= tol_eq
                and c["ell"] >= -sl_ell and c["lam_S"] > -sl_S and c["lam_D"] > -sl_D]
        if elig:
            best_r = min(abs(c["R"]) for c in elig)
            compatible = [c for c in elig if abs(c["R"]) <= best_r + tau_R]
        else:
            compatible = []
    else:
        thr = tol * scale_g
        compatible = [
            c for c in candidates
            if abs(c["R"]) <= thr and abs(c["off"]) <= thr
            and abs(c["eq_ell"]) <= thr and c["ell"] >= -slack
            and c["lam_S"] > 0.0 and c["lam_D"] > 0.0
        ]

    return {
        **_summary(compatible, complete=complete, mode=mode),
        "kind": kind,
        "completeness": completeness,
        "compatible": compatible,
        "caveats": caveats,
    }


def certify_two_exposures(
    exp_a: tuple, exp_b: tuple, *, exposure_ratios: tuple = (None, None), **kwargs
) -> dict:
    """Certify jointly across two exposures (G0, G1, G2, Delta, eps).

    Filters exposure-a compatible motions by checking whether each
    reproduces exposure-b's (G0, G1, G2) within tol (breaking both
    complex-log near-aliases and scalar-Phi counterexamples).
    """
    if kwargs.get("mode", "population") != "population":
        return _refusal("two-exposure finite/bootstrap joint uncertainty is unsupported",
                        resolved_by_two_exposures=False)
    if "exposure_ratio" in kwargs:
        raise ValueError("use exposure_ratios=(ratio_a, ratio_b) for two exposures")
    G0a, G1a, G2a, Da, ea = exp_a
    G0b, G1b, G2b, Db, eb = exp_b
    res_a = certify_covariances(G0a, G1a, G2a, Da, ea, exposure_ratio=exposure_ratios[0], **kwargs)
    res_b = certify_covariances(G0b, G1b, G2b, Db, eb, exposure_ratio=exposure_ratios[1], **kwargs)
    tol = kwargs.get("tol", 1e-7)
    # A complete source enumeration suffices; the other exposure is a filter.
    source = res_a
    if not res_a["search_complete"] and res_b["search_complete"]:
        source = res_b
        G0b, G1b, G2b, Db, eb = exp_a
    scale_b = max(1.0, max(abs(G0b[i][j]) for i in range(2) for j in range(2)))
    joint = []
    max_sep = 0.0
    for c in source["compatible"]:
        if c["lam_S"] <= 0.0 or c["lam_D"] <= 0.0:
            continue
        gv = GeneralVortex.__new__(GeneralVortex)
        gv.A, gv.Sigma, gv.Dm = c["A"], c["Sigma"], c["Dm"]
        ell_c = max(0.0, c["ell"])
        err = max(
            _matrix_max_diff(gv.observed_cov_matrix(Db, eb, ell_c, 0), G0b),
            _matrix_max_diff(gv.observed_cov_matrix(Db, eb, ell_c, 1), G1b),
            _matrix_max_diff(gv.observed_cov_matrix(Db, eb, ell_c, 2), G2b),
        )
        if err <= max(1e-5, tol * scale_b * 100.0):
            joint.append(c)
        else:
            max_sep = max(max_sep, err)
    summary = _summary(joint, complete=source["search_complete"], mode="population")
    return {
        **summary,
        "single_a": res_a,
        "single_b": res_b,
        "compatible": joint,
        "resolved_by_two_exposures": summary["status"] == "unique" and
                                     (len(res_a["compatible"]) > 1 or len(res_b["compatible"]) > 1),
        "rejected_separation": max_sep,
        "caveats": [] if source["search_complete"] else ["Both source searches are incomplete; joint filtering cannot establish global uniqueness or exclusion."],
    }


def certify_track_csv(
    path: str, Delta: float, eps: float, detrend_degree: int = 0,
    mode: str = "finite", bootstrap_reps: int = 24,
) -> dict:
    """Fixed-cadence track diagnostics; Delta is the time per consecutive frame.

    See load_csv_track for accepted labels. Continuous uncertainty unsupported.
    """
    if mode not in ("finite", "bootstrap"):
        raise ValueError("a sampled CSV cannot supply exact population covariances")
    frames = load_csv_track(path)
    frames = detrend_frames(frames, detrend_degree)
    Gs = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
    res = certify_covariances(Gs[0], Gs[1], Gs[2], Delta, eps,
                              mode=mode, n_frames=len(frames),
                              bootstrap_reps=bootstrap_reps)
    res["n_frames"] = len(frames)
    res["detrend_degree"] = detrend_degree
    return res


def _run_self_checks() -> int:
    """Small runnable population examples and finite-contract witnesses."""
    failures = []

    def check(name, ok):
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            failures.append(name)

    g = GeneralVortex([[-1., -3.9], [3.9, -1.]], [[1., 0.], [0., 1.]])
    Gs = [g.observed_cov_matrix(1., .5, .04, k) for k in range(3)]
    exact = certify_covariances(*Gs, 1., .5, exposure_ratio=Fraction(1, 2))
    check("explicit rational population example retains sigma=30.42",
          exact['status'] == 'unique' and abs(exact['sigma_bounds'][0]-30.42) < 1e-6)
    unspecified = certify_covariances(*Gs, 1., .5)
    check("float timing alone cannot certify all-m completeness",
          unspecified['status'] == 'incomplete' and unspecified['sigma_bounds'] is None)
    f = FROZEN_GENERAL
    general = GeneralVortex(f['A'], f['Dm'])
    rat = [general.observed_cov_matrix(.9, .3, f['ell2'], k) for k in range(3)]
    r = certify_covariances(*rat, .9, .3, exposure_ratio=Fraction(1, 3))
    check("exact one-third population example preserves true dissipation",
          r['status'] == 'unique' and abs(r['sigma_bounds'][0]-general.dissipation()) < 1e-6)
    frames = simulate_general_frames(general, f['Delta'], f['eps'], f['ell2'],
                                     1000, seed=12345, sub=20)
    film = [empirical_Gamma(frames, k) for k in range(3)]
    r = certify_covariances(*film, f['Delta'], f['eps'], mode='finite', n_frames=1000)
    check("finite singleton is diagnostic, not a dissipation bound",
          r['status'] == 'uncertainty_unavailable' and r['sigma_bounds'] is None
          and abs(r['plugin_span'][0]-11.4818297137227) < 1e-6)
    A = family_drift(-1.051604554356144, 2*math.pi, .916683, 3.077661, 1.)
    scalar = GeneralVortex(A, [[.195454, .216758], [.216758, .780373]])
    a = (*[scalar.observed_cov_matrix(1., .691196, .2, k) for k in range(3)], 1., .691196)
    b = (*[scalar.observed_cov_matrix(1., .5, .2, k) for k in range(3)], 1., .5)
    r = certify_two_exposures(a, b, tol=1e-6)
    check("second exposure separates tested scalar rivals without a global claim",
          r['status'] == 'incomplete' and len(r['compatible']) == 1
          and r['sigma_bounds'] is None and not r['resolved_by_two_exposures'])
    print(f"{len(failures)} failures")
    return int(bool(failures))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Population examples and finite-track plug-in diagnostics (uncertainty unsupported).")
    parser.add_argument("--csv", help="2D track CSV: frame,y1,y2; consecutive nonnegative integer frames required")
    parser.add_argument("--Delta", type=float, default=1.0, help="Frame period Delta")
    parser.add_argument("--eps", type=float, default=0.5, help="Shutter exposure eps")
    parser.add_argument("--detrend", type=int, default=0, choices=[0, 1, 2, 3],
                        help="Polynomial detrending degree (0..3)")
    parser.add_argument("--mode", choices=["finite", "bootstrap"],
                        default="finite", help="Tolerance mode for --csv")
    parser.add_argument("--bootstrap", type=int, default=24, help="Bootstrap replicates")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary for --csv")
    args = parser.parse_args(argv)

    if not args.csv:
        return _run_self_checks()

    try:
        res = certify_track_csv(args.csv, args.Delta, args.eps,
                            detrend_degree=args.detrend,
                            mode=args.mode, bootstrap_reps=args.bootstrap)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        safe = {
            "status": res["status"],
            "kind": res.get("kind"),
            "reason": res.get("reason"),
            "n_frames": res["n_frames"],
            "detrend_degree": res["detrend_degree"],
            "completeness": res.get("completeness"),
            "search_complete": res["search_complete"],
            "uncertainty": res["uncertainty"],
            "candidate_status": res["candidate_status"],
            "plugin_span": res["plugin_span"],
            "sigma_bounds": res["sigma_bounds"],
            "compatible_branches": [
                {"label": c["label"], "sigma": c["sigma"], "ell2": c["ell"], "R": c["R"]}
                for c in res["compatible"]
            ],
            "caveats": res["caveats"],
        }
        print(json.dumps(safe, indent=2))
    else:
        print(f"Track: {args.csv} (N={res['n_frames']}, Delta={args.Delta}, eps={args.eps}, detrend={args.detrend})")
        print(f"Status: {res['status']} | Phi kind: {res.get('kind')} | {res.get('completeness')}")
        if res.get("reason"):
            print(f"Reason: {res['reason']}")
        if res["sigma_bounds"] is not None:
            lo, hi = res["sigma_bounds"]
            print(f"Certified dissipation bounds: [{lo:.4f}, {hi:.4f}]")
        if res["plugin_span"] is not None:
            print(f"Searched plug-in span (not a confidence interval): {res['plugin_span']}")
        for c in res["compatible"]:
            print(f"  branch {c['label']}: sigma={c['sigma']:.4f}, ell2={c['ell']:.4f}, R={c['R']:.3e}")
        for cav in res["caveats"]:
            print(f"  CAVEAT: {cav}")
    return 0 if res["sigma_bounds"] is not None else 1


if __name__ == "__main__":
    sys.exit(main())
