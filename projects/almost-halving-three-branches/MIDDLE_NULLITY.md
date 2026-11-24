# Complete all-scale classification of the middle operator, left-right kernel duality, and seed-free compatibility equalities

Sundew, 24 November 2026. Continuation of `FULL_SHORTER_COUPLING.md` (Tern,
`45a6638` / `71e2f45`) and `AFFINE_MIDDLE_COMPATIBILITY.md` (Mallow, `f3d3e60`
/ `7e7a9beb`) on project `small-after-sum-20261120` (task
`fern-tripod-middle-nullity-20261124`). Priority remains provisional. Owns only
`MIDDLE_NULLITY.md`, `middle_nullity.py`, and `test_middle_nullity.py`. No
dependency source is copied or republished here.

## Main theorem (all-scale kernel, rank, and compatibility for `0 <= h <= 2t - 2`)

For every integer $t \ge 1$ and every hole parameter $0 \le h \le 2t - 2$ on
$T(99t, 79t, 23t)$ with holes $H = \{(1, 99t), (1, h)\}$ (interpreting $h = 0$
as the omitted centre $(0, 0)$), let $M(t, h) \in \mathbb{Z}^{5t \times 5t}$ be
the exact middle operator on relative coordinates $i \in \{1, \dots, 5t\}$
($z_i = w_{13t + i}$),

$$(M(t, h) z)_i = v_i - v_{i + D} - v_{i + D + h} + v_{i + D + h + 1} = b_i \qquad (1 \le i \le 5t), \tag{1}$$

where $D = 3t + 1$, $v_k = z_k$ for $1 \le k \le 5t$, and
$v_k = -z_{10t + 1 - k}$ for $5t + 1 \le k \le 10t$.

Set $g_1 := \gcd(3t, h + 1)$ and, for $h \ge 1$, $g_2 := \gcd(3t + 2, h)$. Let
$\nu_2(n)$ denote the $2$-adic valuation of $n$. Then:

1. **Exact rational nullity and rank.** For every $t \ge 1$ and
   $0 \le h \le 2t - 2$,
   $$\dim \ker_{\mathbb{Q}} M(t, h) = \dim \operatorname{coker}_{\mathbb{Q}} M(t, h) = d_1(t, h) + d_2(t, h), \tag{2}$$
   where
   $$d_1(t, h) = \left\lfloor \frac{\gcd(3t, h + 1)}{2} \right\rfloor, \qquad d_2(t, h) = \left\lfloor \frac{\gcd(3t + 2, 2h) - \gcd(3t + 2, h)}{2} \right\rfloor = \begin{cases} \lfloor g_2 / 2 \rfloor & \text{if } h \ge 1 \text{ and } \nu_2(3t + 2) > \nu_2(h), \\ 0 & \text{otherwise.} \end{cases} \tag{3}$$
   Equivalently, $\operatorname{rank}_{\mathbb{Q}} M(t, h) = 5t - d_1(t, h) - d_2(t, h)$
   and the $(5t) \times (2h + 2)$ reduced seed operator $C = M(t, h) T$ has
   $\operatorname{rank}_{\mathbb{Q}} C = (2h + 2) - d_1(t, h) - d_2(t, h)$.

2. **Explicit $\{-1, 0, +1\}$-valued basis of $\ker M(t, h)$.**
   - **Type-I ($g_1$-periodic) basis ($d_1(t, h)$ vectors):** For each residue
     $r \in \{0, \dots, g_1 - 1\}$ with $r < r' := (10t + 1 - r) \bmod g_1$,
     $$z^{(1, r)}_i := \mathbf{1}_{i \equiv r \pmod{g_1}} - \mathbf{1}_{i \equiv r' \pmod{g_1}} \qquad (1 \le i \le 5t). \tag{4}$$
   - **Type-II ($g_2$-antiperiodic) basis ($d_2(t, h)$ vectors, active when
     $h \ge 1$ and $\nu_2(3t + 2) > \nu_2(h)$):** For each residue
     $r \in \{0, \dots, g_2 - 1\}$ with $r < r' := (10t + 1 - r) \bmod g_2$,
     put $q_2(r) := (10t + 1 - r - r') / g_2$ and define
     $$z^{(2, r)}_i := \begin{cases} (-1)^{(i - r)/g_2} & \text{if } i \equiv r \pmod{g_2}, \\ (-1)^{q_2(r) + 1 + (i - r')/g_2} & \text{if } i \equiv r' \pmod{g_2}, \\ 0 & \text{otherwise} \end{cases} \qquad (1 \le i \le 5t). \tag{5}$$
   The $d_1(t, h) + d_2(t, h)$ vectors $\{z^{(1, r)}\} \cup \{z^{(2, r)}\}$ are
   linearly independent and form an exact basis of $\ker_{\mathbb{Q}} M(t, h)$.

3. **Left-right kernel duality and explicit compatibility equalities.** Define
   the boundary-folding linear operator
   $\mathcal{L} = L_{t, h} : \mathbb{Q}^{5t} \to \mathbb{Q}^{5t}$ by
   $$(\mathcal{L} z)_i := \begin{cases} 0 & (1 \le i \le 2t - h - 2), \\ z_{5t} & (i = 2t - h - 1), \\ z_{5t - 1 - r} - z_{5t - r} & (i = 2t - h + r,\,\, 0 \le r \le h - 1), \\ z_i & (2t \le i \le 5t). \end{cases} \tag{6}$$
   Then $L_{t, h}$ satisfies the global operator symmetry identity
   $$L_{t, h}^T M(t, h) = M(t, h)^T L_{t, h} \quad \text{on } \mathbb{Q}^{5t \times 5t}, \tag{7}$$
   and restricts to a vector-space isomorphism
   $$\mathcal{L}\big|_{\ker M(t, h)} : \ker_{\mathbb{Q}} M(t, h) \stackrel{\sim}{\longrightarrow} \ker_{\mathbb{Q}}\bigl(M(t, h)^T\bigr). \tag{8}$$
   Consequently, the $d_1(t, h) + d_2(t, h)$ integer weight vectors
   $w^{(m, r)} := \mathcal{L}(z^{(m, r)})$ form an exact basis of
   $\ker_{\mathbb{Q}}(M(t, h)^T)$. An arbitrary rational forcing vector
   $b \in \mathbb{Q}^{5t}$ belongs to $\operatorname{im} M(t, h)$ **if and only
   if** it satisfies the $d_1(t, h) + d_2(t, h)$ seed-free linear compatibility
   equalities
   $$\bigl(w^{(m, r)}\bigr)^T b = \sum_{i = 2t - h - 1}^{5t} w^{(m, r)}_i b_i = \sum_{i = 2t}^{5t} z^{(m, r)}_i \tilde{b}_i = 0, \tag{9}$$
   where $\tilde{b}_i = b_i$ for $2t \le i \le 5t - h - 1$,
   $\tilde{b}_{5t - h} = b_{5t - h} + b_{2t - 1}$ (when $h \ge 1$, or
   $\tilde{b}_{5t} = b_{5t} + b_{2t - 1}$ when $h = 0$),
   $\tilde{b}_{5t - r} = b_{5t - r} - b_{2t - h + r} + b_{2t - h - 1 + r}$ for
   $1 \le r \le h - 1$, and
   $\tilde{b}_{5t} = b_{5t} - b_{2t - h} + b_{2t - h - 1}$ (for $h \ge 1$).

4. **All-scale invertibility at $h = 19$ on the resistant family.** For
   $h = 19$ ($t \ge 11$), $h + 1 = 20$ and $h = 19$ is prime, so
   $$d_1(t, 19) = \left\lfloor \frac{\gcd(3t, 20)}{2} \right\rfloor, \qquad d_2(t, 19) = \begin{cases} 9 & \text{if } t \equiv 12 \pmod{38}, \\ 0 & \text{otherwise.} \end{cases} \tag{10}$$
   In particular, $M(t, 19)$ is invertible ($\dim \ker M(t, 19) = 0$,
   $\operatorname{rank} C = 40$) if and only if $\gcd(t, 10) = 1$ and
   $t \not\equiv 12 \pmod{38}$. Because every resistant scale
   $t = 2660 k + 1$ ($k \ge 1$) satisfies $t \equiv 1 \pmod{10}$ and is odd,
   $M(2660 k + 1, 19)$ is invertible at **every** resistant scale $k \ge 1$.

**Scope and limitations.** Invertibility or compatibility of $M(t, h)$ concerns
only the $5t$ middle shell rows $92t + 2 \le e \le 97t + 1$ for the hole pair
$\{(1, 99t), (1, h)\}$ with $0 \le h \le 2t - 2$. When $\dim \ker M(t, h) > 0$
and $b \in \operatorname{im} M(t, h)$, a nonliteral particular solution does
**not** exclude literal $\{-1, +1\}$ solutions in the affine coset
$z_{\text{part}} + \ker M(t, h)$. Even when $M(t, h)$ is invertible and produces
a literal middle vector, full first-arm literal feasibility, global balance,
unused shell rows, hole parameters $h \ge 2t - 1$, and all other hole placements
remain separate open requirements. The universal tripod milestone remains open.

---

## Complete proof

The $h = 0$ case is proved in `AFFINE_MIDDLE_COMPATIBILITY.md` and matches (3)
since $g_1 = \gcd(3t, 1) = 1$ and $d_1(t, 0) = d_2(t, 0) = 0$. Assume
$1 \le h \le 2t - 2$.

### 1. Lower-bound proof: Type-I and Type-II kernel basis and linear independence

Let $S$ denote the forward shift $(S v)_k = v_{k + 1}$. On the extended
antisymmetric vector $v = (v_1, \dots, v_{10t})$ with $v_{10t + 1 - k} = -v_k$,
all four indices of (1) for $1 \le i \le 5t$ lie in $\{1, \dots, 10t\}$ because
$5t + D + h + 1 = 8t + h + 2 \le 10t$. Thus $(M(t, h) z)_i = (P(S) v)_i$ where
$P(S) = 1 - S^{3t + 1} - S^{3t + 1 + h} + S^{3t + 2 + h}$. In $\mathbb{Z}[S]$,
$P(S)$ admits two exact factorizations:

$$\begin{aligned}
P(S) &= (1 - S^{3t + 1})(1 - S^{h + 1}) + S^{h + 1}(1 - S^{3t}), \\
P(S) &= (1 - S^{3t + 1})(1 + S^h) - S^h(1 - S^{3t + 2}).
\end{aligned} \tag{11}$$

- **Type-I vectors:** Every $z^{(1, r)}$ in (4) extends by the same formula to a
  $g_1$-periodic sequence $v^{(1, r)}$ on $\{1, \dots, 10t\}$. Because
  $r' \equiv 10t + 1 - r \pmod{g_1}$, reflection exchanges $k \equiv r$ and
  $10t + 1 - k \equiv r' \pmod{g_1}$, so $v^{(1, r)}_{10t + 1 - k} = -v^{(1, r)}_k$.
  Since $g_1 \mid (h + 1)$ and $g_1 \mid 3t$, both $1 - S^{h + 1}$ and
  $1 - S^{3t}$ annihilate $v^{(1, r)}$, so the first factorization in (11)
  gives $M(t, h) z^{(1, r)} = 0$. The involution $r \mapsto (10t + 1 - r) \bmod g_1$
  on $\mathbb{Z}/g_1\mathbb{Z}$ has $1$ fixed point when $g_1$ is odd and $0$
  fixed points when $g_1$ is even (since $2 \mid g_1 \implies 2 \mid 3t \implies t$
  is even, so $10t + 1$ is odd and $2r \equiv 10t + 1 \pmod{g_1}$ has no
  solution). In both parities there are exactly $d_1(t, h) = \lfloor g_1 / 2 \rfloor$
  non-fixed pairs $r < r'$.

- **Type-II vectors:** Suppose $\nu_2(3t + 2) > \nu_2(h)$ and put
  $g_2 = \gcd(3t + 2, h)$. Then $\nu_2(g_2) = \nu_2(h)$, so $h / g_2$ is **odd**
  while $(3t + 2) / g_2$ is **even**. Every $z^{(2, r)}$ in (5) extends by the
  same formula to a $g_2$-antiperiodic sequence $v^{(2, r)}$ on
  $\{1, \dots, 10t\}$ ($v^{(2, r)}_{k + g_2} = -v^{(2, r)}_k$). For
  $k = m g_2 + r$, we have
  $10t + 1 - k = (q_2(r) - m) g_2 + r'$, so
  $v^{(2, r)}_{10t + 1 - k} = (-1)^{q_2(r) + 1 + q_2(r) - m} = -(-1)^m = -v^{(2, r)}_k$,
  and by symmetry the same holds for $k \equiv r' \pmod{g_2}$. Because
  $h / g_2$ is odd and $(3t + 2) / g_2$ is even,
  $v^{(2, r)}_{k + h} = (-1)^{h / g_2} v^{(2, r)}_k = -v^{(2, r)}_k$ and
  $v^{(2, r)}_{k + 3t + 2} = (-1)^{(3t + 2)/g_2} v^{(2, r)}_k = +v^{(2, r)}_k$.
  Thus both $1 + S^h$ and $1 - S^{3t + 2}$ annihilate $v^{(2, r)}$, and the
  second factorization in (11) gives $M(t, h) z^{(2, r)} = 0$. Since
  $\nu_2(3t + 2) > 0$, $t$ is even and $10t + 1$ is odd; thus
  $r \mapsto (10t + 1 - r) \bmod g_2$ has $0$ fixed points when $g_2$ is even
  and $1$ fixed point $r_0$ when $g_2$ is odd, leaving in both parities exactly
  $d_2(t, h) = \lfloor g_2 / 2 \rfloor$ non-fixed pairs $r < r'$.

- **Linear independence:** Within Type-I, the $d_1(t, h)$ vectors $z^{(1, r)}$
  have disjoint supports on $\{1, \dots, g_1\} \subseteq \{1, \dots, 5t\}$.
  Within Type-II, the $d_2(t, h)$ vectors $z^{(2, r)}$ have disjoint supports on
  $\{1, \dots, g_2\} \subseteq \{1, \dots, 5t\}$. Finally, suppose
  $z \in \operatorname{span}\{z^{(1, r)}\} \cap \operatorname{span}\{z^{(2, r)}\}$.
  Then $z_{i + g_1} = z_i$ and $z_{i + g_2} = -z_i$. Since
  $\gcd(g_1, g_2) \mid \gcd(h + 1, h) = 1$, Bézout coefficients
  $\alpha g_1 + \beta g_2 = 1$ give $z_{i + 1} = (-1)^\beta z_i$. If $g_2$ is
  even, $-z_i = z_{i + g_2} = ((-1)^\beta)^{g_2} z_i = z_i \implies z = 0$. If
  $g_2$ is odd, then $z_i = c (-1)^i$; however, every non-fixed paired vector
  $z^{(2, r)}$ ($r < r'$) has $z^{(2, r)}_i = 0$ on the unique fixed residue
  $i \equiv r_0 \pmod{g_2}$, whereas $(-1)^i \ne 0$ there, forcing $c = 0$.
  Hence $\operatorname{span}\{z^{(1, r)}\} \cap \operatorname{span}\{z^{(2, r)}\} = \{0\}$
  and $\dim \ker_{\mathbb{Q}} M(t, h) \ge d_1(t, h) + d_2(t, h)$.

### 2. Block LDU decomposition, Schur complement symmetry, and left-right duality

Partition $\{1, \dots, 5t\}$ into the lower block
$I_L = \{1, \dots, 2t - h - 2\}$, the straddling block
$I_S = \{2t - h - 1, \dots, 2t - 1\}$ (size $h + 1$), and the upper block
$I_U = \{2t, \dots, 5t\}$ (size $3t + 1$).

- For $i \in I_L$, all shifted indices $i + D, i + D + h, i + D + h + 1$ lie in
  $\{3t + 2, \dots, 5t\} \subseteq I_U$. No row in $I_S \cup I_U$ references
  $z_k$ for $k \in I_L$.
- For $i = 2t - 1 - r \in I_S$ ($0 \le r \le h$), $i + D = 5t - r \in I_U$ and
  $i + D + h + 1 = 5t + h + 1 - r > 5t$ (reflecting to $5t - h + r \in I_U$),
  while $i + D + h = 5t + h - r$ is $> 5t$ for $0 \le r \le h - 1$ (reflecting
  to $5t - h + 1 + r \in I_U$) and equals $5t \in I_U$ at $r = h$. Thus the
  $h + 1$ straddling rows are
  $$\begin{aligned}
  S_{2t - 1 - r}(z) &= z_{2t - 1 - r} - z_{5t - r} - z_{5t - h + r} + z_{5t - h + 1 + r} \qquad (0 \le r \le h - 1), \\
  S_{2t - h - 1}(z) &= z_{2t - h - 1} - 2 z_{5t} - z_{5t - h}.
  \end{aligned} \tag{12}$$
- For $i \in I_U$ ($2t \le i \le 5t$, $j = 7t - i \in I_U$), all three shifted
  indices exceed $5t$, giving
  $$E_i(z) = z_i + z_{7t - i} + z_{7t - i - h} - z_{7t - i - h - 1}. \tag{13}$$
  Restricted to columns $k \in I_U$, the upper submatrix $M_{U, U}$ has entries
  $$(M_{U, U})_{i, k} = \mathbf{1}_{i = k} + \mathbf{1}_{i + k = 7t} + \mathbf{1}_{i + k = 7t - h} - \mathbf{1}_{i + k = 7t - h - 1} = (M_{U, U})_{k, i}, \tag{14}$$
  which is **symmetric** on $I_U \times I_U$. The coupling block $M_{U, S}$ is
  supported only on the top $h + 1$ rows $I_{\text{top}} = \{5t - h, \dots, 5t\}$,
  where $7t - i - h$ or $7t - i - h - 1$ falls in $I_S$.

Therefore $M(t, h)$ has the block form
$$M(t, h) = \begin{pmatrix} I_{2t - h - 2} & 0 & M_{L, U} \\ 0 & I_{h + 1} & M_{S, U} \\ 0 & M_{U, S} & M_{U, U} \end{pmatrix}. \tag{15}$$
Notice that the operator $\mathcal{L} = L_{t, h}$ in (6) is precisely
$L_{t, h} = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & -M_{U, S}^T \\ 0 & 0 & I_{3t + 1} \end{pmatrix}$.
Direct multiplication on $I_{\text{top}} \times I_{\text{top}}$ from (12) and
(13) verifies that $M_{U, S} M_{S, U}$ is symmetric: for $0 \le r, q \le h$,
both $(M_{U, S} M_{S, U})_{5t - r, 5t - q}$ and its transpose equal the
coefficient of $z_{5t - q}$ in $\delta_{2t - h + r}$ (for $r < h$) or
$-z_{2t - 1}$ (for $r = h$) expanded via (12). Since both $M_{U, U}$ and
$M_{U, S} M_{S, U}$ are symmetric, the Schur complement
$H_{t, h} := M_{U, U} - M_{U, S} M_{S, U}$ is **symmetric** on $I_U \times I_U$,
and
$$L_{t, h}^T M(t, h) = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \\ 0 & 0 & H_{t, h} \end{pmatrix} = \bigl(L_{t, h}^T M(t, h)\bigr)^T = M(t, h)^T L_{t, h}. \tag{16}$$
This proves (7). If $z \in \ker M(t, h)$, then
$M(t, h)^T L_{t, h} z = L_{t, h}^T M(t, h) z = 0$, so
$\mathcal{L}(z) \in \ker(M(t, h)^T)$. If $\mathcal{L}(z) = 0$ for
$z \in \ker M(t, h)$, then $z_U = 0$, whence $z_S = -M_{S, U} z_U = 0$ and
$z_L = -M_{L, U} z_U = 0$. Since $\dim \ker M(t, h) = \dim \ker(M(t, h)^T)$,
(8) and the exact compatibility criterion (9) follow immediately.

### 3. Upper-bound proof: every vector in $\ker M(t, h)$ lies in $V_1 + V_2$

Let $z \in \ker M(t, h)$. As shown in `FULL_SHORTER_COUPLING.md` (12),
$\delta_i = z_i - z_{i - 1}$ satisfies the homogeneous recurrence
$\delta_i + \delta_{i - h} - \delta_{i - h - 1} - \delta_{i - 2h - 1} = 0$ for
$2t + h + 1 \le i \le 5t$. Summing once shows that
$$z_i + z_{i - h} - z_{i - h - 1} - z_{i - 2h - 1} = \kappa := z_{2t + h} + z_{2t} - z_{2t - 1} - z_{2t - h - 1} \qquad (2t + h \le i \le 5t). \tag{17}$$
Extend $z_i$ to all $i \in \mathbb{Z}$ by the invertible relation (17), and set
$\xi_i := z_i + z_{i - h}$ and $\eta_i := z_i - z_{i - h - 1}$ for all
$i \in \mathbb{Z}$. Then (17) is equivalent to the two first-order step rules
$$\xi_{i + h + 1} = \xi_i + \kappa, \qquad \eta_{i + h} = \kappa - \eta_i \qquad (\forall\, i \in \mathbb{Z}), \tag{18}$$
while their sum gives the telescoping reconstruction identity
$$\xi_{i - 1} + \eta_i = (z_{i - 1} + z_{i - h - 1}) + (z_i - z_{i - h - 1}) = z_i + z_{i - 1} \qquad (\forall\, i \in \mathbb{Z}). \tag{19}$$

Now use the $2h + 2$ boundary equations $S_{2t - h - 1}(z) = \dots = S_{2t - 1}(z) = 0$
from (12) and $E_{5t - h}(z) = \dots = E_{5t}(z) = 0$ from (13). Writing
$Y_q := z_{5t - h + q}$ ($0 \le q \le h$) for the top block and
$X_p := z_{2t - h - 1 + p}$ ($0 \le p \le 2h + 1$) for the seed, (12) and (13)
express the entire seed $X = \Psi_h Y$ in terms of $Y$:
$$X_0 = Y_0 + 2 Y_h, \qquad X_p = Y_p + Y_{h - p} - Y_{h - p + 1} \quad (1 \le p \le h), \tag{20}$$
$$X_{h + 1 + r} + X_{r + 1} - X_r = -Y_{h - r} \qquad (0 \le r \le h). \tag{21}$$
From (20)–(21) at $r = h$, $X_{2h + 1} + X_{h + 1} - X_h = -Y_0$, so
$\kappa = -Y_0 - X_0 = -2(Y_0 + Y_h)$. Grouping the left side of (21) first as
$\xi_{2t + r} - X_r = -Y_{h - r}$ and second as
$\eta_{2t + r} + X_{r + 1} = -Y_{h - r}$ cancels $Y_{h - r}$ identically against
(20), yielding the exact symmetries on the seed window:
$$\begin{aligned}
\xi_{2t} &= Y_0 + Y_h = -\frac{\kappa}{2}, \qquad \xi_{2t + r} = Y_r - Y_{h + 1 - r} = -\xi_{2t + h + 1 - r} \quad (1 \le r \le h), \\
\eta_{2t + h - 1} &= -(Y_0 + Y_h) = \frac{\kappa}{2}, \qquad \eta_{2t + s} = -(Y_{s + 1} + Y_{h - 1 - s}) = \eta_{2t + h - 2 - s} \quad (0 \le s \le h - 2).
\end{aligned} \tag{22}$$
Propagating (22) to all $a \in \mathbb{Z}$ via (18) gives the global reflection
identities
$$\xi_{2t + a} + \xi_{2t - a} = -\kappa, \qquad \eta_{2t + a} + \eta_{2t - 2 - a} = \kappa \qquad (\forall\, a \in \mathbb{Z}). \tag{23}$$

Next, for $2t \le i \le 5t$ and $j = 7t - i$, combine $E_i(z) = 0$ with
$E_{i - h}(z) = 0$ and $E_{i - h - 1}(z) = 0$ using (17):
$$\begin{aligned}
0 &= E_i(z) + E_{i - h}(z) = \xi_i + \xi_{7t - i} + \kappa = \xi_{7t - i} - \xi_{4t - i} \qquad (2t + h \le i \le 5t), \\
0 &= E_i(z) - E_{i - h - 1}(z) = \eta_i + \eta_{7t - i} - \kappa = \eta_{7t - i} - \eta_{4t - 2 - i} \qquad (2t + h + 1 \le i \le 5t),
\end{aligned} \tag{24}$$
where the right-hand equalities substitute (23) at $a = i - 2t$. Since
$h \le 2t - 2$, the interval $[2t + h, 5t]$ has length
$3t - h + 1 = (h + 1) + (3t - 2h) \ge h + 4 > h + 1$ (a full period of the
$(h + 1)$-periodic sequence $\xi_{k + 3t} - \xi_k$), and $[2t + h + 1, 5t]$ has
length $3t - h \ge h + 3 > h$ (a full antiperiod of $\eta_{k + 3t + 2} - \eta_k$).
Therefore $\xi_{k + 3t} = \xi_k$ and $\eta_{k + 3t + 2} = \eta_k$ hold for
**all** $k \in \mathbb{Z}$.

Summing $\xi_{k + 3t} - \xi_k = 0$ over $h + 1$ consecutive indices yields
$3t \kappa = 0$, hence $\kappa = 0$. With $\kappa = 0$:
- $\xi_k$ is both $(h + 1)$-periodic and $3t$-periodic, hence $g_1$-periodic
  with $g_1 = \gcd(3t, h + 1)$, and satisfies $\xi_{4t - k} = -\xi_k$ by (23).
  The space $\mathcal{X}_{t, h}$ of $g_1$-periodic sequences satisfying
  $\xi_{4t - k} = -\xi_k$ (which fixes $k \equiv 2t \pmod{g_1}$, where
  $\xi_{2t} = 0$) has dimension $\lfloor (g_1 - 1)/2 \rfloor$.
- $\eta_k$ is both $h$-antiperiodic ($\eta_{k + h} = -\eta_k$) and
  $(3t + 2)$-periodic ($\eta_{k + 3t + 2} = \eta_k$), and satisfies
  $\eta_{4t - 2 - k} = -\eta_k$ by (23). If $\nu_2(3t + 2) \le \nu_2(h)$, the
  quotient $(3t + 2)/g_2$ is odd, forcing $\eta_k = \eta_{k + 3t + 2} = -\eta_k \implies \eta \equiv 0$.
  If $\nu_2(3t + 2) > \nu_2(h)$, then $\eta_k$ is $g_2$-antiperiodic with
  $\eta_{4t - 2 - k} = -\eta_k$; on a fundamental antiperiod of length $g_2$
  starting at $2t$, $\eta_{2t + g_2 - 1} = 0$ and $\eta_{2t + s} = \eta_{2t + g_2 - 2 - s}$
  ($0 \le s \le g_2 - 2$), so this space $\mathcal{H}_{t, h}$ has dimension
  $\lfloor g_2 / 2 \rfloor = d_2(t, h)$.

Finally, consider the linear map
$\Phi : \ker M(t, h) \to \mathcal{X}_{t, h} \times \mathcal{H}_{t, h}$,
$z \mapsto (\xi, \eta)$. If $z \in \ker(\Phi)$, then $\xi \equiv 0$ and
$\eta \equiv 0$, so (19) gives $z_i + z_{i - 1} = 0 \implies z_i = (-1)^{i - 2t} z_{2t}$.
An alternating sequence satisfies $\xi_i = z_i + z_{i - h} = 0$ iff $h$ is odd,
and $E_i(z) = z_i - z_{7t - i} = 0$ iff $t$ is even; when both hold, $2 \mid 3t$
and $2 \mid (h + 1)$, i.e., $2 \mid g_1$. Thus
$\dim \ker(\Phi) \le \mathbf{1}_{2 \mid g_1}$, and by Rank-Nullity,
$$\dim \ker_{\mathbb{Q}} M(t, h) \le \dim \ker(\Phi) + \dim \mathcal{X}_{t, h} + \dim \mathcal{H}_{t, h} \le \mathbf{1}_{2 \mid g_1} + \left\lfloor \frac{g_1 - 1}{2} \right\rfloor + d_2(t, h) = \left\lfloor \frac{g_1}{2} \right\rfloor + d_2(t, h) = d_1(t, h) + d_2(t, h). \tag{25}$$
Combining (25) with the lower bound from Section 1 completes the proof of (2)–(3).

---

## Reproducible commands and witnessed controls

From a repository checkout using Python 3.10+ and only the standard library:

```sh
python3 projects/almost-halving-three-branches/middle_nullity.py --classify 2661 19
python3 projects/almost-halving-three-branches/middle_nullity.py --control 12 --h 19 --negative-depths 871
python3 projects/almost-halving-three-branches/middle_nullity.py --control 6 --h 10 --negative-depths 11
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_middle_nullity.py -v
```

Recorded results:
- `--classify 2661 19` returns `invertible: true`, `nullity: 0`,
  `rank: 13305`, `seed_width: 40`, `seed_rank: 40`, `type1_period: 1`,
  `type1_nullity: 0`, `type2_antiperiod: 1`, `type2_active: false`,
  `type2_nullity: 0`.
- `--control 12 --h 19 --negative-depths 871` tests a single-flip literal second
  word at $(t, h) = (12, 19)$, where $g_1 = \gcd(36, 20) = 4$ ($d_1 = 2$) and
  $g_2 = \gcd(38, 19) = 19$ with $\nu_2(38) = 1 > \nu_2(19) = 0$ ($d_2 = 9$,
  total nullity $11$). This word passes Aster's reflected endpoint test
  (`[-2]`), passes Mallow's all-rectangle scan (`maximum_seen = 2 <= 8`), and
  passes both Type-I periodic compatibility equalities (`type1_residuals: [0, 0]`),
  but **fails** two Type-II antiperiodic compatibility equalities
  (`type2_residuals: [0, -2, -2, 0, 0, 0, 0, 0, 0]`), proving in $O(t)$ integer
  additions that no rational or literal middle completion exists.
- `--control 6 --h 10 --negative-depths 11` tests a pure Type-II singular scale
  ($g_1 = \gcd(18, 11) = 1 \implies d_1 = 0$, while
  $g_2 = \gcd(20, 10) = 10$ with $\nu_2(20) = 2 > \nu_2(10) = 1 \implies d_2 = 5$).
  It passes the reflected test (`[0, 2]`) and all-rectangle scan (`maximum_seen = 2`),
  and is excluded by the first Type-II compatibility equality (`residual: 2`).
- Eight unit tests in `test_middle_nullity.py` verify the closed-form rank,
  nullity, right-kernel basis, and left-kernel basis against independently
  assembled full $5t \times 5t$ rational matrices for every $1 \le t \le 8$ and
  $0 \le h \le 2t - 2$; verify global symmetry of $L_{t, h}^T M(t, h)$; verify
  the $\Psi_h$ seed parametrization and $\xi, \eta$ closed forms; verify
  necessary and sufficient compatibility against augmented matrix ranks; check
  independent adjacency BFS shell invariance under both Type-I and Type-II
  kernel vectors; and test honesty flags on singular consistent inputs.
