# Prior-Art Comparison (Milestone 1 Gate)

Milestone 1 asks: *Compare the claimed probability-range legend with the cited prior art, and stop if the claimed difference is already supplied by prior art or no useful bound is obtained.*

## 1. Comparison Against Cited Prior Art

| Prior Work | What It Already Supplies | What Remains Missing for Blended-Colour Legends |
|---|---|---|
| **VSUP** (Correll, Moritz, & Heer, CHI 2018) | Value-Suppressing Uncertainty Palettes allocate a bivariate wedge/pyramid legend where high uncertainty compresses value distinctions into muted/gray bins, discouraging over-interpretation of uncertain means. | VSUP assumes a known 2D `(value, uncertainty)` encoding rather than recovering event probabilities from a *weighted-average / alpha-blended colour*. It does not compute feasible probability intervals $[P_{\min}, P_{\max}]$ for a blended swatch or identify Radon-degenerate blends. |
| **Colour Blinded by the Noise** (Mason, Rogers, Kleffner, & Cook, arXiv:2608.17976) | Evaluates choropleth uncertainty methods (including VSUP, overlaid sampling, and transparency/pixelation) as noise suppression. Explicitly notes that when uncertainty increases in transparency/blended approaches, colours drift from static legends and need an *interpretable legend*. | Identifies and names the legend gap as future research; does not supply an exact inverse probability-interval model, dual certificates, or an identifiability-flagging legend. |
| **`ggdibbler`** (R / ggplot2 extension) | Replaces deterministic aesthetics with draws from `distributional` random variables, rendering uncertainty directly through overplotting and spatial/visual noise. | Encodes distributions forward by sampling/overplotting; does not invert an averaged colour back to event-probability bounds or audit palette degeneracy. |
| **`bootplot`** | Treats arbitrary graphics as black-box functionals, averages pixel intensities across bootstrapped renders, and warns qualitatively about visual averaging caveats. | Averages images without computing which event probabilities remain identifiable from the resulting colour or annotating unidentifiable `[0%, 100%]` swatches on a legend. |
| **Moment-LP / SDP Bounds** (Bertsimas & Popescu, *SIAM J. Optim.* 2005) | Establishes the general convex optimization and primal-dual framework for sharp event-probability bounds given support and moments. | Supplies the general mathematical optimization machinery, not a finite-palette colour-blending formulation, 3D vs 1D colour-geometry audit, or a readable probability-interval vector legend. |

## 2. Gate Evaluation

1. **Is the claimed difference already supplied by prior art?** **No.** None of VSUP, *Colour Blinded by the Noise*, `ggdibbler`, or `bootplot` pairs an averaged finite-palette colour with exact $[P_{\min}, P_{\max}]$ bounds and explicit `[0%, 100%]` unidentifiability flags.
2. **Is a useful bound obtained?** **Yes.** Comparing a standard 1D linear 5-colour ramp (`nullspace dim 3`, midpoint tail bound $[0, \tfrac{2}{3}]$) against a non-coplanar 3D 5-colour palette (`nullspace dim 1`) shrinks outer-boundary tail uncertainty to exact recovery (`S2`: $\frac{3}{5}$) and tight interior intervals (`S3`: $[\frac{1}{2}, \frac{3}{5}]$), while explicitly isolating and flagging non-identifiable stop blends (`S6`: $[0, 1]$ at $c_3$).

Conclusion: **Proceed to Milestone 2** after independent review of Milestone 1.
