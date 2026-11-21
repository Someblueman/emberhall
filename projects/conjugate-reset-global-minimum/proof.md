# Global Optimality of the Conjugate Restart-Time Law in 1D Brownian Search

## 1. Literature Audit and Exact Scope

Before giving the proof, we check the current literature (up to November 2026, bounded search of published abstracts and arXiv preprints; priority remains provisional pending independent verification) for an equivalent theorem in this persistent-target setting:

1. **Evans & Ray**, *Phys. Rev. Lett.* **134**, 247102 (2025); [arXiv:2410.01941v2](https://arxiv.org/html/2410.01941v2) (*Stochastic resetting prevails over sharp restart for broad target distributions*):
   Formulates the target-averaged mean first-passage time $J[\nu] = \int_0^\infty P_T(R)\langle T_r(R)\rangle_\nu\,\mathrm{d}R$ for a target distance $R$ drawn once and kept fixed across attempts, introduces the conjugate target density $P_T^*(R) \propto D_\mu(R)^2$ via first-variation stationarity, and compares specific restart families (such as deterministic sharp restart vs. exponential and power-law protocols). Immediately after their variational calculation, Evans and Ray state that it remains to confirm that the stationary law minimizes Eq. (1) and is therefore optimal.
2. **Pal & Reuveni**, *Phys. Rev. Lett.* **118**, 030603 (2017); [arXiv:1607.06048v3](https://arxiv.org/html/1607.06048v3) (*First Passage under Restart*):
   Closest global optimality theorem in restart theory. In Pal and Reuveni, every restart attempt draws a fresh independent completion time from one fixed unconditional distribution (equivalently, a single fixed target distance $R$), reducing the mean search time to a single ratio $\mathbb{E}[\min(T, \tau)] / \mathbb{P}(T \le \tau)$ that is always minimized globally by a deterministic sharp restart. By contrast, when $R \sim P_T^*(R)$ persists across attempts, the objective averages ratios $N_\nu(R)/D_\nu(R)$ over $R$; deterministic sharp restart generally diverges ($J[\delta_T] = +\infty$ for exponential $P_T^*$), and genuine stochastic mixtures can be uniquely optimal.
3. **García-Valladares, Prados, Manacorda & Plata**, *Phys. Rev. E* **113**, 024107 (Feb 2026); [arXiv:2505.16626v2](https://arxiv.org/html/2505.16626v2) (*How target distributions shape optimal stochastic resetting*):
   Studies a Brownian searcher on a finite interval $[-L, L]$ with boundary resetting and spatially dependent bulk resetting, noting that numerical optimization establishes local rather than global optimality.
4. **Citing 2025–2026 works & analytic technique**:
   Recent works citing Evans–Ray (e.g., Colantoni & Pagnini, *Proc. R. Soc. A* **481**, 20250641, Dec 2025; Del Vecchio et al., *Phys. Rev. Lett.* **137**, 057102, July 2026) treat continuous-time random walks and active exploration rather than proving global optimality of the conjugate restart law. Our remainder construction adapts the ground-state representation technique of **Frank & Seiringer**, *J. Funct. Anal.* **255**, 3407–3430 (2008); [arXiv:0803.0503](https://arxiv.org/pdf/0803.0503), to the 1D radial diffusion operator $-D\,\mathrm{d}^2/\mathrm{d}R^2$ on $(0, \infty)$ using the positive concave expected attempt-duration profile $N_\nu(R)$.

**Scope boundary.** The theorem below holds for one-dimensional Brownian diffusion ($D > 0$) starting at $X_0 = 0$, a stationary absorbing target at fixed $R > 0$ drawn once from $P_T^*$, and all Borel probability measures $\nu$ on $(0, \infty)$ (independent positive finite restart times). It does not cover higher dimensions ($d \ge 2$), spatial/history-dependent resets, or restart time penalties.

---

## 2. Renewal Formulation and Exact Half-Line Kernels

Fix diffusivity $D > 0$. For a Brownian particle $X_t$ starting at $X_0 = 0$ searching for an absorbing target at fixed coordinate $R > 0$, the reflection principle gives the free first-passage time $T_R = \inf\{t \ge 0 : X_t = R\}$ survival probability $Q_0(R, t) = \mathbb{P}(T_R > t) = \operatorname{erf}\!\left(\frac{R}{\sqrt{4Dt}}\right)$, solving the half-line heat equation
$$\partial_t Q_0(R, t) = D\,\partial_R^2 Q_0(R, t), \qquad R > 0,\ t > 0,$$
with initial condition $\lim_{t \downarrow 0} Q_0(R, t) = 1$ ($R > 0$) and absorbing boundary $\lim_{R \downarrow 0} Q_0(R, t) = 0$ ($t > 0$).

Let $\mathcal{P}((0,\infty))$ be the set of all Borel probability measures on $(0, \infty)$, representing i.i.d. positive finite restart times $\tau \sim \nu$ (so $\nu(\{0\}) = \nu(\{\infty\}) = 0$; putting mass at $0$ gives instantaneous zero-progress resets, and putting mass at $\infty$ makes $\mathbb{E}[\min(T_R, \tau)] = \infty$ identically because 1D Brownian motion has $\mathbb{E}[T_R] = \infty$).

For any $\nu \in \mathcal{P}((0,\infty))$ and $R > 0$:
- **Single-attempt hitting probability:**
  $$D_\nu(R) := \mathbb{E}_\nu\bigl[1 - Q_0(R, \tau)\bigr] = \int_{(0,\infty)} \operatorname{erfc}\!\left(\frac{R}{\sqrt{4D\tau}}\right)\mathrm{d}\nu(\tau) \in (0, 1).$$
  Because $\operatorname{erfc}(R/\sqrt{4D\tau}) > 0$ for every $\tau \in (0,\infty)$ and $\nu((0,\infty)) = 1$, $D_\nu(R) > 0$ everywhere on $(0,\infty)$, and by bounded convergence $\lim_{R \downarrow 0} D_\nu(R) = 1$.
- **Single-attempt expected duration:** Since $\min(T_R, \tau) = \int_0^\tau \mathbf{1}_{\{T_R > t\}}\,\mathrm{d}t$ and $\tau$ is independent of $T_R$, Tonelli's theorem gives
  $$N_\nu(R) := \mathbb{E}[\min(T_R, \tau)] = \int_{(0,\infty)} \left(\int_0^\tau \operatorname{erf}\!\left(\frac{R}{\sqrt{4Dt}}\right)\mathrm{d}t\right)\mathrm{d}\nu(\tau) \in (0, \infty].$$
  Evaluating the inner integral explicitly by substituting $u = R / \sqrt{4Dt}$ (and setting $x = R/\sqrt{4D}$) yields
  $$N_{\delta_\tau}(R) = \int_0^\tau \operatorname{erf}\!\left(\frac{x}{\sqrt{t}}\right)\mathrm{d}t = \bigl(\tau + 2x^2\bigr)\operatorname{erf}\!\left(\frac{x}{\sqrt{\tau}}\right) + 2x\sqrt{\frac{\tau}{\pi}}\,e^{-x^2/\tau} - 2x^2.$$
- **Fixed-target mean first-passage time (MFPT):** Because each reset restarts the Brownian motion independently at $0$ while keeping $R$ fixed, the number of attempts until hitting is Geometric($D_\nu(R)$), and Wald's identity yields
  $$\langle T_r(R) \rangle_\nu = \frac{N_\nu(R)}{D_\nu(R)} \in (0, \infty].$$

### Lemma 1 (Exact $A$ and $B$ kernels and sharp moment bounds)
For every $s, \tau > 0$:
1. **Conjugate normalization kernel:**
   $$A(s, \tau) := \int_0^\infty \operatorname{erfc}\!\left(\frac{R}{\sqrt{4Ds}}\right)\operatorname{erfc}\!\left(\frac{R}{\sqrt{4D\tau}}\right)\mathrm{d}R = 2\sqrt{\frac{D}{\pi}}\Bigl(\sqrt{s} + \sqrt{\tau} - \sqrt{s+\tau}\Bigr) \le 2\sqrt{\frac{D}{\pi}}\,(s\tau)^{1/4}.$$
2. **Symmetric renewal bilinear kernel:**
   $$B(s, \tau) := \int_0^\infty \operatorname{erfc}\!\left(\frac{R}{\sqrt{4D\tau}}\right) N_{\delta_s}(R)\,\mathrm{d}R = \frac{4}{3}\sqrt{\frac{D}{\pi}}\Bigl[(s+\tau)^{3/2} - s^{3/2} - \tau^{3/2}\Bigr] \le 2\sqrt{\frac{2D}{\pi}}\,s^{3/4}\tau^{3/4}.$$

**Proof of Lemma 1.**
For (1), set $R = \sqrt{4D}\,x$ and define $\tilde{A}(s,\tau) = \int_0^\infty \operatorname{erfc}(x/\sqrt{s})\operatorname{erfc}(x/\sqrt{\tau})\,\mathrm{d}x$. Differentiating under the integral sign using $\partial_\tau \operatorname{erfc}(x/\sqrt{\tau}) = \frac{x}{\sqrt{\pi}\,\tau^{3/2}} e^{-x^2/\tau}$ gives
$$\partial_s\partial_\tau \tilde{A}(s, \tau) = \frac{1}{\pi (s\tau)^{3/2}} \int_0^\infty x^2 e^{-x^2(s^{-1}+\tau^{-1})}\,\mathrm{d}x = \frac{1}{4\sqrt{\pi}\,(s+\tau)^{3/2}}.$$
Since $\lim_{\tau\downarrow 0} \tilde{A}(s, \tau) = 0$ and $\lim_{\tau\downarrow 0} \partial_s \tilde{A}(s, \tau) = 0$ by dominated convergence, integrating first in $\tau$ from $0$ to $\tau$ gives $\partial_s \tilde{A}(s, \tau) = \frac{1}{2\sqrt{\pi}}\bigl(s^{-1/2} - (s+\tau)^{-1/2}\bigr)$, and integrating in $s$ from $0$ to $s$ yields $\tilde{A}(s, \tau) = \frac{1}{\sqrt{\pi}}(\sqrt{s} + \sqrt{\tau} - \sqrt{s+\tau})$. Multiplying by $2\sqrt{D}$ gives the formula for $A(s, \tau)$. Since $\sqrt{s} + \sqrt{\tau} - \sqrt{s+\tau} \le \min(\sqrt{s}, \sqrt{\tau}) \le (s\tau)^{1/4}$, the bound in (1) follows.

For (2), differentiate $B(s, \tau)$ in $s$ and $\tau$ for $s, \tau > 0$ (justified on compact subsets of $(0,\infty)^2$ by Gaussian decay in $R$):
$$\partial_s B(s, \tau) = \int_0^\infty \operatorname{erfc}\!\left(\frac{R}{\sqrt{4D\tau}}\right)\operatorname{erf}\!\left(\frac{R}{\sqrt{4Ds}}\right)\mathrm{d}R,$$
$$\partial_\tau \partial_s B(s, \tau) = \int_0^\infty \frac{R}{\sqrt{4\pi D}\,\tau^{3/2}} e^{-R^2/(4D\tau)} \operatorname{erf}\!\left(\frac{R}{\sqrt{4Ds}}\right)\mathrm{d}R.$$
Substitute $u = R^2 / (4D)$, so $R\,\mathrm{d}R = 2D\,\mathrm{d}u$ and $\frac{R\,\mathrm{d}R}{\sqrt{4\pi D}} = \sqrt{\frac{D}{\pi}}\,\mathrm{d}u$:
$$\partial_\tau \partial_s B(s, \tau) = \sqrt{\frac{D}{\pi}}\,\tau^{-3/2} \int_0^\infty e^{-u/\tau} \operatorname{erf}\!\left(\sqrt{\frac{u}{s}}\right)\mathrm{d}u.$$
Evaluating the Laplace transform at $p = 1/\tau$ using $\frac{\mathrm{d}}{\mathrm{d}u}\operatorname{erf}(\sqrt{u/s}) = \frac{1}{\sqrt{\pi s u}} e^{-u/s}$ gives
$$\int_0^\infty e^{-p u} \operatorname{erf}\!\left(\sqrt{\frac{u}{s}}\right)\mathrm{d}u = \frac{1}{p}\int_0^\infty \frac{e^{-(p + 1/s)u}}{\sqrt{\pi s u}}\,\mathrm{d}u = \frac{1}{p\sqrt{1 + p s}}.$$
At $p = 1/\tau$, $\frac{1}{p\sqrt{1 + ps}} = \frac{\tau^{3/2}}{\sqrt{s+\tau}}$, whence the manifestly symmetric identity
$$\partial_\tau \partial_s B(s, \tau) = \sqrt{\frac{D}{\pi}}\,\frac{1}{\sqrt{s + \tau}}.$$
Since $\lim_{\tau\downarrow 0} B(s, \tau) = \lim_{\tau\downarrow 0}\partial_s B(s, \tau) = 0$ and $\lim_{s\downarrow 0} B(s, \tau) = 0$, integrating in $\tau$ gives $\partial_s B(s, \tau) = 2\sqrt{\frac{D}{\pi}}(\sqrt{s+\tau} - \sqrt{s})$, and integrating in $s$ yields
$$B(s, \tau) = \frac{4}{3}\sqrt{\frac{D}{\pi}}\Bigl[(s+\tau)^{3/2} - s^{3/2} - \tau^{3/2}\Bigr].$$
For the moment bound, assume without loss of generality $0 < s \le \tau$. By the fundamental theorem of calculus,
$$(s+\tau)^{3/2} - \tau^{3/2} - s^{3/2} \le (s+\tau)^{3/2} - \tau^{3/2} = \frac{3}{2}\int_\tau^{\tau+s} u^{1/2}\,\mathrm{d}u \le \frac{3}{2} s (\tau+s)^{1/2} \le \frac{3}{\sqrt{2}}\, s \tau^{1/2} \le \frac{3}{\sqrt{2}}\, s^{3/4}\tau^{3/4},$$
because $s \le \tau \implies (s/\tau)^{1/4} \le 1$. Multiplying by $\frac{4}{3}\sqrt{\frac{D}{\pi}}$ gives $B(s,\tau) \le 2\sqrt{\frac{2D}{\pi}}\,s^{3/4}\tau^{3/4}$. $\square$

---

## 3. Baseline Normalization and the Finite $3/4$-Moment Hypothesis

Let $\mu \in \mathcal{P}((0,\infty))$ be a baseline restart law satisfying the finite three-quarter moment hypothesis:
$$M_{3/4}(\mu) := \mathbb{E}_\mu[\tau^{3/4}] = \int_{(0,\infty)} \tau^{3/4}\,\mathrm{d}\mu(\tau) < \infty.$$
Since $\tau^{1/4} \le 1 + \tau^{3/4}$ and $\tau^{1/2} \le 1 + \tau^{3/4}$, we automatically have $\mathbb{E}_\mu[\tau^{1/4}] < \infty$ and $\mathbb{E}_\mu[\tau^{1/2}] < \infty$ (while $\mathbb{E}_\mu[\tau]$ may be infinite).

Define the **conjugate target density** of $\mu$ on $(0, \infty)$ by
$$P_T^*(R) := \frac{D_\mu(R)^2}{Z}, \qquad Z := \int_0^\infty D_\mu(R)^2\,\mathrm{d}R.$$
By Tonelli's theorem and Lemma 1(1),
$$0 < Z = \iint_{(0,\infty)^2} A(s, \tau)\,\mathrm{d}\mu(s)\,\mathrm{d}\mu(\tau) \le 2\sqrt{\frac{D}{\pi}}\,\bigl(\mathbb{E}_\mu[\tau^{1/4}]\bigr)^2 < \infty,$$
so $P_T^*$ is a strictly positive, continuous, normalized probability density on $(0, \infty)$ ($\int_0^\infty P_T^*(R)\,\mathrm{d}R = 1$).

For any competitor $\nu \in \mathcal{P}((0, \infty))$, the target-averaged mean first-passage time is
$$J[\nu] := \int_0^\infty P_T^*(R)\,\langle T_r(R)\rangle_\nu\,\mathrm{d}R = \frac{1}{Z}\int_0^\infty \frac{D_\mu(R)^2}{D_\nu(R)}\,N_\nu(R)\,\mathrm{d}R \in (0, \infty].$$
At the baseline $\nu = \mu$, Tonelli's theorem and Lemma 1(2) give
$$J[\mu] = \frac{1}{Z}\int_0^\infty D_\mu(R) N_\mu(R)\,\mathrm{d}R = \frac{1}{Z}\iint_{(0,\infty)^2} B(s, \tau)\,\mathrm{d}\mu(s)\,\mathrm{d}\mu(\tau) \le \frac{2}{Z}\sqrt{\frac{2D}{\pi}}\,\bigl(\mathbb{E}_\mu[\tau^{3/4}]\bigr)^2 < \infty.$$

**Sharpness of the $3/4$ moment.** For $s = \tau$, $B(\tau, \tau) = \frac{4}{3}\sqrt{\frac{D}{\pi}}(2\sqrt{2} - 2)\tau^{3/2}$, and for $0 < s \le \tau$, $B(s, \tau) \ge \frac{4}{3}\sqrt{\frac{D}{\pi}}(\frac{3}{2}s\tau^{1/2} - s^{3/2}) \asymp \min(s,\tau)\max(s,\tau)^{1/2}$. If a baseline tail behaves as $\mu((\tau,\infty)) \sim c\tau^{-3/4}$ (so $\mathbb{E}_\mu[\tau^{1/4}] < \infty$ gives $Z < \infty$ while $\mathbb{E}_\mu[\tau^{3/4}] = +\infty$), then $D_\mu(R) \asymp R^{-3/2}$ and $N_\mu(R) \asymp R^{2 - 3/2} = R^{1/2}$ as $R \to \infty$, so $D_\mu(R) N_\mu(R) \asymp R^{-1}$ and $J[\mu] = +\infty$. Thus $\mathbb{E}_\mu[\tau^{3/4}] < \infty$ is **sufficient** for $J[\mu] < \infty$ and **sharp as a power-law moment exponent** (though not strictly necessary for every Borel law—for instance a sparse atomic law with $w_k \propto k^{-1} 2^{-3k/4}$ at $\tau_k = 2^k$ has $\mathbb{E}_\mu[\tau^{3/4}] = +\infty$ while $\sum_k k^{-2} < \infty$ keeps $B(\mu,\mu) < \infty$).

---

## 4. Differential Equation and Asymptotics of $N_\nu(R)$

### Lemma 2 (Differential equation, concavity, and boundary decay)
1. For any $\nu \in \mathcal{P}((0,\infty))$:
   - If $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$, then $N_\nu(R) = +\infty$ for every $R > 0$.
   - If $\mathbb{E}_\nu[\tau^{1/2}] < \infty$, then $N_\nu \in C^1([0,\infty)) \cap C^\infty((0,\infty))$ with $N_\nu(0) = 0$, $N_\nu'(R) > 0$, $N_\nu'(0^+) = \frac{2}{\sqrt{\pi D}}\,\mathbb{E}_\nu[\tau^{1/2}] < \infty$, and
     $$-D\,N_\nu''(R) = D_\nu(R) > 0 \qquad \forall R > 0.$$
     In particular, $N_\nu$ is strictly increasing and strictly concave on $[0,\infty)$, so
     $$0 < \frac{N_\nu'(R)}{N_\nu(R)} \le \frac{1}{R} \qquad \forall R > 0.$$
2. Under $\mathbb{E}_\mu[\tau^{3/4}] < \infty$, we have $\lim_{R\to\infty} R^{-1/2} N_\mu(R) = 0$, i.e., $N_\mu(R) = o(R^{1/2})$ as $R \to \infty$.
3. Consequently, for every $\nu \in \mathcal{P}((0,\infty))$ with $\mathbb{E}_\nu[\tau^{1/2}] < \infty$,
   $$\lim_{\epsilon \downarrow 0} N_\mu(\epsilon)^2 \frac{N_\nu'(\epsilon)}{N_\nu(\epsilon)} = 0, \qquad \lim_{M \to \infty} N_\mu(M)^2 \frac{N_\nu'(M)}{N_\nu(M)} = 0,$$
   and
   $$\int_0^\infty D_\mu(R) N_\mu(R)\,\mathrm{d}R = D\int_0^\infty \bigl(N_\mu'(R)\bigr)^2\,\mathrm{d}R = Z\,J[\mu] < \infty.$$

**Proof of Lemma 2.**
For (1), note $\operatorname{erf}(z) \ge \frac{2}{\sqrt{\pi}} e^{-1} z$ on $z \in [0, 1]$, so for $\tau \ge R^2/(4D)$,
$$N_{\delta_\tau}(R) \ge \int_{R^2/(4D)}^\tau \operatorname{erf}\!\left(\frac{R}{\sqrt{4Dt}}\right)\mathrm{d}t \ge \frac{R}{e\sqrt{\pi D}}\bigl(2\sqrt{\tau} - \tfrac{R}{\sqrt{D}}\bigr),$$
whose $\nu$-integral diverges whenever $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$.

When $\mathbb{E}_\nu[\tau^{1/2}] < \infty$, recall $\operatorname{erf}(z) \le \min\bigl(1, \frac{2}{\sqrt{\pi}} z\bigr)$ for $z \ge 0$, so
$$N_{\delta_\tau}(R) \le \int_0^\tau \frac{R}{\sqrt{\pi D t}}\,\mathrm{d}t = \frac{2R}{\sqrt{\pi D}}\,\tau^{1/2}, \qquad \text{and} \qquad N_{\delta_\tau}'(R) = \int_0^\tau \frac{1}{\sqrt{\pi D t}} e^{-R^2/(4Dt)}\,\mathrm{d}t \le \frac{2}{\sqrt{\pi D}}\,\tau^{1/2}.$$
(Explicitly, with $x = R/\sqrt{4D}$, $N_{\delta_\tau}'(R) = D^{-1/2}\bigl[2x(\operatorname{erf}(x/\sqrt{\tau})-1) + 2\sqrt{\tau/\pi}\,e^{-x^2/\tau}\bigr]$.) By dominated convergence against $\tau^{1/2}\,\mathrm{d}\nu(\tau)$, $N_\nu \in C^1([0,\infty))$ with $N_\nu(0)=0$, $N_\nu'(0^+) = \frac{2}{\sqrt{\pi D}}\mathbb{E}_\nu[\tau^{1/2}]$, and $N_\nu'(R) > 0$. On $[\epsilon, \infty)$ ($\epsilon > 0$), $\partial_R^2 N_{\delta_\tau}(R) = -\frac{1}{D}\operatorname{erfc}(R/\sqrt{4D\tau})$ has uniform boundedness ($|\partial_R^2 N_{\delta_\tau}| \le 1/D$ and higher $R$-derivatives have uniform exponential bounds in $t$), so $-D N_\nu''(R) = D_\nu(R) > 0$ on $(0, \infty)$. Since $N_\nu(0)=0$ and $N_\nu'$ is strictly decreasing, $N_\nu(R) = \int_0^R N_\nu'(r)\,\mathrm{d}r > R\,N_\nu'(R)$ for every $R > 0$, giving $N_\nu'(R)/N_\nu(R) < 1/R$.

For (2), combine the two elementary bounds $N_{\delta_\tau}(R) \le \tau$ and $N_{\delta_\tau}(R) \le \frac{2R}{\sqrt{\pi D}}\tau^{1/2}$ via their geometric mean:
$$N_{\delta_\tau}(R) \le \min\!\left(\tau,\, \frac{2R}{\sqrt{\pi D}}\tau^{1/2}\right) \le \tau^{1/2}\left(\frac{2R}{\sqrt{\pi D}}\tau^{1/2}\right)^{1/2} = \sqrt{\frac{2}{\sqrt{\pi D}}}\, R^{1/2}\,\tau^{3/4}.$$
Dividing by $R^{1/2}$, the integrand $R^{-1/2} N_{\delta_\tau}(R)$ is dominated by $\sqrt{\frac{2}{\sqrt{\pi D}}}\,\tau^{3/4} \in L^1(\mu)$, while for each fixed $\tau > 0$, $R^{-1/2} N_{\delta_\tau}(R) \le R^{-1/2}\tau \to 0$ as $R \to \infty$. Dominated convergence gives $\lim_{R\to\infty} R^{-1/2} N_\mu(R) = 0$.

For (3), as $\epsilon \downarrow 0$, $N_\mu(\epsilon) \le N_\mu'(0^+)\,\epsilon$ and $\epsilon\,N_\nu'(\epsilon)/N_\nu(\epsilon) \le 1$, so $N_\mu(\epsilon)^2 N_\nu'(\epsilon)/N_\nu(\epsilon) \le (N_\mu'(0^+))^2\,\epsilon \to 0$. As $M \to \infty$, $N_\mu(M)^2 N_\nu'(M)/N_\nu(M) \le N_\mu(M)^2 / M = (M^{-1/2} N_\mu(M))^2 \to 0$. Choosing $\nu = \mu$ shows $N_\mu(\epsilon) N_\mu'(\epsilon) \to 0$ and $N_\mu(M) N_\mu'(M) \le N_\mu(M)^2 / M \to 0$, so integrating $\int_\epsilon^M (-D N_\mu'') N_\mu\,\mathrm{d}R$ by parts and letting $\epsilon \downarrow 0, M \uparrow \infty$ gives $\int_0^\infty D_\mu N_\mu\,\mathrm{d}R = D\int_0^\infty (N_\mu')^2\,\mathrm{d}R = Z J[\mu]$. $\square$

---

## 5. Main Theorem: Global Optimality and Uniqueness

### Theorem (Global minimum with explicit nonnegative remainder)
Let $\mu \in \mathcal{P}((0,\infty))$ satisfy $\mathbb{E}_\mu[\tau^{3/4}] < \infty$, and let $P_T^*(R) = Z^{-1} D_\mu(R)^2$ be its conjugate target density. Then for every admissible competing law $\nu \in \mathcal{P}((0,\infty))$:
1. $J[\nu] \ge J[\mu]$ (including all competitors with $J[\nu] = +\infty$).
2. Whenever $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$, $J[\nu] = +\infty > J[\mu]$.
3. Whenever $\mathbb{E}_\nu[\tau^{1/2}] < \infty$, the excess mean first-passage time satisfies the exact identity in $[0, +\infty]$:
   $$J[\nu] - J[\mu] = \frac{1}{Z}\int_0^\infty \left(\sqrt{\frac{N_\nu(R)}{D_\nu(R)}}\,D_\mu(R) - \sqrt{\frac{D_\nu(R)}{N_\nu(R)}}\,N_\mu(R)\right)^2 \mathrm{d}R + \frac{D}{Z}\int_0^\infty \left(N_\mu'(R) - \frac{N_\nu'(R)}{N_\nu(R)}\,N_\mu(R)\right)^2 \mathrm{d}R,$$
   where both integrals are finite if and only if $J[\nu] < \infty$, and both equal $+\infty$ in sum if and only if $J[\nu] = +\infty$.
4. **Equality characterization:** $J[\nu] = J[\mu]$ if and only if $\nu = \mu$.

### Proof
If $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$, Lemma 2(1) gives $N_\nu(R) = +\infty$ for all $R > 0$. Since $D_\nu(R) \in (0, 1)$ and $P_T^*(R) > 0$ on $(0,\infty)$, $\langle T_r(R)\rangle_\nu = +\infty$ identically on $(0, \infty)$, so $J[\nu] = +\infty > J[\mu]$.

Assume now that $\mathbb{E}_\nu[\tau^{1/2}] < \infty$. Fix $0 < \epsilon < M < \infty$. Because $D_\nu, N_\nu, D_\mu, N_\mu$ are smooth and strictly positive on $[\epsilon, M]$, every integral below on $[\epsilon, M]$ is finite. We form two nonnegative integrals on $[\epsilon, M]$:
$$I_1[\epsilon, M] := \int_\epsilon^M \left(\sqrt{\frac{N_\nu(R)}{D_\nu(R)}}\,D_\mu(R) - \sqrt{\frac{D_\nu(R)}{N_\nu(R)}}\,N_\mu(R)\right)^2 \mathrm{d}R \ge 0,$$
$$I_2[\epsilon, M] := D\int_\epsilon^M \left(N_\mu'(R) - \frac{N_\nu'(R)}{N_\nu(R)}\,N_\mu(R)\right)^2 \mathrm{d}R \ge 0.$$
Expanding $I_1[\epsilon, M]$ gives
$$I_1[\epsilon, M] = \int_\epsilon^M \frac{D_\mu(R)^2}{D_\nu(R)} N_\nu(R)\,\mathrm{d}R - 2\int_\epsilon^M D_\mu(R) N_\mu(R)\,\mathrm{d}R + \int_\epsilon^M \frac{D_\nu(R)}{N_\nu(R)} N_\mu(R)^2\,\mathrm{d}R.$$
Expanding $I_2[\epsilon, M]$ and integrating the cross term $-D\int_\epsilon^M (N_\mu^2)' \frac{N_\nu'}{N_\nu}\,\mathrm{d}R$ by parts using Lemma 2(1) ($D N_\nu'' = -D_\nu$):
$$\begin{aligned}
I_2[\epsilon, M] &= D\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R - D\int_\epsilon^M (N_\mu^2)'\,\frac{N_\nu'}{N_\nu}\,\mathrm{d}R + D\int_\epsilon^M N_\mu^2 \frac{(N_\nu')^2}{N_\nu^2}\,\mathrm{d}R \\
&= D\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R + \left[-D\,N_\mu(R)^2 \frac{N_\nu'(R)}{N_\nu(R)}\right]_{R=\epsilon}^{R=M} + D\int_\epsilon^M N_\mu^2 \frac{N_\nu''}{N_\nu}\,\mathrm{d}R \\
&= D\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R + \left[-D\,N_\mu(R)^2 \frac{N_\nu'(R)}{N_\nu(R)}\right]_\epsilon^M - \int_\epsilon^M \frac{D_\nu(R)}{N_\nu(R)} N_\mu(R)^2\,\mathrm{d}R.
\end{aligned}$$
Adding $I_1[\epsilon, M] + I_2[\epsilon, M]$, the terms $\pm \int_\epsilon^M \frac{D_\nu}{N_\nu} N_\mu^2\,\mathrm{d}R$ cancel identically; moving the remaining terms to the right yields the exact finite-interval identity
$$\int_\epsilon^M P_T^*(R)\,\langle T_r(R)\rangle_\nu\,\mathrm{d}R = \frac{1}{Z}\left(2\int_\epsilon^M D_\mu N_\mu\,\mathrm{d}R - D\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R - \left[-D\,N_\mu^2 \frac{N_\nu'}{N_\nu}\right]_\epsilon^M + I_1[\epsilon, M] + I_2[\epsilon, M]\right).$$
(For an explicit rational check of the minus sign in front of the bracket, take $\mu = \mathrm{Exp}(1)$, $\nu = \mathrm{Exp}(1/4)$, $D = 1$, $\epsilon = 2\ln 2$, $M = 2\ln 4$: then $Z\int_\epsilon^M P_T^*(R)\langle T_r(R)\rangle_\nu\,\mathrm{d}R = 67/384$, $\int_\epsilon^M D_\mu N_\mu\,\mathrm{d}R = 81/512$, $\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R = 15/512$, $\bigl[-N_\mu^2 N_\nu'/N_\nu\bigr]_\epsilon^M = 69/512$, $I_1[\epsilon,M] = 9/2048$, and $I_2[\epsilon,M] = 109/6144$, giving $2(81/512) - 15/512 - 69/512 + 9/2048 + 109/6144 = 67/384$.)
As $\epsilon \downarrow 0$ and $M \uparrow \infty$:
- By Lemma 2(3), $2\int_\epsilon^M D_\mu N_\mu\,\mathrm{d}R - D\int_\epsilon^M (N_\mu')^2\,\mathrm{d}R \to 2 Z J[\mu] - Z J[\mu] = Z J[\mu] < \infty$, and both boundary terms in $[-D N_\mu^2 N_\nu'/N_\nu]_\epsilon^M$ converge to $0$.
- By the Monotone Convergence Theorem, the left-hand side converges to $J[\nu] \in (0, \infty]$ while $I_1[\epsilon, M] \uparrow I_1 \in [0, \infty]$ and $I_2[\epsilon, M] \uparrow I_2 \in [0, \infty]$.

Passing to the limit establishes (3) and hence $J[\nu] \ge J[\mu]$ in all cases (even when $\mathbb{E}_\nu[\tau^{3/4}] = \infty$ or $J[\nu] = +\infty$, where divergence of $J[\nu]$ is equivalent to $I_1 + I_2 = +\infty$).

For (4), suppose $J[\nu] = J[\mu] < \infty$. Then necessarily $\mathbb{E}_\nu[\tau^{1/2}] < \infty$ and both nonnegative continuous integrands in (3) vanish for all $R \in (0, \infty)$. In particular, from the second integral,
$$0 = N_\mu'(R) - \frac{N_\nu'(R)}{N_\nu(R)}\,N_\mu(R) = N_\nu(R)\,\frac{\mathrm{d}}{\mathrm{d}R}\!\left(\frac{N_\mu(R)}{N_\nu(R)}\right) \qquad \forall R > 0.$$
Hence there exists a constant $c > 0$ such that $N_\mu(R) = c\,N_\nu(R)$ for all $R > 0$. Differentiating twice and multiplying by $-D$ gives $D_\mu(R) = c\,D_\nu(R)$ for all $R > 0$. Letting $R \downarrow 0$ and using $D_\mu(0^+) = D_\nu(0^+) = 1$ (since $\mu, \nu$ are probability measures on $(0,\infty)$) forces $c = 1$, so $D_\mu(R) = D_\nu(R)$ for all $R > 0$. Differentiating in $R$ yields
$$-D_\mu'(R) = \int_{(0,\infty)} \frac{1}{\sqrt{\pi D\tau}}\,e^{-R^2/(4D\tau)}\,\mathrm{d}\mu(\tau) = -D_\nu'(R) \qquad \forall R > 0.$$
Substituting $s = R^2 / (4D) > 0$ and $w = 1/\tau \in (0, \infty)$ expresses $-D_\mu'(\sqrt{4Ds}) = \int_{(0,\infty)} e^{-s w}\,\mathrm{d}\sigma_\mu(w)$, where $\mathrm{d}\sigma_\mu(w) = \sqrt{\frac{w}{\pi D}}\,\mathrm{d}(\tau^{-1}_\# \mu)(w)$ is a $\sigma$-finite positive Borel measure on $(0,\infty)$. Because $\sup_{\tau > 0} \tau^{-1/2} e^{-s_0/\tau} = (2 e s_0)^{-1/2} < \infty$ for any fixed $s_0 > 0$, the tilted measure $\tilde{\sigma}_\mu(\mathrm{d}w) := e^{-s_0 w}\,\sigma_\mu(\mathrm{d}w)$ is a bounded positive Borel measure on $(0,\infty)$ (total mass at most $(2\pi e D s_0)^{-1/2}$) whose Laplace transform at $t > 0$ equals $-D_\mu'(\sqrt{4D(s_0 + t)}) = -D_\nu'(\sqrt{4D(s_0 + t)})$. By uniqueness of Laplace transforms of finite positive Borel measures on $[0,\infty)$, $\tilde{\sigma}_\mu = \tilde{\sigma}_\nu$, hence $\sigma_\mu = \sigma_\nu$, and therefore $\mu = \nu$. $\square$

### Remark (Equivalent Green-Kernel Double Integral and Half-Line Convention)
For every fixed deterministic $\tau \in (0,\infty)$, $-D N_{\delta_\tau}'' = D_{\delta_\tau}$ with $N_{\delta_\tau}(0) = 0$ and $\lim_{R\to\infty} N_{\delta_\tau}'(R) = 0$ integrates directly to $N_{\delta_\tau}(x) = \frac{1}{D}\int_0^\infty \min(x, y)\,D_{\delta_\tau}(y)\,\mathrm{d}y$. Integrating against $\mathrm{d}\nu(\tau)$ and applying Tonelli's theorem extends the Dirichlet–Neumann Green representation $N_\nu(x) = \frac{1}{D}\int_0^\infty \min(x, y)\,D_\nu(y)\,\mathrm{d}y$ in $[0, \infty]$ to **every** $\nu \in \mathcal{P}((0,\infty))$ (including when $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$ and $N_\nu(x) \equiv +\infty$), and likewise $N_\mu(x) = \frac{1}{D}\int_0^\infty \min(x, y)\,D_\mu(y)\,\mathrm{d}y < \infty$. Substituting into $J[\nu] - J[\mu]$, symmetrizing $(x, y) \leftrightarrow (y, x)$, and truncating $(x, y) \in (0, M]^2$ before letting $M \to \infty$ (where the subtracted baseline integral converges to the finite constant $J[\mu] < \infty$) shows that the remainder equals the symmetric double integral
$$J[\nu] - J[\mu] = \frac{1}{2DZ}\iint_{(0,\infty)^2} \min(x, y)\,D_\nu(x)\,D_\nu(y)\,\left(\frac{D_\mu(x)}{D_\nu(x)} - \frac{D_\mu(y)}{D_\nu(y)}\right)^2 \mathrm{d}x\,\mathrm{d}y = \frac{1}{2DZ}\iint_{(0,\infty)^2} \min(x, y)\,\frac{\bigl(D_\mu(x) D_\nu(y) - D_\mu(y) D_\nu(x)\bigr)^2}{D_\nu(x)\,D_\nu(y)}\,\mathrm{d}x\,\mathrm{d}y.$$
Both forms vanish if and only if $D_\mu / D_\nu$ is constant on $(0,\infty)$. Throughout this note all integrals $Z = \int_0^\infty D_\mu(R)^2\,\mathrm{d}R$ and $B(s, \tau)$ use the half-line $(0,\infty)$ convention consistently; any full-line symmetry factor $2$ cancels identically in $J[\nu] = \int P_T^*(R)\langle T_r(R)\rangle_\nu\,\mathrm{d}R$.

---

## 6. Worked Examples (Including Atomic Mixtures, Long Tails, and Divergent Competitors)

Throughout this section we set $D = 1$.

### Example 1: Poisson Baseline vs. Exponential Family and Sharp Restart
Take $\mathrm{d}\mu(\tau) = r e^{-r\tau}\,\mathrm{d}\tau$ ($r > 0$), with $\alpha_0 = \sqrt{r}$. Then
$$D_\mu(R) = e^{-\alpha_0 R}, \qquad N_\mu(R) = \frac{1}{r}\bigl(1 - e^{-\alpha_0 R}\bigr), \qquad Z = \int_0^\infty e^{-2\alpha_0 R}\,\mathrm{d}R = \frac{1}{2\alpha_0},$$
so $P_T^*(R) = 2\alpha_0 e^{-2\alpha_0 R}$ and $J[\mu] = \int_0^\infty 2\alpha_0 e^{-2\alpha_0 R}\frac{1}{r}(e^{\alpha_0 R} - 1)\,\mathrm{d}R = \frac{1}{r}$.

- **Competing exponential $\nu = \operatorname{Exp}(r_1)$ ($\alpha_1 = \sqrt{r_1}$):**
  $\langle T_r(R)\rangle_\nu = \frac{1}{r_1}(e^{\alpha_1 R} - 1)$.
  - If $r_1 \ge 4r$ ($\alpha_1 \ge 2\alpha_0$), $P_T^*(R)\langle T_r(R)\rangle_\nu \ge \frac{2\alpha_0}{r_1}(1 - e^{-2\alpha_0 R})$ is non-integrable at $\infty$, so $J[\nu] = +\infty$ (consistent with $I_1 + I_2 = +\infty$).
  - If $0 < r_1 < 4r$ ($0 < \alpha_1 < 2\alpha_0$), exact integration gives
    $$J[\nu] = \frac{1}{r_1}\left(\frac{2\alpha_0}{2\alpha_0 - \alpha_1} - 1\right) = \frac{1}{\sqrt{r_1}(2\sqrt{r} - \sqrt{r_1})}, \qquad J[\nu] - J[\mu] = \frac{(\sqrt{r} - \sqrt{r_1})^2}{r\bigl(r - (\sqrt{r} - \sqrt{r_1})^2\bigr)} \ge 0,$$
    with equality if and only if $r_1 = r$.
  For instance, at $r = 1$, $r_1 = 1/4$: $J[\mu] = 1$, $J[\nu] = 4/3$, $I_1/Z = 1/4$, $I_2/Z = 1/12$, and $(I_1 + I_2)/Z = 1/3 = J[\nu] - J[\mu]$.
- **Competing deterministic sharp restart $\nu = \delta_T$ ($T > 0$):**
  Since $D_{\delta_T}(R) = \operatorname{erfc}(R/\sqrt{4T}) \sim \frac{\sqrt{4T}}{\sqrt{\pi}\,R} e^{-R^2/(4T)}$ while $P_T^*(R) = 2\alpha_0 e^{-2\alpha_0 R}$, the integrand $P_T^*(R) N_{\delta_T}(R)/D_{\delta_T}(R)$ grows like $c R e^{R^2/(4T) - 2\alpha_0 R} \to +\infty$, giving $J[\delta_T] = +\infty$ for every sharp restart period $T > 0$.

### Example 2: Two-Point Atomic Mixture Baseline
Take $\mu = \frac{1}{2}\delta_1 + \frac{1}{2}\delta_3$, which satisfies $\mathbb{E}_\mu[\tau^{3/4}] = \frac{1 + 3^{3/4}}{2} \approx 1.63975 < \infty$. Evaluating the closed-form expressions of Lemma 1(1)–(2) gives
$$Z = \frac{4\sqrt{3} - \sqrt{2} - \sqrt{6}}{2\sqrt{\pi}} \approx 0.864479468267576, \qquad B(\mu, \mu) \approx 1.643814475273593, \qquad J[\mu] = \frac{B(\mu,\mu)}{Z} \approx 1.901507827094854.$$
For deterministic competitors $\nu = \delta_s$:
- **Divergent threshold ($s \le \frac{3}{2}$):** Since $D_\mu(R)^2 \asymp R^{-2} e^{-R^2/6}$ and $D_{\delta_s}(R) \asymp R^{-1} e^{-R^2/(4s)}$, $D_\mu(R)^2/D_{\delta_s}(R)$ fails to be integrable whenever $\frac{1}{4s} \ge \frac{1}{6}$, i.e., $s \le 3/2$: for $s < 3/2$ it grows exponentially, while at the boundary $s = 3/2$ it decays as $R^{-1}$ and diverges logarithmically. In particular, $J[\delta_1] = +\infty$.
- **Finite comparisons ($s > \frac{3}{2}$):** Numerical quadrature confirms agreement between $J[\delta_s] - J[\mu]$ and $(I_1 + I_2)/Z$:
  - $s = 2$: $J[\delta_2] - J[\mu] \approx 0.0684926$, with $I_1/Z \approx 0.066874$ and $I_2/Z \approx 0.001618$.
  - $s = 3$: $J[\delta_3] - J[\mu] \approx 0.0567613$, with $I_1/Z \approx 0.044454$ and $I_2/Z \approx 0.012307$.
  - $s = 5$: $J[\delta_5] - J[\mu] \approx 0.3443989$, with $I_1/Z \approx 0.269545$ and $I_2/Z \approx 0.074853$.

### Example 3: Heavy-Tailed Baseline ($\mathbb{E}_\mu[\tau^{3/4}] < \infty$, $\mathbb{E}_\mu[\tau] = +\infty$) and Critical Boundary
Consider the dyadic heavy-tailed law
$$\mu = \sum_{k=0}^\infty (1 - q) q^k \delta_{2^k}, \qquad q = 2^{-7/8}.$$
Here $\mathbb{E}_\mu[\tau^{3/4}] = \frac{1 - 2^{-7/8}}{1 - 2^{-1/8}} \approx 5.479136 < \infty$ (and $\mathbb{E}_\mu[\tau^{1/4}] = \frac{1 - 2^{-7/8}}{1 - 2^{-5/8}} \approx 1.293435 < \infty$), whereas $\mathbb{E}_\mu[\tau] = \sum_{k=0}^\infty (1-q)(2^{1/8})^k = +\infty$. Evaluating the cancellation-free closed-form Lemma 1 sums (converged to double precision by $K = 256$ atoms) yields
$$Z \approx 0.968595959356969 < \infty, \qquad B(\mu, \mu) \approx 8.781704310764571 < \infty, \qquad J[\mu] \approx 9.066426744743561 < \infty.$$
- **Light-tailed competitor $\nu = \operatorname{Exp}(1)$:** Because $D_\mu(R) \asymp R^{-7/4}$ so $P_T^*(R) \asymp R^{-7/2}$, while $\langle T_r(R)\rangle_{\mathrm{Exp}(1)} = e^R - 1$, $J[\operatorname{Exp}(1)] = +\infty$.
- **Heavy-tailed competitor $\nu$ with $q_1 = 2^{-5/6}$:** Both $J[\nu] < \infty$ and $(I_1 + I_2)/Z < \infty$, with $J[\nu] - J[\mu] \approx 0.10386 > 0$.
- **Infinite $1/2$-moment competitor $\nu$ with $q_1 = 2^{-1/4}$:** $\mathbb{E}_\nu[\tau^{1/2}] = +\infty$, placing $\nu$ in Theorem Case (2): $N_\nu(R) = +\infty$ for all $R > 0$, so $J[\nu] = +\infty$.
- **Critical $3/4$-moment baseline boundary ($q = 2^{-3/4}$):** Then $\mathbb{E}_\mu[\tau^{1/4}] < \infty$ ($Z < \infty$), while $\mathbb{E}_\mu[\tau^{3/4}] = +\infty$ and $\sum_k \sum_j w_k w_j B(2^k, 2^j) \ge \sum_k w_k^2 B(2^k, 2^k) = +\infty$, giving $J[\mu] = +\infty$.
