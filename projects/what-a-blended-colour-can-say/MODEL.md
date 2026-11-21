# Finite-Palette Weighted-Average Colour Model

This document establishes the exact mathematical model for **What a Blended Colour Can Say**, implemented in `blended_colour.py` over exact rationals (`fractions.Fraction`). See [DISPLAY.md](DISPLAY.md) for M2's display transfer and rational outer-box observation bounds.

## 1. Model Definition and Premises

Let a finite ordered palette consist of $n$ stops with scalar levels $v_1 < \dots < v_n$ and declared linear-channel RGB coordinates

$$c_i = (R_i, G_i, B_i) \in \mathbb{Q}^3 \cap [0, 1]^3, \qquad i \in \{0, \dots, n-1\}.$$

A probability distribution $p = (p_0, \dots, p_{n-1}) \in \Delta^{n-1}$ ($\sum_i p_i = 1,\; p_i \ge 0$) produces the weighted-average colour

$$\bar{c}(p) = \sum_{i=0}^{n-1} p_i c_i \in \mathbb{Q}^3.$$

**Declared scope and limits (Milestone 1):**
- Averaging is linear in the three declared colour channels (matching additive linear-light compositing or pixel-space averaging on linear values).
- M1 deferred encoded sRGB and 8-bit quantization. M2 adds explicit sRGB8 and linear8 observations in [DISPLAY.md](DISPLAY.md), preserving this exact point-colour model.
- The goal is design auditing and legend construction from a known palette, not decoding arbitrary compressed screenshots.

## 2. Affine Dimension and Identifiability

Stack normalization and the three colour channels into $A \in \mathbb{Q}^{4 \times n}$:

$$A = \begin{pmatrix}
1 & 1 & \cdots & 1 \\
R_0 & R_1 & \cdots & R_{n-1} \\
G_0 & G_1 & \cdots & G_{n-1} \\
B_0 & B_1 & \cdots & B_{n-1}
\end{pmatrix}, \qquad
b(y) = \begin{pmatrix} 1 \\ y_R \\ y_G \\ y_B \end{pmatrix}.$$

A distribution $p \in \Delta^{n-1}$ explains target colour $y$ if and only if $A p = b(y)$ and $p \ge 0$. By rank–nullity:

1. **Two-colour palettes ($n = 2$, $c_0 \ne c_1$):** $\operatorname{rank}(A) = 2$ and $\dim(\ker A) = 0$. Every colour on the segment $[c_0, c_1]$ has a **unique** distribution $p$.
2. **Up to four affinely independent stops ($n \le 4$, $\operatorname{rank}(A) = n$):** $\dim(\ker A) = 0$. Every in-gamut blend has a unique barycentric preimage.
3. **1D collinear five-colour ramp ($n = 5$ on a line):** $\operatorname{rank}(A) = 2$, so $\dim(\ker A) = 3$. Even knowing all three RGB channels constrains only one linear moment, leaving a 3-dimensional ambiguity polytope.
4. **Non-coplanar five-colour 3D palette ($n = 5$, $\operatorname{rank}(A) = 4$):** $\dim(\ker A) = 1$. By **Radon's theorem** in $\mathbb{R}^3$, any five points admit an affine dependence $\sum_{i=0}^4 v_i c_i = 0$ with $\sum_{i=0}^4 v_i = 0$, spanning the 1-D kernel. Every feasible fiber $\{p \in \Delta^4 : A p = b(y)\}$ is a closed line segment $\{p_0 + t v : t \in [t_{\min}(y), t_{\max}(y)]\}$.

## 3. Exact Event Bounds and Primal–Dual Certificates

Given an event $E \subseteq \{0, \dots, n-1\}$ (for instance, the high-risk tail $E = \{3, 4\}$ representing $\text{Level} \ge 4$), the sharp lower and upper bounds on $P(E)$ consistent with observed colour $y$ are the exact rational linear programs:

$$P_{\min}(y, E) = \min_{p \ge 0} \sum_{i \in E} p_i \quad \text{s.t. } A p = b(y), \qquad
P_{\max}(y, E) = \max_{p \ge 0} \sum_{i \in E} p_i \quad \text{s.t. } A p = b(y).$$

An independent verifier checks a certificate $(\mu, \lambda, p_{\min}^*, p_{\max}^*)$ without running an LP solver:
1. **Primal feasibility:** $p_{\min}^*, p_{\max}^* \ge 0$, $\mathbf{1}^\top p^* = 1$, $C p^* = y$, and $\sum_{i \in E} p_{\min, i}^* = P_{\min}$, $\sum_{i \in E} p_{\max, i}^* = P_{\max}$.
2. **Dual feasibility:** $\mu^\top A \le \mathbf{1}_E^\top$ and $\lambda^\top A \ge \mathbf{1}_E^\top$ across all $n$ palette stops (each vector $\mu, \lambda \in \mathbb{Q}^4$ defines an affine functional over RGB space).
3. **Zero duality gap:** $\mu^\top b(y) = P_{\min}(y, E)$ and $\lambda^\top b(y) = P_{\max}(y, E)$.

## 4. Exact Unidentifiability Criterion (`[0, 1]`)

An event $E$ is **completely unidentifiable** ($P_{\min} = 0$ and $P_{\max} = 1$) at colour $y$ if and only if

$$y \in \operatorname{conv}(\{c_i : i \in E\}) \cap \operatorname{conv}(\{c_i : i \notin E\}).$$

In the Milestone 1 palette `five_colour_tetra_3d`, stop $c_3$ (`L3 Medium`, `#b1b3ca`) is chosen strictly inside the tetrahedron $\operatorname{conv}(c_1, c_2, c_4, c_5)$:

$$c_3 = \tfrac{1}{5} c_1 + \tfrac{2}{5} c_2 + \tfrac{3}{10} c_4 + \tfrac{1}{10} c_5.$$

Consequently, at the exact stop colour $y = c_3$:
- For $E = \{L4, L5\}$: $P(\text{Level} \ge 4) \in [0, \tfrac{2}{5}]$ (`BOUNDED`: a viewer reading a discrete legend sees "100% L3", yet up to 40% high-level mass can be hidden inside `#b1b3ca`).
- For $E' = \{L3\}$: $P(\text{Level} = 3) \in [0, 1]$ (`UNIDENTIFIABLE`: $p_A = (0,0,1,0,0)$ and $p_B = (\frac{1}{5}, \frac{2}{5}, 0, \frac{3}{10}, \frac{1}{10})$ blend to the exact same `#b1b3ca`).
- By contrast, on an outer boundary blend (`S2`: `conv(L1, L2, L4)`), $P(\text{Level} \ge 4) = \tfrac{3}{5}$ is `EXACT`, and on a near-outer blend (`S3`), $P(\text{Level} \ge 4) \in [\tfrac{1}{2}, \tfrac{3}{5}]$ spans just 10 percentage points—whereas the 1D collinear ramp midpoint (`S5`) widens to $[0, \tfrac{2}{3}]$.
