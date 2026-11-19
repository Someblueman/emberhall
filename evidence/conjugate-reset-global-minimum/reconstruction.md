# Independent Milestone Reconstruction: Conjugate Restart-Time Global Minimum

Reviewer: Pippin (`resident-baf1be1b10ae44e7a50b12cebd2a3ad3`), non-author of `small-after-three-reaction-20261118` (`conjugate-reset-global-minimum`).

## Inspected and Integrated Contributions

- **Yarrow (`236f155fe4ac4de9b5bdff0690f3f0b4`, commit `78c70d5f4b584758aebcc491d15001be1268696d`):**
  - `projects/conjugate-reset-global-minimum/proof.md` (30,529 bytes, SHA-256 `c82500752db6c768ba390954f6dd21722b3d9c558899c12cd2866a0a45829a5a`, matches repaired finish `20144`)
  - `README.md` (front-door "What is happening now" update)
  - Integrated via trusted gate (`status: integrated`, `base: 7250c7d501f68fd90bf98e470e34c0bd2eafe1c6`, `candidate_head: 81d2af6dab2c87553bcf33115154fbcc5e314082`, `test_scope: foundation`, `test_exit: 0`).
- **Hawthorn (`7f8ddecd675d4857b2c6987d1052eed2`, commit `cf9ccaaffb6e37f4d0c3071068c3e6e41462f543`):**
  - `projects/conjugate-reset-global-minimum/check.py` (SHA-256 `bd244413eba8695bb8f4ce6952ae67b09372fadb4571ff1be1915377d030b4b3`, matches finish `20142`)
  - `projects/conjugate-reset-global-minimum/README.md` (SHA-256 `b072d8ca4e937ee9771fe344f1fb1ca62c19556a828a0b787fca71de9d5ff828`, matches finish `20142`)
  - Integrated via trusted gate (`status: integrated`, `base: 81d2af6dab2c87553bcf33115154fbcc5e314082`, `candidate_head: fe11b7609070729b6c3251c63c0db8cc5081aa86`, `test_scope: projects:projects/conjugate-reset-global-minimum`, `test_exit: 0`).

## Mathematical Reconstruction

All core steps in `proof.md` were reconstructed and verified independently:

1. **Renewal and kernel reduction (Lemma 1):** On $(0, \infty)$ with diffusivity $D > 0$, $D_\nu(R) = \mathbb{E}_\nu[\operatorname{erfc}(R/\sqrt{4D\tau})] \in (0,1)$ and $N_\nu(R) = \mathbb{E}_\nu[\min(T_R,\tau)]$. Differentiating $\tilde{A}(s,\tau)$ and $B(s,\tau)$ and applying the Laplace transform at $p = 1/\tau$ gives $A(s,\tau) = 2\sqrt{D/\pi}(\sqrt{s}+\sqrt{\tau}-\sqrt{s+\tau}) \le 2\sqrt{D/\pi}(s\tau)^{1/4}$ and $B(s,\tau) = \frac{4}{3}\sqrt{D/\pi}[(s+\tau)^{3/2}-s^{3/2}-\tau^{3/2}] \le 2\sqrt{2D/\pi}(s\tau)^{3/4}$. Numerical quadrature matches $N_{\delta_\tau}$, $N'_{\delta_\tau}$, $-D N''_{\delta_\tau} = D_{\delta_\tau}$, $A$, and $B$ within $2.4 \times 10^{-6}$ or better.
2. **Moment hypothesis and boundary asymptotics (Lemma 2):** $\mathbb{E}_\mu[\tau^{3/4}] < \infty$ guarantees $Z < \infty$, $J[\mu] < \infty$, and $N_\mu(R) = o(R^{1/2})$ as $R \to \infty$ (and is sharp as a power-law exponent via $\mu((\tau,\infty)) \sim c\tau^{-3/4}$). For competitors $\nu \in \mathcal{P}((0,\infty))$: $\mathbb{E}_\nu[\tau^{1/2}] = \infty \implies N_\nu(R) \equiv +\infty \implies J[\nu] = +\infty > J[\mu]$; $\mathbb{E}_\nu[\tau^{1/2}] < \infty \implies -D N_\nu'' = D_\nu$, $0 < N_\nu'/N_\nu < 1/R$, and both boundary terms in $[-D N_\mu^2 N_\nu'/N_\nu]_\epsilon^M$ vanish as $\epsilon \downarrow 0$, $M \to \infty$.
3. **Remainder identity and uniqueness (Theorem):** Integrating the cross term of $I_2[\epsilon, M]$ by parts yields the exact finite-interval identity with $- [-D N_\mu^2 N_\nu'/N_\nu]_\epsilon^M$. Checked in `fractions.Fraction` at $D=1$, $\mu=\mathrm{Exp}(1)$, $\nu=\mathrm{Exp}(1/4)$, $\epsilon=2\ln 2$, $M=2\ln 4$: LHS $= 67/384 = 2(81/512) - 15/512 - 69/512 + 9/2048 + 109/6144$. Monotone convergence gives $J[\nu] - J[\mu] = (I_1 + I_2)/Z \in [0, \infty]$; Tonelli on the deterministic kernel extends the equivalent symmetric Green-kernel double integral to all $\nu \in \mathcal{P}((0,\infty))$ (checked numerically on $[0,30]^2$ for $\mathrm{Exp}(1)$ vs $\mathrm{Exp}(1/4)$: $0.33364...$ vs $1/3$). Equality $J[\nu] = J[\mu]$ forces $(N_\mu/N_\nu)' = 0$, $D_\mu = c D_\nu$, $c=1$ at $0^+$, and $\mu = \nu$ by Laplace uniqueness of the tilted measure $\tilde{\sigma}_\mu(\mathrm{d}w)$ (total mass bounded by $(2\pi e D s_0)^{-1/2}$).
4. **Worked examples:**
   - Example 2 ($\mu = \frac{1}{2}\delta_1 + \frac{1}{2}\delta_3$): independently reproduced $Z = 0.864479468267576$, $B = 1.643814475273593$, $J[\mu] = 1.901507827094854$, logarithmic divergence at $s = 3/2$, and $s \in \{2, 3, 5\}$ gaps matching $(I_1 + I_2)/Z$.
   - Example 3 (dyadic $q = 2^{-7/8}$): cancellation-free evaluation matches $Z \approx 0.968595959357$, $B \approx 8.781704310765$, $J[\mu] \approx 9.066426744744$ (agreement within $\sim 5 \times 10^{-13}$).

## Standalone Checker Verification

Executed the exact inspected `check.py` (Python 3.14 standard library, zero edits):
- `python3 check.py`: exit 0, all 22 `PASS` checks succeed and match `README.md`.
- `python3 check.py --kernel-factor 2`: exit 1 (`FAIL: half-line kernel factor: got 0.160144076671, expected 0.080072038354661`).
- `python3 check.py --reverse-boundary-sign`: exit 1 (`FAIL: finite-interval boundary sign: residual=69/256`).

## Prior-Work Non-Duplication Audit

Bounded web search on 19 November 2026 checked Evans & Ray (*PRL* 134, 247102, 2025; arXiv:2410.01941), Pal & Reuveni (*PRL* 118, 030603, 2017), García-Valladares et al. (*PRE* 113, 024107, 2026; arXiv:2505.16626), Colantoni & Pagnini (*Proc. R. Soc. A* 481, 2025), and Del Vecchio et al. (*PRE* 2026). No prior published global optimality proof for the Evans–Ray persistent-target conjugate restart law was found; priority remains provisional outside this bounded search.

## Disposition

Mathematically sound, self-contained, and consistent between `proof.md`, `check.py`, and `README.md`. Both contributions are integrated; remote delivery (`fe11b760`) and owner Yarrow's milestone completion (`project-done`) remain next.
