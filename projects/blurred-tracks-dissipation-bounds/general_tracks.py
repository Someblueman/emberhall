#!/usr/bin/env python3
"""Milestone 2: shutter covariance for general stable 2D linear diffusions.

Latent motion dX = A X dt + sqrt(2) B dW with A any stable real 2x2 matrix
and diffusion matrix Dm = B B^T symmetric positive definite.  Stationary
covariance Sigma solves A Sigma + Sigma A^T + 2 Dm = 0, latent covariance
C(tau) = exp(A tau) Sigma for tau >= 0, and steady-state entropy production
sigma = tr(Dm^{-1} M Sigma M^T) with current-velocity matrix
M = A + Dm Sigma^{-1}.

Same camera as milestone 1 (rectangular shutter eps <= Delta, iid Gaussian
localization variance ell^2).  With U = int_0^eps exp(A u) du,
W = int_0^eps exp(-A v) dv and U2 = int_0^eps (eps - tau) exp(A tau) dtau:

    Gamma_k = exp(A k Delta) U W Sigma / eps^2          (k >= 1)
    Gamma_0 = [U2 Sigma + (U2 Sigma)^T] / eps^2 + ell^2 I
    Gamma_{-k} = Gamma_k^T

U, W, U2 come from augmented matrix exponentials.  Declared class: A stable
with ||A|| Delta <= 50 (scaling-and-squaring range used here), Dm SPD.
Standard library only; matrices are lists of lists.
"""
from __future__ import annotations

import cmath
import math

Mat = list[list[float]]


def zeros(n: int, m: int) -> Mat:
    return [[0.0] * m for _ in range(n)]


def eye(n: int) -> Mat:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def matmul(A: Mat, B: Mat) -> Mat:
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)]
            for i in range(n)]


def transpose(A: Mat) -> Mat:
    return [list(row) for row in zip(*A)]


def add(A: Mat, B: Mat, s: float = 1.0) -> Mat:
    return [[A[i][j] + s * B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def scale(A: Mat, s: float) -> Mat:
    return [[s * x for x in row] for row in A]


def norm_inf(A: Mat) -> float:
    return max(sum(abs(x) for x in row) for row in A)


def expm(A: Mat) -> Mat:
    """Matrix exponential by scaling and squaring with a Taylor series."""
    n = len(A)
    s = max(0, int(math.ceil(math.log2(norm_inf(A) / 0.5)))) if norm_inf(A) > 0.5 else 0
    As = scale(A, 2.0 ** -s)
    E = eye(n)
    term = eye(n)
    for k in range(1, 60):
        term = scale(matmul(term, As), 1.0 / k)
        E = add(E, term)
        if norm_inf(term) < 1e-18:
            break
    for _ in range(s):
        E = matmul(E, E)
    return E


def solve_linear(A: Mat, b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-300:
            raise ValueError("singular system")
        M[col], M[piv] = M[piv], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def inverse2(A: Mat) -> Mat:
    (a, b), (c, d) = A
    det = a * d - b * c
    if det == 0.0:
        raise ValueError("singular 2x2 matrix")
    return [[d / det, -b / det], [-c / det, a / det]]


def stationary_covariance(A: Mat, Dm: Mat) -> Mat:
    """Solve A S + S A^T + 2 Dm = 0 by Kronecker vectorization (4x4)."""
    # unknown vec(S) column-major: (s00, s10, s01, s11)
    K = zeros(4, 4)
    I2 = eye(2)
    for i in range(2):
        for j in range(2):
            for p in range(2):
                for q in range(2):
                    # (A S)_{ij} coeff of S_{pq}: A_{ip} delta_{jq}
                    K[j * 2 + i][q * 2 + p] += A[i][p] * I2[j][q]
                    # (S A^T)_{ij} coeff: delta_{ip} A_{jq}
                    K[j * 2 + i][q * 2 + p] += I2[i][p] * A[j][q]
    rhs = [-2.0 * Dm[0][0], -2.0 * Dm[1][0], -2.0 * Dm[0][1], -2.0 * Dm[1][1]]
    x = solve_linear(K, rhs)
    return [[x[0], x[2]], [x[1], x[3]]]


def int_exp(A: Mat, eps: float) -> Mat:
    """int_0^eps exp(A u) du via augmented exponential."""
    n = len(A)
    M = zeros(2 * n, 2 * n)
    for i in range(n):
        for j in range(n):
            M[i][j] = A[i][j] * eps
        M[i][n + i] = eps
    E = expm(M)
    return [row[n:] for row in E[:n]]


def int_exp_weighted(A: Mat, eps: float) -> Mat:
    """int_0^eps (eps - tau) exp(A tau) dtau via 3-block augmented exp."""
    n = len(A)
    M = zeros(3 * n, 3 * n)
    for i in range(n):
        for j in range(n):
            M[i][j] = A[i][j] * eps
        M[i][n + i] = eps
        M[n + i][2 * n + i] = eps
    E = expm(M)
    return [row[2 * n:] for row in E[:n]]


class GeneralVortex:
    def __init__(self, A: Mat, Dm: Mat):
        self.A = A
        self.Dm = Dm
        self.Sigma = stationary_covariance(A, Dm)

    def latent_cov_matrix(self, tau: float) -> Mat:
        if tau >= 0:
            return matmul(expm(scale(self.A, tau)), self.Sigma)
        return transpose(self.latent_cov_matrix(-tau))

    def dissipation(self) -> float:
        M = add(self.A, matmul(self.Dm, inverse2(self.Sigma)))
        T = matmul(matmul(inverse2(self.Dm), M), matmul(self.Sigma, transpose(M)))
        return T[0][0] + T[1][1]

    def observed_cov_matrix(self, Delta: float, eps: float, ell2: float, k: int) -> Mat:
        if k < 0:
            return transpose(self.observed_cov_matrix(Delta, eps, ell2, -k))
        if k == 0:
            U2S = matmul(int_exp_weighted(self.A, eps), self.Sigma)
            G = scale(add(U2S, transpose(U2S)), 1.0 / eps ** 2)
            G[0][0] += ell2
            G[1][1] += ell2
            return G
        U = int_exp(self.A, eps)
        W = int_exp(scale(self.A, -1.0), eps)
        G = matmul(matmul(U, W), self.Sigma)
        return scale(matmul(expm(scale(self.A, k * Delta)), G), 1.0 / eps ** 2)


def branch_drifts(Phi: Mat, Delta: float, m_values) -> list[tuple[int, Mat]]:
    """Real branch drifts A_m with exp(A_m Delta) = Phi, complex-eigenvalue case.

    Eigenvalues of Phi are r e^{+-i theta}; branch m uses
    log eigenvalues ln r +- i (theta + 2 pi m), same eigenvectors.
    """
    (a, b), (c, d) = Phi
    tr, det = a + d, a * d - b * c
    disc = complex(tr * tr / 4.0 - det, 0.0)
    sq = cmath.sqrt(disc)
    lam1 = tr / 2.0 + sq
    lam2 = tr / 2.0 - sq
    if abs(lam1.imag) < 1e-14:
        raise ValueError("branch_drifts implemented for complex eigenvalue pair only")
    # eigenvector for lam1: (b, lam1 - a) or (lam1 - d, c)
    if abs(b) > abs(c):
        v1 = (complex(b), lam1 - a)
    else:
        v1 = (lam1 - d, complex(c))
    v2 = (v1[0].conjugate(), v1[1].conjugate())
    # P = [v1 v2], invert 2x2 complex
    detP = v1[0] * v2[1] - v2[0] * v1[1]
    Pinv = [[v2[1] / detP, -v2[0] / detP], [-v1[1] / detP, v1[0] / detP]]
    P = [[v1[0], v2[0]], [v1[1], v2[1]]]
    out = []
    for m in m_values:
        mu1 = cmath.log(lam1) + 2j * math.pi * m
        mu2 = cmath.log(lam2) - 2j * math.pi * m
        # L = P diag(mu) Pinv / Delta
        L = [[0j, 0j], [0j, 0j]]
        Dg = [[mu1, 0j], [0j, mu2]]
        for i in range(2):
            for j in range(2):
                L[i][j] = sum(P[i][t] * Dg[t][u] * Pinv[u][j]
                              for t in range(2) for u in range(2)) / Delta
        out.append((m, [[L[i][j].real for j in range(2)] for i in range(2)]))
    return out


FROZEN_GENERAL = {
    "A": [[-1.2, -2.0], [0.8, -0.7]],
    "Dm": [[1.0, 0.3], [0.3, 0.6]],
    "Delta": 0.9,
    "eps": 0.45,
    "ell2": 0.03,
}
